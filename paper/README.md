# REA: ICLR 2027 submission project

Target: ICLR 2027. Status: research draft, not submitted; comparative experiments and human author review remain outstanding. TMLR is the fallback if evidence is not ready. Do not submit concurrently.

## Schedule

| Date (2026) | Deliverable |
| --- | --- |
| September 11 | Freeze benchmark tasks, independent references, baselines and scoring protocol |
| September 15 | Pilot all conditions; inspect failures and estimate remaining compute |
| September 17 | Decide whether results justify abstract submission; finalize all authors and OpenReview profiles |
| September 18, 23:59 AoE | Official abstract deadline |
| September 22 | Freeze experiments; complete uncertainty estimates, ablations and failure analysis |
| September 24 | Human technical review, citation audit, anonymization and PDF checks |
| September 25, 23:59 AoE | Official full paper deadline |

No authors can be added after the abstract deadline. These are project milestones, not scheduled automations. Author names, affiliations, OpenReview profiles and reviewer eligibility must be supplied before submission.

Official sources checked September 9, 2026:
- https://iclr.cc/Conferences/2027/CallForPapers
- https://iclr.cc/Conferences/2027/AuthorGuidelines
- https://iclr.cc/Conferences/2027/AIPolicyForAuthors
- https://media.iclr.cc/Conferences/ICLR2027/iclr-2027-style-files.zip

The main text limit is nine pages; references and appendices are excluded. The official unmodified style and bibliography style are in `iclr2027/`. The draft includes the required AI use section. Human verification is pending, so that section must not claim it has happened. The old NeurIPS style files are retained only for provenance.

## Build

From `paper/`: `python3 build_taxonomy.py`, then `make`. Requires Python 3 and TeX Live with latexmk. Output: `iclr2027/rea.pdf`. The complete 71-domain, 609-subcategory taxonomy is generated from the same JSON used by the runtime; do not edit the generated appendix independently.

## Submission gate

Proceed only with completed, reproducible engineering evaluations against matched baselines, a defensible novelty comparison, verified citations, and author approval of every claim. Passing runtime tests and a synthetic recursion smoke test is not evidence of engineering superiority. Narrow the claim or use the fallback venue if evidence is insufficient.

See `EXPERIMENTS.md` for the evaluation protocol. `taxonomy-verification.json` is a local corpus audit, not a benchmark. The wider scite inventory is in `../docs/rlm/`; its candidate records are not all screened and should not automatically enter the manuscript bibliography.
