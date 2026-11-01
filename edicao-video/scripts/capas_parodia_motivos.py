"""Capas da paródia 'motivos para votar no Flávio' (A e B com o rosto dele, C sem rosto)."""
import sys, importlib.util
S = sys.argv[1]; sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("rm", f"{S}/work/render_parodia_motivos.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
from PIL import Image, ImageDraw
import cv2
W, H = R.W, R.H; MF = R.MF; V = R.V
def pill(img, txt, cy, size, fill, col):
    f = MF("ExtraBold", size); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); tw = d0.textlength(txt, font=f); h = int(size * 1.7)
    lay = Image.new("RGBA", (int(tw + 72), h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, lay.width - 1, h - 1), h // 3, fill=fill); d.text((36, h / 2 + 2), txt, font=f, fill=col, anchor="lm")
    R.paste(img, lay, W / 2 - lay.width / 2, cy - h / 2, 0.55, 16, (5, 14))
fr = R.me_src(5.0).copy(); fr = R.big_behind(fr, 3.5)
A = Image.fromarray(fr).convert("RGBA"); A.alpha_composite(R.top)
pill(A, "POR QUE VOTAR NO FLÁVIO?", 1330, 56, R.GD, R.NAVY + (255,)); pill(A, "ELE TENTOU EXPLICAR...", 1460, 64, R.RED + (255,), R.WH)
B = R.audio_scene(R.AU_IN + 12.0); B.alpha_composite(R.top)
face = cv2.resize(R.me_src(5.0)[260:1340, 0:1080], (300, 300), interpolation=cv2.INTER_AREA)
mm = Image.new("L", (300, 300), 0); ImageDraw.Draw(mm).ellipse((0, 0, 299, 299), fill=255)
fc = Image.fromarray(face).convert("RGBA"); fc.putalpha(mm); ring = Image.new("RGBA", (316, 316), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((0, 0, 315, 315), fill=R.GD)
R.paste(B, ring, W // 2 - 158, 1500, 0.5, 16, (5, 12)); B.alpha_composite(fc, (W // 2 - 150, 1508))
C = R.paper_scene(R.PAPER_IN + 2.4); C.alpha_composite(R.top); pill(C, "ELE NÃO SOUBE EXPLICAR", 1320, 60, R.RED + (255,), R.WH)
for k, im in zip("ABC", (A, B, C)): im.convert("RGB").save(f"{V}/capa_{k}.jpg", quality=95)
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas_motivos_ABC.jpg", quality=90); print("ok")
