"""Terras raras no Brasil, 9:16: ranking de reservas, usos, mapa com GO/MG/BA e pinos, produção x China, sem refino,
venda da Serra Verde (US$ 2,8 bi), o que fazer (checklist) e opinião marcada. Narração do ElevenLabs, identidade do canal."""
import sys, math, subprocess, importlib.util, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("rex", f"{S}/work/render_exercito.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; eo = R.ease_out; ei = R.ease_in; eio = R.ease_io; bo = R.back_out
V = f"{S}/v82"; FD = f"{S}/fontdl"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
EDIT_END = 41.4; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = EDIT_END; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
GOLD = R.GOLD; GOLD_L = R.GOLD_L; NAVY = R.NAVY; WHITE = (255, 255, 255); RED = (226, 52, 52); GREEN_BR = (40, 150, 90); YEL = (255, 214, 64)
def ANTON(s): return ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s)
MF = R.MF
# ---------------------------------------------------------------- legenda (texto revisado à mão)
CAPTXT = [(0.09, 4.00, "O Brasil tem a segunda maior reserva de terras raras do mundo,"), (4.28, 5.51, "atrás só da China."),
          (6.04, 9.63, "São minerais usados em ímãs de carros elétricos e celulares."), (10.07, 12.65, "Estão em Goiás, Minas Gerais e Bahia."),
          (13.18, 18.27, "Mas o Brasil produz quase nada e não tem nenhuma usina para separar esses elementos."), (18.65, 20.10, "Vende o minério misturado."),
          (20.63, 22.95, "A única mina em operação, em Goiás,"), (23.26, 25.54, "teve a compra anunciada por uma empresa americana:"),
          (25.94, 28.49, "2,8 bilhões de dólares."), (29.05, 31.75, "Para gerar riqueza, o Brasil precisa refinar,"),
          (31.99, 34.63, "fabricar ímãs e controlar quem explora."), (35.16, 35.98, "Na minha opinião,"),
          (36.25, 39.24, "não dá para vender barato e comprar caro depois."), (39.64, 40.35, "Comenta aqui.")]
HOT = {"SEGUNDA", "TERRAS", "RARAS", "CHINA.", "ÍMÃS", "GOIÁS,", "MINAS", "GERAIS", "BAHIA.", "NADA", "NENHUMA", "USINA", "MISTURADO.", "ÚNICA", "AMERICANA:",
       "2,8", "BILHÕES", "REFINAR,", "FABRICAR", "CONTROLAR", "OPINIÃO,", "BARATO", "CARO", "AQUI."}
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
CARDS = [(0.6, 13.0, "USGS 2026", ["2ª MAIOR RESERVA", "DO MUNDO"]), (13.0, 29.0, "O PROBLEMA", ["NENHUMA USINA", "DE SEPARAÇÃO"]),
         (29.0, 35.1, "O QUE FAZER", ["REFINAR E", "FABRICAR AQUI"]), (35.1, EDIT_END, "OPINIÃO", ["A RIQUEZA TEM", "QUE FICAR AQUI"])]
CAP_Y, CARD_Y = 1430, 1712
# ---------------------------------------------------------------- mapa (países + estados)
GJ = json.load(open(f"{S}/v80/world.json")); BR = json.load(open(f"{S}/v76/br.json"))
SA = {"BRA", "ARG", "PRY", "URY", "BOL", "PER", "COL", "VEN", "GUY", "SUR", "CHL", "ECU", "FRA"}
LAT0 = math.cos(math.radians(-15))
def proj(lon, lat): return (lon * LAT0, -lat)
def rings_of(g, filt=None):
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]; out = []
    for p in polys:
        ring = [(x, y) for x, y in p[0]]
        if filt and not filt(ring): continue
        out.append(np.array([proj(x, y) for x, y in ring], np.float32))
    return out
SHAPES = {}
for f in GJ["features"]:
    if f["id"] not in SA: continue
    r = rings_of(f["geometry"], (lambda ring: all(-56 < x < -50 for x, _ in ring)) if f["id"] == "FRA" else None)
    if r: SHAPES[f["id"]] = r
UF = {f["properties"]["sigla"]: rings_of(f["geometry"]) for f in BR["features"]}
HL = {"GO": 10.1, "MG": 10.9, "BA": 11.7}   # quando cada estado acende
UFNAME = {"GO": ("GOIÁS", -49.6, -16.0), "MG": ("MINAS GERAIS", -44.6, -18.2), "BA": ("BAHIA", -41.6, -12.6)}
PTS = {"MIN": (-48.22, -13.53), "POC": (-46.56, -21.79), "ARX": (-46.94, -19.59), "ANG": (-42.9, -9.6)}
def P(k): return np.array(proj(*PTS[k]), np.float32)
CAM = [(0.0, -55, -15, 26), (9.6, -46.5, -15.5, 62), (20.2, -48.22, -13.53, 110), (28.8, -46.5, -15.5, 40)]
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
GOLDC = (232, 180, 60)
def draw_map(t):
    c, s = cam(t); img = OCEAN.copy(); SH = 3; F = 1 << SH
    def sc(rings): return [(((r - c) * s + (OX, OY)) * F).astype(np.int32) for r in rings]
    for iso, rings in SHAPES.items():
        if iso == "BRA": continue
        p = sc(rings); cv2.fillPoly(img, p, (58, 70, 94), cv2.LINE_AA, SH); cv2.polylines(img, p, True, (150, 165, 190), 2, cv2.LINE_AA, SH)
    for uf, rings in UF.items():
        p = sc(rings); col = np.array((36, 120, 76), np.float32)
        if uf in HL:
            k = clamp((t - HL[uf]) / 0.5) * (1 if uf == "GO" else 1 - clamp((t - 13.0) / 0.5)); pulse = 0.12 * math.sin((t - HL[uf]) * 5) if 0 < t - HL[uf] < 2.5 else 0
            col = col * (1 - k) + np.array(GOLDC, np.float32) * k * (1 + pulse)
        cv2.fillPoly(img, p, tuple(int(v) for v in np.clip(col, 0, 255)), cv2.LINE_AA, SH)
        cv2.polylines(img, p, True, (190, 220, 200), 1, cv2.LINE_AA, SH)
    p = sc(SHAPES["BRA"]); cv2.polylines(img, p, True, (235, 240, 250), 4, cv2.LINE_AA, SH)
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
def bars(fr, t, a, b, title, rows, unit, src, y0=430):
    """barras horizontais animadas: rows = [(rótulo, emoji, valor, cor)]"""
    k = env(t, a, b)
    if k <= 0: return
    put(fr, txt(title, ANTON(84), WHITE, 6, NAVY), CX, y0, k, 0.9 + 0.1 * bo((t - a) / 0.4))
    vmax = max(r[2] for r in rows); L = 560
    for i, (lab, em, v, col) in enumerate(rows):
        ti = a + 0.35 + i * 0.5; g = eo((t - ti) / 1.0); y = y0 + 170 + i * 190
        if t < ti: continue
        al = k * clamp((t - ti) / 0.25)
        put(fr, emoji(em, 74), 200, y, al); put(fr, txt(lab, MF("ExtraBold", 36), WHITE, 3), 330, y - 58, al)
        d = ImageDraw.Draw(fr); w = int(L * v / vmax * g)
        d.rounded_rectangle((260, y - 30, 260 + max(w, 30), y + 30), 30, fill=col + (int(255 * al),))
        put(fr, txt(f"{v * g:.0f} {unit}" if g < 1 else f"{v:g} {unit}".replace(".", ","), ANTON(54), WHITE, 5, NAVY), 260 + max(w, 30) + 130, y, al)
    put(fr, txt(src, MF("SemiBold", 26), (200, 210, 230), 3), CX, y0 + 170 + len(rows) * 190 - 40, k * clamp((t - a - 1.2) / 0.4))
def overlays(fr, t, c, s):
    d = ImageDraw.Draw(fr)
    # 0-5.8: reservas
    k = env(t, 0.05, 1.9)
    if k > 0: put(fr, txt("TERRAS", ANTON(170), WHITE, 8, NAVY), CX, 560, k, 0.8 + 0.2 * bo(t / 0.5)); put(fr, txt("RARAS", ANTON(200), GOLD_L, 8, NAVY), CX, 760, k, 0.8 + 0.2 * bo((t - 0.15) / 0.5))
    bars(fr, t, 1.9, 5.85, "RESERVAS", [("CHINA", "🇨🇳", 44, RED), ("BRASIL", "🇧🇷", 21, GREEN_BR)], "mi t", "USGS 2026 · as estimativas variam")
    if 4.2 < t < 5.85: put(fr, chipimg("2º LUGAR NO MUNDO", GOLD, 40, NAVY), CX, 1080, env(t, 4.2, 5.85), 0.8 + 0.2 * bo((t - 4.2) / 0.3))
    # 5.9-9.9: usos
    k = env(t, 5.9, 9.95)
    if k > 0:
        put(fr, emoji("🧲", 230), CX, 560, k, 0.6 + 0.4 * bo((t - 5.9) / 0.45), 8 * math.sin(t * 3))
        put(fr, chipimg("ÍMÃS SUPERFORTES", GOLD, 40, NAVY), CX, 760, k * clamp((t - 6.6) / 0.3))
        for i, (em, lab, ti) in enumerate([("🚗", "CARRO ELÉTRICO", 7.6), ("📱", "CELULAR", 8.6), ("🌬️", "ENERGIA EÓLICA", 9.0)]):
            if t < ti: continue
            x = CX + (i - 1) * 300; kk = k * clamp((t - ti) / 0.25)
            put(fr, emoji(em, 130), x, 960, kk, 0.6 + 0.4 * bo((t - ti) / 0.35)); put(fr, txt(lab, MF("ExtraBold", 28), WHITE, 3), x, 1060, kk)
    # 10-13: mapa com estados e pinos
    mi, po, ar, an = (to_screen(P(k_), c, s) for k_ in ("MIN", "POC", "ARX", "ANG"))
    if 9.9 <= t < 13.1:
        for uf, (nm, lo, la) in UFNAME.items():
            x, y = to_screen(np.array(proj(lo, la)), c, s); put(fr, txt(nm, ANTON(46), WHITE, 5, NAVY), x, y, env(t, HL[uf] + 0.2, 13.1))
        pin(fr, *mi, "MINAÇU", RED, env(t, 10.3, 13.1), dy=-50)
        pin(fr, *ar, "ARAXÁ", RED, env(t, 11.0, 13.1), dy=-50)
        pin(fr, *po, "POÇOS DE CALDAS", RED, env(t, 11.2, 13.1), dy=54)
        pin(fr, *an, "ANGICO DOS DIAS", RED, env(t, 11.8, 13.1), dy=-50)
        if t > 10.6:
            kk = env(t, 10.6, 13.1); put(fr, chipimg("LEVES: NEODÍMIO", (60, 120, 200), 30), CX - 190, 1290, kk); put(fr, chipimg("PESADAS: DISPRÓSIO", (150, 80, 170), 30), CX + 200, 1290, kk)
    # 13.2-20.4: produção e refino
    if 13.15 <= t < 20.5:
        bars(fr, t, 13.15, 20.45, "PRODUÇÃO 2025", [("CHINA", "🇨🇳", 270, RED), ("BRASIL", "🇧🇷", 2, GREEN_BR)], "mil t", "USGS 2026", y0=380)
        if t > 15.6: put(fr, stamp("NENHUMA USINA DE SEPARAÇÃO", RED, 50, -7), CX, 1000, env(t, 15.6, 20.45), 0.7 + 0.3 * bo(clamp((t - 15.6) / 0.25), 2.0))
        if t > 18.6:
            kk = env(t, 18.6, 20.45); put(fr, emoji("⛏️", 100), CX - 260, 1160, kk); put(fr, emoji("🚢", 110), CX + 260, 1160, kk)
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay); g = eo((t - 18.8) / 0.8)
            dashed(dl, [(CX - 180, 1160), (CX - 180 + 360 * g, 1160)], YEL + (int(255 * kk),), 8); fr.alpha_composite(lay)
            put(fr, txt("MINÉRIO MISTURADO", MF("ExtraBold", 30), YEL, 3), CX, 1225, kk)
    # 20.5-28.8: mina de Goiás e o dinheiro
    if 20.5 <= t < 28.8:
        pin(fr, *mi, "MINAÇU (GO)", RED, env(t, 20.7, 28.8), sub="Serra Verde")
        if t > 21.2: put(fr, chipimg("ÚNICA MINA EM OPERAÇÃO", NAVY, 36), CX, 380, env(t, 21.2, 28.8))
        if t > 23.3:
            kk = env(t, 23.3, 28.8); put(fr, emoji("🇺🇸", 120), CX, 980, kk, 0.6 + 0.4 * bo((t - 23.3) / 0.35)); put(fr, chipimg("EMPRESA AMERICANA", (60, 90, 160), 34), CX, 1090, kk)
        if t > 25.9:
            kk = env(t, 25.9, 28.8); g = eo((t - 25.9) / 1.0); v = 2.8 * g
            put(fr, txt(f"US$ {v:.1f} BI".replace(".", ","), ANTON(150), GOLD_L, 8, NAVY), CX, 490, kk, 0.85 + 0.15 * bo((t - 25.9) / 0.35))
            put(fr, txt("compra anunciada em 2026", MF("SemiBold", 30), WHITE, 3), CX, 610, kk * clamp((t - 26.4) / 0.3))
            put(fr, chipimg("+ US$ 750 MI DO GOVERNO DOS EUA", (40, 40, 50), 28, YEL), CX, 1190, env(t, 26.8, 28.8))
    # 29-35.1: checklist
    k = env(t, 29.0, 35.1)
    if k > 0:
        put(fr, txt("O QUE O BRASIL", ANTON(96), WHITE, 6, NAVY), CX, 380, k); put(fr, txt("PRECISA FAZER", ANTON(96), GOLD_L, 6, NAVY), CX, 490, k)
        for i, (lab, ti) in enumerate([("REFINAR AQUI", 30.9), ("FABRICAR ÍMÃS", 32.3), ("CONTROLAR QUEM EXPLORA", 33.4)]):
            if t < ti - 0.3: continue
            y = 660 + i * 140; kk = k * clamp((t - ti + 0.3) / 0.3)
            d = ImageDraw.Draw(fr); d.rounded_rectangle((140, y - 52, W - 140, y + 52), 26, fill=(10, 26, 56, int(220 * kk)), outline=GOLD + (int(255 * kk),), width=3)
            if t >= ti: put(fr, emoji("✅", 70), 210, y, kk, 0.5 + 0.5 * bo((t - ti) / 0.3))
            put(fr, txt(lab, MF("ExtraBold", 42), WHITE, 2), CX + 40, y, kk)
        if t > 33.9: put(fr, chipimg("LEI 15.506/2026 · ATÉ R$ 7 BI EM INCENTIVOS", (40, 40, 50), 26, YEL), CX, 1100, env(t, 33.9, 35.1))
    # 35.2-39.5: opinião
    k = env(t, 35.2, 39.55)
    if k > 0:
        put(fr, chipimg("NA MINHA OPINIÃO", (30, 30, 40), 36, GOLD_L), CX, 380, k)
        for i, (lab, em, ti) in enumerate([("VENDER BARATO", "📉", 36.3), ("COMPRAR CARO", "📈", 37.6)]):
            if t < ti: continue
            kk = k * clamp((t - ti) / 0.25); y = 600 + i * 260
            put(fr, emoji(em, 110), CX - 330, y, kk); put(fr, txt(lab, ANTON(96), WHITE, 6, NAVY), CX + 60, y, kk, 0.8 + 0.2 * bo((t - ti) / 0.3))
            if t > ti + 0.5: put(fr, emoji("❌", 90), CX + 400, y, kk, 0.5 + 0.5 * bo((t - ti - 0.5) / 0.3))
    # 39.6-fim: pergunta
    k = env(t, 39.6, EDIT_END + 0.4, 0.3, 0.3)
    if k > 0:
        put(fr, txt("O BRASIL VAI", ANTON(130), WHITE, 7, NAVY), CX, 520, k, 0.9 + 0.1 * bo((t - 39.6) / 0.4)); put(fr, txt("CONSEGUIR?", ANTON(140), GOLD_L, 7, NAVY), CX, 680, k)
        put(fr, chipimg("COMENTA AQUI", RED, 46), CX, 880, k, 1 + 0.04 * math.sin(t * 6))
    if 0.5 < t < EDIT_END: R.credit(fr, "Fontes: USGS, SGB, CGEE, CNN Brasil, Agência Câmara", W - 30, 168, clamp((t - 0.5) / 0.4))
def map_alpha(t):
    """mapa forte no trecho dos estados e da mina; no resto fica apagado atrás dos cartões"""
    on = lambda a, b: clamp((t - a) / 0.5) * (1 - clamp((t - b) / 0.5))
    return 0.22 + 0.73 * max(on(9.7, 13.0), on(20.3, 28.6))
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); mp, c, s = draw_map(tt); a = map_alpha(tt)
    fr = Image.blend(Image.fromarray(OCEAN).convert("RGBA"), mp, a)
    if a < 0.5:   # escurece um pouco mais atrás dos textos
        fr.alpha_composite(Image.new("RGBA", (W, H), (4, 12, 26, int(90 * (1 - a)))))
    overlays(fr, tt, c, s)
    g = np.zeros((520, W, 4), np.uint8); g[..., :3] = (3, 10, 22); g[..., 3] = np.linspace(0, 210, 520)[:, None].astype(np.uint8); fr.alpha_composite(Image.fromarray(g), (0, H - 520))
    M.caption(fr, tt, CAP_Y, 54)
    for a_, b_, kick, lines in CARDS:
        kc = clamp((tt - a_) / 0.4) * (1 - clamp((tt - (b_ - 0.3)) / 0.3))
        if kc > 0: BAR.lower_card(fr, kick, lines, CARD_Y, kc, fs=40)
    cta = clamp((t - 39.6) / 0.4) if t > 39.6 else 0.0
    BAR.draw_bar(fr, clamp(t / END_IN), "canal", eo((t - 0.2) / 0.6), cta, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(fr, t)
    if t >= END_IN: fr.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return fr.convert("RGB")
def capa(out):
    global OY
    OY0 = OY; OY = OY0 + 330; mp, c, s = draw_map(12.6); fr = Image.blend(Image.fromarray(OCEAN).convert("RGBA"), mp, 0.95)
    for k_, lab, dy in (("MIN", "MINAÇU", -50), ("ARX", "ARAXÁ", -50), ("POC", "POÇOS DE CALDAS", 54), ("ANG", "ANGICO DOS DIAS", -50)):
        pin(fr, *to_screen(P(k_), c, s), lab, RED, 1, dy=dy)
    OY = OY0
    g = np.zeros((560, W, 4), np.uint8); g[..., :3] = (4, 12, 26); g[..., 3] = np.linspace(230, 0, 560)[:, None].astype(np.uint8); fr.alpha_composite(Image.fromarray(g), (0, 100))
    put(fr, chipimg("O TESOURO DO BRASIL", RED, 44), CX, 230); put(fr, txt("TERRAS RARAS", ANTON(150), GOLD_L, 8, NAVY), CX, 380)
    put(fr, txt("ONDE ESTÃO E QUANTO VALEM", ANTON(70), WHITE, 6, NAVY), CX, 520); put(fr, emoji("💰", 150), CX + 340, 1650); put(fr, emoji("🧲", 150), CX - 340, 1650)
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
    def coin(seed=1):
        rng = np.random.default_rng(seed); tt = np.arange(int(0.35 * SR)) / SR; y = np.zeros_like(tt)
        for f0, g in ((2093, 1.0), (2637, 0.7), (3136, 0.5)): y += g * np.sin(2 * np.pi * f0 * tt) * np.exp(-tt / 0.09)
        y /= np.abs(y).max(); return np.stack([y, y], 1)
    def pop():
        tt = np.arange(int(0.12 * SR)) / SR; y = np.sin(2 * np.pi * (500 + 900 * tt / 0.12) * tt) * np.exp(-tt / 0.03); return np.stack([y, y], 1)
    ev = [(a - 0.15, sfx.whoosh(0.5), 0.15) for a in (1.9, 5.9, 9.8, 13.15, 20.4, 29.0, 35.1, 39.6)]
    ev += [(x, pop(), 0.35) for x in (2.25, 2.75, 7.6, 8.6, 9.0, 10.3, 11.0, 11.2, 11.8, 13.5, 14.0, 20.7, 23.3)]
    ev += [(15.6, sfx.thud(0.45), 0.3), (4.2, coin(2), 0.25)] + [(25.9 + i * 0.12, coin(i), 0.22) for i in range(6)] + [(26.8, coin(9), 0.2)]
    ev += [(x, sfx.click(), 0.4) for x in (30.9, 32.3, 33.4)] + [(36.8, sfx.thud(0.35), 0.2), (38.1, sfx.thud(0.35), 0.2), (END_IN - 0.3, sfx.whoosh(0.6), 0.2)]
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
