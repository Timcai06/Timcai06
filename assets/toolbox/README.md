# Toolbox SVGs

Run `python3 scripts/build_toolbox.py` to rebuild both 1200×890 theme variants offline. Edit the script, never the generated output.

`toolbox.json` preserves the six groups, labels and image URLs from the profile README before the table was replaced. `source/` vendors those existing skillicons.dev and shields.io SVGs, including light and dark skillicons variants, retrieved on 2026-10-11. These remain third-party logos, not original artwork. No tools were added to the existing stack list.

The builder embeds SVG elements and data-URI logos, prefixes IDs to avoid collisions, and rejects scripts, foreignObject, style elements, event handlers and external hrefs in input SVGs. Fonts use local system fallbacks. The frame uses neutral colors, interrupted perimeter lines, three corner marks, two-digit group numbers and a short bottom-center rule.

README selects the light/dark image using picture/source inside a centered paragraph. No GitHub table borders or custom README CSS are involved.

Tool icons are 64 px high; badge SVGs are scaled to 32 px high. Cards are 270 px high, with up to two centered badge rows and a 24 px gap between card rows.
