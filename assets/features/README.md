# Featured project panels

Build with `uv run --with fonttools --with pillow python scripts/build_feature_panels.py`,
then `python3 scripts/stamp_readme.py`.

The builder emits static PNG and animated, self-contained SVG versions in dark
and light palettes. The README uses static PNGs for reduced-motion preferences;
the SVGs also independently disable motion under that preference. No JavaScript,
external image requests or external fonts are used inside the SVGs. Captions are
converted to paths with the existing licensed DM Mono font.

EduCanvas shows three archived product screenshots, shown in four-second slots
with a 0.5-second crossfade. SciScope shows an archived Go TUI screenshot and a separate
Agent trace diagram. Its moving dot illustrates the event flow; it is not a
recording of application execution. Sources are copied unchanged into
`screenshots/`; `manifest.json` records their archive paths, types and hashes.
The source desktop files are not modified. Screenshots reflect their captured
version, not necessarily the latest application.

The film panel cycles through four real selected frames. Cropped source frames
are stored in `assets/motion/frames/`, allowing clean checkouts to rebuild without
private desktop originals. If selections or crop coordinates in
`assets/motion/series.json` change, remove the corresponding exported frame and
rebuild with the originals available. The original `clawd-mv.jpg` is retained.

Descriptions, full technology badge rows and repository links remain native
README content. EduCanvas retains its implementation disclosure and full-size image links.
SciScope has no implementation disclosure. The old compact SVG assets are retained but no longer used
for these two lead projects. The existing daily activity generators are unchanged.

Fonts and licenses are shared with `assets/showcase/fonts/`. Transparent outer
canvases inherit the profile background. Panel text supplements native
README descriptions rather than replacing essential accessible content.

Shared palette, title size, image radii and slideshow timing are maintained in
`scripts/visual_style.py`, also used by the Sophon and toolbox builders.
