"""Build self-contained light/dark toolbox SVGs from the vendored README icons."""
from copy import deepcopy
from pathlib import Path
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets/toolbox'
ICON_HEIGHT = 64
BADGE_SCALE = 1.6
BADGE_GAP = 8
CARD_HEIGHT = 270
ROW_GAP = 24
CANVAS_HEIGHT = 2 * 16 + 3 * CARD_HEIGHT + 2 * ROW_GAP
NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')


def element(parent, tag, **attrs):
    return ET.SubElement(parent, f'{{{NS}}}{tag}', {k.replace('_', '-'): str(v) for k, v in attrs.items()})


def text(parent, x, y, content, size, color, **attrs):
    node = element(parent, 'text', x=x, y=y, font_size=size, fill=color, **attrs)
    node.text = content


def icon(image, theme, prefix):
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


def build(theme, groups):
    dark = theme == 'dark'
    bg, edge, corner, ink, muted = ('#111820', '#303b47', '#85939f', '#e0e6ed', '#97a4b0') if dark else (
        '#f6f8fa', '#d4dce3', '#748392', '#242d37', '#596875')
    root = ET.Element(f'{{{NS}}}svg', width='1200', height=str(CANVAS_HEIGHT), viewBox=f'0 0 1200 {CANVAS_HEIGHT}', role='img')
    element(root, 'title').text = 'Tim Cai — languages, AI, web, backend, tooling and scientific computing'
    element(root, 'desc').text = 'Six centered groups. Icons and badges are embedded; no external resources are loaded.'
    body = element(root, 'g', font_family='-apple-system,BlinkMacSystemFont,Segoe UI,Arial,sans-serif')
    for index, group in enumerate(groups):
        x, y, w, h = 16 + (index % 2) * 600, 16 + (index // 2) * (CARD_HEIGHT + ROW_GAP), 568, CARD_HEIGHT
        cx = x + w / 2
        g = element(body, 'g')
        element(g, 'rect', x=x, y=y, width=w, height=h, rx=12, fill=bg)
        # Interrupted perimeter: a numbered opening at top left and a center gap below.
        element(g, 'path', d=f'M {x+66} {y} H {x+w-12} Q {x+w} {y} {x+w} {y+12} V {y+h-12} Q {x+w} {y+h} {x+w-12} {y+h} H {cx+24} M {cx-24} {y+h} H {x+12} Q {x} {y+h} {x} {y+h-12} V {y+34}',
                fill='none', stroke=edge, stroke_width=1)
        # Short drafting-style corner marks, all neutral gray.
        element(g, 'path', d=f'M {x} {y+18} V {y} H {x+18} M {x+w-18} {y} H {x+w} V {y+18} M {x+w} {y+h-18} V {y+h} H {x+w-18}',
                fill='none', stroke=corner, stroke_width=1.5, stroke_linecap='round')
        text(g, x+32, y+5, f'{index+1:02d}', 12, muted, font_family='monospace', letter_spacing=2)
        element(g, 'path', d=f'M {cx-9} {y+h} H {cx+9}', stroke=corner, stroke_width=2, stroke_linecap='round')
        text(g, cx, y+39, group['title'], 24, ink, text_anchor='middle', font_weight=600)
        text(g, cx, y+62, group['subtitle'], 14, muted, text_anchor='middle')
        node, iw, ih = icon(group['images'][0], theme, f'g{index}-main-')
        scale = ICON_HEIGHT / ih
        place(g, node, cx-iw*scale/2, y+82, iw*scale, ICON_HEIGHT)
        badges = [icon(im, theme, f'g{index}-b{j}-') for j, im in enumerate(group['images'][1:])]
        if badges:
            rows, row, used = [], [], 0
            for badge in badges:
                bw = badge[1] * BADGE_SCALE
                if row and used + BADGE_GAP + bw > w-48:
                    rows.append(row); row, used = [], 0
                row.append(badge); used += (BADGE_GAP if len(row)>1 else 0) + bw
            if row: rows.append(row)
            assert len(rows) <= 2, 'Badge rows exceed card height'
            for r, row in enumerate(rows):
                total = sum(b[1]*BADGE_SCALE for b in row) + BADGE_GAP*(len(row)-1)
                bx = cx-total/2
                for node, bw, bh in row:
                    place(g,node,bx,y+174+r*40,bw*BADGE_SCALE,bh*BADGE_SCALE)
                    bx += bw*BADGE_SCALE+BADGE_GAP
        else:
            text(g,cx,y+198,group['images'][0]['alt'].replace(', ', ' · '),18,muted,text_anchor='middle')
    output = ASSETS / f'toolbox-{theme}.svg'
    ET.ElementTree(root).write(output,encoding='utf-8',xml_declaration=False)
    print(f'{output.relative_to(ROOT)}: 1200x{CANVAS_HEIGHT}, {output.stat().st_size} bytes')


if __name__ == '__main__':
    groups = json.loads((ASSETS / 'toolbox.json').read_text())['groups']
    assert len(groups) == 6
    for theme in ('dark', 'light'):
        build(theme, groups)
