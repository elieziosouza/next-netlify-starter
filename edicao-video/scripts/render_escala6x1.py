"""Fim da escala 6x1 (EC 141/2026, promulgada em 16/10/2026), 9:16, ~77 s, narração do ElevenLabs com a voz do Eliezio. Sem opinião.
Calendário em cartão 3D com camadas (6x1 → 5x2), placar da votação (Senado 75 × 1, Câmara 461 × 19 no 2º turno), hoje × depois,
linha do tempo 44 h → 42 h (dez/2026) → 40 h (dez/2027), salário sem redução, 3 detalhes em cartões empilhados, quem fica de fora
(servidor público; prestadoras de serviço ao governo com 12 meses) e pergunta no fim. Formato loop. Fontes: Agência Senado,
Agência Câmara, Agência Brasil. Datas exatas (dois e catorze meses após a publicação) aparecem só como "dez/2026" e "dez/2027"."""
import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
sys.path.insert(0, f"{S}/work")
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; eo = R.ease_out; ei = R.ease_in; eio = R.ease_io; bo = R.back_out
V = f"{S}/escala6x1"; FD = f"{S}/fontdl"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
EDIT_END = 77.42; TOTAL = EDIT_END                                  # loop: acaba 0,4 s depois de "Comenta aqui embaixo"
R.FIN_IN = EDIT_END + 99; R.END_IN = EDIT_END + 99; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
GOLD = R.GOLD; GOLD_L = R.GOLD_L; NAVY = R.NAVY; WHITE = (255, 255, 255); RED = (226, 52, 52); GREEN = (46, 170, 100); BLUE = (52, 110, 190); MUTE = (200, 210, 230)
def ANTON(s): return ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s)
MF = R.MF
# ---------------------------------------------------------------- legenda (texto do roteiro, tempos da transcrição)
CAPTXT = [(0.12, 1.83, "Acabou a escala 6x1."), (2.20, 4.10, "Mas calma: não é pra amanhã."), (4.60, 6.69, "Vou te explicar o que muda e quando."),
          (7.13, 11.27, "Em outubro, o Congresso aprovou a Emenda Constitucional 141."), (11.90, 12.93, "Foi por ampla maioria:"), (13.24, 15.78, "no Senado, 75 votos a 1."),
          (16.28, 16.93, "Como é hoje?"), (17.21, 21.32, "A lei permite até 44 horas por semana, com só uma folga."),
          (21.62, 22.25, "O que muda?"), (22.49, 25.41, "Agora são duas folgas remuneradas por semana."), (25.78, 27.60, "E as horas caem em duas etapas."),
          (27.85, 28.97, "Primeira etapa:"), (29.21, 35.33, "em dezembro deste ano, o máximo cai para 42 horas por semana, já com as duas folgas."),
          (35.61, 36.55, "Segunda etapa:"), (36.82, 40.45, "em dezembro de 2027, chega a 40 horas."),
          (40.70, 41.38, "E o salário?"), (41.66, 42.95, "Não pode diminuir."), (43.32, 45.41, "A jornada cai, o salário fica."),
          (45.69, 48.55, "Agora, três detalhes que pouca gente sabe."), (48.82, 52.23, "Um: as duas folgas não precisam ser seguidas."),
          (52.57, 56.68, "Dois: quem já trabalha 40 horas ou menos continua como está."), (56.98, 63.24, "Três: em casos excepcionais, um acordo coletivo pode criar outra escala, como compensação."),
          (63.45, 64.84, "E tem quem fique de fora:"), (65.18, 68.01, "servidor público não muda, tem regra própria."),
          (68.25, 72.71, "E as empresas que prestam serviço para o governo ganham 12 meses para se adaptar."),
          (73.02, 73.86, "Agora me conta:"), (74.14, 75.69, "você trabalha 6x1 hoje?"), (76.06, 77.02, "Comenta aqui embaixo.")]
HOT = {"ACABOU", "6X1.", "6X1", "AMANHÃ.", "141.", "AMPLA", "75", "44", "FOLGA.", "DUAS", "FOLGAS", "REMUNERADAS", "ETAPAS.", "42", "DEZEMBRO", "2027,", "40",
       "SALÁRIO?", "DIMINUIR.", "FICA.", "SEGUIDAS.", "ESTÁ.", "EXCEPCIONAIS,", "COLETIVO", "FORA:", "SERVIDOR", "PRÓPRIA.", "12", "MESES", "HOJE?", "COMENTA"}
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
CARDS = [(0.4, 16.2, "FIM DA ESCALA 6x1", ["EC 141/2026", "PROMULGADA EM 16/10"]), (16.2, 40.6, "O QUE MUDA", ["2 FOLGAS POR SEMANA", "44 h → 42 h → 40 h"]),
         (40.6, 63.4, "NO SEU DIA A DIA", ["SALÁRIO NÃO CAI", "FOLGAS NÃO SEGUIDAS"]), (63.4, EDIT_END + 0.3, "QUEM FICA DE FORA", ["SERVIDOR PÚBLICO", "PRESTADORA: 12 MESES"])]
CAP_Y, CARD_Y = 1430, 1712
yy_, xx_ = np.mgrid[0:H, 0:W].astype(np.float32)
OCEAN = (np.array([6, 22, 44], np.float32) + np.array([10, 30, 56], np.float32) * np.clip(1 - np.sqrt(((xx_ - W / 2) / W) ** 2 + ((yy_ - 700) / H) ** 2) * 1.6, 0, 1)[..., None])
OCEAN[::60, :] += 5; OCEAN[:, ::60] += 5
OCEAN = np.clip(OCEAN, 0, 255).astype(np.uint8); del yy_, xx_
# ---------------------------------------------------------------- peças
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
_ch = {}
def chipimg(t_, fill, size=30, col=WHITE):
    key = (t_, fill, size, col)
    if key not in _ch:
        f = MF("ExtraBold", size); w = int(f.getlength(t_)) + 40; h = int(size * 1.7)
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=fill + (255,), outline=WHITE + (255,), width=3)
        d.text((w / 2, h / 2 + 1), t_, font=f, fill=col + (255,), anchor="mm"); _ch[key] = im
    return _ch[key]
def stamp(t_, col, size=70, rot=-8):
    f = ANTON(size); bb = f.getbbox(t_); w, h = bb[2] - bb[0] + 60, bb[3] - bb[1] + 50
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, w - 5, h - 5), 12, fill=(255, 255, 255, 235), outline=col + (255,), width=9); d.text((30 - bb[0], 25 - bb[1]), t_, font=f, fill=col + (255,))
    return im.rotate(rot, Image.BICUBIC, expand=True)
def big(fr, s, cy, size, col, k, t=None, a=None):
    sc = 0.85 + 0.15 * bo((t - a) / 0.4) if t is not None else 1.0
    im = txt(s, ANTON(size), col, max(5, size // 16), NAVY)
    while im.width > 700: size -= 6; im = txt(s, ANTON(size), col, max(5, size // 16), NAVY)
    put(fr, im, CX, cy, k, sc)
def layered(im, rad=30, plates=((30, 70), (15, 120))):
    """cartão com duas camadas douradas deslocadas por trás (padrão do canal)"""
    pad = 40; out = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(out)
    for off, al in plates: d.rounded_rectangle((pad + off, pad + off, pad + off + im.width, pad + off + im.height), rad, outline=GOLD + (al,), width=4, fill=(10, 28, 52, int(al * 0.9)))
    out.alpha_composite(im, (pad, pad)); return out
def card3d(fr, im, cx, cy, t, a, side=1, al=1.0, tilt0=0.03):
    """entra deslizando da lateral girando em profundidade (rotação Y) com desfoque de movimento, depois balança de leve"""
    u = clamp((t - a) / 0.5); k = eo(u); lay = layered(im)
    tilt = 0.10 * (1 - k) + tilt0 * (0.5 + 0.5 * math.sin(t * 0.9 + side))
    arr = R.persp(np.asarray(lay), "left" if side > 0 else "right", tilt); img = Image.fromarray(arr)
    R.paste(fr, R.fade(img, al * clamp(u / 0.4)), cx - img.width / 2 + side * 480 * (1 - k), cy - img.height / 2, 0.55, 24, (10, 22), (side * -60 * (1 - k) if u < 1 else 0, 0))
def panel(w, h, border=GOLD):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 30, fill=(10, 28, 56, 245), outline=border + (255,), width=4); return im, d
DAYS = ["SEG", "TER", "QUA", "QUI", "SEX", "SÁB", "DOM"]
def calendar(states, flip=None, title=None):
    """semana em 7 blocos: 'w' trabalho (azul), 'f' folga (dourado); flip = (índice, progresso) vira o bloco de trabalho em folga"""
    tw, th, gap = 92, 150, 10; w = 7 * tw + 6 * gap + 60; h = th + (110 if title else 60)
    im, d = panel(w, h); y0 = 80 if title else 30
    if title: d.text((w / 2, 42), title, font=MF("ExtraBold", 30), fill=GOLD_L + (255,), anchor="mm")
    for i, st in enumerate(states):
        x = 30 + i * (tw + gap); sq = 1.0
        if flip and flip[0] == i:
            p = flip[1]; sq = abs(math.cos(p * math.pi)); st = "f" if p > 0.5 else "w"
        if sq < 0.04: continue
        cw = int(tw * sq); xx = x + (tw - cw) // 2; fill = GOLD if st == "f" else BLUE
        d.rounded_rectangle((xx, y0, xx + cw, y0 + th), 18, fill=fill + (255,))
        if cw > 40:
            d.text((xx + cw / 2, y0 + 30), DAYS[i], font=MF("ExtraBold", 24), fill=(NAVY if st == "f" else WHITE) + (255,), anchor="mm")
            e = emoji("😴" if st == "f" else "💼", int(46 * sq) + 2); im.alpha_composite(e, (int(xx + cw / 2 - e.width / 2), y0 + 66))
            d.text((xx + cw / 2, y0 + 128), "FOLGA" if st == "f" else "", font=MF("ExtraBold", 18), fill=NAVY + (255,), anchor="mm")
    return im
def hours_card(lab, sub, hrs, col, w=620):
    im, d = panel(w, 150, col)
    d.text((34, 52), lab, font=MF("ExtraBold", 34), fill=WHITE + (255,), anchor="lm"); d.text((34, 104), sub, font=MF("SemiBold", 24), fill=MUTE + (255,), anchor="lm")
    d.text((w - 34, 76), f"{hrs} h", font=ANTON(84), fill=col + (255,), anchor="rm"); return im
def fit(d, s, w, f0, name="ExtraBold"):
    size = f0
    while d.textlength(s, font=MF(name, size)) > w and size > 18: size -= 2
    return MF(name, size)
def detail_card(n, l1, l2, emo, l3=None, w=720, h=250):
    im, d = panel(w, h); d.ellipse((30, 30, 120, 120), fill=GOLD + (255,)); d.text((75, 77), str(n), font=ANTON(64), fill=NAVY + (255,), anchor="mm")
    tw = w - 150 - 130
    d.text((150, 70), l1, font=fit(d, l1, tw, 34), fill=WHITE + (255,), anchor="lm"); d.text((150, 118), l2, font=fit(d, l2, tw, 34), fill=GOLD_L + (255,), anchor="lm")
    if l3: d.text((150, 170), l3, font=fit(d, l3, tw, 26, "SemiBold"), fill=MUTE + (255,), anchor="lm")
    e = emoji(emo, 80); im.alpha_composite(e, (w - e.width - 34, h - e.height - 26)); return im
def who_card(emo, l1, l2, col, w=700, h=200):
    im, d = panel(w, h, col); e = emoji(emo, 100); im.alpha_composite(e, (34, (h - e.height) // 2))
    d.text((170, 76), l1, font=fit(d, l1, w - 200, 36), fill=WHITE + (255,), anchor="lm"); d.text((170, 132), l2, font=fit(d, l2, w - 200, 30, "SemiBold"), fill=MUTE + (255,), anchor="lm"); return im
# ---------------------------------------------------------------- cenas
W6 = list("wwwwwwf"); W5 = list("wwwwwff"); W5S = list("wwfwwwf")     # 6x1, 5x2, 5x2 com folgas separadas
def overlays(fr, t):
    # 0 - 7,0: abertura
    k = env(t, 0.0, 7.0, 0.2)
    if k > 0:
        put(fr, chipimg("TRABALHO · CLT", GOLD, 36, NAVY), CX, 280, k, 0.8 + 0.2 * bo(t / 0.4))
        big(fr, "ESCALA 6x1", 410, 140, WHITE, k, t, 0.15)
        fl = (5, clamp((t - 1.2) / 0.6)) if t > 1.2 else None
        card3d(fr, calendar(W6, fl), CX, 680, t, 0.25, 1, k)
        if t > 1.5: put(fr, stamp("ACABOU", RED, 90, -8), CX + 150, 560, env(t, 1.5, 7.0), 0.6 + 0.4 * bo(clamp((t - 1.5) / 0.25), 2.2))
        if t > 3.0: put(fr, chipimg("MAS NÃO É PRA AMANHÃ", NAVY, 44), CX, 920, env(t, 3.0, 7.0), 0.7 + 0.3 * bo((t - 3.0) / 0.3))
        if t > 4.6: put(fr, chipimg("EU TE EXPLICO", (40, 150, 90), 40), CX, 1040, env(t, 4.6, 7.0), 0.7 + 0.3 * bo((t - 4.6) / 0.3))
    # 7,0 - 16,2: a emenda e a votação
    k = env(t, 7.0, 16.2)
    if k > 0:
        put(fr, chipimg("PROMULGADA EM 16/10/2026", GOLD, 36, NAVY), CX, 290, k, 0.8 + 0.2 * bo((t - 7.0) / 0.4))
        im, d = panel(620, 240); d.text((310, 82), "EMENDA", font=MF("ExtraBold", 34), fill=MUTE + (255,), anchor="mm"); d.text((310, 160), "CONSTITUCIONAL 141", font=ANTON(76), fill=WHITE + (255,), anchor="mm")
        card3d(fr, im, CX, 500, t, 7.2, -1, k)
        if t > 11.9: put(fr, chipimg("AMPLA MAIORIA", (40, 150, 90), 40), CX, 720, env(t, 11.9, 16.2), 0.7 + 0.3 * bo((t - 11.9) / 0.3))
        if t > 13.24:
            g = eio((t - 13.24) / 1.0); put(fr, txt("SENADO", MF("ExtraBold", 34), MUTE, 3), CX, 820, env(t, 13.24, 16.2))
            put(fr, txt(f"{int(round(75 * g))} × 1", ANTON(170), GOLD_L, 9, NAVY), CX, 950, env(t, 13.24, 16.2), 1 + 0.04 * (1 - eo((t - 13.24) / 0.3)))
            if t > 14.4: put(fr, txt("Câmara: 461 × 19 (2º turno)", MF("SemiBold", 30), MUTE, 3), CX, 1090, env(t, 14.4, 16.2))
    # 16,2 - 21,6: como é hoje
    k = env(t, 16.2, 21.6)
    if k > 0:
        big(fr, "COMO É HOJE", 300, 100, WHITE, k, t, 16.2)
        card3d(fr, calendar(W6, title="6 DIAS DE TRABALHO · 1 FOLGA"), CX, 560, t, 16.35, 1, k)
        if t > 17.9: put(fr, txt("ATÉ 44 h", ANTON(170), WHITE, 9, NAVY), CX, 840, env(t, 17.9, 21.6), 0.8 + 0.2 * bo((t - 17.9) / 0.35))
        if t > 18.6: put(fr, txt("por semana", MF("SemiBold", 34), MUTE, 3), CX, 960, env(t, 18.6, 21.6))
    # 21,6 - 27,8: o que muda
    k = env(t, 21.6, 27.8)
    if k > 0:
        big(fr, "O QUE MUDA", 300, 100, GOLD_L, k, t, 21.6)
        fl = (5, clamp((t - 22.6) / 0.6)) if t > 22.6 else None
        card3d(fr, calendar(W6 if t < 23.2 else W5, None if t >= 23.2 else fl, title="2 FOLGAS REMUNERADAS"), CX, 560, t, 21.75, -1, k)
        if t > 23.4: put(fr, chipimg("6x1  →  5x2", GOLD, 54, NAVY), CX, 800, env(t, 23.4, 27.8), 0.7 + 0.3 * bo((t - 23.4) / 0.3))
        if t > 25.78: put(fr, chipimg("AS HORAS CAEM EM 2 ETAPAS", NAVY, 38), CX, 930, env(t, 25.78, 27.8), 0.7 + 0.3 * bo((t - 25.78) / 0.3))
    # 27,8 - 40,6: linha do tempo
    k = env(t, 27.8, 40.6)
    if k > 0:
        big(fr, "LINHA DO TEMPO", 290, 96, WHITE, k, t, 27.8)
        rows = [("HOJE", "6 dias · 1 folga", 44, (120, 132, 156), 27.95), ("DEZ / 2026", "1ª etapa · 2 folgas", 42, GOLD, 29.4), ("DEZ / 2027", "2ª etapa · 2 folgas", 40, (60, 200, 120), 36.9)]
        for i, (lab, sub, hrs, col, ta) in enumerate(rows):
            if t < ta: continue
            card3d(fr, hours_card(lab, sub, hrs, col), CX, 480 + i * 210, t, ta, 1 if i % 2 == 0 else -1, env(t, ta, 40.6), 0.02)
            if i > 0 and t > ta + 0.3: put(fr, txt("↓", ANTON(60), GOLD_L, 4, NAVY), CX - 250, 480 + i * 210 - 105, env(t, ta + 0.3, 40.6))
        if t > 33.0: put(fr, chipimg("JÁ COM AS 2 FOLGAS", (40, 150, 90), 34), CX, 1150, env(t, 33.0, 36.6), 0.7 + 0.3 * bo((t - 33.0) / 0.3))
        if t > 38.4: put(fr, chipimg("JORNADA MÁXIMA: 40 h POR SEMANA", NAVY, 34), CX, 1150, env(t, 38.4, 40.6), 0.7 + 0.3 * bo((t - 38.4) / 0.3))
    # 40,6 - 45,6: salário
    k = env(t, 40.6, 45.6)
    if k > 0:
        big(fr, "E O SALÁRIO?", 320, 120, WHITE, k, t, 40.6)
        put(fr, emoji("💰", 190), CX, 590, k, 0.6 + 0.4 * bo((t - 40.8) / 0.4))
        if t > 41.66: put(fr, stamp("SEM REDUÇÃO", GREEN, 84, -7), CX, 820, env(t, 41.66, 45.6), 0.6 + 0.4 * bo(clamp((t - 41.66) / 0.25), 2.2))
        if t > 43.32:
            put(fr, txt("A JORNADA CAI,", ANTON(80), WHITE, 6, NAVY), CX, 1000, env(t, 43.32, 45.6)); put(fr, txt("O SALÁRIO FICA", ANTON(80), GOLD_L, 6, NAVY), CX, 1095, env(t, 44.2, 45.6))
    # 45,6 - 63,4: três detalhes (cartões empilhados em camadas: o novo entra por cima e o anterior recua)
    k = env(t, 45.6, 63.4)
    if k > 0:
        big(fr, "3 DETALHES", 290, 110, GOLD_L, k, t, 45.6)
        if t < 49.3: put(fr, txt("que pouca gente sabe", MF("SemiBold", 34), MUTE, 3), CX, 390, env(t, 45.9, 49.3))
        dets = [(49.3, detail_card(1, "AS 2 FOLGAS NÃO", "PRECISAM SER SEGUIDAS", "🧩")), (53.2, detail_card(2, "QUEM JÁ FAZ 40 h", "OU MENOS: NADA MUDA", "✅")),
                (57.7, detail_card(3, "ACORDO COLETIVO PODE", "CRIAR OUTRA ESCALA", "🤝", "só em casos excepcionais, como compensação"))]
        on = [i for i, (ta, _) in enumerate(dets) if t >= ta]
        for i in on:
            ta, im = dets[i]; depth = on[-1] - i                     # 0 = cartão da frente
            cy = 640 - depth * 70; sc = 1 - 0.08 * depth; al = env(t, ta, 63.4) * (1 if depth == 0 else 0.55)
            if depth == 0: card3d(fr, im, CX, cy, t, ta, 1 if i % 2 == 0 else -1, al, 0.02)
            else: put(fr, layered(im), CX, cy, al, sc)
        if t > 50.4 and t < 53.2: card3d(fr, calendar(W5S, title="EXEMPLO: FOLGA NA QUARTA E NO DOMINGO"), CX, 980, t, 50.4, -1, env(t, 50.4, 53.2), 0.02)
    # 63,4 - 72,9: quem fica de fora
    k = env(t, 63.4, 72.9)
    if k > 0:
        big(fr, "QUEM FICA DE FORA", 300, 96, WHITE, k, t, 63.4)
        if t > 65.0: card3d(fr, who_card("🏛️", "SERVIDOR PÚBLICO", "não muda: tem regra própria", BLUE), CX, 540, t, 65.0, 1, env(t, 65.0, 72.9), 0.02)
        if t > 68.1: card3d(fr, who_card("🏢", "PRESTADORAS DO GOVERNO", "12 meses para se adaptar", GOLD), CX, 800, t, 68.1, -1, env(t, 68.1, 72.9), 0.02)
    # 72,9 - fim: pergunta (sem tela final; o SIGA entra por cima da última frase)
    k = env(t, 72.9, EDIT_END + 1, 0.3, 0.01)
    if k > 0:
        big(fr, "VOCÊ TRABALHA", 430, 110, WHITE, k, t, 72.9); big(fr, "6x1 HOJE?", 580, 150, GOLD_L, k, t, 73.2)
        if t > 76.0: put(fr, chipimg("COMENTA AQUI", RED, 50), CX, 790, k, (0.6 + 0.4 * bo((t - 76.0) / 0.35, 2.2)) * (1 + 0.03 * math.sin(t * 6)))
        if t > 76.4: put(fr, chipimg("SIGA PARA MAIS", GOLD, 46, NAVY), CX, 920, k, 0.6 + 0.4 * bo((t - 76.4) / 0.35, 2.2))
    if 0.5 < t < EDIT_END: R.credit(fr, "Fontes: Agência Senado, Agência Câmara, Agência Brasil", W - 30, 168, clamp((t - 0.5) / 0.4))
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); fr = Image.fromarray(OCEAN).convert("RGBA")
    overlays(fr, tt)
    g = np.zeros((520, W, 4), np.uint8); g[..., :3] = (3, 10, 22); g[..., 3] = np.linspace(0, 210, 520)[:, None].astype(np.uint8); fr.alpha_composite(Image.fromarray(g), (0, H - 520))
    R.draw_caption(fr, tt, CAP_Y, 52, ("me", "au"))
    for a_, b_, kick, lines in CARDS:
        kc = clamp((tt - a_) / 0.4) * (1 - clamp((tt - (b_ - 0.3)) / 0.3))
        if kc > 0: BAR.lower_card(fr, kick, lines, CARD_Y, kc, fs=40)
    cta = max(clamp((t - 74.0) / 0.4), clamp((t - 30.0) / 0.4) * clamp((35.0 - t) / 0.4))
    BAR.draw_bar(fr, clamp(t / TOTAL), "canal", eo((t - 0.2) / 0.6), cta, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(fr, t)
    return fr.convert("RGB")
def capa(out, var="A"):
    fr = Image.fromarray(OCEAN).convert("RGBA")
    if var == "A":
        put(fr, chipimg("TRABALHO · CLT", GOLD, 40, NAVY), CX, 260); big(fr, "FIM DA 6x1", 420, 170, WHITE, 1)
        put(fr, layered(calendar(W5)), CX, 700); put(fr, stamp("ACABOU", RED, 96, -8), CX + 170, 590)
        big(fr, "O QUE MUDA E QUANDO", 960, 88, GOLD_L, 1); put(fr, chipimg("44 h → 42 h → 40 h", NAVY, 50), CX, 1100); put(fr, chipimg("SEM REDUZIR SALÁRIO", (40, 150, 90), 44), CX, 1230)
    elif var == "B":
        big(fr, "ACABOU A 6x1?", 380, 150, WHITE, 1); put(fr, emoji("😴", 200), CX, 640)
        big(fr, "NÃO É PRA AMANHÃ", 860, 110, GOLD_L, 1); put(fr, chipimg("VEJA AS DATAS", RED, 50), CX, 1020); put(fr, chipimg("DEZ/2026 · DEZ/2027", NAVY, 46), CX, 1150)
    else:
        put(fr, chipimg("EC 141/2026", GOLD, 42, NAVY), CX, 260); big(fr, "6x1 → 5x2", 430, 180, WHITE, 1)
        for i, (lab, sub, hrs, col) in enumerate([("HOJE", "1 folga", 44, (120, 132, 156)), ("DEZ / 2026", "2 folgas", 42, GOLD), ("DEZ / 2027", "2 folgas", 40, (60, 200, 120))]):
            put(fr, layered(hours_card(lab, sub, hrs, col)), CX, 700 + i * 190)
        put(fr, chipimg("O SEU SALÁRIO NÃO CAI", (40, 150, 90), 46), CX, 1330)
    BAR.draw_bar(fr, 0.0, "canal"); fr.alpha_composite(R.top, (R.HDX, 0)); fr.convert("RGB").save(out, quality=95)
def capa_yt(out, var="A"):
    """miniatura horizontal do YouTube (16:9, 1280x720): acima de 60 s o vídeo vai para vídeos longos"""
    YW, YH = 1280, 720
    bg = cv2.resize(OCEAN[300:300 + 1080 * 1080 // 1920 * 2:, :], (YW, YH)) if False else cv2.resize(OCEAN[420:1500, :], (YW, YH), interpolation=cv2.INTER_AREA)
    fr = Image.fromarray(bg).convert("RGBA"); d = ImageDraw.Draw(fr)
    d.rectangle((0, 0, 14, YH), fill=GOLD + (255,))                                  # filete dourado da marca na borda esquerda
    def tx(s_, size, col, x, y, anchor="lm", st=8, maxw=600):
        while d.textlength(s_, font=ANTON(size)) > maxw: size -= 4
        d.text((x, y), s_, font=ANTON(size), fill=col + (255,), anchor=anchor, stroke_width=st, stroke_fill=NAVY + (255,))
    if var == "A":
        fr.alpha_composite(chipimg("TRABALHO · CLT", GOLD, 34, NAVY), (60, 50))
        tx("FIM DA", 120, WHITE, 60, 200, maxw=560); tx("ESCALA 6x1", 150, GOLD_L, 60, 335, maxw=580)
        tx("O QUE MUDA E QUANDO", 64, WHITE, 60, 470, st=6, maxw=580)
        fr.alpha_composite(chipimg("SEM REDUZIR SALÁRIO", (40, 150, 90), 40), (60, 540))
        cal = layered(calendar(W5)); cal = cal.resize((int(cal.width * 0.70), int(cal.height * 0.70)), Image.LANCZOS)
        cal = Image.fromarray(R.persp(np.asarray(cal), "right", 0.05)); fr.alpha_composite(cal, (YW - cal.width - 24, 96))
        for i, (lab, sub, hrs, col) in enumerate([("HOJE", "1 folga", 44, (120, 132, 156)), ("DEZ / 2026", "2 folgas", 42, GOLD), ("DEZ / 2027", "2 folgas", 40, (60, 200, 120))]):
            c = layered(hours_card(lab, sub, hrs, col, w=500)); c = c.resize((int(c.width * 0.66), int(c.height * 0.66)), Image.LANCZOS)
            fr.alpha_composite(c, (YW - c.width - 34, 318 + i * 118))
        st_ = stamp("ACABOU", RED, 64, -8); fr.alpha_composite(st_, (YW - st_.width - 40, 22))
    d = ImageDraw.Draw(fr); d.text((60, YH - 34), "ELIEZIO SOUZA  ·  OPINIÃO · ATUALIDADES · REAÇÕES", font=MF("SemiBold", 22), fill=GOLD_L + (230,), anchor="lm")
    fr.convert("RGB").save(out, quality=92)
def audio(vout):
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{V}/vo.mp3", "-ar", "48000", "-ac", "2", f"{V}/vo48.wav"], check=True)
    vo = R.readw(f"{V}/vo48.wav"); vt = np.zeros((n, 2), np.float32); vt[:min(len(vo), n)] = vo[:n]
    subprocess.run([sys.executable, f"{S}/work/music.py", f"{V}/bed.wav", f"{TOTAL + 0.5:.2f}"], check=True)   # trilha própria do canal
    bed = R.readw(f"{V}/bed.wav")[:n]; bed = np.pad(bed, ((0, max(0, n - len(bed))), (0, 0)))[:n]
    tl = np.arange(n) / SR; gain = 0.30 * np.clip(tl / 0.3, 0, 1) * np.clip((TOTAL - tl) / 0.4, 0, 1)
    R.writew(f"{V}/voice.wav", vt); R.writew(f"{V}/song.wav", bed * gain[:, None])
    def pop():
        tt = np.arange(int(0.12 * SR)) / SR; y = np.sin(2 * np.pi * (500 + 900 * tt / 0.12) * tt) * np.exp(-tt / 0.03); return np.stack([y, y], 1)
    ev = [(a - 0.15, sfx.whoosh(0.5), 0.15) for a in (7.0, 16.2, 21.6, 27.8, 40.6, 45.6, 63.4, 72.9)]
    ev += [(x, pop(), 0.3) for x in (3.0, 4.6, 11.9, 23.4, 25.78, 27.95, 29.4, 36.9, 49.3, 53.2, 57.7, 65.0, 68.1, 76.0, 76.4)]
    ev += [(x, sfx.click(), 0.4) for x in (1.2, 22.6)] + [(x, sfx.thud(0.4), 0.28) for x in (1.5, 13.24, 41.66)]
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.5], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=70,acompressor=threshold=0.1:ratio=2.2:attack=8:release=200:makeup=1.4,asplit=2[vox][k2];[2:a]volume=0.9[sf];[3:a]volume=1.0[sg];"
                    "[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][sgd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
def main():
    if MODE == "lib": return
    if MODE.startswith("yt"): capa_yt(OUTFILE, MODE.split(":")[1] if ":" in MODE else "A"); return
    if MODE.startswith("capa"): capa(OUTFILE, MODE.split(":")[1] if ":" in MODE else "A"); return
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
