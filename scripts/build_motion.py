"""Compose one key visual per work from real frames; edit assets/motion/series.json to select frames."""
from pathlib import Path
import json
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
MOTION = ROOT / 'assets/motion'
SHOWCASE = ROOT / 'assets/showcase'
GUTTER = '#0d1117'


def frame_image(path, frame):
    with Image.open(path) as source:
        image = source.convert('RGB')
    if frame.get('crop'):
        image = image.crop(tuple(frame['crop']))
    return image


def key_visual(work, base=MOTION):
    """One large lead frame plus the remaining frames stacked on the right.

    Edge-to-edge, thin gutters only, no title text. The lead frame is the
    selection marked "lead": true, or the first one.
    """
    frames = work['selected_frames']
    if not frames:
        raise ValueError(f"Select at least one real frame for {work['slug']}")
    lead = next((f for f in frames if f.get('lead')), frames[0])
    rest = [f for f in frames if f is not lead]
    directory = base / work['candidates']
    gap, width = 12, 2400
    if rest:
        n = len(rest)
        # lead_w*9/16 == n*side_w*9/16 + (n-1)*gap  and  lead_w + gap + side_w == width
        side_w = round((width - gap - (n - 1) * gap * 16 / 9) / (n + 1))
        lead_w = width - gap - side_w
    else:
        side_w, lead_w = 0, width
    lead_h = round(lead_w * 9 / 16)
    canvas = Image.new('RGB', (width, lead_h), GUTTER)
    fit = lambda f, size: ImageOps.fit(frame_image(directory / f['file'], f), size,
                                       method=Image.Resampling.LANCZOS)
    canvas.paste(fit(lead, (lead_w, lead_h)), (0, 0))
    if rest:
        side_h = (lead_h - (len(rest) - 1) * gap) // len(rest)
        for i, frame in enumerate(rest):
            canvas.paste(fit(frame, (side_w, side_h)), (lead_w + gap, i * (side_h + gap)))
    destination = base / f"{work['slug']}.jpg"
    quality = 85
    while True:
        canvas.save(destination, quality=quality, optimize=True)
        if destination.stat().st_size <= 800_000:
            break
        quality -= 5
        if quality < 50:
            raise ValueError(f'{destination.name} exceeds 800 KB at quality 50')
    print(f'{destination.relative_to(ROOT)}: {canvas.width}×{canvas.height}, '
          f'{destination.stat().st_size} bytes, quality {quality}')


def main():
    config = json.loads((MOTION / 'series.json').read_text())
    for work in config['works']:
        key_visual(work)
    # Other works (not part of the series) reuse the same key-visual layout.
    showcase = SHOWCASE / 'showcase.json'
    if showcase.exists():
        for work in json.loads(showcase.read_text())['works']:
            key_visual(work, SHOWCASE)


if __name__ == '__main__':
    main()
