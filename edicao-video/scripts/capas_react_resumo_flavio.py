"""Capas com o Flávio recortado (pedido de 17/10/2026): D só com ele, E com ele e o Eliezio num círculo."""
import sys, importlib.util
S = sys.argv[1]; sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("rr", f"{S}/work/render_react_resumo_entrevista.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
from PIL import Image, ImageDraw, ImageFilter
import numpy as np, cv2
W, H = R.W, R.H; MF = R.MF; V = R.V
def pill(img, txt, cy, size, fill, col):
    f = MF("ExtraBold", size); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); tw = d0.textlength(txt, font=f); h = int(size * 1.7)
    lay = Image.new("RGBA", (int(tw + 72), h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, lay.width - 1, h - 1), h // 3, fill=fill); d.text((36, h / 2 + 2), txt, font=f, fill=col, anchor="lm")
    R.paste(img, lay, W / 2 - lay.width / 2, cy - h / 2, 0.55, 16, (5, 14))
band = R.clip_frame(3.0)[R.BAND[0]:R.BAND[1]]                     # Flávio de frente, apontando
crop = band[0:607, 180:900]                                          # 720x607 em volta dele
sc = 1.55; big = cv2.resize(crop, (int(720 * sc), int(607 * sc)), interpolation=cv2.INTER_LANCZOS4)
m = R.SEG(cv2.resize(big, (478, 403))); m = cv2.resize(m, (big.shape[1], big.shape[0]))
m = np.clip((m - 0.3) / 0.35, 0, 1); m = cv2.GaussianBlur(m, (0, 0), 1.5)
fl = Image.fromarray(np.dstack([big, (m * 255).astype(np.uint8)]), "RGBA")
def base():
    bg = np.clip(R.NAVYBG * 1.15, 0, 255).astype(np.uint8); img = Image.fromarray(bg).convert("RGBA")
    d = ImageDraw.Draw(img); f = R.BIGF(330); txt = "RESUMO"
    d.text((W / 2 + 6, 560 + 12), txt, font=f, fill=(0, 0, 0, 120), anchor="mm"); d.text((W / 2, 560), txt, font=f, fill=R.GOLD_L + (255,), anchor="mm")
    return img
def put_flavio(img, y):
    glow = Image.new("RGBA", fl.size, (0, 0, 0, 0)); glow.putalpha(fl.getchannel("A").filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.6)))
    x = (W - fl.width) // 2; img.alpha_composite(glow, (x + 8, y + 18)); img.alpha_composite(fl, (x, y))
D = base(); put_flavio(D, 420); D.alpha_composite(R.top)
R.counter(D, 8.6, 1380); pill(D, "SÓ FALOU DO LULA", 1530, 76, R.RED + (255,), R.WH)
E = base(); put_flavio(E, 420); E.alpha_composite(R.top)
me = R.me_src(2.6); face = cv2.resize(me[260:1340, 0:1080], (340, 340), interpolation=cv2.INTER_AREA)
mm = Image.new("L", (340, 340), 0); ImageDraw.Draw(mm).ellipse((0, 0, 339, 339), fill=255)
fc = Image.fromarray(face).convert("RGBA"); fc.putalpha(mm); ring = Image.new("RGBA", (356, 356), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((0, 0, 355, 355), fill=R.GD)
R.paste(E, ring, 40, 1000, 0.5, 16, (5, 12)); E.alpha_composite(fc, (48, 1008))
R.counter(E, 8.6, 1420); pill(E, "SÓ FALOU DO LULA", 1570, 76, R.RED + (255,), R.WH)
for k, im in zip("DE", (D, E)): im.convert("RGB").save(f"{V}/capa_{k}.jpg", quality=95)
sheet = Image.new("RGB", (720, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("DE")]
sheet.save(f"{V}/capas_flavio_DE.jpg", quality=90); print("ok")
