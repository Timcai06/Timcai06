"""Build the live terminal (skyline.svg) from assets/editor/activity.json.

One window, two commands: `git log` (latest commits across public repos) and
`skyline` — one building per week (height = weekly contributions, sqrt scale,
lit windows = days by contribution level), a 24-floor tower whose windows are
commit counts by weekday x hour (UTC+8), and the real moon phase in the sky.
Run scripts/fetch_activity.py first; both run daily in .github/workflows/skyline.yml.
"""
from pathlib import Path
from html import escape
from datetime import date, datetime, timedelta, timezone
import base64
import io
import json
import math

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/editor/skyline.svg'
FONT = "'SFMono-Regular',Consolas,'Liberation Mono',monospace"
LEVEL = {'NONE': '#232b42', 'FIRST_QUARTILE': '#6c5a3e', 'SECOND_QUARTILE': '#a8834f',
         'THIRD_QUARTILE': '#e0ae6e', 'FOURTH_QUARTILE': '#f5d2a4'}
LEVELS = list(LEVEL.values())
TZ = timezone(timedelta(hours=8))
SYNODIC = 29.530588853
NEW_MOON = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
PHASES = ['new moon', 'waxing crescent', 'first quarter', 'waxing gibbous',
          'full moon', 'waning gibbous', 'last quarter', 'waning crescent']


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


def spans(x, y, size, parts):
    inner = ''.join(f'<tspan fill="{c}"{extra}>{escape(t)}</tspan>' for t, c, extra in parts)
    return f'<text x="{x}" y="{y}" font-size="{size}" xml:space="preserve">{inner}</text>'


def prompt(cmd):
    return [('~/Timcai06', '#8fc4f0', ''), (' $ ', '#f2c48f', ''), (cmd, '#ced7ee', '')]


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


def moon(cx, cy, today):
    # Phase snapped to 1/16 of a cycle so the image changes every ~2 days, not daily.
    noon = datetime(today.year, today.month, today.day, 12, tzinfo=TZ)
    p = round(((noon - NEW_MOON).total_seconds() / 86400 / SYNODIC % 1) * 16) / 16 % 1
    name = PHASES[int(p * 8 + .5) % 8]
    cell, r = 3, 6
    out = [f'<circle cx="{cx}" cy="{cy}" r="{r * cell + 9}" fill="#f2c48f" opacity=".05"/>',
           f'<circle cx="{cx}" cy="{cy}" r="{r * cell + 4}" fill="#f2c48f" opacity=".06"/>']
    k = math.cos(2 * math.pi * p)
    for j in range(-r, r):
        for i in range(-r, r):
            x, y = i + .5, j + .5
            if x * x + y * y > r * r:
                continue
            edge = math.sqrt(r * r - y * y)
            lit = x >= k * edge if p <= .5 else x <= -k * edge
            out.append(rect(cx + i * cell, cy + j * cell, cell, cell, '#f2c48f' if lit else '#2a3150',
                            '' if lit else 'opacity=".55"'))
    return out, name


def build(data, today):
    cal = data['calendar']
    weeks = cal['weeks']
    days = [d for w in weeks for d in w['contributionDays']]
    totals = [sum(d['contributionCount'] for d in w['contributionDays']) for w in weeks]
    longest, current = streaks(days)
    W, H = 1200, 560
    b = ['<defs><filter id="shadow" x="-6%" y="-8%" width="112%" height="120%"><feDropShadow dx="0" dy="14" '
         'stdDeviation="16" flood-color="#02040c" flood-opacity=".6"/></filter></defs>',
         f'<image width="{W}" height="{H}" preserveAspectRatio="xMidYMax slice" xlink:href="data:image/png;base64,{background()}"/>',
         rect(0, 0, W, H, '#070b1b', 'opacity=".12"')]
    moon_cells, phase = moon(1125, 92, today)
    b += moon_cells
    b += [rect(150, 42, 900, 482, '#111728', 'rx="10" fill-opacity=".97" stroke="#576078" filter="url(#shadow)"'),
          rect(151, 80, 898, 1, '#343d54')]
    for x, c in [(174, '#f28c84'), (194, '#e9ba79'), (214, '#97bf9b')]:
        b.append(f'<circle cx="{x}" cy="61" r="5.5" fill="{c}"/>')
    b += [text(600, 66, 'zsh — ~/Timcai06', 14, '#9aa5c0', 'text-anchor="middle"'),
          text(1028, 66, 'LIVE', 11, '#edc38c', 'text-anchor="end" letter-spacing="1"')]
    # Pane 1: latest commits across public repositories.
    b.append(spans(186, 114, 16, prompt('git log --oneline -5') + [('   # all public repos', '#6c7a98', ' font-style="italic"')]))
    for k, c in enumerate(data['recent']):
        repo = c['repo'] if len(c['repo']) <= 14 else c['repo'][:13] + '…'
        msg = c['message'] if len(c['message']) <= 58 else c['message'][:57] + '…'
        b.append(spans(186, 142 + k * 24, 14, [(c['sha'], '#f2c48f', ''), ('  ' + c['date'][5:], '#6c7a98', ''),
                                                (f'  {repo:<14}', '#8fc4f0', ''), ('  ' + msg, '#c3cde4', '')]))
    # Pane 2: skyline and tower.
    b += [rect(170, 272, 860, 1, '#262e44'),
          spans(186, 302, 16, prompt(f'skyline --weeks {len(weeks)}')),
          spans(186, 328, 15, [(f'{cal["totalContributions"]:,}', '#f2c48f', ' font-weight="700"'),
                               (' contributions in the last year   ·   longest streak ', '#a5b2ce', ''),
                               (f'{longest}d', '#f2c48f', ''), ('   ·   current streak ', '#a5b2ce', ''),
                               (f'{current}d', '#f2c48f', '')])]
    X0, X1, GROUND, TOP = 186, 880, 486, 360
    pitch, bw, peak = (X1 - X0) / len(weeks), 10, max(totals) or 1

    def height(total):
        return 4 if not total else max(12, round((math.sqrt(total / peak) * (GROUND - TOP)) / 4) * 4)

    month = None
    for i, (week, total) in enumerate(zip(weeks, totals)):
        x = round(X0 + i * pitch + (pitch - bw) / 2)
        h = height(total)
        y = GROUND - h
        b += [rect(x, y, bw, h, '#1b2236'), rect(x, y, bw, 1, '#3a4562')]
        wd = week['contributionDays']
        for r in range((h - 6) // 6):
            for c in range(2):
                d = wd[(r * 2 + c) % len(wd)]
                b.append(rect(x + 1 + c * 5, y + 4 + r * 6, 3, 3, LEVEL[d['contributionLevel']]))
        first = date.fromisoformat(wd[0]['date'])
        if first.month != month:
            if month is not None:
                b.append(text(x, GROUND + 18, first.strftime('%b'), 10, '#5f6b88'))
            month = first.month
    # Beacon on the current week's roof.
    bx = round(X0 + (len(weeks) - 1) * pitch + (pitch - bw) / 2) + bw // 2
    bh = height(totals[-1])
    b += [rect(bx - 1, GROUND - bh - 6, 2, 6, '#7f89a3'),
          f'<rect x="{bx - 2}" y="{GROUND - bh - 10}" width="4" height="4" fill="#f28c84">'
          '<animate attributeName="opacity" values="1;.15;1" dur="1.6s" repeatCount="indefinite"/></rect>']
    # Tower: 24 floors (00h at street level) x 7 windows (Mon..Sun), quartiles of non-zero cells.
    punch = data['punch']
    nonzero = sorted(v for row in punch for v in row if v)
    cuts = [nonzero[int(len(nonzero) * q)] for q in (.25, .5, .75)] if nonzero else [1, 1, 1]
    TX, FLOOR = 930, 5
    top = GROUND - 24 * FLOOR - 6
    b += [rect(TX, top, 42, GROUND - top, '#1b2236'), rect(TX, top, 42, 1, '#3a4562'),
          rect(TX + 20, top - 12, 2, 12, '#7f89a3')]
    for hour in range(24):
        y = GROUND - 4 - (hour + 1) * FLOOR
        for wd in range(7):
            v = punch[wd][hour]
            level = 0 if not v else 1 + sum(v >= c for c in cuts)
            b.append(rect(TX + 3 + wd * 5.5, y + 1, 3, 3, LEVELS[level]))
    for hour in (0, 6, 12, 18):
        b.append(text(TX + 48, GROUND - 4 - hour * FLOOR - 1, f'{hour:02d}h', 9, '#5f6b88'))
    b += [text(TX + 21, GROUND + 18, 'hours', 10, '#5f6b88', 'text-anchor="middle"'),
          rect(176, GROUND, 848, 1, '#3a435a'),
          rect(151, 498, 898, 25, '#313952'), text(170, 515, '⎇ main', 12, '#f5d2a4'),
          text(1030, 515, f'buildings = weeks  ·  tower = commit hours (UTC+8)  ·  ☾ {phase}', 12, '#bcc8e2', 'text-anchor="end"')]
    title = (f'Live terminal: latest commits; contribution skyline ({cal["totalContributions"]} contributions '
             f'in the last year); commit-hour tower; {phase}')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img"><title>{escape(title)}</title><g font-family="{FONT}">' + ''.join(b) + '</g></svg>')


data = json.loads((ROOT / 'assets/editor/activity.json').read_text())
OUT.write_text(build(data, datetime.now(TZ).date()))
print('Built live terminal')
