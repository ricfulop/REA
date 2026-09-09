# Evaluation protocol — proposed, not yet executed

Primary question: Does recursive access to versioned engineering procedures and tool/parts/dataset evidence improve independently scored engineering task success under matched model and resource budgets?

Freeze tasks and scoring before viewing test outputs. Begin with CAD, CFD, structural mechanics, controls, optics and digital electronics. Aim for at least 20 independently checkable tasks per domain, with three repeated runs per condition. This is a planning target, not a power analysis or a claim that tasks already exist. Use a pilot to estimate variance and cost; revise sample size before the held-out evaluation. Split by underlying design/problem family to avoid paraphrase leakage.

## Conditions

| Condition | Purpose |
| --- | --- |
| Same model, task only | Base capability |
| Progressive skill disclosure | Upstream-style procedural access |
| Flat lexical retrieval over all stores | Retrieval baseline |
| RLM plus skills | Isolate recursive procedural access |
| RLM plus skills and Tool/Parts/Dataset Memex | Measure catalog contribution |
| Full REA with taxonomy-scoped specialist profiles | Measure routing contribution |

Use the same model snapshot, task prompt, output contract, maximum tokens, elapsed time, concurrency and dollar budget. Record both actual usage and budget truncation. Add leave-one-store-out ablations and taxonomy shuffled/disabled controls on a preregistered task subset. Do not compare full REA on a larger budget without a separate matched-cost analysis.

## Tasks and ground truth

Each task requires a stable ID, domain/category, problem-family split, input artifacts, provenance, license, expected answer or executable oracle, units, tolerances and failure criteria. Include catalog selection, incompatible-interface rejection, unit conversion, constraint checking and multi-domain handoffs. Use deterministic independent calculations or solver outputs where possible. Selection tasks alone do not establish solver competence. If solver runs are included, pin software versions and boundary conditions; compare against independent reference solutions and convergence criteria.

Keep task answers and scorer code outside every model-accessible Memex. Audit indexed records for answer leakage. Parts and dataset catalog entries describe sources; they do not establish access to underlying data or qualification of parts. Freeze snapshots and report unavailable resources rather than replacing them selectively after results are known.

## Measurements and analysis

Primary outcome is per-task engineering correctness under a frozen rubric. Report units, constraint satisfaction, citation support, version/interface compatibility, explicit abstention and unsupported assertions separately. Record wall time, input/output tokens, recursive calls, maximum depth, failures and cost. Distinguish timeout, provider error, retrieval miss, wrong reasoning and invalid tool output. Include every attempted run in the denominator.

Compare paired task outcomes; bootstrap problem families for 95% confidence intervals and show domain breakdowns. Aggregate repeated runs within task before resampling rather than treating them as independent problems. Predefine primary comparisons and report all ablations. Report accuracy-versus-budget curves rather than a single favorable budget. No performance table should contain estimated or invented results.

## Artifact contract

Store one JSON record per attempt containing task_id, split, domain_id, condition, seed, model_snapshot, prompt_hash, corpus_hashes, taxonomy_hash, code_commit, budgets, timestamps, response, record_citations, recursive_trace_path, usage, failure_kind and scorer_output. Retain raw traces with secrets removed. Publish only data with redistribution rights; otherwise publish acquisition instructions and hashes.

## Current evidence

Fourteen deterministic extension tests and ten upstream metadata tests passed on September 9, 2026. A previously recorded two-record synthetic load-summation test demonstrated recursive subcalls; it is not an engineering benchmark. Full taxonomy export contains 71 domains, 609 subcategories, 4,795 tool records and 5,658 membership edges. Six real catalog scope audits reported no missing referenced evidence IDs. No comparative task-success result has been measured yet.
