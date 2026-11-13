import sys
sys.path.insert(0, '.')
from motor import F, RED, WHITE, AMBER, logo, stamp, tw
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
S = '/tmp/claude-0/-home-user-next-netlify-starter/6f39d91d-c3da-569d-877d-3efa63008be2/scratchpad/'
TW, TH = 1280, 720

def cover(path, zoom=1.0, cx=0.5, cy=0.5):
    im = Image.open(path).convert('RGB')
    s = max(TW / im.width, TH / im.height) * zoom
    im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
    x = int((im.width - TW) * cx); y = int((im.height - TH) * cy)
    return im.crop((x, y, x + TW, y + TH))

def grad(w, h, left=True, a0=240, a1=0, end=0.62):
    g = Image.new('L', (w, 1))
    for x in range(w):
        f = x / w if left else 1 - x / w
        g.putpixel((x, 0), int(a0 + (a1 - a0) * min(1, f / end)))
    return g.resize((w, h))

def outline_text(d, xy, s, f, fill, stroke=6, anchor='la'):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))

def brand(im):
    o = Image.new('RGBA', im.size, (0, 0, 0, 0))
    logo(o, 52, 52, 26, 1.0, 5)
    im.alpha_composite(o)

# A — passageiros e painel CANCELLED
im = cover(S + 'fr_angry_16.jpg', 1.12, 0.85, 0.35)
im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.15)).enhance(1.12).convert('RGBA')
sh = Image.new('RGBA', im.size, (0, 0, 0, 255)); sh.putalpha(grad(TW, TH, True, 245, 0, 0.6)); im.alpha_composite(sh)
d = ImageDraw.Draw(im)
d.rectangle((60, 150, 60 + tw('USA · NOV 13', F('black', 40)) + 40, 210), fill=RED)
d.text((80, 180), 'USA · NOV 13', font=F('black', 40), fill=WHITE, anchor='lm')
outline_text(d, (52, 240), 'EVERY', F('black', 150), WHITE)
outline_text(d, (52, 390), 'FLIGHT', F('black', 150), WHITE)
outline_text(d, (52, 540), 'STOPPED', F('black', 150), RED)
brand(im); im.convert('RGB').save('thumbs/thumb-A.jpg', quality=92)

# B — avião contra o sol, WHO PAYS?
im = cover(S + 'fr_takeoff_9.jpg', 1.5, 0.95, 0.42)
r, g, b = im.split()
im = Image.merge('RGB', (r.point(lambda v: int(v * 0.85)), g.point(lambda v: int(v * 0.42)), b.point(lambda v: int(v * 0.25))))
im = ImageEnhance.Contrast(im).enhance(1.35).convert('RGBA')
sh = Image.new('RGBA', im.size, (0, 0, 0, 255)); sh.putalpha(grad(TW, TH, False, 250, 0, 0.55)); im.alpha_composite(sh)
d = ImageDraw.Draw(im)
outline_text(d, (TW - 50, 250), 'ALL U.S. FLIGHTS', F('black', 70), WHITE, 5, 'ra')
outline_text(d, (TW - 50, 330), 'GROUNDED', F('black', 104), WHITE, 6, 'ra')
outline_text(d, (TW - 50, 460), 'WHO PAYS?', F('black', 132), RED, 7, 'ra')
brand(im); im.convert('RGB').save('thumbs/thumb-B.jpg', quality=92)

# C — painel de partidas todo STOPPED + carimbo
im = cover(S + 'fr_landing_11.jpg', 1.1, 0.5, 0.5)
im = ImageEnhance.Brightness(ImageEnhance.Color(im).enhance(0.6)).enhance(0.35).convert('RGBA')
d = ImageDraw.Draw(im)
d.rounded_rectangle((60, 120, 1220, 640), 18, fill=(10, 10, 12, 235))
d.text((100, 165), 'DEPARTURES', font=F('xbold', 40), fill=AMBER, anchor='lm')
fm = F('mono', 58)
for i, c in enumerate(['NEW YORK', 'CHICAGO', 'ATLANTA', 'DALLAS', 'DENVER']):
    y = 240 + i * 82
    d.text((100, y), c, font=fm, fill=WHITE, anchor='lm')
    d.text((1180, y), 'STOPPED', font=fm, fill=RED, anchor='rm')
st = Image.new('RGBA', im.size, (0, 0, 0, 0))
stamp(st, 'GROUND STOP', 760, 520, 10, 0, RED, 104, -9)
im.alpha_composite(st)
d = ImageDraw.Draw(im)
outline_text(d, (640, 690), 'THE ENTIRE U.S.', F('black', 60), WHITE, 5, 'mb')
brand(im); im.convert('RGB').save('thumbs/thumb-C.jpg', quality=92)

sheet = Image.new('RGB', (1280, 720 * 3 // 2 + 0))
a, b, c = [Image.open(f'thumbs/thumb-{k}.jpg').resize((640, 360)) for k in 'ABC']
sheet = Image.new('RGB', (1280, 720), (30, 30, 30)); sheet.paste(a, (0, 0)); sheet.paste(b, (640, 0)); sheet.paste(c, (320, 360))
sheet.save(S + 'thumbs_sheet.jpg', quality=90)
print('ok')
