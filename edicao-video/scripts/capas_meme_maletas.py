"""Capas do meme das maletas: A e B com o rosto dele, C sem rosto."""
import sys, importlib.util
S = sys.argv[1]; sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("rm", f"{S}/work/render_meme_maletas.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
from PIL import Image, ImageDraw
import numpy as np, cv2
W, H = R.W, R.H; MF = R.MF; V = R.V

def pill(img, txt, cy, size, fill, col, padx=36):
    f = MF("ExtraBold", size); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); tw = d0.textlength(txt, font=f); h = int(size * 1.7)
    lay = Image.new("RGBA", (int(tw + 2 * padx), h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, lay.width - 1, h - 1), h // 3, fill=fill); d.text((padx, h / 2 + 2), txt, font=f, fill=col, anchor="lm")
    R.paste(img, lay, W / 2 - lay.width / 2, cy - h / 2, 0.55, 16, (5, 14))
def base(img):
    img.alpha_composite(R.top); R.urgent(img, 3.0); return img
def clip_hl(u):
    return Image.fromarray(R.clip_full(u)).convert("RGBA")

A = base(Image.fromarray(R.me_src(6.6).copy()).convert("RGBA"))
pill(A, "ACABOU A ELEIÇÃO", 1330, 64, R.GD, R.NAVY + (255,)); pill(A, "PRO LULA?!", 1460, 76, R.RED + (255,), R.WH)
pill(A, "DUAS MALETAS PRETAS", 1600, 52, (4, 14, 26, 230), R.WH)
B = base(clip_hl(2.6))
me = R.me_src(6.6); face = cv2.resize(me[300:1380, 0:1080], (380, 380), interpolation=cv2.INTER_AREA)
m = Image.new("L", (380, 380), 0); ImageDraw.Draw(m).ellipse((0, 0, 379, 379), fill=255)
fc = Image.fromarray(face).convert("RGBA"); fc.putalpha(m); ring = Image.new("RGBA", (396, 396), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((0, 0, 395, 395), fill=R.GD)
R.paste(B, ring, 52, 1230, 0.5, 16, (5, 12)); B.alpha_composite(fc, (60, 1238))
pill(B, "ENCONTRADO COM LULA?!", 1690, 56, R.RED + (255,), R.WH)
C = base(clip_hl(5.6))
pill(C, "DUAS MALETAS", 1380, 70, R.GD, R.NAVY + (255,)); pill(C, "PRETAS?!", 1520, 80, R.RED + (255,), R.WH)
for k, im in zip("ABC", (A, B, C)): im.convert("RGB").save(f"{V}/capa_{k}.jpg", quality=95)
sheet = Image.new("RGB", (360 * 3, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640), Image.LANCZOS), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas_maletas_ABC.jpg", quality=90); print("ok")
