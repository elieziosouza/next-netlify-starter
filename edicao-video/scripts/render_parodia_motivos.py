"""Paródia: o amigo bolsonarista tenta explicar por que vai votar no Flávio (áudio no cartão 3D, rosto escondido),\nlista de motivos vazia, respiro de recorte de papel e final vai dar PT."""
import sys, math, subprocess, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.path.insert(0, f"{S}/work")
import sfx, zoom_suave
from minitop import make_minitop, make_minifooter, handles_row
from segment_person import PersonSeg
V = f"{S}/v26"; FD = f"{S}/fontdl"; ME, AU = f"{V}/me.mp4", f"{V}/au.mp4"
W, H, FPS = 1080, 1920, 30
WHITE = (255, 255, 255); GOLD = (214, 182, 116); GOLD_L = (245, 226, 176); NAVY = (6, 34, 58); RED = (210, 30, 36)
WH = (255, 255, 255, 255); GD = GOLD + (255,)
# trechos dele (me.mp4): abertura e a cara de paisagem no final; áudio do amigo (au.mp4) no cartão 3D
P1 = (0.10, 4.55); P2 = (4.60, 6.15)
AU_LEN = 15.0; PAPER = 2.6
segs = [dict(src="me", a=P1[0], b=P1[1], t0=0.0, t1=P1[1] - P1[0])]
AU_IN = segs[0]["t1"]; AU_OUT = AU_IN + AU_LEN; PAPER_IN = AU_OUT; PAPER_OUT = PAPER_IN + PAPER
segs.append(dict(src="me", a=P2[0], b=P2[1], t0=PAPER_OUT, t1=PAPER_OUT + P2[1] - P2[0]))
def out_t(x):
    for s in segs:
        if s["a"] <= x <= s["b"]: return s["t0"] + x - s["a"]
    raise ValueError(x)
FIN_IN = PAPER_OUT                                # cara de paisagem + refrão "vai dar PT"
MUS_IN = FIN_IN - 4.87
LYR = [(0.0, 1.43, "ESSE ANO"), (1.43, 2.87, "O LULA BOTA"), (2.87, 3.87, "O BOLSONARO"), (3.87, 4.87, "PRA MAMAR"),
       (4.87, 5.73, "VAI DAR PT"), (5.73, 6.73, "VAI DAR"), (6.73, 8.23, "VAI DAR PT"), (8.23, 9.43, "VAI DAR PT")]
FIN_LEN = 9.45 - (FIN_IN - MUS_IN); EDIT_END = FIN_IN + FIN_LEN; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
ME_CAPS = [("MEU AMIGO BOLSONARISTA", 0.15, 1.40), ("TÁ TENTANDO ME EXPLICAR", 1.45, 2.55),
           ("POR QUE ELE VAI VOTAR", 2.60, 3.45), ("NO FLÁVIO BOLSONARO", 3.45, 4.50)]
HOT = {"BOLSONARISTA", "EXPLICAR", "FLÁVIO", "BOLSONARO"}
AU_LINES = [(0.15, 1.65, "PORQUE? PORQUE O..."), (1.65, 11.20, "( ENROLANDO... )"), (11.40, 13.10, "PORQUE? PORQUE O..."), (13.10, 14.90, "EU NÃO SEI SE VOCÊ...")]
MOTIVOS = [2.2, 6.4, 10.4]                        # quando cada "MOTIVO ?: ???" entra na lista
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
for c in CAPS: c["src"] = "au" if any(w.strip(",.?!") in HOT for w in c["words"]) else "me"
SEG = PersonSeg(f"{S}/seg/u2net_human_seg.onnx")
def BIGF(s): return ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s)
def SERIF(s): return ImageFont.truetype(f"{FD}/DMSerifDisplay-Regular.ttf", s)
ZOOMS = [(2.60, 4.55, 0.07)]
BIG = [(2.60, 4.55, "POR QUÊ?")]

_me = {}
def me_src(a):
    key = int(a // 6)
    if key not in _me:
        p = subprocess.run(["ffmpeg", "-v", "error", "-i", ME, "-ss", f"{key * 6:.3f}", "-t", "6.4", "-vf", "fps=30,scale=1080:1920:flags=lanczos",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        n = len(p) // (1080 * 1920 * 3); _me[key] = np.frombuffer(p[:n * 1080 * 1920 * 3], np.uint8).reshape(n, 1920, 1080, 3)
    fr = _me[key]; return fr[min(len(fr) - 1, int((a - key * 6) * FPS))]
def me_at(tt):
    for s in segs:
        if s["t0"] <= tt < s["t1"]: return s["a"] + (tt - s["t0"])
    return P2[1] - 0.04                                          # depois: congela a cara de paisagem (zoom lento)

def big_behind(img, st):
    for a, b, word in BIG:
        if not (a <= st < b): continue
        u = st - a; k = back_out(u / 0.35, 1.6); al = clamp(u / 0.12) * clamp((b - st) / 0.25)
        size = 300; f = BIGF(size); d0 = ImageDraw.Draw(Image.new("L", (4, 4)))
        while d0.textlength(word, font=f) > W - 80: size -= 6; f = BIGF(size)
        lay = Image.new("RGBA", (W, int(size * 1.4)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.text((W / 2 + 5, lay.height / 2 + 10), word, font=f, fill=(0, 0, 0, 70), anchor="mm"); d.text((W / 2, lay.height / 2), word, font=f, fill=NAVY + (255,), anchor="mm")
        L = np.asarray(lay, np.float32) / 255; sc = 0.78 + 0.22 * k
        L = cv2.resize(L, (int(L.shape[1] * sc), int(L.shape[0] * sc)), interpolation=cv2.INTER_LINEAR)
        m = np.clip((cv2.resize(SEG(cv2.resize(img, (478, 850), interpolation=cv2.INTER_AREA)), (W, H)) - 0.35) / 0.3, 0, 1)
        y0 = int(262 - L.shape[0] / 2); x0 = int(W / 2 - L.shape[1] / 2); ya, yb = max(0, y0), min(H, y0 + L.shape[0]); xa, xb = max(0, x0), min(W, x0 + L.shape[1])
        Lc = L[ya - y0:yb - y0, xa - x0:xb - x0]; A = Lc[..., 3:4] * al * (1 - m[ya:yb, xa:xb, None])
        img[ya:yb, xa:xb] = np.clip(img[ya:yb, xa:xb].astype(np.float32) * (1 - A) + Lc[..., :3] * 255 * A, 0, 255).astype(np.uint8)
    return img

# --------------------------------------------------------------- áudio do amigo
_w = wave.open(f"{V}/au.wav"); _a = np.frombuffer(_w.readframes(_w.getnframes()), np.int16).astype(np.float32) / 32768
ENV = np.sqrt(np.convolve(np.r_[_a[:len(_a) // 160 * 160]].reshape(-1, 160).__pow__(2).mean(1), np.ones(4) / 4, "same"))
ENV = ENV / (np.percentile(ENV, 98) + 1e-6)
def env(x): i = int(x * 100); return float(ENV[i]) if 0 <= i < len(ENV) else 0.0
AU_FR = decode(AU, 0, AU_LEN, 720, 1280)
PW, PH = 430, 520
def make_portrait():
    fr = AU_FR[int(1.3 * FPS)]; crop = fr[500:1272, 40:680]
    p = Image.fromarray(cv2.resize(crop, (PW, PH), interpolation=cv2.INTER_AREA)).convert("RGBA"); d = ImageDraw.Draw(p)
    cx, cy, r = 235, 232, 132                                    # rosto escondido (só ilustração)
    d.ellipse((cx - r - 8, cy - r - 8, cx + r + 8, cy + r + 8), fill=WH)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=GOLD + (255,))
    d.text((cx, cy + 6), "?", font=BIGF(190), fill=NAVY + (255,), anchor="mm")
    return np.asarray(p)
PORT = make_portrait()

def kicker(frame, u):
    k = ease_io((u - 0.75) / 0.6); al = ease_out(u / 0.25) * (1 - ease_in((u - (AU_LEN - 0.4)) / 0.4))
    size = int(lerp(150, 46, k)); y = lerp(760, 205, k)
    f = MF("ExtraBold", size); lay = Image.new("RGBA", (W, size + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    sp = int(lerp(18, 6, k)); txt = "ÁUDIO"; ws = [d.textlength(c, font=f) for c in txt]; tw = sum(ws) + sp * (len(txt) - 1); x = W / 2 - tw / 2
    for c, cw in zip(txt, ws): d.text((x, 30), c, font=f, fill=GD); x += cw + sp
    if u < 0.75: lay = lay.filter(ImageFilter.GaussianBlur(10 * (1 - ease_out(u / 0.35))))
    frame.alpha_composite(fade(lay, al), (0, int(y - size / 2 - 30)))
    k2 = ease_out((u - 1.15) / 0.5) * (1 - ease_in((u - (AU_LEN - 0.4)) / 0.4))
    if k2 > 0:
        d = ImageDraw.Draw(frame)
        d.text((W / 2, 262 + 8 * (1 - k2)), "O AMIGO BOLSONARISTA EXPLICA", font=MF("SemiBold", 24), fill=(255, 255, 255, int(210 * k2)), anchor="mm")
        lw = int(70 * k2); d.rectangle((W / 2 - lw, 234, W / 2 + lw, 236), fill=GD)

def waveform(frame, u, al, cy):
    lay = Image.new("RGBA", (W, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    n = 41; c = n // 2; bw = 9; gap = 12; x0 = W / 2 - (n * bw + (n - 1) * gap) / 2
    for i in range(n):
        dist = abs(i - c)
        e = env(u - dist * 0.03) * (1 - dist / (n * 0.75)) + 0.03 * (0.5 + 0.5 * math.sin(u * 6 + i))
        hh = 6 + 140 * clamp(e) ** 0.8; x = x0 + i * (bw + gap); col = GOLD_L if dist < 3 else GOLD
        d.rounded_rectangle((x, 100 - hh / 2, x + bw, 100 + hh / 2), bw // 2, fill=col + (int(255 * (1 - dist / (n * 0.9))),))
    glow = lay.filter(ImageFilter.GaussianBlur(10)); frame.alpha_composite(fade(glow, al * 0.6), (0, cy - 100)); frame.alpha_composite(fade(lay, al), (0, cy - 100))

def motivos(frame, u, al):
    for i, t0 in enumerate(MOTIVOS):
        q = u - t0
        if q < 0: continue
        k = ease_out(q / 0.35); y = 340 + i * 180
        lay = Image.new("RGBA", (400, 160), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.rounded_rectangle((0, 0, 399, 159), 24, fill=(4, 14, 26, 230), outline=GD, width=3)
        d.text((26, 40), f"MOTIVO {i + 1}:", font=MF("ExtraBold", 36), fill=GD, anchor="lm")
        blink = 0.55 + 0.45 * abs(math.sin(u * 3 + i))
        d.text((26, 108), "???", font=BIGF(80), fill=RED + (int(255 * blink),), anchor="lm")
        paste(frame, fade(lay, al * clamp(q / 0.15)), 40 - 420 * (1 - k), y, 0.5, 14, (4, 10))

def loading(frame, u, al):
    p = min(0.99, ease_out(u / 4.5) * 0.99); stuck = u > 4.5
    lay = Image.new("RGBA", (860, 110), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    dots = "." * (1 + int(u * 2.5) % 3)
    d.text((0, 22), "CARREGANDO ARGUMENTO" + dots, font=MF("ExtraBold", 30), fill=WH, anchor="lm")
    pct = f"{int(p * 100)}%"; blink = (int(u * 2) % 2 == 0) or not stuck
    if blink: d.text((860, 22), pct, font=MF("ExtraBold", 30), fill=(RED if stuck else GOLD) + (255,), anchor="rm")
    d.rounded_rectangle((0, 56, 859, 92), 18, fill=(255, 255, 255, 40))
    d.rounded_rectangle((0, 56, max(36, int(859 * p)), 92), 18, fill=(RED if stuck else GOLD) + (255,))
    frame.alpha_composite(fade(lay, al), ((W - 860) // 2, 1200))

def au_caption(frame, u, al):
    for a, b, txt in AU_LINES:
        if not (a <= u < b): continue
        q = u - a; k = back_out(q / 0.2, 1.6); enrola = txt.startswith("(")
        f = MF("ExtraBoldItalic" if enrola else "ExtraBold", 50 if enrola else 54)
        tw = ImageDraw.Draw(frame).textlength(txt, font=f)
        lay = Image.new("RGBA", (int(tw + 60), 92), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        if enrola: d.rounded_rectangle((0, 0, lay.width - 1, 91), 26, fill=(255, 255, 255, 40)); d.text((30, 48), txt, font=f, fill=(225, 230, 238, 255), anchor="lm")
        else: d.rounded_rectangle((0, 0, lay.width - 1, 91), 26, fill=GD); d.text((30, 48), txt, font=f, fill=NAVY + (255,), anchor="lm")
        sc = 0.85 + 0.15 * k; lay = fade(lay.resize((int(lay.width * sc), int(92 * sc)), Image.BICUBIC), al * clamp(q / 0.08) * clamp((b - u) / 0.08))
        paste(frame, lay, (W - lay.width) / 2, 1430 - lay.height / 2, 0.5, 14, (4, 12))

def audio_scene(tt):
    u = tt - AU_IN; fr = AU_FR[int(clamp(u * FPS, 0, len(AU_FR) - 1))]
    bl = cv2.resize(cv2.GaussianBlur(cv2.resize(fr, (72, 128)), (0, 0), 3), (W, H)).astype(np.float32)
    bg = NAVYBG * 0.85 + bl * 0.18
    frame = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
    al = clamp(u / 0.25) * (1 - ease_in((u - (AU_LEN - 0.4)) / 0.4))
    kicker(frame, u)
    q = u - 1.0
    if q >= 0:                                                   # cartão 3D entra girando pela direita e brilha com a voz
        kin = ease_out(q / 0.65); e = env(u); glow = clamp(e * 1.3)
        rgba = rounded(np.ascontiguousarray(PORT[..., :3]), 24, 3, GOLD + (int(150 + 105 * glow),))
        a = 0.10 + 0.45 * (1 - kin)
        im = Image.fromarray(persp(rgba, "right", a), "RGBA"); sc = 1 + 0.02 * glow
        im = im.resize((int(PW * sc), int(PH * sc)), Image.BICUBIC)
        x = 760 - im.width / 2 + 520 * (1 - kin); y = 330 + (PH - im.height) / 2
        if glow > 0.05:
            g = Image.new("RGBA", (im.width + 80, im.height + 80), (0, 0, 0, 0))
            ImageDraw.Draw(g).rounded_rectangle((40, 40, 40 + im.width, 40 + im.height), 30, fill=GOLD + (int(120 * glow),))
            frame.alpha_composite(fade(g.filter(ImageFilter.GaussianBlur(26)), al), (int(x - 40), int(y - 40)))
        paste(frame, fade(im, al), x, y, 0.55, 20, (8, 20))
        d = ImageDraw.Draw(frame); ka = al * clamp((q - 0.4) / 0.3)
        d.text((760, 890), "AMIGO BOLSONARISTA", font=MF("ExtraBold", 30), fill=(255, 255, 255, int(255 * ka)), anchor="mm")
        d.text((760, 928), "eleitor do Flávio · rosto escondido", font=MF("SemiBold", 21), fill=GOLD + (int(240 * ka),), anchor="mm")
    motivos(frame, u, al)
    waveform(frame, u, al * clamp((u - 1.2) / 0.4), 1060)
    loading(frame, u, al * clamp((u - 1.6) / 0.4))
    au_caption(frame, u, al)
    return frame

# --------------------------------------------------------------- respiro: recorte de papel
yy_, xx_ = np.mgrid[0:H, 0:W]
MAT = (np.array([10, 40, 66], np.float32) + 10 * np.sin(xx_ / 900.0)[..., None]).astype(np.float32)
_g = ((xx_ % 60 < 2) | (yy_ % 60 < 2)); _G = ((xx_ % 300 < 3) | (yy_ % 300 < 3))
MAT[_g] += 26; MAT[_G] += 30
MAT = np.clip(MAT, 0, 255).astype(np.uint8)
STRIPS = [(0.15, "MOTIVOS PARA", 360, -2.0, False), (0.55, "VOTAR NO", 540, 1.5, False), (0.95, "FLÁVIO:", 720, -1.0, True), (1.45, "· · · · · · · ·", 930, 2.0, False)]
def paper_scene(tt):
    u = tt - PAPER_IN; frame = Image.fromarray(MAT).convert("RGBA")
    for t0, txt, y, rot, hl in STRIPS:
        q = u - t0
        if q < 0: continue
        f = SERIF(96); tw = ImageDraw.Draw(frame).textlength(txt, font=f)
        st = Image.new("RGBA", (int(tw + 80), 150), (0, 0, 0, 0)); d = ImageDraw.Draw(st)
        d.rectangle((0, 8, st.width - 1, 142), fill=(GOLD_L if hl else (246, 244, 236)) + (255,))
        d.text((40, 76), txt, font=f, fill=(18, 18, 22, 255), anchor="lm")
        st = st.rotate(rot, resample=Image.BICUBIC, expand=True)
        k = ease_out(q / 0.12); s = 1.25 - 0.25 * k
        st = st.resize((int(st.width * s), int(st.height * s)), Image.BICUBIC)
        paste(frame, fade(st, clamp(q / 0.06)), W / 2 - st.width / 2, y - st.height / 2, 0.45, 8 + 10 * (1 - k), (6, 10 + 14 * (1 - k)))
    return frame

def lyrics(frame, t):
    mt = t - MUS_IN; k_all = clamp((t - FIN_IN) / 0.4)
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
    tt = min(t, EDIT_END - 1e-3)
    if AU_IN <= tt < AU_OUT: frame = audio_scene(tt)
    elif PAPER_IN <= tt < PAPER_OUT: frame = paper_scene(tt)
    else:
        st = me_at(tt); z = zoom_suave.nivel(st, ZOOMS) + (0.07 * ease_io((tt - FIN_IN) / FIN_LEN) if tt >= FIN_IN else 0)
        img = big_behind(me_src(st).copy(), st); img = zoom_suave.aplica(img, z, 0.42)
        frame = Image.fromarray(img).convert("RGBA")
        if tt < AU_IN: draw_caption(frame, t, 1450, 56, ("me", "au"))
        else: lyrics(frame, t)
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
    if MODE == "info": print("TOTAL", TOTAL, "AU", AU_IN, AU_OUT, "PAPER", PAPER_IN, PAPER_OUT, "FIN", FIN_IN, "END", END_IN); return
    vout = f"{V}/video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
    for i in range(int(round(TOTAL * FPS))): enc.stdin.write(finish(render_frame(i / FPS), i / FPS).tobytes())
    enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    for f, o in ((ME, "me48.wav"), (AU, "au48.wav")): subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-ar", "48000", "-ac", "2", f"{V}/{o}"], check=True)
    voice = readw(f"{V}/me48.wav"); vt = np.zeros((n, 2), np.float32)
    s = segs[0]; p = voice[int(s["a"] * SR):int(s["b"] * SR)].copy(); f = int(0.03 * SR)
    env_ = np.ones(len(p)); env_[:f] = np.linspace(0, 1, f); env_[-f:] = np.linspace(1, 0, f); vt[int(s["t0"] * SR):int(s["t0"] * SR) + len(p)] += p * env_[:, None]
    writew(f"{V}/voice.wav", vt)
    au = readw(f"{V}/au48.wav")[:int(AU_LEN * SR)]; at = np.zeros((n, 2), np.float32); f = int(0.05 * SR)
    au[:f] *= np.linspace(0, 1, f)[:, None]; au[-int(0.3 * SR):] *= np.linspace(1, 0, int(0.3 * SR))[:, None]; at[int(AU_IN * SR):int(AU_IN * SR) + len(au)] = au; writew(f"{V}/au_t.wav", at)
    song = readw(f"{S}/v15/song_vox.wav"); Ls = min(len(song), n - int(MUS_IN * SR)); ts_ = np.arange(Ls) / SR; lead = FIN_IN - MUS_IN
    gain = np.clip((ts_ - lead + 0.12) / 0.12, 0, 1) * np.clip(1 - (ts_ - (TOTAL - MUS_IN - 1.6)) / 1.5, 0, 1)
    sg = np.zeros((n, 2), np.float32); sg[int(MUS_IN * SR):int(MUS_IN * SR) + Ls] = song[:Ls] * gain[:, None]; writew(f"{V}/song.wav", sg)
    ev = [(0.3, sfx.whoosh(0.5), 0.2), (AU_IN - 0.12, sfx.whoosh(0.6), 0.26), (AU_IN + 1.0, sfx.whoosh(0.5), 0.22)]
    ev += [(AU_IN + x, sfx.whoosh(0.35), 0.24) for x in MOTIVOS] + [(AU_IN + x + 0.05, sfx.click(13), 0.45) for x in MOTIVOS]
    ev += [(AU_IN + 4.5, sfx.thud(), 0.22), (PAPER_IN - 0.1, sfx.whoosh(0.5), 0.24)]
    ev += [(PAPER_IN + t0, sfx.paper(), 0.5) for t0, *_ in STRIPS] + [(PAPER_IN + STRIPS[2][0], sfx.thud(), 0.25)]
    ev += [(FIN_IN - 0.08, sfx.whoosh(0.4, False), 0.2), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
    for a, b, w in BIG: ev.append((out_t(a), sfx.click(), 0.5))
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/au_t.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=70[vox];[2:a]volume=0.8[sf];[3:a]highpass=f=80,volume=1.25[au];[4:a]volume=0.95[sg];"
                    f"[vox][sf][au][sg]amix=inputs=4:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
