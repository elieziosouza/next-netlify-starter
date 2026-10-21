"""Capa da série "Faltam X dias": mesmo molde todo dia, muda o número e a frase do tema (DAY e TEMA no ambiente)."""
import sys, os, io, importlib.util, subprocess, math
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; DAY = int(os.environ.get("DAY", "4")); TEMA = os.environ.get("TEMA", "LULA AUTORIZOU.|E O FLÁVIO?").split("|")
ME_T = float(os.environ.get("ME_T", "10.5")); V = os.environ.get("VDIR", f"{S}/v46")
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
W, H = R.W, R.H; BAR = R.BAR; CX = R.CX; YEL = (255, 214, 0)
p = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(ME_T), "-i", f"{V}/me.mp4", "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
ME = np.asarray(Image.open(io.BytesIO(p)).convert("RGB"))
img = Image.fromarray(np.clip(R.blur_bg(ME, 0.45), 0, 255).astype(np.uint8)).convert("RGBA")
fw = 2 * min(CX, W - CX); me = cv2.LUT(cv2.resize(ME, (fw, int(fw * ME.shape[0] / ME.shape[1]))), R.LUT)
m = np.ones((me.shape[0], fw), np.float32); m[:200] = np.linspace(0, 1, 200)[:, None]
base = np.asarray(img.convert("RGB"), np.float32); y0 = int(os.environ.get("FACE_Y0", "560"))                                           # rosto inteiro, abaixo dos textos
hh = min(H - y0, me.shape[0]); reg = base[y0:y0 + hh, CX - fw // 2:CX + fw // 2]; mm = m[:hh, :, None]; reg[:] = reg * (1 - mm) + me[:hh] * mm
img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(img)
# placa gigante com o número
pw, ph, cy = 330, 390, 420
d.rounded_rectangle((CX - pw // 2, cy - ph // 2, CX + pw // 2, cy + ph // 2), 46, fill=R.NAVY + (255,), outline=R.GOLD_L + (255,), width=10)
d.text((CX, cy + 12), str(DAY), font=R.BIGF(340), fill=YEL + (255,), anchor="mm")
d.line((CX - pw // 2 + 10, cy, CX + pw // 2 - 10, cy), fill=(0, 0, 0, 170), width=6)
lab = "FALTAM" if DAY != 1 else "FALTA"
d.text((CX, 150), lab, font=R.BIGF(120), fill=(255, 255, 255, 255), anchor="mm", stroke_width=12, stroke_fill=R.NAVY + (255,))
d.text((CX, cy + ph // 2 + 72), "DIAS" if DAY != 1 else "DIA", font=R.BIGF(120), fill=(255, 255, 255, 255), anchor="mm", stroke_width=12, stroke_fill=R.NAVY + (255,))
y = 820
for i, line in enumerate(TEMA):
    sz = 104
    while R.BIGF(sz).getlength(line) > 720: sz -= 4
    f = R.BIGF(sz); tw = f.getlength(line)
    if i == 0:
        d.rounded_rectangle((CX - tw / 2 - 34, y - sz * 0.62, CX + tw / 2 + 34, y + sz * 0.62), 18, fill=YEL + (255,))
        d.text((CX, y + 4), line, font=f, fill=R.NAVY + (255,), anchor="mm")
    else:
        d.text((CX, y + 4), line, font=f, fill=YEL + (255,), anchor="mm", stroke_width=12, stroke_fill=R.NAVY + (255,))
    y += sz * 1.3
BAR.draw_bar(img, 0.0, "canal"); img.alpha_composite(R.top, (R.HDX, 0))
img.convert("RGB").save(f"{V}/capa_dia{DAY}.jpg", quality=95)
