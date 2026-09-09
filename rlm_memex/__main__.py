import argparse
import json
from .store import MemexStore, import_catalog, import_skills, verify_handoff


def main():
    parser = argparse.ArgumentParser(description="Scientific skills and engineering Memex for RLM")
    parser.add_argument("--db", required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("index-skills")
    p.add_argument("root")
    p.add_argument("--revision", required=True)
    p = sub.add_parser("import-catalog")
    p.add_argument("path")
    p.add_argument("--namespace", choices=["parts", "datasets"], required=True)
    p.add_argument("--version", required=True)
    p = sub.add_parser("import-tools")
    p.add_argument("handoff")
    p = sub.add_parser("search")
    p.add_argument("query")
    p.add_argument("--namespace", default="skills")
    p.add_argument("--limit", type=int, default=5)
    p = sub.add_parser("read")
    p.add_argument("namespace")
    p.add_argument("id")
    p.add_argument("version")
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--size", type=int, default=8000)
    sub.add_parser("stats")
    p = sub.add_parser("ask")
    p.add_argument("question")
    p.add_argument("--model", required=True)
    p.add_argument("--backend", default="openai")
    args = parser.parse_args()
    store = MemexStore(args.db)
    try:
        if args.command == "index-skills":
            result = {"imported": import_skills(store, args.root, args.revision)}
        elif args.command == "import-catalog":
            result = {"imported": import_catalog(store, args.path, args.namespace, args.version)}
        elif args.command == "import-tools":
            from pathlib import Path
            manifest = verify_handoff(args.handoff)
            version = manifest["files"]["tools.jsonl"]["sha256"]
            # The catalog's own verifier additionally checks semantic references.
            result = {"evidence": import_catalog(store, Path(args.handoff) / "evidence-sources.jsonl", "evidence", version),
                      "tools": import_catalog(store, Path(args.handoff) / "tools.jsonl", "tools", version)}
        elif args.command == "search":
            result = store.search(args.query, args.namespace, args.limit)
        elif args.command == "read":
            result = store.read(args.namespace, args.id, args.version, args.start, args.size)
        elif args.command == "stats":
            result = store.stats()
        else:
            from .engine import run
            completion = run(store, args.question, args.model, args.backend)
            result = {"answer": completion.response, "execution_time": completion.execution_time,
                      "usage": completion.usage_summary.to_dict()}
        print(json.dumps(result, indent=2, ensure_ascii=False))
    finally:
        store.close()


if __name__ == "__main__":
    main()
