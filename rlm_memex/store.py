"""Versioned SQLite corpus. Search is lexical; suitability is not inferred."""

import hashlib
import json
import re
import sqlite3
from pathlib import Path

NAMESPACES = ("skills", "tools", "parts", "datasets", "evidence")


class MemexStore:
    def __init__(self, path):
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS records (
                namespace TEXT NOT NULL, id TEXT NOT NULL, version TEXT NOT NULL,
                title TEXT NOT NULL, body TEXT NOT NULL, source TEXT NOT NULL,
                sha256 TEXT NOT NULL, PRIMARY KEY(namespace, id, version));
            CREATE VIRTUAL TABLE IF NOT EXISTS search USING fts5(
                namespace UNINDEXED, id UNINDEXED, version UNINDEXED, title, body);
        """)

    def close(self):
        self.db.close()

    def put(self, namespace, record_id, version, title, body, source):
        if namespace not in NAMESPACES:
            raise ValueError(f"Unknown namespace: {namespace}")
        if not all(isinstance(v, str) and v for v in (record_id, version, title, body, source)):
            raise ValueError("Identity, version, title, body and source must be nonempty strings")
        digest = hashlib.sha256(body.encode()).hexdigest()
        prior = self.db.execute(
            "SELECT sha256, title, source FROM records WHERE namespace=? AND id=? AND version=?",
            (namespace, record_id, version),
        ).fetchone()
        if prior:
            if tuple(prior) != (digest, title, source):
                raise ValueError(f"Immutable version conflict: {namespace}/{record_id}@{version}")
            return False
        self.db.execute("INSERT INTO records VALUES (?,?,?,?,?,?,?)",
                        (namespace, record_id, version, title, body, source, digest))
        self.db.execute("INSERT INTO search VALUES (?,?,?,?,?)",
                        (namespace, record_id, version, title, body))
        return True

    def search(self, query, namespace="skills", limit=5, offset=0):
        if namespace not in NAMESPACES or not 1 <= limit <= 50 or offset < 0:
            raise ValueError("Invalid namespace or page bounds")
        terms = re.findall(r"\w+", query, flags=re.UNICODE)[:32]
        if not terms:
            return []
        expression = " OR ".join('"' + t + '"' for t in terms)
        rows = self.db.execute("""
            SELECT namespace,id,version,title,snippet(search,4,'','', ' … ',40) AS excerpt,
                   bm25(search,0,0,0,5,1) AS rank
            FROM search WHERE search MATCH ? AND namespace=?
            ORDER BY rank,id,version LIMIT ? OFFSET ?
        """, (expression, namespace, limit, offset))
        return [dict(r) for r in rows]

    def read(self, namespace, record_id, version, start=0, size=8000):
        if start < 0 or not 1 <= size <= 32000:
            raise ValueError("Invalid read bounds")
        row = self.db.execute(
            "SELECT * FROM records WHERE namespace=? AND id=? AND version=?",
            (namespace, record_id, version),
        ).fetchone()
        if row is None:
            raise KeyError((namespace, record_id, version))
        result = dict(row)
        total = len(result["body"])
        result["body"] = result["body"][start:start + size]
        result.update(start=start, total_chars=total,
                      next_start=start + size if start + size < total else None)
        return result

    def stats(self):
        return {r[0]: {"records": r[1], "chars": r[2]} for r in self.db.execute(
            "SELECT namespace,count(*),sum(length(body)) FROM records GROUP BY namespace")}

    def context(self, max_chars=250_000_000):
        """Materialize an external REPL payload, not a model prompt.

        SQLite search/read scale independently of RAM. This convenience adapter
        has an explicit RAM-sized limit because upstream serializes its payload.
        """
        if max_chars <= 0:
            raise ValueError("max_chars must be positive")
        result = {n: {} for n in NAMESPACES}
        size = 0
        for row in self.db.execute("SELECT * FROM records ORDER BY namespace,id,version"):
            record = dict(row)
            size += len(json.dumps(record, ensure_ascii=False))
            if size > max_chars:
                raise ValueError("External payload exceeds max_chars; use paged search/read integration")
            result[row["namespace"]][json.dumps([row["id"], row["version"]])] = record
        return result


def import_skills(store, root, revision):
    root = Path(root).resolve()
    count = 0
    with store.db:
        for skill in sorted(root.iterdir()):
            if not skill.is_dir() or not (skill / "SKILL.md").is_file():
                continue
            paths = [skill / "SKILL.md"]
            if (skill / "references").is_dir():
                paths += sorted((skill / "references").rglob("*.md"))
            for path in paths:
                if not path.resolve().is_relative_to(root):
                    raise ValueError(f"Reference escapes corpus: {path}")
                relative = path.relative_to(root).as_posix()
                count += store.put("skills", relative, revision, relative,
                                   path.read_text(encoding="utf-8"),
                                   f"https://github.com/K-Dense-AI/scientific-agent-skills/blob/{revision}/skills/{relative}")
    return count


def import_catalog(store, path, namespace, version):
    """Import catalog metadata only. Does not crawl linked documentation."""
    path = Path(path)
    if namespace not in ("tools", "parts", "datasets", "evidence"):
        raise ValueError("Catalog namespace must be tools, parts, datasets or evidence")
    seen = set()
    count = 0
    with path.open(encoding="utf-8") as stream, store.db:
        records = (json.loads(line) for line in stream if line.strip()) if path.suffix == ".jsonl" else json.load(stream)
        if isinstance(records, dict):
            raise ValueError("Expected a JSON array or JSONL records")
        for record in records:
            record_id = record.get("tool_id") if namespace == "tools" else record.get("id")
            if not isinstance(record_id, str) or not record_id or record_id in seen:
                raise ValueError(f"Missing or duplicate ID: {record_id}")
            seen.add(record_id)
            count += store.put(namespace, record_id, version,
                               record.get("name") or record.get("title") or record_id,
                               json.dumps(record, ensure_ascii=False, sort_keys=True),
                               path.name)
    return count


def verify_handoff(path):
    """Check release state and each declared file before any Tool Memex import."""
    path = Path(path).resolve()
    manifest = json.loads((path / "manifest.json").read_text())
    if manifest.get("release_status") != "ready-for-rlm-builder":
        raise ValueError("Tool handoff is not ready-for-rlm-builder")
    for name in ("tools.jsonl", "evidence-sources.jsonl", "documentation-sources.jsonl"):
        if name not in manifest.get("files", {}):
            raise ValueError(f"Missing manifest entry: {name}")
    for name, expected in manifest["files"].items():
        source = (path / name).resolve()
        if not source.is_relative_to(path):
            raise ValueError("Manifest path escapes handoff")
        digest = hashlib.sha256()
        with source.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        if source.stat().st_size != expected["bytes"] or digest.hexdigest() != expected["sha256"]:
            raise ValueError(f"Handoff integrity failure: {name}")
    return manifest
