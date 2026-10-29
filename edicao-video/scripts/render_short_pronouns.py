"""Short 9:16 (1080x1920): Pronomes (subject pronouns), versão sem desafio para o próximo vídeo (semana 1, básico). Narração bilíngue gerada pelo conector do
ElevenLabs (voz do Eliezio, v4), com o silêncio do contador do quiz aberto entre "He or she?" e "She!". Abertura fixa "Hello! Today",
resposta do desafio anterior (HAD), os 7 pronomes, he/she, it, quiz (SHE) e desafio final para os comentários."""
import sys, os, math, re, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.path.insert(0, f"{S}/work")
import sfx
V = f"{S}/v91"; FD = f"{S}/fontdl"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H, FPS = 1080, 1920, 30
# sem desafio para o próximo vídeo: corta a resposta do desafio anterior (6,10-11,55) e o desafio final vira um 2º quiz com resposta
CUT = (6.10, 11.55)
PINS, GAP = [37.03, 46.00], 5.6   # contadores: entre "He or she?" (36,85) e "She!" (37,22); depois de "He, she or it?" (45,83), antes de "Responde" (46,18)
PIN = PINS[0]
def f(t):
    cut = (CUT[1] - CUT[0]) if t >= CUT[1] else max(0.0, t - CUT[0])
    return t - cut + GAP * sum(1 for p in PINS if p < t)
VO_LEN = f(49.55); TOTAL = VO_LEN + 1.2
NAVY = (12, 28, 58); INK = (16, 22, 36); WHITE = (255, 255, 255); YEL = (255, 214, 64); YEL_D = (64, 48, 0)
C_AM = (236, 84, 84); C_IS = (64, 150, 255); C_ARE = (52, 190, 110); C_HE = (64, 150, 255); C_SHE = (236, 84, 140); C_IT = (52, 190, 110); GREEN = (46, 184, 92); C_ING = (255, 214, 64); MUTED = (180, 196, 224); RED_B = (220, 40, 40)
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
SEG = [("en", 0.05, 2.52, "Hello! Today: pronouns."), ("pt", 2.91, 5.89, "Você sabe quando usar he, she e it?"),
       ("en", 11.75, 15.64, "I, you, he, she, it, we, they."), ("pt", 16.06, 21.67, "Eu, você, ele, ela, it para coisas e animais, nós e eles."),
       ("en", 22.01, 25.12, "He is for a man. She is for a woman."), ("en", 25.53, 28.96, "It is for things and animals. The dog? It!"),
       ("pt", 29.35, 31.26, "It é para coisas e animais."),
       ("en", 31.65, 36.85, "Quiz! My mother is a teacher. ___ is nice. He or she?"), ("pt", 37.22, 39.83, "She! Mãe é mulher, então she."),
       ("en", 40.27, 45.83, "Challenge: The car is red. ___ is new. He, she or it?"), ("pt", 46.18, 49.32, "Responde nos comentários, me segue e salva pra revisar!")]
SEG = [(lg, f(a), f(b), tx) for lg, a, b, tx in SEG]
PAIRS = []
for s_ in SEG:
    if s_[0] == "en" or not PAIRS or PAIRS[-1]["pt"] is not None: PAIRS.append(dict(en=s_, pt=None))
    else: PAIRS[-1]["pt"] = s_
for i, p in enumerate(PAIRS): p["t1"] = PAIRS[i + 1]["en"][1] - 0.1 if i + 1 < len(PAIRS) else TOTAL
HLW = {"he": C_HE, "she": C_SHE, "it": C_IT, "had": C_HE}
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
EXPR = [(0, 1), (2.9, 2), (f(11.6), 1), (f(PINS[0]) + 0.1, 2), (f(PINS[0]) + 5.3, 7), (f(38.6), 1), (f(40.3), 2), (f(PINS[1]) + 5.3, 7), (f(46.4), 8), (f(47.5), 1)]
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
QZ = (f(PINS[0]) + 0.3, f(PINS[0]) + 5.3)   # 1º quiz: começo do contador e revelação
QZ2 = (f(PINS[1]) + 0.3, f(PINS[1]) + 5.3)  # 2º quiz (o antigo desafio)
PRON = [("I", "🙋", "eu", 11.8), ("YOU", "🫵", "você", 12.4), ("HE", "👨", "ele", 13.0), ("SHE", "👩", "ela", 13.5), ("IT", "🐶", "coisa / animal", 14.2), ("WE", "👫", "nós", 14.7), ("THEY", "👥", "eles / elas", 15.2)]
PC = {"HE": C_HE, "SHE": C_SHE, "IT": C_IT}
def T(a): return f(a)
def hook(fr, t):
    k = env(t, 0.0, T(6.2))
    if k <= 0: return
    put(fr, txt("PRONOUNS", ANTON(170), YEL, 8), 540, 360, k, 0.9 + 0.1 * bo(t / 0.4))
    pop(fr, chip("BÁSICO · A1", C_ARE, WHITE, 40), 540, 530, t, 0.8, k)
    for i, (w_, em, a) in enumerate([("HE", "👨", 3.2), ("SHE", "👩", 3.7), ("IT", "🐶", 4.3)]):
        if t < a: continue
        x = 240 + i * 300; u = bo((t - a) / 0.35, 2.2)
        put(fr, emoji(em, 110), x, 740, k, 0.6 + 0.4 * u); put(fr, chip(w_, PC[w_], WHITE, 60, 36, 26), x, 880, k, 0.6 + 0.4 * u)
    if t > 4.8: put(fr, txt("?", ANTON(130), YEL, 6), 540, 1040, env(t, 4.8, T(6.2)), 1 + 0.08 * math.sin(t * 7))
def prev(fr, t):
    k = env(t, T(6.2), T(11.6))
    if k <= 0: return
    put(fr, chip("DESAFIO ANTERIOR", (40, 40, 50), YEL, 44), 540, 300, k, 0.7 + 0.3 * bo((t - 6.2) / 0.4))
    put(fr, txt("If I", MF("ExtraBold", 72), WHITE, 4), 540, 470, k)
    g = clamp((t - T(9.6)) / 0.3)
    if g <= 0: put(fr, txt("___", MF("ExtraBold", 72), WHITE, 4), 540, 580, k)
    else: put(fr, chip("HAD", C_HE, WHITE, 70, 40, 26), 540, 580, k, 0.6 + 0.4 * bo((t - T(9.6)) / 0.35, 2.4))
    put(fr, txt("known, I would have", MF("ExtraBold", 60), WHITE, 4), 540, 700, k); put(fr, txt("called you.", MF("ExtraBold", 60), WHITE, 4), 540, 790, k)
    if t > T(10.0): put(fr, emoji("✅", 100), 540, 950, env(t, T(10.0), T(11.6)), 0.5 + 0.5 * bo((t - T(10.0)) / 0.3, 2.2)); put(fr, chip("RESPOSTA CERTA", GREEN, WHITE, 40), 540, 1070, env(t, T(10.1), T(11.6)))
def plist(fr, t):
    k = env(t, T(11.6), T(21.85))
    if k <= 0: return
    put(fr, chip("SUBJECT PRONOUNS", YEL, INK, 44), 540, 290, k, 0.7 + 0.3 * bo((t - T(11.6)) / 0.4))
    for i, (w_, em, pt, a) in enumerate(PRON):
        if t < T(a): continue
        col_, row = i % 4, i // 4; x = 540 + (col_ - 1.5) * 232 + (116 if row else 0); y = 520 + row * 330
        u = bo((t - T(a)) / 0.3, 2); card = Image.new("RGBA", (214, 290), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
        c = PC.get(w_, (70, 100, 160)); d.rounded_rectangle((0, 0, 213, 289), 26, fill=(14, 32, 64, 240), outline=c + (255,), width=4)
        card.alpha_composite(emoji(em, 90), (int(107 - emoji(em, 90).width / 2), 22)); d.text((107, 160), w_, font=ANTON(64), fill=WHITE + (255,), anchor="mm")
        if t > T(16.0): d.text((107, 238), pt, font=MF("ExtraBold", 26 if len(pt) < 9 else 20), fill=(255, 230, 150, int(255 * clamp((t - T(16.0) - i * 0.5) / 0.3))), anchor="mm")
        put(fr, card, x, y, k, 0.6 + 0.4 * u)
def heshe(fr, t):
    k = env(t, T(21.85), T(25.45))
    if k <= 0: return
    for i, (em, w_, lab, a) in enumerate([("👨", "HE", "MAN · homem", 22.0), ("👩", "SHE", "WOMAN · mulher", 23.7)]):
        if t < T(a): continue
        y = 470 + i * 380; u = bo((t - T(a)) / 0.35, 2)
        put(fr, emoji(em, 170), 300, y, k, 0.6 + 0.4 * u); put(fr, chip(w_, PC[w_], WHITE, 90, 44, 30), 690, y - 50, k, 0.6 + 0.4 * u)
        put(fr, txt(lab, MF("ExtraBold", 44), WHITE, 3), 690, y + 70, k)
def itscene(fr, t):
    k = env(t, T(25.45), T(31.5))
    if k <= 0: return
    put(fr, chip("IT", C_IT, WHITE, 100, 50, 34), 540, 360, k, 0.7 + 0.3 * bo((t - T(25.45)) / 0.4))
    for i, (em, lab, a) in enumerate([("📦", "COISAS", 25.9), ("🐶", "ANIMAIS", 26.8)]):
        if t < T(a): continue
        x = 330 + i * 420; u = bo((t - T(a)) / 0.35, 2)
        put(fr, emoji(em, 150), x, 620, k, 0.6 + 0.4 * u); put(fr, txt(lab, MF("ExtraBold", 44), WHITE, 3), x, 760, k)
    if t > T(27.7): put(fr, txt("The dog?", MF("ExtraBold", 70), WHITE, 4), 540, 920, env(t, T(27.7), T(31.5)))
    if t > T(28.55): put(fr, chip("IT!", C_IT, WHITE, 70, 40, 26), 540, 1050, env(t, T(28.55), T(31.5)), 0.6 + 0.4 * bo((t - T(28.55)) / 0.35, 2.4))
def quiz(fr, t):
    a, b = T(31.5), T(40.1); k = env(t, a, b); c0, rv = QZ
    if k <= 0: return
    put(fr, chip("QUIZ", YEL, INK, 60), 540, 290, k, 0.7 + 0.3 * bo((t - a) / 0.4))
    put(fr, txt("My mother is a teacher.", MF("ExtraBold", 60), WHITE, 4), 540, 430, k); put(fr, txt("___ is nice.", MF("ExtraBold", 60), WHITE, 4), 540, 530, k)
    put(fr, emoji("🏫", 80), 540, 630, k)   # sem 👩 para não entregar a resposta
    for i, (s_, ok) in enumerate([("HE", False), ("SHE", True)]):
        ta = T(35.95) + 0.3 * i
        if t < ta: continue
        y = 770 + i * 150; card = Image.new("RGBA", (760, 124), (0, 0, 0, 0)); d = ImageDraw.Draw(card); rvd = t >= rv
        fill = (GREEN if ok else (90, 104, 136)) if rvd else WHITE; tc = WHITE if rvd else INK
        d.rounded_rectangle((0, 0, 759, 123), 30, fill=fill + (255,), outline=(YEL if not rvd else fill) + (255,), width=5)
        d.ellipse((20, 20, 104, 104), fill=(INK if not rvd else WHITE) + (255,)); d.text((62, 63), "AB"[i], font=MF("ExtraBold", 44), fill=(WHITE if not rvd else fill) + (255,), anchor="mm")
        d.text((420, 63), s_, font=MF("ExtraBold", 56), fill=tc + (255,), anchor="mm")
        sc = 0.6 + 0.4 * bo((t - ta) / 0.35, 1.8)
        if rvd and ok: sc *= 1 + 0.06 * bo((t - rv) / 0.3, 3) - 0.06 + 0.02 * math.sin(t * 6)
        sput(fr, card, 540, y, k * (0.55 if rvd and not ok else 1), sc)
        if rvd: put(fr, emoji("✅" if ok else "❌", 76), 950, y, k, 0.5 + 0.5 * bo((t - rv) / 0.3, 2))
    if c0 <= t < rv:
        u = (t - c0) / 5.0; n_ = int(5.0 - (t - c0)) + 1; fz = (t - c0) % 1; R_ = 100
        lay = Image.new("RGBA", (300, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); col = YEL if n_ > 2 else C_AM
        d.ellipse((150 - R_, 150 - R_, 150 + R_, 150 + R_), fill=(8, 18, 40, 230)); d.ellipse((150 - R_, 150 - R_, 150 + R_, 150 + R_), outline=(60, 84, 128, 255), width=16)
        d.arc((150 - R_, 150 - R_, 150 + R_, 150 + R_), -90, -90 + 360 * (1 - u), fill=col + (255,), width=16)
        put(fr, lay, 540, 1100, k); put(fr, txt(str(n_), ANTON(115), col, 5), 540, 1100, k, 1 + 0.25 * (1 - eo(fz / 0.3)))
    if t >= rv + 0.3: put(fr, chip("MÃE = MULHER → SHE", C_SHE, WHITE, 42), 540, 1100, env(t, rv + 0.3, b), 0.7 + 0.3 * bo((t - rv - 0.3) / 0.3))
def ring(fr, t, c0, y):
    u = (t - c0) / 5.0; n_ = int(5.0 - (t - c0)) + 1; fz = (t - c0) % 1; R_ = 100
    lay = Image.new("RGBA", (300, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); col = YEL if n_ > 2 else C_AM
    d.ellipse((150 - R_, 150 - R_, 150 + R_, 150 + R_), fill=(8, 18, 40, 230)); d.ellipse((150 - R_, 150 - R_, 150 + R_, 150 + R_), outline=(60, 84, 128, 255), width=16)
    d.arc((150 - R_, 150 - R_, 150 + R_, 150 + R_), -90, -90 + 360 * (1 - u), fill=col + (255,), width=16)
    put(fr, lay, 540, y); put(fr, txt(str(n_), ANTON(115), col, 5), 540, y, 1, 1 + 0.25 * (1 - eo(fz / 0.3)))
def challenge(fr, t):
    k = env(t, T(40.1), TOTAL, 0.3, 0.01); c0, rv = QZ2
    if k <= 0: return
    put(fr, txt("CHALLENGE!", ANTON(130), YEL, 7), 540, 320, k, 0.9 + 0.1 * bo((t - T(40.1)) / 0.4))
    put(fr, emoji("🚗", 100), 540, 470, k)
    put(fr, txt("The car is red.", MF("ExtraBold", 66), WHITE, 4), 540, 600, k); put(fr, txt("___ is new.", MF("ExtraBold", 66), WHITE, 4), 540, 700, k)
    for i, (w_, a, ok) in enumerate([("HE", 44.3, False), ("SHE", 44.7, False), ("IT", 45.2, True)]):
        if t < T(a): continue
        rvd = t >= rv; c = (GREEN if ok else (70, 80, 100)) if rvd else (90, 104, 136)   # mesma cor até a revelação
        im = chip(w_, c, WHITE, 60, 38, 26); sc = 0.5 + 0.5 * bo((t - T(a)) / 0.35, 2.2)
        if rvd and ok: sc *= 1 + 0.08 * bo((t - rv) / 0.3, 3) - 0.08 + 0.03 * math.sin(t * 6)
        put(fr, im, 240 + i * 300, 850, k * (0.5 if rvd and not ok else 1), sc)
        if rvd: put(fr, emoji("✅" if ok else "❌", 56), 240 + i * 300, 770, k, 0.5 + 0.5 * bo((t - rv) / 0.3, 2))
    if c0 <= t < rv: ring(fr, t, c0, 1060)
    if t >= rv + 0.3: put(fr, chip("CARRO = COISA → IT", C_IT, WHITE, 42), 540, 990, env(t, rv + 0.3, TOTAL, 0.3, 0.01), 0.7 + 0.3 * bo((t - rv - 0.3) / 0.3))
    if t > T(46.4): put(fr, chip("COMENTA SE ACERTOU 👇" if False else "COMENTA SE VOCÊ ACERTOU", RED_B, WHITE, 40), 540, 1080, k, (0.6 + 0.4 * bo((t - T(46.4)) / 0.35, 2.2)) * (1 + 0.03 * math.sin(t * 6)))
    if t > T(47.4): put(fr, chip("SIGA @teachereliezio", WHITE, INK, 40), 540, 1160, k, (0.6 + 0.4 * bo((t - T(47.4)) / 0.35, 2.2)) * (1 + 0.04 * math.sin(t * 5)))
    if t > T(48.4): put(fr, chip("SALVA PRA REVISAR DEPOIS", YEL, INK, 34), 540, 1230, k, 0.6 + 0.4 * bo((t - T(48.4)) / 0.35, 2.2))
def captions(fr, t):
    for p in PAIRS:
        if not (p["en"][1] - 0.05 <= t < p["t1"]): continue
        a, b = p["en"][1], p["en"][2]; kin = eo((t - a) / 0.25)
        y = 1300 if p["en"][1] < T(40.1) else 1335
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
    fr = BG.copy(); hook(fr, t); plist(fr, t); heshe(fr, t); itscene(fr, t); quiz(fr, t); challenge(fr, t)
    if t < VO_LEN: captions(fr, t)
    avatar(fr, min(t, VO_LEN - 0.01)); progress(fr, t); return fr.convert("RGB")
def capa(out):
    fr = BG.copy(); put(fr, txt("PRONOUNS", ANTON(180), YEL, 8), 540, 360)
    for i, (w_, em) in enumerate([("HE", "👨"), ("SHE", "👩"), ("IT", "🐶")]):
        x = 240 + i * 300; put(fr, emoji(em, 130), x, 620); sput(fr, chip(w_, PC[w_], WHITE, 70, 40, 28).rotate((-6, 4, -3)[i], Image.BICUBIC, expand=True), x, 780)
    put(fr, txt("?", ANTON(140), YEL, 7), 540, 960); put(fr, chip("QUIZ COM CONTADOR", C_AM, WHITE, 46), 540, 1130); put(fr, chip("INGLÊS RÁPIDO · A1", YEL, INK, 46), 540, 1250)
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
    ev = [(0.1, sfx.whoosh(0.4), 0.15)] + [(f(a) - 0.15, sfx.whoosh(0.4), 0.12) for a in (11.6, 21.85, 25.45, 31.5, 40.1)]
    ev += [(f(a), sfx.click(seed=i), 0.16) for i, a in enumerate((3.2, 3.7, 4.3, 11.8, 12.4, 13.0, 13.5, 14.2, 14.7, 15.2, 22.0, 23.7, 25.9, 26.8, 35.95, 36.25, 44.3, 44.7, 45.2))]
    ev += [(f(28.55), sfx.thud(0.3), 0.18)]
    for q_ in (QZ, QZ2): ev += [(q_[0] + k_, sfx.click(seed=30 + k_), 0.3) for k_ in range(5)] + [(q_[1], ding, 0.45)]
    ev += [(f(46.4), sfx.thud(0.35), 0.18), (f(47.4), sfx.thud(0.35), 0.18)]
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
