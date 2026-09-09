# REA — Recursive Engineering Agents: related work

Search date: 9 September 2026 UTC. This is a scoping discovery inventory to guide
the implementation and benchmark design, not a completed systematic review.

## What was searched

Twelve scite MCP searches cover recursive language models; agent skills and
procedural memory; CFD/FEA; mechanical design and CAD; materials; electronics;
dataset discovery; civil/structural engineering and BIM; optics, control and
robotics; memory foundations; and component selection. Exact-title queries recover
the seed paper and foundational work that broad relevance ranking missed.

The first page of each query yielded 116 records before DOI deduplication. A
bidirectional, one-hop citation search around RLM, Multi-Field Tool Retrieval,
OpenFOAMGPT and MechRAG returned 150 edges. The combined inventory contains 262
distinct DOIs. Preprint and published DOIs may refer to the same work; this number
is not a count of 262 independently screened studies.

- [Search log, exact queries and coverage limits](search-log.json)
- [Candidate inventory, CSV](paper-inventory.csv)
- [Candidate inventory, JSON](paper-inventory.json)
- [Priority bibliography, BibTeX](related-work.bib)
- [Scite screening record: 24 priority entries, 7 off-topic exclusions](scite-screening.json)
- Raw results under `sources/`; regenerate using `python3 docs/rlm/build_inventory.py`.

The citation graph hit its cap. Multi-Field Tool Retrieval and the OpenFOAMGPT
preprint have low direct DOI-edge coverage. Some retrieved dates lie beyond the
search date and need online-publication verification. Search ranking also produced
off-topic records; unreviewed candidates remain explicitly marked. Broad query
match counts are not relevant-paper counts. Scite's citation labels do not prove
that a proposed system works. Publisher access links containing account data were
removed from saved records; public DOI links identify papers instead.

## Design implications from inspected sources

The seed paper packages procedures as selectively loaded skills and reports corpus
measurements rather than task-level benefits. Its reference-heavy workflows can
exceed a native context window. That motivates external storage, but does not
establish that any new runtime will improve scientific correctness.
[Scientific Agent Skills](https://arxiv.org/abs/2609.00065).

RLM treats long input as an external environment that the model inspects through
code and recursive calls. The useful adaptation is to expose procedures and
catalog evidence to that environment. Storage, RAM, recursion depth, model calls
and time still constrain the system. Its reported long-context benchmark results
must not be transferred to engineering tasks without evaluation.
[Recursive Language Models](https://arxiv.org/abs/2512.24601).

MechRAG explicitly discusses context limits when retrieving mechanical-engineering
information, making it a close domain-specific comparison. Its multimodal setting
also exposes a gap in this implementation: a Markdown/JSON corpus does not cover
drawings, geometry or simulation fields.
[MechRAG](https://doi.org/10.1038/s44172-025-00517-z).

Multi-Field Tool Retrieval evaluates tool retrieval over several datasets and a
mixed collection. It motivates preserving separate descriptive and capability
fields, and benchmarking a learned reranker against the initial SQLite lexical
retriever. Retrieval success alone is not solver compatibility.
[Multi-Field Tool Retrieval](https://arxiv.org/abs/2602.05366).

ChatCFD includes tutorial cases and perturbed cases in its evaluation. This is a
useful pattern for separating reproduction from generalization: change boundary
conditions, physical properties and solver settings, then check the resulting
simulation rather than only whether code executes.
[ChatCFD](https://doi.org/10.1002/aidi.202500174).

The component-selection paper's retrieved abstract describes datasheet retrieval
for replacement parts. It is a relevant reading candidate for the Parts Memex;
its performance has not been independently evaluated here. Source-catalog entries
will need actual versioned datasheets, dimensions, tolerances and applicability
conditions before they support component substitution.
[Datasheet retrieval and component selection](https://doi.org/10.3390/electronics15112301).

## Priority reading map

These papers were verified as records by scite, with all 24 requested bibliography
entries resolved. This is metadata verification, not full-text review of all 24.
The independent checker resolved 12 DOI occurrences in this report (including
duplicates); it does not extract the arXiv URL links and returned incomplete
metadata for the ChemRxiv entry, whose metadata is instead present in scite.

| Area | Priority papers | What to test or learn |
|---|---|---|
| Context and memory | [RLM](https://arxiv.org/abs/2512.24601), [RLM reproduction](https://arxiv.org/abs/2603.02615), [MemGPT](https://arxiv.org/abs/2310.08560), [A-MEM](https://arxiv.org/abs/2502.12110) | External addressing, termination, persistent memory and retrieval failures |
| Procedures and tools | [Scientific Agent Skills](https://arxiv.org/abs/2609.00065), [Voyager](https://arxiv.org/abs/2305.16291), [ToolLLM](https://arxiv.org/abs/2307.16789), [Multi-Field Tool Retrieval](https://arxiv.org/abs/2602.05366), [Skill Retrieval Augmentation](https://arxiv.org/abs/2604.24594) | Skill discovery, reuse, tool routing and appropriate baselines |
| CFD | [OpenFOAMGPT](https://doi.org/10.1063/5.0257555), [ChatCFD](https://doi.org/10.1002/aidi.202500174) | Solver configuration and perturbed physics cases |
| Mechanics and FEA | [MechAgents](https://doi.org/10.1016/j.eml.2024.102131), [MechGPT](https://doi.org/10.1115/1.4063843), [ALL-FEM](https://arxiv.org/abs/2603.21011) | Executable analyses, constitutive assumptions and numerical checks |
| CAD and geometry | [MechRAG](https://doi.org/10.1038/s44172-025-00517-z), [ABC dataset](https://doi.org/10.1109/cvpr.2019.00983), [DeepCAD](https://doi.org/10.1109/iccv48922.2021.00670) | Geometry identity, multimodal retrieval and reconstruction |
| Electronics and parts | [Datasheet retrieval](https://doi.org/10.3390/electronics15112301), [AutoSizer](https://arxiv.org/abs/2602.02849) | Parameter extraction, compatibility and simulation-based sizing |
| Optics | [OPTIAGENT](https://arxiv.org/abs/2602.23761) | Physics-based optical design and performance oracles |
| Structures and BIM | [Structural workflow agents](https://arxiv.org/abs/2510.11004), [BIM-Edit](https://arxiv.org/abs/2606.20146) | Structural assumptions and valid model edits |
| Materials | [Modular materials agents](https://doi.org/10.26434/chemrxiv-2025-zkn81-v2) | Tool composition across materials workflows |
| Dataset discovery | [LEDD](https://arxiv.org/abs/2502.15182) | Dataset selection and metadata grounding |

Additional discovery candidates cover robotics, control, manufacturing, energy and
chemical engineering. They appear in the machine-readable inventory and require
screening before inclusion in a formal related-work section. Aerospace and
controls need more targeted searches; CFD alone does not cover either discipline.

## Proposed evaluation

Hold model, task set, execution environment and scoring fixed. Compare: no skills;
the upstream progressive-disclosure collection; flat retrieval; RLM with skills;
and RLM with skills plus Tool, Parts and Dataset Memex. Separate the retrieval
effect from recursion with an ablation using the same retrieved documents.

Use held-out workflows with explicit ground truth: CFD boundary-condition
perturbations; structural load/constraint changes; CAD feature constraints;
electronic substitutions with unit and package mismatches; optics requirements;
and dataset selection with incompatible versions or restricted access. Keep
gold answers outside the imported corpus.

Report task completion and engineering correctness separately. Also report
source coverage, invalid citations, skill/tool recall, unresolved constraints,
latency, token usage, cost and termination failures. Repeat stochastic runs and
report uncertainty. A search index passing unit tests is not performance evidence;
a live recursion smoke test is not an engineering benchmark.

## Scope still open

Complete paginated searches and citation expansion for a defined engineering
taxonomy; deduplicate preprint/publication versions; screen full texts; check
editorial notices; and record inclusion/exclusion decisions before describing this
as comprehensive. The current inventory is an auditable starting point, not a
claim to have found all related papers.
