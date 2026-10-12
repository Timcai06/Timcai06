"""Build the hero typing SVGs locally (replaces readme-typing-svg.demolab.com).

Same mechanism as the hosted service: a textPath whose path grows and shrinks
via SMIL, with a subset of JetBrains Mono embedded so the look does not depend
on installed fonts. Run with: uv run --with fonttools python scripts/build_hero.py
"""
from pathlib import Path
from html import escape
from io import BytesIO
import base64

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/hero'
FONTS = OUT / 'fonts'
COLORS = {'dark': '#79C0FF', 'light': '#0969DA'}
WEIGHT_FILE = {500: 'JetBrainsMono-Medium.ttf', 600: 'JetBrainsMono-SemiBold.ttf'}

HEROES = [
    dict(name='title', weight=600, size=30, width=540, height=50, letter_spacing='1px',
         duration=1800, pause=6000, repeat=True, lines=["Hi, I'm Tim Cai"]),
    dict(name='tagline', weight=500, size=18, width=760, height=50, letter_spacing='normal',
         duration=3000, pause=900, repeat=True, lines=['Building evidence-grounded AI systems',
                                                       'Designing ML tools you can inspect',
                                                       'Turning experiments into useful products']),
]


def font_face(weight, chars):
    font = TTFont(FONTS / WEIGHT_FILE[weight])
    options = subset.Options()
    options.layout_features = []
    options.name_IDs = []
    options.notdef_outline = True
    subsetter = subset.Subsetter(options)
    subsetter.populate(text=''.join(sorted(set(chars))))
    subsetter.subset(font)
    buffer = BytesIO()
    font.save(buffer)
    data = base64.b64encode(buffer.getvalue()).decode()
    return (f"@font-face{{font-family:'JetBrains Mono';font-style:normal;font-weight:{weight};"
            f"src:url(data:font/truetype;base64,{data}) format('truetype');}}")


def build(h, color):
    # Timing follows the hosted service: type in 80% of `duration`, hold for
    # `pause`, then erase in the remaining 20% (or hold the last line).
    w, y = h['width'], h['height'] // 2
    typing, erase = h['duration'] * 0.8, h['duration'] * 0.2
    total = typing + h['pause'] + erase
    k1, k2 = typing / total, (typing + h['pause']) / total
    n = len(h['lines'])
    body = []
    for i, line in enumerate(h['lines']):
        last = i == n - 1
        if h['repeat']:
            begin = f'0s;d{n - 1}.end' if i == 0 else f'd{i - 1}.end'
            fill, end_w = 'remove', 0
        else:
            begin = '0s' if i == 0 else f'd{i - 1}.end'
            fill, end_w = ('freeze', w) if last else ('remove', 0)
        values = f'm0,{y} h0 ; m0,{y} h{w} ; m0,{y} h{w} ; m0,{y} h{end_w}'
        body.append(f'<path id="path{i}"><animate id="d{i}" attributeName="d" begin="{begin}" dur="{total:g}ms" '
                    f'fill="{fill}" values="{values}" keyTimes="0;{k1:.6f};{k2:.6f};1"/></path>')
        body.append(f'<text font-family="\'JetBrains Mono\', monospace" font-weight="{h["weight"]}" fill="{color}" '
                    f'font-size="{h["size"]}" dominant-baseline="middle" x="50%" text-anchor="middle" '
                    f'letter-spacing="{h["letter_spacing"]}"><textPath xlink:href="#path{i}">{escape(line)}</textPath></text>')
    style = font_face(h['weight'], ''.join(h['lines']))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {w} {h["height"]}" width="{w}" height="{h["height"]}" role="img">'
            f'<title>{escape("; ".join(h["lines"]))}</title><style>{style}</style>' + ''.join(body) + '</svg>')


for hero in HEROES:
    for theme, color in COLORS.items():
        (OUT / f'{hero["name"]}-{theme}.svg').write_text(build(hero, color))
print('Built hero typing SVGs')
