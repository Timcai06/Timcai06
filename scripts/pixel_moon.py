"""Pixel moon lit by the real phase, shared by skyline.svg and workspace.svg.

Lambert shading from the sun direction of the day's phase (snapped to 1/16 of a
cycle, so images change every ~2 days), Bayer-dithered into a warm 7-step ramp,
near-side maria for albedo, earthshine on the night side and a radial glow whose
strength follows the lit fraction. The glow breathes via the `moonglow` keyframes.
"""
from datetime import datetime, timedelta, timezone
import math

TZ = timezone(timedelta(hours=8))
SYNODIC = 29.530588853
NEW_MOON = datetime(2000, 1, 6, 18, 14, tzinfo=timezone.utc)
PHASES = ['new moon', 'waxing crescent', 'first quarter', 'waxing gibbous',
          'full moon', 'waning gibbous', 'last quarter', 'waning crescent']
GLOW_CSS = ('@keyframes moonglow{0%,100%{transform:scale(1);opacity:.75}50%{transform:scale(1.08);opacity:1}}'
            '.moonglow{transform-box:fill-box;transform-origin:center;animation:moonglow 7s ease-in-out infinite}')


def rect(x, y, w, h, c, extra=''):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}" {extra}/>'


# Moon: pixel-art shading lit by the real phase. Albedo map = the major near-side maria
# (normalised disc coords, x right, y down: Imbrium, Serenitatis, Tranquillitatis,
# Crisium, Procellarum, Nubium, Fecunditatis, Nectaris).
MARIA = [(-.25, -.36, .24), (.2, -.3, .15), (.32, -.04, .18), (.62, -.24, .1),
         (-.55, .02, .3), (-.15, .38, .16), (.52, .18, .12), (.32, .3, .08)]
CRATERS = [(-.12, .72, .05), (-.3, -.04, .05), (.05, .1, .04), (-.6, -.5, .04)]
LIT = ['#4a4656', '#6e6672', '#9c8f86', '#c8b394', '#e6cda2', '#f4dfb8', '#fff1d6']
BAYER = [[0, 2], [3, 1]]


def moon(cx, cy, today, R=15, cell=2, glow_id="moonglow"):
    # Phase snapped to 1/16 of a cycle so the image changes every ~2 days, not daily.
    noon = datetime(today.year, today.month, today.day, 12, tzinfo=TZ)
    p = round(((noon - NEW_MOON).total_seconds() / 86400 / SYNODIC % 1) * 16) / 16 % 1
    name = PHASES[int(p * 8 + .5) % 8]
    lit_fraction = (1 - math.cos(2 * math.pi * p)) / 2
    # Sun direction in the moon's frame: behind it at new moon, from the right while waxing.
    lx, lz = math.sin(2 * math.pi * p), -math.cos(2 * math.pi * p)
    glow = .3 + .7 * lit_fraction
    out = [f'<defs><radialGradient id="{glow_id}"><stop offset="0" stop-color="#f6d9a6" stop-opacity=".55"/>'
           '<stop offset=".35" stop-color="#f2c48f" stop-opacity=".16"/><stop offset="1" stop-color="#f2c48f" stop-opacity="0"/>'
           '</radialGradient></defs>',
           # Glow strength follows the lit fraction; the inner circle breathes on top of it.
           f'<g opacity="{glow:.2f}"><circle cx="{cx}" cy="{cy}" r="{round(R * cell * 2.6)}" fill="url(#{glow_id})" '
           'class="moonglow"/></g>']
    for j in range(-R, R):
        for i in range(-R, R):
            nx, ny = (i + .5) / R, (j + .5) / R
            d2 = nx * nx + ny * ny
            if d2 > 1:
                continue
            nz = math.sqrt(1 - d2)
            albedo = .7 if any((nx - mx) ** 2 + (ny - my) ** 2 < mr * mr for mx, my, mr in MARIA) else 1
            if any((nx - mx) ** 2 + (ny - my) ** 2 < mr * mr for mx, my, mr in CRATERS):
                albedo *= .8
            light = max(0, nx * lx + nz * lz) * albedo * (.78 + .22 * nz)
            if light < .05:
                # Earthshine: the night side stays faintly visible, cooler at the limb.
                colour = '#2e3758' if nz > .45 else '#29304e'
                if albedo < 1:
                    colour = '#262c48'
            else:
                level = light * len(LIT) + (BAYER[j % 2][i % 2] / 4 - .375) * .9
                colour = LIT[max(0, min(len(LIT) - 1, int(level)))]
            out.append(rect(cx + i * cell, cy + j * cell, cell, cell, colour))
    return out, name, lit_fraction
