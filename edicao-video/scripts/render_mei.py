"""Perdão de dívidas do MEI e as novas regras (LC 238/2026), 9:16, ~55 s: sanção, o que é perdoado (dívidas federais até
13/10/2026, com multas e juros, automático), o que fica de fora (ICMS e ISS), a condição (DAS em dia por 6 meses a partir de 2027),
novo teto (81 → 110 → 140 mil), até 2 funcionários, dívida com banco só com renegociação, e opinião marcada. Voz do ElevenLabs."""
import sys, math, subprocess, importlib.util, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("rex", f"{S}/work/render_exercito.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; eo = R.ease_out; ei = R.ease_in; eio = R.ease_io; bo = R.back_out
V = f"{S}/v93"; FD = f"{S}/fontdl"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
EDIT_END = 54.6; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = EDIT_END; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
GOLD = R.GOLD; GOLD_L = R.GOLD_L; NAVY = R.NAVY; WHITE = (255, 255, 255); RED = (226, 52, 52); GREEN_BR = (40, 150, 90); YEL = (255, 214, 64); INK = (20, 24, 34)
def ANTON(s): return ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s)
MF = R.MF
# ---------------------------------------------------------------- legenda (texto revisado à mão)
CAPTXT = [(0.12, 2.34, "Saiu o perdão de dívidas do MEI."), (2.68, 4.16, "Vou te explicar como funciona."), (4.60, 7.89, "O presidente Lula sancionou a lei no dia 21 de outubro."),
          (8.28, 13.42, "As dívidas federais do MEI até 13 de outubro de 2026 serão perdoadas,"), (13.72, 14.93, "com multas e juros."), (15.25, 17.75, "É automático: não precisa pedir nada."),
          (18.14, 18.86, "Mas atenção:"), (19.19, 22.40, "ICMS e ISS ficam de fora."), (22.78, 24.37, "E, para manter o perdão,"),
          (24.54, 29.39, "você precisa pagar o DAS em dia nos seis meses depois que a regra começar a valer,"), (29.66, 30.78, "em 2027."), (31.16, 31.74, "Tem mais:"),
          (32.06, 37.15, "o teto do MEI sobe de 81 mil para 110 mil reais em 2027,"), (37.50, 40.07, "e para 140 mil em 2028."), (40.42, 43.32, "E o MEI vai poder contratar até dois funcionários."),
          (43.70, 45.76, "Dívida com banco não é perdoada,"), (46.06, 48.68, "mas está prevista uma renegociação com desconto."), (49.17, 52.33, "Na minha opinião, é um alívio para quem vive do próprio trabalho."),
          (52.70, 53.27, "Você é MEI?"), (53.66, 54.24, "Comenta aqui.")]
HOT = {"PERDÃO", "MEI.", "LULA", "SANCIONOU", "21", "FEDERAIS", "PERDOADAS,", "MULTAS", "JUROS.", "AUTOMÁTICO:", "NADA.", "ATENÇÃO:", "ICMS", "ISS", "FORA.",
       "DAS", "SEIS", "MESES", "2027.", "TETO", "81", "110", "140", "DOIS", "FUNCIONÁRIOS.", "BANCO", "NÃO", "RENEGOCIAÇÃO", "DESCONTO.", "OPINIÃO,", "ALÍVIO", "MEI?", "AQUI."}
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
CARDS = [(0.6, 18.0, "PROSPERA MEI", ["DÍVIDAS FEDERAIS", "PERDOADAS"]), (18.0, 31.0, "ATENÇÃO", ["DAS EM DIA", "POR 6 MESES"]), (31.0, 43.6, "NOVO TETO", ["R$ 110 MIL EM 2027", "R$ 140 MIL EM 2028"]),
         (43.6, 49.0, "BANCOS", ["SÓ RENEGOCIAÇÃO", "COM DESCONTO"]), (49.0, EDIT_END, "OPINIÃO", ["UM ALÍVIO PARA", "QUEM TRABALHA"])]
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
def doc(lines_on):
    w, h = 720, 470; im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 18, fill=(250, 248, 240, 255), outline=(200, 196, 180, 255), width=3)
    d.text((w / 2, 50), "DÍVIDA COM A UNIÃO", font=MF("ExtraBold", 34), fill=(20, 24, 34, 255), anchor="mm")
    y = 110
    for ln in lines_on:
        if ln is None: d.rounded_rectangle((60, y, w - 60 - (y * 7) % 160, y + 12), 6, fill=(205, 205, 205, 255)); y += 34
        else: d.text((w / 2, y + 8), ln, font=MF("ExtraBold", 32), fill=(20, 24, 34, 255), anchor="mm"); y += 56
    return im
def overlays(fr, t):
    # 0-4.5: abertura
    k = env(t, 0.0, 4.5, 0.2)
    if k > 0:
        put(fr, chipimg("NOVA LEI", GOLD, 40, NAVY), CX, 330, k, 0.8 + 0.2 * bo(t / 0.4))
        put(fr, txt("PERDÃO", ANTON(170), WHITE, 8, NAVY), CX, 520, k, 0.85 + 0.15 * bo(t / 0.45))
        put(fr, txt("DE DÍVIDAS", ANTON(130), WHITE, 7, NAVY), CX, 690, k, 0.85 + 0.15 * bo((t - 0.15) / 0.45))
        put(fr, txt("DO MEI", ANTON(170), GOLD_L, 8, NAVY), CX, 860, k, 0.85 + 0.15 * bo((t - 0.3) / 0.45))
        if t > 2.7: put(fr, chipimg("COMO FUNCIONA", NAVY, 40), CX, 1060, env(t, 2.7, 4.5), 0.7 + 0.3 * bo((t - 2.7) / 0.3))
    # 4.5-8.2: sanção
    k = title(fr, t, 4.5, 8.25, "SANCIONADA", "Lei Complementar 238/2026 · Prospera MEI")
    if k > 0:
        put(fr, emoji("✍️", 150), CX, 650, k, 0.6 + 0.4 * bo((t - 4.7) / 0.4))   # sem 📅: o emoji mostra outra data
        if t > 6.0: put(fr, txt("21 DE OUTUBRO", ANTON(110), GOLD_L, 7, NAVY), CX, 840, env(t, 6.0, 8.25), 0.7 + 0.3 * bo((t - 6.0) / 0.35))
    # 8.2-18: o que é perdoado
    k = env(t, 8.2, 18.05)
    if k > 0:
        lines = [None, "dívidas federais do MEI", "até 13/10/2026", None]
        if t > 13.7: lines += ["+ multas e juros"]
        put(fr, doc(lines + [None] * (5 - len(lines) + 1)), CX, 600, k, 0.85 + 0.15 * bo((t - 8.2) / 0.4), -2)
        if t > 10.6: put(fr, stamp("PERDOADA", (40, 150, 90), 80, -12), CX + 150, 860, env(t, 10.6, 18.05), 0.6 + 0.4 * bo(clamp((t - 10.6) / 0.25), 2.2))
        if t > 15.3: put(fr, chipimg("AUTOMÁTICO · NÃO PRECISA PEDIR", (40, 150, 90), 36), CX, 1000, env(t, 15.3, 18.05), 0.7 + 0.3 * bo((t - 15.3) / 0.3))
        if t > 16.2: put(fr, txt("o que já foi pago não é devolvido", MF("SemiBold", 28), (200, 210, 230), 3), CX, 1090, env(t, 16.2, 18.05))
    # 18.1-31: atenção
    k = title(fr, t, 18.1, 31.05, "ATENÇÃO", None, 330)
    if k > 0:
        if t < 22.7:
            for i, (lab, ta) in enumerate([("ICMS", 19.2), ("ISS", 20.5)]):
                if t < ta: continue
                x = CX + (i * 2 - 1) * 210; kk = env(t, ta, 22.75)
                put(fr, chipimg(lab, NAVY, 70), x, 620, kk, 0.6 + 0.4 * bo((t - ta) / 0.35, 2)); put(fr, emoji("❌", 90), x, 760, kk, 0.5 + 0.5 * bo((t - ta - 0.2) / 0.3))
            if t > 21.0: put(fr, txt("FICAM DE FORA", ANTON(90), GOLD_L, 6, NAVY), CX, 930, env(t, 21.0, 22.75))
            if t > 21.4: put(fr, txt("são as partes estadual e municipal do DAS", MF("SemiBold", 28), (200, 210, 230), 3), CX, 1030, env(t, 21.4, 22.75))
        else:
            kk = env(t, 22.75, 31.05)
            put(fr, txt("DAS EM DIA", ANTON(110), WHITE, 7, NAVY), CX, 480, kk)
            for i in range(6):
                ta = 23.6 + i * 0.35; x = CX - 375 + i * 150
                box = Image.new("RGBA", (130, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(box)
                d.rounded_rectangle((0, 0, 129, 129), 18, fill=(14, 32, 64, 240), outline=GOLD + (255,), width=3); d.text((65, 34), f"MÊS {i + 1}", font=MF("ExtraBold", 22), fill=(200, 210, 230, 255), anchor="mm")
                if t >= ta: box.alpha_composite(emoji("✅", 56), (37, 56))
                put(fr, box, x, 660, kk, (0.6 + 0.4 * bo((t - ta) / 0.3, 2)) if t >= ta else 0.9)
            if t > 26.0: put(fr, txt("6 MESES SEGUIDOS", ANTON(80), GOLD_L, 6, NAVY), CX, 830, env(t, 26.0, 31.05))
            if t > 29.6: put(fr, chipimg("A PARTIR DE 2027", GOLD, 42, NAVY), CX, 960, env(t, 29.6, 31.05), 0.7 + 0.3 * bo((t - 29.6) / 0.3))
            if t > 27.0: put(fr, txt("atrasou? o perdão é cancelado", MF("SemiBold", 28), (200, 210, 230), 3), CX, 1070, env(t, 27.0, 31.05))
    # 31.1-40.3: teto
    k = title(fr, t, 31.1, 40.35, "TETO DO MEI", "faturamento por ano")
    if k > 0:
        hbar(fr, t, 32.1, 620, "HOJE", 81, 140, GREY, "R$ 81 MIL", k); hbar(fr, t, 34.5, 800, "2027", 110, 140, GOLD, "R$ 110 MIL", k); hbar(fr, t, 37.5, 980, "2028", 140, 140, GREEN_BR, "R$ 140 MIL", k)
    # 40.4-43.6: funcionários
    k = title(fr, t, 40.4, 43.65, "FUNCIONÁRIOS", "quantos o MEI pode contratar")
    if k > 0:
        put(fr, txt("HOJE", MF("ExtraBold", 40), (200, 210, 230), 3), CX - 230, 560, k); put(fr, txt("2027", MF("ExtraBold", 40), GOLD_L, 3), CX + 230, 560, k)
        put(fr, emoji("🧑‍🔧" if False else "👷", 140), CX - 230, 720, k, 0.6 + 0.4 * bo((t - 41.0) / 0.35))
        if t > 41.4: put(fr, emoji("👷", 140), CX + 160, 720, env(t, 41.4, 43.65), 0.6 + 0.4 * bo((t - 41.4) / 0.35))
        if t > 42.2: put(fr, emoji("👷", 140), CX + 300, 720, env(t, 42.2, 43.65), 0.6 + 0.4 * bo((t - 42.2) / 0.35, 2.4))
        put(fr, txt("1", ANTON(90), WHITE, 6, NAVY), CX - 230, 880, k); 
        if t > 42.2: put(fr, txt("ATÉ 2", ANTON(90), GOLD_L, 6, NAVY), CX + 230, 880, env(t, 42.2, 43.65))
    # 43.7-49: bancos
    k = title(fr, t, 43.7, 49.05, "DÍVIDA COM BANCO")
    if k > 0:
        put(fr, emoji("🏦", 160), CX, 610, k, 0.6 + 0.4 * bo((t - 43.8) / 0.4))
        if t > 44.6: put(fr, stamp("NÃO É PERDOADA", RED, 64, -8), CX, 800, env(t, 44.6, 49.05), 0.6 + 0.4 * bo(clamp((t - 44.6) / 0.25), 2.2))
        if t > 46.1: put(fr, chipimg("RENEGOCIAÇÃO COM DESCONTO", NAVY, 38), CX, 980, env(t, 46.1, 49.05), 0.7 + 0.3 * bo((t - 46.1) / 0.3)); put(fr, txt("prevista · regras ainda serão definidas", MF("SemiBold", 26), (200, 210, 230), 3), CX, 1070, env(t, 46.6, 49.05))
    # 49.1-52.6: opinião
    k = env(t, 49.1, 52.65)
    if k > 0:
        put(fr, chipimg("NA MINHA OPINIÃO", (30, 30, 40), 40, GOLD_L), CX, 380, k)
        if t > 50.0: put(fr, txt("UM ALÍVIO", ANTON(150), GOLD_L, 8, NAVY), CX, 580, env(t, 50.0, 52.65), 0.8 + 0.2 * bo((t - 50.0) / 0.35))
        if t > 50.6: put(fr, txt("para quem vive do", MF("ExtraBold", 46), WHITE, 3), CX, 740, env(t, 50.6, 52.65)); put(fr, txt("próprio trabalho", MF("ExtraBold", 46), WHITE, 3), CX, 810, env(t, 50.8, 52.65))
        if t > 51.2: put(fr, emoji("💪", 130), CX, 970, env(t, 51.2, 52.65))
    # 52.6-fim
    k = env(t, 52.6, EDIT_END + 0.4, 0.3, 0.3)
    if k > 0:
        put(fr, txt("VOCÊ É", ANTON(130), WHITE, 7, NAVY), CX, 520, k, 0.9 + 0.1 * bo((t - 52.6) / 0.4)); put(fr, txt("MEI?", ANTON(170), GOLD_L, 8, NAVY), CX, 700, k)
        put(fr, chipimg("COMENTA AQUI", RED, 46), CX, 900, k, 1 + 0.04 * math.sin(t * 6))
    if 0.5 < t < EDIT_END: R.credit(fr, "Fontes: Agência Brasil, PGFN, InfoMoney, Fenacon", W - 30, 168, clamp((t - 0.5) / 0.4))
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); fr = Image.fromarray(OCEAN).convert("RGBA")
    overlays(fr, tt)
    g = np.zeros((520, W, 4), np.uint8); g[..., :3] = (3, 10, 22); g[..., 3] = np.linspace(0, 210, 520)[:, None].astype(np.uint8); fr.alpha_composite(Image.fromarray(g), (0, H - 520))
    M.caption(fr, tt, CAP_Y, 54)
    for a_, b_, kick, lines in CARDS:
        kc = clamp((tt - a_) / 0.4) * (1 - clamp((tt - (b_ - 0.3)) / 0.3))
        if kc > 0: BAR.lower_card(fr, kick, lines, CARD_Y, kc, fs=40)
    cta = clamp((t - 52.6) / 0.4) if t > 52.6 else 0.0
    BAR.draw_bar(fr, clamp(t / END_IN), "canal", eo((t - 0.2) / 0.6), cta, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(fr, t)
    if t >= END_IN: fr.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return fr.convert("RGB")
def capa(out, var="A"):
    fr = Image.fromarray(OCEAN).convert("RGBA")
    if var == "A":
        put(fr, chipimg("NOVA LEI SANCIONADA", GOLD, 44, NAVY), CX, 250)
        put(fr, txt("PERDÃO", ANTON(180), WHITE, 8, NAVY), CX, 430); put(fr, txt("DE DÍVIDAS", ANTON(130), WHITE, 7, NAVY), CX, 600); put(fr, txt("DO MEI", ANTON(180), GOLD_L, 8, NAVY), CX, 770)
        put(fr, doc([None, "dívidas federais do MEI", "até 13/10/2026", None, "+ multas e juros", None]), CX, 1120, 1, 0.8, -3)
        put(fr, stamp("PERDOADA", (40, 150, 90), 96, -12), CX + 70, 1150); put(fr, chipimg("QUEM TEM DIREITO?", RED, 44), CX, 1420)
    else:
        put(fr, txt("MEI:", ANTON(150), GOLD_L, 8, NAVY), CX, 300); put(fr, txt("O QUE MUDA", ANTON(130), WHITE, 7, NAVY), CX, 460)
        hbar(fr, 99, 0, 680, "HOJE", 81, 140, GREY, "R$ 81 MIL"); hbar(fr, 99, 0, 860, "2027", 110, 140, GOLD, "R$ 110 MIL"); hbar(fr, 99, 0, 1040, "2028", 140, 140, GREEN_BR, "R$ 140 MIL")
        put(fr, chipimg("ATÉ 2 FUNCIONÁRIOS", NAVY, 44), CX, 1200); put(fr, chipimg("PERDÃO DE DÍVIDAS", (40, 150, 90), 44), CX, 1320)
    BAR.draw_bar(fr, 0.0, "canal"); fr.alpha_composite(R.top, (R.HDX, 0)); fr.convert("RGB").save(out, quality=95)
def audio(vout):
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{V}/vo.mp3", "-ar", "48000", "-ac", "2", f"{V}/vo48.wav"], check=True)
    vo = R.readw(f"{V}/vo48.wav"); vt = np.zeros((n, 2), np.float32); vt[:min(len(vo), n)] = vo[:n]
    bed = R.readw(f"{S}/v49/bed.wav"); xf = int(1.5 * SR); loop = bed.copy()
    while len(loop) < n:
        r = np.linspace(0, 1, xf)[:, None]; loop[-xf:] = loop[-xf:] * (1 - r) + bed[:xf] * r; loop = np.concatenate([loop, bed[xf:]])
    tl = np.arange(n) / SR; gain = 0.09 * np.clip(tl / 1.0, 0, 1) * np.clip(1 - (tl - (TOTAL - 1.8)) / 1.6, 0, 1)
    R.writew(f"{V}/voice.wav", vt); R.writew(f"{V}/song.wav", loop[:n] * gain[:, None])
    def pop():
        tt = np.arange(int(0.12 * SR)) / SR; y = np.sin(2 * np.pi * (500 + 900 * tt / 0.12) * tt) * np.exp(-tt / 0.03); return np.stack([y, y], 1)
    ev = [(a - 0.15, sfx.whoosh(0.5), 0.15) for a in (4.5, 8.2, 18.1, 31.1, 40.4, 43.7, 49.1, 52.6)]
    ev += [(x, pop(), 0.3) for x in (2.7, 6.0, 8.4, 13.7, 15.3, 19.2, 20.5, 32.1, 34.5, 37.5, 41.0, 42.2, 46.1)]
    ev += [(23.6 + i * 0.35, sfx.click(seed=i), 0.22) for i in range(6)] + [(x, sfx.thud(0.4), 0.28) for x in (10.6, 44.6, 50.0)] + [(END_IN - 0.3, sfx.whoosh(0.6), 0.2)]
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
