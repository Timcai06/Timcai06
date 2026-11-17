"""Compose project panels from archived product screenshots and real movie frames.

Movie stills are exported from the existing selection once and kept in frames/ so
the published panels can also be rebuilt without the local desktop originals.
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps
from visual_frame import frame
from visual_style import WIDTH, DISPLAY_SIZE, HERO_RADIUS, DETAIL_RADIUS, SLIDE_SECONDS, FADE_SECONDS, palette

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/features'
FONTS = ROOT / 'assets/showcase/fonts'
W = WIDTH


def font(size, face='DMMono-Regular.ttf'):
    return ImageFont.truetype(str(FONTS / face), size)


def text(im, xy, value, size, color, face='DMMono-Regular.ttf'):
    ImageDraw.Draw(im).text(xy, value, font=font(size, face), fill=color)


def picture(im, source, box, radius=HERO_RADIUS, cut=0):
    x, y, w, h = box
    tile = ImageOps.fit(source.convert('RGB'), (w, h), method=Image.Resampling.LANCZOS)
    im.paste(tile, (x, y))
    frame(im, box, radius, cut)


def movie_frames():
    base = ROOT / 'assets/motion'
    work = json.loads((base / 'series.json').read_text())['works'][0]
    dest = base / 'frames'
    dest.mkdir(exist_ok=True)
    result = []
    for f in work['selected_frames']:
        target = dest / (f['scene'].lower() + '.jpg')
        if not target.exists():
            with Image.open(base / work['candidates'] / f['file']) as raw:
                cropped = raw.convert('RGB').crop(tuple(f['crop']))
                cropped.thumbnail((1800, 1200), Image.Resampling.LANCZOS)
                cropped.save(target, quality=89, optimize=True)
        result.append(Image.open(target))
    return result


def build(light=False):
    colors = palette(light)
    ink, muted, rail = (colors[k] for k in ('ink', 'muted', 'rail'))
    suffix = '-light' if light else ''

    def panel(height):
        return Image.new('RGBA', (W, height))

    def heading(im, left, right):
        text(im, (80, 35), left, 24, muted)
        f = font(24)
        text(im, (1720-f.getlength(right), 35), right, 24, muted)
        ImageDraw.Draw(im).line((80, 86, 1720, 86), fill=rail, width=2)

    def save(im, name):
        im.save(OUT / f'{name}{suffix}.png', optimize=True)

    mv = panel(1970)
    heading(mv, 'TIM CAI / SELECTED WORK', 'CODE IN MOTION')
    text(mv, (75, 111), 'WORKS ON', 160, ink, 'BigShoulders-Bold.ttf')
    text(mv, (75, 275), 'MY MACHINE', 160, ink, 'BigShoulders-Bold.ttf')
    text(mv, (1120, 215), 'A music video,', 43, ink, 'CrimsonPro-Italic.ttf')
    text(mv, (1120, 270), 'composed in code.', 43, ink, 'CrimsonPro-Italic.ttf')
    text(mv, (1120, 366), 'SCENES / CAMERAS / TIME', 23, muted)
    frames = movie_frames()
    picture(mv, frames[3], (80, 490, 1640, 922))
    text(mv, (80, 1438), 'S18 / CLOSING CREDITS', 24, muted)
    for i, (f, label) in enumerate(zip(frames[:3], ['S03 / OCTOBER 32', 'S11 / UNDEFINED', 'S13 / LOCAL vs CI'])):
        x = 80 + i * 556
        picture(mv, f, (x, 1530, 528, 297), radius=DETAIL_RADIUS, cut=24)
        text(mv, (x, 1855), label, 22, muted)
    text(mv, (80, 1920), 'TypeScript + Three.js / offline rendering', 23, muted)
    save(mv, 'motion')

    shots = OUT / 'screenshots'
    edu = panel(1370)
    heading(edu, 'TIM CAI / SELECTED WORK', 'AGENT ENGINEERING')
    text(edu, (75, 110), 'EduCanvas', DISPLAY_SIZE, ink, 'BigShoulders-Bold.ttf')
    text(edu, (1090, 175), 'A place to learn.', 60, ink, 'CrimsonPro-Italic.ttf')
    text(edu, (1090, 260), 'A PERSONAL LEARNING AGENT', 24, muted)
    edu_box = (80, 370, 1640, 895)
    picture(edu, Image.open(shots / 'educanvas-focus-mode.webp'), edu_box)
    text(edu, (80, 1295), 'FOCUS / A QUIET SPACE TO BEGIN', 24, muted)
    save(edu, 'educanvas')
    animated(edu, 'educanvas', suffix, edu_box, [
        shots / 'educanvas-focus-mode.webp', shots / 'educanvas-learning-response.webp',
        shots / 'educanvas-home.webp'], ink, muted,
        ['FOCUS / A QUIET SPACE TO BEGIN', 'LEARNING / COMPUTER VISION', 'NOTEBOOK / HOME'], (80, 1295))

    sci = panel(2120)
    heading(sci, 'TIM CAI / SELECTED WORK', 'RESEARCH AGENT')
    text(sci, (75, 110), 'SciScope', DISPLAY_SIZE, ink, 'BigShoulders-Bold.ttf')
    text(sci, (1050, 175), 'Follow the evidence.', 60, ink, 'CrimsonPro-Italic.ttf')
    text(sci, (1050, 260), 'RESEARCH IN THE TERMINAL', 24, muted)
    tui = Image.open(shots / 'sciscope-tui-product.webp').crop((0, 160, 1600, 825))
    picture(sci, tui, (80, 370, 1640, 682))
    text(sci, (80, 1080), 'GO TUI / PRODUCT SCREENSHOT', 24, muted)
    text(sci, (80, 1170), 'The process is part of the answer.', 65, ink, 'CrimsonPro-Italic.ttf')
    trace = Image.open(shots / 'sciscope-agent-trace.webp').crop((35, 250, 1565, 770))
    picture(sci, trace, (80, 1300, 1640, 557), radius=DETAIL_RADIUS, cut=30)
    text(sci, (80, 1885), 'AGENT TRACE / WORKFLOW DIAGRAM', 24, muted)
    d = ImageDraw.Draw(sci)
    d.line((80, 1995, 1720, 1995), fill=rail, width=2)
    for x, label in [(80, 'plan'), (420, 'tool_call'), (800, 'tool_result'), (1190, 'reflect'), (1590, 'final')]:
        d.ellipse((x, 1989, x+12, 2001), fill=muted)
        text(sci, (x, 2025), label, 23, muted)
    save(sci, 'sciscope')
    animated(sci, 'sciscope', suffix, None, [], ink, muted)
    # The film also gets a slow cut between real selected frames.
    animated(mv, 'motion', suffix, (80, 490, 1640, 922),
             [ROOT / 'assets/motion/frames' / (s + '.jpg') for s in ['s18', 's03', 's11', 's13']],
             ink, muted, ['S18 / CLOSING CREDITS', 'S03 / OCTOBER 32', 'S11 / UNDEFINED', 'S13 / LOCAL vs CI'], (80, 1438))


def animated(base, name, suffix, box, sources, ink, muted, labels=None, label_xy=None):
    """Self-contained SVG; only presentation moves, never fabricated application state."""
    import base64
    from io import BytesIO
    from html import escape
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.ttLib import TTFont

    def data(im, fmt='PNG'):
        buf = BytesIO()
        im.save(buf, format=fmt, **({'quality': 86, 'optimize': True} if fmt == 'JPEG' else {}))
        return 'data:image/' + fmt.lower() + ';base64,' + base64.b64encode(buf.getvalue()).decode()

    # Convert captions to paths so the typography is stable in GitHub image mode.
    def caption(value, x, y):
        f = TTFont(FONTS / 'DMMono-Regular.ttf'); gs = f.getGlyphSet(); cmap = f.getBestCmap()
        scale = 24 / f['head'].unitsPerEm; paths = []; cursor = x
        for char in value:
            glyph = gs[cmap[ord(char)]]; pen = SVGPathPen(gs); glyph.draw(pen)
            paths.append(f'<path d="{pen.getCommands()}" transform="translate({cursor},{y+24}) scale({scale},-{scale})"/>')
            cursor += glyph.width*scale
        f.close()
        return '<g fill="'+muted+'">'+''.join(paths)+'</g>'

    clean = base.copy()
    if labels:
        ImageDraw.Draw(clean).rectangle((label_xy[0]-2, label_xy[1]-2, 1720, label_xy[1]+45), fill=(0, 0, 0, 0))
    # 1400px is sufficient at the profile width and keeps embedded payloads modest.
    thumb = clean.resize((1400, round(clean.height*1400/W)), Image.Resampling.LANCZOS)
    chunks = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1800" height="{base.height}" viewBox="0 0 1800 {base.height}" role="img">',
              f'<title>{escape(name)} — selected project views</title>',
              '<desc>Animated presentation of existing stills. Reduced motion shows a static composition.</desc>',
              '<style>@media(prefers-reduced-motion:reduce){.slide{animation:none!important;opacity:0!important}.slide.first{opacity:1!important}.signal{display:none}}',
              '@keyframes signal{0%,10%{transform:translateX(0);opacity:0}15%{opacity:1}85%{opacity:1}95%,100%{transform:translateX(1640px);opacity:0}}</style>',
              f'<image width="1800" height="{base.height}" xlink:href="{data(thumb)}"/>']
    if sources:
        x,y,w,h = box; n=len(sources)
        chunks.append(f'<defs><clipPath id="shot"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14"/></clipPath></defs>')
        # Slide duration and crossfade are shared across project panels.
        for i,source in enumerate(sources):
            start = i*100/n; fade=FADE_SECONDS/(SLIDE_SECONDS*n)*100; end=(i+1)*100/n
            if i==0:
                keys=f'0%,{end-fade}%{{opacity:1}}{end}%,{100-fade}%{{opacity:0}}100%{{opacity:1}}'
            else:
                keys=f'0%,{start-fade}%{{opacity:0}}{start}%,{end-fade}%{{opacity:1}}{end}%,100%{{opacity:0}}'
            chunks.append(f'<style>@keyframes shot{i}{{{keys}}}</style>')
            im = Image.open(source).convert('RGB'); im.thumbnail((1400, 1000), Image.Resampling.LANCZOS)
            chunks.append(f'<g class="slide {"first" if i==0 else ""}" style="opacity:{1 if i==0 else 0};animation:shot{i} {SLIDE_SECONDS*n}s linear infinite">')
            chunks.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid slice" clip-path="url(#shot)" xlink:href="{data(im,"JPEG")}"/>')
            chunks.append(caption(labels[i], *label_xy)); chunks.append('</g>')
    else:
        chunks.append(f'<circle class="signal" cx="80" cy="1995" r="8" fill="{ink}" style="animation:signal 12s linear infinite"/>')
    chunks.append('</svg>')
    (OUT / f'{name}{suffix}.svg').write_text(''.join(chunks))


if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    build()
    build(light=True)
