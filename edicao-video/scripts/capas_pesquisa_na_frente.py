"""Capas A/B (com rosto) e C (sem rosto) da pesquisa PoderData/Aya 16/10 (empate) (palavra gigante atrás da pessoa)."""
import sys, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; V = f"{S}/v21"; FD = f"{S}/fontdl"
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

me = grab(f"{V}/me.mp4", 1.0, 1080, 1920).copy(); me_s = cv2.resize(me, (478, 850), interpolation=cv2.INTER_AREA)
def stamp(img, txt, cx, cy, size, rot=-5):
    f = MF("ExtraBold", size); tw = ImageDraw.Draw(Image.new("RGBA", (4, 4))).textlength(txt, font=f)
    st = Image.new("RGBA", (int(tw + 80), int(size * 1.55)), (0, 0, 0, 0)); d = ImageDraw.Draw(st)
    d.rounded_rectangle((8, 8, st.width - 8, st.height - 8), 20, fill=RED + (255,), outline=WHITE + (255,), width=5); d.text((st.width / 2, st.height / 2), txt, font=f, fill=WHITE, anchor="mm")
    st = st.rotate(rot, Image.BICUBIC, expand=True); img.alpha_composite(st, (int(cx - st.width / 2), int(cy - st.height / 2)))

# A: ele com VIRADA gigante atrás
A = Image.fromarray(behind_anton(me, "VIRADA", 262, 330, GOLD_L, me_s)).convert("RGBA")
A = grad(A, 1350, 1700, 0.85)
stamp(A, "50% × 50%", W / 2, 1480, 92, -3)
pill(A, "PODERDATA/AYA · 16/10 · VOTOS VÁLIDOS", 1640, 32)
A.convert("RGB").save(f"{V}/capa_A.jpg", quality=95)

# B: o quadro do vídeo (ele com o painel da pesquisa na frente)
B = Image.open(f"{V}/fB.png").convert("RGBA")
B.convert("RGB").save(f"{V}/capa_B.jpg", quality=95)

# C: sem o rosto dele — só os números
yy = np.linspace(0, 1, H)[:, None, None]
base = np.array([3, 10, 20], np.float32) + np.array([12, 40, 70], np.float32) * (1 - np.abs(yy - 0.45) * 1.6).clip(0, 1)
C = Image.fromarray(np.broadcast_to(base, (H, W, 3)).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(C)
pill(C, "PESQUISA PODERDATA/AYA · 2º TURNO", 330, 36)
text_block(C, ["LULA", "50%"], 560, [96, 210], [WHITE, GOLD_L])
d.text((W / 2, 900), "×", font=MF("ExtraBold", 110), fill=(255, 255, 255, 180), anchor="mm")
text_block(C, ["50%", "FLÁVIO"], 1080, [210, 96], [WHITE, WHITE])
stamp(C, "EMPATE", W / 2, 1495, 96, -5)
d.text((W / 2, 1655), "13/10: 49% × 51%  →  16/10: 50% × 50%", font=MF("Bold", 36), fill=GOLD_L + (255,), anchor="mm")
d.text((W / 2, 1705), "votos válidos · margem ±1,8 p.p.", font=MF("SemiBold", 30), fill=(220, 226, 236, 255), anchor="mm")
C.convert("RGB").save(f"{V}/capa_C.jpg", quality=95)
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas_pesquisa_ABC.jpg", quality=90)
