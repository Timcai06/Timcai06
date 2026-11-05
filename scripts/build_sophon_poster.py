"""Build editorial Sophon panels from the existing screenshot gallery."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'assets/showcase'
GALLERY = BASE / 'sophon-2026-11'
FONTS = BASE / 'fonts'
WIDTH = 1800
DARK, PAPER, MUTED, GREEN = '#0a0c0b', '#e8e4d8', '#aaa9a4', '#d1d0c8'
FRAME, CORNER = '#59636f', '#a7b3c0'


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def text(canvas, xy, value, size=22, color=None, face='DMMono-Regular.ttf'):
    ImageDraw.Draw(canvas).text(xy, value, font=font(face, size), fill=color or PAPER)


def picture(canvas, name, box):
    source = Image.open(GALLERY / f'{name}.jpg')
    canvas.paste(ImageOps.fit(source, box[2:], method=Image.Resampling.LANCZOS), box[:2])
    x, y, width, height = box
    style = {
        'home-hero': (18, 0),
        'home-contact': (5, 18),
        'home-valley': (10, 0),
        'rsi-hero': (18, 0),
        'rsi-state': (10, 0),
        'rsi-transition': (4, 20),
        'rsi-explanation': (8, 0),
    }[name]
    frame(canvas, (x, y, width, height), *style)


def frame(canvas, box, radius=12, cut=0):
    """Quiet rounded outline; selected supporting frames have a transparent cut."""
    x, y, width, height = box
    scale = 3
    size = (width * scale, height * scale)

    def silhouette(inset):
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        right, bottom = size[0] - 1, size[1] - 1
        draw.rounded_rectangle((inset, inset, right - inset, bottom - inset),
                               radius=max(0, radius * scale - inset), fill=255)
        if cut:
            # The diagonal remains parallel for the inset outline.
            diagonal = cut * scale + round(inset * 1.414)
            draw.polygon([(right, bottom - diagonal),
                          (right - diagonal, bottom), (right, bottom)], fill=0)
        return mask

    from PIL import ImageChops
    outer = silhouette(0)
    inner = silhouette(3)  # one source pixel; subtle at README display width
    alpha = outer.resize((width, height), Image.Resampling.LANCZOS)
    region = canvas.crop((x, y, x + width, y + height))
    region.putalpha(alpha)
    canvas.paste(region, (x, y))
    border = Image.new('RGBA', size, FRAME)
    border.putalpha(ImageChops.subtract(outer, inner))
    canvas.alpha_composite(border.resize((width, height), Image.Resampling.LANCZOS), (x, y))


def label(canvas, y, number, title, light=False):
    text(canvas, (80, y), number, color='#58564f' if light else GREEN)
    text(canvas, (145, y), title, color=DARK if light else PAPER)


def build(light=False):
    global PAPER, MUTED, GREEN, FRAME, CORNER
    PAPER, MUTED, GREEN = (('#24292f', '#57606a', '#424a53') if light
                           else ('#e6edf3', '#a0aab5', '#c9d1d9'))
    FRAME, CORNER = ('#b7bec6', '#57606a') if light else ('#424a54', '#a7b3c0')
    home = Image.new('RGBA', (WIDTH, 1500), (0, 0, 0, 0))
    draw = ImageDraw.Draw(home)
    text(home, (80, 45), 'TIM CAI / SELECTED WORK')
    text(home, (1335, 45), 'WEB EXPERIENCE', color=MUTED)
    draw.line((80, 91, 1720, 91), fill=FRAME)
    text(home, (73, 111), 'SOPHON', 180, face='BigShoulders-Bold.ttf')
    text(home, (780, 132), 'AI', 150, GREEN, 'CrimsonPro-Italic.ttf')
    text(home, (1234, 147), 'DESIGN + DEVELOPMENT', 18, MUTED)
    text(home, (1234, 180), 'HOME / RSI / MEMORY', 18, MUTED)
    picture(home, 'home-hero', (80, 398, 1640, 619))
    picture(home, 'home-contact', (80, 1099, 530, 200))
    picture(home, 'home-valley', (650, 1040, 1070, 403))
    text(home, (80, 1330), 'HOME / CONTACT', 18, MUTED)

    rsi = Image.new('RGBA', (WIDTH, 1860), (0, 0, 0, 0))
    picture(rsi, 'rsi-hero', (80, 95, 1640, 618))
    picture(rsi, 'rsi-state', (80, 741, 1040, 392))
    picture(rsi, 'rsi-transition', (1150, 741, 570, 215))
    text(rsi, (1150, 984), 'TRANSITION / STILL', 19, MUTED)
    text(rsi, (1150, 1018), 'CONTINUOUS-TIME STATE', 19, MUTED)
    picture(rsi, 'rsi-explanation', (80, 1170, 1640, 601))
    text(rsi, (80, 1801), 'WHAT REMAINS AFTER AN INTERACTION?', 19, MUTED)

    memory = Image.new('RGBA', (WIDTH, 1000), (0, 0, 0, 0))
    text(memory, (80, 98), 'What remains.', 110, PAPER, 'CrimsonPro-Italic.ttf')
    source = Image.open(BASE / 'sophon.jpg')
    height = round(source.height * 1640 / source.width)
    memory.paste(source.resize((1640, height), Image.Resampling.LANCZOS), (80, 250))
    frame(memory, (80, 250, 1640, height), radius=12)
    text(memory, (80, 964), 'TIMCAI06 / SOPHON AI', 16, MUTED)

    # Trim the former chapter-label strips; README supplies native headings.
    rsi = rsi.crop((0, 80, WIDTH, 1790))
    memory = memory.crop((0, 85, WIDTH, 1000))
    panels = {'home': home, 'rsi': rsi, 'memory': memory}
    for name, canvas in panels.items():
        suffix = '-light' if light else ''
        canvas.save(BASE / f'sophon-poster-{name}{suffix}.png', optimize=True)
    return panels


if __name__ == '__main__':
    build()
    build(light=True)
