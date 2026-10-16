"""Pesquisa PoderData/Aya 16/10/2026 (Lula 50 × Flávio 50 nos válidos) na frente dele: ele encolhe para um quadro
e o painel da pesquisa sobe na frente do peito; números animam do 13/10 (49 × 51) para o 16/10 (50 × 50); final 'vai dar PT'."""
import sys, math, subprocess, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.path.insert(0, f"{S}/work")
import sfx, zoom_suave
from minitop import make_minitop, make_minifooter, handles_row
V = f"{S}/v21"; FD = f"{S}/fontdl"; ME = f"{V}/me.mp4"
W, H, FPS = 1080, 1920, 30
WHITE = (255, 255, 255); GOLD = (214, 182, 116); GOLD_L = (245, 226, 176); NAVY = (6, 34, 58); RED = (210, 30, 36); STEEL = (150, 172, 196)
WH = (255, 255, 255, 255); GD = GOLD + (255,)
A0, A1 = 1.30, 7.49                         # fala dele (fonte)
SPEECH = A1 - A0; HOLD = 1.0
FIN_IN = SPEECH + HOLD
MUS_IN = 5.37 - A0                          # música entra no "a virada tá chegando, hein?"
LYR = [(0.0, 1.43, "ESSE ANO"), (1.43, 2.87, "O LULA BOTA"), (2.87, 3.87, "O BOLSONARO"), (3.87, 4.87, "PRA MAMAR"),
       (4.87, 5.73, "VAI DAR PT"), (5.73, 6.73, "VAI DAR"), (6.73, 8.23, "VAI DAR PT"), (8.23, 9.43, "VAI DAR PT")]
FIN_LEN = 9.45 - (FIN_IN - MUS_IN); EDIT_END = FIN_IN + FIN_LEN; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
segs = [dict(src="me", a=A0, b=A1, t0=0.0, t1=SPEECH)]
ME_CAPS = [("OLHA A VIRADA!", 1.59, 2.76), ("A VIRADA TÁ CHEGANDO AÍ", 3.26, 4.97), ("A VIRADA TÁ CHEGANDO, HEIN?", 5.37, 7.49)]
HOT = {"VIRADA"}
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
for c in CAPS: c["src"] = "au" if any(w.strip(",.?!") in HOT for w in c["words"]) else "me"
TR = 1.59 - A0 - 0.05                        # "olha a virada": ele encolhe e o painel sobe
SC1 = 0.62; FY0 = 150                         # quadro dele: 62% do tamanho, topo em y 150 (queixo fica acima do painel)
CX, CY, CW, CH = 50, 1105, 980, 640           # painel da pesquisa

_fr = None
def me_frame(st):
    global _fr
    if _fr is None: _fr = decode(ME, 0, 7.5, 1080, 1920)
    return _fr[int(clamp(st * FPS, 0, len(_fr) - 1))]
def me_at(t):
    if t < SPEECH: return A0 + t
    u = (t - SPEECH) * 0.8; L0, L1 = 0.25, 1.50; Lq = L1 - L0; p = u % (2 * Lq)   # sorriso em silêncio, vai e volta
    return L1 - p if p < Lq else L0 + (p - Lq)

def k_frame(t):
    return ease_io((t - TR) / 0.5) * (1 - ease_io((t - FIN_IN) / 0.5))

def compose(me, k):
    if k <= 0.001: return me.copy()
    bg = cv2.resize(cv2.GaussianBlur(cv2.resize(me, (W // 8, H // 8)), (0, 0), 3), (W, H)).astype(np.float32) * 0.35 + np.array([3, 9, 18], np.float32) * 0.65
    out = me.astype(np.float32) * (1 - k) + bg * k
    s = lerp(1.0, SC1, k); fw, fh = int(W * s), int(H * s); fx, fy = (W - fw) // 2, int(lerp(0, FY0, k))
    small = cv2.resize(me, (fw, fh), interpolation=cv2.INTER_AREA).astype(np.float32)
    m = Image.new("L", (fw, fh), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, fw - 1, fh - 1), int(34 * k), fill=255); m = np.asarray(m, np.float32)[..., None] / 255
    yb = min(H, fy + fh); out[fy:yb, fx:fx + fw] = out[fy:yb, fx:fx + fw] * (1 - m[:yb - fy]) + small[:yb - fy] * m[:yb - fy]
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")
    ImageDraw.Draw(img).rounded_rectangle((fx, fy, fx + fw, fy + fh), int(34 * k), outline=GOLD + (int(220 * k),), width=3)
    return img

def bar(d, x, y, w, h, frac, col):
    d.rounded_rectangle((x, y, x + w, y + h), h // 2, fill=(255, 255, 255, 40))
    d.rounded_rectangle((x, y, x + max(h, int(w * frac)), y + h), h // 2, fill=col + (255,))

def card(t):
    u = t - TR - 0.1
    lay = Image.new("RGBA", (CW, CH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, CW - 1, CH - 1), 32, fill=(5, 16, 30, 242), outline=GD, width=3)
    d.rounded_rectangle((26, 22, CW - 26, 74), 26, fill=GD); d.text((CW / 2, 48), "PESQUISA PODERDATA/AYA · 2º TURNO", font=MF("ExtraBold", 30), fill=NAVY + (255,), anchor="mm")
    m = smooth((u - 1.5) / 1.0)                                   # 0 = 13/10, 1 = 16/10
    lula = lerp(49, 50, m); fla = lerp(51, 50, m)
    lab = "13/10 (anterior) · votos válidos" if m < 0.5 else "16/10 · NOVA · votos válidos"
    d.text((CW / 2, 112), lab, font=MF("Bold", 30), fill=(255, 255, 255, 230) if m < 0.5 else GOLD_L + (255,), anchor="mm")
    for i, (nm, v, col, dlt) in enumerate((("LULA", lula, GOLD, "+1"), ("FLÁVIO", fla, STEEL, "−1"))):
        x0 = 60 + i * (CW // 2); d.text((x0, 170), nm, font=MF("ExtraBold", 40), fill=WH, anchor="lm")
        d.text((x0, 268), f"{v:.0f}%", font=MF("ExtraBold", 116), fill=(GOLD_L if i == 0 else WHITE) + (255,), anchor="lm")
        if m > 0.95:
            ka = ease_out((m - 0.95) / 0.05)
            d.text((x0 + 300, 262), dlt, font=MF("ExtraBold", 44), fill=((120, 220, 140) if i == 0 else (255, 140, 140)) + (int(255 * ka),), anchor="lm")
        bar(d, x0, 340, CW // 2 - 110, 30, v / 100 * 1.6, col)
    d.text((CW / 2, 505), "Total: 47% × 47% · brancos e nulos 4% · não sabem 2%", font=MF("SemiBold", 26), fill=(200, 208, 220, 255), anchor="mm")
    d.text((CW / 2, 560), "3.000 entrevistas · 13 a 15/10 · margem ±1,8 p.p. · TSE BR-04258/2026", font=MF("Medium", 22), fill=(170, 182, 198, 255), anchor="mm")
    d.text((CW / 2, 596), "Fonte: PoderData/Aya, divulgada em 16/10/2026", font=MF("Medium", 22), fill=(170, 182, 198, 255), anchor="mm")
    img = Image.fromarray(np.asarray(lay)).convert("RGBA")
    # carimbo EMPATE
    ks = u - 2.7
    if ks > 0:
        kk = back_out(ks / 0.35, 2.4); f = MF("ExtraBold", 70); txt = "EMPATE"
        tw = ImageDraw.Draw(Image.new("RGBA", (4, 4))).textlength(txt, font=f)
        st = Image.new("RGBA", (int(tw + 60), 110), (0, 0, 0, 0)); ds = ImageDraw.Draw(st)
        ds.rounded_rectangle((8, 8, st.width - 8, 102), 16, outline=RED + (255,), width=8); ds.text((st.width / 2, 56), txt, font=f, fill=RED + (255,), anchor="mm")
        st = st.rotate(-4, Image.BICUBIC, expand=True); sc = 1.6 - 0.6 * kk; st = st.resize((int(st.width * sc), int(st.height * sc)), Image.BICUBIC)
        img.alpha_composite(fade(st, clamp(ks / 0.08)), (int(CW / 2 - st.width / 2), int(432 - st.height / 2)))
    return img

def lyrics(frame, t):
    mt = t - MUS_IN; k_all = clamp((t - FIN_IN - 0.3) / 0.4)
    g = Image.new("RGBA", (W, 760), (0, 0, 0, 0)); ImageDraw.Draw(g).rectangle((0, 0, W, 760), fill=(4, 10, 20, 255))
    g.putalpha(Image.linear_gradient("L").resize((W, 760)).point(lambda v: int(v * 0.72 * k_all))); frame.alpha_composite(g, (0, H - 760))
    for a, b, txt in LYR:
        if not (a <= mt < b): continue
        u = mt - a; k = back_out(u / 0.18, 2.0); pt = txt.endswith("PT")
        f = MF("ExtraBold", 108 if len(txt) <= 10 else 88); lay = Image.new("RGBA", (W, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        if pt:
            pre = txt[:-2]; wp = d.textlength(pre, font=f); wt = d.textlength("PT", font=f); x0 = W / 2 - (wp + wt + 30) / 2
            d.text((x0, 100), pre, font=f, fill=WH, anchor="lm")
            d.rounded_rectangle((x0 + wp + 2, 30, x0 + wp + wt + 34, 172), 18, fill=RED + (255,)); d.text((x0 + wp + 18, 100), "PT", font=f, fill=WH, anchor="lm")
        else: d.text((W / 2, 100), txt, font=f, fill=WH, anchor="mm")
        sc = 0.7 + 0.3 * k; lay = fade(lay.resize((int(W * sc), int(200 * sc)), Image.BICUBIC), k_all)
        blk = Image.new("RGBA", lay.size, (0, 0, 0, 255)); blk.putalpha(lay.getchannel("A").point(lambda v: int(v * 0.6)))
        frame.alpha_composite(blk.filter(ImageFilter.GaussianBlur(10)), (int(W / 2 - lay.width / 2) + 4, 1630 - lay.height // 2 + 8))
        frame.alpha_composite(lay, (int(W / 2 - lay.width / 2), 1630 - lay.height // 2))

def render_frame(t):
    if t >= END_IN + 0.35: return end_card(t)
    tt = min(t, EDIT_END - 1e-3); st = me_at(tt)
    me = zoom_suave.aplica(me_frame(st), 0.04 * zoom_suave._io((tt - FIN_IN - 0.4) / 1.5))
    k = k_frame(tt); frame = compose(me, k) if k > 0.001 else Image.fromarray(me).convert("RGBA")
    if k > 0.001:
        kin = ease_out((tt - TR - 0.1) / 0.55); kout = ease_in((tt - (FIN_IN - 0.05)) / 0.4)
        c = card(tt); arr = np.asarray(c)
        tilt = clamp((1 - kin) + kout)
        if tilt > 0.003: arr = persp(arr, "top", 0.02 + 0.35 * tilt)
        dy = 900 * (1 - kin) + 900 * kout
        paste(frame, fade(Image.fromarray(arr, "RGBA"), clamp(kin * 1.5) * (1 - kout)), CX, CY + dy, 0.6, 22, (10, 26))
        draw_caption(frame, t, 1050 if k > 0.5 else 1450, 50 if k > 0.5 else 56, ("me", "au"))
    elif tt < FIN_IN: draw_caption(frame, t, 1450, 56, ("me", "au"))
    if tt >= FIN_IN: lyrics(frame, t)
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
        outs = [finish(render_frame(t), t).resize((360, 640), Image.LANCZOS) for t in ts]
        sheet = Image.new("RGB", (360 * len(outs), 640)); [sheet.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]
        sheet.save(OUTFILE, quality=90); return
    if MODE == "info": print("TOTAL", TOTAL, "TR", TR, "FIN", FIN_IN, "MUS", MUS_IN); return
    vout = f"{V}/video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
    for i in range(int(round(TOTAL * FPS))): enc.stdin.write(finish(render_frame(i / FPS), i / FPS).tobytes())
    enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", ME, "-ar", "48000", "-ac", "2", f"{V}/me48.wav"], check=True)
    v = readw(f"{V}/me48.wav")[int(A0 * SR):int(A1 * SR)]; vt = np.zeros((n, 2), np.float32); f = int(0.04 * SR)
    env = np.ones(len(v)); env[:f] = np.linspace(0, 1, f); env[-f:] = np.linspace(1, 0, f); vt[:len(v)] = v * env[:, None]; writew(f"{V}/voice.wav", vt)
    song = readw(f"{S}/v15/song_vox.wav"); lead = FIN_IN - MUS_IN; Ls = min(len(song), n - int(MUS_IN * SR)); tl = np.arange(Ls) / SR
    gain = np.where(tl < lead, 10 ** ((-22 + 22 * tl / lead) / 20), 1.0) * np.clip(1 - (tl - (TOTAL - MUS_IN - 1.6)) / 1.5, 0, 1)
    sg = np.zeros((n, 2), np.float32); sg[int(MUS_IN * SR):int(MUS_IN * SR) + Ls] = song[:Ls] * gain[:, None]; writew(f"{V}/song.wav", sg)
    subprocess.run([sys.executable, f"{S}/work/music.py", f"{V}/bed.wav", f"{TOTAL + 0.5:.2f}"], check=True)
    bed = readw(f"{V}/bed.wav")[:n]; bed = np.pad(bed, ((0, max(0, n - len(bed))), (0, 0)))[:n]
    gate = np.ones(n, np.float32); gate[int((MUS_IN - 0.3) * SR):] = 0; gate = np.convolve(gate, np.ones(int(0.5 * SR)) / int(0.5 * SR), "same"); writew(f"{V}/bed_g.wav", bed * gate[:, None])
    ev = [(0.2, sfx.whoosh(0.5), 0.2), (TR, sfx.whoosh(0.5), 0.28), (TR + 1.6, sfx.marker(0.7), 0.2), (TR + 2.8, sfx.thud(), 0.32), (TR + 2.85, sfx.paper(), 0.2),
          (FIN_IN - 0.05, sfx.whoosh(0.5, False), 0.22), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/bed_g.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=70,asplit=3[vox][k1][k2];[2:a]volume=0.8[sf];[3:a]volume=0.26[bed];[4:a]volume=0.9[sg];"
                    "[bed][k1]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=500[bedd];[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][bedd][sgd]amix=inputs=4:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
