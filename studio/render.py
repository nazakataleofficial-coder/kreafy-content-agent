"""Offline composition: fit the approved photographic region without face regeneration."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

SIZES = {'portrait': (1080, 1350), 'wide': (1200, 675)}


def font(size, bold=False):
    names = ['DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf',
             'C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf']
    for name in names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    raise RuntimeError('A readable TrueType font is required; no silent tiny-font fallback')


def lines(draw, text, face, width):
    result, current = [], ''
    for word in text.split():
        candidate = f'{current} {word}'.strip()
        if draw.textlength(candidate, font=face) > width and current:
            result.append(current)
            current = word
        else:
            current = candidate
        if draw.textlength(current, font=face) > width:
            raise ValueError('Headline contains a word too wide to render')
    return result + [current] if current else result


def render(photo, headline, takeaway, output, variant='portrait', checklist=()):
    """Photo-first layout. Detailed advice belongs in the platform caption.

    Accept a pre-extracted approved photo or a normal image path. Fit it in full;
    never use generative processing, stretch it, or overlay the face with text.
    """
    width, height = SIZES[variant]
    wide = variant == 'wide'
    canvas = Image.new('RGB', (width, height), '#101214')
    draw = ImageDraw.Draw(canvas)
    if wide:
        box, text_xy, text_width = (470, 0, 1200, 651), (34, 155), 405
        max_head_height, headline_size = 330, 54
    else:
        box, text_xy, text_width = (0, 0, 1080, 963), (46, 1001), 988
        max_head_height, headline_size = 234, 76
    if isinstance(photo, Image.Image):
        source = photo.copy().convert('RGB')
    else:
        with Image.open(photo) as opened:
            source = ImageOps.exif_transpose(opened).convert('RGB')
    source = ImageOps.contain(source, (box[2]-box[0], box[3]-box[1]), Image.Resampling.LANCZOS)
    xy = (box[0]+(box[2]-box[0]-source.width)//2,
          box[1]+(box[3]-box[1]-source.height)//2)
    canvas.paste(source, xy)
    for size in range(headline_size, 33, -2):
        face = font(size, True)
        wrapped = lines(draw, headline, face, text_width)
        step = size + 12
        if len(wrapped) * step <= max_head_height:
            break
    else:
        raise ValueError('Headline does not fit; shorten before rendering')
    x, y = text_xy
    for i, line in enumerate(wrapped):
        draw.text((x, y), line, font=face, fill='#F7F5EF' if i == 0 else '#F2C861')
        y += step
    footer_y = height-54 if not wide else height-42
    draw.text((34 if wide else 46, footer_y), 'TheAleBuilds · Kreafy',
              font=font(22 if wide else 26), fill='#C8A96B')
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, 'PNG', optimize=True)
    return {'size': [width, height], 'source_cropped': False, 'face_regenerated': False,
            'photo_box': list(box), 'template_version': 3}
