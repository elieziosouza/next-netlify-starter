"""Carta de Flávio em Miami, 9:16: manchete do jornal (recorte, sem logotipo), mapa da rota Argentina → Equador → Miami, carta com
"verdadeiro presidente eleito", fraude sem provas, as três versões (brasão com Z, presidente → líder), reação do TSE e de Tarcísio,
opinião marcada. Narração do ElevenLabs com a voz do Eliezio, identidade do canal."""
import sys, math, subprocess, importlib.util, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("rex", f"{S}/work/render_exercito.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; eo = R.ease_out; ei = R.ease_in; eio = R.ease_io; bo = R.back_out
V = f"{S}/v86"; FD = f"{S}/fontdl"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
EDIT_END = 38.1; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = EDIT_END; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
GOLD = R.GOLD; GOLD_L = R.GOLD_L; NAVY = R.NAVY; WHITE = (255, 255, 255); RED = (226, 52, 52); GREEN_BR = (40, 150, 90); YEL = (255, 214, 64); INK = (20, 24, 34)
def ANTON(s): return ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s)
MF = R.MF
# ---------------------------------------------------------------- legenda (texto revisado à mão)
CAPTXT = [(0.09, 1.64, "Derrotado no segundo turno,"), (1.82, 3.97, "Flávio Bolsonaro foi para Miami"),
          (4.10, 8.18, "e divulgou uma carta se dizendo o verdadeiro presidente eleito do Brasil."), (8.76, 9.69, "Falou em fraude,"),
          (9.86, 11.10, "sem apresentar provas,"), (11.46, 13.33, "e agradeceu a Milei e a Trump."), (14.00, 15.65, "A carta teve três versões."),
          (16.08, 18.03, "A primeira saiu com o brasão antigo:"), (18.42, 20.02, "Estados Unidos do Brazil."), (20.60, 23.14, "Na última, trocou presidente por líder."),
          (23.96, 26.34, "O TSE disse que a eleição foi normal."), (26.78, 29.09, "E até Tarcísio pediu respeito às urnas."), (29.66, 30.39, "Na minha opinião,"),
          (30.74, 33.23, "quem perde precisa aceitar o resultado."), (33.66, 34.77, "Isso é democracia."), (35.27, 36.47, "E você, o que acha?"), (36.88, 37.46, "Comenta aqui.")]
HOT = {"DERROTADO", "MIAMI", "VERDADEIRO", "PRESIDENTE", "ELEITO", "FRAUDE,", "PROVAS,", "MILEI", "TRUMP.", "TRÊS", "VERSÕES.", "BRASÃO", "BRAZIL.",
       "LÍDER.", "TSE", "NORMAL.", "TARCÍSIO", "URNAS.", "OPINIÃO,", "PERDE", "ACEITAR", "RESULTADO.", "DEMOCRACIA.", "AQUI."}
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
CARDS = [(0.6, 13.6, "CARTA EM MIAMI", ["SE DISSE PRESIDENTE", "ELEITO"]), (13.6, 23.6, "3 VERSÕES", ["BRAZIL COM Z", "PRESIDENTE → LÍDER"]),
         (23.6, 29.4, "REAÇÕES", ["TSE: ELEIÇÃO NORMAL", "TARCÍSIO: RESPEITO"]), (29.4, EDIT_END, "OPINIÃO", ["QUEM PERDE", "ACEITA O RESULTADO"])]
CAP_Y, CARD_Y = 1430, 1712
# ---------------------------------------------------------------- mapa (Américas)
GJ = json.load(open(f"{S}/v80/world.json"))
LAT0 = math.cos(math.radians(-5))
def proj(lon, lat): return (lon * LAT0, -lat)
def rings_of(g):
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]; out = []
    for p in polys:
        ring = [(x, y) for x, y in p[0]]
        if all(x > -30 or x < -125 or y > 50 for x, y in ring): continue
        out.append(np.array([proj(x, y) for x, y in ring], np.float32))
    return out
SHAPES = {}
for f in GJ["features"]:
    r = rings_of(f["geometry"])
    if r: SHAPES[f["id"]] = r
PTS = {"BUE": (-58.4, -34.6), "ECU": (-78.5, -0.2), "MIA": (-80.19, 25.76)}
def P(k): return np.array(proj(*PTS[k]), np.float32)
CAM = [(0.0, -64, -6, 11.5), (1.8, -68, -5, 13.5), (8.4, -66, -10, 9.0)]
MAPBOX = (130, 230, 1050, 1260); OX, OY = (MAPBOX[0] + MAPBOX[2]) / 2 + 20, (MAPBOX[1] + MAPBOX[3]) / 2 - 20
def cam(t):
    i = max(k for k, c in enumerate(CAM) if c[0] <= t); t0, lo1, la1, s1 = CAM[i]
    _, lo0, la0, s0 = CAM[i - 1] if i else CAM[0]; k = eio((t - t0) / 1.6)
    ls = math.log(s0) + (math.log(s1) - math.log(s0)) * k
    return np.array(proj(lo0 + (lo1 - lo0) * k, la0 + (la1 - la0) * k), np.float32), math.exp(ls)
def to_screen(p, c, s): return (float(OX + (p[0] - c[0]) * s), float(OY + (p[1] - c[1]) * s))
yy_, xx_ = np.mgrid[0:H, 0:W].astype(np.float32)
OCEAN = (np.array([6, 22, 44], np.float32) + np.array([10, 30, 56], np.float32) * np.clip(1 - np.sqrt(((xx_ - W / 2) / W) ** 2 + ((yy_ - 700) / H) ** 2) * 1.6, 0, 1)[..., None])
OCEAN = np.clip(OCEAN, 0, 255).astype(np.uint8); del yy_, xx_
HLC = {"ARG": (2.0, (90, 120, 170)), "ECU": (2.9, (90, 120, 170)), "USA": (3.6, (90, 120, 170))}
def draw_map(t):
    c, s = cam(t); img = OCEAN.copy(); SH = 3; F = 1 << SH
    def sc(rings): return [(((r - c) * s + (OX, OY)) * F).astype(np.int32) for r in rings]
    for iso, rings in SHAPES.items():
        p = sc(rings); col = np.array((58, 70, 94), np.float32)
        if iso == "BRA": col = np.array((36, 120, 76), np.float32)
        if iso in HLC: k = clamp((t - HLC[iso][0]) / 0.5); col = col * (1 - k) + np.array(HLC[iso][1], np.float32) * k
        cv2.fillPoly(img, p, tuple(int(v) for v in col), cv2.LINE_AA, SH); cv2.polylines(img, p, True, (150, 165, 190), 2, cv2.LINE_AA, SH)
    return Image.fromarray(img).convert("RGBA"), c, s
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
MANCH = Image.open(f"{V}/manchete.png").convert("RGBA")
def paper(lines, w=760, h=520, head="CARTA À NAÇÃO BRASILEIRA", seal=None):
    """folha de carta genérica (sem brasão oficial): título, linhas de texto fingidas e as frases que importam"""
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 18, fill=(250, 248, 240, 255), outline=(200, 196, 180, 255), width=3)
    y = 40
    if seal:
        d.ellipse((w / 2 - 46, y, w / 2 + 46, y + 92), outline=(150, 130, 70, 255), width=5); d.polygon([(w / 2 + 30 * math.cos(math.radians(-90 + 36 * i)) * (1 if i % 2 == 0 else 0.42), y + 46 + 30 * math.sin(math.radians(-90 + 36 * i)) * (1 if i % 2 == 0 else 0.42)) for i in range(10)], fill=(150, 130, 70, 255)); y += 110
        d.text((w / 2, y), seal, font=MF("ExtraBold", 30), fill=INK + (255,), anchor="mm"); y += 50
    d.text((w / 2, y), head, font=MF("ExtraBold", 28), fill=INK + (255,), anchor="mm"); y += 50
    for ln in lines:
        if ln is None: d.rounded_rectangle((60, y, w - 60 - (y * 7) % 140, y + 12), 6, fill=(200, 200, 200, 255)); y += 32
        else: d.text((w / 2, y + 6), ln, font=MF("ExtraBold", 34), fill=INK + (255,), anchor="mm"); y += 54
    return im
_pp = {}
def P1():
    if "a" not in _pp: _pp["a"] = paper([None, None, "verdadeiro presidente", "eleito do Brasil", None, None, None], seal="ESTADOS UNIDOS DO BRAZIL")
    return _pp["a"]
def overlays(fr, t, c, s):
    d = ImageDraw.Draw(fr)
    # 0-1.8: manchete
    k = env(t, 0.0, 1.85, 0.2)
    if k > 0:
        put(fr, chipimg("DERROTADO NO 2º TURNO", RED, 40), CX, 360, k, 0.8 + 0.2 * bo(t / 0.4))
        card = Image.new("RGBA", (MANCH.width + 40, MANCH.height + 40), (255, 255, 255, 255)); card.alpha_composite(MANCH, (20, 20))
        sc_ = 900 / card.width; put(fr, card, CX, 640, k, sc_ * (0.92 + 0.08 * eo(t / 0.5)), -2)
        put(fr, txt("Estadão · 29/10/2026", MF("SemiBold", 28), WHITE, 3), CX, 870, k)
    # 1.8-8.3: rota no mapa
    bue, ecu, mia = (to_screen(P(k_), c, s) for k_ in ("BUE", "ECU", "MIA"))
    k = env(t, 1.85, 8.3)
    if k > 0:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        g1 = eo((t - 2.0) / 1.0); g2 = eo((t - 2.9) / 1.1)
        p1 = path(bue, ecu, g1, -0.25); p2 = path(ecu, mia, g2, 0.2) if t > 2.9 else []
        if len(p1) > 1: dashed(dl, p1, YEL + (int(255 * k),), 7)
        if len(p2) > 1: dashed(dl, p2, YEL + (int(255 * k),), 7)
        fr.alpha_composite(lay)
        pin(fr, *bue, "ARGENTINA", (70, 100, 160), env(t, 1.95, 8.3), dy=54)
        pin(fr, *ecu, "ESCALA NO EQUADOR", (70, 100, 160), env(t, 2.9, 8.3), dy=54)
        pin(fr, *mia, "MIAMI", RED, env(t, 3.7, 8.3), dy=-52)
        pl = p2 if p2 else p1
        if len(pl) > 1 and t < 4.1:
            (x0, y0), (x1, y1) = pl[-2], pl[-1]; ang = math.degrees(math.atan2(-(y1 - y0), x1 - x0)) - 45
            put(fr, emoji("✈️", 70), x1, y1, k, 1, ang)
        if t > 4.2:  # a carta
            kk = env(t, 4.2, 8.3); im = paper([None, None, None, "verdadeiro presidente" if t > 6.0 else "", "eleito do Brasil" if t > 6.0 else "", None, None], head="CARTA À NAÇÃO BRASILEIRA")
            put(fr, im, CX, 780, kk, 0.6 + 0.4 * bo((t - 4.2) / 0.4), -3)
            if t > 6.0:
                g = eo((t - 6.0) / 0.4); lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).rounded_rectangle((CX - 300, 742, CX - 300 + 600 * g, 852), 14, outline=RED + (int(255 * kk),), width=7)
                fr.alpha_composite(lay.rotate(-3, Image.BICUBIC, center=(CX, 780)))
    # 8.6-13.4: fraude sem provas + agradecimentos
    k = env(t, 8.6, 13.5)
    if k > 0:
        put(fr, txt("FALOU EM", ANTON(90), WHITE, 6, NAVY), CX, 380, k)
        put(fr, txt("FRAUDE", ANTON(170), GOLD_L, 8, NAVY), CX, 520, k, 0.8 + 0.2 * bo((t - 8.7) / 0.4))
        if t > 9.85: put(fr, stamp("SEM PROVAS", RED, 80, -8), CX, 720, env(t, 9.85, 13.5), 0.7 + 0.3 * bo(clamp((t - 9.85) / 0.25), 2.0))
        if t > 11.4:
            put(fr, txt("AGRADECEU A", MF("ExtraBold", 40), WHITE, 3), CX, 900, env(t, 11.4, 13.5))
            for i, (em, nm, ti) in enumerate([("🇦🇷", "MILEI", 11.9), ("🇺🇸", "TRUMP", 12.5)]):
                if t < ti: continue
                x = CX + (i * 2 - 1) * 200; kk = env(t, ti, 13.5)
                put(fr, emoji(em, 120), x, 1030, kk, 0.6 + 0.4 * bo((t - ti) / 0.35)); put(fr, chipimg(nm, NAVY, 34), x, 1130, kk)
    # 14-23.4: as três versões
    k = env(t, 14.0, 23.5)
    if k > 0:
        put(fr, txt("3 VERSÕES", ANTON(110), WHITE, 6, NAVY), CX, 360, k, 0.85 + 0.15 * bo((t - 14.0) / 0.4))
        if t < 16.0:
            for i in range(3):
                ti = 14.4 + i * 0.4
                if t < ti: continue
                im = paper([None] * 7, w=480, h=330, head=f"VERSÃO {i + 1}"); put(fr, im, CX - 220 + i * 220, 700 + (i - 1) * 30, env(t, ti, 16.2), 0.6 + 0.4 * bo((t - ti) / 0.35), (i - 1) * -6)
        elif t < 20.5:
            kk = env(t, 16.0, 20.5); put(fr, chipimg("VERSÃO 1", (70, 100, 160), 34), CX, 470, kk)
            im = P1(); put(fr, im, CX, 800, kk, 0.9 + 0.1 * bo((t - 16.0) / 0.35))
            if t > 18.4:  # o Z circulado
                g = eo((t - 18.4) / 0.4); fz = MF("ExtraBold", 30); w0 = fz.getlength("ESTADOS UNIDOS DO BRAZIL"); xz = CX - w0 / 2 + fz.getlength("ESTADOS UNIDOS DO BRA") + fz.getlength("Z") / 2 - 14
                yz = 800 - im.height / 2 + 40 + 110 + 2; lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(lay).ellipse((xz - 30 - 10 * (1 - g), yz - 30, xz + 30, yz + 30), outline=RED + (int(255 * kk * g),), width=6); fr.alpha_composite(lay)
                put(fr, chipimg("NOME E GRAFIA ANTIGOS DO PAÍS", RED, 30), CX, 1130, env(t, 18.6, 20.5))
        else:
            kk = env(t, 20.5, 23.5); put(fr, chipimg("VERSÃO FINAL", (70, 100, 160), 34), CX, 470, kk)
            fa = ANTON(120); y1, y2 = 700, 900
            put(fr, txt("PRESIDENTE", fa, WHITE, 7, NAVY), CX, y1, kk)
            if t > 21.2:
                g = eo((t - 21.2) / 0.35); tw = fa.getlength("PRESIDENTE"); ImageDraw.Draw(fr).line((CX - tw / 2 - 10, y1 + 8, CX - tw / 2 - 10 + (tw + 20) * g, y1 + 8), fill=RED + (int(255 * kk),), width=14)
            if t > 21.8: put(fr, txt("LÍDER", ANTON(150), GOLD_L, 8, NAVY), CX, y2, env(t, 21.8, 23.5), 0.6 + 0.4 * bo((t - 21.8) / 0.35, 2.2))
    # 23.9-29.4: reações
    k = env(t, 23.9, 29.5)
    if k > 0:
        def quote(y, who, role, q, ti):
            kk = env(t, ti, 29.5)
            if kk <= 0: return
            bw, bh = 860, 300; im = Image.new("RGBA", (bw, bh), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
            dd.rounded_rectangle((0, 0, bw - 1, bh - 1), 26, fill=(10, 26, 56, 235), outline=GOLD + (255,), width=3)
            dd.text((40, 34), who, font=ANTON(52), fill=GOLD_L + (255,)); dd.text((40, 104), role, font=MF("SemiBold", 26), fill=(200, 210, 230, 255))
            ff = MF("ExtraBold", 38); words = q.split(); lines = [""]
            for w in words:
                if ff.getlength((lines[-1] + " " + w).strip()) > bw - 80: lines.append("")
                lines[-1] = (lines[-1] + " " + w).strip()
            for i, l in enumerate(lines): dd.text((40, 160 + i * 50), l, font=ff, fill=WHITE + (255,))
            put(fr, im, CX, y, kk, 0.85 + 0.15 * bo((t - ti) / 0.35))
        quote(520, "TSE", "Kassio Nunes Marques, presidente do tribunal", "“Eleições transcorreram com absoluta normalidade”", 24.0)
        quote(880, "TARCÍSIO", "Governador de São Paulo", "“O caminho é respeitar o resultado das urnas e seguir em frente”", 26.8)
        if t > 25.2: put(fr, txt("TSE: questionamentos pelo devido processo legal serão analisados", MF("SemiBold", 24), (200, 210, 230), 3), CX, 1090, env(t, 25.2, 29.5))
    # 29.6-34.9: opinião
    k = env(t, 29.6, 35.0)
    if k > 0:
        put(fr, chipimg("NA MINHA OPINIÃO", (30, 30, 40), 40, GOLD_L), CX, 380, k)
        if t > 30.7: put(fr, txt("QUEM PERDE", ANTON(130), WHITE, 7, NAVY), CX, 560, env(t, 30.7, 35.0), 0.8 + 0.2 * bo((t - 30.7) / 0.35))
        if t > 31.9: put(fr, txt("ACEITA O RESULTADO", ANTON(96), GOLD_L, 6, NAVY), CX, 720, env(t, 31.9, 35.0), 0.8 + 0.2 * bo((t - 31.9) / 0.35))
        if t > 33.6: put(fr, emoji("🗳️", 150), CX, 930, env(t, 33.6, 35.0), 0.6 + 0.4 * bo((t - 33.6) / 0.35)); put(fr, chipimg("ISSO É DEMOCRACIA", GOLD, 40, NAVY), CX, 1080, env(t, 33.7, 35.0))
    # 35.2-fim: pergunta
    k = env(t, 35.2, EDIT_END + 0.4, 0.3, 0.3)
    if k > 0:
        put(fr, txt("E VOCÊ,", ANTON(130), WHITE, 7, NAVY), CX, 520, k, 0.9 + 0.1 * bo((t - 35.2) / 0.4)); put(fr, txt("O QUE ACHA?", ANTON(140), GOLD_L, 7, NAVY), CX, 680, k)
        put(fr, chipimg("COMENTA AQUI", RED, 46), CX, 880, k, 1 + 0.04 * math.sin(t * 6))
    if 0.5 < t < EDIT_END: R.credit(fr, "Fontes: Estadão, Poder360, CNN Brasil, Metrópoles", W - 30, 168, clamp((t - 0.5) / 0.4))
def map_alpha(t):
    on = lambda a, b: clamp((t - a) / 0.5) * (1 - clamp((t - b) / 0.5))
    return 0.22 + 0.73 * on(1.6, 4.4) + 0.3 * on(4.4, 8.2)
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); mp, c, s = draw_map(tt); a = map_alpha(tt)
    fr = Image.blend(Image.fromarray(OCEAN).convert("RGBA"), mp, min(a, 0.95))
    if a < 0.5: fr.alpha_composite(Image.new("RGBA", (W, H), (4, 12, 26, int(90 * (1 - a)))))
    overlays(fr, tt, c, s)
    g = np.zeros((520, W, 4), np.uint8); g[..., :3] = (3, 10, 22); g[..., 3] = np.linspace(0, 210, 520)[:, None].astype(np.uint8); fr.alpha_composite(Image.fromarray(g), (0, H - 520))
    M.caption(fr, tt, CAP_Y, 54)
    for a_, b_, kick, lines in CARDS:
        kc = clamp((tt - a_) / 0.4) * (1 - clamp((tt - (b_ - 0.3)) / 0.3))
        if kc > 0: BAR.lower_card(fr, kick, lines, CARD_Y, kc, fs=40)
    cta = clamp((t - 35.2) / 0.4) if t > 35.2 else 0.0
    BAR.draw_bar(fr, clamp(t / END_IN), "canal", eo((t - 0.2) / 0.6), cta, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(fr, t)
    if t >= END_IN: fr.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return fr.convert("RGB")
def capa(out, var="A"):
    mp, c, s = draw_map(3.9); fr = Image.blend(Image.fromarray(OCEAN).convert("RGBA"), mp, 0.55 if var == "A" else 0.3)
    fr.alpha_composite(Image.new("RGBA", (W, H), (4, 12, 26, 90)))
    if var == "A":
        put(fr, chipimg("DERROTADO NO 2º TURNO", RED, 44), CX, 250)
        put(fr, txt("FLÁVIO SE DIZ", ANTON(120), WHITE, 7, NAVY), CX, 400); put(fr, txt("“PRESIDENTE”", ANTON(150), GOLD_L, 8, NAVY), CX, 560)
        put(fr, txt("EM CARTA NOS EUA", ANTON(84), WHITE, 6, NAVY), CX, 700)
        put(fr, P1(), CX, 1080, 1, 0.95, -4); put(fr, stamp("SEM PROVAS", RED, 80, -10), CX + 200, 1330)
        put(fr, emoji("✈️", 120), CX - 330, 1600); put(fr, emoji("🇺🇸", 120), CX + 330, 1600)
    else:
        put(fr, txt("CARTA EM MIAMI", ANTON(110), WHITE, 7, NAVY), CX, 300); put(fr, txt("3 VERSÕES", ANTON(170), GOLD_L, 8, NAVY), CX, 470)
        fa = ANTON(120); put(fr, txt("PRESIDENTE", fa, WHITE, 7, NAVY), CX, 700); tw = fa.getlength("PRESIDENTE")
        ImageDraw.Draw(fr).line((CX - tw / 2 - 10, 708, CX + tw / 2 + 10, 708), fill=RED + (255,), width=16)
        put(fr, txt("LÍDER", ANTON(160), GOLD_L, 8, NAVY), CX, 880)
        put(fr, chipimg("TSE: ELEIÇÃO NORMAL", (70, 100, 160), 44), CX, 1090); put(fr, chipimg("TARCÍSIO: RESPEITO ÀS URNAS", NAVY, 40), CX, 1210)
        put(fr, emoji("🗳️", 150), CX, 1480)
    BAR.draw_bar(fr, 0.0, "canal"); fr.alpha_composite(R.top, (R.HDX, 0)); fr.convert("RGB").save(out, quality=95)
def audio(vout):
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{V}/vo.mp3", "-ar", "48000", "-ac", "2", f"{V}/vo48.wav"], check=True)
    vo = R.readw(f"{V}/vo48.wav"); vt = np.zeros((n, 2), np.float32); vt[:min(len(vo), n)] = vo[:n]
    bed = R.readw(f"{S}/v49/bed.wav"); xf = int(1.5 * SR); loop = bed.copy()
    while len(loop) < n:
        r = np.linspace(0, 1, xf)[:, None]; loop[-xf:] = loop[-xf:] * (1 - r) + bed[:xf] * r; loop = np.concatenate([loop, bed[xf:]])
    tl = np.arange(n) / SR; gain = 0.10 * np.clip(tl / 1.0, 0, 1) * np.clip(1 - (tl - (TOTAL - 1.8)) / 1.6, 0, 1)
    R.writew(f"{V}/voice.wav", vt); R.writew(f"{V}/song.wav", loop[:n] * gain[:, None])
    def pop():
        tt = np.arange(int(0.12 * SR)) / SR; y = np.sin(2 * np.pi * (500 + 900 * tt / 0.12) * tt) * np.exp(-tt / 0.03); return np.stack([y, y], 1)
    ev = [(a - 0.15, sfx.whoosh(0.5), 0.15) for a in (1.85, 4.2, 8.6, 14.0, 16.0, 20.5, 23.9, 29.6, 35.2)]
    ev += [(x, pop(), 0.35) for x in (1.95, 2.9, 3.7, 11.9, 12.5, 14.4, 14.8, 15.2, 21.8, 24.0, 26.8, 33.6)]
    ev += [(9.85, sfx.thud(0.45), 0.3), (6.0, sfx.click(), 0.35), (18.4, sfx.click(), 0.35), (21.2, sfx.thud(0.35), 0.25), (30.7, sfx.thud(0.35), 0.2), (END_IN - 0.3, sfx.whoosh(0.6), 0.2)]
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
