"""Corte viral: Dia do Professor (15/10/2026). Eliezio abre, depois trechos do discurso do colega. Palavra-chave gigante atrás da pessoa."""
import sys, math, subprocess, json, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.path.insert(0, f"{S}/work")
import sfx
from minitop import make_minitop, make_minifooter, handles_row
from segment_person import PersonSeg
V = f"{S}/v18"; FD = f"{S}/fontdl"
SRCS = {"me": f"{V}/x36.mp4", "cl": f"{V}/x37.mp4"}
W, H, FPS = 1080, 1920, 30
WHITE = (255, 255, 255); GOLD = (214, 182, 116); GOLD_L = (245, 226, 176); NAVY = (6, 34, 58); RED = (200, 38, 38)
WH = (255, 255, 255, 255); GD = GOLD + (255,)
EDL = [("me", 1.20, 6.68), ("me", 6.98, 10.45), ("me", 10.78, 14.25), ("me", 14.52, 17.00), ("me", 17.28, 18.42), ("me", 19.02, 19.80),
       ("cl", 0.10, 9.60), ("cl", 10.00, 19.00), ("cl", 73.45, 80.40), ("cl", 113.65, 119.05), ("cl", 128.40, 133.75)]
segs = []; acc = 0.0
for src, a, b in EDL:
    segs.append(dict(src=src, a=a, b=b, t0=acc, t1=acc + (b - a))); acc += b - a
EDIT_END = acc; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
def seg_at(t):
    for s in segs:
        if s["t0"] <= t < s["t1"]: return s
    return segs[-1]
def out_t(src, x):
    for s in segs:
        if s["src"] == src and s["a"] <= x <= s["b"]: return s["t0"] + x - s["a"]
    raise ValueError(x)
ME_CAPS = [("NESSE DIA 15 DE OUTUBRO DE 2026", 1.30, 3.90), ("EU GOSTARIA DE DAR OS PARABÉNS AOS PROFESSORES", 3.95, 6.62),
           ("EU ME INCLUO TAMBÉM NESSE MEIO", 7.00, 8.74), ("QUE EU TAMBÉM SOU PROFESSOR", 9.14, 10.42),
           ("EU GOSTARIA DE DEIXAR UM VÍDEO AQUI", 10.81, 12.40), ("DE UM ALERTA DE UM COLEGA NOSSO", 12.40, 14.22),
           ("E DIZ RESPEITO AOS DIAS QUE NÓS ESTAMOS VIVENDO", 14.55, 16.98), ("E É O NOSSO FUTURO", 17.34, 18.38), ("DÁ UMA OLHADA", 19.06, 19.78)]
HOT = {"PROFESSORES", "PROFESSOR", "FUTURO"}
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
def BIGF(s): return ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s)
SEG = PersonSeg(f"{S}/seg/u2net_human_seg.onnx")

# palavras gigantes atrás da pessoa: (fonte, início, fim na fonte, palavra, cor, centro y)
BIG = [("me", 4.85, 6.68, "PROFESSORES", GOLD_L, 268), ("me", 17.30, 18.42, "FUTURO", GOLD_L, 262),
       ("cl", 14.70, 16.40, "ESCOLA PÚBLICA", WHITE, 640), ("cl", 116.90, 119.05, "CIVILIDADE", GOLD_L, 640),
       ("cl", 129.60, 133.75, "ESPERANÇA", GOLD_L, 470)]
_txt = {}
def word_layer(word, col, size):
    key = (word, size)
    if key not in _txt:
        size = int(size * 1.5); f = BIGF(size); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4)))    # Anton: palavra gigante (16/10/2026)
        while d0.textlength(word, font=f) > W - 50: size -= 6; f = BIGF(size)
        lay = Image.new("RGBA", (W, int(size * 1.5)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.text((W / 2, lay.height / 2), word, font=f, fill=col + (255,), anchor="mm")
        sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); blk = Image.new("RGBA", lay.size, (0, 0, 0, 255)); blk.putalpha(lay.getchannel("A").point(lambda v: int(v * 0.55)))
        sh.alpha_composite(blk.filter(ImageFilter.GaussianBlur(14)), (0, 8)); sh.alpha_composite(lay)
        _txt[key] = np.asarray(sh, np.float32) / 255
    return _txt[key]

def behind(img, src_img, t, s):
    """desenha a palavra atrás da pessoa (máscara U2Net)"""
    st = s["a"] + (t - s["t0"])
    for src, a, b, word, col, cy in BIG:
        if src != s["src"] or not (a <= st < b): continue
        u = st - a; k = back_out(u / 0.35, 1.6); al = clamp(u / 0.12) * clamp((b - st) / 0.25)
        lay = word_layer(word, col, 200 if src == "me" else 170)
        sc = 0.75 + 0.25 * k; lh, lw = lay.shape[:2]
        lay = cv2.resize(lay, (int(lw * sc), int(lh * sc)), interpolation=cv2.INTER_LINEAR)
        m = cv2.resize(SEG(src_img), (W, H), interpolation=cv2.INTER_LINEAR)
        m = np.clip((m - 0.35) / 0.3, 0, 1)
        y0 = int(cy - lay.shape[0] / 2); x0 = int(W / 2 - lay.shape[1] / 2)
        ya, yb = max(0, y0), min(H, y0 + lay.shape[0]); xa, xb = max(0, x0), min(W, x0 + lay.shape[1])
        L = lay[ya - y0:yb - y0, xa - x0:xb - x0]; A = L[..., 3:4] * al * (1 - m[ya:yb, xa:xb, None])
        reg = img[ya:yb, xa:xb].astype(np.float32)
        img[ya:yb, xa:xb] = np.clip(reg * (1 - A) + L[..., :3] * 255 * A, 0, 255).astype(np.uint8)
    return img

_cache = {}
def seg_frames(s):
    key = (s["src"], s["a"])
    if key not in _cache:
        _cache.clear(); _cache[key] = decode(SRCS[s["src"]], s["a"], s["b"], 478, 850)
    return _cache[key]

def to_full(img, z=0.0, cy=0.42):
    up = cv2.resize(img, (W, H), interpolation=cv2.INTER_LANCZOS4)
    if z > 0.001:
        sc = 1 + z; c = H * cy; M = np.float32([[sc, 0, W / 2 - W / 2 * sc], [0, sc, c - c * sc]])
        up = cv2.warpAffine(up, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    return up

def fact_chip(frame, t, t0, t1):
    if not (t0 <= t < t1): return
    q = t - t0; k = ease_out(q / 0.45); ko = ease_in((t - (t1 - 0.35)) / 0.35)
    lay = Image.new("RGBA", (720, 118), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, 719, 117), 22, fill=(5, 16, 30, 236), outline=GD, width=2)
    d.text((24, 40), "15 DE OUTUBRO · DIA DO PROFESSOR", font=MF("ExtraBold", 31), fill=WH, anchor="lm")
    d.text((24, 88), "Decreto nº 52.682/1963", font=MF("SemiBold", 25), fill=GOLD_L + (255,), anchor="lm")
    paste(frame, fade(lay, k * (1 - ko)), W / 2 - 360 - 500 * (1 - k), 1560, 0.5, 14, (5, 12))

def render_frame(t):
    if t >= END_IN + 0.35: return end_card(t)
    tt = min(t, EDIT_END - 1e-3); s = seg_at(tt); u = tt - s["t0"]; fr = seg_frames(s)
    src = fr[min(len(fr) - 1, int(u * FPS))]
    if s["src"] == "me":
        img = to_full(src, 0.0)
    else:
        k0 = segs.index(s); z = 0.05 * (u / (s["t1"] - s["t0"]))       # aproximação lenta e suave no discurso
        img = to_full(src, z, 0.40)
    # troca de trecho: leve zoom e desfoque
    q = min(u, s["t1"] - tt)
    first_of_src = segs.index(s) == 0 or segs[segs.index(s) - 1]["src"] != s["src"]
    if q < 0.16 and s is not segs[0] and (first_of_src or u > s["t1"] - s["t0"] - 0.16 and segs.index(s) + 1 < len(segs) and segs[segs.index(s) + 1]["src"] != s["src"]):
        kk = 1 - q / 0.16; img = cv2.GaussianBlur(img, (0, 0), 1 + 8 * kk)
    img = behind(img.copy(), src, tt, s)
    frame = Image.fromarray(img).convert("RGBA")
    if s["src"] == "me":
        draw_caption(frame, t, 1450, 56, ("me", "au"))
        fact_chip(frame, t, 0.15, 3.6)
    else:
        al = clamp((tt - out_t("cl", 0.10)) / 0.4)
        credit(frame, "Reprodução: redes sociais", W - 30, H - 232, al)
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
    if MODE == "info":
        print("TOTAL", TOTAL, [(s["src"], round(s["t0"], 2), round(s["t1"], 2)) for s in segs]); return
    vout = f"{V}/video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
    for i in range(int(round(TOTAL * FPS))):
        enc.stdin.write(finish(render_frame(i / FPS), i / FPS).tobytes())
        if i % 300 == 0: print(f"{i / FPS:.0f}s", flush=True)
    enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    srcw = {}
    for k, f in SRCS.items():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-ar", "48000", "-ac", "2", f"{V}/{k}.wav"], check=True); srcw[k] = readw(f"{V}/{k}.wav")
    vt = np.zeros((n, 2), np.float32)
    for s in segs:
        p = srcw[s["src"]][int(s["a"] * SR):int(s["b"] * SR)].copy() * (1.0 if s["src"] == "me" else 1.15); f = int(0.03 * SR)
        env = np.ones(len(p)); env[:f] = np.linspace(0, 1, f); env[-f:] = np.linspace(1, 0, f)
        t0 = int(s["t0"] * SR); vt[t0:t0 + len(p)] += p * env[:, None]
    writew(f"{V}/voice.wav", vt)
    subprocess.run([sys.executable, f"{S}/work/music.py", f"{V}/music.wav", f"{TOTAL + 0.5:.2f}"], check=True)
    ev = [(0.3, sfx.whoosh(0.6), 0.2)]
    for i, s in enumerate(segs[1:], 1):
        if s["src"] != segs[i - 1]["src"] or s["src"] == "cl": ev.append((s["t0"] - 0.15, sfx.whoosh(0.45), 0.2))
    for src, a, b, word, col, cy in BIG: ev.append((out_t(src, a) + 0.02, sfx.click(), 0.55))   # clique de mouse na entrada da palavra
    ev.append((END_IN - 0.3, sfx.whoosh(0.6), 0.25))
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/music.wav", "-filter_complex",
                    "[1:a]highpass=f=70,asplit=2[vox][key];[2:a]volume=0.8[sf];[3:a]volume=0.28[mus];"
                    "[mus][key]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=500[musd];"
                    f"[vox][sf][musd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
