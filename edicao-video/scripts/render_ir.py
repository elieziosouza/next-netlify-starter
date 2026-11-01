"""Isenção do IR até R$ 5 mil, 9:16, ~45 s, narração do ElevenLabs. Holerite com o IR zerando, "não é isenção, é desconto que zera",
régua de salários (até 5 mil zero, 5 mil a 7.350 paga menos, acima igual), quem paga a conta (dividendos acima de R$ 50 mil/mês com 10% na fonte,
imposto mínimo para renda acima de R$ 600 mil/ano). Sem opinião. Formato loop. Fontes: Lei 15.270/2025, XP, Barbieri Advogados."""
import sys, math, subprocess, importlib.util, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("rex", f"{S}/work/render_exercito.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; eo = R.ease_out; ei = R.ease_in; eio = R.ease_io; bo = R.back_out
V = f"{S}/ir5mil"; FD = f"{S}/fontdl"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
EDIT_END = 45.25; TOTAL = EDIT_END; END_IN = TOTAL + 99   # loop: nenhuma tela final, acaba 0,37 s depois da voz
R.FIN_IN = EDIT_END + 99; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
GOLD = R.GOLD; GOLD_L = R.GOLD_L; NAVY = R.NAVY; WHITE = (255, 255, 255); RED = (226, 52, 52); GREEN = (60, 200, 120); YEL = (255, 196, 54); INK = (20, 24, 34)
def ANTON(s): return ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s)
MF = R.MF
# ---------------------------------------------------------------- legenda (tempos do silencedetect + ASR, texto revisado à mão)
CAPTXT = [(0.05, 2.66, "Quem ganha até 5 mil reais por mês"), (2.76, 4.16, "não paga mais Imposto de Renda."),
          (4.41, 6.77, "Mas tem detalhes que muita gente não sabe."), (7.02, 10.22, "A regra vale desde janeiro de 2026."),
          (10.37, 12.94, "E, tecnicamente, não é uma isenção:"), (13.33, 16.87, "é um desconto que zera o imposto de quem ganha até 5 mil."),
          (17.23, 20.63, "Quem ganha entre 5 mil e 7.350"), (20.8, 23.87, "também paga menos, com um desconto que vai diminuindo."),
          (24.29, 26.03, "Acima disso, nada muda."), (26.43, 27.44, "E quem paga a conta?"),
          (27.88, 32.25, "Quem recebe mais de 50 mil reais por mês em dividendos"), (32.36, 35.13, "de uma mesma empresa passa a ter 10% retidos na fonte."),
          (35.35, 39.63, "E quem ganha mais de 600 mil por ano entra num imposto mínimo,"), (39.77, 41.44, "que pode chegar a 10%."),
          (41.88, 42.92, "Você foi beneficiado?"), (43.31, 44.8, "Comenta aqui e me segue.")]
HOT = {"5", "MIL", "NÃO", "IMPOSTO", "RENDA.", "DETALHES", "JANEIRO", "2026.", "ISENÇÃO:", "DESCONTO", "ZERA", "7.350", "MENOS,", "DIMINUINDO.", "NADA", "MUDA.",
       "CONTA?", "50", "DIVIDENDOS", "MESMA", "10%", "FONTE.", "600", "MÍNIMO,", "10%.", "BENEFICIADO?", "AQUI", "SEGUE."}
CAPS = []
for a, b, txt_ in CAPTXT:
    ws = txt_.upper().split(); n = len(ws); k = max(1, math.ceil(n / 4)); per = math.ceil(n / k); chunks = [ws[i:i + per] for i in range(0, n, per)]
    tot = sum(len(w) + 2 for w in ws); acc = 0
    for ch in chunks:
        c0 = a + (b - a) * acc / tot; ts = []
        for w in ch: ts.append(a + (b - a - 0.06) * acc / tot); acc += len(w) + 2
        CAPS.append(dict(words=ch, ts=ts, start=c0, end=a + (b - a) * acc / tot + (0.25 if ch is chunks[-1] else 0.0), src="au" if any(w in HOT for w in ch) else "me"))
for i in range(len(CAPS) - 1): CAPS[i]["end"] = min(CAPS[i]["end"], CAPS[i + 1]["start"])
R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
CARDS = [(0.4, 10.3, "IMPOSTO DE RENDA", ["ATÉ R$ 5 MIL: ZERO", "VALE DESDE JANEIRO"]), (10.3, 26.4, "COMO FUNCIONA", ["DESCONTO QUE ZERA O IR", "ATÉ R$ 7.350 PAGA MENOS"]),
         (26.4, 41.8, "QUEM PAGA A CONTA", ["DIVIDENDOS: 10% NA FONTE", "IMPOSTO MÍNIMO ATÉ 10%"]), (41.8, EDIT_END + 0.3, "E VOCÊ?", ["COMENTA AQUI"])]
CAP_Y, CARD_Y = 1430, 1712
yy_, xx_ = np.mgrid[0:H, 0:W].astype(np.float32)
OCEAN = (np.array([6, 22, 44], np.float32) + np.array([10, 30, 56], np.float32) * np.clip(1 - np.sqrt(((xx_ - W / 2) / W) ** 2 + ((yy_ - 700) / H) ** 2) * 1.6, 0, 1)[..., None])
OCEAN[::60, :] += 5; OCEAN[:, ::60] += 5
OCEAN = np.clip(OCEAN, 0, 255).astype(np.uint8); del yy_, xx_
GREY = (120, 132, 156)
# ---------------------------------------------------------------- elementos
_emo = {}
def emoji(ch, size):
    key = (ch, size)
    if key not in _emo:
        f = ImageFont.truetype(EMOJI, 109); im = Image.new("RGBA", (180, 160), (0, 0, 0, 0)); ImageDraw.Draw(im).text((8, 8), ch, font=f, embedded_color=True)
        bb = im.getbbox(); im = im.crop(bb) if bb else im; sc = size / max(im.size); _emo[key] = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    return _emo[key]
_tx = {}
def txt(t_, f, col, stroke=0, scol=(0, 0, 0)):
    key = (t_, f.path, f.size, col, stroke)
    if key not in _tx:
        bb = f.getbbox(t_); im = Image.new("RGBA", (bb[2] - bb[0] + 16 + 2 * stroke, bb[3] - bb[1] + 16 + 2 * stroke), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((8 - bb[0] + stroke, 8 - bb[1] + stroke), t_, font=f, fill=col + (255,), stroke_width=stroke, stroke_fill=scol + (255,)); _tx[key] = im
    return _tx[key]
def put(fr, im, cx, cy, al=1.0, sc=1.0, rot=0):
    if al <= 0.01: return
    if abs(sc - 1) > 0.004: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
    if rot: im = im.rotate(rot, Image.BICUBIC, expand=True)
    fr.alpha_composite(R.fade(im, al), (int(cx - im.width / 2), int(cy - im.height / 2)))
def env(t, a, b, fi=0.3, fo=0.25): return clamp((t - a) / fi) * clamp((b - t) / fo)
def dashed(d, pts, col, w, dash=22, gap=14):
    acc = 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        if L < 1e-3: continue
        p = 0.0
        while p < L:
            on = (acc + p) % (dash + gap) < dash; q = min(L, p + 4)
            if on: d.line((x0 + (x1 - x0) * p / L, y0 + (y1 - y0) * p / L, x0 + (x1 - x0) * q / L, y0 + (y1 - y0) * q / L), fill=col, width=w)
            p = q
        acc += L
def path(a, b, g, bend=0.18, n=40):
    a, b = np.array(a), np.array(b); m = (a + b) / 2; nrm = np.array([-(b - a)[1], (b - a)[0]]) * bend
    pts = [tuple((1 - u) ** 2 * a + 2 * (1 - u) * u * (m + nrm) + u * u * b) for u in np.linspace(0, 1, n)]
    k = max(2, int(n * clamp(g))); return pts[:k]
def pin(fr, x, y, label, col, al, sub=None, dy=-52):
    if al <= 0: return
    d = ImageDraw.Draw(fr); a = int(255 * al)
    d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=col + (a,), outline=WHITE + (a,), width=4)
    put(fr, chipimg(label, col, 30), x, y + dy, al)
    if sub: put(fr, txt(sub, MF("SemiBold", 24), WHITE, 3), x, y + 40, al)
_ch = {}
def chipimg(t_, fill, size=30, col=WHITE):
    key = (t_, fill, size, col)
    if key not in _ch:
        f = MF("ExtraBold", size); w = int(f.getlength(t_)) + 36; h = int(size * 1.7)
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=fill + (255,), outline=WHITE + (255,), width=3)
        d.text((w / 2, h / 2 + 1), t_, font=f, fill=col + (255,), anchor="mm"); _ch[key] = im
    return _ch[key]
def stamp(t_, col, size=70, rot=-10):
    f = ANTON(size); bb = f.getbbox(t_); w, h = bb[2] - bb[0] + 60, bb[3] - bb[1] + 50
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, w - 5, h - 5), 12, fill=(255, 255, 255, 230), outline=col + (255,), width=9); d.text((30 - bb[0], 25 - bb[1]), t_, font=f, fill=col + (255,))
    return im.rotate(rot, Image.BICUBIC, expand=True)
def title(fr, t, a, b, s, sub=None, y=360):
    k = env(t, a, b)
    if k <= 0: return 0
    put(fr, txt(s, ANTON(92), WHITE, 6, NAVY), CX, y, k, 0.85 + 0.15 * bo((t - a) / 0.4))
    if sub: put(fr, txt(sub, MF("SemiBold", 28), (200, 210, 230), 3), CX, y + 78, k)
    return k
def hbar(fr, t, ta, y, lab, val, vmax, col, vtxt, al=1.0, L=560, x0=190):
    if t < ta: return
    g = eo((t - ta) / 0.9); kk = al * clamp((t - ta) / 0.25); d = ImageDraw.Draw(fr)
    li = txt(lab, MF("ExtraBold", 34), WHITE, 3); put(fr, li, x0 + li.width / 2, y - 52, kk)
    w = max(24, int(L * val / vmax * g)); d.rounded_rectangle((x0, y - 28, x0 + w, y + 28), 28, fill=col + (int(255 * kk),))
    im = txt(vtxt, ANTON(52), WHITE, 5, NAVY); put(fr, im, x0 + w + 20 + im.width / 2, y, kk)
# ---------------------------------------------------------------- cenas
PAPER = (250, 248, 240); INKP = (24, 28, 36); SUB = (200, 210, 230)
def holerite(t, t_zero):
    """holerite ilustrativo: a linha do IR vira R$ 0,00 em t_zero"""
    w, h = 600, 470; im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 18, fill=PAPER + (255,))
    d.rounded_rectangle((0, 0, w - 1, 86), 18, fill=(30, 52, 96, 255)); d.rectangle((0, 60, w - 1, 86), fill=(30, 52, 96, 255))
    d.text((w / 2, 44), "HOLERITE", font=MF("ExtraBold", 38), fill=WHITE + (255,), anchor="mm")
    f = MF("ExtraBold", 32); fs = MF("SemiBold", 24); y = 120
    d.text((36, y), "SALÁRIO", font=f, fill=INKP + (255,)); d.text((w - 36, y), "R$ 5.000,00", font=f, fill=INKP + (255,), anchor="ra"); y += 70
    for x in range(30, w - 30, 16): d.line((x, y, x + 8, y), fill=(170, 170, 170, 255), width=2)
    y += 34; g = eo(clamp((t - t_zero) / 0.35))
    d.rounded_rectangle((24, y - 14, w - 24, y + 56), 12, fill=tuple(int(a + (b - a) * g) for a, b in zip((236, 230, 216), (205, 240, 215))) + (255,))
    d.text((40, y), "IMPOSTO DE RENDA", font=f, fill=INKP + (255,))
    if t < t_zero:
        d.text((w - 40, y), "R$ ???", font=f, fill=RED + (255,), anchor="ra")
    else:
        d.text((w - 40, y), "R$ 0,00", font=f, fill=(20, 120, 70, 255), anchor="ra")
    y += 100; d.text((w / 2, y), "exemplo ilustrativo · regra de 2026", font=fs, fill=(110, 116, 128, 255), anchor="mm")
    return im
def ruler(fr, t, t_g, t_y, t_dim, t_gr, y=640):
    """régua de salários: até 5 mil (verde), 5 mil a 7.350 (amarelo, desconto diminuindo), acima (cinza)"""
    d = ImageDraw.Draw(fr); x0, x1 = 90, W - 90; xa = x0 + (x1 - x0) * 0.42; xb = x0 + (x1 - x0) * 0.70; hh = 70
    def seg(xs, xe, col, g, grad=False):
        if g <= 0: return
        xe2 = xs + (xe - xs) * eo(g)
        if grad:
            for xx in range(int(xs), int(xe2)):
                u = (xx - xs) / max(1, xe - xs); c = tuple(int(a + (b - a) * u) for a, b in zip(col, (150, 150, 150)))
                d.line((xx, y - hh / 2, xx, y + hh / 2), fill=c + (255,))
        else: d.rectangle((xs, y - hh / 2, xe2, y + hh / 2), fill=col + (255,))
    seg(x0, xa, GREEN, clamp((t - t_g) / 0.6)); seg(xa, xb, YEL, clamp((t - t_y) / 0.6), t > t_dim); seg(xb, x1, (120, 132, 156), clamp((t - t_gr) / 0.6))
    for xx, lab, ta in ((x0, "R$ 0", t_g), (xa, "5 MIL", t_g + 0.3), (xb, "7.350", t_y + 0.3)):
        if t > ta:
            k = clamp((t - ta) / 0.3); d.line((xx, y - hh / 2 - 16, xx, y + hh / 2 + 16), fill=WHITE + (int(255 * k),), width=4)
            put(fr, txt(lab, MF("ExtraBold", 30), WHITE, 3), min(max(xx, x0 + 50), x1 - 50), y + hh / 2 + 44, k)
    for xm, lab, col, ta, em in (((x0 + xa) / 2, "ZERO", GREEN, t_g + 0.4, "✅"), ((xa + xb) / 2, "PAGA\nMENOS", YEL, t_y + 0.4, "⬇️"), ((xb + x1) / 2, "IGUAL", (170, 180, 200), t_gr + 0.3, "➖")):
        if t > ta:
            k = clamp((t - ta) / 0.3); sc = 0.6 + 0.4 * bo((t - ta) / 0.35, 2)
            lines = lab.split("\n")
            for j, ln in enumerate(lines): put(fr, txt(ln, ANTON(54), col, 5, NAVY), xm, y - 110 - (len(lines) - 1 - j) * 60, k, sc)
    if t > t_dim: put(fr, txt("o desconto diminui até sumir em 7.350", MF("SemiBold", 28), SUB, 3), CX, y + 170, clamp((t - t_dim) / 0.3))
def overlays(fr, t):
    # 0-4.4: hook
    k = env(t, 0.0, 4.4, 0.2)
    if k > 0:
        put(fr, chipimg("IMPOSTO DE RENDA", GOLD, 38, NAVY), CX, 280, k, 0.8 + 0.2 * bo(t / 0.4))
        put(fr, txt("ATÉ R$ 5 MIL", ANTON(150), GOLD_L, 8, NAVY), CX, 440, k, 0.85 + 0.15 * bo((t - 0.1) / 0.4))
        put(fr, holerite(t, 3.0), CX, 820, k, 0.92 + 0.08 * eo(t / 0.4), -2)
        if t > 3.2: put(fr, stamp("ZERO", GREEN, 90, -10), CX + 170, 1060, env(t, 3.2, 4.4), 0.6 + 0.4 * bo(clamp((t - 3.2) / 0.25), 2.2))
    # 4.4-7.0: detalhes
    k = env(t, 4.4, 7.0)
    if k > 0:
        put(fr, emoji("🔍", 170), CX, 460, k, 0.6 + 0.4 * bo((t - 4.4) / 0.4))
        put(fr, txt("TEM DETALHES", ANTON(110), WHITE, 7, NAVY), CX, 660, k, 0.85 + 0.15 * bo((t - 4.5) / 0.4))
        put(fr, txt("que muita gente não sabe", MF("SemiBold", 34), SUB, 3), CX, 770, env(t, 5.2, 7.0))
    # 7.0-10.3: janeiro de 2026
    k = env(t, 7.0, 10.3)
    if k > 0:
        put(fr, txt("VALE DESDE", ANTON(96), WHITE, 7, NAVY), CX, 330, k, 0.85 + 0.15 * bo((t - 7.0) / 0.4))
        cal = Image.new("RGBA", (420, 400), (0, 0, 0, 0)); dc = ImageDraw.Draw(cal)
        dc.rounded_rectangle((0, 0, 419, 399), 30, fill=PAPER + (255,)); dc.rounded_rectangle((0, 0, 419, 120), 30, fill=RED + (255,)); dc.rectangle((0, 90, 419, 120), fill=RED + (255,))
        dc.text((210, 62), "JANEIRO", font=ANTON(72), fill=WHITE + (255,), anchor="mm"); dc.text((210, 262), "2026", font=ANTON(150), fill=INKP + (255,), anchor="mm")
        put(fr, cal, CX, 680, env(t, 7.4, 10.3), 0.6 + 0.4 * bo((t - 7.4) / 0.4, 2), -4)
        if t > 8.6: put(fr, txt("no salário de janeiro em diante", MF("SemiBold", 30), SUB, 3), CX, 950, env(t, 8.6, 10.3))
    # 10.3-17.2: não é isenção, é desconto
    k = env(t, 10.3, 17.2)
    if k > 0:
        put(fr, txt("TECNICAMENTE…", ANTON(80), SUB, 6, NAVY), CX, 300, k)
        ki = env(t, 10.9, 17.2); put(fr, txt("ISENÇÃO", ANTON(130), WHITE, 7, NAVY), CX, 470, ki, 0.85 + 0.15 * bo((t - 10.9) / 0.4))
        if t > 11.9:
            g = eo(clamp((t - 11.9) / 0.3)); d = ImageDraw.Draw(fr); w0 = 300
            d.line((CX - w0, 470, CX - w0 + 2 * w0 * g, 470), fill=RED + (int(255 * ki),), width=16)
            put(fr, chipimg("NÃO É", RED, 44), CX, 590, env(t, 11.9, 17.2), 0.6 + 0.4 * bo((t - 11.9) / 0.3, 2))
        if t > 13.4: put(fr, stamp("DESCONTO QUE ZERA", GREEN, 74, -6), CX, 800, env(t, 13.4, 17.2), 0.6 + 0.4 * bo(clamp((t - 13.4) / 0.25), 2.2))
        if t > 14.6: put(fr, txt("a tabela continua; um redutor abate o imposto", MF("SemiBold", 28), SUB, 3), CX, 960, env(t, 14.6, 17.2))
        if t > 15.6: put(fr, txt("até R$ 5 mil, o desconto cobre tudo", MF("SemiBold", 28), SUB, 3), CX, 1010, env(t, 15.6, 17.2))
    # 17.2-26.4: régua
    k = env(t, 17.2, 26.4)
    if k > 0:
        put(fr, txt("QUANTO VOCÊ PAGA", ANTON(92), WHITE, 7, NAVY), CX, 300, k, 0.85 + 0.15 * bo((t - 17.2) / 0.4))
        ruler(fr, t, 17.3, 18.2, 21.6, 24.3)
        if t > 24.3: put(fr, chipimg("ACIMA DE R$ 7.350: NADA MUDA", (80, 92, 120), 40), CX, 1060, env(t, 24.3, 26.4), 0.7 + 0.3 * bo((t - 24.3) / 0.3))
    # 26.4-27.9: quem paga a conta
    k = env(t, 26.4, 27.9, 0.2)
    if k > 0:
        put(fr, emoji("💰", 190), CX, 480, k, 0.5 + 0.5 * bo((t - 26.4) / 0.35, 2.2))
        put(fr, txt("QUEM PAGA", ANTON(130), WHITE, 7, NAVY), CX, 700, k, 0.85 + 0.15 * bo((t - 26.5) / 0.35)); put(fr, txt("A CONTA?", ANTON(140), GOLD_L, 8, NAVY), CX, 860, k)
    # 27.9-35.3: dividendos
    k = env(t, 27.9, 35.3)
    if k > 0:
        put(fr, chipimg("DIVIDENDOS", GOLD, 52, NAVY), CX, 300, k, 0.7 + 0.3 * bo((t - 27.9) / 0.35))
        put(fr, txt("ACIMA DE", ANTON(70), WHITE, 5, NAVY), CX, 430, env(t, 28.3, 35.3))
        put(fr, txt("R$ 50 MIL/MÊS", ANTON(130), GOLD_L, 8, NAVY), CX, 560, env(t, 28.5, 35.3), 0.85 + 0.15 * bo((t - 28.5) / 0.35))
        if t > 32.4: put(fr, chipimg("DE UMA MESMA EMPRESA", (30, 52, 96), 38), CX, 720, env(t, 32.4, 35.3), 0.7 + 0.3 * bo((t - 32.4) / 0.3))
        if t > 33.6: put(fr, stamp("10% NA FONTE", RED, 84, -6), CX, 900, env(t, 33.6, 35.3), 0.6 + 0.4 * bo(clamp((t - 33.6) / 0.25), 2.2))
        if t > 33.9: put(fr, txt("antes, dividendo não pagava IR", MF("SemiBold", 28), SUB, 3), CX, 1050, env(t, 33.9, 35.3))
    # 35.3-41.9: imposto mínimo
    k = env(t, 35.3, 41.9)
    if k > 0:
        put(fr, txt("RENDA ACIMA DE", ANTON(70), WHITE, 5, NAVY), CX, 300, k)
        put(fr, txt("R$ 600 MIL/ANO", ANTON(124), GOLD_L, 8, NAVY), CX, 425, env(t, 35.5, 41.9), 0.85 + 0.15 * bo((t - 35.5) / 0.35))
        if t > 38.1: put(fr, chipimg("IMPOSTO MÍNIMO", RED, 52), CX, 580, env(t, 38.1, 41.9), 0.7 + 0.3 * bo((t - 38.1) / 0.3))
        if t > 39.7:
            d = ImageDraw.Draw(fr); x0, L, yb = 140, W - 280, 760; g = eo(clamp((t - 39.7) / 1.0)); kk = env(t, 39.7, 41.9)
            d.rounded_rectangle((x0, yb - 34, x0 + L, yb + 34), 34, fill=(30, 40, 66, int(230 * kk)))
            d.rounded_rectangle((x0, yb - 34, x0 + max(68, int(L * g)), yb + 34), 34, fill=GOLD + (int(255 * kk),))
            put(fr, txt(f"{10 * g:.0f}%", ANTON(64), WHITE, 5, NAVY), x0 + max(68, int(L * g)) - 70, yb, kk)
            put(fr, txt("sobe aos poucos e chega a 10% com R$ 1,2 milhão por ano", MF("SemiBold", 26), SUB, 3), CX, yb + 80, kk)
    # 41.9-fim: pergunta + CTA (sem tela final)
    k = env(t, 41.85, EDIT_END + 1, 0.3, 0.01)
    if k > 0:
        put(fr, txt("VOCÊ FOI", ANTON(120), WHITE, 7, NAVY), CX, 460, k, 0.85 + 0.15 * bo((t - 41.85) / 0.4)); put(fr, txt("BENEFICIADO?", ANTON(124), GOLD_L, 7, NAVY), CX, 620, k)
        if t > 43.3: put(fr, chipimg("COMENTA AQUI", RED, 50), CX, 820, k, (0.6 + 0.4 * bo((t - 43.3) / 0.35, 2.2)) * (1 + 0.03 * math.sin(t * 6)))
        if t > 44.0: put(fr, chipimg("SIGA PARA MAIS", GOLD, 46, NAVY), CX, 950, k, 0.6 + 0.4 * bo((t - 44.0) / 0.35, 2.2))
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); fr = Image.fromarray(OCEAN).convert("RGBA")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); overlays(lay, tt); fr.alpha_composite(lay, (0, 110))   # cenas descem 110 px
    if 0.5 < tt: R.credit(fr, "Fontes: Lei 15.270/2025, XP, Barbieri Advogados", W - 30, 168, clamp((tt - 0.5) / 0.4))
    g = np.zeros((520, W, 4), np.uint8); g[..., :3] = (3, 10, 22); g[..., 3] = np.linspace(0, 210, 520)[:, None].astype(np.uint8); fr.alpha_composite(Image.fromarray(g), (0, H - 520))
    M.caption(fr, tt, CAP_Y, 54)
    for a_, b_, kick, lines in CARDS:
        kc = clamp((tt - a_) / 0.4) * (1 - clamp((tt - (b_ - 0.3)) / 0.3))
        if kc > 0: BAR.lower_card(fr, kick, lines, CARD_Y, kc, fs=40)
    cta = clamp((t - 43.3) / 0.4) if t > 43.3 else 0.0
    BAR.draw_bar(fr, clamp(t / TOTAL), "canal", eo((t - 0.2) / 0.6), cta, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(fr, t)
    return fr.convert("RGB")
def capa(out, var="A"):
    fr = Image.fromarray(OCEAN).convert("RGBA")
    if var == "A":
        put(fr, chipimg("IMPOSTO DE RENDA", GOLD, 42, NAVY), CX, 250)
        put(fr, txt("ATÉ R$ 5 MIL", ANTON(150), GOLD_L, 8, NAVY), CX, 400); put(fr, txt("NÃO PAGA MAIS", ANTON(104), WHITE, 7, NAVY), CX, 545)
        put(fr, holerite(99, 0), CX, 900, 1, 0.95, -3); put(fr, stamp("ZERO", GREEN, 110, -10), CX + 190, 1110)
        put(fr, chipimg("MAS TEM DETALHES", RED, 44), CX, 1330)
    else:
        put(fr, txt("R$ 0", ANTON(320), GREEN, 10, NAVY), CX, 430); put(fr, chipimg("IR DE QUEM GANHA ATÉ R$ 5 MIL", GOLD, 40, NAVY), CX, 650)
        put(fr, txt("E QUEM", ANTON(120), WHITE, 7, NAVY), CX, 830); put(fr, txt("PAGA A CONTA?", ANTON(132), GOLD_L, 8, NAVY), CX, 985)
        put(fr, emoji("💰", 170), CX, 1200)
    BAR.draw_bar(fr, 0.0, "canal"); fr.alpha_composite(R.top, (R.HDX, 0)); fr.convert("RGB").save(out, quality=95)
def audio(vout):
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{V}/vo.mp3", "-ar", "48000", "-ac", "2", f"{V}/vo48.wav"], check=True)
    vo = R.readw(f"{V}/vo48.wav"); vt = np.zeros((n, 2), np.float32); vt[:min(len(vo), n)] = vo[:n]
    bed = R.readw(f"{S}/v49/bed.wav"); xf = int(1.5 * SR); loop = bed.copy()
    while len(loop) < n:
        r = np.linspace(0, 1, xf)[:, None]; loop[-xf:] = loop[-xf:] * (1 - r) + bed[:xf] * r; loop = np.concatenate([loop, bed[xf:]])
    tl = np.arange(n) / SR; gain = 0.09 * np.clip(tl / 0.3, 0, 1) * np.clip((TOTAL - tl) / 0.5, 0, 1)
    R.writew(f"{V}/voice.wav", vt); R.writew(f"{V}/song.wav", loop[:n] * gain[:, None])
    def pop():
        tt = np.arange(int(0.12 * SR)) / SR; y = np.sin(2 * np.pi * (500 + 900 * tt / 0.12) * tt) * np.exp(-tt / 0.03); return np.stack([y, y], 1)
    ev = [(a - 0.15, sfx.whoosh(0.5), 0.15) for a in (4.4, 7.0, 10.3, 17.2, 26.4, 27.9, 35.3, 41.85)]
    ev += [(x, pop(), 0.3) for x in (7.4, 11.9, 17.7, 18.6, 24.3, 28.5, 32.4, 38.1, 39.7, 43.3, 44.0)]
    ev += [(x, sfx.thud(0.4), 0.28) for x in (3.2, 13.4, 33.6)]
    sfx.build(ev, TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=70,acompressor=threshold=0.1:ratio=2.2:attack=8:release=200:makeup=1.4,asplit=2[vox][k2];[2:a]volume=0.9[sf];[3:a]volume=1.0[sg];"
                    "[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][sgd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
def main():
    if MODE == "lib": return
    if MODE.startswith("capa"): capa(OUTFILE, MODE.split(":")[1] if ":" in MODE else "A"); return
    if MODE.startswith("one:"): frame_at(float(MODE[4:])).save(OUTFILE, quality=92); return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(x).resize((360, 640), Image.LANCZOS) for x in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    NF = int(round(TOTAL * FPS))
    if MODE.startswith("part"):
        i, nparts = map(int, MODE.split(":")[1:]); a, b = NF * i // nparts, NF * (i + 1) // nparts
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", OUTFILE], stdin=subprocess.PIPE)
        for k in range(a, b): enc.stdin.write(frame_at(k / FPS).tobytes())
        enc.stdin.close(); enc.wait(); print("part done", i); return
    if MODE == "mux": audio(f"{V}/video.mp4"); print("done"); return
main()
