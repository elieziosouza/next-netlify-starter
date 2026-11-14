import sys
sys.path.insert(0, '.')
from motor import F, RED, WHITE, logo, tw
from PIL import Image, ImageDraw, ImageEnhance
S = '/tmp/claude-0/-home-user-next-netlify-starter/6f39d91d-c3da-569d-877d-3efa63008be2/scratchpad/'
TW, TH = 1280, 720
im = Image.open(S + 'fr_angry_16.jpg').convert('RGB')
s = max(TW / im.width, TH / im.height) * 1.18
im = im.resize((int(im.width * s), int(im.height * s)))
x = int((im.width - TW) * 0.75); y = int((im.height - TH) * 0.3)
im = im.crop((x, y, x + TW, y + TH))
im = ImageEnhance.Brightness(im).enhance(0.5).convert('RGBA')
# escurece de baixo para cima e da esquerda, como no post
g = Image.new('L', (TW, TH))
px = g.load()
for yy in range(TH):
    for xx in range(0, TW, 4):
        v = max(0, (yy - 180) / 540) * 0.75 + max(0, (700 - xx) / 700) * 0.55
        for k in range(4):
            if xx + k < TW: px[xx + k, yy] = int(255 * min(0.95, v))
sh = Image.new('RGBA', (TW, TH), (0, 0, 0, 255)); sh.putalpha(g); im.alpha_composite(sh)
d = ImageDraw.Draw(im)
logo(im, 66, 62, 26, 1, 5); d.text((106, 62), 'OVERDRAWN FILES', font=F('xbold', 30), fill=WHITE, anchor='lm')
tag = 'USA · NOV 13'
d.rectangle((52, 250, 52 + tw(tag, F('black', 38)) + 40, 308), fill=RED)
d.text((72, 279), tag, font=F('black', 38), fill=WHITE, anchor='lm')
d.text((48, 322), 'EVERY U.S. FLIGHT', font=F('black', 96), fill=WHITE, stroke_width=5, stroke_fill=(0, 0, 0))
d.text((48, 425), 'STOPPED.', font=F('black', 96), fill=WHITE, stroke_width=5, stroke_fill=(0, 0, 0))
d.text((48, 528), 'WHO PAYS?', font=F('black', 132), fill=RED, stroke_width=6, stroke_fill=(0, 0, 0))
im.convert('RGB').save('entrega/Overdrawn Files - Ground Stop EUA - THUMB 4 ESTILO POST.jpg', quality=92)
print('ok')
