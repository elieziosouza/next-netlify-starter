"""Capas do corte do deputado do PL detido após tiro em balada (Itaim Bibi). Só fatos de imprensa."""
import sys, io, subprocess, importlib.util
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; V = f"{S}/v50"
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
W, H = R.W, R.H; BAR = R.BAR; CX = R.CX; YEL = (255, 214, 0); WHITE = (255, 255, 255); BLUE = (14, 62, 120)
def grab(path, t, crop=None):
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", path, "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    a = np.asarray(Image.open(io.BytesIO(p)).convert("RGB")); return a if crop is None else a[crop[1]:crop[3], crop[0]:crop[2]]
def word(img, txt, cy, size, col, stroke=R.NAVY, sw=12, rot=0, band=None, tcol=None, maxw=720):
    f = R.BIGF(size)
    while f.getlength(txt) > maxw: size -= 4; f = R.BIGF(size)
    tw = f.getlength(txt); h = int(size * 1.25)
    lay = Image.new("RGBA", (int(tw + 90), h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if band: d.rounded_rectangle((0, 6, lay.width - 1, h + 12), 16, fill=band + (255,))
    d.text((lay.width / 2, lay.height / 2 + 4), txt, font=f, fill=(tcol or col) + (255,), anchor="mm", stroke_width=0 if band else sw, stroke_fill=stroke + (255,))
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    R.paste(img, lay, CX - lay.width / 2, cy - lay.height / 2, 0.7, 18, (6, 14))
def photo(img, src, w, x, y, rad=26):
    c = Image.fromarray(R.rounded(cv2.resize(cv2.LUT(src, R.LUT), (w, int(w * src.shape[0] / src.shape[1])), interpolation=cv2.INTER_LANCZOS4), rad, 5)); R.paste(img, c, x, y, 0.6, 22, (8, 20)); return c
def base(src, k=0.3): return Image.fromarray(np.clip(R.blur_bg(src, k), 0, 255).astype(np.uint8)).convert("RGBA")
def finish(img, name):
    BAR.draw_bar(img, 0.0, "canal"); img.alpha_composite(R.top, (R.HDX, 0)); img.convert("RGB").save(f"{V}/{name}.jpg", quality=95)
PRESO = grab(f"{V}/cl.mp4", 15.0, (0, 0, 288, 430)); PRESO = cv2.resize(PRESO, (576, 860), interpolation=cv2.INTER_CUBIC)
FRED = grab(f"{V}/cl.mp4", 20.0, (288, 0, 576, 280)); FRED = cv2.resize(FRED, (576, 560), interpolation=cv2.INTER_CUBIC)
A = base(PRESO); word(A, "DO ATO DO FLÁVIO", 210, 140, WHITE); word(A, "À DELEGACIA", 380, 190, YEL)
c = photo(A, PRESO, 560, CX - 330, 520); photo(A, FRED, 280, CX + 150, 520 + c.height - 330)
word(A, "DEPUTADO DO PL DETIDO APÓS TIRO", 520 + c.height + 90, 70, R.NAVY, band=YEL, tcol=R.NAVY, rot=-3)
word(A, "HORAS DEPOIS DO ATO NA PAULISTA", 520 + c.height + 210, 62, WHITE, sw=8)
finish(A, "capa_A")
B = base(FRED); word(B, "TIRO NA BALADA", 210, 150, WHITE); word(B, "DEPUTADO DO PL", 380, 170, YEL)
photo(B, PRESO, 460, CX - 480, 540); photo(B, FRED, 460, CX + 10, 640)
word(B, "FRED BRUNO ATINGIDO DE RASPÃO", 1330, 72, R.NAVY, band=YEL, tcol=R.NAVY, rot=-2)
word(B, "E FOI LIBERADO POR IMUNIDADE", 1470, 80, WHITE, sw=8)
finish(B, "capa_B")
sheet = Image.new("RGB", (720, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("AB")]
sheet.save(f"{V}/capas_AB.jpg", quality=90)
