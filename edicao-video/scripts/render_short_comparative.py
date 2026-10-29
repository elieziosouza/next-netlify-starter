"""Short 9:16 (1080x1920): Comparative Adjectives em ~45 s. Narração bilíngue (ElevenLabs, voz do Eliezio). ER entrando no fim do
adjetivo curto, MORE caindo na frente do longo, irregulares good/better e bad/worse e o desafio São Paulo x Santos.
Legenda grande no meio (inglês + português) e avatar 3D do professor embaixo, reagindo."""
import sys, math, re, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.path.insert(0, f"{S}/work")
import sfx
V = f"{S}/v83"; FD = f"{S}/fontdl"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H, FPS = 1080, 1920, 30
VO_LEN = 44.2; TOTAL = 45.4
NAVY = (12, 28, 58); INK = (16, 22, 36); WHITE = (255, 255, 255); YEL = (255, 214, 64); YEL_D = (64, 48, 0)
C_ER = (64, 150, 255); C_MORE = (52, 190, 110); C_IRR = (236, 84, 84); MUTED = (180, 196, 224)
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
# ---------------------------------------------------------------- falas
SEG = [("en", 0.09, 3.21, "Hello! Today: comparative adjectives."), ("pt", 3.48, 6.06, "Hoje: como comparar coisas em inglês."),
       ("en", 6.42, 11.87, "Short adjectives get E R. Tall, taller. Cheap, cheaper."), ("pt", 12.22, 14.54, "Adjetivo curto ganha E R no final."),
       ("en", 14.90, 16.65, "My brother is taller than me."), ("pt", 16.95, 18.47, "Meu irmão é mais alto que eu."),
       ("en", 18.84, 23.14, "Long adjectives use more. Expensive, more expensive."), ("pt", 23.42, 25.64, "Adjetivo longo usa more antes."),
       ("en", 25.91, 28.20, "This car is more expensive than that one."), ("pt", 28.54, 30.31, "Este carro é mais caro que aquele."),
       ("en", 30.65, 34.34, "Watch out: good, better. Bad, worse."), ("pt", 34.65, 38.18, "Cuidado: bom vira better, ruim vira worse."),
       ("en", 38.49, 43.08, "Now you: São Paulo is... than Santos. Big or bigger?"), ("pt", 43.35, 44.01, "Comenta aqui!")]
PAIRS = []
for s in SEG:
    if s[0] == "en": PAIRS.append(dict(en=s, pt=None))
    else: PAIRS[-1]["pt"] = s
for i, p in enumerate(PAIRS): p["t1"] = PAIRS[i + 1]["en"][1] - 0.1 if i + 1 < len(PAIRS) else TOTAL
HLW = {"taller": C_ER, "cheaper": C_ER, "bigger": C_ER, "more": C_MORE, "better": C_IRR, "worse": C_IRR}
def karaoke(t_, a, b, t, f, maxw, col=WHITE, hl=True):
    """frase com a palavra falada acendendo (amarelo) e a forma comparativa na cor da regra"""
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
            if c: d.rounded_rectangle((x - 8, y + 4, x + wl + 8, y + f.size * 1.16), 12, fill=c + (255,)); fc = WHITE
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
EXPR = [(0, 1), (30.6, 7), (34.6, 1), (38.4, 2), (42.0, 8), (43.3, 1)]
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
# ---------------------------------------------------------------- cenas (área de cima: y 170-1150)
def hook(fr, t):
    k = env(t, 0.0, 6.3)
    if k <= 0: return
    put(fr, txt("COMPARATIVE", ANTON(130), WHITE, 6), 540, 300, k, 0.9 + 0.1 * bo(t / 0.4))
    put(fr, txt("ADJECTIVES", ANTON(130), YEL, 6), 540, 450, k, 0.9 + 0.1 * bo((t - 0.2) / 0.4))
    for i, (w_, c, a) in enumerate([("TALLER", C_ER, 1.7), ("MORE", C_MORE, 2.1), ("BETTER", C_IRR, 2.5)]):
        im = chip(w_, c, WHITE, 52, 30, 24).rotate(3 * math.sin(t * 4 + i), Image.BICUBIC, expand=True)
        pop(fr, im, 220 + i * 320, 680, t, a, k)
    if t > 4.15: put(fr, chip("COMO COMPARAR EM INGLÊS", YEL, INK, 40), 540, 880, env(t, 4.15, 6.3))
    if t > 4.4: put(fr, emoji("⚖️", 120), 540, 1050 + 6 * math.sin(t * 4), env(t, 4.4, 6.3))
def short(fr, t):
    k = env(t, 6.3, 14.75)
    if k <= 0: return
    put(fr, chip("SHORT ADJECTIVES", C_ER, WHITE, 50), 540, 290, k, 0.7 + 0.3 * bo((t - 6.3) / 0.4))
    pop(fr, chip("+ ER", YEL, INK, 70, 40), 540, 450, t, 7.3, k)
    suffix_join(fr, "TALL", "ER", t, 8.9, 9.72, 670, k, C_ER)
    suffix_join(fr, "CHEAP", "ER", t, 10.65, 11.3, 890, k, C_ER)
    if t > 12.2: put(fr, txt("adjetivo curto + ER", MF("ExtraBold", 50), MUTED), 540, 1065, env(t, 12.2, 14.75))
def example1(fr, t):
    k = env(t, 14.75, 18.7)
    if k <= 0: return
    put(fr, chip("TALLER THAN", C_ER, WHITE, 56), 540, 290, k, 0.7 + 0.3 * bo((t - 14.75) / 0.4))
    base = 1010
    for x, sz, lab, a in [(340, 420, "MY BROTHER", 15.0), (740, 250, "ME", 15.9)]:
        if t < a: continue
        u = bo((t - a) / 0.4, 1.8); e = emoji("🧍", sz)
        e = e.resize((max(1, e.width), max(1, int(e.height * u))), Image.BICUBIC) if u < 0.999 else e
        fr.alpha_composite(fade(e, k), (int(x - e.width / 2), int(base - e.height)))
        put(fr, chip(lab, WHITE, INK, 34), x, base + 50, k)
    if t > 15.6:  # régua de altura
        d = ImageDraw.Draw(fr); g = eo((t - 15.6) / 0.5); al = int(255 * k)
        d.line((140, base, 140, base - 420 * g), fill=YEL + (al,), width=8)
        for h_ in range(0, int(420 * g), 60): d.line((128, base - h_, 152, base - h_), fill=YEL + (al,), width=4)
def long_(fr, t):
    k = env(t, 18.7, 25.8)
    if k <= 0: return
    put(fr, chip("LONG ADJECTIVES", C_MORE, WHITE, 50), 540, 290, k, 0.7 + 0.3 * bo((t - 18.7) / 0.4))
    pop(fr, chip("MORE + adjetivo", YEL, INK, 56, 36), 540, 460, t, 19.6, k)
    prefix_join(fr, "EXPENSIVE", "MORE", t, 20.95, 22.0, 720, k, C_MORE)
    if t > 23.4: put(fr, emoji("💎", 120), 540, 990 + 6 * math.sin(t * 4), env(t, 23.4, 25.8))
def example2(fr, t):
    k = env(t, 25.8, 30.5)
    if k <= 0: return
    put(fr, chip("MORE EXPENSIVE THAN", C_MORE, WHITE, 50), 540, 290, k, 0.7 + 0.3 * bo((t - 25.8) / 0.4))
    for x, e, tag, col, a in [(300, "🏎️", "$$$", C_MORE, 26.2), (780, "🚗", "$", (120, 136, 170), 27.4)]:
        pop(fr, emoji(e, 260), x, 640, t, a, k)
        pop(fr, chip(tag, col, WHITE, 64, 34), x, 850, t, a + 0.25, k)
    if t > 28.5: put(fr, txt("mais caro que", MF("ExtraBold", 50), MUTED), 540, 1040, env(t, 28.5, 30.5))
def irregular(fr, t):
    k = env(t, 30.5, 38.3)
    if k <= 0: return
    put(fr, chip("WATCH OUT!", C_IRR, WHITE, 56), 540, 290, k, 0.7 + 0.3 * bo((t - 30.5) / 0.4) + 0.03 * math.sin(t * 8))
    put(fr, txt("IRREGULARES", MF("ExtraBold", 40), MUTED), 540, 390, k)
    for y, a_, b_, ta, tb in [(570, "GOOD", "BETTER", 30.7, 31.67), (790, "BAD", "WORSE", 32.28, 33.72)]:
        pop(fr, chip(a_, WHITE, INK, 64, 34), 270, y, t, ta, k)
        if t > ta + 0.3: put(fr, txt("→", MF("ExtraBold", 80), YEL), 540, y, k * eo((t - ta - 0.3) / 0.3))
        pop(fr, chip(b_, C_IRR, WHITE, 64, 34), 790, y, t, tb, k)
    if t > 34.9:
        g = env(t, 34.9, 38.3); f = MF("ExtraBold", 46); s_ = "gooder · badder"; im = txt(s_, f, MUTED)
        lay = im.copy(); d = ImageDraw.Draw(lay); w_ = int((lay.width - 20) * eo((t - 35.4) / 0.4)); d.line((10, lay.height / 2 + 4, 10 + w_, lay.height / 2 + 4), fill=C_IRR + (255,), width=7)
        put(fr, lay, 500, 1010, g); put(fr, emoji("❌", 60), 500 + lay.width / 2 + 50, 1010, g)
def now_you(fr, t):
    k = env(t, 38.3, TOTAL, 0.3, 0.01)
    if k <= 0: return
    put(fr, chip("NOW YOU!", YEL, INK, 60), 540, 290, k, 0.7 + 0.3 * bo((t - 38.3) / 0.4))
    if t > 39.6:
        g = eo((t - 39.6) / 0.35); f = MF("ExtraBold", 70)
        put(fr, txt("São Paulo is ____", f, WHITE, 4), 540, 500, g * k); put(fr, txt("than Santos.", f, WHITE, 4), 540, 600, eo((t - 40.7) / 0.35) * k)
    for x, w_, c, a in [(290, "BIG", (120, 136, 170), 42.0), (800, "BIGGER", C_ER, 42.55)]:
        pop(fr, chip(w_, c, WHITE, 64, 40).rotate(3 * math.sin(t * 4 + x), Image.BICUBIC, expand=True), x, 790, t, a, k)
    if t > 42.3: put(fr, txt("?", ANTON(110), YEL, 5), 540, 790, k, 1 + 0.08 * math.sin(t * 7))
    if t > 43.3:
        put(fr, chip("COMENTA AQUI", (220, 40, 40), WHITE, 56), 540, 980, k, (0.6 + 0.4 * bo((t - 43.3) / 0.35, 2.2)) * (1 + 0.04 * math.sin(t * 6)))
        put(fr, emoji("👇", 90), 540, 1100 + 10 * math.sin(t * 6), k)
def captions(fr, t):
    for p in PAIRS:
        if not (p["en"][1] - 0.05 <= t < p["t1"]): continue
        a, b = p["en"][1], p["en"][2]; kin = eo((t - a) / 0.25)
        im = karaoke(p["en"][3], a, b, t, MF("ExtraBold", 56), 960); y = 1280
        put(fr, im, 540, y, kin, 0.92 + 0.08 * kin)
        if p["pt"] and t >= p["pt"][1] - 0.05:
            ip = karaoke(p["pt"][3], p["pt"][1], p["pt"][2], t, MF("Bold", 40), 940, (255, 230, 150), hl=False)
            put(fr, ip, 540, y + im.height / 2 + 46, eo((t - p["pt"][1]) / 0.25))
        return
def progress(fr, t):
    d = ImageDraw.Draw(fr); d.rounded_rectangle((60, 1880, 1020, 1892), 6, fill=(60, 84, 128, 255)); d.rounded_rectangle((60, 1880, 60 + 960 * clamp(t / VO_LEN), 1892), 6, fill=YEL + (255,))
def frame_at(t):
    fr = BG.copy(); hook(fr, t); short(fr, t); example1(fr, t); long_(fr, t); example2(fr, t); irregular(fr, t); now_you(fr, t)
    captions(fr, t); avatar(fr, min(t, VO_LEN - 0.01)); progress(fr, t); return fr.convert("RGB")
def capa(out):
    fr = BG.copy(); put(fr, txt("COMPARATIVE", ANTON(140), WHITE, 7), 540, 320); put(fr, txt("ADJECTIVES", ANTON(140), YEL, 7), 540, 480)
    for i, (a_, b_, c) in enumerate([("TALL", "TALLER", C_ER), ("EXPENSIVE", "MORE EXPENSIVE", C_MORE), ("GOOD", "BETTER", C_IRR)]):
        y = 720 + i * 190; f = MF("ExtraBold", 50); la = txt(a_, f, WHITE, 3); cb = chip(b_, c, WHITE, 54, 30)
        tw = la.width + 90 + cb.width; x = 540 - tw / 2
        put(fr, la, x + la.width / 2, y); put(fr, txt("→", MF("ExtraBold", 60), YEL), x + la.width + 45, y); sput(fr, cb, x + la.width + 90 + cb.width / 2, y)
    put(fr, chip("INGLÊS RÁPIDO", YEL, INK, 50), 540, 1360)
    avatar(fr, 0.0); fr.convert("RGB").save(out, quality=95)
def load_amp():
    global AMP
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{V}/vo.mp3", "-ar", "16000", "-ac", "1", f"{V}/vo16.wav"], check=True)
    w = wave.open(f"{V}/vo16.wav"); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
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
    writew(f"{V}/voice.wav", vt); writew(f"{V}/song.wav", loop[:n] * gain[:, None])
    ev = [(0.1, sfx.whoosh(0.4), 0.15)] + [(a, sfx.click(seed=i), 0.15) for i, a in enumerate((1.7, 2.1, 2.5))]
    ev += [(a - 0.15, sfx.whoosh(0.4), 0.12) for a in (6.3, 14.75, 18.7, 25.8, 30.5, 38.3)]
    ev += [(a, sfx.click(seed=5), 0.2) for a in (9.72, 11.3)] + [(22.0, sfx.thud(0.35), 0.2), (7.3, sfx.thud(0.3), 0.15)]
    ev += [(a, sfx.click(seed=9), 0.15) for a in (31.67, 33.72, 42.0, 42.55)] + [(43.3, sfx.thud(0.35), 0.18)]
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
