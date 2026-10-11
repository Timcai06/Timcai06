# Editor profile assets

Regenerate with `python3 scripts/build_profile.py` from the repository root.

`workspace.svg` embeds the unchanged image-generated pixel background and draws the editor UI with SVG text and shapes. Section strips share the same palette and tab treatment. No external fonts, scripts or foreignObject are used. The README contains selectable text, public repository links and descriptions independently of the decorative SVGs.

Content was checked against GitHub repository metadata and default-branch READMEs on 2026-10-11. This is a curated selection: package distribution repositories and forks are not shown as separate original projects. Seen and Sophon have names and short descriptions only, as authorized; no private repository URLs are included. Electricity modeling is also described without its private repository URL.

Preview the README in VS Code or on GitHub; there is no separate local preview. Editor tabs/file tree are static illustration, not interactive controls.

## Project workspaces

SciScope, EduCanvas and PulseGraph each have a self-contained SVG workspace, with their previous pixel illustrations repurposed strictly as backgrounds behind the editor. Their readable descriptions and repository links are also present as native README HTML. Eight native `<details>` sections retain the complete content while keeping the initial view compact. No scripts are needed for expansion.

## Featured hierarchy revision

TTT-I-M and BDI lead the two-column grid; SciScope and EduCanvas follow. PulseGraph uses a side-by-side image/text row. Compact SVGs are composed for half-width placement instead of shrinking the old wide sidebar layout. INA is omitted from the profile selection.

Code in motion is a separate ongoing code-animation series. Its first listed work is clawd-mv. The series artwork is native SVG timeline/scene art; no future works are presented as completed.

TTT-I-M uses a newly generated pixel architecture/cosmic-stage backdrop (`assets/pixel-lab/tttim.png`); BDI uses the bridge scene. Each remaining project uses its own earlier scene as background, never a claimed product screenshot.

## Hierarchy revision (2026-10-11, round 2)

Reading order: who I am → featured work → Code in motion → toolbox & more.

- The published hero (typing title, Blog/Email badges, typing subtitle "Building… / Designing… / Turning…") is kept verbatim above `workspace.svg`; the old website/email nav line was replaced by in-page section anchors to avoid duplicating the badges.
- Featured work has two tiers: TTT-I-M and BDI as a two-column grid of cards (image, description, badges and links visible); SciScope, EduCanvas and PulseGraph as a list with the image on the left and text on the right. Project descriptions are no longer collapsed.
- Code in motion keeps its series banner; works are numbered rows (01 clawd-mv). No future works are listed.
- The toolbox restores the skillicons icons and shields badges from the published/earlier README, grouped by category.
- The section strip SVGs (`about`, `agents`, `products`, `creative`, `toolbox`, `models`) and the wide project SVGs are no longer referenced by the README. They are kept on disk.
- Only two `<details>` remain, none nested: more projects and mathematical modeling. The full bilingual intro is shown directly under the workspace image (round 3, at Tim's request). Seen/Sophon are visible names with short descriptions and no links.

## Backgrounds v2 and series banner (2026-10-11, round 3)

- Editor SVGs now embed `assets/pixel-lab/v2/*.png` when present. At build time each is quantized to an 8-colour palette (median cut, no dithering, no resampling); the generated PNGs on disk are not modified. Each SVG dropped from about 1.6–1.9 MB to about 50–140 KB.
- Code in motion is split into two levels: a centred series statement (text only) and one bordered card per work. Each work's key visual is `assets/motion/<slug>.jpg`, composed by `scripts/build_motion.py` from the frames in `assets/motion/series.json`: one lead frame (`"lead": true`) plus the rest stacked on the right, edge to edge, with no title text. `series-banner.jpg` and `animation-series.svg` are no longer referenced.
- Raw frames, the contact sheet and Codex process records stay local (see `.gitignore`).

## Featured order and navigation (2026-10-11, round 4)

- Chapters are centred `<h1>` openers (01–04). Subsections use a `<kbd>` label plus bold English.
- Lead projects are EduCanvas and SciScope (two-column cards). TTT-I-M, BDI and PulseGraph follow as "Also featured" rows. The workspace file tree and `featured` array use the same order.
- The in-page anchor nav under the workspace image was removed (GitHub always renders links blue).
- Hero contact badges: Instagram and LinkedIn were added after Blog/Email (2026-10-11, at Tim's request), so the hero is no longer byte-identical to the originally published block. URLs come from the GitHub profile's social accounts. LinkedIn has no shields/simple-icons logo; the badge embeds a minimal "in" SVG as a data URI.
- Project cards are 640×540: README pane (markdown, stack chips) plus a terminal panel showing two real quick-start commands quoted from each repository's README (`TERMINAL_CMDS` in `build_profile.py`), an idle prompt with cursor, and the status bar.
- Chapter 04 folds: "其他作品" and "数学建模" are sibling `<details>`; inside "数学建模" each of the 5 projects has its own `<details>` (two levels, at Tim's request). `scripts/build_modeling.py` still finds each project fold by its summary title.
