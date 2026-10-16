"""Capas A/B (com rosto) e C (sem rosto) do corte do Dia do Professor (palavra gigante atrás da pessoa)."""
import sys, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; V = f"{S}/v18"; FD = f"{S}/fontdl"
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

sys.path.insert(0, f"{S}/work")
from segment_person import PersonSeg
SEG = PersonSeg(f"{S}/seg/u2net_human_seg.onnx"); RED = (206, 34, 40)
def behind_word(img_rgb, word, cy, size, col, src_small=None):
    m = SEG(src_small if src_small is not None else img_rgb); m = cv2.resize(m, (W, H)); m = np.clip((m - 0.35) / 0.3, 0, 1)
    f = MF("ExtraBold", size); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    while d0.textlength(word, font=f) > W - 40: size -= 6; f = MF("ExtraBold", size)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text((W / 2 + 5, cy + 10), word, font=f, fill=(0, 0, 0, 140), anchor="mm"); d.text((W / 2, cy), word, font=f, fill=col + (255,), anchor="mm")
    L = np.asarray(lay, np.float32) / 255; A = L[..., 3:4] * (1 - m[..., None])
    return (img_rgb * (1 - A) + L[..., :3] * 255 * A).astype(np.uint8)

me_s = grab(f"{V}/x36.mp4", 3.2, 478, 850); me = cv2.resize(me_s, (W, H), interpolation=cv2.INTER_LANCZOS4)
def nocap(a):
    """apaga a legenda branca gravada no meio do vídeo"""
    a = a.copy(); y0, y1 = int(a.shape[0] * 0.52), int(a.shape[0] * 0.70); reg = a[y0:y1].astype(np.int16)
    white = ((reg.min(2) > 215) & (reg.max(2) - reg.min(2) < 30)).astype(np.uint8)
    dark = cv2.dilate((reg.max(2) < 120).astype(np.uint8), np.ones((9, 9), np.uint8))
    m = (white & dark).astype(np.uint8) * 255; m = cv2.dilate(m, np.ones((7, 7), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 25), np.uint8)); a[y0:y1] = cv2.inpaint(a[y0:y1], m, 5, cv2.INPAINT_TELEA); return a
sp_s = nocap(grab(f"{V}/x37.mp4", 131.0, 478, 850)); sp = cv2.resize(sp_s, (W, H), interpolation=cv2.INTER_LANCZOS4)
sp2_s = nocap(grab(f"{V}/x37.mp4", 15.5, 478, 850)); sp2 = cv2.resize(sp2_s, (W, H), interpolation=cv2.INTER_LANCZOS4)

# A: ele com EDUCAÇÃO gigante atrás + chamada embaixo
A = Image.fromarray(behind_word(me, "EDUCAÇÃO", 250, 200, GOLD_L, me_s)).convert("RGBA")
pill(A, "15/10 · DIA DO PROFESSOR", 1590, 38)
text_block(A, ["O ALERTA DE UM PROFESSOR"], 1710, [66], [WHITE])
A.convert("RGB").save(f"{V}/capa_A.jpg", quality=95)

# B: em cima o professor falando, embaixo ele; frase do vídeo como pergunta
B = Image.new("RGBA", (W, H)); B.paste(Image.fromarray(cover(sp, W, 900, 0.30)), (0, 0))
band = me[60:1720]; sc = 1020 / band.shape[0]; fg = cv2.resize(band, (int(W * sc), 1020), interpolation=cv2.INTER_AREA)
bg = cv2.resize(cv2.GaussianBlur(cv2.resize(me, (135, 240)), (0, 0), 3), (W, H))[450:1470]
bot = (bg.astype(np.float32) * 0.55).astype(np.uint8); x = (W - fg.shape[1]) // 2; bot[:, x:x + fg.shape[1]] = fg
B.paste(Image.fromarray(bot), (0, 900)); ImageDraw.Draw(B).rectangle((0, 896, W, 903), fill=GOLD + (255,))
B = grad(B, 450, 900, 0.0)
text_block(B, ["SE O FLÁVIO GANHA,", "A EDUCAÇÃO PERDE?"], 640, [84, 84], [WHITE, GOLD_L])
B.convert("RGB").save(f"{V}/capa_B.jpg", quality=95)

# C: sem o rosto dele — o professor com ESCOLA PÚBLICA atrás
C = Image.fromarray(behind_word(sp2, "ESCOLA PÚBLICA", 520, 150, WHITE, sp2_s)).convert("RGBA")
C = grad(C, 1150, 1500, 0.88)
pill(C, "DIA DO PROFESSOR", 1300, 40)
text_block(C, ["SE O FLÁVIO GANHA,", "A EDUCAÇÃO PERDE?"], 1450, [84, 84], [WHITE, GOLD_L])
C.convert("RGB").save(f"{V}/capa_C.jpg", quality=95)
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas_professor_ABC.jpg", quality=90)
