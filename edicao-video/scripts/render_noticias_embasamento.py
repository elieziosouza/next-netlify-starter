import sys, math, json, subprocess
from pathlib import Path
KIT = Path(__file__).resolve().parent.parent   # pasta edicao-video
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = sys.argv[1]; OUTFILE = sys.argv[2]
MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.path.insert(0, str(KIT / "scripts"))
import sfx
from clean import Cleaner

SRC = "/root/.claude/uploads/698dd744-d40f-5d96-b9e9-72023ae79dbf/a45bb844-VID-20261010-WA0024.mp4"
UP = "/root/.claude/uploads/698dd744-d40f-5d96-b9e9-72023ae79dbf"
V3 = f"{S}/v6"; FD = str(KIT / "assets" / "fonts")
W, H, FPS = 1080, 1920, 30
SW, SH = 478, 850
NSRC = 1392
SRC_DUR = 46.4
END_IN = 45.95
TOTAL = 49.20

WHITE = (255, 255, 255); GOLD = (214, 182, 116); GOLD_L = (245, 226, 176); NAVY = (6, 34, 58)
PANEL_BG = (5, 28, 50); CYAN = (90, 190, 235); GREEN = (96, 186, 92)
def MF(w, s): return ImageFont.truetype(f"{FD}/Montserrat-{w}.ttf", s)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_in(x): x = clamp(x); return x ** 3
def back_out(x, s=1.7):
    x = clamp(x) - 1; return 1 + (s + 1) * x ** 3 + s * x ** 2
def lerp(a, b, k): return a + (b - a) * k
def fade(img, a):
    if a >= 1: return img
    img = img.copy(); img.putalpha(img.getchannel("A").point(lambda v: int(v * max(0, a)))); return img

yy, xx = np.mgrid[0:H, 0:W]

# ---------------------------------------------------------------- captions (from CapCut captions)
CAPS6 = [("AGORA VAMOS ENTRAR NO ASSUNTO AQUI SÓ POR CURIOSIDADE MESMO É AQUELE CASO LÁ DO FLÁVIO BOLSONARO LÁ DA RACHADINHA LÁ NO RIO DE JANEIRO", 0.57, 6.60),
         ("AQUELES MAIS DE R$ 2 MILHÕES QUE FORAM DEPOSITADOS NA CONTA DO QUEIROZ QUE ERA ASSIM AMIGUINHO DELE AMIGAÇO DELE", 7.16, 13.22),
         ("POR QUE ELE NÃO FOI CONDENADO NESSE CASO?", 14.04, 16.23), ("POR QUÊ?", 16.57, 17.06),
         ("PORQUE NÃO TINHA A PROVA? TINHA A PROVA!", 17.72, 19.43), ("O PROBLEMA FOI UM DETALHE TÉCNICO", 20.02, 21.99),
         ("AS PROVAS FORAM ANULADAS PORQUE FOI DECIDIDO QUE UM JUIZ DE PRIMEIRA INSTÂNCIA NÃO TINHA COMPETÊNCIA PARA PEDIR A QUEBRA DE SIGILO BANCÁRIO DELE E AÍ ELE ESCAPOU", 22.30, 31.42),
         ("MAS NÃO QUER DIZER QUE ELE NÃO FEZ", 31.70, 34.12),
         ("ENTÃO SE ELE FAZIA ISSO NO RIO DE JANEIRO IMAGINA O QUE ELE VAI FAZER NA PRESIDÊNCIA DA REPÚBLICA", 34.55, 39.30),
         ("É SÓ RACIOCINAR", 39.83, 40.87), ("SÓ RACIOCINAR DIA 25 NÃO TEM ERRO", 41.85, 44.01), ("É 13", 44.89, 45.54)]
caps = []
for txt, st, en in CAPS6:
    words = txt.split(); n = max(1, math.ceil(len(words) / 5)); per = math.ceil(len(words) / n)
    chunks = [words[k:k + per] for k in range(0, len(words), per)]
    tot = sum(len(w) + 2 for w in words); acc = 0
    for ch in chunks:
        cs = st + (en - st) * acc / tot; ts = []
        for w in ch: ts.append(st + (en - st - 0.1) * acc / tot); acc += len(w) + 2
        caps.append(dict(words=ch, ts=ts, start=cs, end=st + (en - st) * acc / tot + 0.12))
for a_, b_ in zip(caps, caps[1:]): a_["end"] = min(a_["end"], b_["start"])
caps[-1]["end"] = min(caps[-1]["end"] + 0.3, END_IN)

CFONT = MF("ExtraBold", 66); CLH = 90; CMAXW = 900
def layout(words, ccy):
    d = ImageDraw.Draw(Image.new("RGB", (4, 4))); sp = d.textlength(" ", font=CFONT)
    wl = [d.textlength(w, font=CFONT) for w in words]
    def width(a, b): return sum(wl[a:b]) + sp * (b - a - 1)
    if width(0, len(words)) <= CMAXW * 0.66 or len(words) < 3: lines = [(0, len(words))]
    else:
        best = min(range(1, len(words)), key=lambda k: max(width(0, k), width(k, len(words))))
        lines = [(0, best), (best, len(words))]
    boxes = [None] * len(words); y0 = 230 - CLH * len(lines) / 2
    for li, (a, b) in enumerate(lines):
        x = (W - width(a, b)) / 2; y = y0 + li * CLH
        for k in range(a, b): boxes[k] = (x, y, x + wl[k], y + CLH); x += wl[k] + sp
    return boxes

_capcache = {}
def caption_text(ci, active):
    key = (ci, active)
    if key not in _capcache:
        c = caps[ci]; boxes = c.setdefault("boxes", layout(c["words"], 0))
        lay = Image.new("RGBA", (W, 460), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        for k, (w, bx) in enumerate(zip(c["words"], boxes)):
            if k == active: d.text((bx[0], bx[1] + 6), w, font=CFONT, fill=NAVY)
            else: d.text((bx[0], bx[1] + 6), w, font=CFONT, fill=WHITE, stroke_width=6, stroke_fill=NAVY)
        if len(_capcache) > 300: _capcache.clear()
        _capcache[key] = lay
    return _capcache[key]

def draw_caption(frame, t, ccy):
    for ci, c in enumerate(caps):
        if not (c["start"] <= t < c["end"]): continue
        boxes = c.setdefault("boxes", layout(c["words"], 0))
        act = max([k for k, ts in enumerate(c["ts"]) if ts <= t] or [0])
        k = ease_out((t - c["ts"][act]) / 0.10)
        cur = boxes[act]; prv = boxes[act - 1] if act > 0 and boxes[act - 1][1] == cur[1] else cur
        bx = [lerp(p, q, k) for p, q in zip(prv, cur)]
        region = Image.new("RGBA", (W, 460), (0, 0, 0, 0)); d = ImageDraw.Draw(region)
        d.rounded_rectangle((bx[0] - 15, bx[1] + 6, bx[2] + 15, bx[3] - 2), 15, fill=GOLD + (255,))
        region.alpha_composite(caption_text(ci, act))
        u = t - c["start"]; sc = 0.86 + 0.14 * back_out(u / 0.20)
        al = clamp(u / 0.06) * clamp((c["end"] - t) / 0.06)
        if abs(sc - 1) > 0.002: region = region.resize((int(W * sc), int(460 * sc)), Image.BICUBIC)
        blk = Image.new("RGBA", region.size, (0, 0, 0, 255))
        blk.putalpha(region.getchannel("A").point(lambda v: int(v * 0.55)))
        sh = blk.filter(ImageFilter.GaussianBlur(9))
        region = fade(region, al); sh = fade(sh, al)
        x = (W - region.width) // 2; y = int(ccy - region.height / 2)
        frame.alpha_composite(sh, (x + 4, y + 9)); frame.alpha_composite(region, (x, y))

# ---------------------------------------------------------------- layout: full screen <-> split screen
PIP_RANGES = [(6.80, 38.30)]
TR = 0.70
def ease_io(x): x = clamp(x); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
def pip_amount(t):
    k = 0.0
    for a, b in PIP_RANGES:
        k = max(k, ease_io((t - a) / TR) * (1 - ease_io((t - b) / TR)))
    return k
WIN = (154, 798, 926, 1680)          # speaker window: whole head + shoulders, nothing cropped
SC_PIP = 1.615
FACE = (239.0, 355.0); HEAD_TOP = 160.0
ZK = [(0, 1.00), (39.83, 1.05), (41.85, 1.00), (44.89, 1.07)]
def zoom_at(t):
    z0, t0, zprev = 1.0, 0.0, 1.0
    for i, (tk, zk) in enumerate(ZK):
        if tk <= t: t0, z0 = tk, zk; zprev = ZK[i - 1][1] if i else zk
    return zprev + (z0 - zprev) * ease_io((t - t0) / 0.6)

x_ = np.arange(256) / 255.0
s_curve = np.clip(x_ + 0.16 * (x_ - 0.5) * (1 - abs(2 * x_ - 1)), 0, 1)
def curve(lo, hi): return np.clip((s_curve + lo * (1 - x_) ** 2.2 + hi * x_ ** 2.2) * 255, 0, 255).astype(np.uint8)
LUT = np.stack([curve(-0.010, 0.022), curve(0.003, 0.010), curve(0.026, -0.015)], 1)[:, None, :]
VIG = (1 - 0.24 * np.clip(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H * 0.45) / (H * 0.62)) ** 2, 0, 1) ** 1.3).astype(np.float32)[..., None]
GRAIN = [np.random.default_rng(i).normal(0, 3.5, (H // 2, W // 2, 1)).astype(np.float32) for i in range(6)]
r_ = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.40) / H) ** 2)
BG = (np.array([3, 11, 24], np.float32) + (np.array([11, 52, 88], np.float32) - np.array([3, 11, 24], np.float32)) * np.clip(1 - r_ * 1.7, 0, 1)[..., None])
# soft shadow of the speaker window, precomputed
_shm = Image.new("L", (W, H), 0); ImageDraw.Draw(_shm).rounded_rectangle((WIN[0] + 10, WIN[1] + 22, WIN[2] + 10, WIN[3] + 22), 30, fill=150)
WIN_SHADOW = np.asarray(_shm.filter(ImageFilter.GaussianBlur(26)), np.float32)[..., None] / 255
class _NoClean:
    def clean(self, f, i): return f
cleaner = _NoClean()

def speaker_and_bg(src, idx, t):
    L = pip_amount(t)
    img = cleaner.clean(src, idx)
    sc = lerp(W / SW * zoom_at(t) * (1 + 0.10 * (1 - ease_out(t / 0.8))), SC_PIP, L)
    fx, fy = FACE
    px = W / 2
    py = lerp(fy * W / SW, WIN[1] + 125 + (fy - HEAD_TOP) * SC_PIP, L)
    M = np.float32([[sc, 0, px - fx * sc], [0, sc, py - fy * sc]])
    sp = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    sp = cv2.LUT(sp, LUT).astype(np.float32)
    sp += cv2.resize(GRAIN[idx % 6], (W, H))[..., None]
    if L < 0.001:
        out = np.clip(sp * VIG, 0, 255).astype(np.uint8)
        if t < 0.7:   # soft entrance: motion blur fading out + fade from black
            kb = int(40 * (1 - ease_out(t / 0.7)))
            if kb > 1: out = cv2.filter2D(out, -1, np.ones((kb, 1), np.float32) / kb)
            out = (out * ease_out(t / 0.35)).astype(np.uint8)
        return Image.fromarray(out).convert("RGBA"), L
    x0 = lerp(0, WIN[0], L); y0 = lerp(0, WIN[1], L); x1 = lerp(W, WIN[2], L); y1 = lerp(H, WIN[3], L)
    rad = lerp(0, 30, L)
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rounded_rectangle((x0, y0, x1, y1), rad, fill=255)
    m = np.asarray(m.filter(ImageFilter.GaussianBlur(1.0)), np.float32)[..., None] / 255
    bg = BG * (1 - WIN_SHADOW * smooth((L - 0.7) / 0.3))
    out = bg * (1 - m) + sp * m
    frame = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).convert("RGBA")
    ImageDraw.Draw(frame).rounded_rectangle((x0, y0, x1, y1), rad, outline=GOLD + (int(210 * L),), width=2)
    return frame, L

# ---------------------------------------------------------------- banners
top = Image.open(KIT / "assets" / "topo.jpg").convert("RGB")
bot = Image.open(KIT / "assets" / "rodape.jpg").convert("RGB")
ta = np.asarray(top).astype(int); colmax = ta.max(axis=(0, 2))
lft = int(np.argmax(colmax > 60)); rgt = len(colmax) - int(np.argmax(colmax[::-1] > 60))
top = top.crop((lft, 0, rgt, top.height))
top = top.resize((W, round(top.height * W / top.width)), Image.LANCZOS).convert("RGBA")
bot = bot.resize((W, round(bot.height * W / bot.width)), Image.LANCZOS).convert("RGBA")
TOPH = top.height
def shine_layer(size, p):
    w, h = size
    gx = np.arange(w)[None, :] + np.arange(h)[:, None] * 0.5
    band = np.exp(-((gx - (-300 + p * (w + 600))) / 90.0) ** 2) * 0.55
    lay = Image.new("RGBA", (w, h), (255, 240, 200, 0)); lay.putalpha(Image.fromarray((band * 255).astype(np.uint8)))
    return lay
SHINES = [0.75, 15.0, 31.5, 45.0]
BAN_IN = 0.4
def draw_banners(frame, t):
    if t < BAN_IN: return
    k = back_out((t - BAN_IN) / 0.55, 1.2)
    ty = int(-TOPH * (1 - k)); by = int(H - bot.height + bot.height * (1 - k))
    tp, bp = top, bot
    for s in SHINES:
        p = (t - s) / 0.9
        if 0 <= p <= 1:
            tp = Image.alpha_composite(top, shine_layer(top.size, p)); bp = Image.alpha_composite(bot, shine_layer(bot.size, p))
    frame.alpha_composite(tp, (0, ty)); frame.alpha_composite(bp, (0, by))
    if t > BAN_IN + 0.4:
        prog = clamp(t / END_IN); d = ImageDraw.Draw(frame); y = by - 7
        d.rectangle((0, y, W, y + 6), fill=(5, 20, 34, 200))
        d.rectangle((0, y, int(W * prog), y + 6), fill=GOLD + (255,))
        d.ellipse((int(W * prog) - 7, y - 4, int(W * prog) + 7, y + 10), fill=GOLD_L + (255,))

# ---------------------------------------------------------------- line icons (thin stroke, editorial look)
def line_icon(kind, size=46, col=GOLD):
    s = size * 4; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c = col + (255,); w = 12; m = s / 2
    if kind == "family":
        for dx, r in [(-40, 26), (40, 26)]:
            d.ellipse((m + dx - r, 30, m + dx + r, 30 + 2 * r), outline=c, width=w)
            d.arc((m + dx - 54, 100, m + dx + 54, 250), 180, 360, fill=c, width=w)
        d.line((20, 175, s - 20, 175), fill=c, width=w)
    elif kind == "crane":
        d.line((60, s - 20, 60, 40), fill=c, width=w); d.line((30, 46, s - 20, 46), fill=c, width=w)
        d.line((60, 100, 120, 46), fill=c, width=w); d.line((150, 46, 150, 110), fill=c, width=w)
        d.rectangle((128, 110, 172, 145), outline=c, width=w); d.line((20, s - 20, 120, s - 20), fill=c, width=w)
    elif kind == "pill":
        p = Image.new("RGBA", (s, s), (0, 0, 0, 0)); pd = ImageDraw.Draw(p)
        pd.rounded_rectangle((m - 80, m - 34, m + 80, m + 34), 34, outline=c, width=w); pd.line((m, m - 34, m, m + 34), fill=c, width=w)
        im.alpha_composite(p.rotate(38, Image.BICUBIC))
    elif kind == "cap":
        d.polygon([(m, 40), (s - 14, 90), (m, 140), (14, 90)], outline=c, width=w)
        d.arc((m - 56, 80, m + 56, 190), 0, 180, fill=c, width=w); d.line((s - 34, 98, s - 34, 160), fill=c, width=w)
    elif kind == "bulb":
        d.arc((m - 56, 22, m + 56, 134), 140, 400, fill=c, width=w)
        d.line((m - 28, 128, m - 24, 160), fill=c, width=w); d.line((m + 28, 128, m + 24, 160), fill=c, width=w)
        d.line((m - 26, 168, m + 26, 168), fill=c, width=w); d.line((m - 18, 190, m + 18, 190), fill=c, width=w)
    elif kind == "drop":
        d.line((m, 22, m - 58, 120), fill=c, width=w); d.line((m, 22, m + 58, 120), fill=c, width=w)
        d.arc((m - 66, 70, m + 66, 200), 0, 180, fill=c, width=w)
        d.arc((m - 66, 70, m + 66, 200), 150, 180, fill=c, width=w); d.arc((m - 66, 70, m + 66, 200), 0, 30, fill=c, width=w)
    elif kind == "leaf":
        d.arc((30, 30, s - 30, s + 60), 200, 340, fill=c, width=w); d.arc((30, -60, s - 30, s - 30), 20, 160, fill=c, width=w)
        d.line((50, s - 40, s - 50, 50), fill=c, width=w)
    elif kind == "sun":
        d.ellipse((m - 40, m - 40, m + 40, m + 40), outline=c, width=w)
        for a in range(0, 360, 45):
            ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
            d.line((m + 62 * ca, m + 62 * sa, m + 84 * ca, m + 84 * sa), fill=c, width=w)
    return im.resize((size, size), Image.LANCZOS)

# ---------------------------------------------------------------- typography helpers
_tcache = {}
def timg(text, font, fill):
    key = (text, id(font), fill)
    if key not in _tcache:
        d = ImageDraw.Draw(Image.new("RGBA", (4, 4))); b = d.textbbox((0, 0), text, font=font)
        im = Image.new("RGBA", (b[2] - b[0] + 24, b[3] - b[1] + 24), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((12 - b[0], 12 - b[1]), text, font=font, fill=fill)
        if len(_tcache) > 600: _tcache.clear()
        _tcache[key] = im
    return _tcache[key]

def put(canvas, im, x, y, k, anchor="l", dy=22):
    """blur-in reveal: fades, un-blurs and rises into place"""
    k = clamp(k)
    if k <= 0: return
    if k < 1:
        im = im.filter(ImageFilter.GaussianBlur((1 - k) * 9)); im = fade(im, k)
    if anchor == "c": x = x - im.width / 2
    elif anchor == "r": x = x - im.width
    canvas.alpha_composite(im, (int(x - 12), int(y - 12 + dy * (1 - ease_out(k)))))

def count(v, k, dec):
    return f"{v * ease_out(k):.{dec}f}".replace(".", ",")

# ---------------------------------------------------------------- panels
PX0, PX1 = 40, 1040
PY0, PY1 = TOPH + 24, 772
PW, PH = PX1 - PX0, PY1 - PY0
F_LAB = MF("Bold", 24); F_T = MF("ExtraBold", 46); F_I = MF("Bold", 33); F_S = MF("SemiBold", 27)
F_N = MF("Black", 84); F_N2 = MF("Black", 60); F_SRC = MF("Medium", 20); F_Q = MF("ExtraBold", 50)
DIM = (255, 255, 255, 140); WH = (255, 255, 255, 255); GD = GOLD + (255,); GDL = GOLD_L + (255,)

_pbase = None
def panel_base():
    global _pbase
    if _pbase is None:
        p = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
        g = np.zeros((PH, PW, 4), np.uint8)
        f = np.linspace(0, 1, PH)[:, None]
        g[..., 0] = (8 - 4 * f); g[..., 1] = (34 - 12 * f); g[..., 2] = (60 - 20 * f); g[..., 3] = 236
        p = Image.fromarray(g, "RGBA")
        m = Image.new("L", (PW, PH), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, PW - 1, PH - 1), 26, fill=236)
        p.putalpha(m)
        ImageDraw.Draw(p).rounded_rectangle((0, 0, PW - 1, PH - 1), 26, outline=GOLD + (90,), width=2)
        _pbase = p
    return _pbase.copy()

def label(p, text, u):
    d = ImageDraw.Draw(p)
    d.rectangle((44, 40, 44 + int(26 * ease_out(u / 0.4)), 43), fill=GD)
    put(p, timg(text, F_LAB, GD), 82, 28, u / 0.4, dy=0)

LIST = [("BOLSA FAMÍLIA", 7.73, "family", ("R$ ", 600, 0, ""), "VALOR MÍNIMO POR FAMÍLIA"),
        ("NOVO PAC", 9.50, "crane", ("R$ ", 1.7, 1, " TRI"), "PREVISTOS EM INVESTIMENTOS"),
        ("FARMÁCIA POPULAR", 11.47, "pill", ("", 41, 0, " ITENS"), "100% GRATUITOS"),
        ("PÉ-DE-MEIA", 12.47, "cap", ("ENSINO MÉDIO", None, 0, ""), "INCENTIVO PARA O ALUNO CONCLUIR"),
        ("LUZ PARA TODOS", 13.33, "bulb", ("+", 17, 0, " MI"), "DE PESSOAS ATENDIDAS")]
ICO = {k: line_icon(k) for k in ["family", "crane", "pill", "cap", "bulb"]}
ICO_BIG = {k: line_icon(k, 64) for k in ["drop", "leaf", "sun"]}
ICO_DIM = {k: line_icon(k, 64, (150, 140, 120)) for k in ["sun"]}

def panel_list(t, t0):
    u = t - t0; p = panel_base(); d = ImageDraw.Draw(p)
    label(p, "A LISTINHA", u)
    act = max([i for i, it in enumerate(LIST) if it[1] <= t] or [0])
    y = 80
    for i, (name, ts, ic, num, sub) in enumerate(LIST):
        k = (t - ts) / 0.45
        if k > 0:
            if i == act:
                ka = ease_out(k)
                d.rounded_rectangle((32, y - 4, PW - 32, y + 50), 12, fill=GOLD + (int(26 * ka),))
                d.rectangle((32, y - 4, 35, y + 50), fill=GOLD + (int(255 * ka),))
            put(p, ICO[ic], 60, y, k, dy=0)
            put(p, timg(name, F_I, WH if i == act else DIM), 124, y + 4, k, dy=14)
            ck = clamp((t - ts - 0.25) / 0.3)
            if ck > 0:
                cx, cy = PW - 74, y + 24
                pts = [(cx - 13, cy), (cx - 3, cy + 10), (cx + 16, cy - 12)]
                seg = [pts[0], (lerp(pts[0][0], pts[1][0], min(1, ck / 0.4)), lerp(pts[0][1], pts[1][1], min(1, ck / 0.4)))]
                if ck > 0.4: seg = [pts[0], pts[1], (lerp(pts[1][0], pts[2][0], (ck - 0.4) / 0.6), lerp(pts[1][1], pts[2][1], (ck - 0.4) / 0.6))]
                d.line(seg, fill=GD, width=4, joint="curve")
        y += 54
    name, ts, ic, (pre, val, dec, suf), sub = LIST[act]
    k = (t - ts - 0.15) / 0.5
    d.line((44, PH - 150, PW - 44, PH - 150), fill=GOLD + (70,), width=1)
    big = pre + (count(val, clamp(k), dec) if val is not None else "") + suf
    put(p, timg(big, F_N2 if val is None else F_N, GD), 44, PH - 140, k)
    put(p, timg(sub, F_S, WH), 44, PH - 40 - 10, k - 0.25, dy=10)
    put(p, timg("Dados: Governo Federal", F_SRC, (150, 162, 178, 255)), PW - 44, PH - 40, 1, anchor="r", dy=0)
    return p

FLOW = [[(PW - 430 + i * 6, 150 + j * 18 + 14 * math.sin(i / 11 + j)) for i in range(65)] for j in range(3)]
def panel_river(t, t0):
    u = t - t0; p = panel_base(); d = ImageDraw.Draw(p)
    label(p, "OBRA HÍDRICA", u)
    put(p, timg("TRANSPOSIÇÃO DO", F_T, WH), 44, 84, (u - 0.1) / 0.45)
    put(p, timg("RIO SÃO FRANCISCO", F_T, GD), 44, 140, (u - 0.25) / 0.45)
    for j, path in enumerate(FLOW):   # thin flowing lines
        kk = ease_out((u - 0.3 - j * 0.12) / 1.2); n = max(2, int(len(path) * kk))
        if kk > 0: d.line(path[:n], fill=CYAN + (110 - j * 25,), width=3, joint="curve")
        if kk >= 1:
            q = (u * 0.5 + j * 0.3) % 1; X, Y = path[int(q * (len(path) - 1))]
            d.ellipse((X - 4, Y - 4, X + 4, Y + 4), fill=(220, 245, 255, 220))
    d.line((PW / 2, PH - 200, PW / 2, PH - 50), fill=GOLD + (int(120 * clamp((u - 1.0) / 0.4)),), width=1)
    k1 = (u - 1.0) / 0.9; k2 = (u - 1.4) / 0.9
    put(p, timg(count(477, clamp(k1), 0) + " KM", F_N, GD), 44, PH - 205, k1)
    put(p, timg("DE CANAIS", F_S, WH), 46, PH - 100, k1 - 0.2, dy=10)
    put(p, timg("EIXOS NORTE E LESTE", F_SRC, (180, 190, 205, 255)), 46, PH - 62, k1 - 0.3, dy=10)
    put(p, timg("~" + count(12, clamp(k2), 0) + " MI", F_N, GD), PW / 2 + 40, PH - 205, k2)
    put(p, timg("DE PESSOAS ATENDIDAS", F_S, WH), PW / 2 + 42, PH - 100, k2 - 0.2, dy=10)
    put(p, timg("Dados: Governo Federal", F_SRC, (150, 162, 178, 255)), PW / 2 + 42, PH - 62, k2 - 0.3, dy=10)
    return p

def panel_sertao(t, t0):
    u = t - t0; p = panel_base(); d = ImageDraw.Draw(p)
    label(p, "NO SERTÃO", u)
    cw = (PW - 88 - 24) // 2; ch = PH - 120; y0 = 92
    xa, xb = 44, 44 + cw + 24
    ka = ease_out(u / 0.5)
    # ANTES card (muted, warm grey)
    d.rounded_rectangle((xa, y0, xa + cw, y0 + ch), 18, fill=(46, 40, 34, int(200 * ka)), outline=(150, 135, 110, int(150 * ka)), width=1)
    put(p, timg("ANTES", F_LAB, (190, 175, 150, 255)), xa + 30, y0 + 28, u / 0.5, dy=0)
    put(p, ICO_DIM["sun"], xa + 30, y0 + 84, (u - 0.2) / 0.5)
    put(p, timg("A ÁGUA", F_T, (225, 215, 200, 255)), xa + 30, y0 + 176, (u - 0.3) / 0.5)
    put(p, timg("NÃO CHEGAVA", F_T, (225, 215, 200, 255)), xa + 30, y0 + 230, (u - 0.4) / 0.5)
    # AGORA card: lights up when the water arrives
    kw = ease_out((t - 25.73) / 0.6)
    fill = (int(lerp(30, 10, kw)), int(lerp(40, 70, kw)), int(lerp(52, 72, kw)), int(200 * ka))
    d.rounded_rectangle((xb, y0, xb + cw, y0 + ch), 18, fill=fill, outline=(int(lerp(110, 120, kw)), int(lerp(120, 210, kw)), int(lerp(130, 200, kw)), int(lerp(110, 230, kw) * ka)), width=2 if kw > 0.5 else 1)
    put(p, timg("AGORA", F_LAB, GD), xb + 30, y0 + 28, u / 0.5, dy=0)
    put(p, ICO_BIG["drop"], xb + 30, y0 + 84, (t - 25.73) / 0.5)
    put(p, timg("A ÁGUA CHEGA", F_I, WH), xb + 110, y0 + 98, (t - 25.85) / 0.5)
    put(p, ICO_BIG["leaf"], xb + 30, y0 + 176, (t - 27.77) / 0.5)
    put(p, timg("PLANTAÇÕES", F_I, WH), xb + 110, y0 + 176, (t - 27.9) / 0.5)
    put(p, timg("CRESCEM", F_I, WH), xb + 110, y0 + 220, (t - 28.0) / 0.5)
    put(p, timg("O SERTÃO", F_T, GD), xb + 30, y0 + 276, (t - 29.13) / 0.5)
    put(p, timg("ESTÁ VERDE", F_T, GD), xb + 30, y0 + 328, (t - 29.3) / 0.5)
    return p

def panel_sp(t, t0):
    u = t - t0; p = panel_base(); d = ImageDraw.Draw(p)
    if t < 45.4:
        label(p, "A CONVERSA DE SEMPRE", u)
        loc = t >= 43.37; tb = 43.37 if loc else t0
        q1, q2 = ("“SÃO PAULO É A", "LOCOMOTIVA DO BRASIL”") if loc else ("“SÃO PAULO", "SUSTENTA O BRASIL”")
        put(p, timg(q1, F_Q, WH), PW / 2, PH / 2 - 70, (t - tb - 0.1) / 0.45, anchor="c")
        put(p, timg(q2, F_Q, WH), PW / 2, PH / 2 - 8, (t - tb - 0.2) / 0.45, anchor="c")
        ks = clamp((t - 44.6) / 0.45)
        if ks > 0:
            d.line((110, PH / 2 + 2, 110 + (PW - 220) * ease_out(ks), PH / 2 - 22), fill=(205, 70, 70, 255), width=6)
        return p
    v = t - 45.4
    label(p, "QUEM CONSTRUIU SÃO PAULO", v)
    put(p, timg("O POVO DO", F_T, WH), 44, 96, (t - 46.5) / 0.45)
    put(p, timg("NORDESTE", MF("Black", 104), GD), 40, 150, (t - 46.7) / 0.5)
    d.line((44, 300, 44 + int((PW - 88) * ease_out((t - 47.2) / 0.8)), 300), fill=GOLD + (120,), width=1)
    put(p, timg("QUE MIGROU PRA CÁ", F_I, WH), 44, 330, (t - 48.73) / 0.45)
    kb = (t - 50.47) / 0.45
    if kb > 0:
        txt = timg("O POVO TRABALHADOR", F_T, NAVY + (255,))
        bw = txt.width + 20; kk = ease_out(kb)
        d.rounded_rectangle((44, 400, 44 + int(bw * kk), 470), 14, fill=GD)
        if kk > 0.6: put(p, txt, 54, 412, (kk - 0.6) / 0.4, dy=0)
    return p


import cards as C
def fmt_int(v): return f"{int(v):,}".replace(",", ".")
def wrap_lines(text, font, maxw):
    d = ImageDraw.Draw(Image.new("RGBA", (4, 4))); out, cur = [], ""
    for w in text.split():
        t2 = (cur + " " + w).strip()
        if d.textlength(t2, font=font) > maxw and cur: out.append(cur); cur = w
        else: cur = t2
    if cur: out.append(cur)
    return out
MUTE = (175, 188, 204, 255)

def panel_money(t, t0):
    u = t - t0; p = panel_base(); d = ImageDraw.Draw(p)
    label(p, "DENÚNCIA DO MP-RJ · 2020", u)
    k = clamp((t - 8.0) / 1.4)
    put(p, timg("R$ " + fmt_int(2062360 * ease_out(k)), MF("Black", 92), GD), 44, 84, (t - 7.9) / 0.5)
    put(p, timg("DEPOSITADOS NA CONTA DE FABRÍCIO QUEIROZ", F_S, WH), 46, 196, (t - 8.3) / 0.5, dy=12)
    d.line((44, 252, PW - 44, 252), fill=GOLD + (int(90 * clamp((u - 0.6) / 0.4)),), width=1)
    d.line((PW / 2, 272, PW / 2, 392), fill=GOLD + (int(90 * clamp((u - 0.8) / 0.4)),), width=1)
    k1 = (t - 9.4) / 0.6; k2 = (t - 9.8) / 0.6
    put(p, timg(str(int(483 * ease_out(clamp(k1)))), F_N, GD), 44, 272, k1)
    put(p, timg("DEPÓSITOS", F_S, WH), 46, 368, k1 - 0.2, dy=10)
    put(p, timg(str(int(13 * ease_out(clamp(k2)))), F_N, GD), PW / 2 + 40, 272, k2)
    put(p, timg("ASSESSORES DO GABINETE", F_S, WH), PW / 2 + 42, 368, k2 - 0.2, dy=10)
    put(p, timg("Período: 2007 a 2018 · Flávio Bolsonaro nega as acusações", F_SRC, MUTE), 44, PH - 62, (t - 10.4) / 0.5, dy=6)
    put(p, timg("Fonte: MP-RJ, segundo a imprensa", F_SRC, (150, 162, 178, 255)), 44, PH - 36, (t - 10.5) / 0.5, dy=6)
    return p

TIMELINE = [(14.30, "2020", "MP-RJ denuncia Flávio e Queiroz"),
            (16.20, "FEV 2021", "STJ anula a quebra de sigilo bancário e fiscal"),
            (17.90, "NOV 2021", "STJ anula as decisões do juiz de 1ª instância"),
            (20.70, "MAI 2022", "TJ-RJ arquiva a denúncia")]
def panel_timeline(t, t0):
    u = t - t0; p = panel_base(); d = ImageDraw.Draw(p)
    label(p, "O CAMINHO DO CASO", u)
    x = 70; y0 = 104; step = 98
    last = max([i for i, (ts, _, _) in enumerate(TIMELINE) if ts <= t] or [-1])
    if last >= 0:   # gold line grows down to the latest event
        yl = y0 + 18 + step * last * ease_out((t - TIMELINE[last][0]) / 0.5) if last > 0 else y0 + 18
        yl = y0 + 18 + step * (last - 1) + step * ease_out((t - TIMELINE[last][0]) / 0.5) if last > 0 else y0 + 18
        d.line((x, y0 + 18, x, yl), fill=GOLD + (200,), width=3)
    hot = 2 if t >= 20.0 else -1     # "detalhe técnico": the November 2021 ruling
    for i, (ts, when, what) in enumerate(TIMELINE):
        k = (t - ts) / 0.45
        if k <= 0: continue
        cy = y0 + 18 + i * step; r = 11 * clamp(ease_out(k) * 1.2, 0, 1)
        d.ellipse((x - r, cy - r, x + r, cy + r), fill=GD)
        if i == hot:
            kh = ease_out((t - 20.0) / 0.4)
            d.rounded_rectangle((x + 30, cy - 34, PW - 36, cy + 52), 12, fill=GOLD + (int(36 * kh),), outline=GOLD + (int(200 * kh),), width=2)
        put(p, timg(when, F_LAB, GD), x + 48, cy - 24, k, dy=10)
        put(p, timg(what, F_I if len(what) < 34 else MF("Bold", 29), WH), x + 48, cy + 4, k - 0.1, dy=12)
    return p

CLIP6 = dict(kicker="STJ  ·  CASO DAS RACHADINHAS",
             head="STJ anula atos de juiz contra Flávio Bolsonaro no caso das rachadinhas",
             hl=(1, 4), src="Manchete: Consultor Jurídico (ConJur)  ·  9 nov. 2021", stamp="PROVAS ANULADAS", seed=5, rot=-1.5)
CBUILT6 = C.build(CLIP6)
_st = C.stamp_img("PROVAS ANULADAS"); CSTAMP6 = _st.resize((int(_st.width * 0.72), int(_st.height * 0.72)), Image.LANCZOS)
HL6 = (22.9, 23.8); STAMP6 = 24.3
_c6 = {}
def panel_clip(t, t0):
    u = t - t0; p = panel_base()
    label(p, "NA IMPRENSA", u)
    pr = round(smooth((t - HL6[0]) / (HL6[1] - HL6[0])), 3)
    if pr not in _c6:
        im = C.render(CBUILT6, pr); sc = min(860 / im.width, (PH - 110) / im.height)
        _c6[pr] = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    card = _c6[pr]
    k = ease_out((u - 0.1) / 0.6); sc = 0.96 + 0.04 * k
    c2 = card.resize((int(card.width * sc), int(card.height * sc)), Image.BICUBIC).rotate(-1.2, Image.BICUBIC, expand=True)
    blk = Image.new("RGBA", c2.size, (0, 0, 0, 255)); blk.putalpha(c2.getchannel("A").point(lambda v: int(v * 0.5)))
    x = int(PW / 2 - c2.width / 2); y = int(78 + (PH - 78) / 2 - c2.height / 2)
    p.alpha_composite(fade(blk.filter(ImageFilter.GaussianBlur(14)), k), (x + 10, y + 16 + int(20 * (1 - k))))
    put(p, c2, x + 12, y + 12, (u - 0.1) / 0.6, dy=20)
    su = t - STAMP6
    if su > 0:
        kk = clamp(su / 0.14); s2 = 1.5 - 0.5 * ease_out(kk)
        st2 = fade(CSTAMP6.resize((int(CSTAMP6.width * s2), int(CSTAMP6.height * s2)), Image.BICUBIC).rotate(-8, Image.BICUBIC, expand=True), kk)
        p.alpha_composite(st2, (int(x + c2.width - st2.width * 0.88), int(y + c2.height * 0.66 - st2.height * 0.5)))
    return p

def panel_explain(t, t0):
    u = t - t0; p = panel_base(); d = ImageDraw.Draw(p)
    label(p, "ENTENDA", u)
    put(p, timg("PROVA ANULADA", F_T, GD), 44, 82, (u - 0.05) / 0.45)
    put(p, timg("NÃO É PROVA INEXISTENTE", F_T, WH), 44, 136, (u - 0.2) / 0.45)
    cw = (PW - 88 - 24) // 2; y0 = 212; ch = 190
    cols = [("ANULADA", "A prova existe, mas fica fora do processo por erro de procedimento.", 0.5),
            ("ABSOLVIÇÃO", "A Justiça julga o caso e conclui pela inocência.", 0.8)]
    for j, (tt, body, dl) in enumerate(cols):
        x = 44 + j * (cw + 24); kk = ease_out((u - dl) / 0.5)
        if kk <= 0: continue
        d.rounded_rectangle((x, y0, x + cw, y0 + ch), 16, fill=(255, 255, 255, int(12 * kk)), outline=GOLD + (int(110 * kk),), width=1)
        put(p, timg(tt, F_LAB, GD), x + 24, y0 + 22, (u - dl) / 0.5, dy=0)
        for li, ln in enumerate(wrap_lines(body, F_S, cw - 48)):
            put(p, timg(ln, F_S, WH), x + 24, y0 + 62 + li * 36, (u - dl - 0.1 - li * 0.05) / 0.5, dy=10)
    put(p, timg("No caso das rachadinhas, o mérito nunca foi julgado.", MF("Bold", 29), GDL), 44, PH - 84, (u - 1.4) / 0.5, dy=10)
    put(p, timg("Flávio Bolsonaro nega as acusações.", F_SRC, MUTE), 44, PH - 40, (u - 1.6) / 0.5, dy=6)
    return p

PANELS = [(6.95, 13.95, panel_money), (13.95, 22.20, panel_timeline), (22.20, 31.60, panel_clip), (31.60, 38.10, panel_explain)]

_psh = Image.new("RGBA", (PW + 80, PH + 80), (0, 0, 0, 0))
_m = Image.new("L", (PW + 80, PH + 80), 0); ImageDraw.Draw(_m).rounded_rectangle((40, 54, 40 + PW, 54 + PH), 26, fill=130)
_psh.putalpha(_m.filter(ImageFilter.GaussianBlur(20)))

def hblur(img, length):
    """horizontal motion blur on premultiplied RGBA"""
    L = int(length)
    if L < 2: return img
    a = np.asarray(img, np.float32); al = a[..., 3:4] / 255
    pm = np.concatenate([a[..., :3] * al, a[..., 3:4]], 2)
    k = np.ones((1, L), np.float32) / L
    pm = cv2.filter2D(pm, -1, k, borderType=cv2.BORDER_CONSTANT)
    al2 = np.clip(pm[..., 3:4], 1e-3, 255) / 255
    rgb = np.where(pm[..., 3:4] > 0.5, pm[..., :3] / al2, 0)
    return Image.fromarray(np.clip(np.concatenate([rgb, pm[..., 3:4]], 2), 0, 255).astype(np.uint8), "RGBA")

def slide_x(t, a, b, chained_in, chained_out):
    """x offset of a panel: slides in from the right, out to the left (with ease)"""
    din = 0.55
    kin = ease_out((t - a) / din)
    x = 340 * (1 - kin)
    if t > b and not chained_out:
        x -= 340 * ease_in((t - b) / 0.4)
    return x, kin

def draw_panels(frame, t):
    for a, b, fn in PANELS:
        if not (a - 0.01 <= t < b + 0.45): continue
        chained_in = any(abs(a - b2) < 0.05 for _, b2, _ in PANELS)
        chained_out = any(abs(b - a2) < 0.05 for a2, _, _ in PANELS)
        if chained_out and t >= b + 0.40: continue
        p = fn(min(t, b), a)
        x, kin = slide_x(t, a, b, chained_in, chained_out)
        x_prev, _ = slide_x(t - 1 / FPS, a, b, chained_in, chained_out)
        al = clamp(kin * 1.6)
        if t > b and not chained_out: al *= 1 - ease_in((t - b) / 0.4)
        if chained_out and t > b: al = 1 - ease_in((t - b) / 0.40)   # outgoing panel fades under the incoming one
        speed = abs(x - x_prev)
        if speed > 1.5: p = hblur(p, speed * 1.8)
        frame.alpha_composite(fade(_psh, al), (PX0 - 40 + int(x), PY0 - 40))
        frame.alpha_composite(fade(p, al), (PX0 + int(x), PY0))

# ---------------------------------------------------------------- end card
def end_card(t):
    u = t - END_IN
    img = Image.fromarray(BG.astype(np.uint8)).convert("RGBA")
    k = back_out(u / 0.7, 1.3); sc = 0.7 + 0.3 * k
    art = fade(top.resize((int(W * sc), int(TOPH * sc)), Image.LANCZOS), clamp(u / 0.35))
    ax, ay = (W - art.width) // 2, int(H * 0.40 - art.height / 2)
    img.alpha_composite(art, (ax, ay))
    d = ImageDraw.Draw(img); k2 = ease_out((u - 0.45) / 0.5)
    if k2 > 0:
        y = int(H * 0.55 + 40 * (1 - k2))
        d.text((W / 2, y), "SIGA PARA MAIS", font=MF("ExtraBold", 64), fill=WHITE + (int(255 * k2),), anchor="mm")
        d.text((W / 2, y + 74), "OPINIÃO • ATUALIDADES • REAÇÕES", font=MF("SemiBold", 40), fill=GOLD + (int(255 * k2),), anchor="mm")
        lw = int(360 * ease_out((u - 0.6) / 0.6)); d.rectangle((W / 2 - lw, y + 120, W / 2 + lw, y + 124), fill=GOLD + (255,))
    p = (u - 1.1) / 0.9
    if 0 <= p <= 1: img.alpha_composite(shine_layer(art.size, p), (ax, ay))
    img.alpha_composite(bot, (0, H - bot.height))
    return img

# ---------------------------------------------------------------- main
def frames_mode(ts):
    outs = []
    for t in ts:
        idx = min(int(round(t * 30)), NSRC - 1)
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-vf", f"select=eq(n\\,{idx})", "-frames:v", "1",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        src = np.frombuffer(raw, np.uint8).reshape(SH, SW, 3).copy()
        if t < END_IN:
            frame, L = speaker_and_bg(src, idx, t); draw_panels(frame, t)
            draw_caption(frame, t, lerp(1450, 1585, clamp(L))); draw_banners(frame, t)
        else: frame = end_card(t)
        if len(ts) == 1: frame.convert("RGB").save(OUTFILE, quality=92); return
        outs.append(frame.convert("RGB").resize((360, 640), Image.LANCZOS))
    sheet = Image.new("RGB", (360 * len(outs), 640))
    for i, o in enumerate(outs): sheet.paste(o, (i * 360, 0))
    sheet.save(OUTFILE, quality=90)

def main():
    if MODE.startswith("frames"):
        return frames_mode([float(x) for x in MODE.split(":")[1].split(",")])
    if MODE.startswith("preview"):
        _, ss, du = MODE.split(":"); ss = float(ss); du = float(du)
    else: ss, du = 0.0, TOTAL
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(ss), "-i", SRC, "-vf", "fps=30", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    vout = f"{V3}/v6_video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
    fb = SW * SH * 3; n = 0; last = None; nframes = int(round(du * FPS))
    while n < nframes:
        t = ss + n / FPS; idx = min(int(round(t * 30)), NSRC - 1)
        raw = dec.stdout.read(fb) if t < SRC_DUR else b""
        if len(raw) == fb: last = np.frombuffer(raw, np.uint8).reshape(SH, SW, 3).copy()
        if t < END_IN + 0.35:
            frame, L = speaker_and_bg(last, idx, t)
            draw_panels(frame, t)
            draw_caption(frame, t, lerp(1450, 1585, clamp(L)))
            draw_banners(frame, t)
        if t >= END_IN:
            ec = end_card(t); a = clamp((t - END_IN) / 0.35)
            if a < 1: frame.alpha_composite(fade(ec, a))
            else: frame = ec
        enc.stdin.write(frame.convert("RGB").tobytes()); n += 1
        if n % 150 == 0: print(f"{t:.1f}s", flush=True)
    enc.stdin.close(); enc.wait(); dec.kill()
    ev = []
    WHS = sfx.whoosh(0.5); T = sfx.thud(); P = sfx.paper(0.2)
    _tb = np.arange(int(0.09 * 48000)) / 48000; _b = np.sin(2 * np.pi * 1650 * _tb) * np.exp(-_tb * 45); BLIP = np.stack([_b, _b], 1)
    for a, b, fn in PANELS:
        ev += [(a - 0.2, WHS, 0.22)]
    for a, b in PIP_RANGES:
        ev += [(a - 0.1, sfx.whoosh(0.45), 0.22), (b - 0.1, sfx.whoosh(0.45), 0.22)]
    for ts, _, _ in TIMELINE: ev.append((ts + 0.05, BLIP, 0.18))
    ev += [(HL6[0], sfx.marker(0.7), 0.08), (STAMP6 + 0.08, T, 0.30)]
    ev += [(BAN_IN - 0.1, sfx.whoosh(0.6), 0.25), (0.0, sfx.whoosh(0.7), 0.30)]
    _n = int(2.0 * 48000); _tt = np.arange(_n) / 48000
    _f = 180 * (2 ** (_tt / 2.0 * 2.6)); _ph = 2 * np.pi * np.cumsum(_f) / 48000
    _nz = np.random.default_rng(9).normal(0, 1, _n); _nz = _nz - np.convolve(_nz, np.ones(24) / 24, "same")
    _env = (_tt / 2.0) ** 2.2
    _r = (0.55 * np.sin(_ph) + 0.25 * np.sin(_ph * 1.5) + 0.35 * _nz * (_tt / 2.0)) * _env
    RISER = np.stack([_r, _r], 1) / (np.abs(_r).max() + 1e-9)
    ev += [(END_IN - 2.0, RISER, 0.30), (END_IN - 0.35, sfx.whoosh(0.7), 0.42), (END_IN + 0.12, T, 0.50)]
    ev = [(a - ss, b, c) for a, b, c in ev if 0 <= a - ss < du - 0.9]
    sfx.build(ev, du, f"{V3}/v6_sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-ss", str(ss), "-i", f"{V3}/vox.wav", "-i", f"{V3}/v6_sfx.wav",
                    "-ss", str(ss), "-i", f"{V3}/music.wav", "-filter_complex",
                    "[1:a]apad,asplit=2[vox1][key];[2:a]volume=0.8,apad[sfx];[3:a]volume=0.30[mus];"
                    "[mus][key]sidechaincompress=threshold=0.02:ratio=5:attack=30:release=500[musd];"
                    f"[vox1][sfx][musd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{du:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-movflags", "+faststart", OUTFILE], check=True)
    print("done", n)

main()
