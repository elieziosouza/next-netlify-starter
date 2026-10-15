"""Capas A/B (com rosto) e C (sem rosto) do react da prisão de Márcio Canella."""
import sys, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; V = f"{S}/v17"; FD = f"{S}/fontdl"
W, H = 1080, 1920
GOLD = (214, 182, 116); GOLD_L = (245, 226, 176); WHITE = (255, 255, 255); NAVY = (4, 16, 30)
def MF(w, s): return ImageFont.truetype(f"{FD}/Montserrat-{w}.ttf", s)
def grab(path, t, w, h):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", path, "-frames:v", "1", "-vf", f"scale={w}:{h}:flags=lanczos",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3)
def cover(img, w, h, fy=0.5):
    ih, iw = img.shape[:2]; sc = max(w / iw, h / ih); r = cv2.resize(img, (int(iw * sc) + 1, int(ih * sc) + 1), interpolation=cv2.INTER_AREA)
    y = int((r.shape[0] - h) * fy); x = (r.shape[1] - w) // 2; return r[y:y + h, x:x + w]
def grad(img, y0, y1, a=0.85, up=False):
    g = np.zeros((H, 1), np.float32); g[y0:y1, 0] = np.linspace(0, a, y1 - y0) if not up else np.linspace(a, 0, y1 - y0)
    if not up: g[y1:] = a
    else: g[:y0] = a
    arr = np.asarray(img.convert("RGB"), np.float32); arr = arr * (1 - g[..., None]) + np.array([3, 10, 20]) * g[..., None]
    return Image.fromarray(arr.astype(np.uint8)).convert("RGBA")
def text_block(img, lines, y, sizes, cols):
    d = ImageDraw.Draw(img)
    for ln, sz, col in zip(lines, sizes, cols):
        f = MF("Black" if False else "ExtraBold", sz)
        d.text((W / 2 + 5, y + 8), ln, font=f, fill=(0, 0, 0, 150), anchor="mm")
        d.text((W / 2, y), ln, font=f, fill=col, anchor="mm", stroke_width=6, stroke_fill=NAVY)
        y += int(sz * 1.12)
def pill(img, txt, y, size=40):
    d = ImageDraw.Draw(img); f = MF("ExtraBold", size); tw = d.textlength(txt, font=f)
    d.rounded_rectangle((W / 2 - tw / 2 - 30, y - size * 0.8, W / 2 + tw / 2 + 30, y + size * 0.8), int(size * 0.8), fill=GOLD + (255,))
    d.text((W / 2, y), txt, font=f, fill=NAVY, anchor="mm")
def card(rgb, w, h, rot):
    im = Image.fromarray(cover(rgb, w, h, 0.85)).convert("RGBA"); m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 28, fill=255); im.putalpha(m)
    ImageDraw.Draw(im).rounded_rectangle((1, 1, w - 2, h - 2), 28, outline=GOLD + (255,), width=6)
    return im.rotate(rot, Image.BICUBIC, expand=True)
def paste_sh(base, im, x, y):
    sh = Image.new("RGBA", im.size, (0, 0, 0, 255)); sh.putalpha(im.getchannel("A").point(lambda v: int(v * 0.6)))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)), (x + 12, y + 26)); base.alpha_composite(im, (x, y))

RED = (206, 34, 40)
def stamp(img, txt, cx, cy, size=96, rot=-5):
    f = MF("ExtraBold", size); tw = ImageDraw.Draw(Image.new("RGBA", (4, 4))).textlength(txt, font=f)
    st = Image.new("RGBA", (int(tw + 80), int(size * 1.6)), (0, 0, 0, 0)); d = ImageDraw.Draw(st)
    d.rounded_rectangle((6, 6, st.width - 6, st.height - 6), 18, fill=RED + (255,))
    d.text((st.width / 2, st.height / 2), txt, font=f, fill=WHITE, anchor="mm")
    st = st.rotate(rot, Image.BICUBIC, expand=True); paste_sh(img, st, int(cx - st.width / 2), int(cy - st.height / 2))

me = grab(f"{V}/x34.mp4", 3.0, 1080, 1920)
sf = grab(f"{V}/x33.mp4", 8.73, 1080, 1920).copy()
reg = sf[1360:1560].copy(); msk = np.all(reg > 200, axis=2).astype(np.uint8) * 255
msk = cv2.dilate(msk, np.ones((17, 17), np.uint8)); sf[1360:1560] = cv2.inpaint(reg, msk, 9, cv2.INPAINT_TELEA)   # tira a legenda gravada

# A: em cima a foto dos dois, embaixo ele (rosto inteiro)
A = Image.new("RGBA", (W, H)); A.paste(Image.fromarray(cover(sf, W, 900, 0.15)), (0, 0))
band = me[60:1720]; sc = 1020 / band.shape[0]; fg = cv2.resize(band, (int(W * sc), 1020), interpolation=cv2.INTER_AREA)
bg = cv2.resize(cv2.GaussianBlur(cv2.resize(me, (135, 240)), (0, 0), 3), (W, H))[450:1470]
bot = (bg.astype(np.float32) * 0.55).astype(np.uint8); x = (W - fg.shape[1]) // 2; bot[:, x:x + fg.shape[1]] = fg
A.paste(Image.fromarray(bot), (0, 900)); ImageDraw.Draw(A).rectangle((0, 896, W, 903), fill=GOLD + (255,))
A = grad(A, 520, 900, 0.0)
text_block(A, ["O AMIGO", "DO FLÁVIO"], 600, [112, 112], [WHITE, GOLD_L])
stamp(A, "PRESO HOJE", W / 2, 380, 84)
A.convert("RGB").save(f"{V}/capa_A.jpg", quality=95)

# B: ele inteiro com moldura, frase dele em cima
yy = np.linspace(0, 1, H)[:, None, None]
base = np.array([3, 10, 20], np.float32) + np.array([10, 34, 60], np.float32) * (1 - yy) ** 1.5
B = Image.fromarray(np.broadcast_to(base, (H, W, 3)).astype(np.uint8)).convert("RGBA")
sc = 0.74; mw, mh = int(W * sc), int(H * sc); mi = Image.fromarray(cv2.resize(me, (mw, mh), interpolation=cv2.INTER_AREA)).convert("RGBA")
m = Image.new("L", (mw, mh), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, mw - 1, mh - 1), 34, fill=255); mi.putalpha(m)
ImageDraw.Draw(mi).rounded_rectangle((1, 1, mw - 2, mh - 2), 34, outline=GOLD + (255,), width=5)
paste_sh(B, mi, (W - mw) // 2, H - mh - 40)
text_block(B, ["“TUDO NO ENTORNO", "DESSE CARA FEDE”"], 250, [78, 78], [WHITE, GOLD_L])
stamp(B, "PRESO PELA PF", W / 2, 1640, 58, -3)
B.convert("RGB").save(f"{V}/capa_B.jpg", quality=95)

# C: sem rosto dele — a foto dos dois, carimbo e valor
C = Image.fromarray(cover(sf, W, H, 0.0)).convert("RGBA"); C = grad(C, 1000, 1500, 0.9)
stamp(C, "PRESO PELA PF", W / 2, 1180, 92)
text_block(C, ["O AMIGO", "DO FLÁVIO"], 1370, [112, 112], [WHITE, GOLD_L])
pill(C, "ESQUEMA DE R$ 7,6 BI, SEGUNDO A PF", 1620, 36)
C.convert("RGB").save(f"{V}/capa_C.jpg", quality=95)
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas_canella_ABC.jpg", quality=90)
