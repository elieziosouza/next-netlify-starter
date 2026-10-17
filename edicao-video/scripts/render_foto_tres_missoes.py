"""Reels com a foto dele (camisa da seleção, 13, fazendo o L) e o áudio das três missões: retomar as ruas, as redes\ne os símbolos do país. Lista de missões com carimbo RETOMAMOS, tela cheia na comemoração e confete verde e amarelo."""
import sys, math, subprocess, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.path.insert(0, f"{S}/work")
import sfx, zoom_suave
from minitop import make_minitop, make_minifooter, handles_row
from segment_person import PersonSeg
V = f"{S}/v28"; FD = f"{S}/fontdl"; AU = f"{V}/au.mp4"
W, H, FPS = 1080, 1920, 30
WHITE = (255, 255, 255); GOLD = (214, 182, 116); GOLD_L = (245, 226, 176); NAVY = (6, 34, 58); RED = (210, 30, 36)
WH = (255, 255, 255, 255); GD = GOLD + (255,)
# foto dele (camisa 13, fazendo o L) + áudio do discurso das três missões (au.mp4, sem a vinheta do TikTok)
AU_END = 46.40
segs = [dict(src="me", a=0.0, b=AU_END, t0=0.0, t1=AU_END)]
EDIT_END = AU_END; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
FULL_IN = 15.0                                    # a foto sai da janela e vai para a tela cheia na comemoração
ME_CAPS = [("NÓS TÍNHAMOS TRÊS MISSÕES.", 0.44, 1.96), ("A PRIMEIRA ERA RETOMAR AS RUAS.", 3.00, 4.60), ("RETOMAMOS!", 4.60, 5.61),
           ("A SEGUNDA ERA RETOMAR AS REDES.", 6.07, 7.75), ("RETOMAMOS!", 7.93, 8.70), ("E A PARTIR DE HOJE...", 8.70, 9.77),
           ("NÓS VAMOS RETOMAR!", 10.20, 11.50), ("NÓS VAMOS RETOMAR!", 13.53, 14.63), ("OS SÍMBOLOS DESSE PAÍS", 26.20, 28.40),
           ("É NOSSO, PORQUE SOMOS O POVO BRASILEIRO", 33.40, 37.20), ("E NINGUÉM, NINGUÉM PODE...", 37.20, 39.60),
           ("QUANDO ELE SE UNE,", 40.20, 42.00), ("O VERDE-AMARELO É NOSSO!", 42.00, 44.80)]
HOT = {"MISSÕES.", "RUAS.", "RETOMAMOS!", "REDES.", "RETOMAR!", "SÍMBOLOS", "BRASILEIRO", "VERDE-AMARELO", "NOSSO!"}
def MF(w, s): return ImageFont.truetype(f"{FD}/Montserrat-{w}.ttf", s)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_in(x): x = clamp(x); return x ** 3
def ease_io(x): x = clamp(x); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
def back_out(x, s=1.7): x = clamp(x) - 1; return 1 + (s + 1) * x ** 3 + s * x ** 2
def lerp(a, b, k): return a + (b - a) * k
def fade(img, a):
    if a >= 1: return img
    img = img.copy(); img.putalpha(img.getchannel("A").point(lambda v: int(v * max(0, a)))); return img

def build_caps(lst, src, maxw, track):
    out = []
    for txt, st, en in lst:
        for s in segs:
            if s["src"] != src: continue
            a, b = max(st, s["a"]), min(en, s["b"])
            if b - a < 0.15: continue
            words = txt.split(); n = max(1, math.ceil(len(words) / maxw)); per = math.ceil(len(words) / n)
            chunks = [words[k:k + per] for k in range(0, len(words), per)]
            tot = sum(len(w) + 2 for w in words); acc_ = 0
            for ch in chunks:
                cs = st + (en - st) * acc_ / tot; ts = []
                for w in ch: ts.append(st + (en - st - 0.1) * acc_ / tot); acc_ += len(w) + 2
                ce = st + (en - st) * acc_ / tot + 0.12
                cs, ce = max(cs, s["a"]), min(ce, s["b"])
                if ce - cs < 0.1: continue
                off = s["t0"] - s["a"]
                out.append(dict(words=ch, ts=[max(x, cs) + off for x in ts], start=cs + off, end=ce + off, src=track))
    out.sort(key=lambda c: c["start"])
    for x, y in zip(out, out[1:]):
        if x["src"] == y["src"]: x["end"] = min(x["end"], y["start"])
    return out

_capcache = {}
def layout(words, font, lh, maxw):
    d = ImageDraw.Draw(Image.new("RGB", (4, 4))); sp = d.textlength(" ", font=font)
    wl = [d.textlength(w, font=font) for w in words]
    def width(a, b): return sum(wl[a:b]) + sp * (b - a - 1)
    if width(0, len(words)) <= maxw * 0.7 or len(words) < 3: lines = [(0, len(words))]
    else:
        best = min(range(1, len(words)), key=lambda k: max(width(0, k), width(k, len(words)))); lines = [(0, best), (best, len(words))]
    boxes = [None] * len(words); y0 = 230 - lh * len(lines) / 2
    for li, (a, b) in enumerate(lines):
        x = (W - width(a, b)) / 2; y = y0 + li * lh
        for k in range(a, b): boxes[k] = (x, y, x + wl[k], y + lh); x += wl[k] + sp
    return boxes

def draw_caption(frame, t, ccy, font_size, tracks):
    f = MF("ExtraBold", font_size); lh = int(font_size * 1.39)
    for ci, c in enumerate(CAPS):
        if c["src"] not in tracks or not (c["start"] <= t < c["end"]): continue
        boxes = c.setdefault(("b", font_size), layout(c["words"], f, lh, 880))
        act = max([k for k, ts in enumerate(c["ts"]) if ts <= t] or [0])
        hot = c["src"] == "au" and c["words"][act] in HOT
        key = (ci, act, font_size)
        if key not in _capcache:
            lay = Image.new("RGBA", (W, 460), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            for k, (w, bx) in enumerate(zip(c["words"], boxes)):
                if k == act: d.text((bx[0], bx[1] + 5), w, font=f, fill=WHITE if hot else NAVY)
                else: d.text((bx[0], bx[1] + 5), w, font=f, fill=WHITE, stroke_width=5, stroke_fill=NAVY)
            if len(_capcache) > 300: _capcache.clear()
            _capcache[key] = lay
        k = ease_out((t - c["ts"][act]) / 0.10)
        cur = boxes[act]; prv = boxes[act - 1] if act > 0 and boxes[act - 1][1] == cur[1] else cur
        bx = [lerp(p, q, k) for p, q in zip(prv, cur)]
        region = Image.new("RGBA", (W, 460), (0, 0, 0, 0))
        ImageDraw.Draw(region).rounded_rectangle((bx[0] - 13, bx[1] + 5, bx[2] + 13, bx[3] - 2), 13, fill=(RED + (255,)) if hot else GD)
        region.alpha_composite(_capcache[key])
        u = t - c["start"]; sc = 0.86 + 0.14 * back_out(u / 0.2); al = clamp(u / 0.06) * clamp((c["end"] - t) / 0.06)
        if abs(sc - 1) > 0.002: region = region.resize((int(W * sc), int(460 * sc)), Image.BICUBIC)
        blk = Image.new("RGBA", region.size, (0, 0, 0, 255)); blk.putalpha(region.getchannel("A").point(lambda v: int(v * 0.55)))
        sh = fade(blk.filter(ImageFilter.GaussianBlur(8)), al); region = fade(region, al)
        x = (W - region.width) // 2; y = int(ccy - region.height / 2)
        frame.alpha_composite(sh, (x + 4, y + 8)); frame.alpha_composite(region, (x, y))

def wrap(text, font, maxw):
    d = ImageDraw.Draw(Image.new("RGB", (4, 4))); lines = [""]
    for w in text.split():
        tst = (lines[-1] + " " + w).strip()
        if d.textlength(tst, font=font) <= maxw: lines[-1] = tst
        else: lines.append(w)
    return lines


# ---------------------------------------------------------------- look
x_ = np.arange(256) / 255.0
s_curve = np.clip(x_ + 0.16 * (x_ - 0.5) * (1 - abs(2 * x_ - 1)), 0, 1)
def curve(lo, hi): return np.clip((s_curve + lo * (1 - x_) ** 2.2 + hi * x_ ** 2.2) * 255, 0, 255).astype(np.uint8)
LUT = np.arange(256, dtype=np.uint8)[:, None].repeat(3, 1)[:, None, :]   # cor: grading.cinema nas fontes
yy, xx = np.mgrid[0:H, 0:W]
VIG = (1 - 0.24 * np.clip(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.45) / (H * 0.62)) ** 2, 0, 1) ** 1.3).astype(np.float32)[..., None]
_r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.36) / H) ** 2)
NAVYBG = (np.array([2, 8, 18], np.float32) + np.array([8, 34, 60], np.float32) * np.clip(1 - _r * 1.9, 0, 1)[..., None])
top, TOPH = make_minitop(W, f"{FD}/Montserrat-SemiBold.ttf")
bot, FOOT_LINE = make_minifooter(W, f"{FD}/Montserrat-SemiBold.ttf")
HROW = handles_row(W, f"{FD}/Montserrat-SemiBold.ttf", size=25, isz=28)
rng = np.random.default_rng(5)
GRAIN = [rng.normal(0, 4.0, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]


def decode(path, a, b, w, h, vf=""):
    filt = f"{vf}," if vf else ""
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-t", f"{b - a + 0.1:.3f}", "-i", path, "-vf", f"{filt}fps=30",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    n = len(p) // (w * h * 3)
    return np.frombuffer(p[:n * w * h * 3], np.uint8).reshape(n, h, w, 3)

def me_full(img, t, z=0.0):
    sc = W / 478 * (1.03 + 0.01 * math.sin(t * 0.3) + z)
    M = np.float32([[sc, 0, W / 2 - FACE[0] * sc], [0, sc, FACE[1] * W / 478 - FACE[1] * sc]])
    out = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    return cv2.LUT(out, LUT)

def me_window(img, rect):
    x0, y0, x1, y1 = rect; w, h = int(x1 - x0), int(y1 - y0)
    sc = max(w / 478, h / 850)
    small = cv2.resize(img, (int(478 * sc) + 1, int(850 * sc) + 1), interpolation=cv2.INTER_AREA)
    sy = int((small.shape[0] - h) * 0.38); sx = (small.shape[1] - w) // 2   # folga acima da cabeça
    return cv2.LUT(small[sy:sy + h, sx:sx + w], LUT).astype(np.float32), (int(x0), int(y0), w, h)


def blur_bg(img, dark=0.24, aspect_src=None):
    h, w = img.shape[:2]
    sm = cv2.GaussianBlur(cv2.resize(img, (max(8, w // 6), max(8, h // 6))), (0, 0), 4)
    sc = max(W / w, H / h); big = cv2.resize(sm, (int(w * sc) + 2, int(h * sc) + 2))
    x0 = (big.shape[1] - W) // 2; y0 = (big.shape[0] - H) // 2
    return big[y0:y0 + H, x0:x0 + W].astype(np.float32) * dark + np.array([2, 5, 10], np.float32)

def compose_me_layer(bg, me_img, t, rect, k):
    """ele em tela cheia mistura com o fundo e encolhe para a janelinha"""
    full = me_full(me_img, t).astype(np.float32)
    out = full * (1 - k) + bg * k if k < 1 else bg.copy()
    if k > 0.002:
        x0, y0, x1, y1 = [lerp(a, b, k) for a, b in zip((0, 0, W, H), rect)]
        win, (wx, wy, ww, wh) = me_window(me_img, (x0, y0, x1, y1))
        m = Image.new("L", (ww, wh), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, ww - 1, wh - 1), int(28 * k), fill=255)
        m = np.asarray(m, np.float32)[..., None] / 255 * k
        # sombra da janela
        sh = np.zeros((H, W), np.float32); cv2.rectangle(sh, (wx + 8, wy + 20), (wx + ww + 8, wy + wh + 20), 1.0, -1)
        sh = cv2.GaussianBlur(sh, (0, 0), 18)[..., None] * 0.55 * k
        out = out * (1 - sh)
        out[wy:wy + wh, wx:wx + ww] = out[wy:wy + wh, wx:wx + ww] * (1 - m) + win * m
    frame = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")
    if k > 0.002:
        ImageDraw.Draw(frame).rounded_rectangle((wx, wy, wx + ww, wy + wh), 28, outline=GOLD + (int(210 * k),), width=2)
    return frame

def persp(rgba, kind, a):
    """3D: 'top' inclina o topo para trás; 'left'/'right' gira no eixo Y (borda oposta recua)"""
    h, w = rgba.shape[:2]; src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    if kind == "top": dst = np.float32([[w * a, h * a * 0.35], [w * (1 - a), h * a * 0.35], [w, h], [0, h]])
    elif kind == "left": dst = np.float32([[0, 0], [w * (1 - a * 0.3), h * a], [w * (1 - a * 0.3), h * (1 - a)], [0, h]])
    else: dst = np.float32([[w * a * 0.3, h * a], [w, 0], [w, h], [w * a * 0.3, h * (1 - a)]])
    return cv2.warpPerspective(rgba, cv2.getPerspectiveTransform(src, dst), (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)

def mblur(img, dx, dy):
    """desfoque de movimento com alfa pré-multiplicado"""
    L = int(min(70, max(abs(dx), abs(dy)) * 1.5))
    if L < 3: return img
    a = np.asarray(img, np.float32); al = a[..., 3:4] / 255
    pm = np.concatenate([a[..., :3] * al, a[..., 3:4]], 2)
    ker = np.ones((L, 1), np.float32) / L if abs(dy) >= abs(dx) else np.ones((1, L), np.float32) / L
    pad = L
    pm = cv2.copyMakeBorder(pm, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=0)
    pm = cv2.filter2D(pm, -1, ker)
    al2 = np.clip(pm[..., 3:4], 1e-3, 255) / 255
    rgb = np.where(pm[..., 3:4] > 0.5, pm[..., :3] / al2, 0)
    return Image.fromarray(np.clip(np.concatenate([rgb, pm[..., 3:4]], 2), 0, 255).astype(np.uint8), "RGBA"), pad

def paste(frame, img, x, y, shadow=0.6, sblur=22, soff=(10, 26), vel=(0, 0)):
    pad = 0
    if max(abs(vel[0]), abs(vel[1])) > 2:
        r = mblur(img, *vel)
        if isinstance(r, tuple): img, pad = r
    if shadow > 0:
        blk = Image.new("RGBA", img.size, (0, 0, 0, 255)); blk.putalpha(img.getchannel("A").point(lambda v: int(v * shadow)))
        frame.alpha_composite(blk.filter(ImageFilter.GaussianBlur(sblur)), (int(x - pad + soff[0]), int(y - pad + soff[1])))
    frame.alpha_composite(img, (int(x - pad), int(y - pad)))

def rounded(rgb, rad=26, border=3, bcol=GOLD + (230,)):
    h, w = rgb.shape[:2]; m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), rad, fill=255)
    im = Image.fromarray(rgb).convert("RGBA"); im.putalpha(m)
    if border: ImageDraw.Draw(im).rounded_rectangle((1, 1, w - 2, h - 2), rad, outline=bcol, width=border)
    return np.asarray(im)


def credit(frame, txt, x, y, al=1.0, anchor="rm"):
    f = MF("SemiBold", 20); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); tw = d0.textlength(txt, font=f)
    lay = Image.new("RGBA", (int(tw + 28), 34), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, lay.width - 1, 33), 17, fill=(3, 10, 20, 170)); d.text((14, 17), txt, font=f, fill=(255, 255, 255, 215), anchor="lm")
    if anchor == "rm": x = x - lay.width
    elif anchor == "mm": x = x - lay.width // 2
    frame.alpha_composite(fade(lay, al), (int(x), int(y)))


def react_tag(frame, t, txt, t0, t1, y=196):
    u = t - t0
    if u < 0 or t > t1: return
    k = ease_out(u / 0.5) * (1 - ease_in((t - (t1 - 0.5)) / 0.5))
    f = MF("Bold", 26); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); tw = d0.textlength(txt, font=f)
    lay = Image.new("RGBA", (int(tw + 60), 56), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, lay.width - 1, 55), 28, fill=(4, 14, 26, 190), outline=GD, width=2)
    d.text((30, 28), txt, font=f, fill=GD, anchor="lm")
    frame.alpha_composite(fade(lay, k), (int(W / 2 - lay.width / 2), int(y + 20 * (1 - k))))


def draw_banners(frame, t):
    k = back_out((t - 0.4) / 0.55, 1.2)
    if t < 0.4: return
    frame.alpha_composite(top, (0, int(-TOPH * (1 - k)))); by = int(H - bot.height + bot.height * (1 - k))
    frame.alpha_composite(bot, (0, by))
    if t > 0.8:
        prog = clamp(t / END_IN); d = ImageDraw.Draw(frame); y = by + FOOT_LINE; x0, x1 = 120, W - 120; xp = int(x0 + (x1 - x0) * prog)
        d.rectangle((x0, y, x1, y + 2), fill=(255, 255, 255, 45)); d.rectangle((x0, y, xp, y + 2), fill=GD)
        d.ellipse((xp - 5, y - 4, xp + 5, y + 6), fill=GOLD_L + (255,))

def end_card(t):
    u = t - END_IN
    img = Image.fromarray(np.clip(NAVYBG * 1.1, 0, 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(img); cy = int(H * 0.46)
    k1 = ease_out((u - 0.15) / 0.5)
    if k1 > 0: d.text((W / 2, cy - 70 + 16 * (1 - k1)), "SIGA PARA MAIS", font=MF("ExtraBold", 50), fill=WHITE + (int(255 * k1),), anchor="mm")
    lw = int(140 * ease_out((u - 0.35) / 0.6))
    if lw > 0: d.rectangle((W / 2 - lw, cy, W / 2 + lw, cy + 2), fill=GD)
    k2 = ease_out((u - 0.5) / 0.5)
    if k2 > 0: img.alpha_composite(fade(HROW, k2), (int(W / 2 - HROW.width / 2), cy + 34))
    img.alpha_composite(bot, (0, H - bot.height))
    return img

def finish(frame, t):
    return frame.convert("RGB")                                 # sem granulação: imagem original
    a = np.asarray(frame.convert("RGB"), np.float32)
    g = cv2.resize(GRAIN[int(t * FPS) % len(GRAIN)], (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    return Image.fromarray(np.clip(a + g, 0, 255).astype(np.uint8))



CAPS = build_caps(ME_CAPS, "me", 4, "me")
for c in CAPS: c["src"] = "au" if any(w in HOT for w in c["words"]) else "me"
SEG = PersonSeg(f"{S}/seg/u2net_human_seg.onnx")
def BIGF(s): return ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s)
GREEN = (0, 132, 61); YEL = (254, 221, 0)
_p = cv2.cvtColor(cv2.imread(f"{V}/foto.png"), cv2.COLOR_BGR2RGB)
PHOTO = cv2.resize(_p, (1081, 1920), interpolation=cv2.INTER_LANCZOS4)[:, :W].copy()     # foto original, sem mexer na cor
MASK = np.clip((cv2.resize(SEG(cv2.resize(PHOTO, (478, 850), interpolation=cv2.INTER_AREA)), (W, H)) - 0.35) / 0.3, 0, 1)
ZOOMS = [(4.6, 5.6, 0.05), (7.9, 8.7, 0.05), (26.2, 28.4, 0.06), (33.4, 37.2, 0.06), (42.0, 46.4, 0.07)]
BIG = [(15.3, 21.0, "VERDE E AMARELO"), (26.2, 28.6, "SÍMBOLOS"), (33.4, 37.4, "POVO BRASILEIRO"), (42.0, 46.4, "É NOSSO!")]

def big_word(t):
    for a, b, word in BIG:
        if a <= t < b: return a, b, word
    return None
def photo_full(t):
    img = PHOTO.copy(); bw = big_word(t)
    if bw:
        a, b, word = bw; u = t - a; k = back_out(u / 0.35, 1.6); al = clamp(u / 0.12) * clamp((b - t) / 0.25)
        size = 230; f = BIGF(size); d0 = ImageDraw.Draw(Image.new("L", (4, 4)))
        while d0.textlength(word, font=f) > W - 90: size -= 6; f = BIGF(size)
        lay = Image.new("RGBA", (W, int(size * 1.4)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.text((W / 2 + 5, lay.height / 2 + 10), word, font=f, fill=(0, 0, 0, 80), anchor="mm")
        d.text((W / 2, lay.height / 2), word, font=f, fill=GREEN + (255,), anchor="mm", stroke_width=6, stroke_fill=YEL + (255,))
        L = np.asarray(lay, np.float32) / 255; sc = 0.78 + 0.22 * k
        L = cv2.resize(L, (int(L.shape[1] * sc), int(L.shape[0] * sc)), interpolation=cv2.INTER_LINEAR)
        y0 = int(300 - L.shape[0] / 2); x0 = int(W / 2 - L.shape[1] / 2); ya, yb = max(0, y0), min(H, y0 + L.shape[0]); xa, xb = max(0, x0), min(W, x0 + L.shape[1])
        Lc = L[ya - y0:yb - y0, xa - x0:xb - x0]; A = Lc[..., 3:4] * al * (1 - MASK[ya:yb, xa:xb, None])
        img[ya:yb, xa:xb] = np.clip(img[ya:yb, xa:xb].astype(np.float32) * (1 - A) + Lc[..., :3] * 255 * A, 0, 255).astype(np.uint8)
    z = 0.02 * ease_io((t - FULL_IN) / 30.0) + zoom_suave.nivel(t, ZOOMS)
    return zoom_suave.aplica(img, z, 0.40)

# --------------------------------------------------------------- lista das três missões
ROWS = [(3.00, 4.60, "RETOMAR AS RUAS"), (6.07, 7.93, "RETOMAR AS REDES"), (8.70, 13.53, "OS SÍMBOLOS DO PAÍS")]
def mission_row(i, t):
    t0, tdone, txt = ROWS[i]; q = t - t0
    w, h = 980, 118; im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    done = t >= tdone; third = i == 2
    d.rounded_rectangle((0, 0, w - 1, h - 1), 28, fill=(4, 14, 26, 232), outline=(GREEN if done and not third else GOLD) + (255,), width=3)
    d.ellipse((22, 22, 96, 96), fill=GD); d.text((59, 61), str(i + 1), font=BIGF(56), fill=NAVY + (255,), anchor="mm")
    d.text((120, 36), f"MISSÃO {i + 1}", font=MF("Bold", 24), fill=GD, anchor="lm")
    if third and not done: d.text((120, 80), "???", font=BIGF(54), fill=(255, 255, 255, 200), anchor="lm")
    else:
        k = ease_out((t - tdone) / 0.35) if third else 1.0
        d.text((120, 80), txt, font=MF("ExtraBold", 44), fill=(YEL if third else WHITE) + (int(255 * k),), anchor="lm")
    if done and not third:                                         # carimbo RETOMAMOS
        kk = back_out((t - tdone) / 0.3, 2.2); st = Image.new("RGBA", (300, 90), (0, 0, 0, 0)); ds = ImageDraw.Draw(st)
        ds.rounded_rectangle((4, 4, 296, 86), 14, outline=GREEN + (255,), width=6); ds.text((150, 46), "RETOMAMOS ✓" if False else "RETOMAMOS", font=MF("ExtraBold", 38), fill=GREEN + (255,), anchor="mm")
        st = st.rotate(-6, resample=Image.BICUBIC, expand=True); s = 1.8 - 0.8 * kk
        st = st.resize((max(1, int(st.width * s)), max(1, int(st.height * s))), Image.BICUBIC)
        im.alpha_composite(fade(st, clamp((t - tdone) / 0.06)), (int(w - 170 - st.width / 2), int(h / 2 - st.height / 2)))
    if third and done:
        pulse = 0.5 + 0.5 * math.sin((t - tdone) * 6)
        d.rounded_rectangle((w - 300, 30, w - 24, 88), 18, fill=GREEN + (int(160 + 95 * pulse),)); d.text((w - 162, 59), "AGORA É NOSSA", font=MF("ExtraBold", 26), fill=WH, anchor="mm")
    return im, q

def window_scene(t):
    k = ease_io((t - FULL_IN) / 0.6)                               # 0 = janela, 1 = tela cheia
    full = photo_full(t)
    bg = cv2.resize(cv2.GaussianBlur(cv2.resize(PHOTO, (W // 8, H // 8)), (0, 0), 3), (W, H)).astype(np.float32) * 0.35 + np.array([3, 9, 18], np.float32) * 0.65
    if k >= 0.999: return Image.fromarray(full).convert("RGBA")
    s = lerp(0.56, 1.0, k); fw, fh = int(W * s), int(H * s); fx = (W - fw) // 2; fy = int(lerp(150, 0, k))
    out = bg * (1 - k) + full.astype(np.float32) * k
    small = cv2.resize(full, (fw, fh), interpolation=cv2.INTER_AREA).astype(np.float32)
    m = Image.new("L", (fw, fh), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, fw - 1, fh - 1), int(34 * (1 - k)), fill=255); m = np.asarray(m, np.float32)[..., None] / 255
    yb = min(H, fy + fh); out[fy:yb, fx:fx + fw] = out[fy:yb, fx:fx + fw] * (1 - m[:yb - fy]) + small[:yb - fy] * m[:yb - fy]
    frame = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")
    ImageDraw.Draw(frame).rounded_rectangle((fx, fy, fx + fw, fy + fh), int(34 * (1 - k)), outline=GOLD + (int(220 * (1 - k)),), width=3)
    for i in range(3):
        im, q = mission_row(i, t)
        if q < 0: continue
        kin = ease_out(q / 0.4); al = clamp(q / 0.15) * (1 - k)
        paste(frame, fade(im, al), (W - im.width) / 2 - 500 * (1 - kin), 1250 + i * 140 + 400 * k, 0.5, 14, (4, 10))
    return frame

rng = np.random.default_rng(13)
CONF = [dict(x=rng.uniform(0, W), y0=rng.uniform(-900, -40), v=rng.uniform(260, 520), w=rng.uniform(14, 26), ph=rng.uniform(0, 6.28),
             col=[GREEN, YEL, (255, 255, 255), (0, 39, 118)][int(rng.integers(0, 4))]) for _ in range(140)]
def confetti(frame, t):
    u = t - 42.0
    if u < 0: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); al = clamp(u / 0.3)
    for c in CONF:
        y = c["y0"] + c["v"] * u
        if not (-40 < y < H + 40): continue
        x = c["x"] + 30 * math.sin(u * 2 + c["ph"]); ww = c["w"] * abs(math.cos(u * 4 + c["ph"])) + 4
        d.rectangle((x - ww / 2, y - c["w"] / 3, x + ww / 2, y + c["w"] / 3), fill=c["col"] + (int(230 * al),))
    a = np.asarray(lay).copy(); a[..., 3] = (a[..., 3] * (1 - MASK)).astype(np.uint8)          # confete passa por trás dele
    frame.alpha_composite(Image.fromarray(a, "RGBA"))

def render_frame(t):
    if t >= END_IN + 0.35: return end_card(t)
    tt = min(t, EDIT_END - 1e-3)
    frame = window_scene(tt)
    draw_caption(frame, t, 1160 if tt < FULL_IN else 1450, 52 if tt < FULL_IN else 56, ("me", "au"))
    confetti(frame, tt)
    draw_banners(frame, t)
    if t >= END_IN: frame.alpha_composite(fade(end_card(t), clamp((t - END_IN) / 0.35)))
    return frame

def readw(p):
    w = wave.open(p); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, w.getnchannels()) / 32768
    return a if a.shape[1] == 2 else np.repeat(a, 2, 1)
def writew(p, a):
    with wave.open(p, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(48000); w.writeframes((np.clip(a, -1, 1) * 32000).astype(np.int16).tobytes())

def main():
    if MODE == "lib": return
    if MODE.startswith("frames"):
        ts = [float(x) for x in MODE.split(":")[1].split(",")]
        outs = [finish(render_frame(t), t).resize((360, 640), Image.LANCZOS) for t in ts]
        sheet = Image.new("RGB", (360 * len(outs), 640)); [sheet.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]
        sheet.save(OUTFILE, quality=90); return
    vout = f"{V}/video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
    for i in range(int(round(TOTAL * FPS))): enc.stdin.write(finish(render_frame(i / FPS), i / FPS).tobytes())
    enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", AU, "-ar", "48000", "-ac", "2", f"{V}/au48.wav"], check=True)
    a = readw(f"{V}/au48.wav")[:int(AU_END * SR)]; fo = int(0.6 * SR); a[-fo:] *= np.linspace(1, 0, fo)[:, None]
    at = np.zeros((n, 2), np.float32); at[:len(a)] = a; writew(f"{V}/au_t.wav", at)
    ev = [(0.3, sfx.whoosh(0.5), 0.2)] + [(t0, sfx.whoosh(0.35), 0.22) for t0, _, _ in ROWS]
    ev += [(td, sfx.thud(), 0.3) for _, td, _ in ROWS[:2]] + [(td + 0.02, sfx.click(5), 0.45) for _, td, _ in ROWS[:2]]
    ev += [(ROWS[2][1], sfx.thud(), 0.35), (FULL_IN - 0.1, sfx.whoosh(0.6), 0.26)] + [(a_, sfx.click(), 0.45) for a_, b_, w_ in BIG]
    ev.append((END_IN - 0.3, sfx.whoosh(0.6), 0.25))
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/au_t.wav", "-i", f"{V}/sfx.wav", "-filter_complex",
                    "[1:a]highpass=f=60[au];[2:a]volume=0.7[sf];"
                    f"[au][sf]amix=inputs=2:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
