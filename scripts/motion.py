"""Shared CSS motion helpers for the profile SVGs (workspace.svg, skyline.svg).

GitHub renders README SVGs as <img>, where CSS keyframes still run. Like a pixel
room with a few moving props, nearly everything stays still. Each moving element
carries its reduced-motion end state as attributes; prefers-reduced-motion turns
the keyframes off and leaves that state.
"""
from html import escape


class Motion:
    def __init__(self, phase=0.0):
        # phase (s) shifts every window loop, so several SVGs on one page do not move in lockstep.
        self.frames = []
        self.phase = phase

    def raw(self, css):
        self.frames.append(css)

    def window(self, name, start, end, period, prop='opacity'):
        """Visible only during [start, end) seconds of a looping period; start > end wraps around."""
        a, z = round(start / period * 100, 3), round(end / period * 100, 3)
        if a > z:
            frames = f'0%{{{prop}:1}}{z}%{{{prop}:0}}{a}%{{{prop}:1}}'
        else:
            frames = (f'0%{{{prop}:0}}' if a > 0 else '') + f'{a}%{{{prop}:1}}' + (f'{z}%{{{prop}:0}}' if z < 100 else '')
        self.raw(f'@keyframes {name}{{{frames}}}.{name}{{animation:{name} {period}s step-end {-(self.phase % period):.2f}s infinite}}')
        return name

    def spans(self, name, intervals, period, prop='opacity'):
        """Visible during each [start, end) of a looping period (step changes)."""
        pct = lambda t: round(t / period * 100, 3)
        frames, on = [], False
        for t in sorted({0, *[x for ab in intervals for x in ab]}):
            now = any(a <= t < z for a, z in intervals)
            if t == 0 or now != on:
                frames.append(f'{pct(t)}%{{{prop}:{1 if now else 0}}}')
                on = now
        self.raw(f'@keyframes {name}{{{"".join(frames)}}}.{name}{{animation:{name} {period}s step-end infinite}}')
        return name

    def appear(self, name, at, period, dx=0, dy=0, dur=.45):
        """Hidden from the start of each loop, eases in at `at` seconds, then stays."""
        a, z = round(at / period * 100, 3), round((at + dur) / period * 100, 3)
        hidden = f'opacity:0;transform:translate({dx}px,{dy}px)'
        self.raw(f'@keyframes {name}{{0%,{a}%{{{hidden}}}{z}%,100%{{opacity:1;transform:translate(0,0)}}}}'
                 f'.{name}{{animation:{name} {period}s ease-out infinite}}')
        return name

    def pop(self, name, start, end, period, dy=-6, dur=.2):
        """Eases in at `start`, eases out by `end` (for overlays such as a command palette)."""
        p = lambda t: round(t / period * 100, 3)
        hidden = f'opacity:0;transform:translate(0,{dy}px)'
        self.raw(f'@keyframes {name}{{0%,{p(start)}%{{{hidden}}}{p(start + dur)}%,{p(end - dur)}%{{opacity:1;transform:translate(0,0)}}'
                 f'{p(end)}%,100%{{{hidden}}}}}.{name}{{animation:{name} {period}s ease-out infinite}}')
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
