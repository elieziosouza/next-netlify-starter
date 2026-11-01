"""Capas de impacto do corte do Bolsa Família (A Flávio + BOLSA FARELO, B matéria + APAGOU!, C ele + PRESAS PRA SEMPRE?)."""
import sys, importlib.util
import numpy as np, cv2
S = sys.argv[1]
spec = importlib.util.spec_from_file_location("rb", f"{S}/work/render_bolsa_farelo.py"); sys.argv = [sys.argv[0], S, "/dev/null", "cover"]
G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G); R = G.R
from PIL import Image, ImageDraw, ImageFilter
W, H = R.W, R.H; V = G.V; BAR = R.BAR; CX = R.CX
YEL = (255, 214, 0); RED = (226, 32, 38)
def word(img, txt, cy, size, col, stroke=R.NAVY, sw=12, rot=0, band=None, tcol=None, maxw=700):
    f = R.BIGF(size); d0 = ImageDraw.Draw(Image.new("L", (4, 4)))
    while d0.textlength(txt, font=f) > maxw: size -= 4; f = R.BIGF(size)
    tw = d0.textlength(txt, font=f); h = int(size * 1.25)
    lay = Image.new("RGBA", (int(tw + 90), h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if band: d.rounded_rectangle((0, 6, lay.width - 1, h + 12), 16, fill=band + (255,))
    d.text((lay.width / 2, lay.height / 2 + 4), txt, font=f, fill=(tcol or col) + (255,), anchor="mm", stroke_width=0 if band else sw, stroke_fill=stroke + (255,))
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    R.paste(img, lay, CX - lay.width / 2, cy - lay.height / 2, 0.7, 18, (6, 14))
def fill_bg(src, dark=0.75):
    bg = cv2.resize(src, (int(src.shape[1] * H / src.shape[0]), H), interpolation=cv2.INTER_LANCZOS4)
    x0 = max(0, (bg.shape[1] - W) // 2); bg = bg[:, x0:x0 + W]
    if bg.shape[1] < W: bg = cv2.resize(bg, (W, H))
    return bg
def vignette(img):
    g = Image.new("L", (W, H), 0); d = ImageDraw.Draw(g)
    for i in range(0, 600, 6): d.rectangle((0, H - 600 + i, W, H - 600 + i + 6), fill=int(240 * i / 600))
    dk = Image.new("RGBA", (W, H), (2, 8, 18, 255)); dk.putalpha(g); img.alpha_composite(dk)
    g2 = Image.new("L", (W, H), 0); d2 = ImageDraw.Draw(g2)
    for i in range(0, 380, 6): d2.rectangle((0, i, W, i + 6), fill=int(200 * (1 - i / 380)))
    dk2 = Image.new("RGBA", (W, H), (2, 8, 18, 255)); dk2.putalpha(g2); img.alpha_composite(dk2)
def finish(img, name):
    BAR.draw_bar(img, 0.0, "canal"); img.alpha_composite(R.top, (R.HDX, 0)); img.convert("RGB").save(f"{V}/{name}.jpg", quality=95)
# A: o Flávio em close (lado esquerdo da foto do áudio), BOLSA FARELO
ph = G.PHOTO; fl = ph[:, :400]
A = Image.fromarray(fill_bg(cv2.LUT(fl, R.LUT))).convert("RGBA"); vignette(A)
word(A, "“BOLSA", 300, 230, YEL); word(A, "FARELO”", 520, 230, YEL)
word(A, "ELE APAGOU OS POSTS", 1430, 110, (255, 255, 255), band=RED, tcol=(255, 255, 255), rot=-3)
word(A, "E AGORA DEFENDE O BOLSA FAMÍLIA?", 1600, 66, (255, 255, 255), sw=8)
finish(A, "bolsa_capa_A")
# B: a foto da matéria, carimbo APAGOU!
u = G.UOL[470:, 0:640]; B = Image.fromarray(fill_bg(cv2.LUT(u, R.LUT))).convert("RGBA"); vignette(B)
word(B, "APAGOU!", 330, 260, RED, stroke=(255, 255, 255), sw=10, rot=6)
word(B, "OS POSTS DO “BOLSA FARELO”", 1440, 90, R.NAVY, band=YEL, tcol=R.NAVY, rot=-2)
word(B, "E AGORA DIZ QUE DEFENDE?", 1610, 76, (255, 255, 255), sw=8)
finish(B, "bolsa_capa_B")
# C: ele com a foto do áudio, PRESAS PRA SEMPRE?
C = Image.fromarray(np.clip(R.blur_bg(ph, 0.35), 0, 255).astype(np.uint8)).convert("RGBA")
card = Image.fromarray(R.rounded(cv2.resize(ph, (980, int(980 * ph.shape[0] / 720))), 28, 5)); R.paste(C, card, CX - 490, 520, 0.6, 22, (8, 20))
me = cv2.LUT(G.me_big(1.25)[60:1500], R.LUT); mw = cv2.resize(me, (470, 470 * 1440 // 1080)); R.paste(C, Image.fromarray(R.rounded(mw, 26, 5)), CX + 40, 1060, 0.7, 20, (6, 16))
word(C, "PRESAS PRA", 250, 190, YEL); word(C, "SEMPRE?", 430, 190, YEL)
R.paste(C, Image.new("RGBA", (1, 1)), 0, 0, 0)
lay_x = CX - 260
wordC = word

f_ = R.BIGF(130); dd = ImageDraw.Draw(C); dd.rounded_rectangle((150, 1180, 520, 1360), 18, fill=RED + (255,)); dd.text((335, 1272), 'OUÇA', font=f_, fill=(255, 255, 255, 255), anchor='mm')
f2 = R.BIGF(72); dd.text((335, 1440), 'O ÁUDIO', font=f2, fill=YEL + (255,), anchor='mm', stroke_width=7, stroke_fill=R.NAVY + (255,))
C2 = C
d = ImageDraw.Draw(C2)
finish(C2, "bolsa_capa_C")
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/bolsa_capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas_bolsa_ABC.jpg", quality=90); print("ok")
