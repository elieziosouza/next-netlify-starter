"""React: Eliezio x Flávio/Vorcaro. Nega no vídeo do Intercept, cobra no áudio (Canal UOL), conclusão com a linha do tempo dos fatos."""
import sys, math, subprocess, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.path.insert(0, f"{S}/work")
import sfx
import grading
GRADE = grading.Fast(grading.cinema, f"{S}/grade/lut_cinema.npy", 0.1, 6)
from minitop import make_minitop, make_minifooter, handles_row

V = f"{S}/v9"; FD = f"{S}/fontdl"
ME, V1, V2 = f"{V}/me.mp4", f"{V}/v1.mp4", f"{V}/v2.mp4"
W, H, FPS = 1080, 1920, 30
WHITE = (255, 255, 255); GOLD = (214, 182, 116); GOLD_L = (245, 226, 176); NAVY = (6, 34, 58); RED = (200, 38, 38)
WH = (255, 255, 255, 255); GD = GOLD + (255,)
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

# ---------------------------------------------------------------- edit decision list (fonte, entrada, saída)
EDL = [("me", 0.80, 4.30),
       ("v1", 0.20, 20.95),
       ("v2", 1.20, 3.75), ("v2", 24.20, 33.40), ("v2", 34.35, 38.45), ("v2", 63.10, 66.95), ("v2", 71.05, 76.20), ("v2", 76.40, 86.65),
       ("me", 22.90, 25.70), ("me", 26.75, 29.60), ("me", 32.00, 37.45), ("me", 38.20, 41.85), ("me", 43.20, 45.70)]
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
V1_IN = out_t("v1", 0.20); V2_IN = out_t("v2", 1.20); V2_OUT = out_t("v2", 86.65)
PANEL_IN = out_t("me", 32.00); PANEL_OUT = out_t("me", 41.85)

# ---------------------------------------------------------------- captions
ME_CAPS = [("VAMOS LÁ ENTÃO, FALA AÍ FLÁVIO", 0.86, 2.45), ("VOCÊ PEDIU DINHEIRO PARA O VORCARO OU...", 2.45, 4.23),
           ("AÍ EU TE PERGUNTO", 22.97, 24.05), ("DÁ PRA CONFIAR NUMA PESSOA DESSA?", 24.05, 25.64),
           ("VOCÊ VAI ME DIZER QUE EU ESTOU MENTINDO AGORA?", 26.84, 29.51),
           ("AÍ ESTÃO OS FATOS", 32.12, 33.55), ("EU ESTOU MOSTRANDO PARA VOCÊS OS FATOS", 33.55, 35.46),
           ("ELE PRIMEIRO DIZ QUE NÃO", 35.46, 36.95), ("DEPOIS...", 36.95, 37.37),
           ("A GENTE VIU QUE ELE PEDIU REALMENTE O DINHEIRO PARA ELE", 38.30, 41.05), ("E AÍ?", 41.10, 41.76),
           ("NÃO ESQUECE, HEIN", 43.29, 44.25), ("DIA 25 TÁ CHEGANDO", 44.25, 45.61)]
FL_CAPS = [("É MENTIRA. DE ONDE VOCÊ TIROU ISSO?", 4.75, 6.40), ("PELO AMOR DE DEUS. AÍ NÃO DÁ.", 8.35, 9.75), ("OBRIGADO.", 9.90, 10.65),
           ("JORNALISTAS, BOM TRABALHO.", 10.90, 12.80), ("MILITANTE, NÃO DÁ, CARA.", 12.90, 13.95), ("DE ONDE VOCÊ TIROU ISSO?", 16.30, 17.25)]
REP_LINES = [("Senador!", 0.38, 1.10), ("Por que o filme do seu pai foi bancado pelo Vorcaro?", 1.18, 4.73),
             ("É que a gente está fazendo uma reportagem…", 6.40, 9.05), ("…que mostra mensagem do senhor pedindo dinheiro pro Vorcaro.", 9.18, 12.65),
             ("Seria importante ter só a sua posição, senador.", 12.79, 16.54), ("São mensagens. A gente já entrou em contato com a sua assessoria.", 17.24, 20.92)]
AU_CAPS = [("IRMÃO, PREFERI TE MANDAR O ÁUDIO AQUI PRA VOCÊ OUVIR COM CALMA", 1.34, 3.62),
           ("E APESAR DE VOCÊ TER DADO A LIBERDADE, DANIEL, DE A GENTE TE COBRAR", 24.34, 27.35),
           ("EU FICO SEM GRAÇA DE FICAR TE COBRANDO, TÁ?", 27.35, 29.72),
           ("MAS, ENFIM, É PORQUE TÁ NUM MOMENTO MUITO DECISIVO AQUI DO FILME", 29.95, 33.29),
           ("E COMO TEM MUITA PARCELA PRA TRÁS, CARA, TÁ TODO MUNDO TENSO", 34.46, 38.36),
           ("ENTÃO, SE VOCÊ PUDER ME DAR UM TOQUE, UMA POSIÇÃO AÍ", 63.19, 66.89),
           ("PORQUE JÁ TEM MUITA CONTA PRA PAGAR ESSE MÊS", 71.19, 73.61), ("E O MÊS SEGUINTE TAMBÉM", 74.81, 76.14),
           ("E AGORA QUE É A RETA FINAL, QUE A GENTE NÃO PODE VACILAR", 76.47, 79.05),
           ("NÃO PODE NÃO HONRAR COM OS COMPROMISSOS AQUI", 79.05, 81.05),
           ("PORQUE SENÃO A GENTE PERDE TUDO, CARA. TUDO É CONTRATO", 81.05, 83.10),
           ("PERDE ATOR, PERDE DIRETOR, PERDE EQUIPE, PERDE TUDO", 83.10, 86.54)]
# palavras que ganham destaque vermelho no áudio
HOT = {"COBRAR", "COBRANDO,", "PARCELA", "CONTA", "PAGAR", "PERDE", "TUDO", "TUDO,", "TUDO."}

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
CAPS = build_caps(ME_CAPS, "me", 5, "me") + build_caps(FL_CAPS, "v1", 5, "fl") + build_caps(AU_CAPS, "v2", 5, "au")
REP = [dict(txt=x, start=out_t("v1", max(a, 0.2)), end=out_t("v1", min(b, 20.95))) for x, a, b in REP_LINES]

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

def draw_reporter(frame, t, y):
    """fala do repórter: linha discreta com rótulo, abaixo do cartão"""
    for r in REP:
        if not (r["start"] <= t < r["end"]): continue
        u = t - r["start"]; al = ease_out(u / 0.18) * clamp((r["end"] - t) / 0.15)
        f = MF("SemiBold", 31); lines = wrap(r["txt"], f, 860)
        lay = Image.new("RGBA", (W, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.text((W / 2, 14), "REPÓRTER", font=MF("Bold", 19), fill=GOLD + (230,), anchor="mm")
        for i, ln in enumerate(lines[:2]):
            d.text((W / 2, 52 + i * 40), ln, font=f, fill=(235, 238, 242, 255), anchor="mm", stroke_width=3, stroke_fill=(4, 12, 22, 200))
        frame.alpha_composite(fade(lay, al), (0, int(y + 10 * (1 - ease_out(u / 0.25)))))

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

# ---------------------------------------------------------------- sources
def decode(path, a, b, w, h, vf=""):
    filt = f"{vf}," if vf else ""
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-t", f"{b - a + 0.1:.3f}", "-i", path, "-vf", f"{filt}fps=30",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    n = len(p) // (w * h * 3)
    return np.frombuffer(p[:n * w * h * 3], np.uint8).reshape(n, h, w, 3)
V1CROP = "crop=1080:1000:0:712"; V1W, V1H = 1080, 1000
REACT = np.stack([GRADE(f) for f in decode(ME, 4.6, 22.6, 478, 850)])        # ele assistindo, sem falar
def react_frame(t):
    n = len(REACT); period = 2 * (n - 1); k = int(t * FPS * 0.85) % period
    return REACT[k if k < n else period - k]

FACE = (245.0, 390.0)
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

WIN1 = (330, 1170, 750, 1730)      # durante o vídeo do Intercept
WIN2 = (370, 1262, 710, 1715)      # durante o áudio
WIN3 = (330, 1190, 750, 1730)      # durante a linha do tempo
def win_state(t):
    """(k, rect) da janelinha do Eliezio. k=0 tela cheia, k=1 janela"""
    if V1_IN <= t < V2_OUT:
        k = ease_io((t - V1_IN) / 0.6) * (1 - ease_io((t - (V2_OUT - 0.5)) / 0.5))
        m = ease_io((t - V2_IN) / 0.7)
        return k, [lerp(a, b, m) for a, b in zip(WIN1, WIN2)]
    if PANEL_IN <= t < PANEL_OUT:
        k = ease_io((t - PANEL_IN) / 0.55) * (1 - ease_io((t - (PANEL_OUT - 0.5)) / 0.5))
        return k, list(WIN3)
    return 0.0, list(WIN1)

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

# ---------------------------------------------------------------- clip 1: limpeza das legendas gravadas
K = lambda n: cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (n, n))
_prev_soft = [None]
def clean_v1(a):
    """apaga as legendas gravadas (amarela do Flávio, branca do repórter) e cobre o resto com vidro fosco suave"""
    mask = np.zeros(a.shape[:2], np.uint8)
    for y0, y1, kind in ((395, 550, "y"), (570, 730, "w")):
        b = a[y0:y1].astype(np.int16); r, g, bl = b[..., 0], b[..., 1], b[..., 2]; mn = b.min(2); mx = b.max(2)
        if kind == "y": txt = ((r > 140) & (g > 120) & (bl < 120) & (r - bl > 60) & (np.abs(r - g) < 70))
        else: txt = ((mn > 195) & (mx - mn < 40))
        txt = txt.astype(np.uint8) * 255
        if txt.sum() < 255 * 80: continue
        near = cv2.dilate(txt, K(13)); dark = ((mx < 80) & (near > 0)).astype(np.uint8) * 255
        mask[y0:y1] = np.maximum(mask[y0:y1], cv2.dilate(cv2.bitwise_or(txt, dark & cv2.dilate(txt, K(9))), K(7)))
    soft = cv2.GaussianBlur(cv2.dilate(mask, K(31)).astype(np.float32) / 255, (0, 0), 14) if mask.any() else np.zeros(a.shape[:2], np.float32)
    if _prev_soft[0] is not None: soft = np.maximum(soft, _prev_soft[0] * 0.82)    # sem piscar entre quadros
    _prev_soft[0] = soft
    if soft.max() < 0.02: return a
    if mask.any(): a = cv2.inpaint(a, mask, 9, cv2.INPAINT_TELEA)
    bl = cv2.GaussianBlur(a, (0, 0), 16).astype(np.float32)
    bl = bl + (np.median(bl.reshape(-1, 3), 0) - bl) * 0.25
    s3 = soft[..., None]
    return np.clip(a * (1 - s3) + bl * s3, 0, 255).astype(np.uint8)

CARD1_W = 930; CARD1_H = int(V1H * CARD1_W / V1W); CARD1_Y = 172
def v1_card(img, t, u, dur):
    """cartão 3D do vídeo do Intercept"""
    kin = ease_out(u / 0.6); kout = ease_in((u - (dur - 0.45)) / 0.45)
    card = cv2.LUT(cv2.resize(img, (CARD1_W, CARD1_H), interpolation=cv2.INTER_AREA), LUT)
    rgba = rounded(card)
    tilt = clamp((1 - ease_out(u / 0.75)) + kout)
    im = Image.fromarray(persp(rgba, "top", 0.08 + 0.24 * tilt) if tilt > 0.003 else rgba, "RGBA")
    def ypos(uu): return -760 * (1 - ease_out(uu / 0.6)) - 900 * ease_in((uu - (dur - 0.45)) / 0.45)
    dy = ypos(u); vy = ypos(u) - ypos(u - 1 / FPS)
    sc = 1 - 0.1 * kout
    if sc < 0.999: im = im.resize((int(im.width * sc), int(im.height * sc)), Image.BICUBIC)
    return im, (W // 2 - im.width // 2, int(CARD1_Y + dy)), (0, vy)

def credit(frame, txt, x, y, al=1.0, anchor="rm"):
    f = MF("SemiBold", 20); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); tw = d0.textlength(txt, font=f)
    lay = Image.new("RGBA", (int(tw + 28), 34), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, lay.width - 1, 33), 17, fill=(3, 10, 20, 170)); d.text((14, 17), txt, font=f, fill=(255, 255, 255, 215), anchor="lm")
    if anchor == "rm": x = x - lay.width
    elif anchor == "mm": x = x - lay.width // 2
    frame.alpha_composite(fade(lay, al), (int(x), int(y)))

def lower_third(frame, t, t0, t1, name, role, x, y):
    u = t - t0
    if u < 0 or t > t1: return
    k = ease_out(u / 0.45) * (1 - ease_in((t - (t1 - 0.4)) / 0.4))
    f1 = MF("ExtraBold", 30); f2 = MF("SemiBold", 21)
    lay = Image.new("RGBA", (620, 96), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    w1 = d.textlength(name, font=f1); w2 = d.textlength(role, font=f2); bw = int(max(w1, w2) + 52)
    d.rounded_rectangle((0, 0, bw, 92), 14, fill=(3, 12, 24, 205)); d.rectangle((0, 12, 5, 80), fill=GD)
    d.text((26, 30), name, font=f1, fill=WH, anchor="lm"); d.text((26, 66), role, font=f2, fill=GOLD + (255,), anchor="lm")
    clip = Image.new("L", lay.size, 0); ImageDraw.Draw(clip).rectangle((0, 0, int(bw * ease_out(u / 0.5)) + 6, 96), fill=255)
    lay.putalpha(Image.fromarray(np.minimum(np.asarray(lay.getchannel("A")), np.asarray(clip))))
    frame.alpha_composite(fade(lay, k), (int(x + 24 * (1 - k)), int(y)))

def react_tag(frame, t, txt, t0, t1, y=196):
    u = t - t0
    if u < 0 or t > t1: return
    k = ease_out(u / 0.5) * (1 - ease_in((t - (t1 - 0.5)) / 0.5))
    f = MF("Bold", 26); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); tw = d0.textlength(txt, font=f)
    lay = Image.new("RGBA", (int(tw + 60), 56), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, lay.width - 1, 55), 28, fill=(4, 14, 26, 190), outline=GD, width=2)
    d.text((30, 28), txt, font=f, fill=GD, anchor="lm")
    frame.alpha_composite(fade(lay, k), (int(W / 2 - lay.width / 2), int(y + 20 * (1 - k))))

# ---------------------------------------------------------------- áudio: envelope para a onda
def load_env(path):
    w = wave.open(path); n = w.getnframes(); sr = w.getframerate(); ch = w.getnchannels()
    a = np.frombuffer(w.readframes(n), np.int16).astype(np.float32).reshape(-1, ch).mean(1) / 32768
    hop = sr // 100; m = len(a) // hop
    e = np.sqrt((a[:m * hop].reshape(m, hop) ** 2).mean(1))
    e = np.convolve(e, np.ones(4) / 4, "same")
    return e / (np.percentile(e, 98) + 1e-6)
ENV2 = load_env(f"{V}/v2_vox.wav")
def env2(x):
    i = int(x * 100); return float(ENV2[i]) if 0 <= i < len(ENV2) else 0.0

def portrait(path, w, h):
    im = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB); ih, iw = im.shape[:2]
    sc = max(w / iw, h / ih); im = cv2.resize(im, (int(iw * sc) + 1, int(ih * sc) + 1), interpolation=cv2.INTER_AREA)
    x0 = (im.shape[1] - w) // 2; return GRADE(np.ascontiguousarray(im[:h, x0:x0 + w]))
PW, PH = 400, 520
P_FL = portrait(f"{V}/flavio.png", PW, PH); P_VO = portrait(f"{V}/vorcaro.png", PW, PH)
HEAD = GRADE(cv2.cvtColor(cv2.imread(f"{V}/intercept.png"), cv2.COLOR_BGR2RGB))

def kicker(frame, t, u):
    """'ÁUDIO' entra grande no centro e sobe para virar o selo do topo"""
    k = ease_io((u - 0.75) / 0.6)
    al = ease_out(u / 0.25) * (1 - ease_in((t - (V2_OUT - 0.45)) / 0.45))
    size = int(lerp(150, 46, k)); y = lerp(760, 205, k)
    f = MF("ExtraBold", size); lay = Image.new("RGBA", (W, size + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    sp = int(lerp(18, 6, k)); txt = "ÁUDIO"; ws = [d.textlength(c, font=f) for c in txt]; tw = sum(ws) + sp * (len(txt) - 1)
    x = W / 2 - tw / 2
    for c, cw in zip(txt, ws): d.text((x, 30), c, font=f, fill=GD); x += cw + sp
    if u < 0.75:   # entrada com desfoque
        lay = lay.filter(ImageFilter.GaussianBlur(10 * (1 - ease_out(u / 0.35))))
    frame.alpha_composite(fade(lay, al), (0, int(y - size / 2 - 30)))
    k2 = ease_out((u - 1.15) / 0.5) * (1 - ease_in((t - (V2_OUT - 0.45)) / 0.45))
    if k2 > 0:
        d = ImageDraw.Draw(frame)
        d.text((W / 2, 262 + 8 * (1 - k2)), "08/09/2025  ·  DIVULGADO PELO INTERCEPT BRASIL", font=MF("SemiBold", 22), fill=(255, 255, 255, int(200 * k2)), anchor="mm")
        lw = int(70 * k2); d.rectangle((W / 2 - lw, 234, W / 2 + lw, 236), fill=GD)

def waveform(frame, t, srcx, al, cy=960):
    lay = Image.new("RGBA", (W, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    n = 41; c = n // 2; bw = 9; gap = 12; x0 = W / 2 - (n * bw + (n - 1) * gap) / 2
    for i in range(n):
        dist = abs(i - c)
        e = env2(srcx - dist * 0.03) * (1 - dist / (n * 0.75)) + 0.03 * (0.5 + 0.5 * math.sin(t * 6 + i))
        hh = 6 + 140 * clamp(e) ** 0.8
        x = x0 + i * (bw + gap); col = GOLD_L if dist < 3 else GOLD
        d.rounded_rectangle((x, 100 - hh / 2, x + bw, 100 + hh / 2), bw // 2, fill=col + (int(255 * (1 - dist / (n * 0.9))),))
    glow = lay.filter(ImageFilter.GaussianBlur(10)); frame.alpha_composite(fade(glow, al * 0.6), (0, cy - 100)); frame.alpha_composite(fade(lay, al), (0, cy - 100))

def pcard(rgb, glow):
    rgba = rounded(rgb, 24, 3, GOLD + (int(150 + 105 * glow),))
    return rgba

def name_tag(frame, cx, y, name, role, al):
    d = ImageDraw.Draw(frame)
    d.text((cx, y), name, font=MF("ExtraBold", 27), fill=(255, 255, 255, int(255 * al)), anchor="mm")
    d.text((cx, y + 34), role, font=MF("SemiBold", 20), fill=GOLD + (int(240 * al),), anchor="mm")

FACT1 = (out_t("v2", 34.40), out_t("v2", 66.90))       # manchete do Intercept
FACT2 = (out_t("v2", 71.10), out_t("v2", 79.30))       # números da reportagem
def fact_state(t):
    for i, (a, b) in enumerate((FACT1, FACT2)):
        if a <= t < b: return i, t - a, b - a
    return None, 0, 0

def headline_card(u, dur):
    w = 900; h = int(HEAD.shape[0] * w / HEAD.shape[1])
    rgba = rounded(cv2.LUT(cv2.resize(HEAD, (w, h), interpolation=cv2.INTER_AREA), LUT), 24, 3)
    return rgba

def numbers_card(u):
    w, h = 900, 560; im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 26, fill=(5, 16, 30, 236), outline=GD, width=3)
    d.text((48, 56), "SEGUNDO O INTERCEPT BRASIL", font=MF("Bold", 24), fill=GD, anchor="lm")
    d.rectangle((48, 82, 160, 84), fill=GD)
    k1 = ease_out((u - 0.25) / 0.9); k2 = ease_out((u - 0.9) / 0.9)
    v1 = 24 * k1; v2 = 10.6 * k2
    d.text((48, 168), f"US$ {v1:.0f} mi", font=MF("ExtraBold", 92), fill=WH, anchor="lm")
    d.text((50, 236), "negociados para o filme (≈ R$ 134 milhões)", font=MF("SemiBold", 27), fill=(220, 226, 234, 255), anchor="lm")
    d.rectangle((48, 284, w - 48, 285), fill=(255, 255, 255, 40))
    d.text((48, 362), f"US$ {v2:.1f} mi".replace(".", ","), font=MF("ExtraBold", 92), fill=GOLD + (255,), anchor="lm")
    d.text((50, 430), "pagos em 2025, segundo a reportagem (≈ R$ 61 milhões)", font=MF("SemiBold", 27), fill=(220, 226, 234, 255), anchor="lm")
    d.text((48, 510), "Fonte: Intercept Brasil", font=MF("SemiBold", 20), fill=(255, 255, 255, 150), anchor="lm")
    return np.asarray(im)

_v2bg = {}
def audio_frame(v2img, me_img, t, u, srcx):
    # fundo: azul profundo + o vídeo do áudio desfocado e escuro
    bg = NAVYBG * 0.85 + blur_bg(v2img, 0.20) * 0.6
    if LAST_V1BG is not None and t - V2_IN < 0.5:
        m = smooth((t - V2_IN) / 0.5); bg = LAST_V1BG * (1 - m) + bg * m
    k, rect = win_state(t)
    frame = compose_me_layer(bg, me_img, t, rect, k)
    ex = ease_in((t - (V2_OUT - 0.5)) / 0.5)                        # saída de tudo
    fi, fu, fd = fact_state(t)
    rec = 0.0
    if fi is not None: rec = ease_io(fu / 0.5) * (1 - ease_io((fu - (fd - 0.45)) / 0.45))
    # retratos: entram pelas laterais girando, se encaram
    e = env2(srcx)
    for side, P, cx, nm, rl in (("left", P_FL, 290, "FLÁVIO BOLSONARO", "senador (PL-RJ)"), ("right", P_VO, 790, "DANIEL VORCARO", "dono do Banco Master")):
        uu = u - (0.95 if side == "left" else 1.1)
        if uu < 0: continue
        kin = ease_out(uu / 0.65)
        glow = clamp(e * 1.3) if side == "left" else 0.0
        rgba = pcard(P, glow)
        a = 0.10 + 0.45 * (1 - kin) + 0.4 * ex
        im = Image.fromarray(persp(rgba, side, a), "RGBA")
        sc = 1 - 0.14 * rec + 0.015 * glow
        if rec > 0.01 or glow > 0:
            arr = np.asarray(im).copy(); arr[..., :3] = (arr[..., :3] * (1 - 0.6 * rec)).astype(np.uint8); im = Image.fromarray(arr, "RGBA")
            im = im.resize((int(PW * sc), int(PH * sc)), Image.BICUBIC)
        def xpos(q): return (-520 if side == "left" else 520) * ((1 - ease_out(q / 0.65)) + ease_in(((t - (V2_OUT - 0.5)) / 0.5)))
        dx = xpos(uu); vx = dx - xpos(uu - 1 / FPS)
        x = cx - im.width / 2 + dx; y = 300 + (PH - im.height) / 2 - 30 * rec
        if side == "left" and glow > 0.05 and rec < 0.5:
            g = Image.new("RGBA", (im.width + 80, im.height + 80), (0, 0, 0, 0))
            ImageDraw.Draw(g).rounded_rectangle((40, 40, 40 + im.width, 40 + im.height), 30, fill=GOLD + (int(120 * glow),))
            frame.alpha_composite(g.filter(ImageFilter.GaussianBlur(26)), (int(x - 40), int(y - 40)))
        paste(frame, im, x, y, 0.65, 24, (8, 22), (vx, 0))
        if rec < 0.6: name_tag(frame, cx + dx, 860, nm, rl, kin * (1 - rec / 0.6) * (1 - ex))
    # pulso viajando de Flávio para Vorcaro
    if u > 1.6 and rec < 0.5 and ex < 0.5:
        d = ImageDraw.Draw(frame); al = ease_out((u - 1.6) / 0.4) * (1 - rec * 2) * (1 - ex * 2)
        for j in range(9):
            x = 500 + j * 10.0; d.ellipse((x - 2, 558, x + 2, 562), fill=(255, 255, 255, int(110 * al)))
        ph = ((t * 0.9) % 1.0); x = 494 + 92 * ph
        d.ellipse((x - 6, 554, x + 6, 566), fill=GOLD_L + (int(255 * al * (1 - abs(ph - 0.5) * 1.2)),))
    # cartões de fato, em camada por cima dos retratos
    if fi is not None:
        def ypos(q): return 620 * (1 - ease_out(q / 0.6)) + 1100 * ease_in((q - (fd - 0.45)) / 0.45)
        rgba = headline_card(fu, fd) if fi == 0 else numbers_card(fu)
        tilt = clamp(1 - ease_out(fu / 0.7) + ease_in((fu - (fd - 0.45)) / 0.45))
        im = Image.fromarray(persp(rgba, "top", 0.04 + 0.22 * tilt), "RGBA")
        dy = ypos(fu); vy = dy - ypos(fu - 1 / FPS)
        y = (300 if fi == 0 else 285) + dy
        paste(frame, im, W / 2 - im.width / 2, y, 0.7, 26, (10, 28), (0, vy))
        if fi == 0:
            credit(frame, "Reportagem: Intercept Brasil", W / 2 + im.width / 2 - 14, y + im.height + 12, clamp(1 - tilt * 2))
    kicker(frame, t, u)
    waveform(frame, t, srcx, ease_out((u - 1.3) / 0.5) * (1 - ex), 975)
    draw_caption(frame, t, 1112, 54, ("au",))
    credit(frame, "Áudio: Intercept Brasil  ·  via Canal UOL", W - 40, 1735 if k < 0.5 else 1727, ease_out((u - 1.5) / 0.5) * (1 - ex))
    return frame

# ---------------------------------------------------------------- linha do tempo (conclusão)
STEPS = [("1", "NEGOU", "“É mentira. De onde você tirou isso?”", out_t("me", 35.50)),
         ("2", "O ÁUDIO", "Cobra Vorcaro: “tem muita parcela pra trás”", out_t("me", 36.95)),
         ("3", "ADMITIU", "Depois, confirmou em vídeo que pediu dinheiro a Vorcaro para o filme", out_t("me", 38.40))]
def step_card(num, title, body):
    w, h = 920, 196; im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 24, fill=(5, 16, 30, 238), outline=GOLD + (200,), width=2)
    d.ellipse((34, 50, 126, 142), fill=GD); d.text((80, 96), num, font=MF("ExtraBold", 50), fill=NAVY, anchor="mm")
    d.text((158, 52), title, font=MF("ExtraBold", 36), fill=GD, anchor="lm")
    for i, ln in enumerate(wrap(body, MF("SemiBold", 28), 720)[:2]):
        d.text((158, 104 + i * 38), ln, font=MF("SemiBold", 28), fill=(232, 236, 242, 255), anchor="lm")
    return np.asarray(im)
_steps = [step_card(n, a, b) for n, a, b, _ in STEPS]

def panel_frame(me_img, t):
    bg = blur_bg(me_img, 0.22)
    k, rect = win_state(t)
    frame = compose_me_layer(bg, me_img, t, rect, k)
    ex = ease_in((t - (PANEL_OUT - 0.5)) / 0.5)
    u = t - PANEL_IN
    kh = ease_out((u - 0.3) / 0.5) * (1 - ex)
    if kh > 0:
        d = ImageDraw.Draw(frame)
        d.text((W / 2, 238 + 14 * (1 - kh)), "OS FATOS", font=MF("ExtraBold", 54), fill=(255, 255, 255, int(255 * kh)), anchor="mm")
        lw = int(80 * kh); d.rectangle((W / 2 - lw, 282, W / 2 + lw, 284), fill=GD)
    for i, (rgba, (_, _, _, ts)) in enumerate(zip(_steps, STEPS)):
        uu = t - ts
        if uu < 0: continue
        kin = ease_out(uu / 0.55)
        a = 0.03 + 0.5 * (1 - kin) + 0.5 * ex
        im = Image.fromarray(persp(rgba, "right", a), "RGBA")
        def xpos(q): return 900 * (1 - ease_out(q / 0.55)) - 1300 * ease_in((t - (PANEL_OUT - 0.5)) / 0.5)
        dx = xpos(uu); vx = dx - xpos(uu - 1 / FPS)
        # cartões anteriores ficam um pouco mais escuros quando entra o próximo (camadas)
        nxt = [t - s[3] for s in STEPS[i + 1:] if t - s[3] > 0]
        if nxt:
            dim = 0.25 * ease_out(min(nxt) / 0.4); arr = np.asarray(im).copy(); arr[..., :3] = (arr[..., :3] * (1 - dim)).astype(np.uint8); im = Image.fromarray(arr, "RGBA")
        paste(frame, im, W / 2 - im.width / 2 + dx, 330 + i * 222, 0.6, 20, (8, 20), (vx, 0))
    kc = ease_out((t - STEPS[0][3] - 0.6) / 0.5) * (1 - ex)
    if kc > 0: credit(frame, "Fontes: Intercept Brasil · Canal UOL · CNN Brasil", W / 2, 982, kc, "mm")
    draw_caption(frame, t, 1112, 50, ("me",))
    return frame

# ---------------------------------------------------------------- moldura
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

# ---------------------------------------------------------------- render
_cache = {}
LAST_V1BG = None
def seg_frames(s):
    key = (s["src"], s["a"])
    if key not in _cache:
        _cache.clear()
        if s["src"] == "me": _cache[key] = np.stack([GRADE(f) for f in decode(ME, s["a"], s["b"], 478, 850)])
        elif s["src"] == "v1": _cache[key] = np.stack([GRADE(cv2.resize(clean_v1(f.copy()), (CARD1_W, CARD1_H), interpolation=cv2.INTER_AREA)) for f in decode(V1, s["a"], s["b"], V1W, V1H, V1CROP)])
        else: _cache[key] = decode(V2, s["a"], s["b"], 540, 960, "scale=540:960")
    return _cache[key]

def render_frame(t):
    global LAST_V1BG
    if t >= END_IN + 0.35: return end_card(t)
    tt = min(t, EDIT_END - 1e-3); s = seg_at(tt); u = tt - s["t0"]; fr = seg_frames(s)
    img = fr[min(len(fr) - 1, int(u * FPS))]
    if s["src"] == "me" and PANEL_IN <= t < PANEL_OUT:
        frame = panel_frame(img, t)
    elif s["src"] == "me":
        z = 0.035 * smooth((t - out_t("me", 24.0)) / 1.6) * (1 - smooth((t - out_t("me", 25.7)) / 0.3)) if out_t("me", 22.9) <= t < out_t("me", 25.7) else 0
        frame = Image.fromarray(np.clip(me_full(img, t, z).astype(np.float32) * VIG, 0, 255).astype(np.uint8)).convert("RGBA")
        draw_caption(frame, t, 1450, 56, ("me",))
        react_tag(frame, t, "REACT  ·  CASO VORCARO", 0.9, 3.4)
    elif s["src"] == "v1":
        bg = blur_bg(cv2.resize(img, (V1W // 2, V1H // 2)), 0.24); LAST_V1BG = bg
        k, rect = win_state(t)
        frame = compose_me_layer(bg, react_frame(t), t, rect, k)
        im, (cx, cy), vel = v1_card(img, t, u, s["t1"] - s["t0"])
        paste(frame, im, cx, cy, 0.6, 22, (10, 26), vel)
        al = clamp((u - 0.7) / 0.4) * (1 - clamp((u - (s["t1"] - s["t0"] - 0.6)) / 0.3))
        credit(frame, "Vídeo: Intercept Brasil", W // 2 + CARD1_W // 2 - 16, CARD1_Y + 18, al)
        lower_third(frame, t, V1_IN + 0.9, V1_IN + 4.6, "FLÁVIO BOLSONARO", "senador (PL-RJ)", 90, CARD1_Y + 40)
        draw_caption(frame, t, 615, 48, ("fl",))
        draw_reporter(frame, t, 1050)
    else:
        u2 = t - V2_IN
        frame = audio_frame(img, react_frame(t), t, u2, s["a"] + u)
    draw_banners(frame, t)
    if t >= END_IN: frame.alpha_composite(fade(end_card(t), clamp((t - END_IN) / 0.35)))
    return frame

def main():
    if MODE.startswith("frames"):
        ts = [float(x) for x in MODE.split(":")[1].split(",")]
        outs = [finish(render_frame(t), t).resize((360, 640), Image.LANCZOS) for t in ts]
        sheet = Image.new("RGB", (360 * len(outs), 640)); [sheet.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]
        sheet.save(OUTFILE, quality=90); return
    if MODE == "info":
        print("TOTAL", TOTAL, "V1", V1_IN, "V2", V2_IN, V2_OUT, "PANEL", PANEL_IN, PANEL_OUT, "FACTS", FACT1, FACT2); return
    vout = f"{V}/video.mp4"
    if MODE != "audio":
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
        n = int(round(TOTAL * FPS))
        for i in range(n):
            enc.stdin.write(finish(render_frame(i / FPS), i / FPS).tobytes())
            if i % 150 == 0: print(f"{i / FPS:.1f}s", flush=True)
        enc.stdin.close(); enc.wait()
    # áudio: cortes pelo EDL com fades curtos
    parts = []
    for j, s in enumerate(segs):
        srcwav = f"{V}/{s['src']}_vox.wav"
        pj = f"{V}/a{j}.wav"; d = s["b"] - s["a"]; fi = 0.02 if s["src"] != "v2" else 0.05
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{s['a']:.3f}", "-t", f"{d:.3f}", "-i", srcwav,
                        "-af", f"afade=t=in:d={fi},afade=t=out:st={d - 0.04:.3f}:d=0.04", "-ar", "48000", "-ac", "2", pj], check=True)
        parts.append(pj)
    lst = f"{V}/alist.txt"; open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "pcm_s16le", f"{V}/voice_edit.wav"], check=True)
    ev = [(0.3, sfx.whoosh(0.6), 0.22)]
    ev += [(V1_IN - 0.15, sfx.whoosh(0.5), 0.30), (V1_IN + 0.45, sfx.thud(), 0.22), (V2_IN - 0.3, sfx.whoosh(0.5, False), 0.22)]
    ev += [(V2_IN + 0.05, sfx.thud(), 0.34), (V2_IN + 0.75, sfx.whoosh(0.5), 0.22), (V2_IN + 0.95, sfx.whoosh(0.45), 0.2), (V2_IN + 1.1, sfx.whoosh(0.45), 0.2)]
    for a, b in (FACT1, FACT2): ev += [(a - 0.12, sfx.whoosh(0.45), 0.26), (a + 0.4, sfx.paper(), 0.25), (b - 0.45, sfx.whoosh(0.4, False), 0.18)]
    ev += [(V2_OUT - 0.5, sfx.whoosh(0.5), 0.24), (PANEL_IN, sfx.whoosh(0.5), 0.24)]
    for *_, ts in STEPS: ev += [(ts - 0.08, sfx.whoosh(0.4), 0.22), (ts + 0.42, sfx.thud(), 0.24)]
    ev += [(PANEL_OUT - 0.5, sfx.whoosh(0.5), 0.22), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
    ev = [e for e in ev if 0 <= e[0] < TOTAL - 0.9]
    sfx.build(ev, TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice_edit.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/music.wav", "-filter_complex",
                    "[1:a]apad,asplit=2[vox1][key];[2:a]volume=0.8,apad[sf];[3:a]volume=0.22[mus];"
                    "[mus][key]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=500[musd];"
                    f"[vox1][sf][musd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")

main()
