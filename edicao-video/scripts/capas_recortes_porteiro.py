"""Capas do porteiro preso no panelaço (A e B com o rosto dele, C sem rosto)."""
import sys, importlib.util
S = sys.argv[1]; sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("rp", f"{S}/work/render_recortes_porteiro.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
from PIL import Image, ImageDraw
W, H = R.W, R.H; MF = R.MF; V = R.V
def pill(img, txt, cy, size, fill, col):
    f = MF("ExtraBold", size); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); tw = d0.textlength(txt, font=f); h = int(size * 1.7)
    lay = Image.new("RGBA", (int(tw + 72), h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, lay.width - 1, h - 1), h // 3, fill=fill); d.text((36, h / 2 + 2), txt, font=f, fill=col, anchor="lm")
    R.paste(img, lay, W / 2 - lay.width / 2, cy - h / 2, 0.55, 16, (5, 14))
fr = R.me_src(5.6).copy(); fr = R.big_behind(fr, 5.4)
A = Image.fromarray(fr).convert("RGBA"); A.alpha_composite(R.top)
pill(A, "PORTEIRO PRESO", 1330, 64, R.GD, R.NAVY + (255,)); pill(A, "POR BATER PANELA?!", 1465, 70, R.RED + (255,), R.WH)
s = R.segs[1]; B = R.split_scene(s["t0"] + 1.6, s, 0.0); B.alpha_composite(R.top)
s3 = R.segs[3]; C = R.paper_scene(s3["t0"] + 3.4, s3); C.alpha_composite(R.top); pill(C, "LEVARAM ATÉ A PANELA", 1730, 58, R.RED + (255,), R.WH)
for k, im in zip("ABC", (A, B, C)): im.convert("RGB").save(f"{V}/capa_{k}.jpg", quality=95)
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas_porteiro_ABC.jpg", quality=90); print("ok")
