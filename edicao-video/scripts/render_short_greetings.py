"""Short 9:16 (1080x1920): Greetings (cumprimentos) em ~51 s (semana 2, básico). Voz gerada pelo conector do ElevenLabs (v4).
Partes do dia (morning, afternoon, evening, night), hi/hello, how are you, e 2 quizzes com contador respondidos no próprio vídeo."""
import sys, os, math, re, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.path.insert(0, f"{S}/work")
import sfx
V = f"{S}/v92"; FD = f"{S}/fontdl"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H, FPS = 1080, 1920, 30
CUT = (0.0, 0.0)
PINS, GAP = [25.38, 31.94], 5.6   # contadores: entre "good evening?" (25,18) e "Good morning!" (25,58); entre "good night?" (31,78) e "Good night!" (32,09)
PIN = PINS[0]
def f(t): return t + GAP * sum(1 for p in PINS if p < t)
VO_LEN = f(38.24); TOTAL = VO_LEN + 1.2
NAVY = (12, 28, 58); INK = (16, 22, 36); WHITE = (255, 255, 255); YEL = (255, 214, 64); YEL_D = (64, 48, 0)
C_AM = (236, 84, 84); C_IS = (64, 150, 255); C_ARE = (52, 190, 110); C_MOR = (255, 196, 60); C_AFT = (255, 140, 60); C_EVE = (150, 100, 220); C_NIG = (64, 110, 220); GREEN = (46, 184, 92); C_ING = (255, 214, 64); MUTED = (180, 196, 224); RED_B = (220, 40, 40)
def MF(w, s): return ImageFont.truetype(f"{FD}/Montserrat-{w}.ttf", s)
def ANTON(s): return ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def eio(x): x = clamp(x); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
def bo(x, s=1.7): x = clamp(x) - 1; return 1 + (s + 1) * x ** 3 + s * x ** 2
def env(t, a, b, fi=0.3, fo=0.25): return clamp((t - a) / fi) * clamp((b - t) / fo)
def fade(img, a):
    if a >= 1: return img
    img = img.copy(); img.putalpha(img.getchannel("A").point(lambda v: int(v * max(0, a)))); return img
def put(fr, im, x, y, al=1.0, sc=1.0):
    if al <= 0.01: return
    if abs(sc - 1) > 0.004: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
    fr.alpha_composite(fade(im, al), (int(x - im.width / 2), int(y - im.height / 2)))
def sput(fr, im, x, y, al=1.0, sc=1.0):
    if al <= 0.01: return
    if abs(sc - 1) > 0.004: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
    sh = Image.new("RGBA", (im.width + 60, im.height + 60), (0, 0, 0, 0)); blk = Image.new("RGBA", im.size, (0, 0, 0, 255)); blk.putalpha(im.getchannel("A").point(lambda v: int(v * 0.45)))
    sh.alpha_composite(blk, (30, 42)); sh = sh.filter(ImageFilter.GaussianBlur(14)); fr.alpha_composite(fade(sh, al), (int(x - im.width / 2 - 30), int(y - im.height / 2 - 30)))
    put(fr, im, x, y, al)
_tc = {}
def txt(t_, f, col, stroke=0, scol=INK):
    key = (t_, f.path, f.size, col, stroke)
    if key not in _tc:
        bb = f.getbbox(t_); im = Image.new("RGBA", (bb[2] - bb[0] + 20 + 2 * stroke, bb[3] - bb[1] + 20 + 2 * stroke), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10 - bb[0] + stroke, 10 - bb[1] + stroke), t_, font=f, fill=col + (255,), stroke_width=stroke, stroke_fill=scol + (255,)); _tc[key] = im
    return _tc[key]
def chip(t_, fill, col=WHITE, size=40, pad=26, rad=None):
    f = MF("ExtraBold", size); w = int(f.getlength(t_)) + pad * 2; h = int(size * 1.7)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), rad if rad is not None else h // 2, fill=fill + (255,)); d.text((w / 2, h / 2 + 1), t_, font=f, fill=col + (255,), anchor="mm"); return im
_emo = {}
def emoji(ch, size):
    key = (ch, size)
    if key not in _emo:
        f = ImageFont.truetype(EMOJI, 109); im = Image.new("RGBA", (180, 160), (0, 0, 0, 0)); ImageDraw.Draw(im).text((8, 8), ch, font=f, embedded_color=True)
        bb = im.getbbox(); im = im.crop(bb) if bb else im; sc = size / max(im.size); _emo[key] = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    return _emo[key]
# ---------------------------------------------------------------- falas (tempos da fala original; f() abre o contador)
SEG = [("en", 0.05, 2.25, "Hello! Today: greetings."), ("pt", 2.60, 4.70, "Você sabe dizer bom dia em inglês?"),
       ("en", 5.02, 8.81, "Good morning is bom dia. Good afternoon is boa tarde."), ("en", 9.14, 11.85, "Good evening is boa noite, quando você chega."),
       ("en", 12.17, 15.83, "Good night is boa noite, quando você vai embora ou vai dormir."), ("en", 16.10, 21.15, "Hi and hello are oi e olá. How are you? I'm fine, thanks!"),
       ("en", 21.44, 25.18, "Quiz! It's eight in the morning. Good morning or good evening?"), ("pt", 25.58, 27.84, "Good morning! De manhã, é morning."),
       ("en", 28.16, 31.78, "Quiz! You are going to bed. Good evening or good night?"), ("pt", 32.09, 34.61, "Good night! Para dormir, é good night."),
       ("pt", 34.89, 38.24, "Comenta se você acertou, me segue e salva pra revisar!")]
SEG = [(lg, f(a), f(b), tx) for lg, a, b, tx in SEG]
PAIRS = []
for s_ in SEG:
    if s_[0] == "en" or not PAIRS or PAIRS[-1]["pt"] is not None: PAIRS.append(dict(en=s_, pt=None))
    else: PAIRS[-1]["pt"] = s_
for i, p in enumerate(PAIRS): p["t1"] = PAIRS[i + 1]["en"][1] - 0.1 if i + 1 < len(PAIRS) else TOTAL
HLW = {"morning": C_MOR, "afternoon": C_AFT, "evening": C_EVE, "night": C_NIG}
def karaoke(t_, a, b, t, f, maxw, col=WHITE, hl=True):
    """frase com a palavra falada acendendo (amarelo) e am/is/are e o verbo com ING nas cores da regra"""
    words = t_.split(); tot = sum(len(w) + 1 for w in words); acc = 0; times = []
    for w in words: times.append(a + (b - a) * acc / tot); acc += len(w) + 1
    sp = f.getlength(" "); lines = [[]]; cw = 0
    for i, w in enumerate(words):
        wl = f.getlength(w)
        if lines[-1] and cw + sp + wl > maxw: lines.append([]); cw = 0
        lines[-1].append((i, w, wl)); cw += (sp if cw else 0) + wl
    lh = int(f.size * 1.28); im = Image.new("RGBA", (maxw + 40, lh * len(lines) + 16), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for li, ln in enumerate(lines):
        lw = sum(w_[2] for w_ in ln) + sp * (len(ln) - 1); x = (im.width - lw) / 2; y = li * lh + 4
        for i, w, wl in ln:
            c = HLW.get(re.sub(r"[^\w]", "", w.lower())) if hl else None
            on = times[i] <= t
            if c: d.rounded_rectangle((x - 8, y + 4, x + wl + 8, y + f.size * 1.16), 12, fill=c + (255,)); fc = INK if c == C_ING else WHITE
            else: fc = (YEL if (hl and on and t < b + 0.3) else col)
            d.text((x, y), w, font=f, fill=fc + (255,), stroke_width=4 if not c else 0, stroke_fill=INK + (255,)); x += wl + sp
    return im
# ---------------------------------------------------------------- fundo
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.38) / H) ** 2)
BG = np.array(NAVY, np.float32) + np.array([26, 52, 96], np.float32) * np.clip(1 - r * 1.5, 0, 1)[..., None]
for g in range(0, W, 60): BG[:, g:g + 1] += 6
for g in range(0, H, 60): BG[g:g + 1, :] += 6
BG = Image.fromarray(np.clip(BG, 0, 255).astype(np.uint8)).convert("RGBA"); del yy, xx, r
hd = ImageDraw.Draw(BG); hd.rounded_rectangle((300, 70, 780, 130), 30, fill=WHITE + (255,)); hd.text((540, 100), "ENGLISH CLASS · Teacher Eliezio", font=MF("ExtraBold", 24), fill=INK + (255,), anchor="mm")
# ---------------------------------------------------------------- avatar (1 sorrindo, 2 desconfiado, 7 surpreso, 8 piscando)
AV = [Image.open(f"{S}/v77/av3d_{k}.png").convert("RGBA").resize((360, 360), Image.LANCZOS) for k in range(1, 9)]
EXPR = [(0, 1), (2.6, 2), (4.9, 1), (f(PINS[0]) + 0.1, 2), (f(PINS[0]) + 5.3, 7), (f(26.6), 1), (f(PINS[1]) + 0.1, 2), (f(PINS[1]) + 5.3, 7), (f(33.2), 1), (f(34.9), 8), (f(36.5), 1)]
AMP = None
def amp_at(t):
    i = int(t * 100); return float(AMP[i]) if 0 <= i < len(AMP) else 0.0
def avatar(fr, t):
    cx, cy = 540, 1715; a = amp_at(t)
    i = max(k for k, e in enumerate(EXPR) if e[0] <= t); cur = EXPR[i][1]; prv = EXPR[i - 1][1] if i else cur; k = clamp((t - EXPR[i][0]) / 0.18)
    face = AV[cur - 1] if k >= 1 else Image.blend(AV[prv - 1], AV[cur - 1], k)
    rot = 2.0 * math.sin(t * 2.3) * (0.3 + a); face = face.rotate(rot, Image.BICUBIC) if abs(rot) > 0.05 else face
    bob = -10 * a + 3 * math.sin(t * 1.7); sc = 1 + 0.04 * a
    g = Image.new("RGBA", (480, 480), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((40, 40, 440, 440), fill=YEL + (int(90 + 90 * a),)); put(fr, g.filter(ImageFilter.GaussianBlur(24)), cx, cy + bob, 1, sc)
    ring = Image.new("RGBA", (396, 396), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((0, 0, 395, 395), fill=YEL + (255,))
    put(fr, ring, cx, cy + bob, 1, sc); put(fr, face, cx, cy + bob, 1, sc)
# ---------------------------------------------------------------- palavras que se juntam
def boxword(w, f, fill):
    """palavra branca dentro de caixa colorida (forma comparativa)"""
    bb = f.getbbox(w); im = Image.new("RGBA", (bb[2] - bb[0] + 44, bb[3] - bb[1] + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), 22, fill=fill + (255,)); d.text((22 - bb[0], 20 - bb[1]), w, font=f, fill=WHITE + (255,)); return im
def suffix_join(fr, base, suf, t, a, t0, y, k, col):
    """BASE aparece em a; o sufixo cai do alto e encaixa no fim em t0 (TALL -> TALL|ER)"""
    if t < a: return
    f = ANTON(150); bi = txt(base, f, WHITE, 6); si = boxword(suf, f, col); g = eo((t - t0) / 0.4) if t >= t0 else 0
    tw = bi.width + (si.width - 10) * g; x0 = 540 - tw / 2; sc = 0.6 + 0.4 * bo((t - a) / 0.35, 2)
    if sc < 0.999: put(fr, bi, 540, y, k, sc); return
    put(fr, bi, x0 + bi.width / 2, y, k)
    if g > 0: sput(fr, si, x0 + bi.width - 10 + si.width / 2, y - 160 * (1 - g), k * min(1, g * 2))
def prefix_join(fr, base, pre, t, a, t0, y, k, col):
    """BASE aparece em a; MORE cai na frente em t0 e empurra a palavra"""
    if t < a: return
    f = ANTON(130); bi = txt(base, f, WHITE, 6); pi = boxword(pre, f, col); g = eo((t - t0) / 0.4) if t >= t0 else 0
    gap = 24; tw = bi.width + (pi.width + gap) * g; x0 = 540 - tw / 2; sc = 0.6 + 0.4 * bo((t - a) / 0.35, 2)
    if sc < 0.999: put(fr, bi, 540, y, k, sc); return
    put(fr, bi, x0 + (pi.width + gap) * g + bi.width / 2, y, k)
    if g > 0: sput(fr, pi, x0 + pi.width / 2, y - 160 * (1 - g), k * min(1, g * 2))
def pop(fr, im, x, y, t, a, k, shadow=True):
    if t < a: return
    (sput if shadow else put)(fr, im, x, y, k, 0.5 + 0.5 * bo((t - a) / 0.35, 2.2))
# ---------------------------------------------------------------- cenas (área de cima: y 170-1150; tempos da fala original via f())
QZ = (f(PINS[0]) + 0.3, f(PINS[0]) + 5.3)    # 1º quiz: começo do contador e revelação
QZ2 = (f(PINS[1]) + 0.3, f(PINS[1]) + 5.3)   # 2º quiz
DAY = [("☀️", "GOOD MORNING", "bom dia", C_MOR, 5.02), ("🌤️", "GOOD AFTERNOON", "boa tarde", C_AFT, 6.9),
       ("🌆", "GOOD EVENING", "boa noite · quando chega", C_EVE, 9.14), ("🌙", "GOOD NIGHT", "boa noite · indo embora ou dormir", C_NIG, 12.17)]
def T(a): return f(a)
def ring(fr, t, c0, y):
    u = (t - c0) / 5.0; n_ = int(5.0 - (t - c0)) + 1; fz = (t - c0) % 1; R_ = 100
    lay = Image.new("RGBA", (300, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); col = YEL if n_ > 2 else C_AM
    d.ellipse((150 - R_, 150 - R_, 150 + R_, 150 + R_), fill=(8, 18, 40, 230)); d.ellipse((150 - R_, 150 - R_, 150 + R_, 150 + R_), outline=(60, 84, 128, 255), width=16)
    d.arc((150 - R_, 150 - R_, 150 + R_, 150 + R_), -90, -90 + 360 * (1 - u), fill=col + (255,), width=16)
    put(fr, lay, 540, y); put(fr, txt(str(n_), ANTON(115), col, 5), 540, y, 1, 1 + 0.25 * (1 - eo(fz / 0.3)))
def hook(fr, t):
    k = env(t, 0.0, T(4.9))
    if k <= 0: return
    put(fr, txt("GREETINGS", ANTON(170), YEL, 8), 540, 360, k, 0.9 + 0.1 * bo(t / 0.4))
    pop(fr, chip("BÁSICO · A1", C_ARE, WHITE, 40), 540, 530, t, 0.8, k)
    if t > 1.5: put(fr, emoji("👋", 150), 540, 720, env(t, 1.5, T(4.9)), (0.6 + 0.4 * bo((t - 1.5) / 0.35)), )
    if t > 2.6: put(fr, txt("BOM DIA = ?", ANTON(110), WHITE, 7), 540, 920, env(t, 2.6, T(4.9)), 0.7 + 0.3 * bo((t - 2.6) / 0.35))
def day(fr, t):
    k = env(t, T(4.9), T(16.0))
    if k <= 0: return
    for i, (em, en_, pt, c, a) in enumerate(DAY):
        if t < T(a): continue
        y = 330 + i * 205; u = bo((t - T(a)) / 0.35, 1.8); act = T(a) <= t < (T(DAY[i + 1][4]) if i < 3 else T(16.0))
        card = Image.new("RGBA", (900, 180), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
        d.rounded_rectangle((0, 0, 899, 179), 30, fill=(14, 32, 64, 245), outline=c + (255,), width=7 if act else 3)
        card.alpha_composite(emoji(em, 110), (30, 35)); d.text((175, 40), en_, font=ANTON(64), fill=(WHITE if act else (200, 210, 230)) + (255,))
        d.text((178, 122), pt, font=MF("ExtraBold", 30), fill=(255, 230, 150, 255))
        put(fr, card, 540, y, k * (1 if act or t > T(15.9) else 0.75), (0.6 + 0.4 * u) * (1.03 if act else 1))
def hi(fr, t):
    k = env(t, T(16.0), T(21.3))
    if k <= 0: return
    for i, (w_, a) in enumerate([("HI!", 16.1), ("HELLO!", 16.8)]):
        pop(fr, chip(w_, C_MOR, INK, 74, 44, 30), 330 + i * 420, 360, t, T(a), k)
    if t > T(17.4): put(fr, txt("oi · olá", MF("ExtraBold", 44), (255, 230, 150), 3), 540, 470, env(t, T(17.4), T(21.3)))
    if t > T(18.9):
        bub = Image.new("RGBA", (640, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(bub); d.rounded_rectangle((0, 0, 639, 130), 40, fill=WHITE + (255,)); d.polygon([(90, 128), (140, 128), (80, 150)], fill=WHITE + (255,))
        d.text((320, 66), "How are you?", font=MF("ExtraBold", 58), fill=INK + (255,), anchor="mm"); put(fr, bub, 470, 660, env(t, T(18.9), T(21.3)), 0.6 + 0.4 * bo((t - T(18.9)) / 0.35))
    if t > T(19.9):
        bub = Image.new("RGBA", (700, 150), (0, 0, 0, 0)); d = ImageDraw.Draw(bub); d.rounded_rectangle((0, 0, 699, 130), 40, fill=C_ARE + (255,)); d.polygon([(560, 128), (610, 128), (620, 150)], fill=C_ARE + (255,))
        d.text((350, 66), "I'm fine, thanks!", font=MF("ExtraBold", 58), fill=WHITE + (255,), anchor="mm"); put(fr, bub, 600, 880, env(t, T(19.9), T(21.3)), 0.6 + 0.4 * bo((t - T(19.9)) / 0.35))
        put(fr, emoji("🙂", 90), 540, 1060, env(t, T(20.1), T(21.3)))
def quizcard(fr, t, a, b, qz, label, lines, em, opts, expl, ecol):
    k = env(t, a, b); c0, rv = qz
    if k <= 0: return
    put(fr, chip(label, YEL, INK, 60), 540, 290, k, 0.7 + 0.3 * bo((t - a) / 0.4))
    for i, l in enumerate(lines): put(fr, txt(l, MF("ExtraBold", 62), WHITE, 4), 540, 430 + i * 100, k)
    put(fr, emoji(em, 90), 540, 430 + len(lines) * 100 + 10, k)
    for i, (s_, ok, ta) in enumerate(opts):
        if t < ta: continue
        y = 760 + i * 150; card = Image.new("RGBA", (800, 124), (0, 0, 0, 0)); d = ImageDraw.Draw(card); rvd = t >= rv
        fill = (GREEN if ok else (90, 104, 136)) if rvd else WHITE; tc = WHITE if rvd else INK
        d.rounded_rectangle((0, 0, 799, 123), 30, fill=fill + (255,), outline=(YEL if not rvd else fill) + (255,), width=5)
        d.ellipse((20, 20, 104, 104), fill=(INK if not rvd else WHITE) + (255,)); d.text((62, 63), "AB"[i], font=MF("ExtraBold", 44), fill=(WHITE if not rvd else fill) + (255,), anchor="mm")
        d.text((450, 63), s_, font=MF("ExtraBold", 52), fill=tc + (255,), anchor="mm")
        sc = 0.6 + 0.4 * bo((t - ta) / 0.35, 1.8)
        if rvd and ok: sc *= 1 + 0.06 * bo((t - rv) / 0.3, 3) - 0.06 + 0.02 * math.sin(t * 6)
        sput(fr, card, 540, y, k * (0.55 if rvd and not ok else 1), sc)
        if rvd: put(fr, emoji("✅" if ok else "❌", 76), 975, y, k, 0.5 + 0.5 * bo((t - rv) / 0.3, 2))
    if c0 <= t < rv: ring(fr, t, c0, 1100)
    if t >= rv + 0.3: put(fr, chip(expl, ecol, WHITE if ecol != C_MOR else INK, 44), 540, 1100, env(t, rv + 0.3, b), 0.7 + 0.3 * bo((t - rv - 0.3) / 0.3))
def quiz(fr, t):
    quizcard(fr, t, T(21.3), T(28.0), QZ, "QUIZ 1", ["It's eight", "in the morning."], "⏰", [("GOOD MORNING", True, T(23.8)), ("GOOD EVENING", False, T(24.5))], "MANHÃ = MORNING", C_MOR)
    quizcard(fr, t, T(28.0), T(34.8), QZ2, "QUIZ 2", ["You are going", "to bed."], "🛏️", [("GOOD EVENING", False, T(30.4)), ("GOOD NIGHT", True, T(31.0))], "DORMIR = GOOD NIGHT", C_NIG)
def challenge(fr, t):
    k = env(t, T(34.8), TOTAL, 0.3, 0.01)
    if k <= 0: return
    put(fr, emoji("🏆", 170), 540, 400, k, 0.6 + 0.4 * bo((t - T(34.8)) / 0.4))
    put(fr, txt("ACERTOU OS 2?", ANTON(120), YEL, 7), 540, 600, k, 0.9 + 0.1 * bo((t - T(34.9)) / 0.4))
    put(fr, chip("COMENTA SE VOCÊ ACERTOU", RED_B, WHITE, 44), 540, 780, k, (0.6 + 0.4 * bo((t - T(34.9)) / 0.35, 2.2)) * (1 + 0.03 * math.sin(t * 6)))
    put(fr, emoji("👇", 64), 540, 860 + 6 * math.sin(t * 6), k)
    if t > T(36.3): put(fr, chip("SIGA @teachereliezio", WHITE, INK, 42), 540, 960, k, (0.6 + 0.4 * bo((t - T(36.3)) / 0.35, 2.2)) * (1 + 0.04 * math.sin(t * 5)))
    if t > T(37.2): put(fr, chip("SALVA PRA REVISAR DEPOIS", YEL, INK, 36), 540, 1060, k, 0.6 + 0.4 * bo((t - T(37.2)) / 0.35, 2.2))
def captions(fr, t):
    for p in PAIRS:
        if not (p["en"][1] - 0.05 <= t < p["t1"]): continue
        a, b = p["en"][1], p["en"][2]; kin = eo((t - a) / 0.25); y = 1300
        neutral = p["en"][3].startswith(("Quiz", "Challenge"))
        if neutral: HLW_SAVE = dict(HLW); HLW.clear()
        im = karaoke(p["en"][3], a, b, t, MF("ExtraBold", 54) if p["en"][0] == "en" else MF("Bold", 48), 960, WHITE if p["en"][0] == "en" else (255, 230, 150), hl=p["en"][0] == "en")
        if neutral: HLW.update(HLW_SAVE)
        put(fr, im, 540, y, kin, 0.92 + 0.08 * kin)
        if p["pt"] and t >= p["pt"][1] - 0.05:
            ip = karaoke(p["pt"][3], p["pt"][1], p["pt"][2], t, MF("Bold", 40), 940, (255, 230, 150), hl=False)
            put(fr, ip, 540, y + im.height / 2 + 46, eo((t - p["pt"][1]) / 0.25))
        return
def progress(fr, t):
    d = ImageDraw.Draw(fr); d.rounded_rectangle((60, 1880, 1020, 1892), 6, fill=(60, 84, 128, 255)); d.rounded_rectangle((60, 1880, 60 + 960 * clamp(t / TOTAL), 1892), 6, fill=YEL + (255,))
def frame_at(t):
    fr = BG.copy(); hook(fr, t); day(fr, t); hi(fr, t); quiz(fr, t); challenge(fr, t)
    if t < VO_LEN: captions(fr, t)
    avatar(fr, min(t, VO_LEN - 0.01)); progress(fr, t); return fr.convert("RGB")
def capa(out):
    fr = BG.copy(); put(fr, txt("GREETINGS", ANTON(180), YEL, 8), 540, 340)
    for i, (em, en_, pt, c, _) in enumerate(DAY):
        y = 560 + i * 150; put(fr, emoji(em, 90), 220, y); put(fr, txt(en_, ANTON(76), WHITE, 5), 610, y)
    put(fr, chip("QUIZ COM CONTADOR", C_AM, WHITE, 46), 540, 1200); put(fr, chip("INGLÊS RÁPIDO · A1", YEL, INK, 46), 540, 1320)
    avatar(fr, 0.0); fr.convert("RGB").save(out, quality=95)
def load_amp():
    global AMP
    tmp = f"{V}/vo16_{os.getpid()}.wav"   # um arquivo por processo: as 4 partes rodam juntas
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{V}/vo.mp3", "-ar", "16000", "-ac", "1", tmp], check=True)
    w = wave.open(tmp); os.remove(tmp) if False else None; a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    hop = 160; n = len(a) // hop; e = np.sqrt((a[:n * hop].reshape(n, hop) ** 2).mean(1)); e = np.clip(e / (np.percentile(e, 95) + 1e-6), 0, 1.2)
    sm = np.zeros_like(e); z = 0
    for i, v in enumerate(e): z = max(v, z * 0.86); sm[i] = z
    AMP = np.clip(sm, 0, 1)
def audio(vout):
    SR = 48000; n = int(TOTAL * SR)
    def readw(p):
        w = wave.open(p); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; return x.reshape(-1, w.getnchannels())
    def writew(p, x):
        w = wave.open(p, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{V}/vo.mp3", "-ar", "48000", "-ac", "2", f"{V}/vo48.wav"], check=True)
    vo = readw(f"{V}/vo48.wav"); vt = np.zeros((n, 2), np.float32); vt[:min(len(vo), n)] = vo[:n]
    bed = readw(f"{S}/v49/bed.wav"); xf = int(1.5 * SR); loop = bed.copy()
    while len(loop) < n:
        rr = np.linspace(0, 1, xf)[:, None]; loop[-xf:] = loop[-xf:] * (1 - rr) + bed[:xf] * rr; loop = np.concatenate([loop, bed[xf:]])
    tl = np.arange(n) / SR; gain = 0.07 * np.clip(tl / 0.5, 0, 1) * np.clip(1 - (tl - (TOTAL - 1.2)) / 1.1, 0, 1)
    for q_ in (QZ, QZ2): gain *= 1 - 0.5 * np.clip((tl - q_[0] + 0.3) / 0.3, 0, 1) * np.clip((q_[1] + 0.4 - tl) / 0.3, 0, 1)
    writew(f"{V}/voice.wav", vt); writew(f"{V}/song.wav", loop[:n] * gain[:, None])
    ding = readw(f"{S}/v81/ding.wav"); c0, rv = QZ
    ev = [(0.1, sfx.whoosh(0.4), 0.15)] + [(f(a) - 0.15, sfx.whoosh(0.4), 0.12) for a in (4.9, 16.0, 21.3, 28.0, 34.8)]
    ev += [(f(a), sfx.click(seed=i), 0.16) for i, a in enumerate((5.02, 6.9, 9.14, 12.17, 16.1, 16.8, 18.9, 19.9, 23.8, 24.5, 30.4, 31.0))]
    for q_ in (QZ, QZ2): ev += [(q_[0] + k_, sfx.click(seed=30 + k_), 0.3) for k_ in range(5)] + [(q_[1], ding, 0.45)]
    ev += [(f(34.9), sfx.thud(0.35), 0.18), (f(36.3), sfx.thud(0.35), 0.18)]
    sfx.build(ev, TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=70,acompressor=threshold=0.1:ratio=2.2:attack=8:release=200:makeup=1.4,asplit=2[vox][k2];[2:a]volume=0.8[sf];[3:a]volume=1.0[sg];"
                    "[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][sgd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.89:level=false[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
def main():
    load_amp()
    if MODE == "capa": capa(OUTFILE); return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(x).resize((360, 640), Image.LANCZOS) for x in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    NF = int(round(TOTAL * FPS))
    if MODE.startswith("part"):
        i, nparts = map(int, MODE.split(":")[1:]); a, b = NF * i // nparts, NF * (i + 1) // nparts
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", OUTFILE], stdin=subprocess.PIPE)
        for k in range(a, b): enc.stdin.write(frame_at(k / FPS).tobytes())
        enc.stdin.close(); enc.wait(); print("part done", i); return
    if MODE == "mux": audio(f"{V}/video.mp4"); print("done"); return
main()
