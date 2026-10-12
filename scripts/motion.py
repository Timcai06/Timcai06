"""Shared CSS motion helpers for the profile SVGs (workspace.svg, skyline.svg).

GitHub renders README SVGs as <img>, where CSS keyframes still run. Like a pixel
room with a few moving props, nearly everything stays still. Each moving element
carries its reduced-motion end state as attributes; prefers-reduced-motion turns
the keyframes off and leaves that state.
"""
from html import escape


class Motion:
    def __init__(self):
        self.frames = []

    def raw(self, css):
        self.frames.append(css)

    def window(self, name, start, end, period, prop='opacity'):
        """Visible only during [start, end) seconds of a looping period; start > end wraps around."""
        a, z = round(start / period * 100, 3), round(end / period * 100, 3)
        if a > z:
            frames = f'0%{{{prop}:1}}{z}%{{{prop}:0}}{a}%{{{prop}:1}}'
        else:
            frames = (f'0%{{{prop}:0}}' if a > 0 else '') + f'{a}%{{{prop}:1}}' + (f'{z}%{{{prop}:0}}' if z < 100 else '')
        self.raw(f'@keyframes {name}{{{frames}}}.{name}{{animation:{name} {period}s step-end infinite}}')
        return name

    def typed(self, prefix, text, color, start, dt, end, period):
        """One tspan per character (font-independent reveal); returns the tspans."""
        return ''.join(f'<tspan fill="{color}" class="{self.window(f"{prefix}{j}", start + j * dt, end, period, "fill-opacity")}">'
                       f'{escape(c)}</tspan>' for j, c in enumerate(text))

    def meteor(self, name, x, y, dx, dy, period, delay):
        """A short streak crossing the sky once per period."""
        self.raw(f'@keyframes {name}{{0%{{transform:translate(0,0);opacity:0}}1%{{opacity:1}}'
                 f'7%{{transform:translate({dx}px,{dy}px);opacity:0}}100%{{transform:translate({dx}px,{dy}px);opacity:0}}}}'
                 f'.{name}{{animation:{name} {period}s linear {delay}s infinite}}')
        length = (dx * dx + dy * dy) ** .5
        ux, uy = dx / length * 26, dy / length * 26
        return (f'<g class="{name}" opacity="0"><path d="M {x} {y} l {ux:.1f} {uy:.1f}" stroke="#f5d2a4" '
                f'stroke-width="2" stroke-linecap="square" opacity=".9"/>'
                f'<rect x="{x + ux - 1:.1f}" y="{y + uy - 1:.1f}" width="3" height="3" fill="#fff4dc"/></g>')

    def stars(self, points):
        """Pixel stars with staggered twinkle; points are (x, y, color, delay)."""
        return [f'<rect x="{x}" y="{y}" width="3" height="3" fill="{c}" style="animation:tw 3.4s ease-in-out {d}s infinite"/>'
                for x, y, c, d in points]

    def style(self):
        return ('<style>@keyframes blink{0%{opacity:1}50%{opacity:0}}.blink{animation:blink 1.1s step-end infinite}'
                '@keyframes tw{0%,100%{opacity:.2}50%{opacity:1}}'
                '@keyframes breathe{0%,100%{opacity:.6}50%{opacity:1}}'
                + ''.join(self.frames) +
                '@media (prefers-reduced-motion:reduce){*{animation:none!important}}</style>')
