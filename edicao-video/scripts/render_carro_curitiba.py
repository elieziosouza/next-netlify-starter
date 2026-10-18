"""Carro com adesivo do PT atacado por bolsonaristas em Curitiba (vídeos do TikTok): tela dividida com o ataque,
vidro traseiro quebrado congelado e destacado, final vai dar PT. Sem recortes de jornal: o caso não saiu na imprensa até 18/10."""
import sys, math, subprocess, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.path.insert(0, f"{S}/work")
import sfx, zoom_suave
from minitop import make_minitop, make_minifooter, handles_row
from segment_person import PersonSeg
V = f"{S}/v29"; FD = f"{S}/fontdl"; ME, C1, C2 = f"{V}/me.mp4", f"{V}/c1.mp4", f"{V}/c2.mp4"
W, H, FPS = 1080, 1920, 30
WHITE = (255, 255, 255); GOLD = (214, 182, 116); GOLD_L = (245, 226, 176); NAVY = (6, 34, 58); RED = (210, 30, 36)
WH = (255, 255, 255, 255); GD = GOLD + (255,)
# trechos dele (me.mp4 720x1280): duas telas divididas com o ataque e dois trechos em tela cheia
PARTS = [("split", 1.20, 6.62), ("split", 8.00, 13.80), ("full", 14.30, 15.85), ("full", 16.38, 20.15), ("full", 21.50, 26.22)]
segs = []; acc = 0.0
for p in PARTS:
    segs.append(dict(src="me", mode=p[0], a=p[1], b=p[2], t0=acc, t1=acc + p[2] - p[1])); acc += p[2] - p[1]
OPEN, OPEN_CA = 2.2, 4.5                                          # abertura: o ataque com o som original dos vândalos, antes da fala
for d in segs: d["t0"] += OPEN; d["t1"] += OPEN
def out_t(x):
    for s in segs:
        if s["src"] == "me" and s["a"] <= x <= s["b"]: return s["t0"] + x - s["a"]
    raise ValueError(x)
TAIL = (26.22, 28.75)
MUS_IN = out_t(22.45); FIN_IN = segs[-1]["t1"]
LYR = [(0.0, 1.43, "ESSE ANO"), (1.43, 2.87, "O LULA BOTA"), (2.87, 3.87, "O BOLSONARO"), (3.87, 4.87, "PRA MAMAR"),
       (4.87, 5.73, "VAI DAR PT"), (5.73, 6.73, "VAI DAR"), (6.73, 8.23, "VAI DAR PT"), (8.23, 9.43, "VAI DAR PT")]
FIN_LEN = 9.45 - (FIN_IN - MUS_IN); EDIT_END = FIN_IN + FIN_LEN; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
ME_CAPS = [("UM CARRO É VANDALIZADO", 1.34, 2.65), ("POR BOLSONARISTAS", 2.65, 3.85), ("AO PASSAR PERTO", 4.44, 5.40), ("DE UMA MANIFESTAÇÃO.", 5.40, 6.50),
           ("O QUE SE PODE DIZER DISSO, NÉ?", 8.09, 9.95), ("ELES NÃO CONSEGUEM ENTENDER,", 10.15, 11.55), ("NÃO CONSEGUEM COMPREENDER", 11.60, 12.85),
           ("QUE UMA PESSOA", 12.90, 13.76), ("PENSE DIFERENTE DELAS.", 14.33, 15.72),
           ("ENTÃO SÃO APENAS", 16.47, 17.75), ("BOLSONARISTAS SENDO BOLSONARISTAS.", 17.75, 20.03),
           ("POR ISSO QUE DIA 25", 21.62, 23.34), ("SERÁ INEVITÁVEL!", 24.92, 26.12)]
HOT = {"VANDALIZADO", "BOLSONARISTAS", "MANIFESTAÇÃO.", "ENTENDER,", "COMPREENDER", "DIFERENTE", "BOLSONARISTAS.", "25", "INEVITÁVEL!"}
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
for c in CAPS: c["src"] = "au" if any(w.strip(",.?!") in {h.strip(",.?!") for h in HOT} for w in c["words"]) else "me"
SEG = PersonSeg(f"{S}/seg/u2net_human_seg.onnx")
def BIGF(s): return ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s)
def SERIF(s): return ImageFont.truetype(f"{FD}/DMSerifDisplay-Regular.ttf", s)
ZOOMS = [(14.55, 15.85, 0.07), (17.75, 20.00, 0.07), (24.92, 26.20, 0.07)]
BIG = [(14.45, 15.90, "DIFERENTE", GOLD_L), (16.50, 17.72, "APENAS", WHITE), (17.75, 20.15, "BOLSONARISTAS", (235, 50, 50)), (22.45, 23.45, "DIA 25", GOLD_L), (24.92, 26.25, "INEVITÁVEL", WHITE)]
SEAM = 1060; PH = H - SEAM

_me = {}
def me_src(a):
    key = int(a // 6)
    if key not in _me:
        if len(_me) > 3: _me.clear()
        p = subprocess.run(["ffmpeg", "-v", "error", "-i", ME, "-ss", f"{key * 6:.3f}", "-t", "6.4", "-vf", "fps=30,scale=1080:1920:flags=lanczos",
                            "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        n = len(p) // (1080 * 1920 * 3); _me[key] = np.frombuffer(p[:n * 1080 * 1920 * 3], np.uint8).reshape(n, 1920, 1080, 3)
    fr = _me[key]; return fr[min(len(fr) - 1, int((a - key * 6) * FPS))]
def seg_at(tt):
    for s in segs:
        if s["t0"] <= tt < s["t1"]: return s
    return None
def me_at(tt):
    s = seg_at(tt)
    if s is not None: return s["a"] + (tt - s["t0"])
    return min(TAIL[1], TAIL[0] + (tt - FIN_IN) * 0.6)             # final: o L em câmera lenta leve e depois congela

# imagens do ataque: c1 (576x1024, letreiro em y 700-830) e c2 (540x968, logo no canto e letreiro em y 615-850) recortados acima das letras
C1_FR = decode(C1, 4.0, 13.0, 576, 1024)
C2_FR = decode(C2, 12.5, 14.6, 540, 968)
C1_T0, C2_T0 = 4.0, 12.5
PLATE = [(13.3, (138, 350, 232, 402)), (14.2, (172, 358, 272, 410))]     # placa do carro no recorte do c2: borrada
FREEZE_CT = 14.2
CLIPMAP = {0: [("c1f", 0.0, 2.2, 6.7), ("c1", 2.2, 99, 6.7)], 1: [("c1", 0.0, 1.8, 10.2), ("c2", 1.8, 3.1, 12.9), ("c2f", 3.1, 99, FREEZE_CT)]}
ATK = (600, 500, 250)                                           # quem está batendo no carro (c1 6.7 s), no painel
WIN = (380, 600, 270, 160)                                        # vidro traseiro no painel: centro e raios da elipse
def plate_box(ct):
    (ta, ba), (tb, bb) = PLATE; k = clamp((ct - ta) / (tb - ta))
    return [int(lerp(x, y, k)) for x, y in zip(ba, bb)]
def c2_crop(ct):
    fr = C2_FR[int(clamp((ct - C2_T0) * FPS, 0, len(C2_FR) - 1))][190:622, 100:540].copy()
    x0, y0, x1, y1 = plate_box(ct); x0, y0 = max(0, x0 - 10), max(0, y0 - 10); x1, y1 = x1 + 10, y1 + 10
    fr[y0:y1, x0:x1] = cv2.GaussianBlur(cv2.resize(cv2.resize(fr[y0:y1, x0:x1], (8, 4)), (x1 - x0, y1 - y0), interpolation=cv2.INTER_NEAREST), (0, 0), 6)
    return fr
def clip_panel(si, u):
    for kind, a, b, ca in CLIPMAP[si]:
        if a <= u < b: break
    if kind in ("c1", "c1f"):
        fr = C1_FR[int(clamp(((ca if kind == "c1f" else ca + u - a) - C1_T0) * FPS, 0, len(C1_FR) - 1))][120:685]
    else:
        fr = c2_crop(ca if kind == "c2f" else ca + u - a)
    big = cv2.resize(fr, (W, SEAM), interpolation=cv2.INTER_LANCZOS4)
    q = u - a
    if kind in ("c1f", "c2f"):                                    # congela e aproxima devagar do vidro
        sc = 1 + 0.22 * ease_io(q / 2.6); cx, cy = (WIN if kind == "c2f" else ATK)[:2]
        big = cv2.warpAffine(big, np.float32([[sc, 0, cx - cx * sc], [0, sc, cy - cy * sc]]), (W, SEAM), flags=cv2.INTER_LINEAR)
    if a > 0 and q < 0.18:                                        # troca de cena com flash
        big = np.clip(big.astype(np.float32) + 160 * (1 - q / 0.18), 0, 255).astype(np.uint8)
    return big, kind, q

def me_panel(img):
    band = img[200:1800]; sc = PH / band.shape[0]                 # rosto inteiro: da testa ao queixo
    fg = cv2.resize(band, (int(W * sc), PH), interpolation=cv2.INTER_AREA)
    bg = cv2.resize(cv2.GaussianBlur(cv2.resize(img, (W // 8, H // 8)), (0, 0), 3), (W, H))[int((H - PH) * 0.45):int((H - PH) * 0.45) + PH]
    out = (bg.astype(np.float32) * 0.6).astype(np.uint8); x = (W - fg.shape[1]) // 2; out[:, x:x + fg.shape[1]] = fg
    return out

def big_behind(img, st):
    """palavra grande atrás dele: a máscara de pessoa recorta a cabeça na frente das letras"""
    for a, b, word, col in BIG:
        if not (a <= st < b): continue
        u = st - a; k = back_out(u / 0.35, 1.6); al = clamp(u / 0.12) * clamp((b - st) / 0.25)
        size = 330; f = BIGF(size); d0 = ImageDraw.Draw(Image.new("L", (4, 4)))
        while d0.textlength(word, font=f) > W - 70: size -= 6; f = BIGF(size)
        lay = Image.new("RGBA", (W, int(size * 1.4)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.text((W / 2 + 6, lay.height / 2 + 10), word, font=f, fill=(0, 0, 0, 160), anchor="mm"); d.text((W / 2, lay.height / 2), word, font=f, fill=col + (255,), anchor="mm")
        L = np.asarray(lay, np.float32) / 255; sc = 0.78 + 0.22 * k
        L = cv2.resize(L, (int(L.shape[1] * sc), int(L.shape[0] * sc)), interpolation=cv2.INTER_LINEAR)
        m = np.clip((cv2.resize(SEG(cv2.resize(img, (478, 850), interpolation=cv2.INTER_AREA)), (W, H)) - 0.35) / 0.3, 0, 1)
        y0 = int(BIG_Y - L.shape[0] / 2); x0 = int(W / 2 - L.shape[1] / 2); ya, yb = max(0, y0), min(H, y0 + L.shape[0]); xa, xb = max(0, x0), min(W, x0 + L.shape[1])
        Lc = L[ya - y0:yb - y0, xa - x0:xb - x0]; A = Lc[..., 3:4] * al * (1 - m[ya:yb, xa:xb, None])
        img[ya:yb, xa:xb] = np.clip(img[ya:yb, xa:xb].astype(np.float32) * (1 - A) + Lc[..., :3] * 255 * A, 0, 255).astype(np.uint8)
    return img
BIG_Y = 330
CAP_Y = 1690

def pill(frame, txt, cx, y, k, fill=RED, tcol=WH, size=40):
    if k <= 0: return
    f = MF("ExtraBold", size); tw = ImageDraw.Draw(Image.new("RGBA", (4, 4))).textlength(txt, font=f)
    lay = Image.new("RGBA", (int(tw + 50), int(size * 1.85)), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
    dl.rounded_rectangle((0, 0, lay.width - 1, lay.height - 1), 20, fill=fill + (255,), outline=WHITE + (255,), width=3)
    dl.text((25, lay.height / 2), txt, font=f, fill=tcol, anchor="lm")
    s = 0.6 + 0.4 * back_out(k, 2.0); lay = fade(lay.resize((int(lay.width * s), int(lay.height * s)), Image.BICUBIC), clamp(k * 3))
    paste(frame, lay, cx - lay.width / 2, y - lay.height / 2, 0.5, 12, (4, 10))

TAGS = {1: [("JOGARAM OBJETOS DENTRO DO CARRO", 0.25, 1.75)]}
def highlight(frame, q, target=None, label="VIDRO TRASEIRO QUEBRADO"):
    x, y, rx, ry = target or WIN; d = ImageDraw.Draw(frame)
    m = Image.new("L", (W, SEAM), 140); ImageDraw.Draw(m).ellipse((x - rx, y - ry, x + rx, y + ry), fill=0)
    m = m.filter(ImageFilter.GaussianBlur(30)).point(lambda v: int(v * clamp(q / 0.25)))
    dark = Image.new("RGBA", (W, SEAM), (0, 0, 0, 255)); dark.putalpha(m); frame.alpha_composite(dark, (0, 0))
    ang = 360 * ease_out(q / 0.45)
    for w_, c in ((16, (255, 255, 255, 110)), (9, RED + (255,))):
        d.arc((x - rx, y - ry, x + rx, y + ry), -90, -90 + ang, fill=c, width=w_)
    if q > 0.35 and int(q / 0.22) % 2 == 0:                       # seta piscando, de baixo para cima
        sx = x; ay = y + ry + 14; L = 150
        shaft = [(sx - 20, ay + 56), (sx + 20, ay + 56), (sx + 20, ay + L), (sx - 20, ay + L)]
        head = [(sx, ay), (sx - 56, ay + 60), (sx + 56, ay + 60)]
        for poly in (shaft, head): d.polygon(poly, fill=RED + (255,), outline=WHITE + (255,))
    pill(frame, label, W / 2, max(250, y - ry - 70), (q - 0.3) / 0.3, size=50)

def split_scene(tt, s, t):
    si = segs.index(s); u = tt - s["t0"]; me = me_src(me_at(tt))
    top, kind, q = clip_panel(si, u); bot = me_panel(me)
    k = 1.0
    canvas = me.copy(); ty = int(-SEAM * (1 - k)); by = int(SEAM + PH * (1 - k))
    if ty + SEAM > 0: canvas[max(0, ty):ty + SEAM] = top[max(0, -ty):]
    if by < H: canvas[by:] = bot[:H - by]
    frame = Image.fromarray(canvas).convert("RGBA"); d = ImageDraw.Draw(frame)
    if kind == "c2f": highlight(frame, q)
    if si == 0 and u < 0.18: frame.alpha_composite(Image.new("RGBA", (W, H), (255, 255, 255, int(200 * (1 - u / 0.18)))))
    if kind == "c1f": highlight(frame, q, (ATK[0], ATK[1], ATK[2], ATK[2] + 30), "ATACANDO O CARRO")
    for txt, a, b in TAGS.get(si, []):
        if a <= u < b: pill(frame, txt, W / 2, 200, (u - a) / 0.3 * (1 if u < b - 0.25 else 0) + (0 if u < b - 0.25 else 1 - (u - (b - 0.25)) / 0.25), size=36)
    d.rectangle((0, ty + SEAM - 2, W, ty + SEAM + 1), fill=GOLD + (int(230 * k),))
    credit(frame, "Imagens: reprodução TikTok", W - 30, SEAM - 150, k)
    draw_caption(frame, t, SEAM, 50, ("me", "au"))
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

def cold_open(t):
    fr = C1_FR[int(clamp((OPEN_CA + t - C1_T0) * FPS, 0, len(C1_FR) - 1))][0:690]
    fg = cv2.resize(fr, (W, int(690 * W / 576)), interpolation=cv2.INTER_LANCZOS4)
    bg = blur_bg(fr, 0.45).astype(np.uint8); y0 = (H - fg.shape[0]) // 2 + 30
    sc = 1 + 0.05 * t / OPEN; img = bg.copy(); img[y0:y0 + fg.shape[0]] = fg
    img = cv2.warpAffine(img, np.float32([[sc, 0, W / 2 * (1 - sc)], [0, sc, H / 2 * (1 - sc)]]), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    frame = Image.fromarray(img).convert("RGBA")
    pill(frame, "CURITIBA (PR) · ATO BOLSONARISTA", W / 2, 230, (t - 0.15) / 0.3, size=40)
    pill(frame, "SOM ORIGINAL", W / 2, 1640, (t - 0.45) / 0.3, fill=GOLD, tcol=NAVY + (255,), size=34)
    credit(frame, "Imagens: reprodução TikTok", W - 30, 1500, 1.0)
    return frame

def render_frame(t):
    if t < OPEN:
        frame = cold_open(t); draw_banners(frame, t); return frame
    if t >= END_IN + 0.35: return end_card(t)
    tt = min(t, EDIT_END - 1e-3); s = seg_at(tt)
    if s is not None and s.get("mode") == "split": frame = split_scene(tt, s, t)
    else:
        st = me_at(tt); z = zoom_suave.nivel(st, ZOOMS) + (0.04 * ease_io((tt - FIN_IN) / FIN_LEN) if tt >= FIN_IN else 0)
        img = big_behind(me_src(st).copy(), st); img = zoom_suave.aplica(img, z, 0.42)
        frame = Image.fromarray(img).convert("RGBA")
        if tt < FIN_IN: draw_caption(frame, t, CAP_Y, 56, ("me", "au"))
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
    if MODE == "info": print("TOTAL", TOTAL, [(s["src"], round(s["t0"], 2), round(s["t1"], 2)) for s in segs], "FIN", FIN_IN, "MUS", MUS_IN); return
    vout = f"{V}/video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
    for i in range(int(round(TOTAL * FPS))): enc.stdin.write(finish(render_frame(i / FPS), i / FPS).tobytes())
    enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", ME, "-ar", "48000", "-ac", "2", f"{V}/me48.wav"], check=True)
    voice = readw(f"{V}/me48.wav"); vt = np.zeros((n, 2), np.float32)
    for s in segs:
        if s["src"] != "me": continue
        p = voice[int(s["a"] * SR):int(s["b"] * SR)].copy(); f = int(0.03 * SR)
        env = np.ones(len(p)); env[:f] = np.linspace(0, 1, f); env[-f:] = np.linspace(1, 0, f)
        t0 = int(s["t0"] * SR); vt[t0:t0 + len(p)] += p * env[:, None]
    writew(f"{V}/voice.wav", vt)
    song = readw(f"{S}/v15/song_vox.wav"); lead = FIN_IN - MUS_IN; Ls = min(len(song), n - int(MUS_IN * SR)); tl = np.arange(Ls) / SR
    gain = np.where(tl < lead, 10 ** ((-22 + 22 * tl / lead) / 20), 1.0) * np.clip(1 - (tl - (TOTAL - MUS_IN - 1.6)) / 1.5, 0, 1)
    sg = np.zeros((n, 2), np.float32); sg[int(MUS_IN * SR):int(MUS_IN * SR) + Ls] = song[:Ls] * gain[:, None]; writew(f"{V}/song.wav", sg)
    subprocess.run([sys.executable, f"{S}/work/music.py", f"{V}/bed.wav", f"{TOTAL + 0.5:.2f}"], check=True)
    bed = readw(f"{V}/bed.wav")[:n]; bed = np.pad(bed, ((0, max(0, n - len(bed))), (0, 0)))[:n]
    gate = np.ones(n, np.float32); gate[int((MUS_IN - 0.3) * SR):] = 0; gate[:int(OPEN * SR)] = 0; gate = np.convolve(gate, np.ones(int(0.5 * SR)) / int(0.5 * SR), "same"); writew(f"{V}/bed_g.wav", bed * gate[:, None])
    ev = [(OPEN - 0.15, sfx.whoosh(0.5), 0.26), (0.15, sfx.click(), 0.4), (segs[2]["t0"] - 0.12, sfx.whoosh(0.5), 0.24), (segs[3]["t0"] - 0.1, sfx.whoosh(0.5), 0.22), (segs[4]["t0"] - 0.1, sfx.whoosh(0.5, False), 0.22)]
    for si, lst in CLIPMAP.items():
        for kind, a, b, ca in lst:
            if a > 0: ev.append((segs[si]["t0"] + a - 0.1, sfx.whoosh(0.4), 0.24))
            if kind in ("c1f", "c2f"): ev.append((segs[si]["t0"] + a + 0.02, sfx.circulo(), 0.22))
    for si, lst in TAGS.items():
        for txt, a, b in lst: ev.append((segs[si]["t0"] + a, sfx.click(), 0.4))
    for a, b, w, _ in BIG: ev.append((out_t(a), sfx.click(), 0.5))
    ev.append((END_IN - 0.3, sfx.whoosh(0.6), 0.25))
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    src = {}
    for nm, path in (("c1", C1), ("c2", C2)):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-ar", "48000", "-ac", "2", f"{V}/{nm}_48.wav"], check=True); src[nm] = readw(f"{V}/{nm}_48.wav")
    ct = np.zeros((n, 2), np.float32); fl = int(0.04 * SR)
    def put(nm, ca, t0, dur, g):
        p = src[nm][int(ca * SR):int((ca + dur) * SR)].copy()
        if len(p) < 2 * fl: return
        env = np.ones(len(p)); env[:fl] = np.linspace(0, 1, fl); env[-fl:] = np.linspace(1, 0, fl)
        i0 = int(t0 * SR); m = min(len(p), n - i0); ct[i0:i0 + m] += p[:m] * (env[:m, None] * g)
    put("c1", OPEN_CA, 0.0, OPEN + 0.15, 1.6)                       # abertura: som dos vândalos em primeiro plano
    for si, lst in CLIPMAP.items():
        sg_ = segs[si]
        for kind, a, b, ca in lst:
            dur = min(b, sg_["t1"] - sg_["t0"]) - a                  # no congelado o som segue correndo
            put("c1" if kind.startswith("c1") else "c2", ca, sg_["t0"] + a, dur, 1.0)
    writew(f"{V}/clipaud.wav", ct)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/bed_g.wav", "-i", f"{V}/song.wav", "-i", f"{V}/clipaud.wav", "-filter_complex",
                    "[1:a]highpass=f=70,asplit=4[vox][k1][k2][k3];[2:a]volume=0.8[sf];[3:a]volume=0.22[bed];[4:a]volume=0.95[sg];[5:a]volume=1.25[cl];"
                    "[cl][k3]sidechaincompress=threshold=0.025:ratio=4:attack=15:release=350[cld];"
                    "[bed][k1]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=500[bedd];[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][bedd][sgd][cld]amix=inputs=5:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
