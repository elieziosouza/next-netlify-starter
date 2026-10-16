"""Capas A/B (com rosto) e C (sem rosto) do react do Lula correndo na chuva (palavra gigante atrás da pessoa)."""
import sys, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; V = f"{S}/v20"; FD = f"{S}/fontdl"
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

def ANT(s): return ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s)
def behind_anton(img_rgb, word, cy, size, col, small):
    m = SEG(small); m = cv2.resize(m, (W, H)); m = np.clip((m - 0.35) / 0.3, 0, 1)
    f = ANT(size); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    while d0.textlength(word, font=f) > W - 50: size -= 6; f = ANT(size)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text((W / 2 + 5, cy + 10), word, font=f, fill=(0, 0, 0, 140), anchor="mm"); d.text((W / 2, cy), word, font=f, fill=col + (255,), anchor="mm")
    L = np.asarray(lay, np.float32) / 255; A = L[..., 3:4] * (1 - m[..., None]); return (img_rgb * (1 - A) + L[..., :3] * 255 * A).astype(np.uint8)
def circle(img, x, y, r, lab):
    d = ImageDraw.Draw(img); d.ellipse((x - r, y - r, x + r, y + r), outline=(255, 255, 255, 130), width=16); d.ellipse((x - r, y - r, x + r, y + r), outline=RED + (255,), width=10)
    f = MF("ExtraBold", 44); tw = d.textlength(lab, font=f); lx = max(30, min(W - tw - 80, x - tw / 2 - 26)); ly = y + r + 30
    d.rounded_rectangle((lx, ly, lx + tw + 52, ly + 76), 20, fill=RED + (255,), outline=(255, 255, 255, 255), width=3); d.text((lx + 26, ly + 38), lab, font=f, fill=WHITE, anchor="lm")

me = cv2.resize(grab(f"{V}/me.mp4", 1.4, 720, 1280), (W, H), interpolation=cv2.INTER_LANCZOS4); me_s = cv2.resize(me, (478, 850), interpolation=cv2.INTER_AREA)
cl = cv2.resize(grab(f"{V}/cl.mp4", 10.3, 720, 1280), (W, H), interpolation=cv2.INTER_LANCZOS4)
mala = (897, 942)                                  # mala preta no quadro 10,3 s (1080x1920)

# A: ele com PIQUE gigante atrás
A = Image.fromarray(behind_anton(me, "PIQUE", 262, 330, GOLD_L, me_s)).convert("RGBA")
pill(A, "LULA NA CHUVA · 22H40", 1590, 38)
text_block(A, ["VOCÊS VIRAM ESSE PIQUE?"], 1710, [70], [WHITE])
A.convert("RGB").save(f"{V}/capa_A.jpg", quality=95)

# B: em cima o Lula com a mala circulada, embaixo ele
top = Image.fromarray(cl[480:1380]).convert("RGBA"); circle(top, mala[0], mala[1] - 480, 120, "A MALA PRETA")
B = Image.new("RGBA", (W, H)); B.paste(top, (0, 0))
band = me[60:1720]; sc = 1020 / band.shape[0]; fg = cv2.resize(band, (int(W * sc), 1020), interpolation=cv2.INTER_AREA)
bg = cv2.resize(cv2.GaussianBlur(cv2.resize(me, (135, 240)), (0, 0), 3), (W, H))[450:1470]
bot = (bg.astype(np.float32) * 0.55).astype(np.uint8); x = (W - fg.shape[1]) // 2; bot[:, x:x + fg.shape[1]] = fg
B.paste(Image.fromarray(bot), (0, 900)); ImageDraw.Draw(B).rectangle((0, 896, W, 903), fill=GOLD + (255,))
B = grad(B, 0, 260, 0.75, up=True); text_block(B, ["O QUE TEM NA", "MALA PRETA?"], 150, [84, 84], [WHITE, GOLD_L])
B.convert("RGB").save(f"{V}/capa_B.jpg", quality=95)

# C: sem o rosto dele — o Lula correndo, a mala circulada
C = Image.fromarray(cl).convert("RGBA"); circle(C, mala[0], mala[1], 125, "A MALA PRETA")
C = grad(C, 1180, 1560, 0.9); C2 = grad(C, 120, 520, 0.8, up=True)
text_block(C2, ["O QUE TEM NA", "MALA PRETA?"], 330, [112, 112], [WHITE, GOLD_L])
pill(C2, "LULA CORRE NA CHUVA ATÉ O AVIÃO", 1600, 34)
C2.convert("RGB").save(f"{V}/capa_C.jpg", quality=95)
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas_chuva_ABC.jpg", quality=90)
