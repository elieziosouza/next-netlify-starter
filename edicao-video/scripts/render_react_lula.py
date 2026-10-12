"""React: Eliezio x reels do Lula na Paulista (11/10). Janelinha com a reação real dele, sincronizada com as cenas; punho erguido com efeito de luz."""
import sys, math, subprocess, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.path.insert(0, f"{S}/work")
import sfx, grading
from minitop import make_minitop, make_minifooter, handles_row
GRADE = grading.Fast(grading.cinema, f"{S}/grade/lut_cinema.npy", 0.08, 6)     # só nas imagens de terceiros

V = f"{S}/v11"; FD = f"{S}/fontdl"
ME, CL = f"{V}/me.mp4", f"{V}/lula.mp4"
W, H, FPS = 1080, 1920, 30
WHITE = (255, 255, 255); GOLD = (214, 182, 116); GOLD_L = (245, 226, 176); NAVY = (6, 34, 58); RED = (200, 38, 38)
WH = (255, 255, 255, 255); GD = GOLD + (255,)
HOT = set()

# (tipo, ...): ("me", a, b) tela cheia | ("cl", clip_a, clip_b, me_a) reels no cartão + janelinha com a reação real dele
EDL = [("me", 0.45, 3.25),
       ("cl", 0.0, 4.2, 4.80),
       ("me", 18.10, 21.45),
       ("cl", 4.5, 6.5, 21.45), ("cl", 12.0, 15.9, 23.45), ("cl", 32.4, 34.9, 27.35, "crop=720:640:0:0"),
       ("me", 29.85, 36.70)]
segs = []; acc = 0.0
for e in EDL:
    if e[0] == "me": a, b = e[1], e[2]; d = dict(src="me", a=a, b=b)
    else: d = dict(src="cl", ca=e[1], cb=e[2], a=e[3], b=e[3] + e[2] - e[1], crop=e[4] if len(e) > 4 else "crop=720:1000:0:200")
    d["t0"] = acc; d["t1"] = acc + (d["b"] - d["a"]); acc = d["t1"]; segs.append(d)
for i, s in enumerate(segs):          # blocos de reels contíguos
    s["blk_start"] = s["t0"] if (i == 0 or segs[i - 1]["src"] != s["src"]) else segs[i - 1]["blk_start"]
for i in range(len(segs) - 1, -1, -1):
    s = segs[i]; s["blk_end"] = s["t1"] if (i == len(segs) - 1 or segs[i + 1]["src"] != s["src"]) else segs[i + 1]["blk_end"]
EDIT_END = acc; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
def seg_at(t):
    for s in segs:
        if s["t0"] <= t < s["t1"]: return s
    return segs[-1]
def out_t(x):
    """tempo da fala dele (fonte) → tempo de saída"""
    for s in segs:
        if s["a"] <= x <= s["b"]: return s["t0"] + x - s["a"]
    raise ValueError(x)

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
            pass                                           # a voz dele corre em todos os trechos
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

# ---------------------------------------------------------------- reels no cartão
CLCROP = "crop=720:1000:0:200"; CW_, CH_ = 720, 1000
CA_W = 590; CA_H = int(CH_ * CA_W / CW_)                 # 819
CARD_Y0 = 168
WINC = (320, 1168, 760, 1746)                             # janelinha maior (pedido de 12/10)

def clip_frame(clip, me_img, t, s, u_seg):
    bs, be = s["blk_start"], s["blk_end"]; u = t - bs; dur = be - bs
    bg = blur_bg(clip, 0.26)
    k = ease_io(u / 0.6)                                  # ele encolhe para a janelinha na entrada do bloco
    frame = compose_me_layer(bg, me_img, t, WINC, k)
    ex = ease_in((t - (be - 0.5)) / 0.5)
    def ya(q): return -860 * (1 - ease_out(q / 0.6)) - 1050 * ease_in((q - (dur - 0.5)) / 0.5)
    tilt = clamp(1 - ease_out(u / 0.75) + ex)
    img = clip
    # troca de cena dentro do cartão: mergulho rápido de luz e desfoque
    cut = min([abs(t - x["t0"]) for x in segs if x["src"] == "cl" and x["t0"] > bs + 0.01] + [9])
    if cut < 0.12:
        q = 1 - cut / 0.12; img = cv2.GaussianBlur(img, (0, 0), 1 + 10 * q); img = np.clip(img.astype(np.float32) * (1 + 0.5 * q), 0, 255).astype(np.uint8)
    caw = CA_W if img.shape[0] > img.shape[1] * 1.2 else 880          # cena larga ganha cartão maior
    cah = int(img.shape[0] * caw / img.shape[1])
    rgba = rounded(cv2.resize(img, (caw, cah), interpolation=cv2.INTER_AREA), 26, 3)
    im = Image.fromarray(persp(rgba, "top", 0.06 + 0.24 * tilt) if tilt > 0.003 else rgba, "RGBA")
    dy = ya(u); vy = dy - ya(u - 1 / FPS)
    x = W / 2 - im.width / 2; y = CARD_Y0 + dy
    paste(frame, im, x, y, 0.6, 22, (10, 26), (0, vy))
    al = clamp((u - 0.7) / 0.4) * (1 - ex)
    if al > 0: credit(frame, "Vídeo: PT", W / 2 + caw / 2 - 16, CARD_Y0 + cah - 50 + dy, al)
    if al > 0 and s is segs[1]: credit(frame, "Av. Paulista · 11/10", W / 2 - caw / 2 + 16, CARD_Y0 + 18 + dy, al, "lm")
    # selo "80 ANOS" no "pique do véio"
    ts = out_t(6.35)
    if s is segs[1] and t >= ts:
        q = t - ts; kk = back_out(q / 0.45, 2.2); al2 = clamp(q / 0.12) * (1 - ex)
        lay = Image.new("RGBA", (440, 210), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.rounded_rectangle((10, 10, 430, 200), 26, fill=(5, 16, 30, 230), outline=GD, width=3)
        d.text((220, 82), "80 ANOS", font=MF("ExtraBold", 84), fill=GOLD_L + (255,), anchor="mm")
        d.text((220, 160), "faz 81 no dia 27/10", font=MF("SemiBold", 28), fill=(230, 234, 240, 255), anchor="mm")
        lay = lay.rotate(-4 + 4 * (1 - kk), Image.BICUBIC, expand=True)
        sc = 0.6 + 0.4 * kk; lay = lay.resize((max(1, int(lay.width * sc)), max(1, int(lay.height * sc))), Image.BICUBIC)
        paste(frame, fade(lay, al2), W / 2 + CA_W / 2 - lay.width + 30, CARD_Y0 + CA_H - lay.height - 70 + dy, 0.5, 16, (6, 16))
    draw_caption(frame, t, 1080, 46, ("me",))
    return frame

# ---------------------------------------------------------------- cartões de vidro acima da cabeça
CARD_X, CARD_Y, CARD_W, CARD_H = 90, 168, 900, 262
GLASS = [(out_t(18.30), out_t(21.45), "parada"), (out_t(31.83), EDIT_END, "dia25")]
def glass_content(kind, u):
    im = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if kind == "parada":
        d.text((CARD_W / 2, 50), "LULA, 80 ANOS", font=MF("Bold", 26), fill=GD, anchor="mm")
        k = back_out((u - 0.1) / 0.5, 1.4); f = MF("ExtraBold", int(104 * (0.75 + 0.25 * k)))
        d.text((CARD_W / 2, 142), "PARADA DURA", font=f, fill=WH, anchor="mm")
        lw = int(170 * ease_out((u - 0.5) / 0.6)); d.rectangle((CARD_W / 2 - lw, 212, CARD_W / 2 + lw, 214), fill=GD)
    else:
        d.text((CARD_W / 2, 50), "SEGUNDO TURNO", font=MF("Bold", 26), fill=GD, anchor="mm")
        k = back_out((u - 0.15) / 0.5, 1.4); f = MF("ExtraBold", int(118 * (0.7 + 0.3 * k)))
        d.text((CARD_W / 2, 142), "DIA 25", font=f, fill=GOLD_L + (255,), anchor="mm")
        lw = int(150 * ease_out((u - 0.5) / 0.6)); d.rectangle((CARD_W / 2 - lw, 212, CARD_W / 2 + lw, 214), fill=GD)
    return im

def draw_glass(frame, t):
    for a, b, kind in GLASS:
        if not (a <= t < b): continue
        u = t - a; dur = b - a
        kin = ease_out(u / 0.6); kout = ease_in((u - (dur - 0.4)) / 0.4)
        base = np.asarray(frame.convert("RGB"))[CARD_Y:CARD_Y + CARD_H, CARD_X:CARD_X + CARD_W].astype(np.float32)
        glass = cv2.GaussianBlur(base, (0, 0), 16) * 0.42 + np.array([4, 14, 28], np.float32) * 0.58
        gl = Image.fromarray(np.clip(glass, 0, 255).astype(np.uint8)).convert("RGBA")
        m = Image.new("L", (CARD_W, CARD_H), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, CARD_W - 1, CARD_H - 1), 26, fill=255); gl.putalpha(m)
        ImageDraw.Draw(gl).rounded_rectangle((1, 1, CARD_W - 2, CARD_H - 2), 26, outline=GOLD + (210,), width=2)
        gl.alpha_composite(glass_content(kind, u))
        tilt = clamp((1 - kin) + kout)
        arr = persp(np.asarray(gl), "top", 0.05 + 0.4 * tilt) if tilt > 0.003 else np.asarray(gl)
        im = fade(Image.fromarray(arr, "RGBA"), clamp(kin * 1.6) * (1 - kout))
        def yy_(q): return 60 * (1 - ease_out(q / 0.6)) - 90 * ease_in((q - (dur - 0.4)) / 0.4)
        dy = yy_(u); vy = dy - yy_(u - 1 / FPS)
        paste(frame, im, CARD_X, CARD_Y + dy, 0.55, 20, (8, 20), (0, vy))

# ---------------------------------------------------------------- punho erguido: rastro de luz + onda de choque
_FJ = json.load(open(f"{V}/fist.json"))
F_T = np.array([o["t"] for o in _FJ if o]); F_P = np.array([o["c"] for o in _FJ if o], np.float32)
F_P = np.array([np.median(F_P[max(0, i - 2):i + 3], 0) for i in range(len(F_P))])
F_P = np.array([F_P[max(0, i - 1):i + 2].mean(0) for i in range(len(F_P))])
F_PEAK = 34.05                                           # "vai ser histórico"
def fist_at(srct):
    return np.array([np.interp(srct, F_T, F_P[:, 0]), np.interp(srct, F_T, F_P[:, 1])])
def to_out(p, t, z):
    sc = W / 478 * (1.03 + 0.01 * math.sin(t * 0.3) + z)
    return (sc * p[0] + W / 2 - FACE[0] * sc, sc * p[1] + FACE[1] * W / 478 - FACE[1] * sc)
_rngF = np.random.default_rng(4)
# partículas de luz subindo devagar (esperança), mais do lado do punho e nas bordas, longe do rosto
MOTES = []
for _ in range(70):
    x = float(np.clip(_rngF.beta(1.3, 3.2) * W, 10, W - 10)) if _rngF.random() < 0.75 else float(_rngF.uniform(W * 0.78, W - 10))
    MOTES.append((33.25 + _rngF.uniform(0, 1.8), x, _rngF.uniform(1150, 1750), _rngF.uniform(55, 130), _rngF.uniform(2.5, 9), _rngF.uniform(2.2, 3.4), _rngF.uniform(0, 6.28)))
def add_light(frame, layer, gain=1.0):
    """luz somada (tela), cor quente sem escurecer as bordas"""
    f = np.asarray(frame, np.float32); l = np.asarray(layer, np.float32)
    a = l[..., 3:4] / 255 * gain
    rgb = f[..., :3] + (255 - f[..., :3]) * a * (l[..., :3] / 255)
    out = np.concatenate([np.clip(rgb, 0, 255), f[..., 3:4]], 2).astype(np.uint8)
    frame.paste(Image.fromarray(out, "RGBA"))

WARM = (255, 222, 165)
def draw_fist(frame, t, z, srct):
    """efeito de esperança: luz quente nascendo atrás do punho, raios suaves para cima e partículas de luz subindo"""
    if srct < 33.2: return
    k = smooth((srct - 33.2) / 0.9) * (1 - smooth((t - (EDIT_END - 0.5)) / 0.5))
    if k <= 0: return
    c = to_out(fist_at(min(srct, 36.3)), t, z)
    breath = 1 + 0.06 * math.sin(t * 2.2)
    lay = Image.new("RGBA", (W, H), WARM + (0,)); d = ImageDraw.Draw(lay)
    for r, al in ((560, 60), (380, 90), (230, 120), (120, 150)):         # amanhecer atrás do punho
        rr = r * breath * (0.6 + 0.4 * k); d.ellipse((c[0] - rr, c[1] - rr, c[0] + rr, c[1] + rr), fill=WARM + (int(al * k),))
    sun = lay.filter(ImageFilter.GaussianBlur(70))
    rays = Image.new("RGBA", (W, H), WARM + (0,)); d = ImageDraw.Draw(rays)
    rot = (srct - 33.2) * 4
    for i in range(7):                                                      # raios para cima e para fora, longe do rosto
        ang = math.radians(196 + i * 12 + 4 * math.sin(rot * 0.3 + i)); L = 1150; wd = math.radians(2.4 + (i % 3) * 0.8)
        p1 = (c[0] + L * math.cos(ang - wd), c[1] + L * math.sin(ang - wd)); p2 = (c[0] + L * math.cos(ang + wd), c[1] + L * math.sin(ang + wd))
        d.polygon([c, p1, p2], fill=WARM + (int((95 + 40 * math.sin(rot + i * 1.7)) * k),))
    rays = rays.filter(ImageFilter.GaussianBlur(16))
    add_light(frame, sun, 0.9); add_light(frame, rays, 0.7)
    pl = Image.new("RGBA", (W, H), (255, 220, 150, 0)); d = ImageDraw.Draw(pl)
    for st, x0, y0, spd, r, life, ph in MOTES:
        age = srct - st
        if age < 0 or age > life: continue
        x = x0 + 18 * math.sin(age * 1.6 + ph); y = y0 - spd * age
        if ((x - 540) / 300) ** 2 + ((y - 760) / 420) ** 2 < 1: continue       # nada sobre o rosto
        a = math.sin(math.pi * age / life) * k; rr = r * 1.3
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(255, 220, 150, int(240 * a)))
    add_light(frame, pl.filter(ImageFilter.GaussianBlur(10)), 1.0); add_light(frame, pl.filter(ImageFilter.GaussianBlur(2)), 0.9)

# ---------------------------------------------------------------- render
_cache = {}
def seg_frames(s):
    key = (s["src"], s["a"])
    if key not in _cache:
        _cache.clear()
        me = decode(ME, s["a"], s["b"], 478, 850)
        cl = None
        if s["src"] == "cl":
            cw, ch = [int(v) for v in s["crop"].split("=")[1].split(":")[:2]]
            cl = np.stack([GRADE(f) for f in decode(CL, s["ca"], s["cb"], cw, ch, s["crop"])])
        _cache[key] = (me, cl)
    return _cache[key]

_last_clip = [None]
def render_frame(t):
    if t >= END_IN + 0.35: return end_card(t)
    tt = min(t, EDIT_END - 1e-3); s = seg_at(tt); u = tt - s["t0"]; me, cl = seg_frames(s)
    img = me[min(len(me) - 1, int(u * FPS))]
    srct = s["a"] + u
    if s["src"] == "cl":
        c = cl[min(len(cl) - 1, int(u * FPS))]; _last_clip[0] = c
        frame = clip_frame(c, img, t, s, u)
    else:
        z = 0.0
        pass
        frame = Image.fromarray(me_full(img, t, z)).convert("RGBA")
        kin = ease_io(u / 0.6) if (segs.index(s) > 0 and segs[segs.index(s) - 1]["src"] == "cl") else 1.0
        if kin < 1:                                            # a janelinha cresce uma vez até a tela cheia
            bg = blur_bg(_last_clip[0], 0.26) if _last_clip[0] is not None else NAVYBG.copy()
            out = np.asarray(frame.convert("RGB"), np.float32)
            x0, y0, x1, y1 = [lerp(a, b, kin) for a, b in zip(WINC, (0, 0, W, H))]
            w, h = int(x1 - x0), int(y1 - y0)
            ch = min(H, int(W * h / w)); cy0 = int(clamp((800 - ch * 0.42) / (H - ch + 1e-6)) * (H - ch)) if ch < H else 0
            cw = int(ch * w / h); cx0 = (W - cw) // 2
            win = cv2.resize(out[cy0:cy0 + ch, cx0:cx0 + cw], (w, h), interpolation=cv2.INTER_AREA)
            m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), int(28 * (1 - kin)), fill=255)
            m = np.asarray(m, np.float32)[..., None] / 255
            o2 = bg.copy(); o2[int(y0):int(y0) + h, int(x0):int(x0) + w] = o2[int(y0):int(y0) + h, int(x0):int(x0) + w] * (1 - m) + win * m
            frame = Image.fromarray(np.clip(o2, 0, 255).astype(np.uint8)).convert("RGBA")
        draw_glass(frame, t)
        # punho sem efeito (pedido de 12/10)
        draw_caption(frame, t, 1450, 56, ("me",))
        if s is segs[0]: react_tag(frame, t, "REACT  ·  LULA NA PAULISTA", 0.9, 2.7)
    draw_banners(frame, t)
    if t >= END_IN: frame.alpha_composite(fade(end_card(t), clamp((t - END_IN) / 0.35)))
    return frame

def main():
    if MODE.startswith("frames"):
        ts = [float(x) for x in MODE.split(":")[1].split(",")]
        outs = [finish(render_frame(t), t).resize((360, 640), Image.LANCZOS) for t in sorted(ts)]
        sheet = Image.new("RGB", (360 * len(outs), 640)); [sheet.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]
        sheet.save(OUTFILE, quality=90); return
    if MODE == "info":
        print("TOTAL", TOTAL, [(s["src"], round(s["t0"], 2), round(s["t1"], 2)) for s in segs], "GLASS", GLASS, "PEAK", out_t(F_PEAK)); return
    vout = f"{V}/video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
    n = int(round(TOTAL * FPS))
    for i in range(n):
        enc.stdin.write(finish(render_frame(i / FPS), i / FPS).tobytes())
        if i % 150 == 0: print(f"{i / FPS:.1f}s", flush=True)
    enc.stdin.close(); enc.wait()
    # áudio: só a voz dele (inclusive as reações na janelinha); o som do reels sai (música com direitos)
    parts = []
    for j, s in enumerate(segs):
        pj = f"{V}/a{j}.wav"; d = s["b"] - s["a"]
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-t", f"{d:.3f}", "-i", f"{V}/me_vox.wav",
                        "-af", f"afade=t=in:d=0.02,afade=t=out:st={d - 0.04:.3f}:d=0.04", "-ar", "48000", "-ac", "2", pj], check=True)
        parts.append(pj)
    lst = f"{V}/alist.txt"; open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "pcm_s16le", f"{V}/voice_edit.wav"], check=True)
    ev = [(0.3, sfx.whoosh(0.6), 0.22)]
    for i, s in enumerate(segs):
        if s["src"] == "cl" and s["t0"] == s["blk_start"]: ev += [(s["t0"] - 0.15, sfx.whoosh(0.5), 0.30), (s["t0"] + 0.45, sfx.thud(), 0.22)]
        elif s["src"] == "cl": ev += [(s["t0"] - 0.05, sfx.whoosh(0.35), 0.2)]
        if s["src"] == "me" and i > 0 and segs[i - 1]["src"] == "cl": ev += [(s["t0"] - 0.1, sfx.whoosh(0.5, False), 0.24)]
    ev += [(out_t(6.35), sfx.thud(), 0.3), (out_t(6.35) + 0.05, sfx.paper(), 0.2)]
    for a, b, k in GLASS: ev += [(a - 0.08, sfx.whoosh(0.4), 0.22), (a + 0.45, sfx.thud(), 0.22)]
    pass
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
