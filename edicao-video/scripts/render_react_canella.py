"""React viral: Eliezio x prisão de Márcio Canella (15/10/2026). Ele aponta para baixo → sobe para a janela no topo e o vídeo entra num cartão 3D embaixo."""
import sys, math, subprocess, json, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.path.insert(0, f"{S}/work")
import sfx
from minitop import make_minitop, make_minifooter, handles_row
V = f"{S}/v17"; FD = f"{S}/fontdl"
ME, CL = f"{V}/x34.mp4", f"{V}/x33.mp4"
W, H, FPS = 1080, 1920, 30
WHITE = (255, 255, 255); GOLD = (214, 182, 116); GOLD_L = (245, 226, 176); NAVY = (6, 34, 58); RED = (200, 38, 38)
WH = (255, 255, 255, 255); GD = GOLD + (255,)
HOT = set()

# fala de abertura (tela cheia) → clipe inteiro com ele na janela → fechamento em tela cheia
OPEN = (0.15, 10.95)                  # trecho dele na abertura
TR_IN = 9.40                          # quando ele aponta para baixo: começa a subir para a janela
REEL_IN = OPEN[1] - OPEN[0]           # o clipe começa logo depois da fala ("...nisso aqui")
CUT_A, CUT_B = 27.45, 36.00          # corte: elogios repetidos e evento (versão < 60 s para o YouTube)
REEL_LEN = 39.05 - (CUT_B - CUT_A)
def clip_src(rt): return rt if rt < CUT_A else rt + (CUT_B - CUT_A)
REEL_OUT = REEL_IN + REEL_LEN
CLOSE = (17.00, 24.95)                # "eu não sei aonde isso vai dar... dia 25 vai ser histórico" + L
CLOSE_IN = REEL_OUT
MUS_IN = CLOSE_IN + (19.50 - CLOSE[0])   # música entra baixinho no "dia 25"
FIN_IN = CLOSE_IN + (22.70 - CLOSE[0])   # fim da fala: música cheia + letra
FIN_LEN = 9.45 - (FIN_IN - MUS_IN)       # música original até o segundo "VAI DAR PT"
EDIT_END = FIN_IN + FIN_LEN; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
WATCH = (11.10, 16.90)                # ele em silêncio olhando: vai e volta na janela
segs = [dict(src="me", a=OPEN[0], b=OPEN[1], t0=0.0, t1=REEL_IN), dict(src="me", a=CLOSE[0], b=CLOSE[1], t0=CLOSE_IN, t1=EDIT_END)]

ME_CAPS = [("POSSO FALAR UMA COISA?", 0.22, 1.48), ("PARECE QUE TUDO NO ENTORNO DESSE CARA FEDE", 1.60, 3.30),
           ("É MILICIANO, É RACHADINHA,", 3.62, 5.85), ("É VORCARO", 5.90, 6.42),
           ("E AGORA ESSE CARA AÍ PRESO HOJE", 6.78, 8.30), ("EU NÃO SEI SE VOCÊ VIU", 8.30, 9.25),
           ("MAS DÁ UMA OLHADINHA NISSO AQUI", 9.25, 10.90),
           ("EU NÃO SEI AONDE ISSO VAI DAR", 17.05, 18.92), ("EU SÓ SEI QUE DIA 25", 19.52, 20.95), ("VAI SER HISTÓRICO", 21.58, 22.62)]
HOT = {"FEDE", "PRESO", "HOJE", "25", "HISTÓRICO"}
LYR = [(0.0, 1.43, "ESSE ANO"), (1.43, 2.87, "O LULA BOTA"), (2.87, 3.87, "O BOLSONARO"), (3.87, 4.87, "PRA MAMAR"),
       (4.87, 5.73, "VAI DAR PT"), (5.73, 6.73, "VAI DAR"), (6.73, 8.23, "VAI DAR PT"), (8.23, 9.43, "VAI DAR PT")]
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
for c in CAPS: c["src"] = "au" if any(w.strip(",.?!") in HOT for w in c["words"]) else "me"   # palavra-chave em vermelho
FACE = (245.0, 380.0)
WIN = (340, 172, 740, 708)                       # janela dele no topo (400 × 536), cabeça inteira com folga
CARD_Y, CARD_B = 742, 1758; CARD_H = CARD_B - CARD_Y; CARD_W = int(CARD_H * 576 / 1024); CARD_X = (W - CARD_W) // 2

def me_win_img(img, w, h):
    sc = max(w / 478, h / 850); small = cv2.resize(img, (int(478 * sc) + 1, int(850 * sc) + 1), interpolation=cv2.INTER_AREA)
    sy = int((small.shape[0] - h) * 0.2); sx = (small.shape[1] - w) // 2
    return small[sy:sy + h, sx:sx + w]

_me = {}
def me_src(a):
    """quadro dele no tempo a (fonte)"""
    key = int(a // 6)
    if key not in _me:
        if len(_me) > 3: _me.clear()
        _me[key] = decode(ME, key * 6, key * 6 + 6, 478, 850)
    fr = _me[key]; return fr[min(len(fr) - 1, int((a - key * 6) * FPS))]

def watch_t(t):
    """tempo da fonte dele durante o clipe: termina a fala, depois vai e volta no trecho em silêncio"""
    a = OPEN[0] + t
    if a < OPEN[1]: return a
    u = (t - REEL_IN) * 0.85; L = WATCH[1] - WATCH[0]; p = u % (2 * L)
    return WATCH[0] + (p if p < L else 2 * L - p)

CLIP = None
def clip_frame(rt):
    global CLIP
    if CLIP is None: CLIP = decode(CL, 0, 39.05, 576, 1024)
    return CLIP[int(clamp(clip_src(rt) * FPS, 0, len(CLIP) - 1))]

def card_3d(img, tilt):
    """cartão com a base recuando, virado para cima (para ele, que está no topo)"""
    c = cv2.resize(img, (CARD_W, CARD_H), interpolation=cv2.INTER_AREA)
    m = Image.new("L", (CARD_W, CARD_H), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, CARD_W - 1, CARD_H - 1), 26, fill=255)
    im = Image.fromarray(c).convert("RGBA"); im.putalpha(m)
    ImageDraw.Draw(im).rounded_rectangle((1, 1, CARD_W - 2, CARD_H - 2), 26, outline=GOLD + (235,), width=3)
    a = 0.035 + 0.25 * tilt; w, h = CARD_W, CARD_H
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    dst = np.float32([[0, 0], [w, 0], [w * (1 - a), h * (1 - a * 0.30)], [w * a, h * (1 - a * 0.30)]])
    return Image.fromarray(cv2.warpPerspective(np.asarray(im), cv2.getPerspectiveTransform(src, dst), (w, h), flags=cv2.INTER_LINEAR), "RGBA")

def win_k(t):
    """0 = ele em tela cheia, 1 = ele na janela do topo"""
    return ease_io((t - TR_IN) / 0.6) * (1 - ease_io((t - (REEL_OUT - 0.25)) / 0.6))

def card_pos(t):
    """deslocamento do cartão: sobe de baixo na entrada, desce na saída"""
    kin = ease_out((t - (TR_IN + 0.15)) / 0.6); kout = ease_in((t - (REEL_OUT - 0.35)) / 0.5)
    return 1100 * (1 - kin) + 1100 * kout, clamp((1 - kin) + kout)

def badge(frame, t, t0, t1, big, small, y, xr):
    if not (t0 <= t < t1): return
    q = t - t0; kk = back_out(q / 0.45, 2.2); al = clamp(q / 0.12) * (1 - smooth((t - (t1 - 0.3)) / 0.3))
    f = MF("ExtraBold", 74); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); tw = d0.textlength(big, font=f)
    bw = int(max(430, tw + 70, d0.textlength(small, font=MF("SemiBold", 25)) + 50))
    lay = Image.new("RGBA", (bw + 20, 196), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((10, 10, bw + 10, 186), 26, fill=(5, 16, 30, 236), outline=GD, width=3)
    d.text((bw / 2 + 10, 78), big, font=f, fill=GOLD_L + (255,), anchor="mm")
    d.text((bw / 2 + 10, 148), small, font=MF("SemiBold", 25), fill=(230, 234, 240, 255), anchor="mm")
    lay = lay.rotate(-4 + 4 * (1 - kk), Image.BICUBIC, expand=True)
    sc = 0.6 + 0.4 * kk; lay = lay.resize((max(1, int(lay.width * sc)), max(1, int(lay.height * sc))), Image.BICUBIC)
    paste(frame, fade(lay, al), xr - lay.width, y - lay.height, 0.5, 16, (6, 16))

def news_chip(frame, t, t0, t1):
    """selo de notícia na abertura (fato conferido)"""
    if not (t0 <= t < t1): return
    q = t - t0; k = ease_out(q / 0.45); ko = ease_in((t - (t1 - 0.35)) / 0.35)
    lay = Image.new("RGBA", (760, 118), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, 759, 117), 22, fill=(5, 16, 30, 236), outline=GD, width=2)
    d.rounded_rectangle((18, 18, 150, 62), 12, fill=RED + (255,)); d.text((84, 40), "PRESO", font=MF("ExtraBold", 26), fill=WH, anchor="mm")
    d.text((168, 40), "MÁRCIO CANELLA", font=MF("ExtraBold", 34), fill=WH, anchor="lm")
    d.text((24, 88), "Polícia Federal · 15/10/2026", font=MF("SemiBold", 25), fill=GOLD_L + (255,), anchor="lm")
    paste(frame, fade(lay, k * (1 - ko)), W / 2 - 380 - 500 * (1 - k), 1560, 0.5, 14, (5, 12))

def lyrics(frame, t):
    """letra da música no lugar da legenda (abaixo do rosto), 'PT' em pílula vermelha"""
    mt = t - MUS_IN; k_all = clamp((t - FIN_IN) / 0.4)
    g = Image.new("RGBA", (W, 760), (0, 0, 0, 0)); ImageDraw.Draw(g).rectangle((0, 0, W, 760), fill=(4, 10, 20, 255))
    g.putalpha(Image.linear_gradient("L").resize((W, 760)).point(lambda v: int(v * 0.72 * k_all)))
    frame.alpha_composite(g, (0, H - 760))
    for a, b, txt in LYR:
        if not (a <= mt < b): continue
        u = mt - a; k = back_out(u / 0.18, 2.0); pt = txt.endswith("PT")
        f = MF("ExtraBold", 108 if len(txt) <= 10 else 88)
        lay = Image.new("RGBA", (W, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        if pt:
            pre = txt[:-2]; wp = d.textlength(pre, font=f); wt = d.textlength("PT", font=f); x0 = W / 2 - (wp + wt + 30) / 2
            d.text((x0, 100), pre, font=f, fill=WH, anchor="lm")
            d.rounded_rectangle((x0 + wp + 2, 30, x0 + wp + wt + 34, 172), 18, fill=RED + (255,)); d.text((x0 + wp + 18, 100), "PT", font=f, fill=WH, anchor="lm")
        else:
            d.text((W / 2, 100), txt, font=f, fill=WH, anchor="mm")
        sc = 0.7 + 0.3 * k; lay = fade(lay.resize((int(W * sc), int(200 * sc)), Image.BICUBIC), k_all)
        blk = Image.new("RGBA", lay.size, (0, 0, 0, 255)); blk.putalpha(lay.getchannel("A").point(lambda v: int(v * 0.6)))
        frame.alpha_composite(blk.filter(ImageFilter.GaussianBlur(10)), (int(W / 2 - lay.width / 2) + 4, 1630 - lay.height // 2 + 8))
        frame.alpha_composite(lay, (int(W / 2 - lay.width / 2), 1630 - lay.height // 2))

def render_frame(t):
    if t >= END_IN + 0.35: return end_card(t)
    tt = min(t, EDIT_END - 1e-3)
    if tt >= CLOSE_IN:                                   # fechamento: ele em tela cheia
        a = CLOSE[0] + (tt - CLOSE_IN)
        if a > 24.85:
            L0, L1 = 23.30, 24.85; u = (a - 24.85) * 0.8; Lq = L1 - L0; pq = u % (2 * Lq); a = L1 - pq if pq < Lq else L0 + (pq - Lq)
        me = me_src(a)
        full = me_full(me, t); k = win_k(tt)
    else:
        me = me_src(watch_t(tt)); full = me_full(me, t); k = win_k(tt)
    if k <= 0.001 and (tt < TR_IN or tt >= CLOSE_IN + 0.4):
        frame = Image.fromarray(full).convert("RGBA")
    else:
        rt = clamp(tt - REEL_IN, 0, REEL_LEN - 0.01); cimg = clip_frame(rt)
        sm = cv2.GaussianBlur(cv2.resize(cimg, (96, 170)), (0, 0), 3); bg = cv2.resize(sm, (W, H)).astype(np.float32) * 0.26 + np.array([2, 6, 12], np.float32)
        out = full.astype(np.float32) * (1 - k) + bg * k
        x0, y0, x1, y1 = [lerp(p, q, k) for p, q in zip((0, 0, W, H), WIN)]
        ww, wh = int(x1 - x0), int(y1 - y0)
        if k > 0.002 and ww > 8 and wh > 8:
            win = me_win_img(me, ww, wh).astype(np.float32); wx, wy = int(x0), int(y0)
            m = Image.new("L", (ww, wh), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, ww - 1, wh - 1), int(28 * k), fill=255)
            m = np.asarray(m, np.float32)[..., None] / 255
            sh = np.zeros((H, W), np.float32); cv2.rectangle(sh, (wx + 8, wy + 20), (wx + ww + 8, wy + wh + 20), 1.0, -1)
            out = out * (1 - cv2.GaussianBlur(sh, (0, 0), 18)[..., None] * 0.55 * k)
            out[wy:wy + wh, wx:wx + ww] = out[wy:wy + wh, wx:wx + ww] * (1 - m) + win * m
        frame = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")
        if k > 0.002: ImageDraw.Draw(frame).rounded_rectangle((int(x0), int(y0), int(x0) + ww, int(y0) + wh), int(28 * k), outline=GOLD + (int(220 * k),), width=2)
        dy, tilt = card_pos(tt)
        if dy < 1100:
            c = card_3d(cimg, tilt); vy = card_pos(tt)[0] - card_pos(tt - 1 / FPS)[0]
            paste(frame, c, CARD_X, CARD_Y + dy, 0.6, 22, (10, 26), (0, vy))
            al = clamp((tt - REEL_IN) / 0.4) * clamp((REEL_OUT - 0.4 - tt) / 0.3)
            credit(frame, "Reprodução: UOL · O Globo · CNN Brasil", W - 30, CARD_Y - 46 + dy, al)
            badge(frame, t, REEL_IN + 18.2, REEL_IN + 23.4, "R$ 7,6 BI", "movimentados em 6 anos, segundo a PF", CARD_Y + 520 + dy, W - 20)
    if tt < TR_IN or tt >= CLOSE_IN: draw_caption(frame, t, 1450, 56, ("me", "au"))
    elif tt < REEL_IN + 0.2 and tt >= TR_IN: draw_caption(frame, t, int(lerp(1450, WIN[3] - 70, win_k(tt))), int(lerp(56, 40, win_k(tt))), ("me", "au"))
    news_chip(frame, t, 6.9, 9.5)
    if tt >= FIN_IN - 0.05: lyrics(frame, t)
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
    if MODE == "info": print("TOTAL", TOTAL, REEL_IN, REEL_OUT, EDIT_END); return
    vout = f"{V}/video.mp4"
    if MODE != "audio":
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
        for i in range(int(round(TOTAL * FPS))):
            enc.stdin.write(finish(render_frame(i / FPS), i / FPS).tobytes())
            if i % 300 == 0: print(f"{i / FPS:.0f}s", flush=True)
        enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    for f, o in (("x34.mp4", "me.wav"), ("x33.mp4", "cl.wav")):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{V}/{f}", "-ar", "48000", "-ac", "2", f"{V}/{o}"], check=True)
    voice = readw(f"{V}/me.wav"); vt = np.zeros((n, 2), np.float32)
    for s in segs:
        p = voice[int(s["a"] * SR):int(s["b"] * SR)].copy(); f = int(0.04 * SR)
        env = np.ones(len(p)); env[:f] = np.linspace(0, 1, f); env[-f:] = np.linspace(1, 0, f)
        t0 = int(s["t0"] * SR); vt[t0:t0 + len(p)] += p * env[:, None]
    writew(f"{V}/voice.wav", vt)
    cl0 = readw(f"{V}/cl.wav"); xf = int(0.08 * SR); A_, B_ = int(CUT_A * SR), int(CUT_B * SR)
    p1, p2 = cl0[:A_].copy(), cl0[B_:int(39.05 * SR)].copy()
    p1[-xf:] *= np.linspace(1, 0, xf)[:, None]; p2[:xf] *= np.linspace(0, 1, xf)[:, None]
    cl = np.concatenate([p1[:-xf], p1[-xf:] + p2[:xf], p2[xf:]])[:int(REEL_LEN * SR)]; ct = np.zeros((n, 2), np.float32)
    f = int(0.4 * SR); env = np.ones(len(cl)); env[-f:] = np.linspace(1, 0, f); env[:int(0.05 * SR)] = np.linspace(0, 1, int(0.05 * SR))
    t0 = int(REEL_IN * SR); ct[t0:t0 + len(cl)] = cl * env[:, None]; writew(f"{V}/clip.wav", ct)
    song = readw(f"{S}/v15/song_vox.wav"); mt0 = int(MUS_IN * SR); L = min(len(song), n - mt0)
    st = np.zeros((n, 2), np.float32); tl = np.arange(L) / SR; lead = FIN_IN - MUS_IN
    gain = np.where(tl < lead, 10 ** ((-22 + 22 * tl / lead) / 20), 1.0)
    fo_t = (TOTAL - MUS_IN) - 1.6; gain = gain * np.clip(1 - (tl - fo_t) / 1.5, 0, 1)   # some no fim do cartão final
    st[mt0:mt0 + L] = song[:L] * gain[:, None]; writew(f"{V}/song.wav", st)
    ev = [(0.3, sfx.whoosh(0.6), 0.2), (6.9, sfx.whoosh(0.4), 0.2), (TR_IN - 0.1, sfx.whoosh(0.6), 0.28),
          (REEL_IN + 18.2, sfx.thud(), 0.26), (REEL_IN + 18.25, sfx.paper(), 0.18), (REEL_OUT - 0.4, sfx.whoosh(0.6, False), 0.24), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/clip.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]volume=1.0,asplit=2[vox][key];[2:a]volume=0.8[sf];[3:a]volume=1.0[cl];[4:a]volume=0.9[sg];"
                    "[sg][key]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][cl][sgd]amix=inputs=4:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
