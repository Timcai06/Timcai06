"""Antialiased image frames shared by the profile exhibition panels."""
from PIL import Image, ImageDraw


def frame(canvas, box, radius=14, cut=0, color="#424a54"):
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
    border = Image.new('RGBA', size, color)
    border.putalpha(ImageChops.subtract(outer, inner))
    canvas.alpha_composite(border.resize((width, height), Image.Resampling.LANCZOS), (x, y))

