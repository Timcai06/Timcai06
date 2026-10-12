"""Build the live terminal (skyline.svg) from assets/editor/activity.json.

One window, three commands: `git log` (latest commits across public repos),
`skyline` — one building per week (height = weekly contributions, sqrt scale,
lit windows = days by contribution level), a 24-floor tower whose windows are
commit counts by weekday x hour (UTC+8), and the real moon phase in the sky —
then `echo "Thanks for stopping by."`, the page's closing bookend. Motion (motion.py)
is decorative only — stars, a meteor, the moon's halo, a car on the street, the
beacon and the retyped echo; buildings and windows are data and never animate.
Run scripts/fetch_activity.py first; both run daily in .github/workflows/skyline.yml.
"""
from pathlib import Path
from html import escape
from datetime import date, datetime, timedelta, timezone
import base64
import io
import json
import math
import os

from PIL import Image

from motion import Motion
from pixel_moon import GLOW_CSS, moon
from pixel_font import columns, render

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/editor/skyline.svg'
FONT = "'SFMono-Regular',Consolas,'Liberation Mono',monospace"
LEVEL = {'NONE': '#232b42', 'FIRST_QUARTILE': '#6c5a3e', 'SECOND_QUARTILE': '#a8834f',
         'THIRD_QUARTILE': '#e0ae6e', 'FOURTH_QUARTILE': '#f5d2a4'}
LEVELS = list(LEVEL.values())
TZ = timezone(timedelta(hours=8))


def background():
    # Same pixel plate and 8-colour quantization as workspace.svg.
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


# Thin moonlit cloud that drifts across the moon now and then (starts off-canvas,
# so a still frame shows none).
def cloud(cx, cy):
    cloud = [(0, 0, 34), (6, -2, 18), (-8, 2, 14), (40, 2, 22), (46, 0, 10)]
    return ('<g class="cloud">' + ''.join(rect(cx + 90 + x, cy + 8 + y, w, 2, '#3a4466') + rect(cx + 90 + x, cy + 10 + y, w, 3, '#232a44')
                                         for x, y, w in cloud) + '</g>')


def build(data, today, generated):
    cal = data['calendar']
    weeks = cal['weeks']
    days = [d for w in weeks for d in w['contributionDays']]
    totals = [sum(d['contributionCount'] for d in w['contributionDays']) for w in weeks]
    longest, current = streaks(days)
    W, H = 1200, 690
    b = ['<defs><filter id="shadow" x="-6%" y="-8%" width="112%" height="120%"><feDropShadow dx="0" dy="14" '
         'stdDeviation="16" flood-color="#02040c" flood-opacity=".6"/></filter></defs>',
         f'<image width="{W}" height="{H}" preserveAspectRatio="xMidYMax slice" xlink:href="data:image/png;base64,{background()}"/>',
         rect(0, 0, W, H, '#070b1b', 'opacity=".12"')]
    moon_cells, phase, lit = moon(1125, 92, today)
    b += moon_cells + [cloud(1125, 92)]
    M = Motion()
    M.raw('@keyframes beacon{0%,100%{opacity:1}50%{opacity:.15}}')
    M.raw(GLOW_CSS)
    M.raw('@keyframes cloud{0%{transform:translateX(0)}100%{transform:translateX(-230px)}}'
          '.cloud{animation:cloud 46s linear 4s infinite}')
    # Night sky around the window (the moon sits at 1125, 92).
    b += M.stars([(30, 18, '#f2c48f', 0), (96, 46, '#8fa0d8', 1.2), (58, 120, '#f2c48f', 2.4), (118, 190, '#8fa0d8', .7),
                  (24, 250, '#8fa0d8', 1.9), (262, 14, '#8fa0d8', 2.8), (470, 26, '#f2c48f', .4), (690, 12, '#8fa0d8', 1.6),
                  (905, 30, '#f2c48f', 2.2), (1072, 20, '#8fa0d8', 1.0), (1176, 40, '#f2c48f', 2.6), (1168, 170, '#8fa0d8', .2),
                  (1086, 236, '#f2c48f', 1.4), (1150, 300, '#8fa0d8', 2.9)])
    b.append(M.meteor('meteor', 20, 60, 110, 70, 13, 5))
    # An airliner crosses the top strip of sky with its nav light and strobe.
    M.raw('@keyframes plane{0%{transform:translateX(0)}100%{transform:translateX(1260px)}}'
          '.plane{animation:plane 70s linear -20s infinite}'
          '@keyframes strobe{0%,92%,100%{opacity:0}94%,96%{opacity:1}}')
    b.append(f'<g class="plane">{rect(-40, 24, 7, 2, "#56627f")}{rect(-37, 22, 2, 6, "#4a5572")}'
             f'{rect(-41, 23, 2, 2, "#f28c84", "class=\"blink\"")}'
             f'<rect x="-33" y="23" width="2" height="2" fill="#ffffff" style="animation:strobe 1.4s linear infinite"/></g>')
    # Moonlight glints on the water strip below the moon; brighter when more of it is lit.
    glints = [(1104, 662, 10), (1122, 660, 16), (1140, 664, 8), (1096, 670, 6), (1114, 668, 14), (1134, 672, 10),
              (1108, 678, 12), (1128, 680, 8), (1146, 676, 6), (1118, 686, 10)]
    b.append(f'<g opacity="{.25 + .55 * lit:.2f}">' + ''.join(
        rect(x, y, w, 1, '#f6d9a6', f'style="animation:tw {2.2 + k % 3 * .6:.1f}s ease-in-out {k * .37:.2f}s infinite"')
        for k, (x, y, w) in enumerate(glints)) + '</g>')
    b += [rect(150, 42, 900, 612, '#111728', 'rx="10" fill-opacity=".97" stroke="#576078" filter="url(#shadow)"'),
          rect(151, 80, 898, 1, '#343d54')]
    for x, c in [(174, '#f28c84'), (194, '#e9ba79'), (214, '#97bf9b')]:
        b.append(f'<circle cx="{x}" cy="61" r="5.5" fill="{c}"/>')
    b += [text(600, 66, 'zsh — ~/Timcai06', 14, '#9aa5c0', 'text-anchor="middle"'),
          text(1028, 66, f'LIVE · updated {generated}', 11, '#edc38c', 'text-anchor="end" letter-spacing=".5"')]
    # Pulsing red dot before the label: this terminal is regenerated from live data.
    live_x = round(1028 - len(f'LIVE · updated {generated}') * 11 * 0.62 - 12)
    M.raw('@keyframes ping{0%{transform:scale(1);opacity:.7}80%,100%{transform:scale(2.6);opacity:0}}'
          '.ping{transform-box:fill-box;transform-origin:center;animation:ping 1.8s ease-out infinite}')
    b += [f'<circle cx="{live_x}" cy="62" r="4" fill="#f85149" class="ping"/>', f'<circle cx="{live_x}" cy="62" r="4" fill="#f85149"/>']
    # ---- One 28 s session, like the workspace: `git log --graph` types and its rows
    # cascade in; `skyline` types, then every building rises to its true height and
    # the tower lights floor by floor; `echo` types and "Thanks for stopping by."
    # assembles in the hero's pixel font. Data only ever animates *to* its true value;
    # reduced motion (and a still frame) shows the finished terminal.
    S, DT = 28, 0.04
    RESET = S - 0.2  # typed characters clear after the session fade below
    fade = M.session_fade('sess', S)
    _n = [0]

    def app(at, parts, dx=0, dy=0, dur=.45):
        _n[0] += 1
        return f'<g class="{M.appear(f"a{_n[0]}", at, S, dx, dy, dur)}">' + ''.join(parts) + '</g>'

    def typed_line(x, y, size, prefix, cmd, at, extra=()):
        spans_ = ''.join(f'<tspan fill="{c}"{e}>{escape(t)}</tspan>' for t, c, e in prefix)
        return (f'<text x="{x}" y="{y}" font-size="{size}" xml:space="preserve">{spans_}'
                + M.typed(f't{_n[0]}_{at:g}'.replace('.', 'p') + '_', cmd, '#ced7ee', at, DT, RESET, S) + ''.join(extra) + '</text>')

    PROMPT = [('~/Timcai06', '#8fc4f0', ''), (' $ ', '#f2c48f', '')]
    cursor_x = round(186 + len('~/Timcai06 $ ') * 16 * 0.6) + 2
    session = []
    # Pane 1: latest commits across public repositories, drawn like `git log --graph`.
    T_LOG = 0.6
    log_cmd = 'git log --oneline --graph -5'
    log_done = T_LOG + len(log_cmd) * DT
    note = (f'<tspan fill="#6c7a98" font-style="italic" class="{M.window("lognote", log_done + .1, RESET, S, "fill-opacity")}">'
            f'{escape("   # all public repos")}</tspan>')
    session.append(typed_line(186, 114, 16, PROMPT, log_cmd, T_LOG, [note]))
    session.append(f'<g class="{M.window("logcur", S - 0.1, T_LOG, S)}" opacity="0">'
                   + rect(cursor_x, 101, 9, 16, '#edc38c', 'opacity=".85" class="blink"') + '</g>')
    rows = data['recent']
    rail_top, rail_bottom = 142 - 9, 142 + (len(rows) - 1) * 24 - 4
    session.append(app(log_done + .15, [rect(192, rail_top, 1, rail_bottom - rail_top, '#3a4562')]))
    for k, c in enumerate(rows):
        repo = c['repo'] if len(c['repo']) <= 14 else c['repo'][:13] + '…'
        msg = c['message'] if len(c['message']) <= 56 else c['message'][:55] + '…'
        node = '#f2c48f' if k == 0 else '#8fc4f0'
        session.append(app(log_done + .2 + k * .12, [
            rect(190, 142 + k * 24 - 9, 5, 5, node), *( [rect(188, 142 - 11, 9, 9, 'none', f'stroke="{node}" stroke-opacity=".5"')] if k == 0 else []),
            spans(208, 142 + k * 24, 14, [(c['sha'], '#f2c48f', ''), ('  ' + c['date'][5:], '#6c7a98', ''),
                                          (f'  {repo:<14}', '#8fc4f0', ''), ('  ' + msg, '#c3cde4', '')])], dx=-6))
    # Pane 2: skyline and tower.
    T_SKY = 2.9
    sky_cmd = f'skyline --weeks {len(weeks)}'
    sky_done = T_SKY + len(sky_cmd) * DT
    RISE = sky_done + .4
    session += [rect(170, 272, 860, 1, '#262e44'),
                typed_line(186, 302, 16, PROMPT, sky_cmd, T_SKY),
                app(sky_done + .2, [spans(186, 328, 15, [(f'{cal["totalContributions"]:,}', '#f2c48f', ' font-weight="700"'),
                               (' contributions in the last year   ·   longest streak ', '#a5b2ce', ''),
                               (f'{longest}d', '#f2c48f', ''), ('   ·   current streak ', '#a5b2ce', ''),
                               (f'{current}d', '#f2c48f', '')])], dy=4)]
    X0, X1, GROUND, TOP = 186, 880, 486, 360
    pitch, bw, peak = (X1 - X0) / len(weeks), 10, max(totals) or 1
    # Night sky behind the city: deep blue overhead, a warm glow on the horizon (decor only).
    b.append('<defs><linearGradient id="citysky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#111728" stop-opacity="0"/>'
             '<stop offset=".7" stop-color="#2a2547" stop-opacity=".55"/><stop offset="1" stop-color="#f2c48f" stop-opacity=".14"/>'
             '</linearGradient></defs>')
    session.append(rect(176, TOP - 24, 848, GROUND - TOP + 24, 'url(#citysky)'))

    def height(total):
        return 4 if not total else max(12, round((math.sqrt(total / peak) * (GROUND - TOP)) / 4) * 4)

    month = None
    labels = []
    for i, (week, total) in enumerate(zip(weeks, totals)):
        x = round(X0 + i * pitch + (pitch - bw) / 2)
        h = height(total)
        y = GROUND - h
        cells = [rect(x, y, bw, h, '#1b2236'), rect(x, y, bw, 1, '#3a4562')]
        wd = week['contributionDays']
        for r in range((h - 6) // 6):
            for c in range(2):
                d = wd[(r * 2 + c) % len(wd)]
                cells.append(rect(x + 1 + c * 5, y + 4 + r * 6, 3, 3, LEVEL[d['contributionLevel']]))
        session.append(f'<g class="{M.grow(f"g{i}", RISE + i * .028, S)}">' + ''.join(cells) + '</g>')
        first = date.fromisoformat(wd[0]['date'])
        if first.month != month:
            if month is not None:
                labels.append(text(x, GROUND + 18, first.strftime('%b'), 10, '#5f6b88'))
            month = first.month
    session.append(app(RISE, labels))
    # Beacon on the current week's roof.
    bx = round(X0 + (len(weeks) - 1) * pitch + (pitch - bw) / 2) + bw // 2
    bh = height(totals[-1])
    session.append(app(RISE + len(weeks) * .028 + .4, [rect(bx - 1, GROUND - bh - 6, 2, 6, '#7f89a3'),
          f'<rect x="{bx - 2}" y="{GROUND - bh - 10}" width="4" height="4" fill="#f28c84" style="animation:beacon 1.6s ease-in-out infinite"/>']))
    # Tower: 24 floors (00h at street level) x 7 windows (Mon..Sun), quartiles of non-zero cells.
    punch = data['punch']
    nonzero = sorted(v for row in punch for v in row if v)
    cuts = [nonzero[int(len(nonzero) * q)] for q in (.25, .5, .75)] if nonzero else [1, 1, 1]
    TX, FLOOR = 930, 5
    top = GROUND - 24 * FLOOR - 6
    session.append(f'<g class="{M.grow("tower", RISE + .2, S, .6)}">' + rect(TX, top, 42, GROUND - top, '#1b2236')
                   + rect(TX, top, 42, 1, '#3a4562') + rect(TX + 20, top - 12, 2, 12, '#7f89a3') + '</g>')
    for hour in range(24):
        y = GROUND - 4 - (hour + 1) * FLOOR
        floor = []
        for wd in range(7):
            v = punch[wd][hour]
            level = 0 if not v else 1 + sum(v >= c for c in cuts)
            floor.append(rect(TX + 3 + wd * 5.5, y + 1, 3, 3, LEVELS[level]))
        session.append(app(RISE + .8 + hour * .045, floor, dur=.2))
    session.append(app(RISE + .8, [text(TX + 48, GROUND - 4 - hour * FLOOR - 1, f'{hour:02d}h', 9, '#5f6b88') for hour in (0, 6, 12, 18)]
                       + [text(TX + 21, GROUND + 18, 'hours', 10, '#5f6b88', 'text-anchor="middle"')]))
    session.append(rect(176, GROUND, 848, 1, '#3a435a'))
    # Pane 3: the closing command; its output is drawn in the hero's pixel font.
    T_ECHO = 6.6
    quote = '"Thanks for stopping by."'
    echo_done = T_ECHO + (5 + len(quote)) * DT
    echo = (f'<text x="186" y="552" font-size="16" xml:space="preserve"><tspan fill="#8fc4f0">~/Timcai06</tspan><tspan fill="#f2c48f"> $ </tspan>'
            + M.typed('e', 'echo ', '#ced7ee', T_ECHO, DT, RESET, S) + M.typed('q', quote, '#b0d6bf', T_ECHO + 5 * DT, DT, RESET, S) + '</text>')
    session += [rect(170, 522, 860, 1, '#262e44'), echo,
                f'<g class="{M.window("ecur", S - 0.1, T_ECHO, S)}" opacity="0">' + rect(cursor_x, 539, 9, 16, '#edc38c', 'opacity=".85" class="blink"') + '</g>']
    THANKS = 'Thanks for stopping by.'
    PX0, PY0, PP, PS = 186, 565, 5, 4
    lit_cols, mask = render(THANKS, PX0, PY0, PP, PS, '#ffe6bf', '#e3a463', '#2b2236')
    width = (columns(THANKS).__len__()) * PP
    assert PX0 + width < 1030, width
    T_PIX = echo_done + .3
    for k, cells in lit_cols:
        session.append(app(T_PIX + k * .014, [cells], dy=-6, dur=.35))
    M.raw(f'@keyframes thx{{0%,{(T_PIX + 2) / S * 100:.2f}%{{transform:translateX(0)}}{(T_PIX + 3) / S * 100:.2f}%,'
          f'{(T_PIX + 9) / S * 100:.2f}%{{transform:translateX({width + 200}px)}}{(T_PIX + 9.01) / S * 100:.2f}%{{transform:translateX(0)}}'
          f'{(T_PIX + 10) / S * 100:.2f}%,100%{{transform:translateX({width + 200}px)}}}}.thx{{animation:thx {S}s ease-in-out infinite}}')
    session.append(f'<defs><mask id="thxmask">{"".join(mask)}</mask><linearGradient id="thxsh" x1="0" x2="1">'
                   '<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".85"/>'
                   '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient></defs>'
                   f'<g mask="url(#thxmask)"><rect class="thx" x="{PX0 - 120}" y="{PY0 - 4}" width="60" height="44" fill="url(#thxsh)" transform="skewX(-18)"/></g>')
    T_IDLE = T_PIX + len(columns(THANKS)) * .014 + .5
    session.append(f'<g class="{M.window("eidle", T_IDLE, RESET, S)}">' + spans(186, 624, 16, prompt(''))
                   + rect(cursor_x, 611, 9, 16, '#edc38c', 'opacity=".85" class="blink"') + '</g>')
    b.append(f'<g class="{fade}">' + ''.join(session) + '</g>')
    # A car drives down the street now and then (decoration, in front of the data).
    M.raw('@keyframes car{0%{transform:translateX(0);opacity:1}55%{transform:translateX(830px);opacity:1}'
          '55.01%,100%{transform:translateX(830px);opacity:0}}.car{animation:car 18s linear 2s infinite}')
    b.append(f'<g class="car" opacity="0">{rect(180, GROUND - 6, 12, 5, "#2c3550")}{rect(183, GROUND - 8, 6, 2, "#2c3550")}'
             f'{rect(192, GROUND - 5, 2, 2, "#f5d2a4")}{rect(194, GROUND - 5, 10, 1, "#f5d2a4", "opacity=\".35\"")}'
             f'{rect(180, GROUND - 5, 1, 2, "#f28c84")}</g>')
    b += [
          rect(151, 628, 898, 25, '#313952'), text(170, 645, '⎇ main', 12, '#f5d2a4'),
          text(1030, 645, f'buildings = weeks  ·  tower = commit hours (UTC+8)  ·  ☾ {phase}', 12, '#bcc8e2', 'text-anchor="end"')]
    title = (f'Live terminal: latest commits; contribution skyline ({cal["totalContributions"]} contributions '
             f'in the last year); commit-hour tower; {phase}; echo "Thanks for stopping by."')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img"><title>{escape(title)}</title>{M.style()}<g font-family="{FONT}">' + ''.join(b) + '</g></svg>')


data = json.loads((ROOT / 'assets/editor/activity.json').read_text())
now = datetime.now(TZ)
generated = now.strftime('%Y-%m-%d %H:%M') + ' (UTC+8)'
# SKYLINE_DATE=YYYY-MM-DD previews another day (e.g. a full moon) without touching the data or README.
preview = os.environ.get('SKYLINE_DATE')
day = date.fromisoformat(preview) if preview else now.date()
OUT.write_text(build(data, day, generated))
if not preview:
    # The README caption under the terminal shows the same timestamp as its title bar.
    readme = ROOT / 'README.md'
    text_ = readme.read_text()
    a, z = text_.index('<!-- live:updated -->'), text_.index('<!-- /live:updated -->')
    readme.write_text(text_[:a] + f'<!-- live:updated --><b>{generated}</b>' + text_[z:])
print('Built live terminal')
