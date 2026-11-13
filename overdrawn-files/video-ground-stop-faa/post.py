import sys
sys.path.insert(0, '.')
from motor import F, RED, WHITE, GREY, logo, tw
from PIL import Image, ImageDraw, ImageEnhance
S = '/tmp/claude-0/-home-user-next-netlify-starter/6f39d91d-c3da-569d-877d-3efa63008be2/scratchpad/'
im = Image.open(S + 'fr_angry_16.jpg').convert('RGB')
s = 1080 / im.height * 1.15
im = im.resize((int(im.width * s), int(im.height * s)))
x = int((im.width - 1080) * 0.62); im = im.crop((x, 0, x + 1080, 1080))
im = ImageEnhance.Brightness(im).enhance(0.45).convert('RGBA')
g = Image.new('L', (1, 1080))
for y in range(1080): g.putpixel((0, y), int(255 * max(0, (y - 380) / 700)))
sh = Image.new('RGBA', (1080, 1080), (0, 0, 0, 255)); sh.putalpha(g.resize((1080, 1080))); im.alpha_composite(sh)
d = ImageDraw.Draw(im)
logo(im, 80, 80, 28, 1, 5); d.text((124, 80), 'OVERDRAWN FILES', font=F('xbold', 34), fill=WHITE, anchor='lm')
d.rectangle((60, 520, 60 + tw('NEW VIDEO', F('black', 40)) + 40, 580), fill=RED)
d.text((80, 550), 'NEW VIDEO', font=F('black', 40), fill=WHITE, anchor='lm')
for i, (t, c) in enumerate([('EVERY U.S. FLIGHT', WHITE), ('STOPPED.', WHITE), ('WHO PAYS?', RED)]):
    d.text((56, 600 + i * 112), t, font=F('black', 92 if i < 2 else 118), fill=c, stroke_width=5, stroke_fill=(0, 0, 0))
d.rounded_rectangle((60, 960, 470, 1030), 35, fill=WHITE)
d.text((265, 995), '▶  WATCH NOW', font=F('black', 38), fill=(15, 15, 15), anchor='mm')
im.convert('RGB').save('entrega/Overdrawn Files - Ground Stop EUA - POST COMUNIDADE.jpg', quality=92)
print('ok')
