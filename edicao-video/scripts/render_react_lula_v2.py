"""React: Eliezio x reels do Lula na Paulista, v2. Reels roda inteiro; tela dividida quando ele fala (reels em cima, ele embaixo); só trechos dele olhando para a câmera."""
import sys, math, subprocess, json, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.path.insert(0, f"{S}/work")
import sfx, grading
from minitop import make_minitop, make_minifooter, handles_row
GRADE = grading.Fast(grading.cinema, f"{S}/grade/lut_cinema.npy", 0.08, 6)     # só no reels

V = f"{S}/v11"; FD = f"{S}/fontdl"
ME, CL = f"{V}/me.mp4", f"{V}/lula.mp4"
W, H, FPS = 1080, 1920, 30
WHITE = (255, 255, 255); GOLD = (214, 182, 116); GOLD_L = (245, 226, 176); NAVY = (6, 34, 58); RED = (200, 38, 38)
WH = (255, 255, 255, 255); GD = GOLD + (255,)
HOT = set()

REEL_IN = 2.80                               # o reels começa aqui e roda inteiro (0 → 40,05 s)
REEL_LEN = 39.55                             # o reels termina num quadro preto: para antes
REEL_OUT = REEL_IN + REEL_LEN
# falas dele (fonte, só olhando para a câmera) → onde entram na saída
ME_PARTS = [  # (me_a, me_b, out_t0, modo)  modo: full = tela cheia, split = tela dividida
    (0.45, 3.25, 0.0, "full"),
    (5.90, 8.90, 4.20, "split"),             # "olha o pique do véio" (Lula andando)
    (18.10, 23.35, 7.20, "split"),           # "o cara é parada dura... andando no meio do povo"
    (25.50, 27.00, 12.45, "split"),          # "olha o povo junto" (multidão)
    (29.85, 31.70, REEL_OUT - 1.85, "split"),  # "pode falar o que quiser dele" (punho do Lula)
    (31.70, 36.90, REEL_OUT, "full"),        # "mas dia 25 vai ser histórico"
]
segs = [dict(src="me", a=a, b=b, t0=t0, t1=t0 + (b - a), mode=m) for a, b, t0, m in ME_PARTS]
EDIT_END = segs[-1]["t1"]; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
def me_seg(t):
    for s in segs:
        if s["t0"] <= t < s["t1"]: return s
    return None
def out_t(x):
    for s in segs:
        if s["a"] <= x <= s["b"]: return s["t0"] + x - s["a"]
    raise ValueError(x)
SPLITS = []                                   # blocos contínuos de tela dividida
for s in segs:
    if s["mode"] != "split": continue
    if SPLITS and abs(SPLITS[-1][1] - s["t0"]) < 0.05: SPLITS[-1][1] = s["t1"]
    else: SPLITS.append([s["t0"], s["t1"]])

ME_CAPS = [("PODE FALAR O QUE QUISER DO LULA", 0.66, 2.0), ("MAS OLHA ISSO AQUI", 2.0, 3.08),
           ("OLHA O PIQUE DO VÉIO!", 6.10, 7.30),
           ("O CARA É PARADA DURA", 18.26, 19.55), ("APANHA HÁ MUITOS ANOS, MAS CONTINUA DE PÉ", 19.55, 21.48),
           ("OLHA ELE AÍ ANDANDO NO MEIO DO POVO", 21.62, 23.21), ("OLHA O POVO JUNTO", 25.75, 26.73),
           ("PODE FALAR O QUE QUISER DELE", 29.98, 31.62), ("MAS DIA 25", 31.83, 33.29), ("VAI SER HISTÓRICO", 34.10, 35.14)]
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


CAPS = build_caps(ME_CAPS, "me", 5, "me")
top, TOPH = make_minitop(W, f"{FD}/Montserrat-SemiBold.ttf")
FACE = (239.0, 390.0)
SEAM = 840
PANEL_Y = 400                                   # recorte do quadro cheio dele usado na metade de baixo (cabeça ao peito)

def split_k(t):
    """0 = reels em tela cheia, 1 = tela dividida"""
    k = 0.0
    for a, b in SPLITS:
        if a - 0.5 <= t < b + 0.5:
            k = max(k, ease_io((t - (a - 0.25)) / 0.5) * (1 - ease_io((t - (b - 0.25)) / 0.5)) if b < REEL_OUT - 0.1 else ease_io((t - (a - 0.25)) / 0.5))
    return k

REEL = None
def reel_frame(rt):
    global REEL
    if REEL is None:
        REEL = np.stack([GRADE(f) for f in decode(CL, 0, REEL_LEN, 720, 1280)])
    return REEL[int(clamp(rt * FPS, 0, len(REEL) - 1))]

def cover_crop(img, w, h, fy=0.5):
    ih, iw = img.shape[:2]; sc = max(w / iw, h / ih)
    cw, ch = w / sc, h / sc; x0 = (iw - cw) / 2; y0 = (ih - ch) * fy
    M = np.float32([[sc, 0, -x0 * sc], [0, sc, -y0 * sc]])
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def me_panel(img, h, t):
    """ele na parte de baixo = recorte do próprio quadro em tela cheia (cabeça inteira, boca e peito)"""
    full = me_full(img, t); y0 = PANEL_Y
    return full[y0:y0 + h] if y0 + h <= H else np.vstack([full[y0:], np.zeros((y0 + h - H, W, 3), np.uint8)])

def badge(frame, t, t0, t1, big, small, y, xr):
    if not (t0 <= t < t1): return
    q = t - t0; kk = back_out(q / 0.45, 2.2); al = clamp(q / 0.12) * (1 - smooth((t - (t1 - 0.3)) / 0.3))
    f = MF("ExtraBold", 84 if len(big) <= 8 else 62); tw = ImageDraw.Draw(Image.new("RGBA", (4, 4))).textlength(big, font=f); bw = int(max(460, tw + 80))
    lay = Image.new("RGBA", (bw + 20, 210), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((10, 10, bw + 10, 200), 26, fill=(5, 16, 30, 230), outline=GD, width=3)
    d.text((bw / 2 + 10, 84), big, font=f, fill=GOLD_L + (255,), anchor="mm")
    d.text((bw / 2 + 10, 160), small, font=MF("SemiBold", 27), fill=(230, 234, 240, 255), anchor="mm")
    lay = lay.rotate(-4 + 4 * (1 - kk), Image.BICUBIC, expand=True)
    sc = 0.6 + 0.4 * kk; lay = lay.resize((max(1, int(lay.width * sc)), max(1, int(lay.height * sc))), Image.BICUBIC)
    paste(frame, fade(lay, al), xr - lay.width, y - lay.height, 0.5, 16, (6, 16))

BADGES = [(out_t(6.30), out_t(8.85), "80 ANOS", "faz 81 no dia 27/10"),
          (out_t(18.35), out_t(21.50), "PARADA DURA", "e continua de pé")]

def reel_layer(t):
    """reels com som e imagem contínuos; em tela cheia ou na metade de cima"""
    rt = t - REEL_IN; img = reel_frame(rt); k = split_k(t)
    h = int(lerp(H, SEAM, k)); fy = lerp(0.5, 0.55, k)
    return cover_crop(img, W, h, fy), h

GLASS_DIA = (max(out_t(31.83), REEL_OUT + 0.65), EDIT_END)
CARD_X, CARD_Y, CARD_W, CARD_H = 90, 168, 900, 262
def draw_dia25(frame, t):
    a, b = GLASS_DIA
    if not (a <= t < b): return
    u = t - a; dur = b - a; kin = ease_out(u / 0.6); kout = ease_in((u - (dur - 0.4)) / 0.4)
    base = np.asarray(frame.convert("RGB"))[CARD_Y:CARD_Y + CARD_H, CARD_X:CARD_X + CARD_W].astype(np.float32)
    glass = cv2.GaussianBlur(base, (0, 0), 16) * 0.42 + np.array([4, 14, 28], np.float32) * 0.58
    gl = Image.fromarray(np.clip(glass, 0, 255).astype(np.uint8)).convert("RGBA")
    m = Image.new("L", (CARD_W, CARD_H), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, CARD_W - 1, CARD_H - 1), 26, fill=255); gl.putalpha(m)
    d = ImageDraw.Draw(gl); d.rounded_rectangle((1, 1, CARD_W - 2, CARD_H - 2), 26, outline=GOLD + (210,), width=2)
    d.text((CARD_W / 2, 50), "SEGUNDO TURNO", font=MF("Bold", 26), fill=GD, anchor="mm")
    kk = back_out((u - 0.15) / 0.5, 1.4); d.text((CARD_W / 2, 142), "DIA 25", font=MF("ExtraBold", int(118 * (0.7 + 0.3 * kk))), fill=GOLD_L + (255,), anchor="mm")
    lw = int(150 * ease_out((u - 0.5) / 0.6)); d.rectangle((CARD_W / 2 - lw, 212, CARD_W / 2 + lw, 214), fill=GD)
    tilt = clamp((1 - kin) + kout)
    arr = persp(np.asarray(gl), "top", 0.05 + 0.4 * tilt) if tilt > 0.003 else np.asarray(gl)
    paste(frame, fade(Image.fromarray(arr, "RGBA"), clamp(kin * 1.6) * (1 - kout)), CARD_X, CARD_Y + 60 * (1 - kin), 0.55, 20, (8, 20))

_mecache = {}
def me_frame(s, t):
    key = s["a"]
    if key not in _mecache:
        _mecache.clear(); _mecache[key] = decode(ME, s["a"], s["b"], 478, 850)
    fr = _mecache[key]; return fr[min(len(fr) - 1, int((t - s["t0"]) * FPS))]

_last_me = [None]
def render_frame(t):
    if t >= END_IN + 0.35: return end_card(t)
    tt = min(t, EDIT_END - 1e-3); s = me_seg(tt)
    if s is not None: _last_me[0] = me_frame(s, tt)
    if s is not None and s["mode"] == "full" and s["t0"] < 1:
        # abertura: ele em tela cheia; no fim, o reels sobe por cima (empurrando)
        frame = Image.fromarray(me_full(_last_me[0], t)).convert("RGBA")
        draw_caption(frame, t, 1450, 56, ("me",))
        react_tag(frame, t, "REACT  ·  LULA NA PAULISTA", 0.9, 2.6)
        q = (t - (REEL_IN - 0.45)) / 0.45
        if q > 0:
            r, h = reel_layer(REEL_IN); y = int(H * (1 - ease_io(q)))
            frame.alpha_composite(Image.fromarray(r).convert("RGBA"), (0, y))
    elif t < REEL_OUT:
        r, h = reel_layer(t); k = split_k(t)
        canvas = np.zeros((H, W, 3), np.uint8); canvas[:h] = r
        if k > 0.001:                                         # ele sobe por baixo, ocupando a metade de baixo
            src = _last_me[0]
            ph = H - SEAM; panel = me_panel(src, ph, t)
            y = int(lerp(H, SEAM, k)); vis = H - y
            canvas[y:] = panel[:vis]
        frame = Image.fromarray(canvas).convert("RGBA")
        if k > 0.001:
            d = ImageDraw.Draw(frame); y = int(lerp(H, SEAM, k))
            sh = Image.new("RGBA", (W, 40), (0, 0, 0, 0)); ImageDraw.Draw(sh).rectangle((0, 18, W, 40), fill=(0, 0, 0, 120))
            frame.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), (0, y - 30))
            d.rectangle((0, y - 2, W, y + 1), fill=GOLD + (int(230 * k),))
        rt = t - REEL_IN
        credit(frame, "Vídeo: PT", W - 30, lerp(H - 230, SEAM - 52, k), 1.0)
        if 1.2 < rt < 6.5: credit(frame, "Av. Paulista · 11/10", 30, lerp(H - 230, SEAM - 52, k), clamp((rt - 1.2) / 0.4) * (1 - clamp((rt - 6.1) / 0.4)), "lm")
        for b0, b1, big, small in BADGES: badge(frame, t, b0, b1, big, small, int(lerp(H - 300, SEAM - 70, k)), W - 40)
        if k > 0.5: draw_caption(frame, t, SEAM, 50, ("me",))
        # momento só da Paulista: rótulo discreto
        if 15.0 < t < 20.5:
            al = ease_out((t - 15.0) / 0.5) * (1 - ease_in((t - 20.0) / 0.5))
            lay = Image.new("RGBA", (W, 120), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
            dd.text((W / 2, 30), "AV. PAULISTA  ·  11/10", font=MF("Bold", 26), fill=GD, anchor="mm")
            dd.text((W / 2, 74), "Ato com Lula toma a avenida", font=MF("ExtraBold", 40), fill=WH, anchor="mm", stroke_width=3, stroke_fill=(4, 12, 22, 180))
            frame.alpha_composite(fade(lay, al), (0, int(1540 + 12 * (1 - al))))
    else:
        # final: a metade de cima (reels) sai e ele cresce até a tela cheia
        full = me_full(_last_me[0], t)
        q = ease_io((t - REEL_OUT) / 0.6)
        if q < 1:
            ya = int(lerp(PANEL_Y, 0, q)); yb = int(lerp(PANEL_Y + H - SEAM, H, q)); dst = int(lerp(SEAM, 0, q))
            canvas = np.zeros((H, W, 3), np.uint8)
            r = cover_crop(reel_frame(REEL_LEN - 0.05), W, SEAM, 0.55); ry = dst - SEAM
            if ry + SEAM > 0: canvas[max(0, ry):ry + SEAM] = r[max(0, -ry):]
            canvas[dst:dst + (yb - ya)] = full[ya:yb][:H - dst]
            frame = Image.fromarray(canvas).convert("RGBA")
            ImageDraw.Draw(frame).rectangle((0, dst - 2, W, dst + 1), fill=GOLD + (int(230 * (1 - q)),))
        else:
            frame = Image.fromarray(full).convert("RGBA")
        draw_dia25(frame, t)
        draw_caption(frame, t, 1450, 56, ("me",))
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
    if MODE.startswith("frames"):
        ts = [float(x) for x in MODE.split(":")[1].split(",")]
        outs = []
        for t in sorted(ts):
            s = me_seg(min(t, EDIT_END - 1e-3)) or max([x for x in segs if x["t1"] <= t], key=lambda x: x["t1"])
            _last_me[0] = me_frame(s, min(max(t, s["t0"]), s["t1"] - 1e-3))
            outs.append(finish(render_frame(t), t).resize((360, 640), Image.LANCZOS))
        sheet = Image.new("RGB", (360 * len(outs), 640)); [sheet.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]
        sheet.save(OUTFILE, quality=90); return
    if MODE == "info":
        print("TOTAL", TOTAL, "SPLITS", SPLITS, [(s["mode"], round(s["t0"], 2), round(s["t1"], 2)) for s in segs]); return
    vout = f"{V}/video2.mp4"
    if MODE != "audio":
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
        n = int(round(TOTAL * FPS))
        for i in range(n):
            enc.stdin.write(finish(render_frame(i / FPS), i / FPS).tobytes())
            if i % 150 == 0: print(f"{i / FPS:.1f}s", flush=True)
        enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    voice = readw(f"{V}/me_vox.wav"); vtrack = np.zeros((n, 2), np.float32)
    for s in segs:
        a0, a1 = int(s["a"] * SR), int(s["b"] * SR); t0 = int(s["t0"] * SR); p = voice[a0:a1].copy()
        f = int(0.03 * SR); env = np.ones(len(p)); env[:f] = np.linspace(0, 1, f); env[-f:] = np.linspace(1, 0, f)
        vtrack[t0:t0 + len(p)] += p * env[:, None]
    writew(f"{V}/voice2.wav", vtrack)
    reel = readw(f"{V}/lula_vox.wav")[:int(REEL_LEN * SR)]; rtrack = np.zeros((n, 2), np.float32)
    t0 = int(REEL_IN * SR); f = int(0.15 * SR); env = np.ones(len(reel)); env[:f] = np.linspace(0, 1, f); env[-int(0.5 * SR):] = np.linspace(1, 0, int(0.5 * SR))
    rtrack[t0:t0 + len(reel)] = reel * env[:, None]; writew(f"{V}/reel2.wav", rtrack)
    gate = np.zeros(n, np.float32); gate[int(REEL_IN * SR):int(REEL_OUT * SR)] = 1
    k = int(0.4 * SR); gate = np.convolve(gate, np.ones(k) / k, "same")
    mus = readw(f"{V}/music2.wav")[:n]; mus = np.pad(mus, ((0, max(0, n - len(mus))), (0, 0)))[:n]
    writew(f"{V}/music2_g.wav", mus * (1 - gate)[:, None]); writew(f"{V}/music2_full.wav", mus)
    ev = [(0.3, sfx.whoosh(0.6), 0.22), (REEL_IN - 0.45, sfx.whoosh(0.5), 0.3)]
    for a, b in SPLITS: ev += [(a - 0.3, sfx.whoosh(0.45), 0.2)] + ([(b - 0.3, sfx.whoosh(0.45, False), 0.18)] if b < REEL_OUT - 0.1 else [])
    ev += [(REEL_OUT - 0.1, sfx.whoosh(0.5), 0.22)]
    for b0, b1, big, small in BADGES: ev += [(b0, sfx.thud(), 0.26), (b0 + 0.05, sfx.paper(), 0.18)]
    ev += [(GLASS_DIA[0] - 0.08, sfx.whoosh(0.4), 0.22), (GLASS_DIA[0] + 0.45, sfx.thud(), 0.22), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx2.wav")
    def mix(out, with_reel):
        ins = ["-i", vout, "-i", f"{V}/voice2.wav", "-i", f"{V}/sfx2.wav", "-i", f"{V}/music2_g.wav" if with_reel else f"{V}/music2_full.wav"]
        fc = "[1:a]asplit=3[vox1][key][key2];[2:a]volume=0.8[sf];[3:a]volume=0.30[mus];[mus][key]sidechaincompress=threshold=0.02:ratio=7:attack=30:release=600[musd];"
        if with_reel:
            ins += ["-i", f"{V}/reel2.wav"]
            fc += "[4:a]volume=0.62[pl];[pl][key2]sidechaincompress=threshold=0.02:ratio=5:attack=20:release=450[pld];"
            fc += f"[vox1][sf][musd][pld]amix=inputs=4:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]"
        else:
            fc += f"[key2]anullsink;[vox1][sf][musd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]"
        subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", fc, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                        "-ar", "48000", "-movflags", "+faststart", out], check=True)
    mix(OUTFILE, True); mix(OUTFILE.replace(".mp4", "_yt.mp4"), False)
    print("done")

main()
