# Toolbox SVGs

Run `uv run --with fonttools python scripts/build_toolbox.py` to rebuild both 1200×1400 theme variants offline. Edit the script, never the generated output.

`toolbox.json` preserves the six groups, labels and image URLs from the profile README before the table was replaced. `source/` vendors those existing skillicons.dev and shields.io SVGs, including light and dark skillicons variants, retrieved on 2026-10-11. These remain third-party logos, not original artwork. Additional text chips cover Node.js, Lenis, OGL and Playwright, already present in the profile project descriptions. A dedicated Agent engineering row adds LangGraph, Agent runtime, RAG, tool orchestration and SSE.

The builder embeds SVG elements and data-URI logos, prefixes IDs to avoid collisions, and rejects scripts, foreignObject, style elements, event handlers and external hrefs in input SVGs. Fonts use local system fallbacks. The frame uses neutral colors, interrupted perimeter lines, three corner marks, two-digit group numbers and a short bottom-center rule.

README selects the light/dark image using picture/source inside a centered paragraph. No GitHub table borders or custom README CSS are involved.

Tool icons are 64 px high; badge SVGs are scaled to 32 px high. Open groups are 310 px high, with up to two centered badge rows and a 24 px gap between card rows.

The Agent engineering header precedes the six original groups. Each group now includes a project or usage caption. All entries, including text-only chips and Agent tools, are included in the searchable native text beneath the image.

The current layout uses a shared editorial palette from `scripts/visual_style.py`, a Big Shoulders wordmark outlined from the vendored font, left-aligned groups and hairline separators. The earlier decorative card borders and group numbering have been removed. The full native technology index is retained in a disclosure.
