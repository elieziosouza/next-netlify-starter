"""React viral: Flávio 'usuário master' de conta de offshore sócia do jato ligado a Vorcaro (PF, revelado pelo O Globo em 14/10/2026).
Ele em tela cheia com palavra gigante atrás; vídeo do Pannunzio em cartão 3D com palavra grande em cima; final com a batida própria + VAI DAR PT."""
import sys, math, subprocess, json, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.path.insert(0, f"{S}/work")
import sfx
from minitop import make_minitop, make_minifooter, handles_row
from segment_person import PersonSeg
V = f"{S}/v19"; FD = f"{S}/fontdl"
SRCS = {"me": f"{V}/me.mp4", "cl": f"{V}/cl.mp4"}; DIMS = {"me": (1080, 1920), "cl": (576, 1024)}
W, H, FPS = 1080, 1920, 30
WHITE = (255, 255, 255); GOLD = (214, 182, 116); GOLD_L = (245, 226, 176); NAVY = (6, 34, 58); RED = (200, 38, 38)
WH = (255, 255, 255, 255); GD = GOLD + (255,)
EDL = [("me", 2.75, 9.25), ("cl", 0.18, 6.25), ("cl", 10.20, 32.55), ("cl", 35.00, 38.85), ("me", 10.10, 12.10), ("me", 13.05, 16.70)]
segs = []; acc = 0.0
for src, a, b in EDL:
    segs.append(dict(src=src, a=a, b=b, t0=acc, t1=acc + (b - a))); acc += b - a
FIN_IN = acc
MUS_IN = segs[-1]["t0"]                      # música original entra baixinho no "dia 25"
LYR = [(0.0, 1.43, "ESSE ANO"), (1.43, 2.87, "O LULA BOTA"), (2.87, 3.87, "O BOLSONARO"), (3.87, 4.87, "PRA MAMAR"),
       (4.87, 5.73, "VAI DAR PT"), (5.73, 6.73, "VAI DAR"), (6.73, 8.23, "VAI DAR PT"), (8.23, 9.43, "VAI DAR PT")]
FIN_LEN = 9.45 - (FIN_IN - MUS_IN); EDIT_END = FIN_IN + FIN_LEN; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
CL_IN = segs[1]["t0"]; CL_OUT = segs[3]["t1"]
def seg_at(t):
    for s in segs:
        if s["t0"] <= t < s["t1"]: return s
    return None
def out_t(src, x):
    for s in segs:
        if s["src"] == src and s["a"] <= x <= s["b"]: return s["t0"] + x - s["a"]
    raise ValueError((src, x))
ME_CAPS = [("PARECE QUE O HOMEM TINHA SOCIEDADE NO JATINHO ALI", 2.81, 5.70), ("ERA LIGADO A UMA CONTA MASTER LÁ NA OFFSHORE", 5.75, 9.20),
           ("CUIDADO, A CASA TÁ CAINDO", 10.14, 12.05), ("E DIA 25", 13.08, 14.38), ("VAI SER HISTÓRICO", 15.60, 16.62)]
CL_CAPS = [("FLÁVIO ERA USUÁRIO MASTER DE UMA CONTA DE OFFSHORE", 0.18, 3.53), ("SÓCIA DAQUELE JATO EM QUE ELE VOLTOU", 3.77, 6.18),
           ("ELE DISSE: “AH, MAS O JATO É DO MEU AMIGO, DO ADVOGADO WILLER TOMAZ”", 10.20, 13.60), ("AGORA SE DESCOBRE QUE ELE, BOLSONARO,", 13.65, 16.30),
           ("ESTAVA LÁ PENDURADO NA CONTA CORRENTE DESSA EMPRESA", 16.44, 18.79), ("POR CAUSA DE E-MAILS ENCONTRADOS NA CORRESPONDÊNCIA ENTRE WILLER TOMAZ", 18.97, 22.91),
           ("E O BANCO SANTANDER, ONDE FICAVA A CONTA DESSA EMPRESA", 23.06, 25.70), ("QUE É DONA DESSA FRAÇÃO DO AVIÃO", 25.75, 27.74),
           ("PELO QUE O JORNAL O GLOBO TÁ DIZENDO", 28.28, 30.20), ("O FLÁVIO BOLSONARO ERA DONO DAQUELE AVIÃO", 30.25, 32.51),
           ("E OUTRA COISA: QUEM É QUE ERA DONO DA OUTRA COTA DESSE AVIÃO?", 35.02, 37.60), ("DANIEL VORCARO", 37.65, 38.75)]
HOT = {"OFFSHORE", "CAINDO", "25", "HISTÓRICO", "MASTER", "VORCARO"}
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
        hot = c["src"] in ("au", "auc") and c["words"][act].strip(",.?!:“”") in HOT
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




CAPS = build_caps(ME_CAPS, "me", 4, "me") + build_caps(CL_CAPS, "cl", 4, "cl")
CAPS.sort(key=lambda c: c["start"])
for c in CAPS:
    hot = any(w.strip(",.?!:“”") in HOT for w in c["words"]); c["src"] = ("au" if hot else "me") if c["src"] == "me" else ("auc" if hot else "cl")
    c["hotc"] = hot
SEG = PersonSeg(f"{S}/seg/u2net_human_seg.onnx")

# palavras grandes: (fonte, início, fim na fonte, palavra, linha de apoio, modo) — modo "atras" = atrás dele; "cima" = em cima do cartão
BIG = [("me", 7.70, 9.25, "OFFSHORE", "", "atras"),
       ("cl", 0.18, 3.60, "USUÁRIO MASTER", "segundo relatório da PF · O Globo, 14/10", "cima"),
       ("cl", 36.90, 38.85, "VORCARO", "outra cota do jato ligada à Prime You, de quem foi sócio", "cima"),
       ("me", 10.90, 12.10, "CAINDO", "", "atras"), ("me", 13.05, 15.40, "DIA 25", "", "atras")]
_txt = {}
def word_layer(word, col, size, sub=""):
    key = (word, size, sub)
    if key not in _txt:
        f = MF("ExtraBold", size); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
        while d0.textlength(word, font=f) > W - 60: size -= 6; f = MF("ExtraBold", size)
        hh = int(size * 1.35) + (60 if sub else 0)
        lay = Image.new("RGBA", (W, hh), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.text((W / 2, size * 0.68), word, font=f, fill=col + (255,), anchor="mm")
        if sub: d.text((W / 2, size * 1.35 + 18), sub, font=MF("SemiBold", 30), fill=(235, 238, 244, 255), anchor="mm")
        sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); blk = Image.new("RGBA", lay.size, (0, 0, 0, 255)); blk.putalpha(lay.getchannel("A").point(lambda v: int(v * 0.6)))
        sh.alpha_composite(blk.filter(ImageFilter.GaussianBlur(14)), (0, 8)); sh.alpha_composite(lay)
        _txt[key] = np.asarray(sh, np.float32) / 255
    return _txt[key]

def big_words(img, src_img, t, s, mode):
    st = s["a"] + (t - s["t0"])
    for src, a, b, word, sub, md in BIG:
        if src != s["src"] or md != mode or not (a <= st < b): continue
        u = st - a; k = back_out(u / 0.35, 1.6); al = clamp(u / 0.12) * clamp((b - st) / 0.25)
        lay = word_layer(word, GOLD_L if word != "CAINDO" else WHITE, 200 if md == "atras" else 150, sub)
        sc = 0.75 + 0.25 * k; lh, lw = lay.shape[:2]
        lay = cv2.resize(lay, (int(lw * sc), int(lh * sc)), interpolation=cv2.INTER_LINEAR)
        cy = 215 if md == "atras" else 268
        if md == "atras":
            m = cv2.resize(SEG(cv2.resize(src_img, (478, 850), interpolation=cv2.INTER_AREA)), (W, H)); m = np.clip((m - 0.35) / 0.3, 0, 1)
        else: m = np.zeros((H, W), np.float32)
        y0 = int(cy - lay.shape[0] / 2); x0 = int(W / 2 - lay.shape[1] / 2)
        ya, yb = max(0, y0), min(H, y0 + lay.shape[0]); xa, xb = max(0, x0), min(W, x0 + lay.shape[1])
        L = lay[ya - y0:yb - y0, xa - x0:xb - x0]; A = L[..., 3:4] * al * (1 - m[ya:yb, xa:xb, None])
        img[ya:yb, xa:xb] = np.clip(img[ya:yb, xa:xb].astype(np.float32) * (1 - A) + L[..., :3] * 255 * A, 0, 255).astype(np.uint8)
    return img

_cache = {}
def frames_of(s):
    key = (s["src"], s["a"])
    if key not in _cache:
        if len(_cache) > 2: _cache.clear()
        w, h = DIMS[s["src"]]; _cache[key] = decode(SRCS[s["src"]], s["a"], s["b"], w, h)
    return _cache[key]
def src_frame(s, tt):
    fr = frames_of(s); return fr[min(len(fr) - 1, int((tt - s["t0"]) * FPS))]

CARD_W, CARD_H = 720, 1280; CARD_X, CARD_Y = (W - CARD_W) // 2, 398
def card_img(img, tilt):
    c = cv2.resize(img, (CARD_W, CARD_H), interpolation=cv2.INTER_AREA)
    m = Image.new("L", (CARD_W, CARD_H), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, CARD_W - 1, CARD_H - 1), 26, fill=255)
    im = Image.fromarray(c).convert("RGBA"); im.putalpha(m)
    ImageDraw.Draw(im).rounded_rectangle((1, 1, CARD_W - 2, CARD_H - 2), 26, outline=GOLD + (235,), width=3)
    if tilt > 0.003: return Image.fromarray(persp(np.asarray(im), "top", 0.02 + 0.3 * tilt), "RGBA")
    return im

def outro_chip(frame, t, t0, t1):
    if not (t0 <= t < t1): return
    q = t - t0; k = ease_out(q / 0.45); ko = ease_in((t - (t1 - 0.3)) / 0.3)
    lay = Image.new("RGBA", (860, 104), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, 859, 103), 22, fill=(5, 16, 30, 240), outline=GD, width=2)
    d.rounded_rectangle((16, 16, 196, 56), 12, fill=GD); d.text((106, 36), "OUTRO LADO", font=MF("ExtraBold", 23), fill=NAVY + (255,), anchor="mm")
    d.text((212, 36), "Flávio nega ter conta com Willer Tomaz", font=MF("Bold", 27), fill=WH, anchor="lm")
    d.text((22, 80), "A PF trata como hipótese de participação de fato", font=MF("SemiBold", 23), fill=GOLD_L + (255,), anchor="lm")
    paste(frame, fade(lay, k * (1 - ko)), W / 2 - 430, 1612 + 40 * (1 - k), 0.5, 14, (5, 12))

def vai_dar_pt(frame, t):
    u = t - FIN_IN
    if u < 0: return
    beat = 60 / 130; k = back_out(u / 0.22, 2.0); pulse = 1 + 0.04 * max(0, 1 - (u % beat) / 0.18)
    g = Image.new("RGBA", (W, 640), (0, 0, 0, 0)); ImageDraw.Draw(g).rectangle((0, 0, W, 640), fill=(4, 10, 20, 255))
    g.putalpha(Image.linear_gradient("L").resize((W, 640)).point(lambda v: int(v * 0.7 * clamp(u / 0.3)))); frame.alpha_composite(g, (0, H - 640))
    f = MF("ExtraBold", 118); lay = Image.new("RGBA", (W, 220), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    pre = "VAI DAR "; wp = d.textlength(pre, font=f); wt = d.textlength("PT", font=f); x0 = W / 2 - (wp + wt + 30) / 2
    d.text((x0, 110), pre, font=f, fill=WH, anchor="lm")
    d.rounded_rectangle((x0 + wp + 2, 36, x0 + wp + wt + 34, 186), 20, fill=RED + (255,)); d.text((x0 + wp + 18, 110), "PT", font=f, fill=WH, anchor="lm")
    sc = (0.7 + 0.3 * k) * pulse; lay = lay.resize((int(W * sc), int(220 * sc)), Image.BICUBIC)
    blk = Image.new("RGBA", lay.size, (0, 0, 0, 255)); blk.putalpha(lay.getchannel("A").point(lambda v: int(v * 0.6)))
    frame.alpha_composite(blk.filter(ImageFilter.GaussianBlur(10)), (int(W / 2 - lay.width / 2) + 4, 1620 - lay.height // 2 + 8))
    frame.alpha_composite(lay, (int(W / 2 - lay.width / 2), 1620 - lay.height // 2))

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

def me_fin_frame(tt):
    """final: ele segura o L (vai e volta no fim da fala)"""
    u = (tt - FIN_IN) * 0.8; L0, L1 = 15.70, 16.68; Lq = L1 - L0; p = u % (2 * Lq); a = L1 - p if p < Lq else L0 + (p - Lq)
    s = segs[-1]; return frames_of(s)[min(len(frames_of(s)) - 1, int((a - s["a"]) * FPS))]

def render_frame(t):
    if t >= END_IN + 0.35: return end_card(t)
    tt = min(t, EDIT_END - 1e-3); s = seg_at(tt)
    if s is None:                                               # final com a batida
        img = me_fin_frame(tt).copy(); frame = Image.fromarray(img).convert("RGBA"); lyrics(frame, t)
    elif s["src"] == "me":
        src = src_frame(s, tt); img = big_words(src.copy(), src, tt, s, "atras")
        # entrada depois do cartão: leve desfoque
        q = tt - CL_OUT
        if 0 <= q < 0.18: img = cv2.GaussianBlur(img, (0, 0), 1 + 8 * (1 - q / 0.18))
        frame = Image.fromarray(img).convert("RGBA")
        draw_caption(frame, t, 1450, 56, ("me", "au"))
    else:
        src = src_frame(s, tt)
        sm = cv2.GaussianBlur(cv2.resize(src, (96, 170)), (0, 0), 3); bg = cv2.resize(sm, (W, H)).astype(np.float32) * 0.26 + np.array([2, 6, 12], np.float32)
        # transição: ele (último quadro) escurece e o cartão sobe de baixo
        kin = ease_out((tt - CL_IN) / 0.55); kout = ease_in((tt - (CL_OUT - 0.4)) / 0.4)
        if tt - CL_IN < 0.55:
            last = src_frame(segs[0], segs[0]["t1"] - 1e-3).astype(np.float32); bg = last * (1 - kin) + bg * kin
        img = np.clip(bg, 0, 255).astype(np.uint8); img = big_words(img, src, tt, s, "cima")
        frame = Image.fromarray(img).convert("RGBA")
        c = card_img(src, clamp(1 - kin + kout)); dy = 1300 * (1 - kin) + 1300 * kout
        vy = (1300 * (1 - ease_out((tt - 1 / FPS - CL_IN) / 0.55))) - 1300 * (1 - kin)
        paste(frame, c, CARD_X, CARD_Y + dy, 0.6, 22, (10, 26), (0, -vy))
        al = clamp((tt - CL_IN) / 0.5) * clamp((CL_OUT - 0.4 - tt) / 0.3)
        credit(frame, "Reprodução: Fábio Pannunzio", W / 2, CARD_Y + CARD_H + 14 + dy, al, "mm")
        draw_caption(frame, t, 1470, 46, ("cl", "auc"))
        outro_chip(frame, t, out_t("cl", 35.4), CL_OUT - 0.05)
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
        print("TOTAL", TOTAL, "FIN", FIN_IN, [(s["src"], round(s["t0"], 2), round(s["t1"], 2)) for s in segs]); return
    vout = f"{V}/video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
    for i in range(int(round(TOTAL * FPS))):
        enc.stdin.write(finish(render_frame(i / FPS), i / FPS).tobytes())
        if i % 300 == 0: print(f"{i / FPS:.0f}s", flush=True)
    enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR); srcw = {}
    for k, f in SRCS.items():
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f, "-ar", "48000", "-ac", "2", "-f", "wav", f"{V}/{k}_48.wav"], check=True); srcw[k] = readw(f"{V}/{k}_48.wav")
    vt = np.zeros((n, 2), np.float32)
    for s in segs:
        p = srcw[s["src"]][int(s["a"] * SR):int(s["b"] * SR)].copy() * (1.0 if s["src"] == "me" else 1.1); f = int(0.03 * SR)
        env = np.ones(len(p)); env[:f] = np.linspace(0, 1, f); env[-f:] = np.linspace(1, 0, f)
        t0 = int(s["t0"] * SR); vt[t0:t0 + len(p)] += p * env[:, None]
    writew(f"{V}/voice.wav", vt)
    # batida própria: entra baixinho no "dia 25" e a virada cai no fim da fala
    lead = FIN_IN - MUS_IN
    song = readw(f"{S}/v15/song_vox.wav")
    L = min(len(song), n - int(MUS_IN * SR)); tl = np.arange(L) / SR
    gain = np.where(tl < lead, 10 ** ((-22 + 22 * tl / lead) / 20), 1.0) * np.clip(1 - (tl - (TOTAL - MUS_IN - 1.6)) / 1.5, 0, 1)
    st = np.zeros((n, 2), np.float32); st[int(MUS_IN * SR):int(MUS_IN * SR) + L] = song[:L] * gain[:, None]; writew(f"{V}/song.wav", st)
    subprocess.run([sys.executable, f"{S}/work/music.py", f"{V}/bed.wav", f"{TOTAL + 0.5:.2f}"], check=True)
    bed = readw(f"{V}/bed.wav")[:n]; bed = np.pad(bed, ((0, max(0, n - len(bed))), (0, 0)))[:n]
    gate = np.ones(n, np.float32); gate[int((MUS_IN - 0.5) * SR):] = 0; gate = np.convolve(gate, np.ones(int(0.5 * SR)) / int(0.5 * SR), "same")
    writew(f"{V}/bed_g.wav", bed * gate[:, None])
    ev = [(0.3, sfx.whoosh(0.6), 0.2), (CL_IN - 0.15, sfx.whoosh(0.5), 0.28), (CL_OUT - 0.35, sfx.whoosh(0.5, False), 0.24)]
    for src, a, b, word, sub, md in BIG: ev.append((out_t(src, a) + 0.02, sfx.click(), 0.55))
    ev.append((END_IN - 0.3, sfx.whoosh(0.6), 0.25))
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/bed_g.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=70,asplit=3[vox][k1][k2];[2:a]volume=0.8[sf];[3:a]volume=0.26[bed];[4:a]volume=0.9[sg];"
                    "[bed][k1]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=500[bedd];"
                    "[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][bedd][sgd]amix=inputs=4:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
