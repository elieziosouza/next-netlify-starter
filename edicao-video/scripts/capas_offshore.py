"""Capas A/B (com rosto) e C (sem rosto) do react do Flávio 'usuário master' (palavra gigante atrás da pessoa)."""
import sys, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; V = f"{S}/v19"; FD = f"{S}/fontdl"
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

me = grab(f"{V}/me.mp4", 5.33, 1080, 1920).copy(); me_s = cv2.resize(me, (478, 850), interpolation=cv2.INTER_AREA)
cl = grab(f"{S}/v17/x33.mp4", 28.6, 576, 1024).copy()        # Flávio em vídeo selfie (imagem limpa, sem título)
fl = cl[0:700]                                          # acima da legenda gravada
fl_big = cv2.resize(cl, (W, H), interpolation=cv2.INTER_CUBIC)

# A: ele com OFFSHORE gigante atrás e a frase dele
A = Image.fromarray(behind_word(me, "OFFSHORE", 215, 200, GOLD_L, me_s)).convert("RGBA")
pill(A, "PF · O GLOBO · 14/10", 1590, 38)
text_block(A, ["“A CASA TÁ CAINDO”"], 1710, [74], [WHITE])
A.convert("RGB").save(f"{V}/capa_A.jpg", quality=95)

# B: em cima o Flávio (foto do vídeo), embaixo ele
B = Image.new("RGBA", (W, H)); B.paste(Image.fromarray(cv2.resize(cl, (W, H), interpolation=cv2.INTER_CUBIC)[120:1020]), (0, 0))
band = me[60:1720]; sc = 1020 / band.shape[0]; fg = cv2.resize(band, (int(W * sc), 1020), interpolation=cv2.INTER_AREA)
bg = cv2.resize(cv2.GaussianBlur(cv2.resize(me, (135, 240)), (0, 0), 3), (W, H))[450:1470]
bot = (bg.astype(np.float32) * 0.55).astype(np.uint8); x = (W - fg.shape[1]) // 2; bot[:, x:x + fg.shape[1]] = fg
B.paste(Image.fromarray(bot), (0, 900)); ImageDraw.Draw(B).rectangle((0, 896, W, 903), fill=GOLD + (255,))
B = grad(B, 500, 900, 0.0)
text_block(B, ["USUÁRIO MASTER"], 700, [104], [GOLD_L])
pill(B, "DE CONTA DE OFFSHORE, APONTA A PF", 820, 34)
B.convert("RGB").save(f"{V}/capa_B.jpg", quality=95)

# C: sem o rosto dele — só o Flávio e a manchete
C = Image.fromarray(fl_big).convert("RGBA"); C = grad(C, 950, 1330, 0.97)
text_block(C, ["USUÁRIO", "MASTER"], 1300, [130, 130], [WHITE, GOLD_L])
pill(C, "CONTA DE OFFSHORE SÓCIA DO JATO DE VORCARO", 1580, 30)
ImageDraw.Draw(C).text((W / 2, 1650), "segundo a PF · Flávio nega", font=MF("SemiBold", 30), fill=(230, 234, 240, 255), anchor="mm")
C.convert("RGB").save(f"{V}/capa_C.jpg", quality=95)
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas_offshore_ABC.jpg", quality=90)
