# REA — Recursive Engineering Agents

REA adds a versioned external corpus and an adapter to the authors'
Recursive Language Models implementation. The upstream portable skills remain
available. This is an experimental runtime extension, not a validated claim of
improved engineering performance or a literally unlimited model context window.

## Basis

- Scientific Agent Skills paper: <https://arxiv.org/abs/2609.00065>.
- Paper snapshot: `v2.65.0`, commit `f6fcafeb1cc8c82eca0160a18bc41c38427b8e0f`.
- This adaptation starts from upstream `9cf7d9aea7d84754db4c167ab04b299d33c444bc`
  (collection version 2.66.0); corpus counts therefore differ from the paper.
- RLM paper: <https://arxiv.org/abs/2512.24601>.
- Runtime dependency: `rlms==0.1.3`, <https://github.com/alexzhang13/rlm>.
- [Related literature and evaluation plan](docs/rlm/RELATED_WORK.md).

## Memory model

| Namespace | Contents | Identity |
|---|---|---|
| skills | SKILL.md procedures and Markdown reference documents | Relative path + source revision |
| tools | Tool catalog records, capabilities and restrictions | Original tool ID + handoff hash |
| parts | Parts-source catalog metadata | Original catalog ID + snapshot version |
| datasets | Dataset/source catalog metadata | Original catalog ID + snapshot version |
| evidence | Source attribution records | Original source ID + snapshot version |

Records retain their complete imported JSON, provenance and SHA-256. Versions
are immutable; identical re-imports are idempotent. SQLite FTS5 offers paged
lexical search and reads bounded to 32,000 characters. It is a baseline
retriever, not a learned reranker or a tool-suitability evaluator. Skills scripts,
binary assets and non-Markdown references are not indexed by this importer.

The RLM adapter supplies the corpus as an external REPL dictionary, while the
root model receives the question. Generated code runs in the upstream Docker
environment and can use recursive subcalls. This convenience path materializes
the corpus in RAM and caps the serialized record character count at 250 million;
it does not offer unlimited storage or a production disk-backed REPL. The SQLite
search/read API is the integration point for a future paged broker.

## Local use

From the repository root, Python 3.13+:

```bash
mkdir -p .local
python3 -m rlm_memex --db .local/memex.sqlite index-skills skills --revision "$(git rev-parse HEAD)"
python3 -m rlm_memex --db .local/memex.sqlite search 'finite element boundary conditions'
python3 -m rlm_memex --db .local/memex.sqlite stats
```

Supply the actual upstream revision corresponding to the skill tree. Import
catalogs explicitly; they are not redistributed with this fork:

```bash
python3 /path/to/catalog/verify_rlm_handoff.py --require-ready
python3 -m rlm_memex --db .local/memex.sqlite import-tools /path/to/catalog/rlm-handoff
python3 -m rlm_memex --db .local/memex.sqlite import-catalog /path/to/parts-sources-memex.json --namespace parts --version SNAPSHOT_ID
python3 -m rlm_memex --db .local/memex.sqlite import-catalog /path/to/datasets-memex.json --namespace datasets --version SNAPSHOT_ID
```

The catalog verifier checks references and database fidelity; this package checks
handoff hashes, release readiness, unique IDs and immutable versions. Catalog
imports do not crawl URLs, install tools, retrieve datasets or grant reuse rights.
The parts catalog describes sources, not a stock inventory of individual parts.

For model calls, install the optional dependency into a separate environment,
start Docker, and configure your provider's API key in the environment:

```bash
uv venv .venv-rlm
uv pip install --python .venv-rlm/bin/python -r requirements-rlm.txt
.venv-rlm/bin/python -m rlm_memex --db .local/memex.sqlite ask 'Identify procedures and tool candidates for a thermal analysis, with unresolved assumptions and citations.' --backend openrouter --model openai/gpt-5-nano
```

The adapter configures depth 3, 20 iterations, 4 concurrent subcalls, 100,000
tokens, 300 seconds and a $1 upstream budget threshold. Upstream checks some
limits after work completes, so these are not strict spending or wall-time
guarantees. Provider calls transmit selected excerpts; running `ask` sends those
excerpts to the configured model provider. Docker isolation inherits the
upstream implementation and is not a security certification.

## Verification

```bash
python3 -m unittest discover -s tests/_rlm_memex -v
python3 -m pytest tests/_meta -q
python3 docs/rlm/build_inventory.py
```

Tests cover namespace/version separation, immutable re-imports, bounded reads,
malformed search syntax, duplicate rollback, release readiness, payload limits
and the adapter's external-context argument contract. These are correctness
tests for the extension, not scientific benchmarks.

On 2026-09-09, all 8 extension tests and 10 repository meta checks passed. A
[live synthetic smoke test](docs/rlm/live-smoke.json) with `rlms==0.1.3`, Docker
29.5.3 and `openai/gpt-5-nano` through OpenRouter returned the expected sum and
record IDs, with 2 observed recursive subcalls. It took 269 seconds and reported
$0.00573641 in provider cost across 5 calls. This establishes the execution path,
not production latency or engineering accuracy. Its optional reproducer is
`PYTHONPATH=. .venv-rlm/bin/python tests/_rlm_memex/live_smoke.py` and makes paid
model calls. The local catalog integrity verifier also passed before import.

## Remaining performance work

Compare identical models and tasks across no skills, upstream progressive
disclosure, flat retrieval, RLM plus skills, and RLM plus all three Memex stores.
Measure task success, scientific correctness, evidence coverage, skill recall,
latency, tokens and cost. Include multi-document constraints, stale versions,
unknown rights, conflicting units and tasks with irrelevant distractors. Require
execution/physics oracles and held-out tasks before claiming a performance gain.
Runtime enforcement of numbered leaf coverage and citation validity is still
needed; the current adapter instructs the model but does not enforce those rules.

## Engineering specialist taxonomy

The runtime includes the complete pinned editorial taxonomy: 71 domains and 609 subcategories, covering 4,795 tool records and 5,658 memberships. Each domain has a specialist role specification with all of its subcategories. These profiles guide recursive calls; they are not independently trained or validated agents. Membership does not certify suitability.

```sh
python3 -m rlm_memex --db .local/memex.sqlite specialists
python3 -m rlm_memex --db .local/memex.sqlite specialist cfd
python3 -m rlm_memex --db .local/memex.sqlite ask --domain cfd --model MODEL "Assess the tool evidence for this task"
```

Use `--subcategory ID` with an explicit domain to narrow tool memberships further. Unknown or cross-domain IDs fail. Scoped calls preserve source evidence, expose missing evidence IDs, and retain shared skills, parts and datasets. The full definitions are in `rlm_memex/data/engineering_taxonomy.json`; generated documentation is in `docs/rlm/ENGINEERING_TAXONOMY.md`. The ICLR manuscript and evaluation protocol are under `paper/`.
