"""Vídeo de vendas do mini curso "Inglês para Viajar" para o Instagram do Teacher Eliezio (10/11/2026).
Vertical 1080x1920, ~37 s, no padrão do canal Teacher: fundo azul com grade, pílula "ENGLISH CLASS", avatar 3D em círculo amarelo,
legenda karaokê (palavra falada em amarelo). Voz dele (ElevenLabs) + oficial (Roger). Capa entra depois, com finaliza_teacher.sh.
Uso: python3 video_vendas.py frames:t1,t2 | python3 video_vendas.py SAIDA.mp4"""
import sys, math, json, re, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
K = "/home/user/next-netlify-starter/edicao-video"; sys.path.insert(0, K + "/scripts")
import sfx
FD = K + "/assets/fonts"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H, FPS = 1080, 1920, 30
YEL = (255, 214, 64); NAVY = (10, 30, 70); WHITE = (255, 255, 255); BLUE = (28, 70, 170); INK = (16, 30, 66)
OFF = 2.8            # voz do professor começa aqui
OF_AT = 0.25         # oficial
PROF_LEN = 34.116
END = OFF + 34.08 + 0.45
def F(n, s): return ImageFont.truetype(f"{FD}/{n}.ttf", s)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def pop(t, t0, dur=0.24, over=1.14):
    if t < t0: return 0.0
    x = clamp((t - t0) / dur)
    return (0.55 + (over - 0.55) * x / 0.7) if x < 0.7 else over - (over - 1) * (x - 0.7) / 0.3
def fade_in(t, t0, d=0.2): return clamp((t - t0) / d)
def fade_out(t, t1, d=0.25): return clamp((t1 - t) / d)

# ---------- tokens (legenda e gatilhos) ----------
SEGS = json.load(open("segs.json"))
TOK = [
 [("Travou?", 2)],
 [("Calma,", 2), ("isso", 2), ("acontece", 3), ("com", 1), ("todo", 2), ("mundo.", 2)],
 [("É", 1), ("por", 1), ("isso", 2), ("que", 1), ("eu", 1), ("criei", 2), ("o", 1), ("mini", 2), ("curso", 2), ("Inglês", 2), ("para", 2), ("Viajar.", 3)],
 [("São", 1), ("sete", 2), ("aulas", 2), ("curtas:", 2)],
 [("aeroporto,", 5), ("hotel,", 2), ("restaurante,", 4), ("na", 1), ("rua,", 2), ("transporte", 3), ("e", 1), ("compras.", 3)],
 [("Cada", 2), ("aula", 2), ("tem", 1), ("uma", 1), ("conversa", 3), ("de", 1), ("verdade,", 3), ("com", 1), ("as", 1), ("respostas", 3), ("que", 1), ("você", 2), ("vai", 1), ("precisar,", 3), ("e", 1), ("um", 1), ("PDF", 3), ("de", 1), ("bolso", 2), ("para", 2), ("levar", 2), ("no", 1), ("celular.", 4)],
 [("A", 1), ("primeira", 3), ("aula", 2), ("é", 1), ("grátis.", 2), ("Assista", 3), ("no", 1), ("link", 1), ("da", 1), ("bio", 1), ("e", 1), ("veja", 2), ("como", 2), ("funciona.", 3)],
 [("De", 1), ("R$ 59", 8), ("por", 1), ("R$ 27,", 7), ("por", 1), ("tempo", 2), ("limitado.", 4)],
 [("E", 1), ("tem", 1), ("7", 2), ("dias", 2), ("de", 1), ("garantia.", 4)],
 [("Link", 1), ("na", 1), ("bio.", 1)],
 [("Follow", 2), ("Teacher", 2), ("Eliezio!", 4)],
]
assert len(SEGS) == len(TOK)
T = []   # (seg, idx, texto, ts, te) em tempo de vídeo
for si, (s, toks) in enumerate(zip(SEGS, TOK)):
    a, b = s["start"] + OFF, s["end"] + OFF; tot = sum(w for _, w in toks); c = a
    for i, (tx, w) in enumerate(toks):
        d = (b - a) * w / tot; T.append((si, i, tx, c, c + d)); c += d
import wave
_w = wave.open("prof16.wav"); _a = np.frombuffer(_w.readframes(_w.getnframes()), np.int16).astype(np.float32) / 32768
_rms = np.sqrt(np.convolve(_a ** 2, np.ones(480) / 480, "same"))[::160]   # 10 ms
def valley(tv, win=0.10):
    c = int((tv - OFF) * 100); lo, hi = max(0, c - int(win * 100)), min(len(_rms), c + int(win * 100))
    return (lo + int(np.argmin(_rms[lo:hi]))) / 100 + OFF
_seg4 = [i for i, x in enumerate(T) if x[0] == 4]
for j, i in enumerate(_seg4):
    if j == 0: continue
    nt = valley(T[i][3]); T[i] = (T[i][0], T[i][1], T[i][2], nt, T[i][4]); T[_seg4[j - 1]] = (*T[_seg4[j - 1]][:4], nt)
def tk(si, i): return next((x[3], x[4]) for x in T if x[0] == si and x[1] == i)
# blocos de legenda
BLK = []; cur = []
for x in T:
    cur.append(x)
    last_of_seg = (x[1] == len(TOK[x[0]]) - 1)
    if re.search(r"[\.\?\!:]$", x[2]) or len(cur) >= 4 or (x[2].endswith(",") and len(cur) >= 3) or last_of_seg:
        BLK.append(cur); cur = []
if cur: BLK.append(cur)

# ---------- recursos ----------
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.38) / H) ** 2)
k_ = np.clip(1 - r * 1.75, 0, 1)[..., None]
BG = np.array([6, 24, 62], np.float32) * (1 - k_) + np.array([30, 82, 178], np.float32) * k_
grid = ((xx % 60 < 2) | (yy % 60 < 2)).astype(np.float32)[..., None] * 9
BG = np.clip(BG + grid, 0, 255).astype(np.uint8)
AV = {n: Image.open(f"av3d_{n}.png").convert("RGBA") for n in (1, 7, 8, 11)}
PDF = [Image.open(f"{n}.jpg").convert("RGBA") for n in ("pdf-1", "pdf-2", "cert-7")]
AULA = Image.open("amostra-capa.jpg").convert("RGB")
_emo = {}
def emo(ch, size):
    k = (ch, size)
    if k not in _emo:
        f = ImageFont.truetype(EMOJI, 109); im = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((0, 0), ch, font=f, embedded_color=True); im = im.crop(im.getbbox())
        _emo[k] = im.resize((int(im.width * size / 109), int(im.height * size / 109)), Image.LANCZOS)
    return _emo[k]
def txt(t, font, fill, stroke=0, scol=NAVY, shadow=True):
    d = ImageDraw.Draw(Image.new("L", (4, 4))); b = d.textbbox((0, 0), t, font=font, stroke_width=stroke)
    im = Image.new("RGBA", (b[2] - b[0] + 70, b[3] - b[1] + 70), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((35 - b[0], 35 - b[1]), t, font=font, fill=fill, stroke_width=stroke, stroke_fill=scol + (255,))
    if not shadow: return im
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.getchannel("A").point(lambda v: int(v * .45))); sh = sh.filter(ImageFilter.GaussianBlur(9))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0)); out.alpha_composite(sh, (0, 7)); out.alpha_composite(im); return out
def put(fr, im, cx, cy, a=1.0, sc=1.0, rot=0.0):
    if a <= 0.01 or sc <= 0.01: return
    if abs(sc - 1) > 0.004: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if a < 1: al = im.getchannel("A").point(lambda v: int(v * a)); im = im.copy(); im.putalpha(al)
    fr.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
def rrect(w, h, rad, fill, outline=None, ow=0):
    s = 2; im = Image.new("RGBA", (w * s, h * s), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w * s - 1, h * s - 1), rad * s, fill=fill, outline=outline, width=ow * s)
    return im.resize((w, h), Image.LANCZOS)
def shadowed(im, blur=20, off=14, op=.5):
    sh = Image.new("RGBA", (im.width + 4 * blur, im.height + 4 * blur), (0, 0, 0, 0)); a = Image.new("L", sh.size, 0)
    a.paste(im.getchannel("A").point(lambda v: int(v * op)), (2 * blur, 2 * blur + off)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(blur)))
    sh.alpha_composite(im, (2 * blur, 2 * blur)); return sh

# ---------- peças ----------
PILL = None
def header(fr):
    global PILL
    if PILL is None:
        f = F("Montserrat-ExtraBold", 25); tw = int(ImageDraw.Draw(Image.new("L", (4, 4))).textlength("ENGLISH CLASS  ·  Teacher Eliezio", font=f)) + 70
        PILL = rrect(tw, 56, 28, (255, 255, 255, 255)); ImageDraw.Draw(PILL).text((tw / 2, 29), "ENGLISH CLASS  ·  Teacher Eliezio", font=f, fill=INK, anchor="mm")
    put(fr, PILL, W / 2, 95)
def avatar(fr, t):
    n = 11 if t < 3.72 + 0.0 else 1
    if 24.0 <= t < 28.0: n = 8
    if 28.3 <= t < 32.5: n = 7
    if t >= 35.4: n = 8
    sz = 336; br = 1 + 0.012 * math.sin(t * 3.1)
    ring = Image.new("RGBA", (sz + 40, sz + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(ring)
    d.ellipse((0, 0, sz + 39, sz + 39), fill=YEL + (255,)); av = AV[n].resize((sz, sz), Image.LANCZOS)
    m = Image.new("L", (sz, sz), 0); ImageDraw.Draw(m).ellipse((0, 0, sz - 1, sz - 1), fill=255); ring.paste(av, (20, 20), m)
    put(fr, shadowed(ring, 16, 10, .45), W / 2, 1668, 1, br)
def progress(fr, t):
    d = ImageDraw.Draw(fr); y = 1884; d.rounded_rectangle((60, y, 1020, y + 8), 4, fill=(255, 255, 255, 60))
    w = int(960 * clamp(t / END)); d.rounded_rectangle((60, y, 60 + max(8, w), y + 8), 4, fill=YEL + (255,))
def caption(fr, t):
    blk = None
    for i, b in enumerate(BLK):
        s = b[0][3] - 0.06; e = (BLK[i + 1][0][3] - 0.06) if i + 1 < len(BLK) else b[-1][4] + 0.4
        if s <= t < e: blk = b; s0 = s; break
    if blk is None: return
    f = F("Montserrat-ExtraBold", 56); d0 = ImageDraw.Draw(Image.new("L", (4, 4))); sp = d0.textlength(" ", font=f)
    ws = [d0.textlength(x[2], font=f) for x in blk]; lines = [[]]; cw = 0
    for x, w in zip(blk, ws):
        if lines[-1] and cw + sp + w > 940: lines.append([]); cw = 0
        cw += (sp if lines[-1] else 0) + w; lines[-1].append((x, w))
    a = fade_in(t, s0, 0.12); lay = Image.new("RGBA", (W, 90 * len(lines) + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for li, ln in enumerate(lines):
        tw = sum(w for _, w in ln) + sp * (len(ln) - 1); x0 = (W - tw) / 2
        for x, w in ln:
            on = x[3] - 0.02 <= t < x[4] + 0.02
            d.text((x0, 20 + li * 88), x[2], font=f, fill=(YEL if on else WHITE) + (255,), stroke_width=9, stroke_fill=NAVY + (255,)); x0 += w + sp
    put(fr, lay, W / 2, 1352 + (len(lines) - 1) * 0, a, 1.0 + 0.05 * (1 - eo((t - s0) / 0.15)))

def scene_hook(fr, t):
    a = fade_in(t, OF_AT) * fade_out(t, 5.6, 0.4)
    if a <= 0: return
    y0 = 240 + 40 * (1 - eo((t - OF_AT) / 0.35)) - 18 * clamp((t - 4.6) / 1.0)
    card = rrect(900, 470, 40, (255, 255, 255, 255)); d = ImageDraw.Draw(card)
    d.rounded_rectangle((40, 36, 640, 100), 32, fill=INK + (255,)); d.text((340, 69), "OFICIAL DA IMIGRAÇÃO", font=F("Montserrat-ExtraBold", 31), fill=WHITE + (255,), anchor="mm")
    f = F("Montserrat-ExtraBold", 72); d.text((450, 205), "What is the purpose", font=f, fill=INK + (255,), anchor="mm"); d.text((450, 292), "of your visit?", font=f, fill=INK + (255,), anchor="mm")
    d.text((450, 400), "Qual o motivo da sua visita?", font=F("Montserrat-Bold", 44), fill=BLUE + (255,), anchor="mm")
    e = emo("🛂", 90); card.alpha_composite(e, (900 - e.width - 40, 22))
    put(fr, shadowed(card, 22, 16, .5), W / 2, y0 + 235, a, pop(t, OF_AT, .3, 1.06) if t < OF_AT + .4 else 1.0)
def scene_travou(fr, t):
    a1 = fade_in(t, 2.8, 0.1) * fade_out(t, 5.7, 0.3)
    if a1 <= 0: return
    if t < 3.72:
        im = txt("TRAVOU?", F("Anton-Regular", 250), YEL, 9); put(fr, im, W / 2, 900, a1, pop(t, 2.85, .26, 1.18))
    else:
        im = txt("CALMA.", F("Anton-Regular", 250), WHITE, 9); put(fr, im, W / 2, 900, a1, pop(t, 3.72, .26, 1.12))
def scene_title(fr, t):
    s, e = tk(2, 5)[0] - 0.1, 9.8
    a = fade_in(t, s, 0.15) * fade_out(t, e, 0.3)
    if a <= 0: return
    put(fr, txt("MINI CURSO", F("Montserrat-ExtraBold", 54), YEL, 0), W / 2, 470, a, pop(t, s, .25, 1.08))
    put(fr, txt("INGLÊS", F("Anton-Regular", 250), WHITE, 9), W / 2, 680, a, pop(t, s + .1, .28, 1.1))
    put(fr, txt("PARA VIAJAR", F("Anton-Regular", 190), YEL, 9), W / 2, 905, a, pop(t, s + .25, .28, 1.1))
    put(fr, emo("✈️", 140), W / 2, 1110, a, pop(t, s + .4, .3, 1.15), rot=-10 + 8 * eo((t - s) / 1.2))
CARDS = [("✈️", "AEROPORTO", "1", None), ("🏨", "HOTEL", "2", None), ("🍽️", "RESTAURANTE", "3·4", "2 aulas"), ("🚶", "NA RUA", "5", None), ("🚕", "TRANSPORTE", "6", None), ("🛍️", "COMPRAS", "7", "e emergências")]
CARDIDX = [0, 1, 2, 4, 5, 7]     # índice do token na seg 4
_cardimg = {}
def card_img(i):
    if i in _cardimg: return _cardimg[i]
    e, name, num, tag = CARDS[i]; im = rrect(450, 180, 30, (255, 255, 255, 40), (255, 255, 255, 150), 3); d = ImageDraw.Draw(im)
    d.ellipse((22, 22, 92, 92), fill=YEL + (255,)); d.text((57, 58), num, font=F("Anton-Regular", 40 if len(num) == 1 else 32), fill=INK + (255,), anchor="mm")
    ei = emo(e, 70); im.alpha_composite(ei, (450 - ei.width - 28, 24))
    d.text((28, 128 if tag is None else 118), name, font=F("Montserrat-ExtraBold", 44 if len(name) < 11 else 38), fill=WHITE + (255,), anchor="lm")
    if tag: d.text((30, 156), tag.upper(), font=F("Montserrat-Bold", 24), fill=YEL + (255,), anchor="lm")
    _cardimg[i] = im; return im
def scene_cards(fr, t):
    s, e = tk(3, 0)[0] - 0.05, 17.0
    a = fade_in(t, s, 0.2) * fade_out(t, e, 0.3)
    if a <= 0: return
    put(fr, txt("7", F("Anton-Regular", 230), YEL, 8), 330, 330, a, pop(t, s, .28, 1.12))
    put(fr, txt("AULAS", F("Anton-Regular", 100), WHITE, 6), 640, 292, a, pop(t, s + .1, .26, 1.08)); put(fr, txt("CURTAS", F("Anton-Regular", 100), WHITE, 6), 660, 400, a, pop(t, s + .2, .26, 1.08))
    for i in range(6):
        t0 = tk(4, CARDIDX[i])[0] - 0.06; col, row = i % 2, i // 2
        x = 300 + col * 480; y = 640 + row * 215
        k = pop(t, t0, .26, 1.1)
        if k > 0: put(fr, shadowed(card_img(i), 12, 8, .35), x + 0 + 15, y, a * fade_in(t, t0, .1), k)
BUBBLES = [("Here is my passport.", 0), ("Ten days.", 1), ("At a hotel downtown.", 2)]
def bubble(txt_, w=640):
    f = F("Montserrat-ExtraBold", 50); tw = int(ImageDraw.Draw(Image.new("L", (4, 4))).textlength(txt_, font=f)) + 80
    im = rrect(tw, 112, 40, YEL + (255,)); ImageDraw.Draw(im).text((tw / 2, 58), txt_, font=f, fill=INK + (255,), anchor="mm"); return im
_b = {}
def scene_bubbles(fr, t):
    s = tk(5, 0)[0] - 0.05; e = tk(5, 16)[0] - 0.15
    a = fade_in(t, s, 0.2) * fade_out(t, e, 0.25)
    if a <= 0: return
    put(fr, txt("SUAS RESPOSTAS", F("Montserrat-ExtraBold", 50), WHITE, 0), W / 2, 330, a, pop(t, s, .25, 1.06))
    put(fr, emo("🗣️", 120), W / 2, 470, a, pop(t, s + .05, .3, 1.12))
    for txt_, i in BUBBLES:
        t0 = tk(5, 4 + i * 3)[0] if i < 2 else tk(5, 12)[0]
        if txt_ not in _b: _b[txt_] = bubble(txt_)
        k = pop(t, t0 + .15, .26, 1.1); x = 640 if i % 2 == 0 else 440
        if k > 0: put(fr, shadowed(_b[txt_], 12, 8, .35), x, 650 + i * 150, a, k)
def scene_pdf(fr, t):
    s = tk(5, 16)[0] - 0.1; e = tk(6, 0)[0] - 0.05
    a = fade_in(t, s, 0.15) * fade_out(t, e, 0.25)
    if a <= 0: return
    put(fr, txt("PDF DE BOLSO", F("Anton-Regular", 120), YEL, 7), W / 2, 330, a, pop(t, s, .26, 1.08))
    for i, (im, ang, dx, dy) in enumerate(zip(PDF, (-9, 0, 9), (-230, 0, 230), (40, 0, 40))):
        pg = im.resize((350, 495), Image.LANCZOS); ph = Image.new("RGBA", pg.size, (0, 0, 0, 0)); ph.paste(pg, (0, 0))
        m = rrect(350, 495, 14, (255, 255, 255, 255)).getchannel("A"); ph.putalpha(m)
        k = pop(t, s + .1 + .12 * i, .3, 1.08); t_in = eo((t - (s + .1 + .12 * i)) / .3)
        put(fr, shadowed(ph, 16, 10, .55), W / 2 + dx, 760 + dy + 40 * (1 - t_in), a, k, ang)
    put(fr, txt("+ CERTIFICADO", F("Montserrat-ExtraBold", 46), WHITE, 0), W / 2, 1110, a * fade_in(t, s + .6, .2))
def scene_gratis(fr, t):
    s = tk(6, 1)[0] - 0.1; e = tk(7, 0)[0] - 0.05
    a = fade_in(t, s, 0.15) * fade_out(t, e, 0.25)
    if a <= 0: return
    put(fr, txt("AULA 1 GRÁTIS", F("Anton-Regular", 150), YEL, 8), W / 2, 330, a, pop(t, s, .28, 1.1))
    card = AULA.resize((900, 506), Image.LANCZOS).convert("RGBA"); card.putalpha(rrect(900, 506, 26, (255, 255, 255, 255)).getchannel("A"))
    fm = Image.new("RGBA", (924, 530), (0, 0, 0, 0)); fm.alpha_composite(rrect(924, 530, 34, YEL + (255,))); fm.alpha_composite(card, (12, 12))
    d = ImageDraw.Draw(fm); d.ellipse((800 - 46, 440 - 46, 800 + 46, 440 + 46), fill=(255, 255, 255, 235)); d.polygon([(788, 418), (788, 462), (824, 440)], fill=INK + (255,))
    put(fr, shadowed(fm, 22, 14, .5), W / 2, 760, a, pop(t, s + .12, .3, 1.06))
    put(fr, txt("É SÓ ASSISTIR NO LINK DA BIO", F("Montserrat-ExtraBold", 38), WHITE, 0), W / 2, 1090, a * fade_in(t, s + .7, .25))
def scene_price(fr, t):
    s = tk(7, 0)[0] - 0.1; e = tk(8, 0)[0] - 0.05
    a = fade_in(t, s, 0.15) * fade_out(t, e, 0.25)
    if a <= 0: return
    t59 = tk(7, 1)[0]; t27 = tk(7, 3)[0]; tt = tk(7, 5)[0]
    im59 = txt("R$ 59", F("Anton-Regular", 210), (255, 255, 255, 200), 0); k = pop(t, t59 - .05, .26, 1.1)
    if k > 0:
        put(fr, im59, W / 2, 470, a, k)
        x1 = W / 2 - im59.width / 2 + 40; w = (im59.width - 80) * eo((t - (tk(7, 2)[0])) / .25)
        if w > 0: ImageDraw.Draw(fr).line((x1, 470, x1 + w, 470 - 14 * (w / (im59.width - 80))), fill=(255, 92, 92, int(255 * a)), width=16)
    put(fr, emo("👇", 100), W / 2, 640, a * fade_in(t, t27 - .3, .2), 1)
    k27 = pop(t, t27 - .04, .3, 1.16)
    if k27 > 0: put(fr, txt("R$ 27", F("Anton-Regular", 400), YEL, 12), W / 2, 880, a, k27)
    kp = pop(t, tt - .05, .26, 1.08)
    if kp > 0:
        pill = rrect(760, 108, 54, YEL + (255,)); ImageDraw.Draw(pill).text((380, 56), "POR TEMPO LIMITADO", font=F("Montserrat-Black", 46), fill=INK + (255,), anchor="mm")
        put(fr, shadowed(pill, 14, 8, .4), W / 2, 1150, a, kp)
def scene_garantia(fr, t):
    s = tk(8, 2)[0] - 0.1; e = tk(9, 0)[0] - 0.05
    a = fade_in(t, s, 0.12) * fade_out(t, e, 0.25)
    if a <= 0: return
    sz = 560; seal = Image.new("RGBA", (sz, sz), (0, 0, 0, 0)); d = ImageDraw.Draw(seal)
    d.ellipse((0, 0, sz - 1, sz - 1), fill=YEL + (255,)); d.ellipse((22, 22, sz - 23, sz - 23), fill=NAVY + (255,)); d.ellipse((36, 36, sz - 37, sz - 37), outline=YEL + (255,), width=5)
    d.text((sz / 2, 215), "7", font=F("Anton-Regular", 300), fill=YEL + (255,), anchor="mm")
    d.text((sz / 2, 368), "DIAS DE", font=F("Montserrat-ExtraBold", 46), fill=WHITE + (255,), anchor="mm"); d.text((sz / 2, 428), "GARANTIA", font=F("Montserrat-Black", 56), fill=WHITE + (255,), anchor="mm")
    put(fr, shadowed(seal, 20, 12, .5), W / 2, 760, a, pop(t, s, .34, 1.1), rot=-6 * (1 - eo((t - s) / .4)))
def scene_cta(fr, t):
    s = tk(9, 0)[0] - 0.08; a = fade_in(t, s, 0.12)
    if a <= 0: return
    put(fr, emo("🔗", 120), W / 2, 460, a, pop(t, s, .3, 1.12))
    put(fr, txt("LINK NA BIO", F("Anton-Regular", 172), WHITE, 8), W / 2, 700, a, pop(t, s + .04, .3, 1.1))
    s2 = tk(10, 0)[0] - 0.05; k = pop(t, s2, .3, 1.1)
    if k > 0:
        pill = rrect(900, 124, 62, YEL + (255,)); ImageDraw.Draw(pill).text((450, 64), "SIGA @teacher.eliezio", font=F("Montserrat-Black", 54), fill=INK + (255,), anchor="mm")
        put(fr, shadowed(pill, 16, 10, .45), W / 2, 960, fade_in(t, s2, .1), k)

def render(t):
    fr = Image.fromarray(BG).convert("RGBA")
    header(fr)
    for sc in (scene_hook, scene_travou, scene_title, scene_cards, scene_bubbles, scene_pdf, scene_gratis, scene_price, scene_garantia, scene_cta): sc(fr, t)
    caption(fr, t); avatar(fr, t); progress(fr, t)
    return fr.convert("RGB")

# ---------- áudio ----------
def audio(out):
    ev = []
    for t0, kind in ((2.75, "w"), (tk(2, 7)[0] - .12, "w"), (tk(3, 0)[0] - .08, "w"), (tk(5, 0)[0] - .1, "w"), (tk(5, 16)[0] - .15, "p"), (tk(6, 1)[0] - .12, "w"), (tk(7, 0)[0] - .12, "w"), (tk(8, 2)[0] - .1, "w"), (tk(9, 0)[0] - .1, "w")):
        ev.append((t0, sfx.whoosh(0.3) if kind == "w" else sfx.paper(), 0.10 if kind == "w" else 0.16))
    ev += [(2.85, sfx.click(5), 0.20), (3.72, sfx.click(8), 0.18), (tk(2, 7)[0] - .05, sfx.click(11), 0.18)]
    for i in range(6): ev.append((tk(4, CARDIDX[i])[0] - .04, sfx.click(11 + i), 0.20))
    for i, j in enumerate((4, 7, 12)): ev.append((tk(5, j)[0] + .18, sfx.click(21 + i), 0.20))
    ev += [(tk(7, 1)[0] - .04, sfx.click(31), 0.18), (tk(7, 3)[0] - .04, sfx.thud(), 0.22), (tk(7, 3)[0] - .04, sfx.siga(), 0.14),
           (tk(8, 2)[0] - .05, sfx.thud(), 0.18), (tk(9, 0)[0] - .05, sfx.click(41), 0.20), (tk(10, 0)[0] - .05, sfx.siga(), 0.14), (0.2, sfx.barra(), 0.0)]
    sfx.build(ev, END + 1, "sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "oficial.mp3", "-i", "prof.mp3", "-i", "sfx.wav", "-i", "song.wav", "-filter_complex",
        f"[0:a]aresample=48000,volume=1.0,adelay={int(OF_AT*1000)}|{int(OF_AT*1000)}[o];"
        f"[1:a]aresample=48000,highpass=f=80,acompressor=threshold=0.12:ratio=2.5:attack=8:release=120,adelay={int(OFF*1000)}|{int(OFF*1000)}[p];"
        f"[o][p]amix=inputs=2:normalize=0,asplit=2[v][vk];[3:a]aresample=48000,atrim=0:{END+1:.2f},volume=0.20[m];"
        f"[m][vk]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[md];[2:a]aresample=48000[s];"
        f"[v][s][md]amix=inputs=3:normalize=0:duration=longest,atrim=0:{END:.3f},afade=t=out:st={END-0.4:.3f}:d=0.4[a]",
        "-map", "[a]", "-c:a", "pcm_s16le", out], check=True)

if __name__ == "__main__":
    a = sys.argv[1]
    if a.startswith("frames:"):
        ims = []
        for ts in a[7:].split(","):
            im = render(float(ts)); im.save(f"vf_{ts}.jpg", quality=88); ims.append(im.resize((360, 640)))
        m = Image.new("RGB", (360 * min(6, len(ims)), 640 * math.ceil(len(ims) / 6)))
        for i, im in enumerate(ims): m.paste(im, ((i % 6) * 360, (i // 6) * 640))
        m.save("vf_sheet.jpg", quality=86); sys.exit()
    audio("mix.wav")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "mix.wav",
        "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", a], stdin=subprocess.PIPE)
    n = int(END * FPS)
    for i in range(n):
        enc.stdin.write(render(i / FPS).tobytes())
        if i % 150 == 0: print(i, n, flush=True)
    enc.stdin.close(); enc.wait(); print("ok", a, n)
