"""Build self-contained light/dark toolbox SVGs from the vendored README icons."""
from copy import deepcopy
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET
from visual_style import palette

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets/toolbox'
ICON_HEIGHT = 64
BADGE_SCALE = 1.6
BADGE_GAP = 8
CARD_HEIGHT = 310
ROW_GAP = 24
HEADER_HEIGHT = 390
CANVAS_HEIGHT = HEADER_HEIGHT + 2 * 16 + 3 * CARD_HEIGHT + 2 * ROW_GAP
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')


def element(parent, tag, **attrs):
    return ET.SubElement(parent, f'{{{NS}}}{tag}', {k.replace('_', '-'): str(v) for k, v in attrs.items()})


def text(parent, x, y, content, size, color, **attrs):
    node = element(parent, 'text', x=x, y=y, font_size=size, fill=color, **attrs)
    node.text = content


def icon(image, theme, prefix):
    if 'text' in image:
        width, height = len(image['text']) * 7.5 + 24, 20
        node = ET.Element(f'{{{NS}}}svg', width=str(width), height=str(height), viewBox=f'0 0 {width} {height}')
        dark = theme == 'dark'
        element(node, 'rect', width=width, height=height, rx=3, fill='#28323e' if dark else '#e4e9ee')
        text(node, width/2, 14, image['text'], 11, '#dce5ed' if dark else '#303b47', text_anchor='middle', font_family='Arial,sans-serif')
        return node, width, height
    path = ASSETS / 'source' / image['file']
    if 'skillicons.dev' in image['url'] and theme == 'light':
        path = path.with_name(path.stem + '-light.svg')
    node = ET.parse(path).getroot()
    width, height = float(node.attrib['width']), float(node.attrib['height'])
    ids = {n.attrib['id']: prefix + n.attrib['id'] for n in node.iter() if 'id' in n.attrib}
    for n in node.iter():
        assert n.tag.split('}')[-1] not in ('script', 'foreignObject', 'style')
        for key, value in list(n.attrib.items()):
            assert not key.lower().startswith('on')
            if key.split('}')[-1] == 'href':
                assert value.startswith(('data:', '#')), 'External SVG reference'
            if key == 'id':
                value = ids[value]
            else:
                value = re.sub(r'url\(#([^)]*)\)', lambda m: f'url(#{ids[m[1]]})', value)
                if value.startswith('#') and value[1:] in ids:
                    value = '#' + ids[value[1:]]
            n.set(key, value)
    node.set('viewBox', node.get('viewBox', f'0 0 {width} {height}'))
    element(node, 'title').text = image['alt']
    return node, width, height


def place(parent, node, x, y, width, height):
    placed = deepcopy(node)
    placed.attrib.update(x=str(x), y=str(y), width=str(width), height=str(height))
    parent.append(placed)


def build(theme, groups, agent):
    dark = theme == 'dark'
    colors = palette(not dark)
    ink, muted, edge = (colors[k] for k in ('ink', 'muted', 'rail'))
    bg = '#111820' if dark else '#f6f8fa'
    root = ET.Element(f'{{{NS}}}svg', width='1200', height=str(CANVAS_HEIGHT), viewBox=f'0 0 1200 {CANVAS_HEIGHT}', role='img')
    element(root, 'title').text = 'Tim Cai — languages, AI, web, backend, tooling and scientific computing'
    element(root, 'desc').text = 'Agent engineering plus six technology groups with project context. All assets are embedded.'
    body = element(root, 'g', font_family='-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif')
    # Same title, margin ratio and metadata rail as the project panels.
    text(body, 53, 39, 'TIM CAI / TOOLBOX', 16, muted, font_family='monospace')
    text(body, 1147, 39, 'ENGINEERING + DESIGN', 16, muted, text_anchor='end', font_family='monospace')
    element(body, 'line', x1=53, y1=57, x2=1147, y2=57, stroke=edge)
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    f = TTFont(ROOT / 'assets/showcase/fonts/BigShoulders-Bold.ttf')
    gs, cmap = f.getGlyphSet(), f.getBestCmap()
    scale = 114 / f['head'].unitsPerEm
    cursor = 50
    for char in 'TOOLBOX':
        glyph = gs[cmap[ord(char)]]; pen = SVGPathPen(gs); glyph.draw(pen)
        element(body, 'path', d=pen.getCommands(), fill=ink,
                transform=f'translate({cursor},170) scale({scale},-{scale})')
        cursor += glyph.width*scale
    f.close()
    text(body, 720, 116, 'From agents to interfaces.', 25, ink, font_family='Georgia,serif', font_style='italic')
    text(body, 720, 153, 'Tools behind the selected work', 16, muted)
    text(body, 53, 238, agent['title'], 24, ink, font_weight=600)
    text(body, 1147, 238, agent['projects'], 16, muted, text_anchor='end', font_family='monospace')
    for i, label in enumerate(agent['tools']):
        x = 53 + i * 222
        element(body, 'path', d=f'M {x+6} 268 H {x+200} Q {x+206} 268 {x+206} 274 V 304 L {x+194} 316 H {x+6} Q {x} 316 {x} 310 V 274 Q {x} 268 {x+6} 268 Z', fill=bg, stroke=edge)
        text(body, x+103, 298, label, 18, ink, text_anchor='middle')
    element(body, 'line', x1=53, y1=358, x2=1147, y2=358, stroke=edge)
    for index, group in enumerate(groups):
        x, y, w, h = 53 + (index % 2) * 568, HEADER_HEIGHT + (index // 2) * (CARD_HEIGHT + ROW_GAP), 526, CARD_HEIGHT
        cx = x + w / 2
        g = element(body, 'g')
        # Open sections replace dashboard boxes; the tools keep their own colors.
        text(g, x, y+31, group['title'], 24, ink, font_weight=600)
        text(g, x, y+56, group['subtitle'], 14, muted)
        node, iw, ih = icon(group['images'][0], theme, f'g{index}-main-')
        scale = ICON_HEIGHT / ih
        place(g, node, x, y+82, iw*scale, ICON_HEIGHT)
        badges = [icon(im, theme, f'g{index}-b{j}-') for j, im in enumerate(group['images'][1:])]
        if badges:
            rows, row, used = [], [], 0
            for badge in badges:
                bw = badge[1] * BADGE_SCALE
                if row and used + BADGE_GAP + bw > w:
                    rows.append(row); row, used = [], 0
                row.append(badge); used += (BADGE_GAP if len(row)>1 else 0) + bw
            if row: rows.append(row)
            assert len(rows) <= 2, 'Badge rows exceed card height'
            for r, row in enumerate(rows):
                total = sum(b[1]*BADGE_SCALE for b in row) + BADGE_GAP*(len(row)-1)
                bx = x
                for node, bw, bh in row:
                    place(g,node,bx,y+174+r*40,bw*BADGE_SCALE,bh*BADGE_SCALE)
                    bx += bw*BADGE_SCALE+BADGE_GAP
        else:
            text(g,x,y+198,group['images'][0]['alt'].replace(', ', ' · '),18,muted)
        element(g, 'path', d=f'M {x} {y+264} H {x+w-16} L {x+w} {y+248} V {y+228}', fill='none', stroke=edge, stroke_width=1)
        text(g, x, y+288, group['caption'], 14, muted)
    output = ASSETS / f'toolbox-{theme}.svg'
    ET.ElementTree(root).write(output,encoding='utf-8',xml_declaration=False)
    print(f'{output.relative_to(ROOT)}: 1200x{CANVAS_HEIGHT}, {output.stat().st_size} bytes')


if __name__ == '__main__':
    config = json.loads((ASSETS / 'toolbox.json').read_text())
    groups = config['groups']
    assert len(groups) == 6
    for theme in ('dark', 'light'):
        build(theme, groups, config['agent'])
    # Plain-text stack under the image: SVG text is invisible to Ctrl+F and search,
    # so the same groups are also written into README.md between the markers.
    line = ' &nbsp;|&nbsp; '.join(f"<b>{g['title']}</b> " + ' · '.join(i['alt'].replace(', ', ' · ') for i in g['images'])
                                 for g in groups)
    line = '<b>Agent 工程</b> ' + ' · '.join(config['agent']['tools']) + ' &nbsp;|&nbsp; ' + line
    block = f'<!-- toolbox:text -->\n<p align="center"><sub>{line}</sub></p>\n<!-- /toolbox:text -->'
    readme = ROOT / 'README.md'
    text_ = readme.read_text()
    start, end = text_.index('<!-- toolbox:text -->'), text_.index('<!-- /toolbox:text -->') + len('<!-- /toolbox:text -->')
    readme.write_text(text_[:start] + block + text_[end:])
    print('README.md: toolbox text updated')
