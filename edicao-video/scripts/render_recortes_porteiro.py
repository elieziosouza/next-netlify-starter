"""Porteiro preso em panelaço contra Flávio Bolsonaro em Maceió (16/10/2026): recortes de jornal com o fato e os detalhes,\ntela dividida com a prisão, respiro O QUE SE SABE e final vai dar PT."""
import sys, math, subprocess, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.path.insert(0, f"{S}/work")
import sfx, zoom_suave
from minitop import make_minitop, make_minifooter, handles_row
from segment_person import PersonSeg
V = f"{S}/v27"; FD = f"{S}/fontdl"; ME, CL = f"{V}/me.mp4", f"{V}/cl.mp4"
W, H, FPS = 1080, 1920, 30
WHITE = (255, 255, 255); GOLD = (214, 182, 116); GOLD_L = (245, 226, 176); NAVY = (6, 34, 58); RED = (210, 30, 36)
WH = (255, 255, 255, 255); GD = GOLD + (255,)
# trechos dele (me.mp4 720x1280): abertura, tela dividida com a prisão (cl.mp4), respiro de recortes, fechamento
PARTS = [("full", 1.15, 7.30), ("split", 7.55, 12.95, 3.0), ("split", 13.05, 17.15, 12.3), ("paper", 3.6), ("full", 18.25, 22.95)]
segs = []; acc = 0.0
for p in PARTS:
    if p[0] == "paper": segs.append(dict(src="paper", t0=acc, t1=acc + p[1])); acc += p[1]; continue
    d = dict(src="me", mode=p[0], a=p[1], b=p[2], t0=acc, t1=acc + p[2] - p[1])
    if p[0] == "split": d["ca"] = p[3]
    segs.append(d); acc += p[2] - p[1]
def out_t(x):
    for s in segs:
        if s["src"] == "me" and s["a"] <= x <= s["b"]: return s["t0"] + x - s["a"]
    raise ValueError(x)
TAIL = (22.95, 26.15)
MUS_IN = out_t(20.18); FIN_IN = segs[-1]["t1"]
LYR = [(0.0, 1.43, "ESSE ANO"), (1.43, 2.87, "O LULA BOTA"), (2.87, 3.87, "O BOLSONARO"), (3.87, 4.87, "PRA MAMAR"),
       (4.87, 5.73, "VAI DAR PT"), (5.73, 6.73, "VAI DAR"), (6.73, 8.23, "VAI DAR PT"), (8.23, 9.43, "VAI DAR PT")]
FIN_LEN = 9.45 - (FIN_IN - MUS_IN); EDIT_END = FIN_IN + FIN_LEN; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
ME_CAPS = [("E AQUELE CASO DO PORTEIRO", 1.34, 2.90), ("QUE FOI PRESO EM FRENTE AO CONDOMÍNIO", 2.90, 4.60),
           ("PORQUE ESTAVA FAZENDO UM PANELAÇO", 4.60, 6.00), ("CONTRA O FLÁVIO BOLSONARO, HEIN?", 6.00, 7.10),
           ("IMAGINA COMO VAI SER O GOVERNO DELE", 7.83, 9.96), ("ELE FOI PRESO!", 11.80, 12.80),
           ("E ACREDITEM SE QUISER,", 13.21, 14.60), ("A POLÍCIA LEVOU A PANELA", 14.60, 16.00), ("COMO PROVA DO CRIME!", 16.00, 17.10),
           ("NÃO TEM, NÃO TEM JEITO.", 18.36, 19.91), ("DIA 25", 20.18, 21.32), ("É INEVITÁVEL!", 21.85, 22.85)]
HOT = {"PORTEIRO", "PRESO", "PANELAÇO", "FLÁVIO", "BOLSONARO,", "GOVERNO", "PRESO!", "PANELA", "CRIME!", "25", "INEVITÁVEL!"}
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
ZOOMS = [(2.90, 4.60, 0.07), (18.36, 22.90, 0.07)]
BIG = [(4.60, 6.10, "PANELAÇO"), (20.18, 21.40, "DIA 25"), (21.85, 22.95, "INEVITÁVEL")]
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
    if s is not None and s["src"] == "me": return s["a"] + (tt - s["t0"])
    return min(TAIL[1], TAIL[0] + (tt - FIN_IN) * 0.6)             # final: o L em câmera lenta leve e depois congela

CL_FR = decode(CL, 0, 17.0, 720, 1280)
def clip_panel(ct):
    fr = CL_FR[int(clamp(ct * FPS, 0, len(CL_FR) - 1))][200:900]     # acima das letras do vídeo original
    big = cv2.resize(fr, (1080, 1050), interpolation=cv2.INTER_LANCZOS4)
    out = np.zeros((SEAM, W, 3), np.uint8); out[:1050] = big; out[1050:] = big[-1]
    return out

def me_panel(img):
    band = img[150:1500]; sc = PH / band.shape[0]
    fg = cv2.resize(band, (int(W * sc), PH), interpolation=cv2.INTER_AREA)
    bg = cv2.resize(cv2.GaussianBlur(cv2.resize(img, (W // 8, H // 8)), (0, 0), 3), (W, H))[int((H - PH) * 0.45):int((H - PH) * 0.45) + PH]
    out = (bg.astype(np.float32) * 0.6).astype(np.uint8); x = (W - fg.shape[1]) // 2; out[:, x:x + fg.shape[1]] = fg
    return out

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

# --------------------------------------------------------------- recortes de jornal (manchetes refeitas, sem logotipo; fonte escrita)
def clipping(kicker, headline, source, w=900, seed=1):
    rng = np.random.default_rng(seed); f = SERIF(64); fk = MF("ExtraBold", 26); fs = MF("SemiBold", 22)
    lines = wrap(headline, f, w - 90); h = 70 + 46 + len(lines) * 74 + 70
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    top = [(x, int(rng.integers(0, 12))) for x in range(0, w + 1, 18)]; bot = [(x, h - 1 - int(rng.integers(0, 12))) for x in range(w, -1, -18)]
    d.polygon(top + [(w, h)] + bot + [(0, h)], fill=(244, 240, 229, 255))
    noise = (rng.normal(0, 5, (h, w))).astype(np.int16)
    a = np.asarray(im).astype(np.int16); a[..., :3] = np.clip(a[..., :3] + noise[..., None], 0, 255); im = Image.fromarray(a.astype(np.uint8), "RGBA"); d = ImageDraw.Draw(im)
    d.text((45, 56), kicker, font=fk, fill=RED + (255,), anchor="lm"); d.rectangle((45, 80, w - 45, 82), fill=(30, 30, 34, 200))
    y = 104
    for ln in lines: d.text((45, y), ln, font=f, fill=(20, 20, 24, 255)); y += 74
    d.text((45, h - 42), source, font=fs, fill=(90, 90, 96, 255), anchor="lm")
    return im
R1 = clipping("MACEIÓ (AL) · NOITE DE 16/10", "PM prende porteiro durante panelaço contra Flávio Bolsonaro", "Fonte: Gazeta de Alagoas e Brasil 247", seed=3)
R2 = clipping("APREENDIDA", "A panela usada no protesto foi apreendida pela polícia", "Fonte: Agenda do Poder e Gazeta de Alagoas", seed=5)
R3 = clipping("NA DELEGACIA", "Ocorrência foi registrada como perturbação do sossego", "Fonte: Gazeta de Alagoas", w=880, seed=7)
R4 = clipping("INVESTIGAÇÃO", "MP Eleitoral abre procedimento e Segurança Pública vai apurar a ação dos PMs", "Fonte: TNH1 e Painel Político", w=880, seed=9)
R0 = clipping("CONTEXTO", "Panelaço foi durante a entrevista de Flávio ao Jornal Nacional", "Fonte: Gazeta de Alagoas e ND+", w=880, seed=11)

def slap(frame, img, cx, cy, q, rot):
    if q < 0: return
    k = ease_out(q / 0.14); s = 1.22 - 0.22 * k
    im = img.rotate(rot, resample=Image.BICUBIC, expand=True)
    im = im.resize((int(im.width * s), int(im.height * s)), Image.BICUBIC)
    paste(frame, fade(im, clamp(q / 0.06)), cx - im.width / 2, cy - im.height / 2, 0.5, 10 + 12 * (1 - k), (8, 14 + 14 * (1 - k)))

RECS = [(R1, 0, 0.7, 540, 820, -2.0), (R2, 1, 1.55, 540, 820, 1.8)]   # (recorte, índice do trecho, entrada, x, y, giro)
yy_, xx_ = np.mgrid[0:H, 0:W]
MAT = (np.array([10, 40, 66], np.float32) + 10 * np.sin(xx_ / 900.0)[..., None]).astype(np.float32)
MAT[((xx_ % 60 < 2) | (yy_ % 60 < 2))] += 26; MAT[((xx_ % 300 < 3) | (yy_ % 300 < 3))] += 30; MAT = np.clip(MAT, 0, 255).astype(np.uint8)
PAPER_RECS = [(R0, 0.35, 560, -1.5), (R3, 1.2, 1010, 2.0), (R4, 2.05, 1460, -1.2)]
def paper_scene(tt, s):
    u = tt - s["t0"]; frame = Image.fromarray(MAT).convert("RGBA"); d = ImageDraw.Draw(frame)
    k = ease_out(u / 0.4); f = MF("ExtraBold", 46); txt = "O QUE SE SABE"; tw = d.textlength(txt, font=f)
    pl = Image.new("RGBA", (int(tw + 70), 84), (0, 0, 0, 0)); dp = ImageDraw.Draw(pl); dp.rounded_rectangle((0, 0, pl.width - 1, 83), 26, fill=GD)
    dp.text((35, 44), txt, font=f, fill=NAVY + (255,), anchor="lm"); paste(frame, fade(pl, k), (W - pl.width) / 2, 230 - 30 * (1 - k), 0.4, 10, (3, 8))
    for img, t0, cy, rot in PAPER_RECS: slap(frame, img, W / 2, cy, u - t0, rot)
    return frame

def split_scene(tt, s, t):
    u = tt - s["t0"]; me = me_src(me_at(tt))
    top = clip_panel(s["ca"] + u); bot = me_panel(me)
    k = ease_io(u / 0.4) if s is segs[1] else 1.0
    canvas = me.copy(); ty = int(-SEAM * (1 - k)); by = int(SEAM + PH * (1 - k))
    if ty + SEAM > 0: canvas[max(0, ty):ty + SEAM] = top[max(0, -ty):]
    if by < H: canvas[by:] = bot[:H - by]
    frame = Image.fromarray(canvas).convert("RGBA"); d = ImageDraw.Draw(frame)
    d.rectangle((0, ty + SEAM - 2, W, ty + SEAM + 1), fill=GOLD + (int(230 * k),))
    credit(frame, "Reprodução: Instagram", W - 30, SEAM - 64, k)
    idx = segs.index(s)
    for img, si, t0, cx, cy, rot in RECS:
        if segs.index(s) == si + 1: slap(frame, img, cx, cy, u - t0, rot)
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

def render_frame(t):
    if t >= END_IN + 0.35: return end_card(t)
    tt = min(t, EDIT_END - 1e-3); s = seg_at(tt)
    if s is not None and s["src"] == "paper": frame = paper_scene(tt, s)
    elif s is not None and s.get("mode") == "split": frame = split_scene(tt, s, t)
    else:
        st = me_at(tt); z = zoom_suave.nivel(st, ZOOMS) + (0.04 * ease_io((tt - FIN_IN) / FIN_LEN) if tt >= FIN_IN else 0)
        img = big_behind(me_src(st).copy(), st); img = zoom_suave.aplica(img, z, 0.42)
        frame = Image.fromarray(img).convert("RGBA")
        if tt < FIN_IN: draw_caption(frame, t, 1450, 56, ("me", "au"))
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
    gate = np.ones(n, np.float32); gate[int((MUS_IN - 0.3) * SR):] = 0; gate = np.convolve(gate, np.ones(int(0.5 * SR)) / int(0.5 * SR), "same"); writew(f"{V}/bed_g.wav", bed * gate[:, None])
    ev = [(0.3, sfx.whoosh(0.5), 0.2), (segs[1]["t0"] - 0.15, sfx.whoosh(0.5), 0.26), (segs[3]["t0"] - 0.12, sfx.whoosh(0.5), 0.24), (segs[4]["t0"] - 0.1, sfx.whoosh(0.5, False), 0.22)]
    ev += [(segs[si + 1]["t0"] + t0, sfx.paper(), 0.55) for _, si, t0, *_ in RECS] + [(segs[si + 1]["t0"] + t0, sfx.thud(), 0.22) for _, si, t0, *_ in RECS]
    ev += [(segs[3]["t0"] + t0, sfx.paper(), 0.55) for _, t0, *_ in PAPER_RECS]
    for a, b, w in BIG: ev.append((out_t(a), sfx.click(), 0.5))
    ev.append((END_IN - 0.3, sfx.whoosh(0.6), 0.25))
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/bed_g.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=70,asplit=3[vox][k1][k2];[2:a]volume=0.8[sf];[3:a]volume=0.22[bed];[4:a]volume=0.95[sg];"
                    "[bed][k1]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=500[bedd];[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][bedd][sgd]amix=inputs=4:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
