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

SRC = "/root/.claude/uploads/698dd744-d40f-5d96-b9e9-72023ae79dbf/a76ce673-VID-20261010-WA0019.mp4"
UP = "/root/.claude/uploads/698dd744-d40f-5d96-b9e9-72023ae79dbf"
V3 = f"{S}/v3"; FD = str(KIT / "assets" / "fonts")
W, H, FPS = 1080, 1920, 30
SW, SH = 478, 850
NSRC = 1698
SRC_DUR = 56.6
END_IN = 56.30
TOTAL = 59.40

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
segs = json.load(open(f"{V3}/segs.json"))
TXT = {0: "MAS ELIAS", 1: "EU NEM SABIA QUE VOCÊ VOTAVA NO PT", 2: "EU NÃO SÓ VOTO NO PT",
       3: "SABE O QUE QUE EU SOU", 4: "EU VOU LER UMA LISTINHA AQUI",
       5: "PORQUE É TANTA COISA QUE EU NÃO CONSIGO DECORAR", 6: "EU SOU BOLSA FAMÍLIA",
       7: "SOU NOVO PAC", 8: "SOU FARMÁCIA POPULAR", 9: "SOU PÉ-DE-MEIA", 10: "SOU LUZ PARA TODOS",
       11: "EU SOU A TRANSPOSIÇÃO DO RIO SÃO FRANCISCO",
       12: "QUE INCLUSIVE RECENTEMENTE EU TIVE A OPORTUNIDADE", 13: "DE IR DE CARRO PRO NORDESTE",
       14: "PASSAR NO SERTÃO E VER AONDE NÃO CHEGAVA UMA GOTA D'ÁGUA", 15: "QUE AGORA CHEGA",
       17: "AS PLANTAÇÕES CRESCEM", 19: "AS PLANTAS ESTÃO VERDINHAS LÁ",
       21: "INCLUSIVE SE VOCÊ TIVER A OPORTUNIDADE", 23: "PRINCIPALMENTE VOCÊ QUE É NORDESTINO",
       24: "DÁ UM PULINHO LÁ PRA VOCÊ VER COMO MUDOU AS COISAS LÁ, TÁ", 25: "E NÃO VEM COM",
       26: "ESSA CONVERSA DE QUE SÃO PAULO SUSTENTA O BRASIL", 27: "SÃO PAULO É A LOCOMOTIVA DO BRASIL",
       28: "PORQUE SÃO PAULO", 29: "ELE FOI CONSTRUÍDO PELO POVO DO NORDESTE",
       30: "POVO QUE MIGROU PRA CÁ", 31: "O POVO TRABALHADOR", 32: "ENTÃO DIA 25",
       34: "É TREZE NA CABEÇA"}
caps = []
for i, txt in sorted(TXT.items()):
    s = segs[i]; st = s["start"] / 30; en = s["end"] / 30
    words = txt.split()
    nchunk = max(1, math.ceil(len(words) / 5))
    per = math.ceil(len(words) / nchunk)
    chunks = [words[k:k + per] for k in range(0, len(words), per)]
    tot = sum(len(w) + 2 for w in words); acc = 0
    for ch in chunks:
        cs = st + (en - st) * acc / tot
        ts = []
        for w in ch:
            ts.append(st + (en - st - 0.1) * acc / tot); acc += len(w) + 2
        caps.append(dict(words=ch, ts=ts, start=cs, end=st + (en - st) * acc / tot))
LIST_CAPS = [("EU SOU BOLSA FAMÍLIA", 8.30, 9.45), ("SOU MINHA CASA", 9.65, 10.25), ("MINHA VIDA", 10.25, 10.65),
             ("SOU NOVO PAC", 10.70, 11.50), ("SOU FARMÁCIA POPULAR", 11.65, 12.45), ("SOU PÉ-DE-MEIA", 12.50, 13.25),
             ("SOU ACREDITA", 13.30, 14.02), ("SOU LUZ PARA TODOS", 14.08, 14.95)]
caps = [c for c in caps if not (7.75 <= c["start"] < 14.97)]
for txt, st, en in LIST_CAPS:
    ws = txt.split(); tot = sum(len(w) + 2 for w in ws); acc = 0; ts = []
    for w in ws: ts.append(st + (en - st - 0.15) * acc / tot); acc += len(w) + 2
    caps.append(dict(words=ws, ts=ts, start=st, end=en))
caps.sort(key=lambda c: c["start"])
for a, b in zip(caps, caps[1:]):
    a["end"] = min(max(a["end"], a["end"] + 0.15), b["start"])
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
PIP_RANGES = [(7.55, 31.0), (40.45, 51.75)]
TR = 0.70
def ease_io(x): x = clamp(x); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
def pip_amount(t):
    k = 0.0
    for a, b in PIP_RANGES:
        k = max(k, ease_io((t - a) / TR) * (1 - ease_io((t - b) / TR)))
    return k
WIN = (154, 798, 926, 1680)          # speaker window: whole head + shoulders, nothing cropped
SC_PIP = 1.615
FACE = (239.0, 392.0); HEAD_TOP = 190.0
ZK = [(0, 1.00), (2.40, 1.06), (4.53, 1.00), (33.30, 1.05), (39.37, 1.00), (51.70, 1.04), (54.90, 1.07)]
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
cleaner = Cleaner(f"{V3}/masks.npy")

def speaker_and_bg(src, idx, t):
    L = pip_amount(t)
    img = cleaner.clean(src, idx)
    sc = lerp(W / SW * zoom_at(t), SC_PIP, L)
    fx, fy = FACE
    px = W / 2
    py = lerp(fy * W / SW, WIN[1] + 125 + (fy - HEAD_TOP) * SC_PIP, L)
    M = np.float32([[sc, 0, px - fx * sc], [0, sc, py - fy * sc]])
    sp = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    sp = cv2.LUT(sp, LUT).astype(np.float32)
    sp += cv2.resize(GRAIN[idx % 6], (W, H))[..., None]
    if L < 0.001:
        return Image.fromarray(np.clip(sp * VIG, 0, 255).astype(np.uint8)).convert("RGBA"), L
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
    elif kind == "house":
        d.line((20, 100, m, 22), fill=c, width=w); d.line((m, 22, s - 20, 100), fill=c, width=w)
        d.rectangle((42, 96, s - 42, s - 24), outline=c, width=w); d.rectangle((m - 22, 130, m + 22, s - 24), outline=c, width=w)
    elif kind == "coin":
        d.ellipse((24, 24, s - 24, s - 24), outline=c, width=w)
        d.line((m, 52, m, s - 52), fill=c, width=w); d.arc((m - 34, 66, m + 34, 118), 90, 330, fill=c, width=w)
        d.arc((m - 34, 106, m + 34, 158), 270, 150, fill=c, width=w)
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

LIST = [("BOLSA FAMÍLIA", 8.30, "family", ("R$ ", 600, 0, ""), "VALOR MÍNIMO POR FAMÍLIA"),
        ("MINHA CASA MINHA VIDA", 9.65, "house", ("+", 2, 0, " MILHÕES"), "DE MORADIAS CONTRATADAS"),
        ("NOVO PAC", 10.70, "crane", ("R$ ", 1.7, 1, " TRI"), "PREVISTOS EM INVESTIMENTOS"),
        ("FARMÁCIA POPULAR", 11.65, "pill", ("", 41, 0, " ITENS"), "100% GRATUITOS"),
        ("PÉ-DE-MEIA", 12.50, "cap", ("ENSINO MÉDIO", None, 0, ""), "INCENTIVO PARA O ALUNO CONCLUIR"),
        ("ACREDITA", 13.30, "coin", ("CRÉDITO", None, 0, ""), "PARA QUEM EMPREENDE"),
        ("LUZ PARA TODOS", 14.08, "bulb", ("+", 17, 0, " MI"), "DE PESSOAS ATENDIDAS")]
ICO = {k: line_icon(k, 40) for k in ["family", "house", "crane", "pill", "cap", "coin", "bulb"]}
ICO_BIG = {k: line_icon(k, 64) for k in ["drop", "leaf", "sun"]}
ICO_DIM = {k: line_icon(k, 64, (150, 140, 120)) for k in ["sun"]}

def panel_list(t, t0):
    u = t - t0; p = panel_base(); d = ImageDraw.Draw(p)
    label(p, "A LISTINHA", u)
    act = max([i for i, it in enumerate(LIST) if it[1] <= t] or [0])
    F_I2 = MF("Bold", 24); colw = (PW - 88 - 20) // 2
    for i, (name, ts, ic, num, sub) in enumerate(LIST):
        col, row = (0, i) if i < 4 else (1, i - 4)
        x = 44 + col * (colw + 20); y = 84 + row * 64
        k = (t - ts) / 0.45
        if k <= 0: continue
        if i == act:
            ka = ease_out(k)
            d.rounded_rectangle((x - 10, y - 8, x + colw, y + 48), 10, fill=GOLD + (int(28 * ka),))
            d.rectangle((x - 10, y - 8, x - 7, y + 48), fill=GOLD + (int(255 * ka),))
        put(p, ICO[ic], x + 4, y, k, dy=0)
        put(p, timg(name, F_I2, WH if i == act else DIM), x + 56, y + 6, k, dy=12)
        ck = clamp((t - ts - 0.25) / 0.3)
        if ck > 0:
            cx, cy = x + colw - 20, y + 20
            pts = [(cx - 11, cy), (cx - 3, cy + 8), (cx + 13, cy - 10)]
            seg = [pts[0], (lerp(pts[0][0], pts[1][0], min(1, ck / 0.4)), lerp(pts[0][1], pts[1][1], min(1, ck / 0.4)))]
            if ck > 0.4: seg = [pts[0], pts[1], (lerp(pts[1][0], pts[2][0], (ck - 0.4) / 0.6), lerp(pts[1][1], pts[2][1], (ck - 0.4) / 0.6))]
            d.line(seg, fill=GD, width=4, joint="curve")
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

PANELS = [(7.62, 14.97, panel_list), (14.97, 22.50, panel_river), (22.50, 30.95, panel_sertao), (40.52, 51.70, panel_sp)]
_psh = Image.new("RGBA", (PW + 80, PH + 80), (0, 0, 0, 0))
_m = Image.new("L", (PW + 80, PH + 80), 0); ImageDraw.Draw(_m).rounded_rectangle((40, 54, 40 + PW, 54 + PH), 26, fill=130)
_psh.putalpha(_m.filter(ImageFilter.GaussianBlur(20)))
def draw_panels(frame, t):
    for a, b, fn in PANELS:
        if not (a - 0.01 <= t < b + 0.45): continue
        chained_in = any(abs(a - b2) < 0.05 for _, b2, _ in PANELS)
        chained_out = any(abs(b - a2) < 0.05 for a2, _, _ in PANELS)
        if chained_out and t >= b + 0.36: continue   # stays underneath while the next one fades in
        p = fn(min(t, b), a)
        kin = ease_out((t - a) / (0.35 if chained_in else 0.6))
        kout = ease_in((t - b) / 0.4) if t > b and not chained_out else 0
        al = kin * (1 - kout)
        dy = int(30 * (1 - kin) - 20 * kout)
        frame.alpha_composite(fade(_psh, al), (PX0 - 40, PY0 - 40 + dy))
        frame.alpha_composite(fade(p, al), (PX0, PY0 + dy))

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
        idx = min(int(round(t * FPS)), NSRC - 1)
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
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(ss), "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    vout = f"{V3}/video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                            "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
    fb = SW * SH * 3; n = 0; last = None; nframes = int(round(du * FPS))
    while n < nframes:
        t = ss + n / FPS; idx = min(int(round(t * FPS)), NSRC - 1)
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
    for it in LIST: ev.append((it[1] + 0.25, BLIP, 0.22))
    ev += [(25.6, sfx.whoosh(1.2), 0.14), (50.47, T, 0.22), (44.6, P, 0.25)]
    for tk, zk in ZK:
        if zk >= 1.30: ev.append((tk - 0.12, sfx.whoosh(0.25), 0.15))
    ev += [(BAN_IN - 0.1, sfx.whoosh(0.6), 0.25), (END_IN - 0.5, sfx.whoosh(0.8), 0.35), (END_IN + 0.15, T, 0.45)]
    ev = [(a - ss, b, c) for a, b, c in ev if 0 <= a - ss < du - 1.3]
    sfx.build(ev, du, f"{V3}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-ss", str(ss), "-i", f"{V3}/vox.wav", "-i", f"{V3}/sfx.wav",
                    "-ss", str(ss), "-i", f"{V3}/music.wav", "-filter_complex",
                    "[1:a]apad,asplit=2[vox1][key];[2:a]volume=0.8,apad[sfx];[3:a]volume=0.30[mus];"
                    "[mus][key]sidechaincompress=threshold=0.02:ratio=5:attack=30:release=500[musd];"
                    f"[vox1][sfx][musd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{du:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-movflags", "+faststart", OUTFILE], check=True)
    print("done", n)

main()
