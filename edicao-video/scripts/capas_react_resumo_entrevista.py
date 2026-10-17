"""Capas do react 'resumo da entrevista do Flávio' (A e B com o rosto dele, C sem rosto)."""
import sys, importlib.util
S = sys.argv[1]; sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("rr", f"{S}/work/render_react_resumo_entrevista.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
from PIL import Image, ImageDraw
W, H = R.W, R.H; MF = R.MF; V = R.V
def pill(img, txt, cy, size, fill, col):
    f = MF("ExtraBold", size); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); tw = d0.textlength(txt, font=f); h = int(size * 1.7)
    lay = Image.new("RGBA", (int(tw + 72), h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, lay.width - 1, h - 1), h // 3, fill=fill); d.text((36, h / 2 + 2), txt, font=f, fill=col, anchor="lm")
    R.paste(img, lay, W / 2 - lay.width / 2, cy - h / 2, 0.55, 16, (5, 14))
fr = R.me_src(2.6).copy(); R.BIG[:] = [(0, 99, "RESUMO")]; fr = R.big_behind(fr, 1.0)
A = Image.fromarray(fr).convert("RGBA"); A.alpha_composite(R.top)
pill(A, "FLÁVIO NA GLOBO", 1330, 62, R.GD, R.NAVY + (255,)); pill(A, "SÓ FALOU DO LULA", 1470, 72, R.RED + (255,), R.WH)
B = R.clip_scene(R.CL_IN + 8.5); B.alpha_composite(R.top)
keep = list(R.LULAS); R.LULAS[:] = []
C = R.clip_scene(R.CL_IN + 1.9); C.alpha_composite(R.top)
R.LULAS[:] = keep; R.counter(C, 8.6, 1300)
pill(C, "SÓ FALOU DO LULA", 1470, 72, R.RED + (255,), R.WH)
for k, im in zip("ABC", (A, B, C)): im.convert("RGB").save(f"{V}/capa_{k}.jpg", quality=95)
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas_resumo_ABC.jpg", quality=90); print("ok")
