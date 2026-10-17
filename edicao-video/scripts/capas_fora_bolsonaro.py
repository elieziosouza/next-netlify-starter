"""Capas do grito FORA BOLSONARO (vídeo sem o rosto dele): A e B."""
import sys, importlib.util
S = sys.argv[1]; sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("rf", f"{S}/work/render_fora_bolsonaro.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
from PIL import Image, ImageDraw
W, H = R.W, R.H; V = R.V
def pill(img, txt, cy, size, fill, col, pt=False):
    f = R.MF("ExtraBold", size); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); h = int(size * 1.7)
    if pt:
        pre = txt[:-2]; wp = d0.textlength(pre, font=f); wt = d0.textlength("PT", font=f)
        lay = Image.new("RGBA", (int(wp + wt + 110), h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.rounded_rectangle((0, 0, lay.width - 1, h - 1), h // 3, fill=fill); d.text((30, h / 2 + 2), pre, font=f, fill=col, anchor="lm")
        d.rounded_rectangle((30 + wp, 12, 30 + wp + wt + 40, h - 12), 16, fill=R.RED + (255,)); d.text((50 + wp, h / 2 + 2), "PT", font=f, fill=R.WH, anchor="lm")
    else:
        tw = d0.textlength(txt, font=f); lay = Image.new("RGBA", (int(tw + 72), h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.rounded_rectangle((0, 0, lay.width - 1, h - 1), h // 3, fill=fill); d.text((36, h / 2 + 2), txt, font=f, fill=col, anchor="lm")
    R.paste(img, lay, W / 2 - lay.width / 2, cy - h / 2, 0.55, 16, (5, 14))
def base(st):
    img = Image.fromarray(R.src_frame(st)).convert("RGBA"); img.alpha_composite(R.top); return img
A = base(10.5); A.alpha_composite(R.FORA, (0, 860 - 410)); pill(A, "O GRITO DAS JANELAS", 1420, 54, R.GD, R.NAVY + (255,))
B = base(4.6); lay = R.FORA.resize((int(W * 0.9), int(820 * 0.9))); B.alpha_composite(lay, (int(W * 0.05), 380)); pill(B, "VAI DAR PT", 1400, 90, (4, 14, 26, 235), R.WH, pt=True)
for k, im in zip("AB", (A, B)): im.convert("RGB").save(f"{V}/capa_{k}.jpg", quality=95)
sheet = Image.new("RGB", (720, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("AB")]
sheet.save(f"{V}/capas_fora_AB.jpg", quality=90); print("ok")
