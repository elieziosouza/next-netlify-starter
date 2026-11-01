"""Capas de impacto do corte do sigilo (A foto do debate + ABRE O SIGILO, FLÁVIO!, B documento do TSE + LULA AUTORIZOU, C ele + E AGORA, FLÁVIO?)."""
import sys, importlib.util
import numpy as np, cv2
S = sys.argv[1]
spec = importlib.util.spec_from_file_location("rc", f"{S}/work/render_sigilo_cnn.py"); sys.argv = [sys.argv[0], S, "/dev/null", "cover"]
G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G); R = G.R
from PIL import Image, ImageDraw
W, H = R.W, R.H; V = G.V; BAR = R.BAR; CX = R.CX
YEL = (255, 214, 0); RED = (226, 32, 38)
def word(img, txt, cy, size, col, stroke=R.NAVY, sw=12, rot=0, band=None, tcol=None, maxw=700):
    f = R.BIGF(size)
    while f.getlength(txt) > maxw: size -= 4; f = R.BIGF(size)
    tw = f.getlength(txt); h = int(size * 1.25)
    lay = Image.new("RGBA", (int(tw + 90), h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if band: d.rounded_rectangle((0, 6, lay.width - 1, h + 12), 16, fill=band + (255,))
    d.text((lay.width / 2, lay.height / 2 + 4), txt, font=f, fill=(tcol or col) + (255,), anchor="mm", stroke_width=0 if band else sw, stroke_fill=stroke + (255,))
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    R.paste(img, lay, CX - lay.width / 2, cy - lay.height / 2, 0.7, 18, (6, 14))
def base(src):
    return Image.fromarray(np.clip(R.blur_bg(src, 0.32), 0, 255).astype(np.uint8)).convert("RGBA")
def card(img, src, w, y, rad=28):
    c = Image.fromarray(R.rounded(G.fit_w(cv2.LUT(src, R.LUT), w), rad, 5)); R.paste(img, c, CX - w / 2, y, 0.6, 22, (8, 20)); return y + c.height
def finish(img, name):
    BAR.draw_bar(img, 0.0, "canal"); img.alpha_composite(R.top, (R.HDX, 0)); img.convert("RGB").save(f"{V}/{name}.jpg", quality=95)
F = G.FOTO
A = base(F); word(A, "ABRE O SIGILO,", 260, 170, YEL); word(A, "FLÁVIO!", 450, 210, YEL)
y = card(A, F, 980, 600); word(A, "O LULA JÁ AUTORIZOU O DELE", y + 120, 84, (255, 255, 255), band=RED, tcol=(255, 255, 255), rot=-3)
word(A, "E DA FAMÍLIA INTEIRA", y + 270, 80, (255, 255, 255), sw=8)
finish(A, "cnn_capa_A")
B = base(G.DOC); word(B, "LULA AUTORIZOU!", 270, 160, RED, stroke=(255, 255, 255), sw=10, rot=-4)
y = card(B, G.DOC, 900, 430); word(B, "QUEBRA DO PRÓPRIO SIGILO NO TSE", y + 110, 74, R.NAVY, band=YEL, tcol=R.NAVY, rot=-2)
word(B, "E O FLÁVIO?", y + 270, 150, (255, 255, 255), sw=10)
finish(B, "cnn_capa_B")
C = base(F); word(C, "E AGORA,", 250, 190, YEL); word(C, "FLÁVIO?", 450, 230, YEL)
y = card(C, F, 980, 620)
me = cv2.LUT(G.me_big(3.5)[60:1500], R.LUT); mw = cv2.resize(me, (430, 430 * 1440 // 1080)); R.paste(C, Image.fromarray(R.rounded(mw, 26, 5)), CX + 70, y - 60, 0.7, 20, (6, 16))
f_ = R.BIGF(84); dd = ImageDraw.Draw(C); dd.rounded_rectangle((120, y + 120, 600, y + 260), 18, fill=RED + (255,)); dd.text((360, y + 190), "LULA AUTORIZOU", font=f_, fill=(255, 255, 255, 255), anchor="mm")
dd.text((360, y + 320), "ABRIR O SIGILO", font=R.BIGF(80), fill=YEL + (255,), anchor="mm", stroke_width=8, stroke_fill=R.NAVY + (255,))
finish(C, "cnn_capa_C")
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/cnn_capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas_cnn_ABC.jpg", quality=90); print("ok")
# D e E: a arte do Lula x Flávio frente a frente que ele mandou
FO = np.asarray(Image.open(f"{V}/faceoff.webp").convert("RGB"))
def faceoff_base():
    img = base(FO); big_ = cv2.resize(FO, (1200, 800), interpolation=cv2.INTER_LANCZOS4)[:, 60:1140]   # sem bordas laterais vazias
    fo = Image.fromarray(big_).convert("RGBA"); m = Image.new("L", fo.size, 255); d = ImageDraw.Draw(m)
    for i in range(80): d.line((0, i, fo.width, i), fill=int(255 * i / 80)); d.line((0, fo.height - 1 - i, fo.width, fo.height - 1 - i), fill=int(255 * i / 80))
    fo.putalpha(m); img.alpha_composite(fo, (0, 470)); return img
D = faceoff_base(); word(D, "ABRE O SIGILO,", 230, 170, YEL); word(D, "FLÁVIO!", 400, 200, YEL)
word(D, "O LULA JÁ AUTORIZOU O DELE", 1380, 84, (255, 255, 255), band=RED, tcol=(255, 255, 255), rot=-3)
word(D, "E VOCÊ?", 1560, 170, (255, 255, 255), sw=10)
finish(D, "cnn_capa_D")
E = faceoff_base(); word(E, "LULA AUTORIZOU", 230, 160, (255, 255, 255)); word(E, "ABRIR O SIGILO", 400, 160, YEL)
word(E, "E O FLÁVIO?", 1420, 190, YEL); word(E, "DESAFIO DO DEBATE DA BAND", 1600, 64, R.NAVY, band=YEL, tcol=R.NAVY, rot=-2)
finish(E, "cnn_capa_E")
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/cnn_capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("DEA")]
sheet.save(f"{V}/capas_cnn_DE.jpg", quality=90); print("ok2")
# B2 (escolhida, mais política e envolvente): documento do TSE com carimbo, o frente a frente embaixo e a pergunta no meio
B2 = Image.fromarray(np.clip(R.blur_bg(FO, 0.30), 0, 255).astype(np.uint8)).convert("RGBA")
fo = Image.fromarray(cv2.resize(FO, (1200, 800), interpolation=cv2.INTER_LANCZOS4)[60:800, 60:1140]).convert("RGBA")
m = Image.new("L", fo.size, 255); dm = ImageDraw.Draw(m)
for i in range(160): dm.line((0, i, fo.width, i), fill=int(255 * i / 160))
fo.putalpha(m); B2.alpha_composite(fo, (0, H - fo.height))
word(B2, "LULA AUTORIZOU", 215, 150, (255, 255, 255))
word(B2, "ABRIR O PRÓPRIO SIGILO", 360, 84, R.NAVY, band=YEL, tcol=R.NAVY, rot=-2)
doc = Image.fromarray(R.rounded(G.fit_w(G.DOC, 760), 22, 5)).rotate(-3, resample=Image.BICUBIC, expand=True)
R.paste(B2, doc, CX - doc.width / 2, 450, 0.7, 24, (10, 22))
st = Image.new("RGBA", (620, 150), (0, 0, 0, 0)); ds = ImageDraw.Draw(st)
ds.rounded_rectangle((6, 6, 613, 143), 18, outline=RED + (255,), width=10); ds.text((310, 78), "PEDIDO NO TSE", font=R.BIGF(96), fill=RED + (255,), anchor="mm")
st = st.rotate(12, resample=Image.BICUBIC, expand=True); R.paste(B2, st, CX - st.width / 2 + 60, 700, 0.3, 8, (3, 6))
word(B2, "E O FLÁVIO?", 1190, 200, YEL, sw=14)
finish(B2, "cnn_capa_B2")
print("ok3")
