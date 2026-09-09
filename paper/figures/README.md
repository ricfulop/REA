# Corpus capacity and recursive investigation figures

Both figures are analytical/conceptual, not measured performance results. They use an assumed 1M-token comparison window rather than a claim about a specific commercial model.

- `corpus-capacity.pdf/png/svg`: explicit 60M-part and 1M-manual scenario, logarithmic token scale. At 500 tokens/part, parts alone occupy 30B tokens (30,000 windows, 4.48 orders of magnitude). At 10,000 tokens/manual, manuals occupy 10B (10,000 windows, four orders). Combined: 40B (40,000 windows, 4.60 orders). A 1M window holds 2,000 assumed specifications before any other prompt content: 0.00333% of the catalog.
- `recursive-workflow.pdf/png/svg`: single-call prompt, iterative retrieval agent, and REA recursive investigation. All calls are bounded; retrieval agents can also access large corpora. Paging and durable state are explicitly marked as required work for the target scale.

`scenarios.json` records assumptions and exclusions. `capacity-data.csv` contains plotted values; `sensitivity-data.csv` varies token densities. Neither interval is statistical uncertainty. No tokenizer was used: densities are scenario parameters, not observed tokens. Figures exclude images, CAD geometry, simulation output, metadata overhead and deduplication. A window equivalent does not estimate calls, runtime, or dollars.

Run `python3 paper/figures/build_figures.py` from the repository root. Python 3 with Matplotlib is required; the export manifest records the version used. PDF/SVG are vector artwork; PNG previews are 300 dpi. Figures use the Science skill’s 7.24-inch canvas width and are included at manuscript text width. Labels and distinct marker shapes provide redundant encodings.

## Alt text

Capacity figure: A log-scale dot plot places a one-million-token prompt at 1M tokens, assumed manuals at 10B, assumed part specifications at 30B, and their sum at 40B. The assumed corpus exceeds one prompt by roughly four orders of magnitude. These are capacity calculations, not measured system results.

Workflow figure: Three rows compare a fixed evidence prompt, an iterative retrieval agent, and recursive engineering investigation. REA branches into specification and procedure subcalls and integrates cited findings. A dashed paging and persistent-state box marks work needed to reach the proposed large-catalog scale. The diagram makes no accuracy comparison.

## Next empirical figure

Measure independently checked engineering success against corpus size, with matched cost and model budgets. Include a multi-turn retrieval baseline. Pair each correctness plot with latency/cost and evidence recall. Leave results absent until runs complete; never populate curves from assumed advantages.

## Figure style

Restyled using Ric Fulop's `science-figure-style` skill and its canonical `sci-viz-mcp/styles.py`. The implementation remains external to this repository. Set `REA_FIGURE_STYLE` to its local path to rebuild; its SHA-256 is recorded in the manifest. Rendered outputs are provided for readers without the private style module. Styling uses Helvetica (Arial/DejaVu Sans fallback), the canonical Okabe-Ito palette, outward major ticks, no minor ticks or grid, black typography, white backgrounds, and caption-only figure titles. Standalone single figures omit redundant A/B labels. Lettering is enlarged on the 7.24-inch Science canvas to remain legible when included at ICLR text width. The manuscript remains in the official ICLR template; this is a visual style choice, not a Science submission.
