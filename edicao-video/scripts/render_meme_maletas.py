"""Meme sensacionalista: "acabou a eleição pro Lula, encontraram duas maletas pretas!" -> as imagens mostram
as maletas com a equipe (alarme falso) -> "dia 25 vai ser histórico" com o final "vai dar PT"."""
import sys, math, subprocess, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.path.insert(0, f"{S}/work")
import sfx, zoom_suave
from minitop import make_minitop, make_minifooter, handles_row
from segment_person import PersonSeg
V = f"{S}/v23"; FD = f"{S}/fontdl"; ME, CL = f"{V}/in.mp4", f"{S}/v20/cl.mp4"
W, H, FPS = 1080, 1920, 30
WHITE = (255, 255, 255); GOLD = (214, 182, 116); GOLD_L = (245, 226, 176); NAVY = (6, 34, 58); RED = (210, 30, 36)
WH = (255, 255, 255, 255); GD = GOLD + (255,)
# trechos dele (fonte in.mp4): isca (tela cheia), imagens do Lula, revelação e fechamento
ME_PARTS = [(0.25, 9.95, "full"), (11.12, 16.55, "full")]
CLIP_LEN = 9.4
segs = [dict(src="me", a=0.25, b=9.95, mode="full", t0=0.0, t1=9.70)]
CL_IN = 9.70; CL_OUT = CL_IN + CLIP_LEN
segs.append(dict(src="me", a=11.12, b=16.55, mode="full", t0=CL_OUT, t1=CL_OUT + 5.43))
def out_t(x):
    for s in segs:
        if s["a"] <= x <= s["b"]: return s["t0"] + x - s["a"]
    raise ValueError(x)
MUS_IN = out_t(13.34); FIN_IN = segs[-1]["t1"]
TAIL = 2.55                                                   # imagem real dele depois da fala (o L), sem loop
LYR = [(0.0, 1.43, "ESSE ANO"), (1.43, 2.87, "O LULA BOTA"), (2.87, 3.87, "O BOLSONARO"), (3.87, 4.87, "PRA MAMAR"),
       (4.87, 5.73, "VAI DAR PT"), (5.73, 6.73, "VAI DAR"), (6.73, 8.23, "VAI DAR PT"), (8.23, 9.43, "VAI DAR PT")]
FIN_LEN = 9.45 - (FIN_IN - MUS_IN); EDIT_END = FIN_IN + FIN_LEN; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
PLANE_IN = FIN_IN + TAIL; PLANE_A = 13.4                      # final: Lula chegando no avião, por baixo da letra
ME_CAPS = [("PESSOAL, ACABOU A ELEIÇÃO", 0.41, 1.55), ("PRO LULA!", 1.55, 2.10), ("ACABOU A ELEIÇÃO", 2.20, 3.50), ("PRO LULA!", 3.50, 4.50),
           ("FOI ENCONTRADO COM LULA", 4.73, 5.95), ("DUAS MALETAS PRETAS!", 6.00, 7.45), ("DÁ UMA OLHADA", 8.00, 8.90),
           ("NESSAS IMAGENS AQUI", 8.90, 9.85), ("VIU?", 11.20, 11.80), ("AGORA NÃO ESQUECE!", 11.90, 13.15),
           ("DIA 25", 13.34, 14.60), ("VAI SER HISTÓRICO", 14.97, 16.45)]
HOT = {"LULA!", "LULA", "ACABOU", "MALETAS", "PRETAS!", "VIU?", "25", "HISTÓRICO"}
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
ZOOMS = [(2.20, 4.40, 0.07), (6.00, 7.50, 0.07), (13.34, 16.50, 0.07)]
BIG = [(13.34, 14.65, "DIA 25"), (14.97, 16.55, "HISTÓRICO")]

# --------------------------------------------------------------- imagens do Lula em tela cheia: roda, congela, destaca
CLIPMAP = [("play", 0.0, 2.2, 0.3), ("freeze", 2.2, 3.9, 2.5), ("play", 3.9, 6.0, 2.5), ("freeze", 6.0, 7.7, 4.6), ("play", 7.7, 9.4, 4.6)]
TARGETS = [((965, 1000), 125, "MALETA Nº 1", 2.2, 3.9), ((712, 735), 92, "MALETA Nº 2", 6.0, 7.7)]
STAMP_IN = 7.8
CL_FR = None
def clip_frames():
    global CL_FR
    if CL_FR is None: CL_FR = decode(CL, 0, 20.5, 1080, 1920, "scale=1080:1920:flags=lanczos")
    return CL_FR
def clip_img(u):
    fr = clip_frames()
    for kind, a, b, ca in CLIPMAP:
        if a <= u < b:
            ct = ca if kind == "freeze" else ca + (u - a)
            return fr[int(clamp(ct * FPS, 0, len(fr) - 1))], kind == "freeze"
    return fr[int(clamp((4.6 + u - 7.7) * FPS, 0, len(fr) - 1))], False

def draw_highlight(img_np, u, tg):
    (x, y), r, lab, a, b = tg; q = u - a
    if q < 0 or u > b: return img_np
    img = Image.fromarray(img_np).convert("RGBA")
    m = Image.new("L", (W, H), 150); ImageDraw.Draw(m).ellipse((x - r, y - r, x + r, y + r), fill=0)
    m = m.filter(ImageFilter.GaussianBlur(30)).point(lambda v: int(v * clamp(q / 0.25)))
    dark = Image.new("RGBA", (W, H), (0, 0, 0, 255)); dark.putalpha(m); img.alpha_composite(dark)
    d = ImageDraw.Draw(img); ang = 360 * ease_out(q / 0.45)
    for w_, c in ((16, (255, 255, 255, 110)), (9, RED + (255,))):
        d.arc((x - r, y - r, x + r, y + r), -90, -90 + ang, fill=c, width=w_)
    if q > 0.35 and int(q / 0.22) % 2 == 0:                    # seta piscando, de baixo para cima
        sx = clamp(x, 160, W - 160); ay = y + r + 18; L = 170
        shaft = [(sx - 22, ay + 60), (sx + 22, ay + 60), (sx + 22, ay + L), (sx - 22, ay + L)]
        head = [(sx, ay), (sx - 60, ay + 64), (sx + 60, ay + 64)]
        for poly in (shaft, head): d.polygon(poly, fill=RED + (255,), outline=WHITE + (255,))
    if q > 0.3:
        f = MF("ExtraBold", 46); tw = d.textlength(lab, font=f); k = back_out((q - 0.3) / 0.3, 2.0)
        lx = clamp(x - tw / 2 - 26, 30, W - tw - 82); ly = y - r - 110
        lay = Image.new("RGBA", (int(tw + 52), 80), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        dl.rounded_rectangle((0, 0, lay.width - 1, 79), 22, fill=RED + (255,), outline=WHITE + (255,), width=3)
        dl.text((26, 40), lab, font=f, fill=WH, anchor="lm")
        lay = lay.resize((max(1, int(lay.width * k)), max(1, int(lay.height * k))), Image.BICUBIC)
        img.alpha_composite(lay, (int(lx), int(ly)))
    return np.asarray(img.convert("RGB"))

def clip_full(u):
    fr, frozen = clip_img(u); out = fr
    for tg in TARGETS:
        (x, y), r, lab, a, b = tg
        if a - 0.15 <= u < b + 0.15:
            k = ease_io((u - (a - 0.15)) / 0.5) * (1 - ease_io((u - (b - 0.15)) / 0.3))
            sc = 1 + 0.30 * k; M = np.float32([[sc, 0, x - x * sc], [0, sc, y - y * sc]])
            out = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            if frozen: out = draw_highlight(out, u, tg)
    return out

def stamp(frame, u):
    q = u - STAMP_IN
    if q < 0: return
    k = back_out(q / 0.3, 2.4); f = MF("ExtraBold", 96); txt = "ALARME FALSO"
    d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); tw = d0.textlength(txt, font=f)
    st = Image.new("RGBA", (int(tw + 80), 160), (0, 0, 0, 0)); ds = ImageDraw.Draw(st)
    ds.rounded_rectangle((8, 8, st.width - 8, 152), 20, fill=(255, 255, 255, 225), outline=RED + (255,), width=10)
    ds.text((st.width / 2, 82), txt, font=f, fill=RED + (255,), anchor="mm")
    st = st.rotate(-6, resample=Image.BICUBIC, expand=True); sc = 2.2 - 1.2 * k
    st = fade(st.resize((max(1, int(st.width * sc)), max(1, int(st.height * sc))), Image.BICUBIC), clamp(q / 0.08))
    frame.alpha_composite(st, (int(W / 2 - st.width / 2), int(820 - st.height / 2)))
    if q > 0.35:
        k2 = back_out((q - 0.35) / 0.3, 1.6); f2 = MF("ExtraBold", 50); t2 = "AS MALETAS TAVAM COM A EQUIPE"
        tw2 = d0.textlength(t2, font=f2); lay = Image.new("RGBA", (int(tw2 + 60), 92), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        dl.rounded_rectangle((0, 0, lay.width - 1, 91), 24, fill=GD); dl.text((30, 47), t2, font=f2, fill=NAVY + (255,), anchor="lm")
        sc2 = 0.8 + 0.2 * k2; lay = lay.resize((int(lay.width * sc2), int(92 * sc2)), Image.BICUBIC)
        paste(frame, lay, W / 2 - lay.width / 2, 1060, 0.5, 14, (4, 12))

def urgent(frame, t):
    """isca sensacionalista: faixa URGENTE piscando e borda vermelha pulsando"""
    if t >= CL_IN: return
    k = back_out((t - 0.35) / 0.4, 1.4)
    if t < 0.35: return
    lay = Image.new("RGBA", (W, 80), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); f = MF("ExtraBold", 38)
    w1 = int(d.textlength("URGENTE", font=f)) + 84
    d.rounded_rectangle((0, 4, w1, 76), 36, fill=RED + (255,)); on = int(t * 2.4) % 2 == 0
    d.ellipse((26, 30, 46, 50), fill=(255, 255, 255, 255 if on else 100)); d.text((58, 41), "URGENTE", font=f, fill=WH, anchor="lm")
    f2 = MF("Bold", 32); t2 = "ÚLTIMA HORA"; w2 = int(d.textlength(t2, font=f2)) + 50
    d.rounded_rectangle((w1 + 12, 4, w1 + 12 + w2, 76), 36, fill=(4, 14, 26, 215), outline=(255, 255, 255, 90), width=2)
    d.text((w1 + 37, 41), t2, font=f2, fill=WH, anchor="lm")
    paste(frame, fade(lay.crop((0, 0, w1 + w2 + 16, 80)), clamp((t - 0.35) / 0.2)), 40, 180 - int(40 * (1 - k)), 0.45, 14, (4, 10))
    pul = 0.0
    for a in (0.35, out_t(6.0)): pul = max(pul, math.exp(-max(0, t - a) / 0.35) * (t >= a))
    if pul > 0.02:
        b = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(b).rectangle((0, 0, W - 1, H - 1), outline=RED + (int(230 * pul),), width=22)
        frame.alpha_composite(b.filter(ImageFilter.GaussianBlur(6)))

# --------------------------------------------------------------- ele
_me = {}
def me_src(a):
    key = int(a // 6)
    if key not in _me:
        if len(_me) > 3: _me.clear()
        _me[key] = decode(ME, key * 6, key * 6 + 6.2, 1080, 1920, "scale=1080:1920:flags=lanczos")
    fr = _me[key]; return fr[min(len(fr) - 1, int((a - key * 6) * FPS))]
def me_at(tt):
    for s in segs:
        if s["t0"] <= tt < s["t1"]: return s["a"] + (tt - s["t0"])
    return min(19.15, 16.55 + (tt - FIN_IN))

def big_behind(img, st):
    for a, b, word in BIG:
        if not (a <= st < b): continue
        u = st - a; k = back_out(u / 0.35, 1.6); al = clamp(u / 0.12) * clamp((b - st) / 0.25)
        size = 230; f = BIGF(size); d0 = ImageDraw.Draw(Image.new("L", (4, 4)))
        while d0.textlength(word, font=f) > W - 100: size -= 6; f = BIGF(size)
        lay = Image.new("RGBA", (W, int(size * 1.4)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        col = RED if word in ("ACABOU?", "MALETAS") else GOLD_L
        d.text((W / 2 + 5, lay.height / 2 + 10), word, font=f, fill=(0, 0, 0, 140), anchor="mm"); d.text((W / 2, lay.height / 2), word, font=f, fill=col + (255,), anchor="mm")
        L = np.asarray(lay, np.float32) / 255; sc = 0.78 + 0.22 * k
        L = cv2.resize(L, (int(L.shape[1] * sc), int(L.shape[0] * sc)), interpolation=cv2.INTER_LINEAR)
        # fundo escuro confunde a máscara; a palavra fica acima da cabeça (topo da cabeça em y≈500), sem encostar
        y0 = int(372 - L.shape[0] / 2); x0 = int(W / 2 - L.shape[1] / 2); ya, yb = max(0, y0), min(H, y0 + L.shape[0]); xa, xb = max(0, x0), min(W, x0 + L.shape[1])
        Lc = L[ya - y0:yb - y0, xa - x0:xb - x0]; A = Lc[..., 3:4] * al
        img[ya:yb, xa:xb] = np.clip(img[ya:yb, xa:xb].astype(np.float32) * (1 - A) + Lc[..., :3] * 255 * A, 0, 255).astype(np.uint8)
    return img

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
    if CL_IN <= tt < CL_OUT:                                     # imagens do Lula
        u = tt - CL_IN; img = clip_full(u)
        if u < 0.16: img = cv2.GaussianBlur(img, (0, 0), 1 + 8 * (1 - u / 0.16))
        if u > CLIP_LEN - 0.16: img = cv2.GaussianBlur(img, (0, 0), 1 + 8 * ((u - CLIP_LEN + 0.16) / 0.16))
        frame = Image.fromarray(img).convert("RGBA"); stamp(frame, u)
        credit(frame, "Reprodução: Instagram", W - 30, H - 232, clamp(u / 0.4))
    elif tt >= PLANE_IN:                                         # final: chegando no avião
        fr = clip_frames(); q = tt - PLANE_IN
        img = fr[int(clamp((PLANE_A + q) * FPS, 0, len(fr) - 1))]
        if q < 0.16: img = cv2.GaussianBlur(img, (0, 0), 1 + 8 * (1 - q / 0.16))
        frame = Image.fromarray(img).convert("RGBA"); lyrics(frame, t)
        credit(frame, "Reprodução: Instagram", W - 30, 200, clamp(q / 0.4))
    else:
        st = me_at(tt); z = zoom_suave.nivel(st, ZOOMS) + (0.03 * ease_io((tt - FIN_IN) / 2.0) if tt >= FIN_IN else 0)
        img = big_behind(me_src(st).copy(), st); img = zoom_suave.aplica(img, z, 0.40)
        frame = Image.fromarray(img).convert("RGBA")
        if tt < FIN_IN: draw_caption(frame, t, 1450, 56, ("me", "au"))
        else: lyrics(frame, t)
        urgent(frame, tt)
    draw_banners(frame, t)
    if t >= END_IN: frame.alpha_composite(fade(end_card(t), clamp((t - END_IN) / 0.35)))
    return frame

def readw(p):
    w = wave.open(p); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, w.getnchannels()) / 32768
    return a if a.shape[1] == 2 else np.repeat(a, 2, 1)
def writew(p, a):
    with wave.open(p, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(48000); w.writeframes((np.clip(a, -1, 1) * 32000).astype(np.int16).tobytes())
def siren(dur=1.1, SR=48000):
    t = np.arange(int(dur * SR)) / SR; f = np.where((t // 0.22) % 2 == 0, 960, 760)
    ph = 2 * np.pi * np.cumsum(f) / SR; s = 0.6 * np.sin(ph) + 0.25 * np.sin(2 * ph)
    env = np.clip(t / 0.03, 0, 1) * np.clip((dur - t) / 0.25, 0, 1); s = s * env
    return np.stack([s, s], 1)

def main():
    if MODE == "lib": return
    if MODE.startswith("frames"):
        ts = [float(x) for x in MODE.split(":")[1].split(",")]
        outs = [finish(render_frame(t), t).resize((360, 640), Image.LANCZOS) for t in ts]
        sheet = Image.new("RGB", (360 * len(outs), 640)); [sheet.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]
        sheet.save(OUTFILE, quality=90); return
    if MODE == "info": print("TOTAL", TOTAL, "CL", CL_IN, CL_OUT, "FIN", FIN_IN, "MUS", MUS_IN, "PLANE", PLANE_IN, "END", END_IN); return
    vout = f"{V}/video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
    for i in range(int(round(TOTAL * FPS))):
        enc.stdin.write(finish(render_frame(i / FPS), i / FPS).tobytes())
    enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    for f, o in ((ME, "me48.wav"), (CL, "cl48.wav")): subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-ar", "48000", "-ac", "2", f"{V}/{o}"], check=True)
    voice = readw(f"{V}/me48.wav"); vt = np.zeros((n, 2), np.float32)
    for s in segs:
        p = voice[int(s["a"] * SR):int(s["b"] * SR)].copy(); f = int(0.03 * SR)
        env = np.ones(len(p)); env[:f] = np.linspace(0, 1, f); env[-f:] = np.linspace(1, 0, f)
        t0 = int(s["t0"] * SR); vt[t0:t0 + len(p)] += p * env[:, None]
    writew(f"{V}/voice.wav", vt)
    # som do vídeo do Lula durante as imagens (sem os congelamentos tocarem trechos repetidos: o áudio corre contínuo)
    cl = readw(f"{V}/cl48.wav"); ct = np.zeros((n, 2), np.float32); a0 = int(0.3 * SR); L = int(CLIP_LEN * SR)
    seg_ = cl[a0:a0 + L].copy(); fo = int(0.4 * SR); seg_[-fo:] *= np.linspace(1, 0, fo)[:, None]; seg_[:int(0.15 * SR)] *= np.linspace(0, 1, int(0.15 * SR))[:, None]
    ct[int(CL_IN * SR):int(CL_IN * SR) + len(seg_)] = seg_; writew(f"{V}/clip.wav", ct)
    song = readw(f"{S}/v15/song_vox.wav"); lead = FIN_IN - MUS_IN; Ls = min(len(song), n - int(MUS_IN * SR)); tl = np.arange(Ls) / SR
    gain = np.where(tl < lead, 10 ** ((-22 + 22 * tl / lead) / 20), 1.0) * np.clip(1 - (tl - (TOTAL - MUS_IN - 1.6)) / 1.5, 0, 1)
    sg = np.zeros((n, 2), np.float32); sg[int(MUS_IN * SR):int(MUS_IN * SR) + Ls] = song[:Ls] * gain[:, None]; writew(f"{V}/song.wav", sg)
    ev = [(0.35, siren(), 0.22), (0.35, sfx.thud(), 0.35), (out_t(6.0), sfx.thud(), 0.35), (CL_IN - 0.12, sfx.whoosh(0.5), 0.26)]
    for (_, _, _, a, b) in TARGETS: ev += [(CL_IN + a, sfx.thud(), 0.26), (CL_IN + a + 0.05, sfx.click(), 0.4)]
    ev += [(CL_IN + STAMP_IN, sfx.thud(), 0.4), (CL_IN + STAMP_IN + 0.02, sfx.paper(), 0.25), (CL_OUT - 0.1, sfx.whoosh(0.5, False), 0.22)]
    for a, b, w in BIG: ev.append((out_t(a), sfx.click(), 0.5))
    ev += [(PLANE_IN - 0.1, sfx.whoosh(0.5), 0.2), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/clip.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=70,asplit=3[vox][k1][k2];[2:a]volume=0.8[sf];[3:a]volume=1.25[cl];[4:a]volume=0.9[sg];"
                    "[cl][k1]sidechaincompress=threshold=0.05:ratio=2.5:attack=30:release=500[cld];[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][cld][sgd]amix=inputs=4:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
