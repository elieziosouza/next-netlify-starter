"""Mapa animado 9:16: a suposta saída de Flávio Bolsonaro pela Tríplice Fronteira (rota relatada pelo Infobae, NÃO confirmada).
América do Sul com o Brasil e os vizinhos, zoom em Foz do Iguaçu / Puerto Iguazú, linha da rota relatada, jato LV-JQW com seta
pontilhada para a Flórida e o carimbo "NÃO DECOLOU (radar)", cartões com os fatos e os dois lados (campanha nega, PF investiga).
Narração do ElevenLabs. Legenda karaokê, caixa fixa e barra lateral do canal. Usa os ajudantes do render_exercito."""
import sys, math, subprocess, importlib.util, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("rex", f"{S}/work/render_exercito.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; eo = R.ease_out; ei = R.ease_in; eio = R.ease_io; bo = R.back_out
V = f"{S}/v80"; FD = f"{S}/fontdl"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
EDIT_END = 48.85; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = EDIT_END; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
GOLD = R.GOLD; GOLD_L = R.GOLD_L; NAVY = R.NAVY; WHITE = (255, 255, 255); RED = (226, 52, 52); GREEN_BR = (40, 150, 90); YEL = (255, 214, 64)
def ANTON(s): return ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s)
MF = R.MF
# ---------------------------------------------------------------- legenda (texto revisado à mão)
CAPTXT = [(0.09, 1.77, "Onde está Flávio Bolsonaro?"), (2.26, 6.27, "Moraes mandou ele entregar os passaportes e proibiu de sair do país."),
          (6.62, 7.50, "Ele não entregou,"), (7.96, 9.96, "e a PF cancelou os documentos."), (10.42, 11.72, "Aí veio a notícia:"),
          (12.12, 14.41, "um site argentino, o Infobae,"), (14.58, 17.42, "disse que ele teria cruzado a fronteira em Foz do Iguaçu,"),
          (17.66, 18.95, "só com a identidade,"), (19.29, 20.55, "o que o Mercosul permite."), (20.95, 23.30, "De lá, iria até Puerto Iguazú"),
          (23.54, 25.32, "e pegaria um jatinho para a Flórida."), (25.88, 27.24, "Mas tem coisa que não fecha."),
          (27.67, 30.86, "Os sites de radar mostram que esse avião não decolou."), (31.32, 34.18, "E a Argentina diz que não tem registro da entrada dele."),
          (34.68, 37.16, "A campanha nega que ele tenha saído do Brasil."), (37.56, 39.14, "A Polícia Federal investiga."),
          (39.64, 40.46, "Na minha opinião,"), (40.70, 43.21, "se a Justiça mandou ficar, tem que ficar."), (43.54, 44.97, "Ninguém está acima da lei."),
          (45.50, 45.99, "E você,"), (46.33, 47.66, "acha que ele saiu do país?"), (47.99, 48.62, "Comenta aqui.")]
HOT = {"FLÁVIO", "BOLSONARO?", "PASSAPORTES", "CANCELOU", "INFOBAE,", "FOZ", "IGUAÇU,", "IDENTIDADE,", "MERCOSUL", "IGUAZÚ", "FLÓRIDA.", "NÃO", "DECOLOU.",
       "REGISTRO", "NEGA", "INVESTIGA.", "OPINIÃO,", "LEI.", "AQUI."}
CAPS = []
for a, b, txt in CAPTXT:
    ws = txt.upper().split(); n = len(ws); k = max(1, math.ceil(n / 4)); per = math.ceil(n / k); chunks = [ws[i:i + per] for i in range(0, n, per)]
    tot = sum(len(w) + 2 for w in ws); acc = 0
    for ch in chunks:
        c0 = a + (b - a) * acc / tot; ts = []
        for w in ch: ts.append(a + (b - a - 0.06) * acc / tot); acc += len(w) + 2
        CAPS.append(dict(words=ch, ts=ts, start=c0, end=a + (b - a) * acc / tot + (0.25 if ch is chunks[-1] else 0.0), src="au" if any(w in HOT for w in ch) else "me"))
for i in range(len(CAPS) - 1): CAPS[i]["end"] = min(CAPS[i]["end"], CAPS[i + 1]["start"])
R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
CARDS = [(0.6, 25.8, "STF · 26/10", ["PASSAPORTES", "CANCELADOS"]), (25.8, 39.5, "O QUE NÃO FECHA", ["SAÍDA NÃO", "CONFIRMADA"]), (39.5, EDIT_END, "OPINIÃO", ["NINGUÉM ACIMA", "DA LEI"])]
CAP_Y, CARD_Y = 1430, 1712
# ---------------------------------------------------------------- mapa
GJ = json.load(open(f"{V}/world.json"))
SA = {"BRA", "ARG", "PRY", "URY", "BOL", "PER", "COL", "VEN", "GUY", "SUR", "CHL", "ECU", "USA", "MEX", "CUB", "PAN", "CRI", "NIC", "HND", "GTM", "SLV", "BLZ", "FRA"}
LAT0 = math.cos(math.radians(-15))
def proj(lon, lat): return (lon * LAT0, -lat)
SHAPES = {}
for f in GJ["features"]:
    if f["id"] not in SA: continue
    g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    rings = []
    for p in polys:
        ring = [(x, y) for x, y in p[0]]
        if f["id"] == "FRA" and not all(-56 < x < -50 for x, _ in ring): continue      # só a Guiana Francesa
        if f["id"] == "USA" and any(x < -130 for x, _ in ring): continue              # sem Alasca e Havaí
        rings.append(np.array([proj(x, y) for x, y in ring], np.float32))
    if rings: SHAPES[f["id"]] = rings
NAMES = {"BRA": ("BRASIL", -52, -11), "ARG": ("ARGENTINA", -65, -36), "PRY": ("PARAGUAI", -58.3, -23.3), "URY": ("URUGUAI", -56, -32.8), "BOL": ("BOLÍVIA", -64.5, -17),
         "PER": ("PERU", -75, -10), "COL": ("COLÔMBIA", -73, 4), "VEN": ("VENEZUELA", -66, 7.5), "CHL": ("CHILE", -71, -30), "ECU": ("EQUADOR", -78.3, -1.5),
         "GUY": ("GUIANA", -59, 5), "SUR": ("SURINAME", -55.9, 4), "USA": ("EUA", -98, 38)}
PTS = {"BSB": (-47.88, -15.79), "FOZ": (-54.58, -25.52), "PIG": (-54.57, -25.60), "FLA": (-80.2, 26.0)}
def P(k): return np.array(proj(*PTS[k]), np.float32)
# câmera: (início, centro lon, centro lat, escala px/grau)
CAM = [(0.0, -57, -17, 22), (10.4, -51, -20, 52), (17.4, -54.58, -25.56, 420), (23.2, -66, -2, 9.5), (27.4, -54.58, -25.56, 260), (34.5, -57, -17, 22)]
MAPBOX = (130, 230, 1050, 1260); OX, OY = (MAPBOX[0] + MAPBOX[2]) / 2 + 20, (MAPBOX[1] + MAPBOX[3]) / 2
def cam(t):
    i = max(k for k, c in enumerate(CAM) if c[0] <= t); t0, lo1, la1, s1 = CAM[i]
    _, lo0, la0, s0 = CAM[i - 1] if i else CAM[0]; k = eio((t - t0) / 1.4)
    ls = math.log(s0) + (math.log(s1) - math.log(s0)) * k
    return np.array(proj(lo0 + (lo1 - lo0) * k, la0 + (la1 - la0) * k), np.float32), math.exp(ls)
def to_screen(p, c, s): return (float(OX + (p[0] - c[0]) * s), float(OY + (p[1] - c[1]) * s))
yy_, xx_ = np.mgrid[0:H, 0:W].astype(np.float32)
OCEAN = (np.array([6, 22, 44], np.float32) + np.array([10, 30, 56], np.float32) * np.clip(1 - np.sqrt(((xx_ - W / 2) / W) ** 2 + ((yy_ - 700) / H) ** 2) * 1.6, 0, 1)[..., None])
OCEAN = np.clip(OCEAN, 0, 255).astype(np.uint8); del yy_, xx_
def draw_map(t):
    c, s = cam(t); img = OCEAN.copy(); SH = 3; F = 1 << SH
    for iso, rings in SHAPES.items():
        polys = [(((r - c) * s + (OX, OY)) * F).astype(np.int32) for r in rings]
        col = (36, 120, 76) if iso == "BRA" else ((150, 120, 60) if iso == "ARG" else ((70, 84, 110) if iso != "USA" else (80, 70, 110)))
        cv2.fillPoly(img, polys, col, cv2.LINE_AA, SH); cv2.polylines(img, polys, True, (200, 215, 235), 2, cv2.LINE_AA, SH)
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
FLAVIO = None
def portrait():
    global FLAVIO
    if FLAVIO is None:
        src = Image.open(f"{S}/v61/dl/flavio.jpg").convert("RGB"); w = 300; h = 360; sc = max(w / src.width, h / src.height)
        im = src.resize((int(src.width * sc) + 1, int(src.height * sc) + 1), Image.LANCZOS); x0 = (im.width - w) // 2; im = im.crop((x0, 0, x0 + w, h))
        g = np.asarray(im, np.float32) @ np.array([0.3, 0.59, 0.11]); im = Image.fromarray(np.clip(np.repeat(g[..., None], 3, 2), 0, 255).astype(np.uint8))
        card = Image.new("RGBA", (w + 24, h + 24), WHITE + (255,)); card.paste(im, (12, 12)); FLAVIO = card
    return FLAVIO
def overlays(fr, t, c, s):
    d = ImageDraw.Draw(fr)
    # 0-10: quem e por quê
    k = env(t, 0.1, 10.3)
    if k > 0:
        put(fr, portrait(), CX, 560, k, 0.9 + 0.1 * bo((t - 0.1) / 0.4), -3)
        put(fr, txt("?", ANTON(220), YEL, 8, NAVY), CX + 190, 430, k * clamp((t - 0.4) / 0.3), 1 + 0.05 * math.sin(t * 4))
        if t > 2.3: put(fr, stamp("PROIBIDO DE SAIR DO PAÍS", RED, 50, 6), CX, 820, env(t, 2.3, 10.3), 1.0)
        if t > 7.9: put(fr, chipimg("PF CANCELOU OS PASSAPORTES", RED, 32), CX, 960, env(t, 7.9, 10.3))
    # pinos e rota
    bsb = to_screen(P("BSB"), c, s); foz = to_screen(P("FOZ"), c, s); pig = to_screen(P("PIG"), c, s); fla = to_screen(P("FLA"), c, s)
    if 10.6 <= t < 34.6:
        pin(fr, *bsb, "BRASÍLIA", NAVY, env(t, 10.8, 17.4))
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        if t < 17.6: dashed(dl, path(bsb, foz, (t - 11.5) / 3.0, 0.12), YEL + (255,), 8)
        if 17.6 <= t < 23.4:
            dl.line((foz[0], foz[1], foz[0] + (pig[0] - foz[0]) * eo((t - 18.0) / 1.6), foz[1] + (pig[1] - foz[1]) * eo((t - 18.0) / 1.6)), fill=YEL + (255,), width=12)
        if 23.4 <= t < 34.6: dashed(dl, path(pig, fla, (t - 23.6) / 1.6, -0.2), (255, 255, 255, 220), 6, 18, 14)
        fr.alpha_composite(lay)
        if 12.0 <= t < 23.4: pin(fr, *foz, "FOZ DO IGUAÇU (BR)", GREEN_BR, env(t, 14.6, 23.4))
        if 17.6 <= t < 34.6: pin(fr, *pig, "PUERTO IGUAZÚ (AR)", (60, 120, 200), env(t, 18.2, 34.6), dy=58)
        if 17.7 <= t < 23.2: put(fr, chipimg("🪪 RG vale no Mercosul" if False else "RG VALE NO MERCOSUL", NAVY, 30), CX, 1150, env(t, 17.7, 23.2))
        if 23.6 <= t < 34.6:
            pin(fr, *fla, "FLÓRIDA", (120, 90, 170), env(t, 24.6, 27.2))
            pl = emoji("🛩️", 70); put(fr, pl, pig[0] + 70, pig[1] + 10, env(t, 23.6, 34.6))
            put(fr, chipimg("JATO LV-JQW", (40, 40, 50), 26), pig[0] + 90, pig[1] + 120, env(t, 23.8, 27.4))
        if t > 27.7 and t < 34.6:
            put(fr, stamp("NÃO DECOLOU", RED, 92, -8), CX, 470, env(t, 27.7, 34.6), 0.7 + 0.3 * bo(clamp((t - 27.7) / 0.25), 2.0))
            put(fr, txt("segundo sites de radar", MF("Bold", 34), WHITE, 3), CX, 590, env(t, 28.2, 34.6))
        if t > 31.3 and t < 34.6:
            put(fr, chipimg("ARGENTINA: SEM REGISTRO DE ENTRADA", (60, 120, 200), 32), CX, 1120, env(t, 31.3, 34.6))
    if 10.4 <= t < 34.6:
        put(fr, chipimg("ROTA RELATADA PELO INFOBAE · NÃO CONFIRMADA", (30, 30, 40), 24, YEL), CX, 260, env(t, 12.1, 34.6))
    # 34.7-39.5: os dois lados
    for i, (a, txt_, col, em) in enumerate([(34.7, "CAMPANHA NEGA A SAÍDA", (90, 90, 110), "🗣️"), (37.6, "PF INVESTIGA", NAVY, "🔎")]):
        if t < a or t > 39.5: continue
        kk = env(t, a, 39.5); put(fr, emoji(em, 120), CX, 520 + i * 330, kk, 0.6 + 0.4 * bo((t - a) / 0.35)); put(fr, chipimg(txt_, col, 44), CX, 650 + i * 330, kk)
    # 39.6-45.4: opinião
    k = env(t, 39.6, 45.4)
    if k > 0:
        put(fr, chipimg("NA MINHA OPINIÃO", (30, 30, 40), 34, GOLD_L), CX, 380, k)
        put(fr, emoji("⚖️", 200), CX, 640, k, 0.8 + 0.2 * bo((t - 39.8) / 0.4))
        if t > 43.5: put(fr, txt("NINGUÉM ESTÁ", ANTON(110), WHITE, 6, NAVY), CX, 900, env(t, 43.5, 45.4)); put(fr, txt("ACIMA DA LEI", ANTON(110), GOLD_L, 6, NAVY), CX, 1030, env(t, 43.6, 45.4))
    # 45.5-fim: pergunta
    k = env(t, 45.5, EDIT_END + 0.4, 0.3, 0.3)
    if k > 0:
        put(fr, txt("ELE SAIU", ANTON(140), WHITE, 7, NAVY), CX, 520, k, 0.9 + 0.1 * bo((t - 45.5) / 0.4)); put(fr, txt("DO PAÍS?", ANTON(140), GOLD_L, 7, NAVY), CX, 680, k)
        put(fr, chipimg("COMENTA AQUI 👇" if False else "COMENTA AQUI", RED, 46), CX, 880, k, 1 + 0.04 * math.sin(t * 6))
    if 0.5 < t < EDIT_END: R.credit(fr, "Fontes: Infobae, Metrópoles, Agência Brasil, Congresso em Foco", W - 30, 168, clamp((t - 0.5) / 0.4))
def map_alpha(t):
    """o mapa aparece da rota até os dois lados; antes e depois fica escuro por trás dos cartões"""
    return clamp((t - 10.0) / 0.6) * (1 - clamp((t - 34.6) / 0.6)) * 0.95 + 0.25
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); mp, c, s = draw_map(tt); a = map_alpha(tt)
    fr = Image.blend(Image.fromarray(OCEAN).convert("RGBA"), mp, a)
    if 0 <= tt < 10.4 or tt >= 34.6:
        for iso, (nm, lo, la) in NAMES.items():
            if iso == "USA": continue
            x, y = to_screen(np.array(proj(lo, la)), c, s); put(fr, txt(nm, MF("Bold", 22), (220, 230, 245), 3), x, y, 0.35 * a)
    elif tt < 17.4:
        for iso in ("BRA", "ARG", "PRY", "URY", "BOL"):
            nm, lo, la = NAMES[iso]; x, y = to_screen(np.array(proj(lo, la)), c, s); put(fr, txt(nm, MF("ExtraBold", 30), WHITE, 3), x, y, env(tt, 10.6, 17.4))
    overlays(fr, tt, c, s)
    g = np.zeros((520, W, 4), np.uint8); g[..., :3] = (3, 10, 22); g[..., 3] = np.linspace(0, 210, 520)[:, None].astype(np.uint8); fr.alpha_composite(Image.fromarray(g), (0, H - 520))
    M.caption(fr, tt, CAP_Y, 54)
    for a_, b_, kick, lines in CARDS:
        kc = clamp((tt - a_) / 0.4) * (1 - clamp((tt - (b_ - 0.3)) / 0.3))
        if kc > 0: BAR.lower_card(fr, kick, lines, CARD_Y, kc, fs=40)
    cta = clamp((t - 45.5) / 0.4) if t > 45.5 else 0.0
    BAR.draw_bar(fr, clamp(t / END_IN), "canal", eo((t - 0.2) / 0.6), cta, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(fr, t)
    if t >= END_IN: fr.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return fr.convert("RGB")
def capa(out):
    mp, c, s = draw_map(16.5); fr = Image.blend(Image.fromarray(OCEAN).convert("RGBA"), mp, 0.9)
    bsb = to_screen(P("BSB"), c, s); foz = to_screen(P("FOZ"), c, s)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dashed(ImageDraw.Draw(lay), path(bsb, foz, 1, 0.12), YEL + (255,), 10); fr.alpha_composite(lay)
    pin(fr, *bsb, "BRASÍLIA", NAVY, 1); pin(fr, *foz, "FOZ DO IGUAÇU", GREEN_BR, 1)
    put(fr, chipimg("FLÁVIO BOLSONARO", RED, 44), CX, 210); put(fr, txt("SAIU DO PAÍS", ANTON(130), WHITE, 7, NAVY), CX, 330); put(fr, txt("SEM PASSAPORTE?", ANTON(120), GOLD_L, 7, NAVY), CX, 480)
    put(fr, portrait(), CX + 230, 1250, 1, 0.8, 4); put(fr, stamp("NÃO CONFIRMADO", RED, 64, -8), CX - 150, 1300)
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
    ev = [(c[0] - 0.2, sfx.whoosh(0.5), 0.15) for c in CAM[1:]] + [(2.3, sfx.thud(0.4), 0.25), (27.7, sfx.thud(0.45), 0.3), (39.6, sfx.whoosh(0.7), 0.15), (END_IN - 0.3, sfx.whoosh(0.6), 0.2)]
    sfx.build(ev, TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=70,acompressor=threshold=0.1:ratio=2.2:attack=8:release=200:makeup=1.4,asplit=2[vox][k2];[2:a]volume=0.9[sf];[3:a]volume=1.0[sg];"
                    "[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][sgd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
def main():
    if MODE == "lib": return
    if MODE == "capa": capa(OUTFILE); return
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
