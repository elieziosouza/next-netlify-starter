"""Capas do carro com adesivo do PT atacado em Curitiba (A e B com o rosto dele, C sem rosto)."""
import sys, importlib.util
import numpy as np
S = sys.argv[1]; sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("rc", f"{S}/work/render_curitiba.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
from PIL import Image, ImageDraw
W, H = R.W, R.H; MF = R.MF; V = R.V
def pill(img, txt, cy, size, fill, col):
    f = MF("ExtraBold", size); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); tw = d0.textlength(txt, font=f); h = int(size * 1.7)
    lay = Image.new("RGBA", (int(tw + 72), h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, lay.width - 1, h - 1), h // 3, fill=fill); d.text((36, h / 2 + 2), txt, font=f, fill=col, anchor="lm")
    R.paste(img, lay, W / 2 - lay.width / 2, cy - h / 2, 0.55, 16, (5, 14))
fr = R.big_above(R.me_src(27.6).copy(), 18.5)                       # olhando para a câmera, boca fechada, fazendo o L
A = Image.fromarray(fr).convert("RGBA"); A.alpha_composite(R.top)
pill(A, "CARRO DO PT ATACADO", 1680, 62, R.GD, R.NAVY + (255,)); pill(A, "QUEBRARAM O VIDRO", 1810, 66, R.RED + (255,), R.WH)
s = R.segs[1]; B = R.split_scene(s["t0"] + 6.2, s, 0.0); B.alpha_composite(R.top)
top, kind, q = R.clip_panel(1, 6.5)
C = Image.fromarray(np.clip(R.NAVYBG * 1.1, 0, 255).astype(np.uint8)).convert("RGBA")
P = Image.fromarray(top).convert("RGBA"); R.highlight(P, 2.0); C.alpha_composite(P, (0, 330)); C.alpha_composite(R.top)
pill(C, "ATO BOLSONARISTA EM CURITIBA", 1530, 54, R.GD, R.NAVY + (255,)); pill(C, "CARRO COM ADESIVO DO PT", 1680, 62, R.RED + (255,), R.WH)
for k, im in zip("ABC", (A, B, C)): im.convert("RGB").save(f"{V}/capa_{k}.jpg", quality=95)
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas_curitiba_ABC.jpg", quality=90); print("ok")
