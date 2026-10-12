"""Build the contribution skyline SVG from the GitHub contribution calendar.

One building per week (height = weekly total, sqrt scale); each building's lit
windows are that week's days, coloured by GitHub's contribution level. Runs
daily in .github/workflows/skyline.yml; locally: GH_TOKEN=$(gh auth token) python scripts/build_skyline.py
"""
from pathlib import Path
from html import escape
from datetime import date
import base64
import io
import json
import math
import os
import time
import urllib.error
import urllib.request

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/editor/skyline.svg'
LOGIN = 'Timcai06'
FONT = "'SFMono-Regular',Consolas,'Liberation Mono',monospace"
QUERY = '''query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
  totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}'''
LEVEL = {'NONE': '#232b42', 'FIRST_QUARTILE': '#6c5a3e', 'SECOND_QUARTILE': '#a8834f',
         'THIRD_QUARTILE': '#e0ae6e', 'FOURTH_QUARTILE': '#f5d2a4'}


def fetch():
    token = os.environ['GH_TOKEN']
    body = json.dumps({'query': QUERY, 'variables': {'login': LOGIN}}).encode()
    req = urllib.request.Request('https://api.github.com/graphql', body,
                                 {'Authorization': f'bearer {token}', 'Content-Type': 'application/json'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.load(resp)
            break
        except urllib.error.URLError:
            if attempt == 2:
                raise
            time.sleep(3)
    if 'errors' in data:
        raise SystemExit(data['errors'])
    return data['data']['user']['contributionsCollection']['contributionCalendar']


def background():
    # Same pixel plate and 8-colour quantization as workspace.svg / footer.svg.
    image = Image.open(ROOT / 'assets/pixel-lab/v2/background.png').convert('RGB')
    image = image.quantize(colors=8, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
    buffer = io.BytesIO()
    image.save(buffer, 'PNG', optimize=True)
    return base64.b64encode(buffer.getvalue()).decode()


def text(x, y, s, size=14, color='#ccd4ea', extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {extra}>{escape(s)}</text>'


def rect(x, y, w, h, c, extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}" {extra}/>'


def streaks(days):
    longest = run = 0
    for d in days:
        run = run + 1 if d['contributionCount'] else 0
        longest = max(longest, run)
    current = 0
    for i, d in enumerate(reversed(days)):
        if d['contributionCount']:
            current += 1
        elif i:  # today may still be empty
            break
    return longest, current


def build(cal):
    weeks = cal['weeks']
    days = [d for w in weeks for d in w['contributionDays']]
    totals = [sum(d['contributionCount'] for d in w['contributionDays']) for w in weeks]
    longest, current = streaks(days)
    W, H = 1200, 380
    X0, X1, GROUND, TOP = 186, 1014, 290, 166
    pitch = (X1 - X0) / len(weeks)
    bw = 12
    peak = max(totals) or 1
    b = ['<defs><filter id="shadow" x="-6%" y="-10%" width="112%" height="130%"><feDropShadow dx="0" dy="14" '
         'stdDeviation="16" flood-color="#02040c" flood-opacity=".6"/></filter></defs>',
         f'<image width="{W}" height="{H}" preserveAspectRatio="xMidYMax slice" xlink:href="data:image/png;base64,{background()}"/>',
         rect(0, 0, W, H, '#070b1b', 'opacity=".12"'),
         rect(150, 42, 900, 302, '#111728', 'rx="10" fill-opacity=".97" stroke="#576078" filter="url(#shadow)"'),
         rect(151, 80, 898, 1, '#343d54')]
    for x, c in [(174, '#f28c84'), (194, '#e9ba79'), (214, '#97bf9b')]:
        b.append(f'<circle cx="{x}" cy="61" r="5.5" fill="{c}"/>')
    b += [text(600, 66, 'skyline — ~/Timcai06', 14, '#9aa5c0', 'text-anchor="middle"'),
          text(1028, 66, 'CONTRIBUTIONS', 11, '#edc38c', 'text-anchor="end" letter-spacing="1"'),
          f'<text x="186" y="116" font-size="16" xml:space="preserve"><tspan fill="#8fc4f0">~/Timcai06</tspan>'
          f'<tspan fill="#f2c48f"> $ </tspan><tspan fill="#ced7ee">skyline --weeks {len(weeks)}</tspan></text>',
          f'<text x="186" y="142" font-size="15" xml:space="preserve"><tspan fill="#f2c48f" font-weight="700">'
          f'{cal["totalContributions"]:,}</tspan><tspan fill="#a5b2ce"> contributions in the last year   ·   longest streak </tspan>'
          f'<tspan fill="#f2c48f">{longest}d</tspan><tspan fill="#a5b2ce">   ·   current streak </tspan>'
          f'<tspan fill="#f2c48f">{current}d</tspan></text>']
    # Buildings: height snaps to a 4px grid for the pixel look.
    month = None
    for i, (week, total) in enumerate(zip(weeks, totals)):
        x = round(X0 + i * pitch + (pitch - bw) / 2)
        h = 4 if not total else max(12, round((math.sqrt(total / peak) * (GROUND - TOP)) / 4) * 4)
        y = GROUND - h
        b += [rect(x, y, bw, h, '#1b2236'), rect(x, y, bw, 1, '#3a4562')]
        wd = week['contributionDays']
        rows = (h - 6) // 6
        for r in range(rows):
            for c in range(2):
                d = wd[(r * 2 + c) % len(wd)]
                b.append(rect(x + 2 + c * 5, y + 4 + r * 6, 3, 3, LEVEL[d['contributionLevel']]))
        first = date.fromisoformat(wd[0]['date'])
        if first.month != month:
            if month is not None:
                b.append(text(x, GROUND + 18, first.strftime('%b'), 10, '#5f6b88'))
            month = first.month
    # A blinking beacon on the current week's roof.
    last_x = round(X0 + (len(weeks) - 1) * pitch + (pitch - bw) / 2) + bw // 2
    last_h = 4 if not totals[-1] else max(12, round((math.sqrt(totals[-1] / peak) * (GROUND - TOP)) / 4) * 4)
    b += [rect(last_x - 1, GROUND - last_h - 6, 2, 6, '#7f89a3'),
          f'<rect x="{last_x - 2}" y="{GROUND - last_h - 10}" width="4" height="4" fill="#f28c84">'
          '<animate attributeName="opacity" values="1;.15;1" dur="1.6s" repeatCount="indefinite"/></rect>',
          rect(176, GROUND, 848, 1, '#3a435a'),
          rect(151, 318, 898, 25, '#313952'), text(170, 335, '⎇ main', 12, '#f5d2a4'),
          text(1030, 335, 'one building per week  ·  lit windows = days', 12, '#bcc8e2', 'text-anchor="end"')]
    title = f'Contribution skyline: {cal["totalContributions"]} contributions in the last year'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img"><title>{escape(title)}</title><g font-family="{FONT}">' + ''.join(b) + '</g></svg>')


OUT.write_text(build(fetch()))
print('Built contribution skyline')
