"""Build the hero SVGs locally (no external service).

- title: "Hi, I'm Tim Cai" in a 5x7 pixel font, matching the page's pixel art. A 16 s
  loop: columns light up and drop in left to right, a block cursor blinks, a highlight
  sweeps the letters twice, stars twinkle, a meteor passes, then the columns go out.
- tagline: typed lines (a textPath whose path grows and shrinks via SMIL, JetBrains
  Mono subset embedded), with a block cursor that follows the reveal edge.
Run with: uv run --with fonttools python scripts/build_hero.py
"""
from pathlib import Path
from html import escape
from io import BytesIO
import base64

from fontTools import subset
from fontTools.ttLib import TTFont

from pixel_font import columns, render

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/hero'
FONTS = OUT / 'fonts'
COLORS = {'dark': '#79C0FF', 'light': '#0969DA'}
WEIGHT_FILE = {500: 'JetBrainsMono-Medium.ttf'}

HEROES = [
    dict(name='tagline', weight=500, size=18, width=760, height=50, letter_spacing='normal',
         duration=3000, pause=900, repeat=True, lines=['Building evidence-grounded AI systems',
                                                       'Designing ML tools you can inspect',
                                                       'Turning experiments into useful products']),
]


def font_face(weight, chars):
    font = TTFont(FONTS / WEIGHT_FILE[weight], recalcTimestamp=False)  # stable bytes across builds
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
        # Block cursor on the reveal edge, clamped to the text (JetBrains Mono advance = 0.6 em).
        tw = len(line) * h['size'] * 0.6
        left, right = w / 2 - tw / 2, w / 2 + tw / 2
        t_l, t_r = left / w * k1, right / w * k1
        e_r, e_l = k2 + (1 - right / w) * (1 - k2), k2 + (1 - left / w) * (1 - k2)
        xs = f'{left:.1f};{left:.1f};{right:.1f};{right:.1f};{right:.1f};{left:.1f};{left:.1f}'
        kt = f'0;{t_l:.6f};{t_r:.6f};{k2:.6f};{e_r:.6f};{e_l:.6f};1'
        body.append(f'<rect y="{y - 11}" width="10" height="22" fill="{color}" opacity="0">'
                    f'<set attributeName="opacity" to=".75" begin="d{i}.begin" end="d{i}.end"/>'
                    f'<animate attributeName="x" begin="d{i}.begin" dur="{total:g}ms" values="{xs}" keyTimes="{kt}"/>'
                    f'<animate attributeName="fill-opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1s" repeatCount="indefinite"/></rect>')
        body.append(f'<text font-family="\'JetBrains Mono\', monospace" font-weight="{h["weight"]}" fill="{color}" '
                    f'font-size="{h["size"]}" dominant-baseline="middle" x="50%" text-anchor="middle" '
                    f'letter-spacing="{h["letter_spacing"]}"><textPath xlink:href="#path{i}">{escape(line)}</textPath></text>')
    style = font_face(h['weight'], ''.join(h['lines']))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {w} {h["height"]}" width="{w}" height="{h["height"]}" role="img">'
            f'<title>{escape("; ".join(h["lines"]))}</title><style>{style}</style>' + ''.join(body) + '</svg>')


PIXEL = {'dark': dict(top='#b6dcff', bottom='#4f9cf0', shadow='#14304f', shine='#ffffff', stars=('#f2c48f', '#8fa0d8')),
         'light': dict(top='#3f8ef5', bottom='#0550ae', shadow='#c9dcf5', shine='#ffffff', stars=('#bf8700', '#54aeff'))}


def pixel_title(theme, text="Hi, I'm Tim Cai", W=540, H=80, P=6, S=5, LOOP=16):
    pal = PIXEL[theme]
    cols = columns(text)
    x0, y0 = round((W - (len(cols) + 2) * P) / 2), round((H - 7 * P) / 2) + 4
    css = [f'@keyframes px{{0%{{opacity:0;transform:translateY(-8px)}}2.5%{{opacity:1;transform:translateY(0)}}'
           f'93%{{opacity:1;transform:translateY(0)}}96%,100%{{opacity:0;transform:translateY(0)}}}}',
           '@keyframes blink{0%{opacity:1}50%{opacity:0}}.blink{animation:blink 1.1s step-end infinite}',
           f'@keyframes cur{{0%,11%{{opacity:0}}11.5%,93%{{opacity:1}}93.5%,100%{{opacity:0}}}}.cur{{animation:cur {LOOP}s step-end infinite}}',
           f'@keyframes shine{{0%,26%{{transform:translateX(0)}}36%,58%{{transform:translateX({W + 160}px)}}58.01%{{transform:translateX(0)}}'
           f'68%,100%{{transform:translateX({W + 160}px)}}}}.shine{{animation:shine {LOOP}s ease-in-out infinite}}',
           '@keyframes tw{0%,100%{opacity:.25}50%{opacity:1}}',
           f'@keyframes met{{0%,47%{{opacity:0;transform:translate(0,0)}}48%{{opacity:1}}53%,100%{{opacity:0;transform:translate(150px,26px)}}}}'
           f'.met{{animation:met {LOOP}s linear infinite}}',
           '@media (prefers-reduced-motion:reduce){*{animation:none!important}}']
    lit, mask = render(text, x0, y0, P, S, pal['top'], pal['bottom'], pal['shadow'])
    body = [f'<g style="animation:px {LOOP}s cubic-bezier(.2,.8,.2,1) {k * 0.022:.3f}s infinite backwards">{cells}</g>' for k, cells in lit]
    cx = x0 + (len(cols) + 1) * P
    body.append(f'<g class="cur"><rect x="{cx}" y="{y0}" width="{S}" height="{7 * P - 1}" fill="{pal["bottom"]}" class="blink"/></g>')
    body.append(f'<defs><mask id="letters">{"".join(mask)}</mask><linearGradient id="sh" x1="0" x2="1">'
                f'<stop offset="0" stop-color="{pal["shine"]}" stop-opacity="0"/><stop offset=".5" stop-color="{pal["shine"]}" stop-opacity=".85"/>'
                f'<stop offset="1" stop-color="{pal["shine"]}" stop-opacity="0"/></linearGradient></defs>'
                f'<g mask="url(#letters)"><rect class="shine" x="-120" y="0" width="70" height="{H}" fill="url(#sh)" transform="skewX(-18)"/></g>')
    stars = [(x0 - 26, 18, 0), (x0 + 70, 9, 1), (x0 + 205, 12, 0), (cx + 22, 20, 1), (cx - 60, 70, 0), (x0 + 30, 70, 1)]
    for k, (sx, sy, c) in enumerate(stars):
        col = pal['stars'][c]
        body.append(f'<g style="animation:tw {2.6 + k % 3 * .7:.1f}s ease-in-out {k * .5:.1f}s infinite" opacity=".8">'
                    f'<rect x="{sx}" y="{sy}" width="2" height="2" fill="{col}"/><rect x="{sx - 2}" y="{sy + .5}" width="6" height="1" fill="{col}" opacity=".5"/>'
                    f'<rect x="{sx + .5}" y="{sy - 2}" width="1" height="6" fill="{col}" opacity=".5"/></g>')
    body.append(f'<g class="met" opacity="0"><path d="M {x0 + 40} 4 l 22 4" stroke="{pal["stars"][0]}" stroke-width="2"/>'
                f'<rect x="{x0 + 61}" y="7" width="3" height="3" fill="{pal["shine"]}"/></g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img">'
            f'<title>{escape(text)}</title><style>{"".join(css)}</style>' + ''.join(body) + '</svg>')


for theme in PIXEL:
    (OUT / f'title-{theme}.svg').write_text(pixel_title(theme))
for hero in HEROES:
    for theme, color in COLORS.items():
        (OUT / f'{hero["name"]}-{theme}.svg').write_text(build(hero, color))
print('Built hero title (pixel) and tagline SVGs')
