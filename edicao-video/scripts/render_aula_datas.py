"""Reels 9:16 (1080x1920) para a aula do 7º ano: Aulas 1, 2 e 3 do 4º bimestre (Birth dates, Dates in history, Life story timeline)
num vídeo só, sem narração (o professor conduz em sala). in/on, números ordinais, anos em dois blocos, linha do tempo do Alberto,
4 perguntas de quiz com contador de 5 s e a tarefa da timeline. Avatar 3D embaixo reagindo (pensando no contador)."""
import sys, math, re, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.path.insert(0, f"{S}/work")
import sfx
V = f"{S}/v84"; FD = f"{S}/fontdl"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H, FPS = 1080, 1920, 30
TOTAL = 90.0; VO_LEN = TOTAL
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
C_IN = (52, 190, 110); C_ON = (64, 150, 255); C_X = (236, 84, 84); GREEN = (46, 184, 92)
# ---------------------------------------------------------------- fundo
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.38) / H) ** 2)
BG = np.array(NAVY, np.float32) + np.array([26, 52, 96], np.float32) * np.clip(1 - r * 1.5, 0, 1)[..., None]
for g in range(0, W, 60): BG[:, g:g + 1] += 6
for g in range(0, H, 60): BG[g:g + 1, :] += 6
BG = Image.fromarray(np.clip(BG, 0, 255).astype(np.uint8)).convert("RGBA"); del yy, xx, r
hd = ImageDraw.Draw(BG); hd.rounded_rectangle((300, 70, 780, 130), 30, fill=WHITE + (255,)); hd.text((540, 100), "ENGLISH CLASS · Teacher Eliezio", font=MF("ExtraBold", 24), fill=INK + (255,), anchor="mm")
# ---------------------------------------------------------------- roteiro (s)
SC = dict(hook=(0, 4.5), inon=(4.5, 13), q1=(13, 22.5), ordn=(22.5, 31), q2=(31, 40.5), years=(40.5, 50), q3=(50, 59.5), tl=(59.5, 72), q4=(72, 81.5), turn=(81.5, TOTAL))
QUIZ = [("q1", "QUIZ 1", "I was born ___ July.", [("IN", True), ("ON", False)], "Só o mês → IN"),
        ("q2", "QUIZ 2", "Como se diz 3º em inglês?", [("THREETH", False), ("THIRD", True)], "THIRD é exceção, como FIRST e SECOND"),
        ("q3", "QUIZ 3", "Como se lê 1980?", [("nineteen eighty", True), ("one nine eight zero", False)], "Dois blocos: 19 | 80"),
        ("q4", "QUIZ 4", "What is NOT a characteristic of a timeline?", [("Short texts with OPINIONS", True), ("Short texts with FACTS", False)], "Timeline mostra fatos, não opiniões")]
CD = 5.0  # contador
def qtimes(key):
    a, b = SC[key]; return a, a + 1.5, a + 1.5 + CD, b     # entra, começa contagem, revela, sai
# ---------------------------------------------------------------- avatar (1 sorrindo, 2 desconfiado, 7 surpreso, 8 piscando)
AV = [Image.open(f"{S}/v77/av3d_{k}.png").convert("RGBA").resize((360, 360), Image.LANCZOS) for k in range(1, 9)]
EXPR = [(0, 1)]
for key, *_ in QUIZ:
    a, c0, rv, b = qtimes(key); EXPR += [(c0, 2), (rv, 7), (rv + 1.0, 1)]
EXPR += [(SC["turn"][0] + 4, 8), (SC["turn"][0] + 6, 1)]
def avatar(fr, t):
    cx, cy = 540, 1715; a = 0.18 + 0.12 * math.sin(t * 3.1) ** 2
    i = max(k for k, e in enumerate(EXPR) if e[0] <= t); cur = EXPR[i][1]; prv = EXPR[i - 1][1] if i else cur; k = clamp((t - EXPR[i][0]) / 0.18)
    face = AV[cur - 1] if k >= 1 else Image.blend(AV[prv - 1], AV[cur - 1], k)
    rot = 2.0 * math.sin(t * 2.3) * (0.3 + a); face = face.rotate(rot, Image.BICUBIC) if abs(rot) > 0.05 else face
    bob = -6 * a + 3 * math.sin(t * 1.7); sc = 1 + 0.03 * a
    g = Image.new("RGBA", (480, 480), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((40, 40, 440, 440), fill=YEL + (int(90 + 90 * a),)); put(fr, g.filter(ImageFilter.GaussianBlur(24)), cx, cy + bob, 1, sc)
    ring = Image.new("RGBA", (396, 396), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((0, 0, 395, 395), fill=YEL + (255,))
    put(fr, ring, cx, cy + bob, 1, sc); put(fr, face, cx, cy + bob, 1, sc)
# ---------------------------------------------------------------- peças
def wrap(s, f, maxw):
    out = [[]]
    for w in s.split():
        if out[-1] and f.getlength(" ".join(out[-1] + [w])) > maxw: out.append([])
        out[-1].append(w)
    return [" ".join(l) for l in out]
def block(s, f, col, maxw=960, stroke=4, lh=1.22):
    """texto quebrado em linhas e centralizado"""
    ls = wrap(s, f, maxw); h = int(f.size * lh); im = Image.new("RGBA", (maxw + 40, h * len(ls) + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for i, l in enumerate(ls): d.text((im.width / 2, 10 + i * h + h / 2), l, font=f, fill=col + (255,), anchor="mm", stroke_width=stroke, stroke_fill=INK + (255,))
    return im
def hlsent(s, key, col, f):
    """frase branca com uma palavra numa caixa colorida"""
    sp = f.getlength(" "); ws = s.split(); tw = sum(f.getlength(w) for w in ws) + sp * (len(ws) - 1)
    im = Image.new("RGBA", (int(tw) + 60, int(f.size * 1.6)), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 30; y = f.size * 0.22
    for w in ws:
        wl = f.getlength(w)
        if w == key: d.rounded_rectangle((x - 10, y - 4, x + wl + 10, y + f.size * 1.12), 14, fill=col + (255,)); d.text((x, y), w, font=f, fill=WHITE + (255,))
        else: d.text((x, y), w, font=f, fill=WHITE + (255,), stroke_width=4, stroke_fill=INK + (255,))
        x += wl + sp
    return im
def note(fr, s, t, a, b, y=1290):
    k = env(t, a, b)
    if k <= 0: return
    f = MF("Bold", 42); ls = wrap(s, f, 860); h = 58; bw = max(f.getlength(l) for l in ls) + 70; bh = h * len(ls) + 40
    im = Image.new("RGBA", (int(bw), int(bh)), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.rounded_rectangle((0, 0, bw - 1, bh - 1), 26, fill=(8, 18, 40, 215), outline=YEL + (255,), width=3)
    for i, l in enumerate(ls): d.text((bw / 2, 20 + i * h + h / 2), l, font=f, fill=(255, 230, 150, 255), anchor="mm")
    put(fr, im, 540, y, k, 0.9 + 0.1 * eo((t - a) / 0.3))
def title(fr, s, col, fill, t, a, y=290, size=54):
    put(fr, chip(s, fill, col, size), 540, y, 1, 0.7 + 0.3 * bo((t - a) / 0.4))
def pop(fr, im, x, y, t, a, k, shadow=True):
    if t < a: return
    (sput if shadow else put)(fr, im, x, y, k, 0.5 + 0.5 * bo((t - a) / 0.35, 2.2))
# ---------------------------------------------------------------- cenas
def hook(fr, t):
    a, b = SC["hook"]; k = env(t, a, b)
    if k <= 0: return
    put(fr, txt("DATES IN", ANTON(150), WHITE, 7), 540, 330, k, 0.9 + 0.1 * bo(t / 0.4))
    put(fr, txt("ENGLISH", ANTON(150), YEL, 7), 540, 500, k, 0.9 + 0.1 * bo((t - 0.2) / 0.4))
    for i, (s, c) in enumerate([("1 · BIRTH DATES", C_IN), ("2 · DATES IN HISTORY", C_ON), ("3 · LIFE STORY TIMELINE", C_X)]):
        pop(fr, chip(s, c, WHITE, 46, 34), 540, 720 + i * 130, t, 1.0 + 0.45 * i, k)
    if t > 2.6: put(fr, chip("+ 4 QUIZZES ⏱" if False else "+ 4 PERGUNTAS DE QUIZ", YEL, INK, 44), 540, 1150, k, 0.6 + 0.4 * bo((t - 2.6) / 0.35, 2.2))
def inon(fr, t):
    a, b = SC["inon"]; k = env(t, a, b)
    if k <= 0: return
    put(fr, txt("WHEN WERE YOU BORN?", ANTON(96), WHITE, 6), 540, 300, k, 0.9 + 0.1 * bo((t - a) / 0.4))
    f = MF("ExtraBold", 72)
    pop(fr, hlsent("I was born in May.", "in", C_IN, f), 540, 560, t, a + 1.0, k, False)
    if t > a + 2.0: put(fr, chip("só o mês → IN", C_IN, WHITE, 38), 540, 680, env(t, a + 2.0, b))
    pop(fr, hlsent("I was born on May 9th.", "on", C_ON, f), 540, 900, t, a + 3.6, k, False)
    if t > a + 4.6: put(fr, chip("data completa → ON", C_ON, WHITE, 38), 540, 1020, env(t, a + 4.6, b))
    note(fr, "Pergunta: When were you born? Resposta: I was born...", t, a + 5.5, b)
def ordn(fr, t):
    a, b = SC["ordn"]; k = env(t, a, b)
    if k <= 0: return
    title(fr, "ORDINAL NUMBERS", WHITE, C_ON, t, a)
    cells = [("1st", "first", True), ("2nd", "second", True), ("3rd", "third", True), ("4th", "fourth", False), ("10th", "tenth", False), ("20th", "twentieth", False)]
    for i, (n_, w_, ex) in enumerate(cells):
        x = 300 + (i // 3) * 480; y = 530 + (i % 3) * 200; ta = a + 0.6 + i * 0.5
        if t < ta: continue
        c = C_X if ex else C_ON; card = Image.new("RGBA", (420, 160), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
        d.rounded_rectangle((0, 0, 419, 159), 26, fill=WHITE + (255,), outline=c + (255,), width=6)
        d.text((110, 80), n_, font=ANTON(84), fill=c + (255,), anchor="mm"); d.text((300, 80), w_, font=MF("ExtraBold", 40), fill=INK + (255,), anchor="mm")
        sput(fr, card, x, y, k, 0.6 + 0.4 * bo((t - ta) / 0.35, 1.8))
    if t > a + 4.0: put(fr, chip("EXCEÇÕES", C_X, WHITE, 34), 300, 405, env(t, a + 4.0, b)); put(fr, chip("+ TH", C_ON, WHITE, 34), 780, 405, env(t, a + 4.0, b))
    note(fr, "A maioria ganha TH no final. Exceções: 1st, 2nd e 3rd. Data: May 9th = May ninth", t, a + 4.6, b)
def years(fr, t):
    a, b = SC["years"]; k = env(t, a, b)
    if k <= 0: return
    title(fr, "YEARS", INK, YEL, t, a)
    f = ANTON(210); g = eio((t - a - 1.6) / 0.6); y = 520
    l, r_ = txt("19", f, WHITE, 7), txt("58", f, WHITE, 7); gap = 20 + 120 * g
    put(fr, l, 540 - gap / 2 - l.width / 2, y, k * clamp((t - a - 0.4) / 0.3)); put(fr, r_, 540 + gap / 2 + r_.width / 2, y, k * clamp((t - a - 0.4) / 0.3))
    if g > 0.5: ImageDraw.Draw(fr).line((540, y - 100, 540, y + 100), fill=YEL + (int(255 * k),), width=8)
    if t > a + 2.4:
        for x, s in [(540 - gap / 2 - l.width / 2, "nineteen"), (540 + gap / 2 + r_.width / 2, "fifty-eight")]: put(fr, chip(s, C_ON, WHITE, 40), x, 700, env(t, a + 2.4, b))
    if t > a + 4.8:
        put(fr, txt("2016", ANTON(130), YEL, 6), 540, 900, env(t, a + 4.8, b), 0.7 + 0.3 * bo((t - a - 4.8) / 0.35))
        if t > a + 5.6: put(fr, chip("two thousand sixteen", C_IN, WHITE, 44), 540, 1060, env(t, a + 5.6, b))
    note(fr, "O ano se lê em dois blocos. Depois de 2000: two thousand...", t, a + 3.2, b)
def quiz(fr, t, key, lab, q, opts, expl):
    a, c0, rv, b = qtimes(key); k = env(t, a, b)
    if k <= 0: return
    title(fr, lab, INK, YEL, t, a, size=60)
    qb = block(q, MF("ExtraBold", 66), WHITE, 940); put(fr, qb, 540, max(470, 375 + qb.height / 2), k, 0.85 + 0.15 * bo((t - a) / 0.4))
    for i, (s, ok) in enumerate(opts):
        ta = a + 0.5 + 0.35 * i
        if t < ta: continue
        y = max(700, 375 + qb.height + 90) + i * 170; card = Image.new("RGBA", (900, 140), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
        rvd = t >= rv; fill = (GREEN if ok else (90, 104, 136)) if rvd else WHITE; tc = WHITE if rvd else INK
        d.rounded_rectangle((0, 0, 899, 139), 30, fill=fill + (255,), outline=YEL + (255,) if not rvd else fill + (255,), width=5)
        d.ellipse((24, 26, 112, 114), fill=(INK if not rvd else WHITE) + (255,)); d.text((68, 71), "AB"[i], font=MF("ExtraBold", 48), fill=(WHITE if not rvd else fill) + (255,), anchor="mm")
        fs = 54 if max(MF("ExtraBold", 54).getlength(o) for o, _ in opts) < 700 else 44
        d.text((500, 72), s, font=MF("ExtraBold", fs), fill=tc + (255,), anchor="mm")
        sc = 0.6 + 0.4 * bo((t - ta) / 0.35, 1.8)
        if rvd and ok: sc *= 1 + 0.06 * bo((t - rv) / 0.3, 3) - 0.06 + 0.02 * math.sin(t * 6)
        sput(fr, card, 540, y, k * (0.55 if rvd and not ok else 1), sc)
        if rvd: put(fr, emoji("✅" if ok else "❌", 84), 990, y, k, 0.5 + 0.5 * bo((t - rv) / 0.3, 2))
    if c0 <= t < rv:  # contador
        u = (t - c0) / CD; n_ = int(CD - (t - c0)) + 1; fz = (t - c0) % 1
        cx, cy, R = 540, max(1110, 375 + qb.height + 90 + 170 + 230), 110; lay = Image.new("RGBA", (300, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.ellipse((150 - R, 150 - R, 150 + R, 150 + R), fill=(8, 18, 40, 230)); d.ellipse((150 - R, 150 - R, 150 + R, 150 + R), outline=(60, 84, 128, 255), width=16)
        col = YEL if n_ > 2 else C_X
        d.arc((150 - R, 150 - R, 150 + R, 150 + R), -90, -90 + 360 * (1 - u), fill=col + (255,), width=16)
        put(fr, lay, cx, cy, k); put(fr, txt(str(n_), ANTON(130), col, 5), cx, cy, k, 1 + 0.25 * (1 - eo(fz / 0.3)))
    if t >= rv: note(fr, expl, t, rv + 0.2, b, y=1110)
def timeline(fr, t):
    a, b = SC["tl"]; k = env(t, a, b)
    if k <= 0: return
    title(fr, "TIMELINE = LINHA DO TEMPO", WHITE, C_X, t, a, size=46)
    put(fr, txt("Alberto's life", MF("ExtraBold", 50), MUTED), 540, 390, k)
    ev = [("2013", "was born", a + 1.0), ("2021", "won his first swimming competition", a + 2.6), ("2023", "went camping with his family", a + 4.2)]
    g = eo((t - a - 0.6) / (4.2 + 0.6 - 0.6)); d = ImageDraw.Draw(fr); y0, y1 = 480, 1060
    d.line((230, y0, 230, y0 + (y1 - y0) * g), fill=YEL + (int(255 * k),), width=10)
    for i, (yr, s, ta) in enumerate(ev):
        if t < ta: continue
        y = 540 + i * 220; u = bo((t - ta) / 0.35, 2)
        dot = Image.new("RGBA", (60, 60), (0, 0, 0, 0)); ImageDraw.Draw(dot).ellipse((0, 0, 59, 59), fill=YEL + (255,), outline=WHITE + (255,), width=6); put(fr, dot, 230, y, k, max(0.01, u))
        put(fr, chip(yr, C_ON, WHITE, 52, 26, 20), 380, y - 10, k, 0.6 + 0.4 * u)
        bl = block(s, MF("ExtraBold", 44), WHITE, 470, 3, 1.15); fr.alpha_composite(fade(bl, k * clamp((t - ta - 0.2) / 0.3)), (495, int(y - 10 - bl.height / 2)))
    if t > a + 6.5: put(fr, hlsent("He was born in 2013.", "in", C_IN, MF("ExtraBold", 54)), 540, 1180, env(t, a + 6.5, b))
    note(fr, "Fatos em ordem cronológica, com datas e verbos no passado. Ano também usa IN.", t, a + 7.5, b, y=1330)
def turn(fr, t):
    a, b = SC["turn"]; k = env(t, a, b, 0.3, 0.01)
    if k <= 0: return
    put(fr, txt("YOUR TURN!", ANTON(140), YEL, 7), 540, 320, k, 0.9 + 0.1 * bo((t - a) / 0.4))
    put(fr, block("List 8 important events in your life. Remember the dates!", MF("ExtraBold", 52), WHITE, 900), 540, 520, k)
    for i, s in enumerate(["2014 – started school", "2015 – got my first pet", "2020 – learned how to ride a bike"]):
        pop(fr, chip(s, WHITE, INK, 40, 30, 22), 540, 720 + i * 120, t, a + 1.2 + 0.6 * i, k)
    if t > a + 3.6: note(fr, "Na próxima aula: você monta a sua timeline!", t, a + 3.6, b + 1, y=1110)
def progress(fr, t):
    d = ImageDraw.Draw(fr); d.rounded_rectangle((60, 1880, 1020, 1892), 6, fill=(60, 84, 128, 255)); d.rounded_rectangle((60, 1880, 60 + 960 * clamp(t / TOTAL), 1892), 6, fill=YEL + (255,))
def frame_at(t):
    fr = BG.copy(); hook(fr, t); inon(fr, t); ordn(fr, t); years(fr, t); timeline(fr, t); turn(fr, t)
    for qz in QUIZ: quiz(fr, t, *qz)
    avatar(fr, t); progress(fr, t); return fr.convert("RGB")
def capa(out):
    fr = BG.copy(); put(fr, txt("DATES IN", ANTON(160), WHITE, 7), 540, 330); put(fr, txt("ENGLISH", ANTON(160), YEL, 7), 540, 510)
    for i, (s, c) in enumerate([("1 · BIRTH DATES", C_IN), ("2 · DATES IN HISTORY", C_ON), ("3 · LIFE STORY TIMELINE", C_X)]): sput(fr, chip(s, c, WHITE, 50, 36), 540, 740 + i * 140)
    put(fr, chip("QUIZ COM CONTADOR", YEL, INK, 52), 540, 1230); put(fr, txt("7º ANO · 4º BIMESTRE", MF("ExtraBold", 40), MUTED), 540, 1340)
    avatar(fr, 0.0); fr.convert("RGB").save(out, quality=95)
def audio(vout):
    SR = 48000; n = int(TOTAL * SR)
    def readw(p):
        w = wave.open(p); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; return x.reshape(-1, w.getnchannels())
    def writew(p, x):
        w = wave.open(p, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
    bed = readw(f"{S}/v49/bed.wav"); xf = int(1.5 * SR); loop = bed.copy()
    while len(loop) < n:
        rr = np.linspace(0, 1, xf)[:, None]; loop[-xf:] = loop[-xf:] * (1 - rr) + bed[:xf] * rr; loop = np.concatenate([loop, bed[xf:]])
    tl = np.arange(n) / SR; gain = 0.22 * np.clip(tl / 0.5, 0, 1) * np.clip(1 - (tl - (TOTAL - 1.5)) / 1.4, 0, 1)
    for key, *_ in QUIZ:  # música abaixa no contador para o tique-taque aparecer
        a, c0, rv, b = qtimes(key); gain *= 1 - 0.6 * np.clip((tl - c0 + 0.3) / 0.3, 0, 1) * np.clip((rv + 0.4 - tl) / 0.3, 0, 1)
    writew(f"{V}/song.wav", loop[:n] * gain[:, None])
    ding = readw(f"{S}/v81/ding.wav")
    ev = [(0.1, sfx.whoosh(0.4), 0.15)] + [(SC[k][0] - 0.15, sfx.whoosh(0.4), 0.14) for k in ("inon", "ordn", "years", "tl", "turn")]
    for key, *_ in QUIZ:
        a, c0, rv, b = qtimes(key); ev += [(a, sfx.thud(0.4), 0.22)] + [(c0 + s, sfx.click(seed=s), 0.32) for s in range(int(CD))] + [(rv, ding, 0.5)]
    sfx.build(ev, TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    f"[1:a][2:a]amix=inputs=2:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.89:level=false[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
def main():
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
