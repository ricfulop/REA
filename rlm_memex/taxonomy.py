"""Complete editorial engineering taxonomy and scope-bound specialist profiles."""

import hashlib
import json
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parent / "data" / "engineering_taxonomy.json"


def load_taxonomy(path=DEFAULT_PATH):
    taxonomy = json.loads(Path(path).read_text(encoding="utf-8"))
    domains, categories = set(), set()
    for domain in taxonomy["domains"]:
        if domain["id"] in domains:
            raise ValueError("Duplicate domain ID")
        domains.add(domain["id"])
        for category in domain["subcategories"]:
            if category["domain"] != domain["id"] or category["id"] in categories:
                raise ValueError("Duplicate or misparented subcategory")
            categories.add(category["id"])
    if len(domains) != taxonomy["counts"]["domains"] or len(categories) != taxonomy["counts"]["subcategories"]:
        raise ValueError("Taxonomy counts do not match definitions")
    return taxonomy


def specialists(taxonomy=None):
    taxonomy = taxonomy or load_taxonomy()
    return {d["id"]: {
        "id": "rea/" + d["id"], "domain_id": d["id"], "name": d["label"],
        "taxonomy_version": taxonomy["version"],
        "subcategories": d["subcategories"],
        "instructions": (
            "Investigate this engineering domain using the supplied procedures and catalog evidence. "
            "Select explicit subcategory IDs; do not treat category membership as qualification. "
            "Check assumptions, units, applicable versions, interfaces, execution requirements and "
            "validation evidence. Preserve unknowns and conflicting evidence. Return cited findings, "
            "unresolved constraints and requested cross-domain handoffs. Do not execute catalog tools "
            "or infer dataset access from a record."
        ),
    } for d in taxonomy["domains"]}


def scope_context(context, domain_id, subcategory_id=None, taxonomy=None):
    """Filter actual catalog memberships, never rank words to infer a membership."""
    taxonomy = taxonomy or load_taxonomy()
    registry = specialists(taxonomy)
    if domain_id not in registry:
        raise ValueError(f"Unknown engineering domain: {domain_id}")
    profile = registry[domain_id]
    allowed = {c["id"] for c in profile["subcategories"]}
    if subcategory_id is not None and subcategory_id not in allowed:
        raise ValueError("Subcategory does not belong to selected domain")
    allowed = {subcategory_id} if subcategory_id else allowed
    selected = {}
    source_ids = set()

    def collect_sources(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if (key == "source_id" or key.endswith("_source_id")) and isinstance(item, str):
                    source_ids.add(item)
                collect_sources(item)
        elif isinstance(value, list):
            for item in value:
                collect_sources(item)

    for key, row in context.get("tools", {}).items():
        record = json.loads(row["body"])
        memberships = {c["id"] for c in record.get("subcategories", [])}
        if memberships & allowed:
            selected[key] = row
            collect_sources(record)
    # Preserve provenance needed by the shared parts/dataset records too.
    for namespace in ("parts", "datasets"):
        for row in context.get(namespace, {}).values():
            collect_sources(json.loads(row["body"]))
    evidence = {key: row for key, row in context.get("evidence", {}).items() if row["id"] in source_ids}
    result = dict(context)
    result.update(tools=selected, evidence=evidence, specialist={
        **profile, "selected_subcategory_id": subcategory_id,
        "tool_records_in_scope": len(selected),
        "missing_evidence_ids": sorted(source_ids - {row["id"] for row in evidence.values()}),
    })
    return result


def export_taxonomy(catalog_root, output):
    """Pin all published categories; candidate expansion rules are never used."""
    from .store import verify_handoff
    root = Path(catalog_root)
    manifest = verify_handoff(root / "rlm-handoff")
    labels_path = root / "domain_labels.json"
    assignments_path = root / "subcategory_assignments.json"
    labels = json.loads(labels_path.read_text())
    assignments = json.loads(assignments_path.read_text())
    categories = assignments["categories"]
    ids = {c["id"] for c in categories}
    if len(ids) != len(categories) or any(c["domain"] not in labels for c in categories):
        raise ValueError("Invalid taxonomy definitions")
    counts = dict.fromkeys(ids, 0)
    tool_counts = dict.fromkeys(labels, 0)
    membership_count = 0
    for line in (root / "rlm-handoff/tools.jsonl").open():
        tool = json.loads(line)
        tool_counts[tool["domain_id"]] += 1
        for category in tool["subcategories"]:
            if category["id"] not in ids:
                raise ValueError("Handoff contains an undefined category")
            canonical = next(c for c in categories if c["id"] == category["id"])
            if any(category[k] != canonical[k] for k in ("domain", "label")):
                raise ValueError("Handoff taxonomy differs from canonical definitions")
            counts[category["id"]] += 1
            membership_count += 1
    sources = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (labels_path, assignments_path)}
    sources["tools.jsonl"] = manifest["files"]["tools.jsonl"]["sha256"]
    version = hashlib.sha256(json.dumps(sources, sort_keys=True).encode()).hexdigest()
    result = {"schema_version": "1.0", "version": version, "source_sha256": sources,
              "method": assignments["method"],
              "counts": {"domains": len(labels), "subcategories": len(ids),
                         "tool_records": sum(tool_counts.values()), "memberships": membership_count},
              "domains": [{"id": domain_id, "label": label, "tool_records": tool_counts[domain_id],
                           "subcategories": [{**c, "tool_memberships": counts[c["id"]]}
                                             for c in categories if c["domain"] == domain_id]}
                          for domain_id, label in labels.items()]}
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    load_taxonomy(output)
    return result
