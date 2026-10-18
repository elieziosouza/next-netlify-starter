"""Capas da pesquisa Vox Brasil de 18/10 (A e B com o rosto dele, C sem rosto), com a barra lateral do canal."""
import sys, importlib.util
import numpy as np
S = sys.argv[1]; sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("rv", f"{S}/work/render_vox.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
from PIL import Image, ImageDraw
W, H = R.W, R.H; MF = R.MF; V = R.V; BAR = R.BAR
def big(img, txt, cy, size, col=R.GOLD_L, band=None, tcol=None, rot=0):
    f = R.BIGF(size); d0 = ImageDraw.Draw(Image.new("L", (4, 4)))
    while d0.textlength(txt, font=f) > W - 220: size -= 4; f = R.BIGF(size)
    tw = d0.textlength(txt, font=f); h = int(size * 1.32)
    lay = Image.new("RGBA", (int(tw + 90), h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if band: d.rounded_rectangle((0, 0, lay.width - 1, h - 1), 18, fill=band + (255,), outline=R.GOLD + (255,), width=5)
    d.text((lay.width / 2, h / 2 + 4), txt, font=f, fill=(tcol or col) + (255,), anchor="mm", stroke_width=0 if band else 8, stroke_fill=R.NAVY + (255,))
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    R.paste(img, lay, W / 2 + 40 - lay.width / 2, cy - lay.height / 2, 0.6, 16, (5, 12))
me = R.me_src(33.4).copy()                                          # olhando para a câmera, boca fechada, fazendo o L
fa = R.big_behind(me.copy(), 2.9)
A = Image.fromarray(fa).convert("RGBA"); BAR.draw_bar(A, 0.0, "canal"); A.alpha_composite(R.top)
BAR.lower_card(A, "PESQUISA VOX BRASIL", ["LULA NA FRENTE", "DO FLÁVIO"], 1560, 1.0)
s = R.segs[1]; B = R.split_scene(s["t0"] + 2.2, s, -10.0); R.draw_card(B, 5.0, s["t0"] + 2.2); BAR.draw_bar(B, 0.0, "canal", 1.0, 1.0, 0.5); B.alpha_composite(R.top)
C = Image.fromarray(np.vstack([R.MAT, R.MAT[:H - R.SEAM]])).convert("RGBA")
R.slap(C, R.RECS[1], W / 2 + 40, 1150, 1.0, -1.5); R.slap(C, R.RECS[2], W / 2 + 40, 1575, 1.0, 1.2)
BAR.draw_bar(C, 0.0, "canal"); C.alpha_composite(R.top)
big(C, "VIRADA!", 330, 230); big(C, "LULA NA FRENTE", 560, 120, band=R.NAVY, tcol=R.WHITE); big(C, "51% x 49%", 760, 150, band=R.GOLD, tcol=R.NAVY)
for k, im in zip("ABC", (A, B, C)): im.convert("RGB").save(f"{V}/capa_{k}.jpg", quality=95)
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas_vox_ABC.jpg", quality=90); print("ok")
