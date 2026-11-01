"""O novo Congresso (eleição 2026), 9:16, ~42 s, narração do ElevenLabs: Câmara em semicírculo com as 513 cadeiras (PL 121, recorde
desde 1988, contra 99 em 2022; federação do PT 80 → 88; União Brasil + PP 106 → 87), Senado de 2027 com 81 cadeiras (PL 29, PT 10,
MDB 8, números da Agência Senado de 25/10), aviso de que pode mudar até a posse e pergunta ao público. Sem opinião do Eliezio.
Formato loop (30/10/2026): sem tela final parada; o SIGA entra por cima da última frase. Fontes: Câmara, Agência Senado, CNN, Exame."""
import sys, math, subprocess, importlib.util, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("rex", f"{S}/work/render_exercito.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; eo = R.ease_out; ei = R.ease_in; eio = R.ease_io; bo = R.back_out
V = f"{S}/congresso"; FD = f"{S}/fontdl"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
EDIT_END = 42.15; TOTAL = EDIT_END; END_IN = TOTAL + 99   # loop: nenhuma tela final
R.FIN_IN = EDIT_END + 99; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
GOLD = R.GOLD; GOLD_L = R.GOLD_L; NAVY = R.NAVY; WHITE = (255, 255, 255); RED = (226, 52, 52); GREEN_BR = (40, 150, 90); YEL = (255, 214, 64); INK = (20, 24, 34)
def ANTON(s): return ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s)
MF = R.MF
# ---------------------------------------------------------------- legenda (texto revisado à mão)
CAPTXT = [(0.05, 2.11, "O novo Congresso já está definido,"), (2.33, 3.22, "e mudou muito."), (3.71, 4.32, "Na Câmara,"),
          (4.60, 7.70, "o PL elegeu 121 deputados,"), (7.85, 11.34, "a maior bancada de um partido desde 1988."), (11.64, 14.18, "Em 2022, eram 99."),
          (14.48, 18.10, "A federação do PT subiu de 80 para 88."), (18.62, 21.02, "Quem mais perdeu foi União Brasil com PP:"), (21.40, 23.61, "de 106 para 87."),
          (23.96, 27.94, "No Senado, o PL terá 29 das 81 cadeiras."), (28.28, 29.58, "O PT, dez."), (29.89, 31.18, "O MDB, oito."),
          (31.59, 35.94, "Até a posse, em fevereiro, esses números ainda podem mudar com troca de partido."),
          (36.26, 39.74, "Esse Congresso vai ajudar ou travar o próximo governo?"), (40.19, 40.84, "Comenta aqui"), (41.08, 41.70, "e me segue.")]
HOT = {"CONGRESSO", "MUITO.", "PL", "121", "1988.", "2022,", "99.", "PT", "88.", "PERDEU", "106", "87.", "SENADO,", "29", "81", "DEZ.", "MDB,", "OITO.",
       "MUDAR", "TROCA", "AJUDAR", "TRAVAR", "AQUI", "SEGUE."}
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
CARDS = [(0.4, 14.3, "CÂMARA 2027", ["PL: 121 DEPUTADOS", "RECORDE DESDE 1988"]), (14.3, 23.8, "CÂMARA 2027", ["FED. PT: 88", "UNIÃO + PP: 87"]),
         (23.8, 31.4, "SENADO 2027", ["PL: 29 DE 81", "PT 10 · MDB 8"]), (31.4, 36.1, "ATENÇÃO", ["PODE MUDAR", "ATÉ A POSSE"]), (36.1, EDIT_END + 0.3, "E VOCÊ?", ["COMENTA AQUI"])]
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
# ---------------------------------------------------------------- semicírculo de cadeiras
C_PL = (36, 104, 226); C_PT = (214, 36, 44); C_UP = (240, 150, 40); C_MDB = (40, 150, 90); C_PSD = (230, 200, 60); C_REP = (40, 170, 190); C_OUT = (92, 108, 138)
CAMARA = [("PSOL-REDE", 15, C_OUT), ("FED. PT", 88, C_PT), ("PSB", 15, C_OUT), ("PDT", 6, C_OUT), ("AVANTE", 5, C_OUT), ("PRD-SOLID.", 7, C_OUT), ("MISSÃO", 1, C_OUT),
          ("MDB", 36, C_MDB), ("PSD", 43, C_PSD), ("PODEMOS", 27, C_OUT), ("PSDB-CID.", 11, C_OUT), ("REPUBLICANOS", 41, C_REP), ("UNIÃO + PP", 87, C_UP),
          ("NOVO", 10, C_OUT), ("PL", 121, C_PL)]
SENADO = [("REDE", 1, C_OUT), ("PT", 10, C_PT), ("PSB", 4, C_OUT), ("PDT", 1, C_OUT), ("SEM PARTIDO", 1, C_OUT), ("MDB", 8, C_MDB), ("PSD", 4, C_PSD),
          ("PODEMOS", 2, C_OUT), ("PSDB", 2, C_OUT), ("REPUBLICANOS", 5, C_REP), ("UNIÃO", 5, C_UP), ("PP", 6, C_UP), ("NOVO", 3, C_OUT), ("PL", 29, C_PL)]
assert sum(n for _, n, _ in CAMARA) == 513 and sum(n for _, n, _ in SENADO) == 81
def seats(parties, rows, r0, r1):
    N = sum(n for _, n, _ in parties); rs = np.linspace(r0, r1, rows); per = rs / rs.sum() * N; cnt = np.floor(per).astype(int)
    for i in np.argsort(-(per - cnt))[:N - cnt.sum()]: cnt[i] += 1
    pos = []
    for r, c in zip(rs, cnt):
        for j in range(c): a = math.pi * (1 - j / max(1, c - 1)); pos.append((a, r))
    pos.sort(key=lambda p: -p[0]); lab = []
    for name, n, col in parties: lab += [(name, col)] * n
    return [(a, r, nm, col) for (a, r), (nm, col) in zip(pos, lab)]
SEAT_C = seats(CAMARA, 12, 120, 318); SEAT_S = seats(SENADO, 5, 150, 300)
def hemi(fr, seatlist, cy, t0, t, hi=None, dot=9.5, al=1.0):
    """cadeiras acendendo da esquerda para a direita a partir de t0; hi = partidos em destaque (os outros apagam)"""
    if al <= 0 or t < t0: return
    S2 = 2; Wd, Hd = 720 * S2, 380 * S2; lay = Image.new("RGBA", (Wd, Hd), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); cx2, cy2 = Wd / 2, Hd - 20 * S2; n = len(seatlist)
    for i, (a, r, nm, col) in enumerate(seatlist):
        g = clamp((t - t0 - 1.4 * i / n) / 0.25)
        if g <= 0: continue
        c = col if (hi is None or nm in hi) else (44, 56, 80); rr = dot * S2 * (0.4 + 0.6 * bo(g, 2.2)) * (1.08 if hi and nm in hi else 1)
        x, y = cx2 + math.cos(a) * r * S2, cy2 - math.sin(a) * r * S2; d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=c + (255,))
    lay = lay.resize((720, 380), Image.LANCZOS); put(fr, lay, CX, cy - 190 + 20, al)
def counter(fr, t, ta, tb, v0, v1, cy, col, size=170):
    if t < ta: return v0
    v = int(round(v0 + (v1 - v0) * eio((t - ta) / max(0.01, tb - ta)))); put(fr, txt(str(v), ANTON(size), col, 8, NAVY), CX, cy, 1, 1 + 0.04 * (1 - eo((t - ta) / 0.3)))
    return v
def delta(fr, t, ta, s, col, cy, x=None):
    if t < ta: return
    put(fr, chipimg(s, col, 46), CX if x is None else x, cy, env(t, ta, 999), 0.5 + 0.5 * bo((t - ta) / 0.35, 2.4))
def overlays(fr, t):
    HY = 800   # base do semicírculo
    # 0-14.3: Câmara + PL
    k = env(t, 0.0, 14.3, 0.2)
    if k > 0:
        put(fr, chipimg("ELEIÇÃO 2026", GOLD, 38, NAVY), CX, 270, k, 0.8 + 0.2 * bo(t / 0.4))
        put(fr, txt("O NOVO CONGRESSO", ANTON(100), WHITE, 7, NAVY), CX, 375, k, 0.85 + 0.15 * bo((t - 0.1) / 0.45))
        hemi(fr, SEAT_C, HY, 0.4, t, hi={"PL"} if t > 4.6 else None, al=k)
        if t > 3.7: put(fr, txt("CÂMARA · 513 CADEIRAS", MF("ExtraBold", 30), (200, 210, 230), 3), CX, HY + 40, k)
        if t > 4.6:
            put(fr, chipimg("PL", C_PL, 40), CX, HY + 120, k)
            counter(fr, t, 4.7, 6.6, 0, 121, HY + 250, WHITE, 140)
        if t > 7.85: put(fr, R.fade(stamp("RECORDE DESDE 1988", GOLD, 52, -5), 1), CX, HY + 385, 1, 0.6 + 0.4 * bo(clamp((t - 7.85) / 0.25), 2.2))
        if t > 11.64:
            put(fr, txt("EM 2022: 99", ANTON(60), (200, 210, 230), 5, NAVY), CX - 90, HY + 495, env(t, 11.64, 14.3))
            delta(fr, t, 12.6, "+22", GREEN_BR, HY + 495, CX + 150)
    # 14.4-18.4: federação do PT
    k = env(t, 14.4, 18.45)
    if k > 0:
        put(fr, txt("CÂMARA", ANTON(90), WHITE, 6, NAVY), CX, 350, k)
        hemi(fr, SEAT_C, HY, -9, t, hi={"FED. PT"}, al=k)
        put(fr, txt("PT · PCdoB · PV", MF("ExtraBold", 30), (200, 210, 230), 3), CX, HY + 40, k)
        put(fr, chipimg("FEDERAÇÃO DO PT", C_PT, 38), CX, HY + 120, k)
        counter(fr, t, 15.6, 17.4, 80, 88, HY + 250, WHITE, 140)
        put(fr, txt("EM 2022: 80", ANTON(60), (200, 210, 230), 5, NAVY), CX - 90, HY + 420, k); delta(fr, t, 17.4, "+8", GREEN_BR, HY + 420, CX + 150)
    # 18.5-23.8: União + PP
    k = env(t, 18.5, 23.85)
    if k > 0:
        put(fr, txt("QUEM MAIS PERDEU", ANTON(90), WHITE, 6, NAVY), CX, 350, k, 0.85 + 0.15 * bo((t - 18.5) / 0.4))
        hemi(fr, SEAT_C, HY, -9, t, hi={"UNIÃO + PP"}, al=k)
        put(fr, txt("FEDERAÇÃO", MF("ExtraBold", 30), (200, 210, 230), 3), CX, HY + 40, k)
        put(fr, chipimg("UNIÃO BRASIL + PP", C_UP, 38, NAVY), CX, HY + 120, k)
        if t > 21.4: counter(fr, t, 21.5, 23.2, 106, 87, HY + 250, WHITE, 140)
        else: put(fr, txt("106", ANTON(140), WHITE, 8, NAVY), CX, HY + 250, k)
        put(fr, txt("EM 2022: 106", ANTON(60), (200, 210, 230), 5, NAVY), CX - 90, HY + 420, k); delta(fr, t, 23.0, "−19", RED, HY + 420, CX + 170)
    # 23.9-31.4: Senado
    k = env(t, 23.9, 31.45)
    if k > 0:
        put(fr, txt("SENADO 2027", ANTON(96), WHITE, 6, NAVY), CX, 350, k, 0.85 + 0.15 * bo((t - 23.9) / 0.4))
        hi = {"PL"} | ({"PT"} if t > 28.3 else set()) | ({"MDB"} if t > 29.9 else set())
        hemi(fr, SEAT_S, HY, 24.0, t, hi=hi if t > 25.2 else None, dot=17, al=k)
        put(fr, txt("81 CADEIRAS", MF("ExtraBold", 30), (200, 210, 230), 3), CX, HY + 40, k)
        for i, (nm, v, col, ta) in enumerate([("PL", 29, C_PL, 25.3), ("PT", 10, C_PT, 28.4), ("MDB", 8, C_MDB, 30.0)]):
            if t < ta: continue
            y = HY + 160 + i * 120; g = eo((t - ta) / 0.7); d = ImageDraw.Draw(fr); x0 = CX - 300; L = int(470 * v / 29 * g) + 20
            put(fr, txt(nm, ANTON(56), WHITE, 4, NAVY), x0 + 50, y, k); d.rounded_rectangle((x0 + 110, y - 26, x0 + 110 + L, y + 26), 26, fill=col + (int(255 * k),))
            put(fr, txt(str(v), ANTON(60), WHITE, 5, NAVY), x0 + 110 + L + 50, y, k)
    # 31.5-36.1: aviso
    k = env(t, 31.5, 36.15)
    if k > 0:
        put(fr, chipimg("ATENÇÃO", RED, 46), CX, 330, k, 0.7 + 0.3 * bo((t - 31.5) / 0.35))
        put(fr, txt("ATÉ A POSSE", ANTON(110), WHITE, 7, NAVY), CX, 500, k); put(fr, txt("FEVEREIRO DE 2027", ANTON(76), GOLD_L, 6, NAVY), CX, 630, k)
        if t > 32.3: put(fr, emoji("🔄", 140), CX, 810, k, 0.6 + 0.4 * bo((t - 32.3) / 0.4))
        if t > 33.7: put(fr, stamp("PODE MUDAR", RED, 70, -6), CX, 1010, env(t, 33.7, 36.15), 0.6 + 0.4 * bo(clamp((t - 33.7) / 0.25), 2.2))
        if t > 34.4:
            put(fr, txt("eleitos por partidos que não bateram a cláusula", MF("SemiBold", 26), (200, 210, 230), 3), CX, 1140, env(t, 34.4, 36.15))
            put(fr, txt("de barreira podem trocar de legenda", MF("SemiBold", 26), (200, 210, 230), 3), CX, 1180, env(t, 34.4, 36.15))
    # 36.2-fim: pergunta + CTA (sem tela final: o vídeo volta para a capa)
    k = env(t, 36.2, EDIT_END + 1, 0.3, 0.01)
    if k > 0:
        put(fr, txt("VAI AJUDAR", ANTON(120), GREEN_BR, 7, NAVY), CX, 470, k, 0.85 + 0.15 * bo((t - 36.9) / 0.4) if t > 36.9 else 0.85)
        if t > 37.9: put(fr, txt("OU TRAVAR?", ANTON(130), RED, 7, NAVY), CX, 640, env(t, 37.9, 99), 0.85 + 0.15 * bo((t - 37.9) / 0.4))
        if t > 40.1: put(fr, chipimg("COMENTA AQUI", RED, 50), CX, 860, k, (0.6 + 0.4 * bo((t - 40.1) / 0.35, 2.2)) * (1 + 0.03 * math.sin(t * 6)))
        if t > 40.9: put(fr, chipimg("SIGA PARA MAIS", GOLD, 46, NAVY), CX, 990, k, 0.6 + 0.4 * bo((t - 40.9) / 0.35, 2.2))
    if 0.5 < t < EDIT_END: R.credit(fr, "Fontes: Câmara dos Deputados, Agência Senado, CNN Brasil, Exame", W - 30, 168, clamp((t - 0.5) / 0.4))
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); fr = Image.fromarray(OCEAN).convert("RGBA")
    overlays(fr, tt)
    g = np.zeros((520, W, 4), np.uint8); g[..., :3] = (3, 10, 22); g[..., 3] = np.linspace(0, 210, 520)[:, None].astype(np.uint8); fr.alpha_composite(Image.fromarray(g), (0, H - 520))
    M.caption(fr, tt, CAP_Y, 54)
    for a_, b_, kick, lines in CARDS:
        kc = clamp((tt - a_) / 0.4) * (1 - clamp((tt - (b_ - 0.3)) / 0.3))
        if kc > 0: BAR.lower_card(fr, kick, lines, CARD_Y, kc, fs=40)
    cta = clamp((t - 40.1) / 0.4) if t > 40.1 else 0.0
    BAR.draw_bar(fr, clamp(t / TOTAL), "canal", eo((t - 0.2) / 0.6), cta, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(fr, t)
    return fr.convert("RGB")
def capa(out, var="A"):
    fr = Image.fromarray(OCEAN).convert("RGBA")
    if var == "A":
        put(fr, chipimg("ELEIÇÃO 2026", GOLD, 44, NAVY), CX, 250)
        put(fr, txt("O NOVO", ANTON(150), WHITE, 8, NAVY), CX, 400); put(fr, txt("CONGRESSO", ANTON(150), GOLD_L, 8, NAVY), CX, 560)
        hemi(fr, SEAT_C, 1000, -99, 0, hi={"PL", "FED. PT", "UNIÃO + PP"}); put(fr, txt("513", ANTON(84), WHITE, 6, NAVY), CX, 960)
        put(fr, stamp("PL: 121 · RECORDE", GOLD, 64, -6), CX, 1180); put(fr, chipimg("QUEM GANHOU E QUEM PERDEU?", RED, 40), CX, 1360)
    else:
        put(fr, txt("QUEM GANHOU", ANTON(130), GREEN_BR, 7, NAVY), CX, 330); put(fr, txt("E QUEM PERDEU", ANTON(120), RED, 7, NAVY), CX, 480)
        for i, (nm, a, b, col, dl, dc) in enumerate([("PL", 99, 121, C_PL, "+22", GREEN_BR), ("FED. PT", 80, 88, C_PT, "+8", GREEN_BR), ("UNIÃO + PP", 106, 87, C_UP, "−19", RED)]):
            y = 700 + i * 200; d = ImageDraw.Draw(fr); x0 = CX - 320; L = int(420 * b / 121)
            put(fr, txt(nm, MF("ExtraBold", 36), WHITE, 3), x0 + 10 + txt(nm, MF("ExtraBold", 36), WHITE, 3).width / 2, y - 62)
            d.rounded_rectangle((x0, y - 30, x0 + L, y + 30), 30, fill=col + (255,)); put(fr, txt(str(b), ANTON(64), WHITE, 5, NAVY), x0 + L + 60, y)
            put(fr, chipimg(dl, dc, 40), x0 + L + 170, y)
        put(fr, chipimg("CÂMARA 2027 × 2022", NAVY, 40), CX, 1320)
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
    ev = [(a - 0.15, sfx.whoosh(0.5), 0.15) for a in (14.4, 18.5, 23.9, 31.5, 36.2)]
    ev += [(x, pop(), 0.3) for x in (4.6, 11.64, 12.6, 15.6, 17.4, 21.5, 23.0, 25.3, 28.4, 30.0, 40.1, 40.9)]
    ev += [(x, sfx.thud(0.4), 0.28) for x in (7.85, 33.7)]
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
