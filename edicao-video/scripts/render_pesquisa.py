"""Pesquisa PoderData/Aya 13/10: Eliezio + matéria do UOL News + gráfico animado de 2º turno."""
import sys, math, subprocess, json, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.path.insert(0, f"{S}/work")
import sfx, grading
from minitop import make_minitop, make_minifooter, handles_row
GRADE = grading.Fast(grading.cinema, f"{S}/grade/lut_cinema.npy", 0.08, 6)     # só na matéria

V = f"{S}/v12"; FD = f"{S}/fontdl"
ME, CL = f"{V}/a.mp4", f"{V}/p.mp4"            # a.mp4 = exportação do CapCut com o filtro dele
W, H, FPS = 1080, 1920, 30
WHITE = (255, 255, 255); GOLD = (214, 182, 116); GOLD_L = (245, 226, 176); NAVY = (6, 34, 58); RED = (200, 38, 38)
STEEL = (150, 172, 196)
WH = (255, 255, 255, 255); GD = GOLD + (255,)
HOT = set()

# (fonte, a, b): me = ele (1080x1920), cl = matéria
EDL = [("me", 1.30, 3.98), ("me", 6.62, 7.95), ("cl", 0.00, 48.75), ("me", 4.10, 6.70), ("me", 8.30, 10.00)]
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
CL_IN = out_t("cl", 0.0); CL_OUT = CL_IN + 48.75
def ct_of(t): return t - CL_IN

ME_CAPS = [("DEPOIS NÃO DIZ QUE EU NÃO AVISEI, HEIN?", 1.56, 3.88), ("DIA 25 VAI SER HISTÓRICO", 4.28, 6.54),
           ("DÁ UMA OLHADINHA AÍ", 6.81, 7.82), ("ME DIZ O QUE VOCÊ ACHA?", 8.44, 9.80)]
AN_CAPS = [("ACABA DE SAIR UMA NOVA PESQUISA", 2.70, 3.2), ("TÁ TODO MUNDO PERGUNTANDO, TEM GENTE NO CHAT FALANDO DISSO", 3.2, 6.68),
           ("PESQUISA PODERDATA/AYA QUE SAIU AGORA HÁ POUCO", 7.06, 11.0), ("E MOSTRA QUE A DIFERENÇA ENTRE ELES", 11.0, 14.36),
           ("CAIU DE 6 PARA 2 PONTOS PERCENTUAIS", 14.68, 18.63),
           ("O SENADOR FLÁVIO BOLSONARO TEM 51% DAS INTENÇÕES DE VOTO NO SEGUNDO TURNO", 18.74, 24.49),
           ("E O PRESIDENTE LULA, 49%", 24.70, 27.6), ("SEGUNDO ESSA PESQUISA, DIVULGADA AGORA PELA MANHÃ", 27.6, 31.78),
           ("HOJE, TERÇA-FEIRA, 13 DE OUTUBRO, OS CANDIDATOS ESTÃO TECNICAMENTE EMPATADOS", 31.93, 36.92),
           ("A MARGEM DE ERRO DESSA PESQUISA É DE 1,8 PONTO PERCENTUAL", 37.02, 40.60),
           ("NA RODADA ANTERIOR, PUBLICADA NO DIA 8 DE OUTUBRO", 40.82, 44.38), ("FLÁVIO TINHA 53% E LULA, 47%", 44.57, 48.60)]
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


CAPS = build_caps(ME_CAPS, "me", 5, "me") + build_caps(AN_CAPS, "cl", 6, "an")
top, TOPH = make_minitop(W, f"{FD}/Montserrat-SemiBold.ttf")

def me_full2(img, t, z=0.0):
    """ele em 1080x1920 (já com o filtro dele): só um respiro leve, sem mexer em cor"""
    sc = 1.03 + 0.008 * math.sin(t * 0.3) + z; cx, cy = 540, 860
    M = np.float32([[sc, 0, cx - cx * sc], [0, sc, cy - cy * sc]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

# ---------------------------------------------------------------- matéria no cartão
CROP = "crop=478:424:0:0"; CW_, CH_ = 478, 424      # altura par (yuv420)
CARD_W = 900; CARD_H = int(CH_ * CARD_W / CW_); CARD_Y = 160          # 800
def portrait_circle(img, box, d):
    x0, y0, x1, y1 = box; p = cv2.resize(img[y0:y1, x0:x1], (d, d), interpolation=cv2.INTER_CUBIC)
    m = Image.new("L", (d, d), 0); ImageDraw.Draw(m).ellipse((0, 0, d - 1, d - 1), fill=255)
    im = Image.fromarray(p).convert("RGBA"); im.putalpha(m)
    ImageDraw.Draw(im).ellipse((1, 1, d - 2, d - 2), outline=GD, width=4); return im
_ref = cv2.cvtColor(cv2.imread(f"{V}/p10.png"), cv2.COLOR_BGR2RGB)
P_FL = portrait_circle(_ref, (0, 470, 190, 660), 112); P_LU = portrait_circle(_ref, (298, 466, 478, 646), 112)

PX, PY, PW, PH = 70, 990, 940, 740                # painel do gráfico
T_MOVE = 14.9                                     # "caiu de 6 para 2"
T_SLOPE = 40.9                                    # "na rodada anterior..."
def chip(d, x, y, txt, col, al, f=None):
    f = f or MF("Bold", 22); tw = d.textlength(txt, font=f)
    d.rounded_rectangle((x, y, x + tw + 36, y + 38), 19, fill=col + (int(235 * al),)); d.text((x + 18, y + 19), txt, font=f, fill=NAVY + (int(255 * al),), anchor="lm")
    return tw + 36

def bars_layer(ct):
    lay = Image.new("RGBA", (PW, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    grow = ease_out((ct - 7.6) / 1.1); move = ease_io((ct - T_MOVE) / 1.3)
    vf = lerp(53, 51, move) * grow; vl = lerp(47, 49, move) * grow
    maxw = 540; scale = maxw / 55.0; bx = 180
    # selo da rodada: ANTERIOR · 08/10 vira NOVA · 13/10 (giro 3D)
    fl = ease_io((ct - T_MOVE) / 0.5); kc = ease_out((ct - 7.6) / 0.5)
    if kc > 0:
        side = fl < 0.5; sq = abs(math.cos(math.pi * fl))
        c = Image.new("RGBA", (300, 44), (0, 0, 0, 0)); dc = ImageDraw.Draw(c)
        chip(dc, 0, 3, "ANTERIOR · 08/10" if side else "NOVA · 13/10", (200, 210, 222) if side else GOLD, kc)
        c = c.resize((300, max(1, int(44 * sq))), Image.BICUBIC); lay.alpha_composite(c, (bx, 140 + (44 - c.height) // 2))
    rows = [("FLÁVIO BOLSONARO", vf, 53, STEEL, P_FL, 18.74, 24.5, "−2"), ("LULA", vl, 47, GOLD, P_LU, 24.70, 30.7, "+2")]
    ends = []
    for i, (nm, v, prev, col, por, h0, h1, delta) in enumerate(rows):
        y = 200 + i * 168
        hl = clamp((ct - h0) / 0.3) * (1 - clamp((ct - h1) / 0.4))
        if hl > 0:
            g = Image.new("RGBA", (PW, 170), (0, 0, 0, 0)); ImageDraw.Draw(g).rounded_rectangle((24, 6, PW - 24, 164), 22, fill=col + (int(60 * hl),))
            lay.alpha_composite(g.filter(ImageFilter.GaussianBlur(8)), (0, y - 20))
        lay.alpha_composite(por, (44, y))
        d.text((bx, y + 22), nm, font=MF("Bold", 28), fill=WH, anchor="lm")
        by = y + 56; bw = int(v * scale)
        d.rounded_rectangle((bx, by, bx + maxw, by + 42), 21, fill=(255, 255, 255, 18))
        if move > 0.01:                                   # fantasma da rodada anterior
            pw_ = int(prev * scale * grow); d.rounded_rectangle((bx, by, bx + pw_, by + 42), 21, outline=(255, 255, 255, int(110 * move)), width=2)
            d.text((bx + pw_, by + 60), "08/10", font=MF("SemiBold", 17), fill=(255, 255, 255, int(150 * move)), anchor="mt")
        if bw > 4:
            d.rounded_rectangle((bx, by, bx + bw, by + 42), 21, fill=col + (255,))
            sh = clamp((ct - T_MOVE) / 1.3) * (1 - clamp((ct - T_MOVE - 1.3) / 0.4))   # brilho correndo na barra durante a mudança
            if sh > 0:
                gx = bx + int(bw * clamp((ct - T_MOVE) / 1.3)); gl = Image.new("RGBA", (PW, PH), (255, 255, 255, 0))
                ImageDraw.Draw(gl).ellipse((gx - 34, by - 4, gx + 34, by + 46), fill=(255, 255, 255, int(120 * sh)))
                m = Image.new("L", (PW, PH), 0); ImageDraw.Draw(m).rounded_rectangle((bx, by, bx + bw, by + 42), 21, fill=255)
                gl = gl.filter(ImageFilter.GaussianBlur(10)); ga = np.minimum(np.asarray(gl.getchannel("A")), np.asarray(m)); gl.putalpha(Image.fromarray(ga))
                lay.alpha_composite(gl)
        d.text((bx + maxw + 22, by + 21), f"{v:.0f}%", font=MF("ExtraBold", 54), fill=WH if i == 0 else GOLD_L + (255,), anchor="lm")
        kd = back_out((ct - T_MOVE - 1.0) / 0.4, 2.0) * (1 - clamp((ct - T_SLOPE) / 0.3))
        if kd > 0:
            f = MF("ExtraBold", int(30 * (0.6 + 0.4 * kd))); dcol = (255, 150, 150) if i == 0 else (180, 240, 190)
            d.text((bx + maxw + 24, by - 22), delta, font=f, fill=dcol + (int(255 * clamp(kd)),), anchor="lm")
        ends.append(bx + bw)
    # colchete da diferença, no nível das barras
    kb = ease_out((ct - 11.5) / 0.6)
    if kb > 0 and len(ends) == 2:
        x0, x1 = min(ends), max(ends); yb = 200 + 168 + 56 - 18
        d.line((x0, yb, x1, yb), fill=GOLD_L + (int(255 * kb),), width=3)
        for xx in (x0, x1): d.line((xx, yb - 9, xx, yb + 9), fill=GOLD_L + (int(255 * kb),), width=3)
        gap = (ends[1] - ends[0]) / scale
        d.text(((x0 + x1) / 2, yb - 14), f"{abs(lerp(6, 2, move)):.0f} pts", font=MF("ExtraBold", 24), fill=GOLD_L + (int(255 * kb),), anchor="ms")
    kd = ease_out((ct - 15.3) / 0.6)
    if kd > 0:
        gap = lerp(6, 2, move)
        d.rounded_rectangle((44, 548, 44 + 470, 612), 32, fill=(255, 255, 255, int(22 * kd)), outline=GOLD + (int(220 * kd),), width=2)
        d.text((74, 580), f"DIFERENÇA: 6 → {gap:.0f} PONTOS", font=MF("ExtraBold", 28), fill=GOLD_L + (int(255 * kd),), anchor="lm")
    return lay

def slope_layer(ct):
    """gráfico de linhas 08/10 → 13/10, desenhado na tela"""
    lay = Image.new("RGBA", (PW, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    u = ct - T_SLOPE; x0, x1 = 230, 690; ytop, ybot = 170, 560; lo, hi = 44.0, 56.0
    def Y(v): return ybot - (v - lo) / (hi - lo) * (ybot - ytop)
    ka = ease_out(u / 0.5)
    for v in (45, 50, 55):
        d.line((x0 - 40, Y(v), x1 + 40, Y(v)), fill=(255, 255, 255, int(28 * ka)), width=1)
        d.text((x0 - 52, Y(v)), f"{v}%", font=MF("SemiBold", 18), fill=(255, 255, 255, int(110 * ka)), anchor="rm")
    for x, lab, sub in ((x0, "08/10", "anterior"), (x1, "13/10", "nova")):
        d.line((x, ytop - 10, x, ybot + 10), fill=(255, 255, 255, int(50 * ka)), width=2)
        d.text((x, ybot + 34), lab, font=MF("ExtraBold", 26), fill=(255, 255, 255, int(255 * ka)), anchor="mm")
        d.text((x, ybot + 62), sub, font=MF("SemiBold", 19), fill=(255, 255, 255, int(150 * ka)), anchor="mm")
    draw = ease_io((u - 0.4) / 1.6)
    for nm, a, b, col, por in (("Flávio", 53, 51, STEEL, P_FL), ("Lula", 47, 49, GOLD, P_LU)):
        pa = (x0, Y(a)); pb = (x1, Y(b)); pe = (lerp(pa[0], pb[0], draw), lerp(pa[1], pb[1], draw))
        if ka > 0:
            d.ellipse((pa[0] - 10, pa[1] - 10, pa[0] + 10, pa[1] + 10), fill=col + (int(255 * ka),))
            d.text((pa[0] - 22, pa[1] - 2 + (-16 if nm == "Flávio" else 16)), f"{a}%", font=MF("ExtraBold", 30), fill=col + (int(255 * ka),), anchor="rm")
        if draw > 0:
            d.line((pa, pe), fill=col + (255,), width=7)
            d.ellipse((pe[0] - 10, pe[1] - 10, pe[0] + 10, pe[1] + 10), fill=col + (255,))
        if draw >= 0.999:
            kb = ease_out((u - 2.0) / 0.4)
            d.text((pb[0] + 22, pb[1] + (-16 if nm == "Flávio" else 16)), f"{b}%  {nm}", font=MF("ExtraBold", 30), fill=col + (int(255 * kb),), anchor="lm")
    kg = ease_out((u - 2.4) / 0.5)
    if kg > 0:
        for x, g in ((x0, "6 pts"), (x1, "2 pts")):
            ya_, yb_ = (Y(53), Y(47)) if x == x0 else (Y(51), Y(49))
            xx = x + (-120 if x == x0 else 0)
        d.text(((x0 + x1) / 2, ytop - 6), "DIFERENÇA: 6 → 2 PONTOS", font=MF("ExtraBold", 26), fill=GOLD_L + (int(255 * kg),), anchor="mm")
    return lay

def panel(frame, t):
    ct = ct_of(t)
    if ct < 6.6 or t > CL_OUT + 0.05: return
    kin = ease_out((ct - 6.6) / 0.7); kout = ease_in((t - (CL_OUT - 0.45)) / 0.45)
    lay = Image.new("RGBA", (PW, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, PW - 1, PH - 1), 30, fill=(5, 16, 30, 236), outline=GOLD + (200,), width=2)
    d.text((44, 52), "PODERDATA/AYA", font=MF("ExtraBold", 34), fill=GD, anchor="lm")
    d.text((44, 94), "2º turno  ·  votos válidos", font=MF("SemiBold", 24), fill=(220, 226, 236, 230), anchor="lm")
    d.rectangle((44, 124, 170, 126), fill=GD)
    sw = ease_io((ct - T_SLOPE) / 0.6)
    if sw < 1: lay.alpha_composite(fade(bars_layer(ct), 1 - sw))
    if sw > 0: lay.alpha_composite(fade(slope_layer(ct), sw))
    kf = 0.55 + 0.45 * clamp((ct - 37.0) / 0.4) * (1 - clamp((ct - 41) / 0.4))
    d = ImageDraw.Draw(lay)
    d.text((44, 668), "Margem de erro: 1,8 ponto  ·  3.000 entrevistas de 10 a 13/10", font=MF("SemiBold", 21), fill=(255, 255, 255, int(255 * kf)), anchor="lm")
    d.text((44, 700), "Registro no TSE: BR-01209/2026  ·  Fonte: PoderData/Aya", font=MF("SemiBold", 21), fill=(255, 255, 255, int(200 * kf)), anchor="lm")
    tilt = clamp((1 - kin) + kout)
    arr = persp(np.asarray(lay), "top", 0.04 + 0.3 * tilt) if tilt > 0.003 else np.asarray(lay)
    im = fade(Image.fromarray(arr, "RGBA"), clamp(kin * 1.5) * (1 - kout))
    def yy_(q): return 260 * (1 - ease_out(q / 0.7))
    dy = yy_(ct - 6.6) + 900 * kout; vy = dy - (yy_(ct - 6.6 - 1 / FPS) + 900 * kout)
    paste(frame, im, PX, PY + dy, 0.6, 24, (10, 26), (0, vy))
    # carimbo EMPATE TÉCNICO
    ks = ct - 32.9
    if ks > 0 and kout < 0.5:
        kk = back_out(ks / 0.35, 2.4); al = clamp(ks / 0.08) * (1 - kout * 2)
        f = MF("ExtraBold", 46); txt = "EMPATE TÉCNICO"
        tw = ImageDraw.Draw(Image.new("RGBA", (4, 4))).textlength(txt, font=f)
        st = Image.new("RGBA", (int(tw + 60), 96), (0, 0, 0, 0)); ds = ImageDraw.Draw(st)
        ds.rounded_rectangle((6, 6, st.width - 6, 90), 14, outline=RED + (255,), width=7); ds.text((st.width / 2, 49), txt, font=f, fill=RED + (255,), anchor="mm")
        a = np.array(st); rng = np.random.default_rng(3); a[..., 3] = np.where(rng.random(a.shape[:2]) < 0.06, (a[..., 3] * 0.3).astype(np.uint8), a[..., 3]); st = Image.fromarray(a)
        st = st.rotate(-6, Image.BICUBIC, expand=True); sc = 1.6 - 0.6 * kk
        st = st.resize((max(1, int(st.width * sc)), max(1, int(st.height * sc))), Image.BICUBIC)
        paste(frame, fade(st, al), PX + PW - 30 - st.width, PY + 68 - st.height / 2 + dy, 0.4, 10, (4, 10))

def clip_frame(img, t):
    ct = ct_of(t); dur = CL_OUT - CL_IN
    bg = blur_bg(img, 0.22) * 0.7 + NAVYBG * 0.45
    frame = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
    kin = ease_out(ct / 0.6); kout = ease_in((ct - (dur - 0.45)) / 0.45)
    rgba = rounded(cv2.resize(img, (CARD_W, CARD_H), interpolation=cv2.INTER_CUBIC), 26, 3)
    tilt = clamp(1 - ease_out(ct / 0.75) + kout)
    im = Image.fromarray(persp(rgba, "top", 0.06 + 0.24 * tilt) if tilt > 0.003 else rgba, "RGBA")
    def ya(q): return -900 * (1 - ease_out(q / 0.6)) - 1000 * ease_in((q - (dur - 0.45)) / 0.45)
    dy = ya(ct); vy = dy - ya(ct - 1 / FPS)
    paste(frame, im, W / 2 - CARD_W / 2, CARD_Y + dy, 0.6, 22, (10, 26), (0, vy))
    al = clamp((ct - 0.7) / 0.4) * (1 - kout)
    if al > 0: credit(frame, "Vídeo: UOL News", W / 2 + CARD_W / 2 - 16, CARD_Y + CARD_H - 50 + dy, al)
    draw_caption(frame, t, CARD_Y + CARD_H - 120 + dy, 40, ("an",))
    panel(frame, t)
    return frame

# ---------------------------------------------------------------- fechamento
GLASS_DIA = (out_t("me", 4.28), EDIT_END)
CTA_T = out_t("me", 8.40)
CARD_X, CARD_Y2, CARD_W2, CARD_H2 = 90, 168, 900, 262
def draw_dia25(frame, t):
    a, b = GLASS_DIA
    if not (a <= t < b + 1.8): return
    u = t - a; kin = ease_out(u / 0.6); kout = ease_in((t - (EDIT_END - 0.4)) / 0.4)
    base = np.asarray(frame.convert("RGB"))[CARD_Y2:CARD_Y2 + CARD_H2, CARD_X:CARD_X + CARD_W2].astype(np.float32)
    glass = cv2.GaussianBlur(base, (0, 0), 16) * 0.42 + np.array([4, 14, 28], np.float32) * 0.58
    gl = Image.fromarray(np.clip(glass, 0, 255).astype(np.uint8)).convert("RGBA")
    m = Image.new("L", (CARD_W2, CARD_H2), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, CARD_W2 - 1, CARD_H2 - 1), 26, fill=255); gl.putalpha(m)
    d = ImageDraw.Draw(gl); d.rounded_rectangle((1, 1, CARD_W2 - 2, CARD_H2 - 2), 26, outline=GOLD + (210,), width=2)
    d.text((CARD_W2 / 2, 50), "SEGUNDO TURNO", font=MF("Bold", 26), fill=GD, anchor="mm")
    kk = back_out((u - 0.15) / 0.5, 1.4); d.text((CARD_W2 / 2, 142), "DIA 25", font=MF("ExtraBold", int(118 * (0.7 + 0.3 * kk))), fill=GOLD_L + (255,), anchor="mm")
    lw = int(150 * ease_out((u - 0.5) / 0.6)); d.rectangle((CARD_W2 / 2 - lw, 212, CARD_W2 / 2 + lw, 214), fill=GD)
    tilt = clamp((1 - kin) + kout)
    arr = persp(np.asarray(gl), "top", 0.05 + 0.4 * tilt) if tilt > 0.003 else np.asarray(gl)
    paste(frame, fade(Image.fromarray(arr, "RGBA"), clamp(kin * 1.6) * (1 - kout)), CARD_X, CARD_Y2 + 60 * (1 - kin), 0.55, 20, (8, 20))

def draw_cta(frame, t):
    u = t - CTA_T
    if u < 0: return
    k = back_out(u / 0.5, 1.8); al = clamp(u / 0.15) * (1 - ease_in((t - (EDIT_END - 0.3)) / 0.3))
    f = MF("ExtraBold", 34); txt = "COMENTE O QUE VOCÊ ACHA"
    tw = ImageDraw.Draw(Image.new("RGBA", (4, 4))).textlength(txt, font=f)
    lay = Image.new("RGBA", (int(tw + 150), 96), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, lay.width - 1, 95), 48, fill=GD)
    # balão de comentário
    bx, by = 34, 26; d.rounded_rectangle((bx, by, bx + 52, by + 38), 10, fill=NAVY + (255,)); d.polygon([(bx + 12, by + 36), (bx + 26, by + 36), (bx + 10, by + 50)], fill=NAVY + (255,))
    for j in range(3): d.ellipse((bx + 11 + j * 13, by + 16, bx + 18 + j * 13, by + 23), fill=GD)
    d.text((110, 48), txt, font=f, fill=NAVY + (255,), anchor="lm")
    sc = 0.7 + 0.3 * k; lay = lay.resize((int(lay.width * sc), int(lay.height * sc)), Image.BICUBIC)
    paste(frame, fade(lay, al), W / 2 - lay.width / 2, 1600 - lay.height / 2, 0.45, 14, (4, 12))

# ---------------------------------------------------------------- render
_cache = {}
def seg_frames(s):
    key = (s["src"], s["a"])
    if key not in _cache:
        _cache.clear()
        if s["src"] == "me": _cache[key] = decode(ME, s["a"], s["b"], 1080, 1920)
        else: _cache[key] = np.stack([GRADE(f) for f in decode(CL, s["a"], s["b"], CW_, CH_, CROP)])
    return _cache[key]

def render_frame(t):
    if t >= END_IN + 0.35: return end_card(t)
    tt = min(t, EDIT_END - 1e-3); s = seg_at(tt); u = tt - s["t0"]; fr = seg_frames(s)
    img = fr[min(len(fr) - 1, int(u * FPS))]
    if s["src"] == "me":
        frame = Image.fromarray(me_full2(img, t)).convert("RGBA")
        if s is segs[0] or s is segs[1]:
            react_tag(frame, t, "PESQUISA  ·  2º TURNO", 0.9, CL_IN - 0.3)
            q = (t - (CL_IN - 0.4)) / 0.4                          # a matéria entra caindo por cima
            if q > 0:
                frame = Image.blend(frame.convert("RGB"), Image.fromarray(np.clip(NAVYBG, 0, 255).astype(np.uint8)), clamp(q) * 0.85).convert("RGBA")
        else:
            draw_dia25(frame, t); draw_cta(frame, t)
        draw_caption(frame, t, 1450, 56, ("me",))
    else:
        frame = clip_frame(img, t)
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
        outs = [finish(render_frame(t), t).resize((360, 640), Image.LANCZOS) for t in sorted(ts)]
        sheet = Image.new("RGB", (360 * len(outs), 640)); [sheet.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]
        sheet.save(OUTFILE, quality=90); return
    if MODE.startswith("tail"):
        t0 = float(MODE.split(":")[1]); i0 = int(round(t0 * FPS)); n = int(round(TOTAL * FPS))
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", OUTFILE], stdin=subprocess.PIPE)
        for i in range(i0, n): enc.stdin.write(finish(render_frame(i / FPS), i / FPS).tobytes())
        enc.stdin.close(); enc.wait(); return
    if MODE == "info":
        print("TOTAL", TOTAL, [(s["src"], round(s["t0"], 2), round(s["t1"], 2)) for s in segs]); return
    vout = f"{V}/video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
    n = int(round(TOTAL * FPS))
    for i in range(n):
        enc.stdin.write(finish(render_frame(i / FPS), i / FPS).tobytes())
        if i % 150 == 0: print(f"{i / FPS:.1f}s", flush=True)
    enc.stdin.close(); enc.wait()
    SR = 48000; N = int(TOTAL * SR); vt = np.zeros((N, 2), np.float32)
    srcs = {"me": readw(f"{V}/me_vox.wav"), "cl": readw(f"{V}/cl_vox.wav")}
    for s in segs:
        src = srcs[s["src"]]; a0, a1 = int(s["a"] * SR), int(s["b"] * SR); t0 = int(s["t0"] * SR); p = src[a0:a1].copy()
        f = int(0.03 * SR); env = np.ones(len(p)); env[:f] = np.linspace(0, 1, f); env[-f:] = np.linspace(1, 0, f)
        vt[t0:t0 + len(p)] += p * env[:, None]
    writew(f"{V}/voice.wav", vt)
    ev = [(0.3, sfx.whoosh(0.6), 0.22), (CL_IN - 0.15, sfx.whoosh(0.5), 0.3), (CL_IN + 0.45, sfx.thud(), 0.22),
          (CL_IN + 6.5, sfx.whoosh(0.5), 0.24), (CL_IN + T_MOVE - 0.05, sfx.whoosh(0.45), 0.24), (CL_IN + T_MOVE + 1.0, sfx.paper(), 0.16), (CL_IN + T_SLOPE, sfx.whoosh(0.45), 0.22), (CL_IN + T_SLOPE + 0.4, sfx.marker(0.9), 0.18), (CL_IN + 32.9, sfx.thud(0.6), 0.36), (CL_IN + 32.95, sfx.paper(), 0.2),
          (CL_OUT - 0.45, sfx.whoosh(0.5, False), 0.24), (GLASS_DIA[0] - 0.08, sfx.whoosh(0.4), 0.22), (GLASS_DIA[0] + 0.45, sfx.thud(), 0.22),
          (CTA_T, sfx.whoosh(0.35), 0.18), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/music.wav", "-filter_complex",
                    "[1:a]asplit=2[vox1][key];[2:a]volume=0.8[sf];[3:a]volume=0.20[mus];"
                    "[mus][key]sidechaincompress=threshold=0.02:ratio=8:attack=30:release=600[musd];"
                    f"[vox1][sf][musd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")

main()
