"""Short 9:16 do Teacher Eliezio: números de 1 a 100 (thirteen × thirty, a força no TEEN e no TY, como juntar 21/45/99) e 2 quizzes
de escuta com contador de 3 s respondidos no vídeo. Voz do Eliezio pelo conector do ElevenLabs (v4); os 2 silêncios do contador já
estão abertos em aula_numeros/vo.mp3 (a original é vo_raw.mp3)."""
import sys, os, math, re, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.path.insert(0, f"{S}/work")
import sfx
V = f"{S}/aula_numeros"; FD = f"{S}/fontdl"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H, FPS = 1080, 1920, 30
PINS, GAP = [33.0, 36.8], 3.6   # "fifty" termina em 32,83 e "It's fifty" começa em 33,23; "fourteen" termina em 36,63 e "It's fourteen" em 37,00
def f(t): return t + GAP * sum(1 for p in PINS if p < t)
CD = 3.0
QZ = [(f(p) + 0.25, f(p) + 0.25 + CD) for p in PINS]
VO_LEN = f(41.17); TOTAL = VO_LEN + 0.45   # loop: acaba logo depois da voz
NAVY = (12, 28, 58); INK = (16, 22, 36); WHITE = (255, 255, 255); YEL = (255, 214, 64); YEL_D = (64, 48, 0)
C_AM = (236, 84, 84); C_IS = (64, 150, 255); C_ARE = (52, 190, 110); C_RUT = (64, 150, 255); C_NOW = (236, 84, 84); GREEN = (46, 184, 92); C_ING = (255, 214, 64); MUTED = (180, 196, 224); RED_B = (220, 40, 40)
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
SEG = [("en", 0.05, 3.52, "Hello! Today: numbers from one to one hundred."), ("en", 3.91, 7.47, "Thirteen or thirty? Many Brazilians mix them up."),
       ("pt", 7.73, 9.18, "Muita gente confunde!"), ("en", 9.58, 14.20, "Teen: the stress is at the end. Thirteen, fourteen, fifteen."),
       ("pt", 14.60, 16.73, "No teen, a força fica no final."), ("en", 17.10, 21.55, "Ty: the stress is at the beginning. Thirty, forty, fifty."),
       ("pt", 21.95, 24.00, "No ty, a força vem no começo."), ("en", 24.38, 28.35, "Twenty-one, forty-five, ninety-nine: just join the words."),
       ("pt", 28.57, 29.38, "É só juntar!"), ("en", 29.76, 32.83, "Quiz time! Listen and choose:"), ("en", 33.23, 34.00, "It's fifty!"),
       ("en", 34.43, 36.63, "Next one. Listen:"), ("en", 37.00, 37.88, "It's fourteen!"), ("en", 38.25, 41.17, "Comment if you got it right, follow and save to review!")]
SEG = [(lg, f(a), f(b), tx) for lg, a, b, tx in SEG]
PAIRS = []
for s_ in SEG:
    if s_[0] == "en" or not PAIRS or PAIRS[-1]["pt"] is not None: PAIRS.append(dict(en=s_, pt=None))
    else: PAIRS[-1]["pt"] = s_
for i, p in enumerate(PAIRS): p["t1"] = PAIRS[i + 1]["en"][1] - 0.1 if i + 1 < len(PAIRS) else TOTAL
C_TEEN = (64, 150, 255); C_TY = (236, 84, 84)
HLW = {"end": C_TEEN, "beginning": C_TY}
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
AV = [Image.open(f"{S}/v77/av3d_{k}.png").convert("RGBA").resize((360, 360), Image.LANCZOS) for k in range(1, 9)]
EXPR = [(0, 1), (3.9, 2), (5.9, 7), (9.5, 1), (29.7, 2), (QZ[0][1], 7), (f(34.4), 2), (QZ[1][1], 7), (f(38.2), 8), (f(39.4), 1)]
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
def boxword(w, f, fill):
    """palavra branca dentro de caixa colorida (forma comparativa)"""
    bb = f.getbbox(w); im = Image.new("RGBA", (bb[2] - bb[0] + 44, bb[3] - bb[1] + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), 22, fill=fill + (255,)); d.text((22 - bb[0], 20 - bb[1]), w, font=f, fill=WHITE + (255,)); return im
def pop(fr, im, x, y, t, a, k, shadow=True):
    if t < a: return
    (sput if shadow else put)(fr, im, x, y, k, 0.5 + 0.5 * bo((t - a) / 0.35, 2.2))
def ring(fr, t, c0, y):
    u = (t - c0) / CD; n_ = int(CD - (t - c0)) + 1; fz = (t - c0) % 1; R_ = 100
    lay = Image.new("RGBA", (300, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); col = YEL if n_ > 1 else C_AM
    d.ellipse((150 - R_, 150 - R_, 150 + R_, 150 + R_), fill=(8, 18, 40, 230)); d.ellipse((150 - R_, 150 - R_, 150 + R_, 150 + R_), outline=(60, 84, 128, 255), width=16)
    d.arc((150 - R_, 150 - R_, 150 + R_, 150 + R_), -90, -90 + 360 * (1 - u), fill=col + (255,), width=16)
    put(fr, lay, 540, y); put(fr, txt(str(n_), ANTON(115), col, 5), 540, y, 1, 1 + 0.25 * (1 - eo(fz / 0.3)))
# ---------------------------------------------------------------- cenas
def T(a): return f(a)
def stressword(pre, hi, post, col, size=120):
    """palavra com a sílaba forte numa caixa colorida: thir|TEEN, THIR|ty"""
    fnt = ANTON(size); parts = [(pre, None), (hi, col), (post, None)]; ws = [fnt.getlength(p) for p, _ in parts]; pad = 18
    im = Image.new("RGBA", (int(sum(ws) + 4 * pad + 40), int(size * 1.5)), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 20
    for (p, c), w_ in zip(parts, ws):
        if not p: continue
        if c: d.rounded_rectangle((x, 10, x + w_ + 2 * pad, im.height - 10), 20, fill=c + (255,)); d.text((x + pad, im.height / 2), p, font=fnt, fill=WHITE + (255,), anchor="lm"); x += w_ + 2 * pad
        else: d.text((x, im.height / 2), p, font=fnt, fill=WHITE + (255,), anchor="lm", stroke_width=5, stroke_fill=INK + (255,)); x += w_
    return im.crop((0, 0, int(x + 20), im.height))
def numcard(n, col):
    im = Image.new("RGBA", (170, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.rounded_rectangle((0, 0, 169, 129), 26, fill=(10, 24, 52, 240), outline=col + (255,), width=5)
    d.text((85, 66), n, font=ANTON(80), fill=col + (255,), anchor="mm"); return im
def hook(fr, t):
    k = env(t, 0.0, T(3.9))
    if k <= 0: return
    put(fr, chip("BÁSICO · A1", C_ARE, WHITE, 38), 540, 300, k, 0.8 + 0.2 * bo(t / 0.4))
    put(fr, txt("NUMBERS", ANTON(170), WHITE, 8), 540, 520, k, 0.85 + 0.15 * bo((t - 0.9) / 0.4) if t > 0.9 else 0.85)
    if t > 2.0: put(fr, txt("1 → 100", ANTON(150), YEL, 7), 540, 720, env(t, 2.0, T(3.9)), 0.7 + 0.3 * bo((t - 2.0) / 0.35))
def confusao(fr, t):
    k = env(t, T(3.9), T(9.5))
    if k <= 0: return
    pop(fr, numcard("13", WHITE).resize((300, 230)), 330, 520, t, T(3.95), k); pop(fr, numcard("30", WHITE).resize((300, 230)), 750, 520, t, T(4.9), k)
    if t > T(4.3): put(fr, txt("ou", MF("ExtraBold", 60), MUTED), 540, 520, k)
    put(fr, txt("THIRTEEN × THIRTY", ANTON(96), YEL, 6), 540, 760, k * clamp((t - T(4.0)) / 0.3))
    if t > T(6.4): put(fr, emoji("🤯", 150), 540, 960 + 8 * math.sin(t * 5), k, 0.5 + 0.5 * bo((t - T(6.4)) / 0.35, 2))
def teen(fr, t):
    k = env(t, T(9.5), T(17.0))
    if k <= 0: return
    put(fr, chip("TEEN = FORÇA NO FINAL", C_TEEN, WHITE, 46), 540, 300, k, 0.7 + 0.3 * bo((t - T(9.5)) / 0.35))
    for i, (pre, n, ta) in enumerate([("thir", "13", 12.05), ("four", "14", 12.75), ("fif", "15", 13.45)]):
        if t < T(ta): continue
        y = 500 + i * 190; sk = 0.6 + 0.4 * bo((t - T(ta)) / 0.35, 2)
        sput(fr, numcard(n, C_TEEN), 230, y, k, sk); sput(fr, stressword(pre, "TEEN", "", C_TEEN, 104), 640, y, k, sk)
def ty(fr, t):
    k = env(t, T(17.0), T(24.3))
    if k <= 0: return
    put(fr, chip("TY = FORÇA NO COMEÇO", C_TY, WHITE, 46), 540, 300, k, 0.7 + 0.3 * bo((t - T(17.0)) / 0.35))
    for i, (hi, post, n, ta) in enumerate([("THIR", "ty", "30", 19.75), ("FOR", "ty", "40", 20.35), ("FIF", "ty", "50", 20.95)]):
        if t < T(ta): continue
        y = 500 + i * 190; sk = 0.6 + 0.4 * bo((t - T(ta)) / 0.35, 2)
        sput(fr, numcard(n, C_TY), 230, y, k, sk); sput(fr, stressword("", hi, post, C_TY, 104), 640, y, k, sk)
def juntar(fr, t):
    k = env(t, T(24.3), T(29.7))
    if k <= 0: return
    for i, (n, a_, b_, ta) in enumerate([("21", "twenty", "one", 24.4), ("45", "forty", "five", 25.25), ("99", "ninety", "nine", 26.05)]):
        if t < T(ta): continue
        y = 360 + i * 190; sk = 0.6 + 0.4 * bo((t - T(ta)) / 0.35, 2)
        sput(fr, numcard(n, YEL), 230, y, k, sk); sput(fr, txt(f"{a_}-{b_}", ANTON(96), WHITE, 6), 640, y, k, sk)
    if t > T(27.2): put(fr, chip("É SÓ JUNTAR: TWENTY + ONE", YEL, INK, 42), 540, 960, env(t, T(27.2), T(29.7)), 0.7 + 0.3 * bo((t - T(27.2)) / 0.35))
def quiz(fr, t):
    a, b = T(29.7), T(38.2); k = env(t, a, b)
    if k <= 0: return
    put(fr, chip("QUIZ", YEL, INK, 60), 540, 290, k, 0.7 + 0.3 * bo((t - a) / 0.4))
    qi = 0 if t < T(34.4) else 1; c0, rv = QZ[qi]
    opts = [("FIFTEEN", False), ("FIFTY", True)] if qi == 0 else [("FOURTEEN", True), ("FORTY", False)]
    qa = T(30.8) if qi == 0 else T(34.43); qk = k * (env(t, qa - 0.05, T(34.35), 0.25, 0.2) if qi == 0 else 1)
    put(fr, txt(f"PERGUNTA {qi + 1} DE 2", MF("ExtraBold", 40), MUTED), 540, 400, qk)
    if t < rv: put(fr, emoji("🎧", 130), 540, 540, qk, (0.6 + 0.4 * bo((t - qa) / 0.35, 2)) * (1 + 0.05 * math.sin(t * 7)))
    for i, (s_, ok) in enumerate(opts):
        ta = qa + 0.25 + i * 0.3
        if t < ta: continue
        y = 720 + i * 150; card = Image.new("RGBA", (760, 124), (0, 0, 0, 0)); d = ImageDraw.Draw(card); rvd = t >= rv
        fill = (GREEN if ok else (90, 104, 136)) if rvd else WHITE; tc = WHITE if rvd else INK
        d.rounded_rectangle((0, 0, 759, 123), 30, fill=fill + (255,), outline=(YEL if not rvd else fill) + (255,), width=5)
        d.ellipse((20, 20, 104, 104), fill=(INK if not rvd else WHITE) + (255,)); d.text((62, 63), "AB"[i], font=MF("ExtraBold", 44), fill=(WHITE if not rvd else fill) + (255,), anchor="mm")
        d.text((420, 63), s_, font=MF("ExtraBold", 56), fill=tc + (255,), anchor="mm")
        sc = 0.6 + 0.4 * bo((t - ta) / 0.35, 1.8)
        if rvd and ok: sc *= 1 + 0.06 * bo((t - rv) / 0.3, 3) - 0.06 + 0.02 * math.sin(t * 6)
        sput(fr, card, 540, y, qk * (0.55 if rvd and not ok else 1), sc)
        if rvd: put(fr, emoji("✅" if ok else "❌", 76), 955, y, qk, 0.5 + 0.5 * bo((t - rv) / 0.3, 2))
    if c0 <= t < rv: ring(fr, t, c0, 1060)
    if t >= rv + 0.2:
        tip = stressword("", "FIF", "ty", C_TY, 84) if qi == 0 else stressword("four", "TEEN", "", C_TEEN, 84)
        put(fr, tip, 540, 1060, qk, 0.7 + 0.3 * bo((t - rv - 0.2) / 0.3))
def challenge(fr, t):
    k = env(t, T(38.2), TOTAL, 0.3, 0.01)
    if k <= 0: return
    put(fr, txt("ACERTOU?", ANTON(140), YEL, 7), 540, 400, k, 0.9 + 0.1 * bo((t - T(38.2)) / 0.4))
    put(fr, chip("COMENTA AQUI", RED_B, WHITE, 50), 540, 590, k, (0.6 + 0.4 * bo((t - T(38.3)) / 0.35, 2.2)) * (1 + 0.03 * math.sin(t * 6)))
    put(fr, emoji("👇", 64), 540, 680 + 6 * math.sin(t * 6), k)
    if t > T(39.6): put(fr, chip("SIGA @teachereliezio", WHITE, INK, 44), 540, 790, k, (0.6 + 0.4 * bo((t - T(39.6)) / 0.35, 2.2)) * (1 + 0.04 * math.sin(t * 5)))
    if t > T(40.3): put(fr, chip("SALVA PRA REVISAR", YEL, INK, 44), 540, 900, k, 0.6 + 0.4 * bo((t - T(40.3)) / 0.35, 2.2))
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
    fr = BG.copy(); hook(fr, t); confusao(fr, t); teen(fr, t); ty(fr, t); juntar(fr, t); quiz(fr, t); challenge(fr, t)
    if t < VO_LEN: captions(fr, t)
    avatar(fr, min(t, VO_LEN - 0.01)); progress(fr, t); return fr.convert("RGB")
def capa(out):
    fr = BG.copy(); put(fr, chip("BÁSICO · A1", C_ARE, WHITE, 40), 540, 250)
    put(fr, numcard("13", WHITE).resize((320, 245)), 320, 480); put(fr, numcard("30", WHITE).resize((320, 245)), 760, 480); put(fr, txt("ou", MF("ExtraBold", 64), MUTED), 540, 480)
    put(fr, txt("VOCÊ CONFUNDE?", ANTON(130), YEL, 7), 540, 720)
    put(fr, stressword("thir", "TEEN", "", C_TEEN, 100), 540, 900); put(fr, stressword("", "THIR", "ty", C_TY, 100), 540, 1060)
    put(fr, chip("QUIZ COM RESPOSTA", C_AM, WHITE, 46), 540, 1240)
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
    for q_ in QZ: gain *= 1 - 0.5 * np.clip((tl - q_[0] + 0.3) / 0.3, 0, 1) * np.clip((q_[1] + 0.4 - tl) / 0.3, 0, 1)
    writew(f"{V}/voice.wav", vt); writew(f"{V}/song.wav", loop[:n] * gain[:, None])
    ding = readw(f"{S}/v81/ding.wav")
    ev = [(f(a) - 0.15, sfx.whoosh(0.4), 0.12) for a in (3.9, 9.5, 17.0, 24.3, 29.7, 38.2)]
    ev += [(f(a), sfx.click(seed=i), 0.16) for i, a in enumerate((3.95, 4.9, 12.05, 12.75, 13.45, 19.75, 20.35, 20.95, 24.4, 25.25, 26.05))]
    for q_ in QZ: ev += [(q_[0] + k_, sfx.click(seed=30 + k_), 0.3) for k_ in range(3)] + [(q_[1], ding, 0.45)]
    ev += [(f(38.3), sfx.thud(0.35), 0.18)]
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
