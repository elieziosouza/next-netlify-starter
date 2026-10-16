"""Capas do esquete 'momento André Janones': A e B com o rosto dele, C sem rosto."""
import sys, importlib.util
S = sys.argv[1]; sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("rj", f"{S}/work/render_esquete_live.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
from PIL import Image, ImageDraw
import numpy as np
W, H = R.W, R.H; MF = R.MF; V = R.V

def pill(img, txt, cy, size, fill, col, padx=36, h=None):
    f = MF("ExtraBold", size); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); tw = d0.textlength(txt, font=f); h = h or int(size * 1.7)
    lay = Image.new("RGBA", (int(tw + 2 * padx), h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, lay.width - 1, h - 1), h // 3, fill=fill); d.text((padx, h / 2 + 2), txt, font=f, fill=col, anchor="lm")
    R.paste(img, lay, W / 2 - lay.width / 2, cy - h / 2, 0.55, 16, (5, 14))

def badge(img, t, y=178):
    R.live_badge(img, t + 2.0)   # sem animação de entrada
def with_me(st, word, n_t, l1, l2):
    fr = R.me_frame(st).copy(); R.BIG[:] = [(0, 99, word)]; fr = R.big_behind(fr, 1.0)
    img = Image.fromarray(fr).convert("RGBA"); img.alpha_composite(R.top)
    R.STEPS[:] = R.STEPS; R.live_badge(img, n_t)
    pill(img, l1, 1380, 66, R.GD, R.NAVY + (255,)); pill(img, l2, 1520, 66, R.RED + (255,), R.WH)
    return img
A = with_me(4.4, "MAIS GENTE!", 7.0, "EU QUERO", "10 MILHÕES!")
B = with_me(0.3, "EXÉRCITO", 0.9, "QUANDO 3 MILHÕES", "É POUCO...")
A.convert("RGB").save(f"{V}/capa_A.jpg", quality=95); B.convert("RGB").save(f"{V}/capa_B.jpg", quality=95)
# C sem rosto
C = Image.fromarray(np.clip(R.NAVYBG * 1.1, 0, 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(C)
pill(C, "•  AO VIVO", 370, 54, R.RED + (255,), R.WH)
d.text((W / 2, 500), "EXÉRCITO DO LULA", font=MF("ExtraBold", 70), fill=R.WH, anchor="mm")
d.text((W / 2, 640), "PARTICIPANTES NO GRUPO DE WHATSAPP", font=MF("Bold", 40), fill=(255, 255, 255, 170), anchor="mm")
d.text((W / 2, 760), "3.000.000", font=R.BIGF(150), fill=(255, 255, 255, 200), anchor="mm")
d.text((W / 2, 900), "↓", font=MF("ExtraBold", 90), fill=R.GD, anchor="mm")
d.text((W / 2, 1060), "10.000.000", font=R.BIGF(210), fill=R.GD, anchor="mm")
pill(C, "\"CHAMA MAIS GENTE!\"", 1300, 64, R.WH, R.NAVY + (255,))
d.text((W / 2, 1430), "bora encher o grupo!", font=MF("SemiBold", 38), fill=(255, 255, 255, 200), anchor="mm")
C.alpha_composite(R.top); C.convert("RGB").save(f"{V}/capa_C.jpg", quality=95)
sheet = Image.new("RGB", (360 * 3, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640), Image.LANCZOS), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas_janones_ABC.jpg", quality=90); print("ok")
