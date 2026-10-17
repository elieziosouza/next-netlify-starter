"""Capas do reels das três missões (A e B com o rosto dele, C sem rosto)."""
import sys, importlib.util
S = sys.argv[1]; sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("rmi", f"{S}/work/render_foto_tres_missoes.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
from PIL import Image, ImageDraw
import numpy as np
W, H = R.W, R.H; MF = R.MF; V = R.V
def pill(img, txt, cy, size, fill, col):
    f = MF("ExtraBold", size); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); tw = d0.textlength(txt, font=f); h = int(size * 1.7)
    lay = Image.new("RGBA", (int(tw + 72), h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, lay.width - 1, h - 1), h // 3, fill=fill); d.text((36, h / 2 + 2), txt, font=f, fill=col, anchor="lm")
    R.paste(img, lay, W / 2 - lay.width / 2, cy - h / 2, 0.55, 16, (5, 14))
R.BIG[:] = [(0, 99, "VERDE E AMARELO")]
A = Image.fromarray(R.photo_full(1.0)).convert("RGBA"); A.alpha_composite(R.top)
pill(A, "O VERDE-AMARELO", 1300, 64, R.GREEN + (255,), R.WH); pill(A, "É NOSSO!", 1430, 80, R.YEL + (255,), R.NAVY + (255,))
B = R.window_scene(14.4); B.alpha_composite(R.top)
C = Image.fromarray(np.clip(R.NAVYBG * 1.1, 0, 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(C)
d.text((W / 2, 520), "3 MISSÕES", font=R.BIGF(200), fill=R.YEL + (255,), anchor="mm")
for i in range(3):
    im, _ = R.mission_row(i, 20.0); R.paste(C, im, (W - im.width) / 2, 760 + i * 150, 0.5, 14, (4, 10))
pill(C, "O VERDE-AMARELO É NOSSO!", 1330, 58, R.GREEN + (255,), R.WH)
C.alpha_composite(R.top)
for k, im in zip("ABC", (A, B, C)): im.convert("RGB").save(f"{V}/capa_{k}.jpg", quality=95)
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas_missoes_ABC.jpg", quality=90); print("ok")
