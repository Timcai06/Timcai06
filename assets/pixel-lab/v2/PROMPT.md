# Pixel backgrounds v2 — prompt for Codex

Generate 6 new images with the image tool and save them to `assets/pixel-lab/v2/`. **Do not modify or overwrite any file directly under `assets/pixel-lab/`.** Then run `python3 scripts/build_profile.py`. The script uses an image from v2 when one exists with the same name.

## Why they are being redone

The current pixel images carry too much information to work as backgrounds. Each one is used **only as a backdrop** behind a code-editor window. The window covers the middle 90%+ of the image, so only a thin border shows around the edges:

- `background.png` → `workspace.svg` (1200×800). Visible: about 60px at the top, about 66px at the bottom, about 45px on each side.
- The other 5 → project cards at 640×430. Visible: about 52px at the top, about 42px at the bottom, about 24px on each side.
- The editor window is 95% opaque, so the middle shows through very faintly.

So the images should have no subject, no story and no small objects. They should be a calm atmosphere layer.

## Shared requirements (put these at the start of every prompt)

```
Calm atmospheric pixel-art background plate, 3:2 landscape, 1536×1024.
It will sit BEHIND a large opaque code-editor window that covers the center 90% —
only a thin border around the edges stays visible. Treat it as a quiet backdrop, not an illustration.

- Chunky, clean pixel art with a coarse pixel grid (each art pixel ≈ 6–8 px). No dithering noise, no fine texture.
- Large flat color fields and soft banded gradients. Very low detail density.
- Center area: almost empty, smooth low-contrast gradient — nothing important there.
- At most 2–3 simple motifs, large and simplified, placed so they read along the edges/corners.
- Limited palette, max 8 colors, low contrast overall; darkest-to-lightest range kept narrow.
  Base: deep indigo #10142a → #1b2140, muted lavender #6c6a9e, with one small accent color (given below).
- No text, letters, logos, UI, screens, monitors, people, desks, books, or small props.
- No vignette frame, border, or card edge. Edge-to-edge.
- Mood: quiet night, lots of breathing room.
```

## Each image (append the matching line to the shared requirements)

| File | Description to append | Accent |
|---|---|---|
| `background.png` | Distant night lake horizon: a single low mountain silhouette band along the bottom edge, a thin moon glow near the top-right corner, a few sparse stars only near the top edge. | warm amber #e9b97f, used only for the moon glow |
| `tttim.png` | Abstract architecture: one or two huge, simplified dark arch silhouettes touching the left and right edges, a faint violet sky gradient, a single small silver sphere near the top-left corner. | soft pink-violet #e4b6eb |
| `bdi.png` | A single long, low, simplified bridge-arch silhouette spanning the bottom edge over still water, dusk gradient sky, no drone, no inspection overlays. | twilight orange #efba85, used only near the horizon |
| `sciscope.png` | Deep navy sky with very sparse stars, a few thin faint constellation lines along the top and side edges suggesting connected evidence, no globe, no papers. | cool blue #9ec9e9 |
| `educanvas.png` | Warm dusk window light: large soft rectangular light shapes falling from the top-left corner, one simple plant-leaf silhouette in the bottom-right corner, no laptop, no desk. | warm amber #e8c397 |
| `pulsegraph.png` | A single smooth, wide waveform/training-curve line running across the bottom edge, faint horizontal grid bands, no CRT, no lab equipment. | violet #b9afea |

## Acceptance (to check after generation)

- Output files are 1536×1024 PNG and their names exactly match the table.
- Files under `assets/pixel-lab/` are byte-identical to before (`git status` / `shasum` shows no change).
- `python3 scripts/build_profile.py && python3 scripts/build_preview.py` runs without errors.
- Visual acceptance is done by Tim; Codex does not make aesthetic judgments.
