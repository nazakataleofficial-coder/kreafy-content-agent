"""Offline poster composition: fit the complete source photo, never crop or regenerate it."""
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
    width, height = SIZES[variant]
    wide = variant == 'wide'
    canvas = Image.new('RGB', (width, height), '#0F0F0F')
    draw = ImageDraw.Draw(canvas)
    gold, white = '#C8A96B', '#F7F5EF'
    draw.text((48, 34), 'TheAleBuilds x Kreafy', font=font(25, True), fill=gold)
    if wide:
        box, text_xy, text_width = (820, 100, 1160, 590), (48, 120), 710
        max_head_height, headline_size = 190, 62
    else:
        box, text_xy, text_width = (48, 430, 600, 1220), (48, 130), 984
        max_head_height, headline_size = 190, 70
    # EXIF orientation is respected; entire source remains inside a dedicated box.
    with Image.open(photo) as opened:
        source = ImageOps.exif_transpose(opened).convert('RGB')
        source.thumbnail((box[2] - box[0], box[3] - box[1]), Image.Resampling.LANCZOS)
        xy = (box[0] + (box[2]-box[0]-source.width)//2,
              box[1] + (box[3]-box[1]-source.height)//2)
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
    for line in wrapped:
        draw.text((x, y), line, font=face, fill=white)
        y += step
    y += 20
    small = font(25 if wide else 30)
    for line in lines(draw, takeaway, small, text_width):
        if y + small.size + 10 > height - 92:
            raise ValueError('Takeaway would overlap footer')
        draw.text((x, y), line, font=small, fill=gold)
        y += small.size + 10
    cx, cy, cw = (48, 405, 710) if wide else (645, 465, 385)
    checklist_font = font(24 if wide else 29)
    for i, item in enumerate(checklist, 1):
        prefix = f'{i:02d}'
        if wide:
            draw.text((cx, cy), prefix, font=font(23, True), fill=gold)
            draw.text((cx+55, cy), item, font=checklist_font, fill=white)
            cy += 53
        else:
            draw.text((cx, cy), prefix, font=font(25, True), fill=gold)
            cy += 43
            for line in lines(draw, item, checklist_font, cw):
                draw.text((cx, cy), line, font=checklist_font, fill=white)
                cy += 41
            cy += 66
        if cy > height-82:
            raise ValueError('Checklist would overlap footer')
    draw.line((48, height-76, width-48, height-76), fill=gold, width=2)
    draw.text((48, height-58), 'kreafy.online', font=font(23), fill=gold)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, 'PNG', optimize=True)
    return {'size': [width, height], 'source_cropped': False, 'face_regenerated': False}
