"""React: Eliezio x Paulista 11/10. Você na janelinha durante as imagens do ato, depois "na frente" da Paulista com os números."""
import sys, math, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.path.insert(0, f"{S}/work")
import sfx, grading
from minitop import make_minitop, make_minifooter, handles_row
from segment_person import PersonSeg
GRADE = grading.Fast(grading.cinema, f"{S}/grade/lut_cinema.npy", 0.1, 6)

V = f"{S}/v10"; FD = f"{S}/fontdl"
ME, AE, IG = f"{V}/me.mp4", f"{V}/aereo.mp4", f"{V}/ig.mp4"
W, H, FPS = 1080, 1920, 30
WHITE = (255, 255, 255); GOLD = (214, 182, 116); GOLD_L = (245, 226, 176); NAVY = (6, 34, 58); RED = (200, 38, 38)
WH = (255, 255, 255, 255); GD = GOLD + (255,)
HOT = set()

# ---------------------------------------------------------------- edit decision list (fonte, entrada, saída)
EDL = [("me", 0.40, 7.05), ("ae", 9.00, 13.60), ("ig", 0.30, 4.80), ("me", 7.40, 24.05)]
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
    raise ValueError((src, x))
CL_IN = out_t("ae", 9.0); IG_IN = out_t("ig", 0.3); CL_OUT = out_t("ig", 4.8); ST_IN = out_t("me", 7.40)

ME_CAPS = [("TEM MUITO BOLSONARISTA CONTANDO VITÓRIA ANTES DO TEMPO, HEIN?", 0.57, 3.66), ("CUIDADO!", 3.80, 4.49),
           ("DÁ UMA OLHADINHA NA PAULISTA DE ONTEM", 5.14, 6.89),
           ("SEM CONTAR QUE MAIS DE 33 MILHÕES DE BRASILEIROS APTOS A VOTAR NÃO VOTARAM NO PRIMEIRO TURNO", 7.61, 13.28),
           ("E EU ESTOU VENDO ATÉ OS DE MAIS DE 70 SE ORGANIZANDO", 13.75, 16.45),
           ("PORQUE NÃO VÃO ABRIR MÃO DE VOTAR AGORA NO SEGUNDO TURNO", 16.45, 19.26),
           ("ENTÃO SEGURA A ONDA AÍ QUE DIA 25", 19.74, 22.22), ("VAI SER HISTÓRICO", 22.78, 23.78)]
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

def draw_caption(frame, t, ccy, font_size, tracks, xoff=0):
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
        x = (W - region.width) // 2 + int(xoff); y = int(ccy - region.height / 2)
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
    full = me_full(me_img, t).astype(np.float32) * VIG
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
    a = np.asarray(frame.convert("RGB"), np.float32)
    g = cv2.resize(GRAIN[int(t * FPS) % len(GRAIN)], (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    return Image.fromarray(np.clip(a + g, 0, 255).astype(np.uint8))


CAPS = build_caps(ME_CAPS, "me", 5, "me")
top, TOPH = make_minitop(W, f"{FD}/Montserrat-SemiBold.ttf")
FACE = (239.0, 380.0)
REACT = np.stack([GRADE(f) for f in decode(ME, 24.4, 36.3, 478, 850)])       # ele assistindo, em silêncio
def react_frame(t):
    n = len(REACT); period = 2 * (n - 1); k = int(t * FPS * 0.85) % period
    return REACT[k if k < n else period - k]

# ---------------------------------------------------------------- imagens do ato em cartões empilhados
AECROP = "crop=610:840:655:0"; AW, AH = 610, 840          # faixa vertical do aéreo, sem a legenda do UOL
IGCROP = "crop=720:1000:0:140"; IW, IH = 720, 1000
CA_W = 640; CA_H = int(AH * CA_W / AW)                    # 881
CI_W = 590; CI_H = int(IH * CI_W / IW)                    # 819
WINC = (380, 1262, 700, 1690)
def win_k(t):
    return ease_io((t - CL_IN) / 0.6) * (1 - ease_io((t - (CL_OUT - 0.55)) / 0.55))

def card_rgba(img, w, h):
    return rounded(cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA), 26, 3)

_last_ae = [None]
def clips_frame(img, t, src):
    if src == "ae": _last_ae[0] = img
    ae = _last_ae[0] if _last_ae[0] is not None else img
    bg = blur_bg(ae, 0.26)
    k = win_k(t)
    frame = compose_me_layer(bg, react_frame(t), t, WINC, k)
    ex = ease_in((t - (CL_OUT - 0.5)) / 0.5)
    # camada 1: aéreo, desce do topo em 3D; recua quando entra o vídeo do Lula
    u = t - CL_IN
    rec = ease_io((t - IG_IN) / 0.6)
    def ya(q): return -820 * (1 - ease_out(q / 0.6)) - 1000 * ease_in((t - (CL_OUT - 0.5)) / 0.5)
    tilt = clamp(1 - ease_out(u / 0.75) + ex)
    rgba = card_rgba(ae, CA_W, CA_H)
    im = Image.fromarray(persp(rgba, "top", 0.06 + 0.24 * tilt) if tilt > 0.003 else rgba, "RGBA")
    if rec > 0.01:
        arr = np.asarray(im).copy(); arr[..., :3] = (arr[..., :3] * (1 - 0.45 * rec)).astype(np.uint8); im = Image.fromarray(arr, "RGBA")
        sc = 1 - 0.12 * rec; im = im.resize((int(im.width * sc), int(im.height * sc)), Image.BICUBIC)
    dy = ya(u); vy = dy - ya(u - 1 / FPS)
    x = W / 2 - im.width / 2 - 150 * rec; y = 168 + dy + 20 * rec
    paste(frame, im, x, y, 0.6, 22, (10, 26), (0, vy))
    al = clamp((u - 0.7) / 0.4) * (1 - rec)
    if al > 0: credit(frame, "Imagens: @MidiaNINJA / X · via UOL", W / 2 + CA_W / 2 - 16, 168 + CA_H - 50, al)
    # camada 2: Lula no meio do ato, entra pela direita girando, por cima do aéreo
    if src == "ig":
        ui = t - IG_IN
        def xi(q): return 760 * (1 - ease_out(q / 0.6)) + 1100 * ease_in((t - (CL_OUT - 0.5)) / 0.5)
        rgba = card_rgba(img, CI_W, CI_H)
        a = 0.03 + 0.45 * (1 - ease_out(ui / 0.7)) + 0.4 * ex
        im = Image.fromarray(persp(rgba, "right", a), "RGBA")
        dx = xi(ui); vx = dx - xi(ui - 1 / FPS)
        paste(frame, im, W / 2 - CI_W / 2 + 110 + dx, 228, 0.7, 24, (12, 28), (vx, 0))
        if ui > 0.7: credit(frame, "Vídeo: Instagram", W / 2 + 110 + CI_W / 2 - 16 + dx, 228 + CI_H - 50, clamp((ui - 0.7) / 0.4) * (1 - ex))
    # rótulo do ato
    kl = ease_out((u - 0.5) / 0.5) * (1 - ex)
    if kl > 0:
        lay = Image.new("RGBA", (W, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.text((W / 2, 22), "AV. PAULISTA  ·  11/10", font=MF("Bold", 24), fill=GD, anchor="mm")
        d.text((W / 2, 62), "Ato pró-Lula ocupou sete quarteirões", font=MF("ExtraBold", 36), fill=WH, anchor="mm")
        d.text((W / 2, 102), "Fonte: UOL  ·  cerca de 1 milhão de pessoas, segundo os organizadores", font=MF("SemiBold", 20), fill=(255, 255, 255, 170), anchor="mm")
        frame.alpha_composite(fade(lay, kl), (0, int(1112 + 14 * (1 - kl))))
    return frame

# ---------------------------------------------------------------- ele "na Paulista": fundo trocado pelo aéreo
SEG = PersonSeg(f"{S}/seg/u2net_human_seg.onnx")
_prev_m = [None]
def person_matte(img):
    m = SEG(img).astype(np.float32)
    m = np.clip((m - 0.5) * 3.2 + 0.5, 0, 1)
    if _prev_m[0] is not None: m = 0.55 * m + 0.45 * _prev_m[0]           # sem tremer entre quadros
    _prev_m[0] = m
    m = cv2.erode(m, np.ones((3, 3), np.uint8))
    return cv2.GaussianBlur(m, (0, 0), 1.1)

def paulista_bg(ae):
    sc = max(W / AW, H / AH); big = cv2.resize(ae, (int(AW * sc) + 2, int(AH * sc) + 2), interpolation=cv2.INTER_LINEAR)
    x0 = (big.shape[1] - W) // 2; big = big[:H, x0:x0 + W]
    big = cv2.GaussianBlur(big, (0, 0), 7).astype(np.float32)
    g = np.clip((yy - 200) / 1500, 0, 1)[..., None]                       # mais escuro embaixo
    return big * (0.62 - 0.25 * g) + np.array([2, 6, 14], np.float32) * 0.5

def me_in_paulista(img, matte, ae, t, z=0.0):
    sc = W / 478 * (1.03 + 0.01 * math.sin(t * 0.3) + z)
    M = np.float32([[sc, 0, W / 2 - FACE[0] * sc], [0, sc, FACE[1] * W / 478 - FACE[1] * sc]])
    fg = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    mt = cv2.warpAffine(matte, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)[..., None]
    bg = paulista_bg(ae)
    # luz de contorno: um pouco da cor do fundo "vaza" na borda (integra a pessoa na cena)
    edge = np.clip(mt * (1 - cv2.GaussianBlur(mt[..., 0], (0, 0), 6)[..., None]) * 2.2, 0, 1)
    fg = fg * (1 - 0.35 * edge) + cv2.GaussianBlur(bg, (0, 0), 10) * 1.4 * 0.35 * edge
    out = fg * mt + bg * (1 - mt)
    return np.clip(out * VIG, 0, 255).astype(np.uint8)

# cartões de número em vidro fosco, no espaço acima da cabeça
CARD_X, CARD_Y, CARD_W, CARD_H = 90, 168, 900, 262
def stat_content(i, u):
    im = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if i == 0:
        v = 33.4 * ease_out((u - 0.2) / 1.1)
        d.text((44, 46), "ABSTENÇÃO NO 1º TURNO", font=MF("Bold", 24), fill=GD, anchor="lm")
        d.text((40, 128), f"{v:.1f} MILHÕES".replace(".", ","), font=MF("ExtraBold", 92), fill=WH, anchor="lm")
        d.text((44, 204), "não votaram  ·  21% de abstenção, a maior desde 1998", font=MF("SemiBold", 25), fill=(226, 232, 240, 255), anchor="lm")
        src = "Fonte: TSE"
    elif i == 1:
        d.text((44, 46), "VOTO FACULTATIVO", font=MF("Bold", 24), fill=GD, anchor="lm")
        d.text((40, 128), "+70 ANOS", font=MF("ExtraBold", 92), fill=WH, anchor="lm")
        d.text((44, 204), "cerca de metade não votou no 1º turno", font=MF("SemiBold", 25), fill=(226, 232, 240, 255), anchor="lm")
        src = "Fonte: presidente do TSE"
    else:
        d.text((CARD_W / 2, 50), "SEGUNDO TURNO", font=MF("Bold", 26), fill=GD, anchor="mm")
        k = back_out((u - 0.15) / 0.5, 1.4); f = MF("ExtraBold", int(118 * (0.7 + 0.3 * k)))
        d.text((CARD_W / 2, 142), "DIA 25", font=f, fill=GOLD_L + (255,), anchor="mm")
        lw = int(150 * ease_out((u - 0.5) / 0.6)); d.rectangle((CARD_W / 2 - lw, 212, CARD_W / 2 + lw, 214), fill=GD)
        src = None
    if src: d.text((CARD_W - 28, 46), src, font=MF("SemiBold", 19), fill=(255, 255, 255, 150), anchor="rm")
    return im

STATS = [(out_t("me", 7.75), out_t("me", 13.45)), (out_t("me", 13.85), out_t("me", 19.45)), (out_t("me", 19.85), out_t("me", 24.05))]
def draw_stat(frame, t):
    for i, (a, b) in enumerate(STATS):
        if not (a <= t < b): continue
        u = t - a; dur = b - a
        kin = ease_out(u / 0.6); kout = ease_in((u - (dur - 0.4)) / 0.4) if i < 2 else ease_in((t - (EDIT_END - 0.35)) / 0.35)
        # vidro fosco: o próprio quadro desfocado e escurecido atrás do cartão
        base = np.asarray(frame.convert("RGB"))[CARD_Y:CARD_Y + CARD_H, CARD_X:CARD_X + CARD_W].astype(np.float32)
        glass = cv2.GaussianBlur(base, (0, 0), 16) * 0.42 + np.array([4, 14, 28], np.float32) * 0.58
        gl = Image.fromarray(np.clip(glass, 0, 255).astype(np.uint8)).convert("RGBA")
        m = Image.new("L", (CARD_W, CARD_H), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, CARD_W - 1, CARD_H - 1), 26, fill=255); gl.putalpha(m)
        ImageDraw.Draw(gl).rounded_rectangle((1, 1, CARD_W - 2, CARD_H - 2), 26, outline=GOLD + (210,), width=2)
        gl.alpha_composite(stat_content(i, u))
        tilt = clamp((1 - kin) + kout)
        arr = persp(np.asarray(gl), "top", 0.05 + 0.4 * tilt) if tilt > 0.003 else np.asarray(gl)
        im = fade(Image.fromarray(arr, "RGBA"), clamp(kin * 1.6) * (1 - kout))
        def yy_(q): return 60 * (1 - ease_out(q / 0.6)) - 90 * (ease_in((q - (dur - 0.4)) / 0.4) if i < 2 else 0)
        dy = yy_(u); vy = dy - yy_(u - 1 / FPS)
        paste(frame, im, CARD_X, CARD_Y + dy, 0.55, 20, (8, 20), (0, vy))

# ---------------------------------------------------------------- o L escrito pela mão
import json
_HJ = json.load(open(f"{V}/hand_smooth.json")); H_T0 = _HJ["t0"]; H_P = np.array(_HJ["pts"], np.float32)
L_START = 22.05; L_V = 0.32; L_H = 0.26                    # tempos na fonte (s)
_rngL = np.random.default_rng(11)
SPARKS = [(L_START + _rngL.uniform(0, L_V + L_H), _rngL.uniform(-1, 1), _rngL.uniform(-1.6, -0.2), _rngL.uniform(0.35, 0.8), _rngL.uniform(2, 5)) for _ in range(46)]
def hand_pts(srct):
    i = (srct - H_T0) * FPS; i0 = int(clamp(math.floor(i), 0, len(H_P) - 1)); i1 = min(len(H_P) - 1, i0 + 1); f = clamp(i - i0)
    p = H_P[i0] * (1 - f) + H_P[i1] * f
    return (p[0], p[1]), (p[2], p[3]), (p[4], p[5])
def to_out(p, t, z):
    sc = W / 478 * (1.03 + 0.01 * math.sin(t * 0.3) + z)
    return (sc * p[0] + W / 2 - FACE[0] * sc, sc * p[1] + FACE[1] * W / 478 - FACE[1] * sc)

def l_progress(srct):
    """0..1 ao longo do L (vertical e depois horizontal)"""
    u = srct - L_START
    if u <= 0: return 0.0
    if u < L_V: return 0.55 * ease_io(u / L_V)
    return 0.55 + 0.45 * ease_out((u - L_V) / L_H)

def l_path(tip, corner, thumb, k):
    lv = math.dist(tip, corner); lh = math.dist(corner, thumb)
    if k <= 0.55:
        q = k / 0.55; return [tip, (lerp(tip[0], corner[0], q), lerp(tip[1], corner[1], q))]
    q = (k - 0.55) / 0.45; return [tip, corner, (lerp(corner[0], thumb[0], q), lerp(corner[1], thumb[1], q))]

def draw_L(frame, t, z, srct):
    k = l_progress(srct)
    if k <= 0: return
    fadeout = 1 - ease_in((t - (EDIT_END - 0.35)) / 0.35)
    tip, corner, thumb = [to_out(p, t, z) for p in hand_pts(srct)]
    # o traço fica um pouco à frente da mão (do lado de fora do dedo e do polegar), como luz escrita no ar
    cx = min(tip[0], corner[0]) - 62                         # por fora do dedo, sem encostar no rosto
    tip = (cx + 8, tip[1] - 10); corner = (cx, corner[1] + 44); thumb = (thumb[0] + 30, corner[1])
    path = l_path(tip, corner, thumb, k)
    done = srct - (L_START + L_V + L_H)
    pulse = 1 + 0.9 * math.exp(-max(0, done) / 0.25) * (done > 0) + 0.12 * math.sin(t * 5)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.line(path, fill=GOLD + (255,), width=16, joint="curve")
    for p in (path[0], path[-1]): d.ellipse((p[0] - 8, p[1] - 8, p[0] + 8, p[1] + 8), fill=GOLD + (255,))
    core = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dc = ImageDraw.Draw(core)
    dc.line(path, fill=(255, 248, 225, 255), width=6, joint="curve")
    for p in (path[0], path[-1]): dc.ellipse((p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3), fill=(255, 248, 225, 255))
    g1 = lay.filter(ImageFilter.GaussianBlur(10)); g2 = lay.filter(ImageFilter.GaussianBlur(30))
    a = fadeout
    frame.alpha_composite(fade(g2, a * min(1, 0.7 * pulse))); frame.alpha_composite(fade(g1, a * min(1, 0.8 * pulse)))
    frame.alpha_composite(fade(lay, a)); frame.alpha_composite(fade(core, a))
    # ponta da "caneta" brilhando enquanto escreve
    if k < 1:
        px, py = path[-1]; fl = Image.new("RGBA", (160, 160), (0, 0, 0, 0)); df = ImageDraw.Draw(fl)
        for r, al in ((70, 40), (40, 90), (18, 200), (8, 255)): df.ellipse((80 - r, 80 - r, 80 + r, 80 + r), fill=GOLD_L + (al,))
        fl = fl.filter(ImageFilter.GaussianBlur(8)); frame.alpha_composite(fl, (int(px - 80), int(py - 80)))
    # faíscas que saem do traço
    sp = ImageDraw.Draw(frame)
    for st, vx, vy, life, r in SPARKS:
        age = srct - st
        if age < 0 or age > life: continue
        kk = clamp((st - L_START) / (L_V + L_H)); kk = l_progress(st)
        bx, by = l_path(tip, corner, thumb, kk)[-1]
        x = bx + vx * 140 * age; y = by + vy * 120 * age + 160 * age * age
        al = int(255 * (1 - age / life) * fadeout); rr = r * (1 - 0.5 * age / life)
        sp.ellipse((x - rr, y - rr, x + rr, y + rr), fill=GOLD_L + (al,))

# ---------------------------------------------------------------- render
_cache = {}
def seg_frames(s):
    key = (s["src"], s["a"])
    if key not in _cache:
        _cache.clear()
        if s["src"] == "me":
            fr = np.stack([GRADE(f) for f in decode(ME, s["a"], s["b"], 478, 850)])
            _cache[key] = fr
        elif s["src"] == "ae": _cache[key] = np.stack([GRADE(f) for f in decode(AE, s["a"], s["b"], AW, AH, AECROP)])
        else: _cache[key] = np.stack([GRADE(f) for f in decode(IG, s["a"], s["b"], IW, IH, IGCROP)])
    return _cache[key]
AEBG = None
def aebg_frame(u):
    global AEBG
    if AEBG is None: AEBG = np.stack([GRADE(f) for f in decode(AE, 14.0, 31.0, AW, AH, AECROP)])
    return AEBG[min(len(AEBG) - 1, int(u * FPS))]

def render_frame(t):
    if t >= END_IN + 0.35: return end_card(t)
    tt = min(t, EDIT_END - 1e-3); s = seg_at(tt); u = tt - s["t0"]; fr = seg_frames(s)
    img = fr[min(len(fr) - 1, int(u * FPS))]
    if s["src"] == "me" and s["a"] < 1:
        z = 0.03 * smooth((t - out_t("me", 3.75)) / 0.25) * (1 - smooth((t - out_t("me", 4.7)) / 0.5))   # "Cuidado!"
        frame = Image.fromarray(np.clip(me_full(img, t, z).astype(np.float32) * VIG, 0, 255).astype(np.uint8)).convert("RGBA")
        draw_caption(frame, t, 1450, 56, ("me",))
        react_tag(frame, t, "REACT  ·  PAULISTA ONTEM", 0.9, 6.2)
    elif s["src"] == "me":
        z = 0.035 * smooth((t - out_t("me", 19.7)) / 3.5)                                         # aproxima no "dia 25"
        out = me_in_paulista(img, person_matte(img), aebg_frame(u), t, z).astype(np.float32)
        kin = ease_io(u / 0.6)                                                                    # a janelinha cresce até a tela cheia
        if kin < 1:
            bg = blur_bg(_last_ae[0], 0.26) if _last_ae[0] is not None else NAVYBG.copy()
            x0, y0, x1, y1 = [lerp(a, b, kin) for a, b in zip(WINC, (0, 0, W, H))]
            w, h = int(x1 - x0), int(y1 - y0)
            ch = min(H, int(W * h / w)); cy0 = int(clamp((800 - ch * 0.42) / (H - ch + 1e-6)) * (H - ch)) if ch < H else 0
            cw = int(ch * w / h); cx0 = (W - cw) // 2
            win = cv2.resize(out[cy0:cy0 + ch, cx0:cx0 + cw], (w, h), interpolation=cv2.INTER_AREA)
            m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), int(28 * (1 - kin)), fill=255)
            m = np.asarray(m, np.float32)[..., None] / 255
            bx, by = int(x0), int(y0); out = bg.copy()
            out[by:by + h, bx:bx + w] = out[by:by + h, bx:bx + w] * (1 - m) + win * m
        frame = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")
        draw_stat(frame, t)
        srct = s["a"] + u
        draw_L(frame, t, z, srct)
        draw_caption(frame, t, 1450, 56, ("me",), 120 * smooth((srct - 21.9) / 0.3))
    else:
        frame = clips_frame(img, t, s["src"])
    draw_banners(frame, t)
    if t >= END_IN: frame.alpha_composite(fade(end_card(t), clamp((t - END_IN) / 0.35)))
    return frame

def main():
    if MODE.startswith("frames"):
        ts = [float(x) for x in MODE.split(":")[1].split(",")]
        outs = []
        for t in sorted(ts):
            _prev_m[0] = None; outs.append(finish(render_frame(t), t).resize((360, 640), Image.LANCZOS))
        sheet = Image.new("RGB", (360 * len(outs), 640)); [sheet.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]
        sheet.save(OUTFILE, quality=90); return
    if MODE == "info":
        print("TOTAL", TOTAL, "CL", CL_IN, IG_IN, CL_OUT, "STATS", STATS); return
    vout = f"{V}/video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
    n = int(round(TOTAL * FPS))
    for i in range(n):
        enc.stdin.write(finish(render_frame(i / FPS), i / FPS).tobytes())
        if i % 150 == 0: print(f"{i / FPS:.1f}s", flush=True)
    enc.stdin.close(); enc.wait()
    # áudio: só a voz dele; nas imagens do ato a música sobe (sem a trilha dos vídeos de terceiros)
    parts = []
    for j, s in enumerate(segs):
        pj = f"{V}/a{j}.wav"; d = s["b"] - s["a"]
        if s["src"] == "me":
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-t", f"{d:.3f}", "-i", f"{V}/me_vox.wav",
                            "-af", f"afade=t=in:d=0.02,afade=t=out:st={d - 0.04:.3f}:d=0.04", "-ar", "48000", "-ac", "2", pj], check=True)
        else:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-t", f"{d:.3f}", "-i", "anullsrc=r=48000:cl=stereo", pj], check=True)
        parts.append(pj)
    lst = f"{V}/alist.txt"; open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "pcm_s16le", f"{V}/voice_edit.wav"], check=True)
    ev = [(0.3, sfx.whoosh(0.6), 0.22), (CL_IN - 0.15, sfx.whoosh(0.5), 0.30), (CL_IN + 0.45, sfx.thud(), 0.24),
          (IG_IN - 0.1, sfx.whoosh(0.45), 0.28), (IG_IN + 0.5, sfx.thud(), 0.2), (CL_OUT - 0.5, sfx.whoosh(0.5, False), 0.24)]
    for a, b in STATS: ev += [(a - 0.08, sfx.whoosh(0.4), 0.22), (a + 0.45, sfx.thud(), 0.22)]
    ev += [(out_t("me", L_START) - 0.02, sfx.marker(0.7), 0.32), (out_t("me", L_START + L_V + L_H), sfx.thud(), 0.18)]
    ev += [(END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
    ev = [e for e in ev if 0 <= e[0] < TOTAL - 0.9]
    sfx.build(ev, TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice_edit.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/music.wav", "-filter_complex",
                    "[1:a]apad,asplit=2[vox1][key];[2:a]volume=0.8,apad[sf];[3:a]volume=0.30[mus];"
                    "[mus][key]sidechaincompress=threshold=0.02:ratio=7:attack=30:release=600[musd];"
                    f"[vox1][sf][musd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")

main()
