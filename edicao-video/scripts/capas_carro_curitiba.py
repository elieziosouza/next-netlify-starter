"""Capas chamativas do carro com adesivo do PT atacado em Curitiba (A e B com o rosto dele, C sem rosto), letras grandes."""
import sys, importlib.util
import numpy as np, cv2
S = sys.argv[1]; sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("rc", f"{S}/work/render_curitiba.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
from PIL import Image, ImageDraw
W, H = R.W, R.H; MF = R.MF; V = R.V; YEL = (255, 212, 0)
def big(img, txt, cy, size, col=YEL, band=None, rot=0, maxw=W - 60):
    f = R.BIGF(size); d0 = ImageDraw.Draw(Image.new("L", (4, 4)))
    while d0.textlength(txt, font=f) > maxw - 60: size -= 4; f = R.BIGF(size)
    tw = d0.textlength(txt, font=f); h = int(size * 1.32)
    lay = Image.new("RGBA", (int(tw + 90), h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if band: d.rounded_rectangle((0, 0, lay.width - 1, h - 1), 18, fill=band + (255,), outline=(255, 255, 255, 255), width=5)
    d.text((lay.width / 2, h / 2 + 4), txt, font=f, fill=col + (255,), anchor="mm", stroke_width=0 if band else 9, stroke_fill=(0, 0, 0, 255))
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    R.paste(img, lay, W / 2 - lay.width / 2, cy - lay.height / 2, 0.7, 18, (6, 14))
def panel(si, u, tgt, lab):
    top, kind, q = R.clip_panel(si, u); P = Image.fromarray(top).convert("RGBA")
    R.highlight(P, 2.0, tgt, lab); return P
ATKP = panel(0, 3.6, (R.ATK[0], R.ATK[1], R.ATK[2], R.ATK[2] + 30), "ATACANDO O CARRO")
WINP = panel(1, 5.3, None, "VIDRO TRASEIRO QUEBRADO")
me = R.me_src(27.6).copy()                                          # olhando para a câmera, boca fechada, fazendo o L

# A: manchete no topo, ataque no meio, ele embaixo
A = Image.fromarray(np.clip(R.NAVYBG, 0, 255).astype(np.uint8)).convert("RGBA")
A.alpha_composite(ATKP.crop((0, 200, W, 820)), (0, 450))
win = panel(1, 5.3, None, "VIDRO QUEBRADO").crop((140, 290, 940, 870)).resize((440, 319)); m = Image.new("L", win.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, 439, 318), 22, fill=255); win.putalpha(m)
ImageDraw.Draw(win).rounded_rectangle((1, 1, 438, 317), 22, outline=R.RED + (255,), width=8)
A.alpha_composite(Image.fromarray(R.me_panel(me)).convert("RGBA"), (0, 1060)); ImageDraw.Draw(A).rectangle((0, 1056, W, 1062), fill=R.GD)
R.paste(A, win.rotate(4, resample=Image.BICUBIC, expand=True), W - 480, 760, 0.7, 18, (8, 16))
big(A, "QUEBRARAM O CARRO", 230, 170); big(A, "SÓ POR CAUSA DO PT!", 390, 120, (255, 255, 255), R.RED, -2)
A.alpha_composite(R.top)

# B: ele em tela cheia com BOLSONARISTAS atrás da cabeça e manchete embaixo
fb = R.big_behind(me.copy(), 18.6)
B = Image.fromarray(fb).convert("RGBA"); B.alpha_composite(R.top)
big(B, "ATACARAM CARRO DO PT", 1665, 130); big(B, "VIDRO QUEBRADO!", 1820, 110, (255, 255, 255), R.RED, -2)

# C: sem rosto, ataque em cima, vidro embaixo, faixa no meio
C = Image.new("RGBA", (W, H), (0, 0, 0, 255))
C.alpha_composite(ATKP.crop((0, 100, W, 1060)), (0, 0)); C.alpha_composite(WINP.crop((0, 140, W, 1060)), (0, 1000))
ImageDraw.Draw(C).rectangle((0, 990, W, 1004), fill=R.RED + (255,))
C.alpha_composite(R.top)
big(C, "ÓDIO NAS RUAS", 905, 150); big(C, "CARRO DO PT ATACADO", 1075, 104, (255, 255, 255), R.RED, -2)

for k, im in zip("ABC", (A, B, C)): im.convert("RGB").save(f"{V}/capa2_{k}.jpg", quality=95)
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/capa2_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas2_curitiba_ABC.jpg", quality=90); print("ok")
