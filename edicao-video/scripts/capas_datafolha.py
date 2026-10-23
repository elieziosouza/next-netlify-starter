"""Capas do corte Datafolha (CNN, 22/10): ele analisando, mão no queixo, e a repórter da CNN."""
import sys, io, subprocess, importlib.util
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; V = f"{S}/v51"
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
ME = grab(f"{V}/in.mp4", 6.0)                                          # ele, 1080x1920
CNN = grab(f"{V}/cl.mp4", 2.0, (0, 0, 1080, 1242))
def scene(src_me, dy=40):
    img = Image.fromarray(np.zeros((H, W, 3), np.uint8)).convert("RGBA"); m = cv2.LUT(src_me, R.LUT)
    a = np.zeros((H, W, 3), np.uint8); a[:] = m[0:1].mean(axis=(0, 1)).astype(np.uint8); a[dy:] = m[:H - dy]
    img = Image.fromarray(a).convert("RGBA")
    g = np.zeros((600, W, 4), np.uint8); g[..., :3] = (4, 14, 28); g[..., 3] = np.linspace(235, 0, 600)[:, None].astype(np.uint8); img.alpha_composite(Image.fromarray(g))
    g2 = np.zeros((700, W, 4), np.uint8); g2[..., :3] = (4, 14, 28); g2[..., 3] = np.linspace(0, 235, 700)[:, None].astype(np.uint8); img.alpha_composite(Image.fromarray(g2), (0, H - 700))
    return img
def cnn_card(img, w, y, rot=-2):
    c = Image.fromarray(R.rounded(cv2.resize(cv2.LUT(CNN, R.LUT), (w, int(w * CNN.shape[0] / CNN.shape[1])), interpolation=cv2.INTER_LANCZOS4), 24, 5)).rotate(rot, resample=Image.BICUBIC, expand=True)
    R.paste(img, c, CX - c.width / 2, y, 0.65, 24, (10, 26)); return c
A = scene(ME); word(A, "EMPATOU!", 190, 210, YEL); word(A, "E AGORA, FLÁVIO?", 350, 100, WHITE, sw=9); c = cnn_card(A, 380, 1440)
word(A, "DATAFOLHA: 50% A 50%", 1400, 72, R.NAVY, band=YEL, tcol=R.NAVY, rot=-3)
finish(A, "capa_A")
B = scene(ME); word(B, "A DISTÂNCIA", 180, 150, WHITE); word(B, "SUMIU", 340, 180, YEL); c = cnn_card(B, 380, 1440, rot=2)
word(B, "FLÁVIO 50% × LULA 50%", 1400, 70, WHITE, band=BLUE, tcol=WHITE, rot=-2)
finish(B, "capa_B")
sheet = Image.new("RGB", (720, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("AB")]
sheet.save(f"{V}/capas_AB.jpg", quality=90)
