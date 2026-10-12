"""5x7 pixel font shared by the hero title and the closing line of the live terminal.

Glyph rows run top to bottom; blank columns are trimmed per glyph, one blank column
separates glyphs and a space is three blank columns. Descenders are folded into the
7 rows so every line has the same height.
"""

GLYPHS = {
    'H': ['10001', '10001', '10001', '11111', '10001', '10001', '10001'],
    'I': ['01110', '00100', '00100', '00100', '00100', '00100', '01110'],
    'T': ['11111', '00100', '00100', '00100', '00100', '00100', '00100'],
    'C': ['01111', '10000', '10000', '10000', '10000', '10000', '01111'],
    'a': ['00000', '00000', '01110', '00001', '01111', '10001', '01111'],
    'b': ['10000', '10000', '10110', '11001', '10001', '10001', '11110'],
    'f': ['00110', '01001', '01000', '11100', '01000', '01000', '01000'],
    'g': ['00000', '00000', '01111', '10001', '01111', '00001', '01110'],
    'h': ['10000', '10000', '10110', '11001', '10001', '10001', '10001'],
    'i': ['00100', '00000', '01100', '00100', '00100', '00100', '01110'],
    'k': ['10000', '10000', '10010', '10100', '11000', '10100', '10010'],
    'm': ['00000', '00000', '11010', '10101', '10101', '10101', '10101'],
    'n': ['00000', '00000', '10110', '11001', '10001', '10001', '10001'],
    'o': ['00000', '00000', '01110', '10001', '10001', '10001', '01110'],
    'p': ['00000', '00000', '11110', '10001', '11110', '10000', '10000'],
    'r': ['00000', '00000', '10110', '11001', '10000', '10000', '10000'],
    's': ['00000', '00000', '01111', '10000', '01110', '00001', '11110'],
    't': ['01000', '01000', '11100', '01000', '01000', '01001', '00110'],
    'y': ['00000', '00000', '10001', '10001', '01111', '00001', '01110'],
    ',': ['00000', '00000', '00000', '00000', '01100', '00100', '01000'],
    '.': ['00000', '00000', '00000', '00000', '00000', '01100', '01100'],
    "'": ['00100', '00100', '01000', '00000', '00000', '00000', '00000'],
}


def columns(text):
    """Bit columns (top to bottom) for a line of text."""
    cols = []
    for ch in text:
        if ch == ' ':
            cols += [[0] * 7] * 3
            continue
        g = GLYPHS[ch]
        used = [c for c in range(5) if any(row[c] == '1' for row in g)]
        for c in range(used[0], used[-1] + 1):
            cols.append([int(row[c]) for row in g])
        cols.append([0] * 7)
    return cols[:-1]


def mix(a, b, t):
    pa, pb = [int(a[i:i + 2], 16) for i in (1, 3, 5)], [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join(f'{round(x + (y - x) * t):02x}' for x, y in zip(pa, pb))


def render(text, x0, y0, pitch, size, top, bottom, shadow):
    """Per lit column: (column index, svg cells) plus white mask rects for highlight sweeps."""
    out, mask = [], []
    for k, bits in enumerate(columns(text)):
        on = [r for r in range(7) if bits[r]]
        if not on:
            continue
        x = x0 + k * pitch
        cells = ''.join(f'<rect x="{x + 1}" y="{y0 + r * pitch + 1}" width="{size}" height="{size}" fill="{shadow}"/>' for r in on)
        cells += ''.join(f'<rect x="{x}" y="{y0 + r * pitch}" width="{size}" height="{size}" fill="{mix(top, bottom, r / 6)}"/>' for r in on)
        mask += [f'<rect x="{x}" y="{y0 + r * pitch}" width="{size}" height="{size}" fill="#fff"/>' for r in on]
        out.append((k, cells))
    return out, mask
