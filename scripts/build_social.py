"""Build 1280×640 social preview images for the featured repositories.

Same pixel plates, editor-window language and card data as the profile cards
(imported from build_profile.py, which writes nothing when imported). Rasterized with headless Chrome; GitHub accepts < 1 MB.
Upload by hand: each repository's Settings → Social preview (no API exists).
"""
from pathlib import Path
import base64
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_profile as bp  # noqa: E402
from PIL import Image  # noqa: E402

OUT = bp.root / 'assets/social'
OUT.mkdir(exist_ok=True)
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
W, H = 1280, 640
# Window covers the frame; GitHub crops previews to roughly the central 1200×600.
X0, Y0, X1, Y1 = 90, 70, 1190, 570
text, rect = bp.text, bp.rect


def window(name, accent, data, mime='png'):
    b = ['<defs><filter id="shadow" x="-6%" y="-8%" width="112%" height="120%"><feDropShadow dx="0" dy="14" '
         'stdDeviation="16" flood-color="#02040c" flood-opacity=".6"/></filter></defs>',
         f'<image width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice" xlink:href="data:image/{mime};base64,{data}"/>',
         rect(0, 0, W, H, '#070b1b', 'opacity=".12"'),
         rect(X0, Y0, X1 - X0, Y1 - Y0, '#0e1527', f'rx="14" fill-opacity=".97" stroke="#354153" filter="url(#shadow)"')]
    for x, c in [(X0 + 28, '#f28c84'), (X0 + 52, '#e9ba79'), (X0 + 76, '#97bf9b')]:
        b.append(f'<circle cx="{x}" cy="{Y0 + 26}" r="7" fill="{c}"/>')
    b += [rect(W / 2 - 170, Y0 + 11, 340, 30, '#182036', 'rx="7" stroke="#2c3550"'),
          text(W / 2, Y0 + 32, f'github.com/Timcai06/{name}', 16, '#97a3bf', 'text-anchor="middle"'),
          rect(X0 + 1, Y0 + 52, X1 - X0 - 2, 1, '#2c3550'),
          rect(X0 + 1, Y1 - 40, X1 - X0 - 2, 39, '#252f48', 'rx="0"'),
          rect(X0 + 1, Y1 - 40, 110, 39, '#3a3356'),
          text(X0 + 20, Y1 - 14, '⎇ main', 17, '#f5d2a4'),
          text(X1 - 22, Y1 - 14, 'Tim Cai  ·  @Timcai06', 17, '#aab6d2', 'text-anchor="end"')]
    return b


def project(slug, name, tagline, desc, stack, accent):
    b = window(name, accent, bp.pixel_b64(f'{slug}.png'))
    left = X0 + 70
    b += [f'<text x="{left}" y="{Y0 + 150}" font-size="64" xml:space="preserve">'
          + bp.tspans([('# ', accent, ' opacity=".55"'), (name, accent, ' font-weight="700"')]) + '</text>',
          f'<text x="{left}" y="{Y0 + 205}" font-size="28" xml:space="preserve">'
          + bp.tspans([('> ', '#6c7a98', ''), (tagline, '#d6e0ef', ' font-style="italic"')]) + '</text>']
    for i, line in enumerate(desc):
        b.append(f'<text x="{left}" y="{Y0 + 262 + i * 40}" font-size="26" xml:space="preserve">'
                 + bp.tspans([('- ', accent, ''), (line, '#c4d3e8', '')]) + '</text>')
    CH, CF, PAD, GAP, XMAX = 36, 19, 26, 10, X1 - 70
    rows, row, x = [], [], left
    for item in stack:
        w = round(len(item) * CF * 0.6 + PAD)
        if row and x + w > XMAX:
            rows.append(row); row, x = [], left
        row.append((item, x, w)); x += w + GAP
    rows.append(row)
    assert len(rows) <= 2, name
    for r, chips in enumerate(rows):
        top = Y0 + 352 + r * (CH + 10)
        for item, x, w in chips:
            b += [rect(x, top, w, CH, accent, f'rx="7" fill-opacity=".14" stroke="{accent}" stroke-opacity=".45"'),
                  text(x + w / 2, top + 25, item, CF, accent, 'text-anchor="middle"')]
    return bp.svg(W, H, b, f'{name} — {tagline}')


def clawd():
    # The window is a video player showing the README key-visual collage.
    bg = bp.pixel_b64('background.png')
    still = base64.b64encode((bp.root / 'assets/motion/clawd-mv.jpg').read_bytes()).decode()
    accent = '#f28c84'
    b = window('clawd-mv', accent, bg)
    px0, py0, px1, py1 = X0 + 1, Y0 + 53, X1 - 1, Y1 - 120
    b += [f'<clipPath id="player"><rect x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}"/></clipPath>',
          f'<image x="{px0}" y="{py0}" width="{px1 - px0}" height="{py1 - py0}" preserveAspectRatio="xMidYMid slice" '
          f'clip-path="url(#player)" xlink:href="data:image/jpeg;base64,{still}"/>',
          rect(px0, py1 - 6, px1 - px0, 6, '#2c3550'), rect(px0, py1 - 6, (px1 - px0) * 0.38, 6, accent),
          f'<circle cx="{W / 2}" cy="{(py0 + py1) / 2}" r="44" fill="#0e1527" fill-opacity=".72" stroke="{accent}" stroke-width="2"/>',
          f'<path d="M {W / 2 - 14} {(py0 + py1) / 2 - 22} L {W / 2 + 24} {(py0 + py1) / 2} L {W / 2 - 14} {(py0 + py1) / 2 + 22} Z" fill="{accent}"/>',
          f'<text x="{X0 + 40}" y="{py1 + 50}" font-size="38" xml:space="preserve">'
          + bp.tspans([('clawd-mv', accent, ' font-weight="700"'), ('  Works on My Machine', '#d6e0ef', ' font-style="italic"')]) + '</text>',
          text(X1 - 40, py1 + 48, 'TypeScript · Three.js · code-rendered MV', 19, '#97a3bf', 'text-anchor="end"')]
    return bp.svg(W, H, b, 'clawd-mv — Works on My Machine')


def rasterize(svg_text, out_png):
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / 'page.html'
        page.write_text('<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:#070b1b}'
                        'svg{display:block}</style>' + svg_text)
        shot = Path(tmp) / 'shot.png'
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--force-device-scale-factor=1',
                        f'--window-size={W},{H}', f'--screenshot={shot}', page.as_uri()],
                       check=True, capture_output=True)
        image = Image.open(shot).convert('RGB')
    assert image.size == (W, H), image.size
    image.save(out_png, 'PNG', optimize=True)
    if out_png.stat().st_size >= 1_000_000:  # GitHub's limit; photos compress better as JPEG
        out_png.unlink()
        out_png = out_png.with_suffix('.jpg')
        image.save(out_png, 'JPEG', quality=90, optimize=True)
    return out_png


# Social previews use a Menlo fallback: Chrome only sees installed fonts.
bp.FONT = "'SFMono-Regular',Menlo,Consolas,monospace"
for slug, name, tagline, desc, stack, accent in bp.compact:
    print(rasterize(project(slug, name, tagline, desc, stack, accent), OUT / f'{name}.png').name)
print(rasterize(clawd(), OUT / 'clawd-mv.png').name)
