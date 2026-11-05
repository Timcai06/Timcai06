"""Build editorial Sophon panels from the existing screenshot gallery."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'assets/showcase'
GALLERY = BASE / 'sophon-2026-11'
FONTS = BASE / 'fonts'
WIDTH = 1800
DARK, PAPER, MUTED, GREEN = '#0a0c0b', '#e8e4d8', '#aaa9a4', '#d1d0c8'
RSI_BACKGROUND = '#101012'


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def text(canvas, xy, value, size=22, color=PAPER, face='DMMono-Regular.ttf'):
    ImageDraw.Draw(canvas).text(xy, value, font=font(face, size), fill=color)


def picture(canvas, name, box):
    source = Image.open(GALLERY / f'{name}.jpg')
    canvas.paste(ImageOps.fit(source, box[2:], method=Image.Resampling.LANCZOS), box[:2])
    x, y, width, height = box
    ImageDraw.Draw(canvas).rectangle((x, y, x + width - 1, y + height - 1),
                                    outline='#29292b', width=1)


def label(canvas, y, number, title, light=False):
    text(canvas, (80, y), number, color='#58564f' if light else GREEN)
    text(canvas, (145, y), title, color=DARK if light else PAPER)


def build():
    home = Image.new('RGB', (WIDTH, 1500), DARK)
    draw = ImageDraw.Draw(home)
    text(home, (80, 45), 'TIM CAI / SELECTED WORK')
    text(home, (1335, 45), 'WEB EXPERIENCE', color=MUTED)
    draw.line((80, 91, 1720, 91), fill='#30302f')
    text(home, (73, 111), 'SOPHON', 180, face='BigShoulders-Bold.ttf')
    text(home, (780, 132), 'AI', 150, GREEN, 'CrimsonPro-Italic.ttf')
    text(home, (1234, 147), 'DESIGN + DEVELOPMENT', 18, MUTED)
    text(home, (1234, 180), 'HOME / RSI / MEMORY', 18, MUTED)
    picture(home, 'home-hero', (80, 398, 1640, 619))
    picture(home, 'home-contact', (80, 1099, 530, 200))
    picture(home, 'home-valley', (650, 1040, 1070, 403))
    text(home, (80, 1330), 'HOME / CONTACT', 18, MUTED)

    rsi = Image.new('RGB', (WIDTH, 1860), RSI_BACKGROUND)
    picture(rsi, 'rsi-hero', (80, 95, 1640, 618))
    picture(rsi, 'rsi-state', (80, 741, 1040, 392))
    picture(rsi, 'rsi-transition', (1150, 741, 570, 215))
    text(rsi, (1150, 984), 'TRANSITION / STILL', 19, MUTED)
    text(rsi, (1150, 1018), 'CONTINUOUS-TIME STATE', 19, MUTED)
    picture(rsi, 'rsi-explanation', (80, 1170, 1640, 601))
    text(rsi, (80, 1801), 'WHAT REMAINS AFTER AN INTERACTION?', 19, MUTED)

    memory = Image.new('RGB', (WIDTH, 1000), PAPER)
    text(memory, (80, 98), 'What remains.', 110, DARK, 'CrimsonPro-Italic.ttf')
    source = Image.open(BASE / 'sophon.jpg')
    height = round(source.height * 1640 / source.width)
    memory.paste(source.resize((1640, height), Image.Resampling.LANCZOS), (80, 250))
    text(memory, (80, 964), 'TIMCAI06 / SOPHON AI', 16, '#58564f')

    # Trim the former chapter-label strips; README supplies native headings.
    rsi = rsi.crop((0, 80, WIDTH, 1790))
    memory = memory.crop((0, 85, WIDTH, 1000))
    panels = {'home': home, 'rsi': rsi, 'memory': memory}
    for name, canvas in panels.items():
        canvas.save(BASE / f'sophon-poster-{name}.png', optimize=True)
    return panels


if __name__ == '__main__':
    build()
