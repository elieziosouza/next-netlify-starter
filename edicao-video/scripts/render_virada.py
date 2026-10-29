"""Resposta ao vídeo viral da "virada impossível" de Lula (2026), 9:16, ~2min30: refaz as contas uma por uma (1º turno, votos em jogo,
3 de cada 4, saldo x fluxo, eleitores de Cury, margem de erro, Datafolha 2022, 0 em 7, viradas para governador, menor diferença desde
1989, TSE) com carimbos de checagem e opinião marcada. Narração do ElevenLabs com a voz do Eliezio, identidade do canal."""
import sys, math, subprocess, importlib.util, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("rex", f"{S}/work/render_exercito.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; eo = R.ease_out; ei = R.ease_in; eio = R.ease_io; bo = R.back_out
V = f"{S}/v87"; FD = f"{S}/fontdl"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
EDIT_END = 148.45; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = EDIT_END; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
GOLD = R.GOLD; GOLD_L = R.GOLD_L; NAVY = R.NAVY; WHITE = (255, 255, 255); RED = (226, 52, 52); GREEN_BR = (40, 150, 90); YEL = (255, 214, 64); INK = (20, 24, 34)
def ANTON(s): return ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s)
MF = R.MF
# ---------------------------------------------------------------- legenda (texto revisado à mão)
CAPTXT = [(0.06, 4.41, "Esse vídeo viralizou dizendo que a virada do Lula era quase impossível."), (4.98, 7.21, "Vamos refazer as contas, uma por uma."),
          (7.77, 12.06, "No primeiro turno, Flávio teve 56,1 milhões de votos,"), (12.28, 15.14, "e Lula, 53,9 milhões."),
          (15.67, 20.19, "Cury, Renan Santos, Caiado e Zema somaram cerca de 9 milhões."), (20.66, 25.47, "No segundo turno, ainda entraram quase 3 milhões de pessoas que não tinham votado,"),
          (25.91, 29.47, "e 1,8 milhão que antes votaram branco ou nulo."), (30.04, 33.56, "Lula ganhou 10,4 milhões de votos a mais."), (33.82, 36.14, "Flávio, 3,7 milhões."),
          (36.73, 40.74, "O vídeo diz que Lula precisava de três em cada quatro votos em jogo."), (41.34, 42.25, "A conta está certa."), (42.55, 44.26, "O problema é a conclusão."),
          (44.82, 47.40, "Primeiro: essa conta só olha o saldo."), (47.74, 51.36, "Finge que ninguém mudou de lado e que todo mundo voltou para votar."),
          (51.80, 55.91, "Na vida real, tem gente que troca de candidato e gente que deixa de votar."), (56.41, 59.72, "Segundo: esses eleitores não eram todos do Flávio."),
          (60.06, 65.45, "Na AtlasIntel, metade dos eleitores de Cury, o maior deles, dizia votar em Lula."), (65.78, 67.91, "E Renan Santos anunciou voto nulo."),
          (68.44, 69.99, "Agora, as pesquisas."), (70.39, 74.46, "O vídeo diz que elas davam 49% para Lula na véspera,"), (74.71, 78.68, "e que chegar a 51,8 tinha chance de três em mil."),
          (79.26, 82.09, "Mas a margem de erro só mede o sorteio da amostra."), (82.36, 84.39, "Não mede quem decide no último dia."),
          (84.82, 90.62, "Em 2022, o Datafolha deu 36% para Bolsonaro na véspera do primeiro turno,"), (90.97, 93.03, "e ele teve 43%."), (93.34, 94.44, "Sete pontos."),
          (94.81, 97.10, "Pela mesma conta, seria impossível."), (97.46, 98.60, "E não foi fraude."), (99.00, 100.74, "Por fim, o zero em sete."), (101.08, 101.77, "É verdade:"),
          (102.07, 107.78, "desde 1989, quem venceu o primeiro turno para presidente venceu o segundo."), (108.22, 110.70, "Mas sete casos é pouco para virar lei."),
          (111.16, 115.90, "Para governador, já foram 19 viradas desde 1998."), (116.47, 120.46, "Em 2022, Eduardo Leite saiu com 27%"), (120.66, 122.89, "e venceu com 57%."),
          (123.42, 128.14, "E em 2026, a diferença no primeiro turno foi de menos de dois pontos,"), (128.38, 131.14, "a menor desde 1989."),
          (131.67, 134.12, "O TSE não encontrou irregularidade,"), (134.55, 137.64, "e até aliados de Flávio dizem que não há prova de fraude."), (138.04, 138.89, "Na minha opinião,"),
          (139.13, 140.84, "número sem contexto engana."), (141.21, 143.11, "Primeira vez não é prova de nada."), (143.54, 144.81, "E você, o que acha?"),
          (145.18, 148.07, "Comenta aqui, e me segue para mais vídeos como esse.")]
HOT = {"VIRALIZOU", "IMPOSSÍVEL.", "CONTAS,", "56,1", "53,9", "9", "3", "1,8", "10,4", "3,7", "TRÊS", "QUATRO", "CERTA.", "CONCLUSÃO.", "SALDO.", "LADO", "TROCA",
       "DEIXA", "FLÁVIO.", "METADE", "LULA.", "NULO.", "PESQUISAS.", "49%", "51,8", "MIL.", "AMOSTRA.", "ÚLTIMO", "36%", "43%.", "SETE", "IMPOSSÍVEL.", "FRAUDE.",
       "ZERO", "SETE.", "POUCO", "LEI.", "19", "VIRADAS", "27%", "57%.", "DOIS", "MENOR", "TSE", "IRREGULARIDADE,", "PROVA", "OPINIÃO,", "ENGANA.", "NADA.", "AQUI,"}
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
CARDS = [(0.6, 30.0, "OS NÚMEROS", ["1º TURNO E", "VOTOS EM JOGO"]), (30.0, 68.3, "A CONTA", ["CERTA, MAS A", "CONCLUSÃO NÃO"]), (68.3, 99.0, "PESQUISAS", ["MARGEM DE ERRO", "NÃO É GARANTIA"]),
         (99.0, 131.5, "0 EM 7", ["19 VIRADAS PARA", "GOVERNADOR"]), (131.5, 138.0, "TSE", ["NENHUMA", "IRREGULARIDADE"]), (138.0, EDIT_END, "OPINIÃO", ["NÚMERO SEM", "CONTEXTO ENGANA"])]
CAP_Y, CARD_Y = 1430, 1712
yy_, xx_ = np.mgrid[0:H, 0:W].astype(np.float32)
OCEAN = (np.array([6, 22, 44], np.float32) + np.array([10, 30, 56], np.float32) * np.clip(1 - np.sqrt(((xx_ - W / 2) / W) ** 2 + ((yy_ - 700) / H) ** 2) * 1.6, 0, 1)[..., None])
OCEAN[::60, :] += 5; OCEAN[:, ::60] += 5
OCEAN = np.clip(OCEAN, 0, 255).astype(np.uint8); del yy_, xx_
C_LULA = (214, 48, 58); C_FLA = (52, 120, 220); C_OUT = (232, 180, 60); C_NEW = (40, 180, 150); C_BN = (150, 100, 210); GREY = (120, 132, 156)
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
def tag(fr, t, ta, b, kind, y=1230):
    """carimbo de checagem: ok / ctx / no"""
    if t < ta: return
    s, col, em = {"ok": ("CORRETO", GREEN_BR, "✅"), "ctx": ("FORA DE CONTEXTO", (220, 150, 30), "⚠️"), "no": ("ENGANOSO", RED, "❌"), "nf": ("NÃO FOI FRAUDE", RED, None)}[kind]
    im = stamp(s, col, 54, -6); sc = 0.7 + 0.3 * bo(clamp((t - ta) / 0.25), 2.0); k = env(t, ta, b)
    put(fr, im, CX + (36 if em else 0), y, k, sc)
    if em: put(fr, emoji(em, 76), CX + 36 - im.width / 2 - 40, y, k, sc)
def hbar(fr, t, ta, y, lab, val, vmax, col, vtxt, al=1.0, L=600, x0=170):
    if t < ta: return
    g = eo((t - ta) / 0.9); kk = al * clamp((t - ta) / 0.25); d = ImageDraw.Draw(fr)
    put(fr, txt(lab, MF("ExtraBold", 34), WHITE, 3), x0 + txt(lab, MF("ExtraBold", 34), WHITE, 3).width / 2, y - 52, kk)
    w = max(24, int(L * val / vmax * g)); d.rounded_rectangle((x0, y - 26, x0 + w, y + 26), 26, fill=col + (int(255 * kk),))
    im = txt(vtxt, ANTON(50), WHITE, 5, NAVY); put(fr, im, x0 + w + 20 + im.width / 2, y, kk)
def people(fr, t, ta, y, n_red, n, al, size=64, cols=(C_LULA, C_FLA)):
    for i in range(n):
        if t < ta + i * 0.12: continue
        x = CX + (i - (n - 1) / 2) * (size + 26); col = cols[0] if i < n_red else cols[1]
        d = ImageDraw.Draw(fr); a = int(255 * al * clamp((t - ta - i * 0.12) / 0.2))
        d.ellipse((x - size * 0.22, y - size * 0.62, x + size * 0.22, y - size * 0.18), fill=col + (a,)); d.rounded_rectangle((x - size * 0.36, y - size * 0.12, x + size * 0.36, y + size * 0.5), int(size * 0.3), fill=col + (a,))
def overlays(fr, t):
    # 0-7.5: o vídeo viral
    k = env(t, 0.0, 7.6, 0.2)
    if k > 0:
        put(fr, chipimg("ESSE VÍDEO VIRALIZOU", RED, 40), CX, 330, k, 0.8 + 0.2 * bo(t / 0.4))
        ph = Image.new("RGBA", (520, 620), (0, 0, 0, 0)); d = ImageDraw.Draw(ph); d.rounded_rectangle((0, 0, 519, 619), 50, fill=(18, 22, 30, 255), outline=(90, 100, 120, 255), width=6)
        d.text((260, 150), "VIRADA", font=ANTON(80), fill=WHITE + (255,), anchor="mm"); d.text((260, 250), "IMPOSSÍVEL?", font=ANTON(80), fill=(255, 90, 90, 255), anchor="mm")
        d.rounded_rectangle((70, 340, 450, 420), 40, fill=(60, 60, 70, 255)); d.text((260, 380), "0 EM 7", font=MF("ExtraBold", 40), fill=WHITE + (255,), anchor="mm")
        d.rounded_rectangle((70, 450, 450, 530), 40, fill=(60, 60, 70, 255)); d.text((260, 490), "3 EM 1.000", font=MF("ExtraBold", 40), fill=WHITE + (255,), anchor="mm")
        put(fr, ph, CX, 780, k * (1 - 0.88 * clamp((t - 4.9) / 0.3)), (0.7 + 0.3 * bo(t / 0.5)) * (1 - 0.15 * clamp((t - 4.9) / 0.3)), -4)
        if t > 4.9: put(fr, txt("VAMOS REFAZER", ANTON(110), WHITE, 7, NAVY), CX, 720, env(t, 4.9, 7.6), 0.8 + 0.2 * bo((t - 4.9) / 0.35)); put(fr, txt("AS CONTAS", ANTON(130), GOLD_L, 7, NAVY), CX, 860, env(t, 5.1, 7.6))
        if t > 5.4: put(fr, emoji("🧮", 120), CX, 1040, env(t, 5.4, 7.6))
    # 7.7-15.5: 1º turno
    k = title(fr, t, 7.7, 15.6, "1º TURNO", "votos de cada candidato · TSE")
    if k > 0:
        hbar(fr, t, 8.6, 640, "FLÁVIO BOLSONARO", 56.1, 56.1, C_FLA, "56,1 mi", k); hbar(fr, t, 12.3, 840, "LULA", 53.9, 56.1, C_LULA, "53,9 mi", k)
        if t > 13.6: put(fr, chipimg("DIFERENÇA: 2,2 MILHÕES", (40, 40, 50), 34, YEL), CX, 1020, env(t, 13.6, 15.6))
    # 15.6-29.8: votos em jogo
    k = title(fr, t, 15.6, 29.9, "VOTOS EM JOGO", "do 1º para o 2º turno")
    if k > 0:
        segs = [(15.8, 9.0, C_OUT, "Eleitores de outros candidatos", "≈ 9 mi"), (21.8, 2.96, C_NEW, "Não votaram no 1º, votaram no 2º", "+ 2,96 mi"), (25.9, 1.82, C_BN, "Branco ou nulo no 1º", "+ 1,82 mi")]
        x0, L, y = 150, 780, 600; d = ImageDraw.Draw(fr); x = x0; tot = 14.1
        for i, (ta, v, col, lab, vt) in enumerate(segs):
            if t < ta: continue
            g = eo((t - ta) / 0.8); w = L * v / tot * g; al = k * clamp((t - ta) / 0.2)
            d.rounded_rectangle((x, y - 44, x + max(w, 10), y + 44), 14, fill=col + (int(255 * al),)); x += w
            yy = 760 + i * 110; d.rounded_rectangle((150, yy - 18, 186, yy + 18), 8, fill=col + (int(255 * al),))
            put(fr, txt(lab, MF("SemiBold", 30), WHITE, 3), 210 + txt(lab, MF("SemiBold", 30), WHITE, 3).width / 2, yy, al)
            put(fr, txt(vt, ANTON(44), col, 4, NAVY), 900, yy, al)
        if t > 16.6: put(fr, txt("Cury · Renan Santos · Caiado · Zema", MF("SemiBold", 26), (200, 210, 230), 3), CX, 690, env(t, 16.6, 21.7))
        if t > 28.0: put(fr, chipimg("≈ 14 MILHÕES EM JOGO", GOLD, 40, NAVY), CX, 1120, env(t, 28.0, 29.9), 0.7 + 0.3 * bo((t - 28.0) / 0.35))
    # 30-44.6: o resultado e o 3 de cada 4
    k = title(fr, t, 30.0, 44.7, "O RESULTADO", "quanto cada um cresceu no 2º turno")
    if k > 0:
        if t < 36.6:
            hbar(fr, t, 30.4, 640, "LULA", 10.4, 10.4, C_LULA, "+10,4 mi", k); hbar(fr, t, 33.9, 840, "FLÁVIO", 3.7, 10.4, C_FLA, "+3,7 mi", k)
        else:
            kk = env(t, 36.6, 44.7); put(fr, chipimg("O VÍDEO DIZ", (40, 40, 50), 30, YEL), CX, 520, kk)
            put(fr, txt("3 DE CADA 4", ANTON(130), WHITE, 7, NAVY), CX, 660, kk, 0.85 + 0.15 * bo((t - 36.7) / 0.35))
            people(fr, t, 38.6, 880, 3, 4, kk, 110)
            tag(fr, t, 41.3, 44.7, "ok", 1060)
            if t > 42.5: put(fr, chipimg("MAS A CONCLUSÃO NÃO", RED, 38), CX, 1190, env(t, 42.5, 44.7), 0.7 + 0.3 * bo((t - 42.5) / 0.3))
    # 44.8-56.3: 1) só o saldo
    k = title(fr, t, 44.8, 56.35, "1. SÓ O SALDO", "a conta finge que ninguém mudou de lado")
    if k > 0:
        if t > 47.7:
            kk = env(t, 47.7, 56.35); d = ImageDraw.Draw(fr)
            for i, (lab, col) in enumerate([("LULA", C_LULA), ("FLÁVIO", C_FLA)]):
                x = CX + (i * 2 - 1) * 230; d.rounded_rectangle((x - 150, 560, x + 150, 660), 30, fill=col + (int(255 * kk),)); put(fr, txt(lab, ANTON(56), WHITE, 0), x, 610, kk)
            g = 0.5 + 0.5 * math.sin((t - 47.7) * 3)
            put(fr, emoji("🔄", 80), CX, 610, kk, 1, (t - 47.7) * -120)
        for i, (em, lab, ta) in enumerate([("🔁", "GENTE QUE TROCA DE CANDIDATO", 52.8), ("🚪", "GENTE QUE DEIXA DE VOTAR", 54.3)]):
            if t < ta: continue
            kk = env(t, ta, 56.35); y = 800 + i * 150; d = ImageDraw.Draw(fr)
            d.rounded_rectangle((150, y - 56, W - 150, y + 56), 28, fill=(10, 26, 56, int(225 * kk)), outline=GOLD + (int(255 * kk),), width=3)
            put(fr, emoji(em, 70), 220, y, kk); put(fr, txt(lab, MF("ExtraBold", 36), WHITE, 2), CX + 40, y, kk)
        tag(fr, t, 50.0, 56.35, "ctx", 1150)
    # 56.4-68.3: 2) eleitores de Cury
    k = title(fr, t, 56.4, 68.35, "2. NÃO ERAM TODOS", "DO FLÁVIO" if False else None)
    if k > 0:
        put(fr, txt("DO FLÁVIO", ANTON(92), GOLD_L, 6, NAVY), CX, 460, k)
        if t > 60.0:
            put(fr, txt("Eleitores de Augusto Cury · AtlasIntel", MF("SemiBold", 30), (200, 210, 230), 3), CX, 580, env(t, 60.0, 68.35))
            hbar(fr, t, 60.6, 700, "LULA", 50.4, 50.4, C_LULA, "50,4%", k); hbar(fr, t, 61.2, 880, "FLÁVIO", 38.9, 50.4, C_FLA, "38,9%", k)
            if t > 62.5: put(fr, txt("pesquisa feita antes do 2º turno", MF("SemiBold", 24), (200, 210, 230), 3), CX, 980, env(t, 62.5, 68.35))
        if t > 65.8: put(fr, chipimg("RENAN SANTOS: VOTO NULO", NAVY, 40), CX, 1100, env(t, 65.8, 68.35), 0.7 + 0.3 * bo((t - 65.8) / 0.3))
    # 68.4-84.7: pesquisas e margem de erro
    k = title(fr, t, 68.4, 84.75, "AS PESQUISAS", "véspera do 2º turno, segundo o vídeo")
    if k > 0:
        if t < 79.2:
            kk = env(t, 70.3, 79.25)
            if t > 70.3:
                put(fr, txt("LULA", ANTON(60), WHITE, 5, NAVY), CX, 560, kk)
                put(fr, txt("49%", ANTON(160), (200, 200, 210), 7, NAVY), CX - 220, 720, kk); put(fr, txt("→", MF("ExtraBold", 90), YEL), CX, 720, kk)
                if t > 74.7: put(fr, txt("51,8%", ANTON(160), C_LULA, 7, NAVY), CX + 230, 720, env(t, 74.7, 79.25), 0.7 + 0.3 * bo((t - 74.7) / 0.35))
                if t > 76.5: put(fr, chipimg("“CHANCE DE 3 EM 1.000”", (40, 40, 50), 38, YEL), CX, 930, env(t, 76.5, 79.25))
        else:
            kk = env(t, 79.2, 84.75); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            x0, x1, yb = 170, W - 150, 900; pts = [(x0 + (x1 - x0) * i / 120, yb - 300 * math.exp(-((i - 60) / 22) ** 2)) for i in range(121)]
            g = eo((t - 79.3) / 0.8); n = max(2, int(len(pts) * g))
            d.polygon([(pts[i][0], pts[i][1]) for i in range(n)] + [(pts[n - 1][0], yb), (x0, yb)], fill=C_FLA + (70,)); d.line(pts[:n], fill=C_FLA + (255,), width=6)
            d.rectangle((x0 + (x1 - x0) * 38 / 120, yb - 310, x0 + (x1 - x0) * 82 / 120, yb), outline=YEL + (200,), width=4); d.line((x0, yb, x1, yb), fill=(200, 210, 230, 200), width=3)
            fr.alpha_composite(R.fade(lay, kk))
            put(fr, chipimg("MARGEM = SÓ O SORTEIO DA AMOSTRA", GOLD, 32, NAVY), CX, 540, kk)
            if t > 82.3:
                d = ImageDraw.Draw(fr); y = 1040; kk2 = env(t, 82.3, 84.75)
                d.rounded_rectangle((150, y - 56, W - 150, y + 56), 28, fill=(10, 26, 56, int(225 * kk2)), outline=RED + (int(255 * kk2),), width=3)
                put(fr, emoji("❌", 60), 220, y, kk2); put(fr, txt("NÃO MEDE QUEM DECIDE NO FIM", MF("ExtraBold", 34), WHITE, 2), CX + 40, y, kk2)
    # 84.8-98.9: Datafolha 2022
    k = title(fr, t, 84.8, 98.95, "2022 · DATAFOLHA", "Bolsonaro, votos válidos, 1º turno")
    if k > 0:
        hbar(fr, t, 86.6, 640, "PESQUISA NA VÉSPERA", 36, 43, GREY, "36%", k); hbar(fr, t, 91.0, 840, "RESULTADO", 43, 43, C_FLA, "43%", k)
        if t > 93.3: put(fr, txt("+7 PONTOS", ANTON(110), YEL, 7, NAVY), CX, 1010, env(t, 93.3, 98.95), 0.7 + 0.3 * bo((t - 93.3) / 0.35))
        if t > 94.8: put(fr, txt("pela conta do vídeo, “impossível”", MF("SemiBold", 30), WHITE, 3), CX, 1110, env(t, 94.8, 98.95))
        tag(fr, t, 97.4, 98.95, "nf", 1230)
    # 99-123.3: 0 em 7 e as viradas
    k = env(t, 99.0, 123.35)
    if k > 0:
        if t < 111.1:
            put(fr, txt("0 EM 7", ANTON(120), GOLD_L, 7, NAVY), CX, 360, k, 0.85 + 0.15 * bo((t - 99.0) / 0.4))
            put(fr, txt("segundos turnos para presidente desde 1989", MF("SemiBold", 28), (200, 210, 230), 3), CX, 450, k)
            Y = [("1989", "COLLOR"), ("2002", "LULA"), ("2006", "LULA"), ("2010", "DILMA"), ("2014", "DILMA"), ("2018", "BOLSONARO"), ("2022", "LULA")]
            for i, (yr, nm) in enumerate(Y):
                ta = 102.1 + i * 0.75
                if t < ta: continue
                col_, row = i % 4, i // 4; x = CX + (col_ - 1.5) * 205 + (102 if row else 0); y = 620 + row * 220
                card = Image.new("RGBA", (190, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(card); d.rounded_rectangle((0, 0, 189, 189), 22, fill=(14, 32, 64, 240), outline=GOLD + (255,), width=3)
                d.text((95, 52), yr, font=ANTON(52), fill=GOLD_L + (255,), anchor="mm"); d.text((95, 110), nm, font=MF("ExtraBold", 24 if len(nm) < 9 else 20), fill=WHITE + (255,), anchor="mm")
                d.text((95, 152), "VENCEU OS 2", font=MF("ExtraBold", 20), fill=(120, 220, 150, 255), anchor="mm")
                put(fr, card, x, y, k, 0.6 + 0.4 * bo((t - ta) / 0.3))
            if t > 108.2: put(fr, chipimg("7 CASOS É POUCO PARA VIRAR LEI", RED, 34), CX, 1100, env(t, 108.2, 111.15), 0.7 + 0.3 * bo((t - 108.2) / 0.3))
        else:
            put(fr, txt("PARA GOVERNADOR", ANTON(92), WHITE, 6, NAVY), CX, 360, k)
            n = int(19 * eo((t - 111.6) / 1.6)) if t > 111.6 else 0
            put(fr, txt(f"{n} VIRADAS", ANTON(150), GOLD_L, 8, NAVY), CX, 540, k, 1 + 0.06 * (1 - eo((t - 113.2) / 0.3)) if t > 113.2 else 1)
            put(fr, txt("desde 1998 · Folhapress", MF("SemiBold", 28), (200, 210, 230), 3), CX, 650, k)
            if t > 116.4:
                put(fr, txt("RS 2022 · EDUARDO LEITE", MF("ExtraBold", 36), WHITE, 3), CX, 770, env(t, 116.4, 123.35))
                hbar(fr, t, 117.9, 900, "1º TURNO", 26.8, 57.1, GREY, "26,8%", k); hbar(fr, t, 120.7, 1080, "2º TURNO (VENCEU)", 57.1, 57.1, GREEN_BR, "57,1%", k)
    # 123.4-131.5: a menor diferença
    k = title(fr, t, 123.4, 131.55, "DIFERENÇA NO 1º TURNO", "entre os dois primeiros colocados")
    if k > 0:
        hbar(fr, t, 124.9, 640, "2026", 1.9, 5.2, YEL, "1,9 ponto", k); hbar(fr, t, 125.8, 840, "2022", 5.2, 5.2, GREY, "5,2 pontos", k)
        if t > 128.4: put(fr, chipimg("A MENOR DESDE 1989", GOLD, 42, NAVY), CX, 1040, env(t, 128.4, 131.55), 0.7 + 0.3 * bo((t - 128.4) / 0.3))
    # 131.6-137.9: TSE e aliados
    k = env(t, 131.6, 138.0)
    if k > 0:
        put(fr, txt("TSE", ANTON(160), WHITE, 8, NAVY), CX, 440, k, 0.85 + 0.15 * bo((t - 131.6) / 0.4))
        put(fr, chipimg("NENHUMA IRREGULARIDADE", GREEN_BR, 42), CX, 600, k)
        if t > 134.5:
            kk = env(t, 134.5, 138.0); bw, bh = 860, 230; im = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
            dd.rounded_rectangle((0, 0, bw - 1, bh - 1), 26, fill=(10, 26, 56, 235), outline=GOLD + (255,), width=3)
            dd.text((40, 30), "ALIADOS DE FLÁVIO", font=ANTON(48), fill=GOLD_L + (255,)); dd.text((40, 98), "ex.: senador Rogério Marinho (PL)", font=MF("SemiBold", 26), fill=(200, 210, 230, 255))
            dd.text((40, 150), "“Não há prova de fraude”", font=MF("ExtraBold", 40), fill=WHITE + (255,))
            put(fr, im, CX, 860, kk, 0.85 + 0.15 * bo((t - 134.5) / 0.35))
    # 138-143.4: opinião
    k = env(t, 138.0, 143.5)
    if k > 0:
        put(fr, chipimg("NA MINHA OPINIÃO", (30, 30, 40), 40, GOLD_L), CX, 380, k)
        if t > 139.1: put(fr, txt("NÚMERO SEM CONTEXTO", ANTON(100), WHITE, 6, NAVY), CX, 560, env(t, 139.1, 143.5), 0.8 + 0.2 * bo((t - 139.1) / 0.35)); put(fr, txt("ENGANA", ANTON(150), GOLD_L, 8, NAVY), CX, 710, env(t, 139.6, 143.5))
        if t > 141.2: put(fr, chipimg("PRIMEIRA VEZ NÃO É PROVA", RED, 40), CX, 900, env(t, 141.2, 143.5), 0.7 + 0.3 * bo((t - 141.2) / 0.3))
    # 143.5-fim
    k = env(t, 143.5, EDIT_END + 0.4, 0.3, 0.3)
    if k > 0:
        put(fr, txt("E VOCÊ,", ANTON(130), WHITE, 7, NAVY), CX, 520, k, 0.9 + 0.1 * bo((t - 143.5) / 0.4)); put(fr, txt("O QUE ACHA?", ANTON(140), GOLD_L, 7, NAVY), CX, 680, k)
        put(fr, chipimg("COMENTA AQUI", RED, 46), CX, 880, k, 1 + 0.04 * math.sin(t * 6))
    if 0.5 < t < EDIT_END: R.credit(fr, "Fontes: TSE, Datafolha, AtlasIntel, Folhapress, Metrópoles", W - 30, 168, clamp((t - 0.5) / 0.4))
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); fr = Image.fromarray(OCEAN).convert("RGBA")
    overlays(fr, tt)
    g = np.zeros((520, W, 4), np.uint8); g[..., :3] = (3, 10, 22); g[..., 3] = np.linspace(0, 210, 520)[:, None].astype(np.uint8); fr.alpha_composite(Image.fromarray(g), (0, H - 520))
    M.caption(fr, tt, CAP_Y, 54)
    for a_, b_, kick, lines in CARDS:
        kc = clamp((tt - a_) / 0.4) * (1 - clamp((tt - (b_ - 0.3)) / 0.3))
        if kc > 0: BAR.lower_card(fr, kick, lines, CARD_Y, kc, fs=40)
    cta = clamp((t - 143.5) / 0.4) if t > 143.5 else 0.0
    BAR.draw_bar(fr, clamp(t / END_IN), "canal", eo((t - 0.2) / 0.6), cta, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(fr, t)
    if t >= END_IN: fr.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return fr.convert("RGB")
def capa(out, var="A"):
    fr = Image.fromarray(OCEAN).convert("RGBA")
    if var == "A":
        put(fr, chipimg("ESSE VÍDEO VIRALIZOU", RED, 44), CX, 250)
        put(fr, txt("VIRADA", ANTON(170), WHITE, 8, NAVY), CX, 420); put(fr, txt("IMPOSSÍVEL?", ANTON(170), GOLD_L, 8, NAVY), CX, 610)
        put(fr, txt("REFIZ AS CONTAS", ANTON(90), WHITE, 6, NAVY), CX, 780)
        for i, (s, kind) in enumerate([("0 EM 7", "ctx"), ("3 EM 1.000", "no")]):
            x = CX + (i * 2 - 1) * 210; put(fr, chipimg(s, (40, 40, 50), 44, WHITE), x, 960)
            put(fr, stamp({"ctx": "FORA DE CONTEXTO", "no": "ENGANOSO"}[kind], {"ctx": (220, 150, 30), "no": RED}[kind], 34, -8), x, 1080)
        put(fr, emoji("🧮", 150), CX, 1330)
    else:
        put(fr, txt("A VIRADA DO LULA", ANTON(110), WHITE, 7, NAVY), CX, 300); put(fr, txt("ERA IMPOSSÍVEL?", ANTON(120), GOLD_L, 7, NAVY), CX, 440)
        hbar(fr, 99, 0, 700, "BOLSONARO 2022 · DATAFOLHA", 36, 43, GREY, "36%"); hbar(fr, 99, 0, 900, "BOLSONARO 2022 · URNA", 43, 43, C_FLA, "43%")
        put(fr, txt("+7 PONTOS", ANTON(110), YEL, 7, NAVY), CX, 1080); put(fr, chipimg("19 VIRADAS PARA GOVERNADOR", GOLD, 40, NAVY), CX, 1240)
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
    ev = [(a - 0.15, sfx.whoosh(0.5), 0.15) for a in (4.9, 7.7, 15.6, 30.0, 36.6, 44.8, 56.4, 68.4, 79.2, 84.8, 99.0, 111.1, 123.4, 131.6, 138.0, 143.5)]
    ev += [(x, pop(), 0.3) for x in (8.6, 12.3, 15.8, 21.8, 25.9, 30.4, 33.9, 52.8, 54.3, 60.6, 61.2, 65.8, 74.7, 86.6, 91.0, 116.4, 117.9, 120.7, 124.9, 125.8, 134.5)]
    ev += [(102.1 + i * 0.75, sfx.click(seed=i), 0.3) for i in range(7)] + [(111.6 + i * 0.085, sfx.click(seed=20 + i), 0.12) for i in range(19)]
    ev += [(x, sfx.thud(0.4), 0.28) for x in (41.3, 50.0, 93.3, 97.4, 108.2, 128.4, 141.2)] + [(END_IN - 0.3, sfx.whoosh(0.6), 0.2)]
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
