# Pixel backgrounds

`v2/` holds the six calm pixel-art plates used behind the editor artwork: `background.png` (workspace and footer) and one per project card (`tttim`, `bdi`, `sciscope`, `educanvas`, `pulsegraph`). They were generated as 1536×1024 atmosphere plates with a near-empty centre, because the editor windows cover ~90% of the frame and only the edges show. They are not product screenshots.

`scripts/build_profile.py` quantizes each plate to 8 colours (median cut, no dithering, no resampling) when embedding it; the PNGs on disk are kept as generated. Earlier, busier scenes were removed from the repository and remain in git history.
