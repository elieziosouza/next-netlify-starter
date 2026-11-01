"""Motion do mapa do Brasil, região por região (2º turno 2026): estados acendem em vermelho (Lula) e azul (Flávio), câmera vai de região
em região, barras de votos, destaques nos estados principais, balança final (9,3 mi x 13,7 mi) e, na opinião, o mapa vira uma cor só
("não existe brasileiro de primeira e de segunda"). Narração do ElevenLabs. Números checados (Bloomberg Línea, Exame, Gazeta do Povo).
Legenda karaokê, caixa fixa e barra lateral do canal. Usa os ajudantes do render_exercito."""
import sys, math, subprocess, importlib.util, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("rex", f"{S}/work/render_exercito.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; eo = R.ease_out; ei = R.ease_in; eio = R.ease_io; bo = R.back_out
V = f"{S}/v76"; FD = f"{S}/fontdl"
EDIT_END = 112.25; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = EDIT_END; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
LULA = (214, 36, 44); FLAV = (36, 104, 226); GRAY = (52, 70, 96); GOLD = R.GOLD; GOLD_L = R.GOLD_L; NAVY = R.NAVY; WHITE = (255, 255, 255)
def ANTON(s): return ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s)
MF = R.MF

# ---------------------------------------------------------------- legenda (texto revisado à mão)
CAPTXT = [(0.18, 3.15, "4,4 milhões de votos separaram Lula e Flávio,"), (3.38, 5.70, "mas cada região do Brasil contou uma história diferente."),
          (6.03, 6.96, "Vamos ver uma por uma."), (7.88, 8.47, "Nordeste."), (9.08, 10.77, "Aqui foi onde o Lula ganhou a eleição."),
          (11.05, 12.07, "Venceu nos nove estados:"), (12.52, 16.81, "24,5 milhões de votos, contra 10,8 milhões do Flávio."),
          (17.25, 19.31, "Uma vantagem de quase 14 milhões."), (19.80, 22.71, "No Piauí, Lula passou de 75%."),
          (23.09, 26.95, "Na Bahia, maior estado da região, passou de 70%."), (27.60, 28.30, "Sudeste."),
          (28.53, 30.22, "O maior colégio eleitoral do país."), (30.81, 37.31, "Flávio venceu em São Paulo, no Rio e no Espírito Santo, com 2,8 milhões de votos de vantagem na região."),
          (37.65, 40.83, "Em São Paulo, Flávio teve perto de 54%."), (41.27, 42.66, "Mas Minas Gerais foi do Lula,"), (42.93, 43.54, "por um fio:"),
          (43.86, 48.20, "50,43 contra 49,57."), (48.45, 48.90, "Sul."), (49.47, 51.06, "Aqui foi onde o Flávio foi mais forte."),
          (51.35, 55.43, "Venceu nos três estados, com 4,6 milhões de votos de vantagem."), (55.72, 57.91, "Em Santa Catarina, quase 70%."),
          (58.34, 60.73, "No Paraná, mais de 62%."), (61.12, 61.79, "Centro-Oeste."), (62.08, 64.73, "Flávio venceu nos três estados e no Distrito Federal,"),
          (65.16, 67.79, "com 1,9 milhão de votos de vantagem."), (68.17, 70.91, "E o Norte foi o empate mais impressionante da eleição."),
          (71.26, 74.00, "Lula ganhou no Pará, no Amazonas e no Amapá."), (74.46, 77.73, "Flávio ganhou em Roraima, Rondônia, Acre e Tocantins."),
          (78.20, 78.94, "Somando tudo,"), (79.27, 82.08, "Lula terminou com 1.079 votos a mais."), (82.73, 83.75, "1.079,"), (84.25, 85.36, "numa região inteira."),
          (85.74, 90.10, "Na conta final, Flávio abriu 9,3 milhões de vantagem fora do Nordeste."), (90.26, 92.77, "Lula abriu 13,7 milhões só no Nordeste."),
          (93.52, 95.17, "Daí os 4,4 milhões."), (95.60, 96.83, "Agora, na minha opinião:"), (97.05, 99.24, "não existe brasileiro de primeira e de segunda."),
          (99.53, 102.87, "O voto do nordestino e o do catarinense valem a mesma coisa."), (103.15, 104.59, "O problema não é votar diferente."),
          (104.88, 106.44, "É deixar de conversar por causa disso."), (106.76, 108.01, "E aí, como foi na sua cidade?"),
          (108.36, 110.72, "Você tem alguém na família que votou diferente de você?"), (111.16, 111.80, "Comenta aqui.")]
HOT = {"4,4", "NORDESTE.", "ELEIÇÃO.", "NOVE", "24,5", "14", "75%.", "70%.", "SUDESTE.", "2,8", "54%.", "MINAS", "FIO:", "SUL.", "FORTE.", "4,6",
       "70%.", "62%.", "CENTRO-OESTE.", "1,9", "NORTE", "EMPATE", "1.079", "1.079,", "9,3", "13,7", "OPINIÃO:", "MESMA", "CONVERSAR", "CIDADE?", "AQUI."}
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
CARD = ("ELEIÇÕES 2026", ["O BRASIL", "REGIÃO POR REGIÃO"])
CAP_Y, CARD_Y = 1500, 1712

# ---------------------------------------------------------------- mapa
GJ = json.load(open(f"{V}/br.json"))
REG = {"NE": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"], "SE": ["SP", "RJ", "ES", "MG"], "S": ["PR", "SC", "RS"],
       "CO": ["GO", "MT", "MS", "DF"], "N": ["PA", "AM", "AP", "RR", "RO", "AC", "TO"]}
REG_OF = {uf: r for r, l in REG.items() for uf in l}
WIN = {uf: (LULA if uf in ("AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE", "MG", "PA", "AM", "AP") else FLAV) for uf in REG_OF}
LAT0 = math.cos(math.radians(15))
def proj(lon, lat): return ((lon + 54) * LAT0, -(lat + 15))
STATES = {}
for f in GJ["features"]:
    uf = f["properties"]["sigla"]; g = f["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    rings = []
    for p in polys:
        ring = np.array([proj(x, y) for x, y in p[0]], np.float32)
        if len(ring) > 30:
            ap = cv2.approxPolyDP(ring.reshape(-1, 1, 2), 0.012, True).reshape(-1, 2)
            ring = ap if len(ap) >= 3 else ring
        if len(ring) >= 3: rings.append(ring)
    allp = np.concatenate(rings); area = [abs(cv2.contourArea(r)) for r in rings]; big = rings[int(np.argmax(area))]
    m = cv2.moments(big.reshape(-1, 1, 2)); c = (m["m10"] / m["m00"], m["m01"] / m["m00"]) if m["m00"] else tuple(allp.mean(0))
    STATES[uf] = dict(rings=rings, c=np.array(c, np.float32), bb=(allp[:, 0].min(), allp[:, 1].min(), allp[:, 0].max(), allp[:, 1].max()))
ALLBB = (min(s["bb"][0] for s in STATES.values()), min(s["bb"][1] for s in STATES.values()), max(s["bb"][2] for s in STATES.values()), max(s["bb"][3] for s in STATES.values()))
def bb_of(ufs):
    b = [STATES[u]["bb"] for u in ufs]; return (min(x[0] for x in b), min(x[1] for x in b), max(x[2] for x in b), max(x[3] for x in b))
BOX = (150, 360, 1030, 1140)                                          # área do mapa na tela
def cam_for(bb, fill=1.0):
    bw, bh = bb[2] - bb[0], bb[3] - bb[1]; sc = min((BOX[2] - BOX[0]) / bw, (BOX[3] - BOX[1]) / bh) * fill
    return ((bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2, sc)
FULL = cam_for(ALLBB, 0.98)
# cenas da câmera: (início, alvo)
SC = [(0.0, FULL), (7.6, cam_for(bb_of(REG["NE"]), 0.92)), (27.3, cam_for(bb_of(REG["SE"]), 0.86)), (48.3, cam_for(bb_of(REG["S"]), 0.8)),
      (60.9, cam_for(bb_of(REG["CO"]), 0.88)), (67.95, cam_for(bb_of(REG["N"]), 0.95)), (85.5, cam_for(ALLBB, 0.9)), (95.4, FULL)]
def camera(t):
    i = max(k for k, s in enumerate(SC) if s[0] <= t); t0, c1 = SC[i]
    if i == 0: c0 = FULL
    else: c0 = SC[i - 1][1]
    k = eio((t - t0) / 0.9); return tuple(a + (b - a) * k for a, b in zip(c0, c1))
FOCUS = [(7.6, 27.3, "NE"), (27.3, 48.3, "SE"), (48.3, 60.9, "S"), (60.9, 67.95, "CO"), (67.95, 85.5, "N")]
def focus_k(uf, t):
    """1 = estado em destaque, 0 = apagado"""
    for a, b, r in FOCUS:
        if a <= t < b + 0.5:
            fin = clamp((t - a) / 0.5); fout = clamp((t - b) / 0.5); inside = REG_OF[uf] == r
            return 1.0 if inside else 1 - 0.68 * fin * (1 - fout)
    if 85.5 <= t < 93.4:                                               # balança: fora do Nordeste, depois o Nordeste
        ne = REG_OF[uf] == "NE"; a1 = clamp((t - 85.7) / 0.4) * (1 - clamp((t - 90.1) / 0.4)); a2 = clamp((t - 90.2) / 0.4) * (1 - clamp((t - 93.3) / 0.4))
        return 1 - 0.68 * (a1 * ne + a2 * (not ne))
    return 1.0
# quando cada estado acende (introdução: oeste→leste; depois região por região)
INTRO = {uf: 0.7 + 2.0 * (s["c"][0] - ALLBB[0]) / (ALLBB[2] - ALLBB[0]) for uf, s in STATES.items()}
REVEAL = {}
def stagger(ufs, t0, dt=0.12):
    for i, u in enumerate(ufs): REVEAL[u] = t0 + i * dt
stagger(["MA", "PI", "CE", "RN", "PB", "PE", "AL", "SE", "BA"], 11.05)
stagger(["SP", "RJ", "ES"], 30.9, 0.25); REVEAL["MG"] = 41.3
stagger(["PR", "SC", "RS"], 51.4, 0.2)
stagger(["GO", "MT", "MS", "DF"], 62.1, 0.18)
stagger(["PA", "AM", "AP"], 71.3, 0.45); stagger(["RR", "RO", "AC", "TO"], 74.5, 0.4)
def lerpc(a, b, k): return tuple(int(x + (y - x) * k) for x, y in zip(a, b))
def state_style(uf, t):
    """cor e escala do estado"""
    win = WIN[uf]
    if t < 7.6:
        p = clamp((t - INTRO[uf]) / 0.35); q = clamp((t - 7.0) / 0.5); col = lerpc(GRAY, win, p * (1 - q)); pop = p if q == 0 else 1.0
    else:
        p = clamp((t - REVEAL[uf]) / 0.35); col = lerpc(GRAY, win, p); pop = p
    u = clamp((t - 97.1) / 0.9) * (1 - clamp((t - 103.2) / 0.7)); col = lerpc(col, GOLD, u)
    fk = focus_k(uf, t); col = lerpc((14, 26, 44), col, fk)
    sc = 0.82 + 0.18 * bo(pop, 2.2) if 0 < pop < 1 else 1.0
    return col, sc, fk
def hl_k(uf, t):
    for a, b, u in HL:
        if u == uf and a <= t < b: return clamp((t - a) / 0.3) * clamp((b - t) / 0.3)
    return 0.0
HL = [(19.8, 23.0, "PI"), (23.1, 27.2, "BA"), (37.6, 41.2, "SP"), (41.3, 48.3, "MG"), (55.7, 58.3, "SC"), (58.35, 60.9, "PR"), (79.3, 85.4, "PA")]
yy_, xx_ = np.mgrid[0:H, 0:W].astype(np.float32)
_r = np.sqrt(((xx_ - W * 0.55) / W) ** 2 + ((yy_ - H * 0.4) / H) ** 2)
BG = (np.array([3, 10, 22], np.float32) + np.array([10, 34, 64], np.float32) * np.clip(1 - _r * 1.7, 0, 1)[..., None])
for g in range(0, W, 60): BG[:, g:g + 1] += 7
for g in range(0, H, 60): BG[g:g + 1, :] += 7
BG = np.clip(BG, 0, 255).astype(np.uint8); del yy_, xx_, _r
def draw_map(t):
    cx, cy, sc = camera(t); ox, oy = (BOX[0] + BOX[2]) / 2, (BOX[1] + BOX[3]) / 2 + 6 * math.sin(t * 0.6)
    img = BG.copy(); glow = np.zeros((H // 4, W // 4, 3), np.uint8); SH = 3; F = 1 << SH; scr = {}
    order = sorted(STATES, key=lambda u: hl_k(u, t))
    for uf in order:
        st = STATES[uf]; col, k, fk = state_style(uf, t); h = hl_k(uf, t); k *= 1 + 0.05 * h
        c = st["c"]; polys = []
        for ring in st["rings"]:
            p = (c + (ring - c) * k - (cx, cy)) * sc + (ox, oy); polys.append((p * F).astype(np.int32))
        scr[uf] = ((c[0] - cx) * sc + ox, (c[1] - cy) * sc + oy)
        if h > 0:
            sh = [((pp // F + np.array([6, 10])) * F).astype(np.int32) for pp in polys]
            cv2.fillPoly(img, sh, (0, 0, 0), cv2.LINE_AA, SH)
        cv2.fillPoly(img, polys, col, cv2.LINE_AA, SH)
        cv2.polylines(img, polys, True, lerpc((14, 26, 44), (235, 240, 250), 0.25 + 0.6 * fk) if h == 0 else GOLD_L, 2 if h == 0 else 5, cv2.LINE_AA, SH)
        if fk > 0.9 and col != GRAY:
            cv2.fillPoly(glow, [(pp // 4) for pp in polys], tuple(int(v * 0.55) for v in col), cv2.LINE_AA, SH)
    gl = cv2.resize(cv2.GaussianBlur(glow, (0, 0), 9), (W, H), interpolation=cv2.INTER_LINEAR)
    img = cv2.add(img, (gl * 0.6).astype(np.uint8))
    return img, scr, sc
# ---------------------------------------------------------------- textos e painéis
_tx = {}
def text_img(txt, font, col, stroke=0, scol=(0, 0, 0)):
    key = (txt, font.path, font.size, col, stroke)
    if key not in _tx:
        bb = font.getbbox(txt); im = Image.new("RGBA", (bb[2] - bb[0] + 16 + 2 * stroke, bb[3] - bb[1] + 16 + 2 * stroke), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((8 - bb[0] + stroke, 8 - bb[1] + stroke), txt, font=font, fill=col + (255,), stroke_width=stroke, stroke_fill=scol + (255,)); _tx[key] = im
    return _tx[key]
def put(fr, im, cx, cy, sc=1.0, al=1.0):
    if al <= 0.01: return
    if abs(sc - 1) > 0.004: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
    fr.alpha_composite(R.fade(im, al), (int(cx - im.width / 2), int(cy - im.height / 2)))
def env(t, a, b, fi=0.3, fo=0.25): return clamp((t - a) / fi) * clamp((b - t) / fo)
TITLES = [(0.2, 7.5, "O BRASIL DIVIDIDO", "2º TURNO · 25/10"), (7.8, 27.3, "NORDESTE", "9 ESTADOS"), (27.6, 48.3, "SUDESTE", "4 ESTADOS"), (48.45, 60.9, "SUL", "3 ESTADOS"),
          (61.1, 67.95, "CENTRO-OESTE", "3 ESTADOS + DF"), (68.15, 85.5, "NORTE", "7 ESTADOS"), (85.7, 95.4, "A CONTA FINAL", "VANTAGEM DE CADA UM"), (95.6, 112.3, "NA MINHA OPINIÃO", None)]
def draw_title(fr, t):
    for a, b, big, kick in TITLES:
        k = env(t, a, b)
        if k <= 0: continue
        u = t - a; f = ANTON(110 if len(big) < 12 else 92); im = text_img(big, f, WHITE)
        put(fr, im, CX, 262 + 30 * (1 - eo(u / 0.35)), 0.9 + 0.1 * bo(u / 0.4), k)
        lw = int(220 * eo((u - 0.15) / 0.5)); d = ImageDraw.Draw(fr)
        if lw > 0: d.rectangle((CX - lw, 330, CX + lw, 335), fill=GOLD + (int(255 * k),))
        if kick: R.pill(fr, kick, CX, 372, clamp((u - 0.3) / 0.3) * k, fill=NAVY, size=26)
def vs_bar(fr, t, a, b, y, lv, rv, frac, ltxt="LULA", rtxt="FLÁVIO", title=None):
    k = env(t, a, b)
    if k <= 0: return
    u = t - a; x0, x1 = 170, 1000; w = x1 - x0; g = eo((u - 0.15) / 0.9); fx = x0 + w * (0.5 + (frac - 0.5) * g)
    lay = Image.new("RGBA", (W, 240), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if title: d.text((CX, 22), title, font=MF("Bold", 30), fill=GOLD_L + (255,), anchor="mm")
    d.rounded_rectangle((x0, 60, x1, 128), 34, fill=(10, 20, 36, 230))
    d.rounded_rectangle((x0, 60, int(fx), 128), 34, fill=LULA + (255,)); d.rounded_rectangle((int(fx), 60, x1, 128), 34, fill=FLAV + (255,))
    d.rectangle((int(fx) - 2, 52, int(fx) + 2, 136), fill=WHITE + (255,))
    d.text((x0 + 26, 94), ltxt, font=MF("ExtraBold", 30), fill=WHITE + (255,), anchor="lm"); d.text((x1 - 26, 94), rtxt, font=MF("ExtraBold", 30), fill=WHITE + (255,), anchor="rm")
    d.text((x0 + 6, 176), lv, font=ANTON(64), fill=(255, 120, 120, 255), anchor="lm"); d.text((x1 - 6, 176), rv, font=ANTON(64), fill=(140, 180, 255, 255), anchor="rm")
    fr.alpha_composite(R.fade(lay, k), (0, int(y + 30 * (1 - eo(u / 0.4)))))
def big_num(fr, t, a, b, y, txt, sub=None, col=WHITE, size=150):
    k = env(t, a, b)
    if k <= 0: return
    u = t - a; put(fr, text_img(txt, ANTON(size), col, 4, (0, 0, 0)), CX, y, 0.7 + 0.3 * bo(u / 0.35, 2.0), k)
    if sub: put(fr, text_img(sub, MF("ExtraBold", 34), GOLD_L), CX, y + size * 0.62, 1.0, k * clamp((u - 0.25) / 0.3))
def counter(t, a, dur, v0, v1):
    x = eo(clamp((t - a) / dur)); return v0 + (v1 - v0) * x
def adv_chip(fr, t, a, b, y, who, txt):
    k = env(t, a, b)
    if k <= 0: return
    col = LULA if who == "L" else FLAV; u = t - a
    R.pill(fr, txt, CX, y, clamp(u / 0.3) * k, fill=col, size=44)
CALL = [(19.8, 23.0, "PI", "PIAUÍ", "75,88% LULA", LULA, (900, 470)), (23.1, 27.2, "BA", "BAHIA", "+70% LULA", LULA, (930, 1070)),
        (37.6, 41.2, "SP", "SÃO PAULO", "53,85% FLÁVIO", FLAV, (870, 1080)), (55.7, 58.3, "SC", "SANTA CATARINA", "69,42% FLÁVIO", FLAV, (870, 600)),
        (58.35, 60.9, "PR", "PARANÁ", "62,58% FLÁVIO", FLAV, (880, 470)), (41.3, 48.3, "MG", "MINAS GERAIS", "POR UM FIO", LULA, (360, 470))]
def callout(fr, t, scr):
    d = ImageDraw.Draw(fr)
    for a, b, uf, name, val, col, (lx, ly) in CALL:
        k = env(t, a, b)
        if k <= 0: continue
        sx, sy = scr[uf]; u = t - a; g = eo(u / 0.4); ex, ey = sx + (lx - sx) * g, sy + (ly - sy) * g
        d.line((sx, sy, ex, ey), fill=WHITE + (int(230 * k),), width=4); d.ellipse((sx - 10, sy - 10, sx + 10, sy + 10), fill=WHITE + (int(255 * k),))
        f1, f2 = MF("ExtraBold", 26), ANTON(54); w = int(max(f1.getlength(name), f2.getlength(val)) + 50); h = 120
        box = Image.new("RGBA", (w, h), (0, 0, 0, 0)); bd = ImageDraw.Draw(box)
        bd.rounded_rectangle((0, 0, w - 1, h - 1), 18, fill=col + (255,), outline=WHITE + (255,), width=3)
        bd.text((w / 2, 32), name, font=f1, fill=WHITE + (255,), anchor="mm"); bd.text((w / 2, 80), val, font=f2, fill=WHITE + (255,), anchor="mm")
        bx = min(max(ex, 140 + w / 2), 1060 - w / 2); put(fr, box, bx, ey, 0.6 + 0.4 * bo(clamp((u - 0.25) / 0.35), 2.0), k * clamp((u - 0.2) / 0.15))
def labels(fr, t, scr, sc):
    """siglas dos estados da região em foco"""
    for a, b, r in FOCUS:
        k = env(t, a + 0.9, b, 0.4, 0.3)
        if k <= 0: continue
        for uf in REG[r]:
            if t < REVEAL[uf]: continue
            x, y = scr[uf]; f = MF("ExtraBold", 30 if uf != "DF" else 22)
            if uf in ("SE", "AL", "PB", "RN", "DF", "ES", "RJ") and sc < 45: continue
            put(fr, text_img(uf, f, WHITE, 3, (0, 0, 0)), x, y, 1.0, k * clamp((t - REVEAL[uf] - 0.2) / 0.3))
PANEL_Y = 1170
def panels(fr, t):
    v = counter(t, 0.3, 2.4, 0, 4_400_000); big_num(fr, t, 0.2, 3.3, PANEL_Y + 90, f"{v:,.0f}".replace(",", "."), "VOTOS DE DIFERENÇA", GOLD_L, 130)
    vs_bar(fr, t, 3.4, 7.4, PANEL_Y, "51,79%", "48,21%", 0.5179, title="BRASIL · VOTOS VÁLIDOS")
    adv_chip(fr, t, 3.4, 7.4, 470, "L", "LULA 13 ESTADOS") if t < 5.4 else adv_chip(fr, t, 5.4, 7.4, 470, "F", "FLÁVIO 13 + DF")
    # Nordeste
    vs_bar(fr, t, 12.5, 19.6, PANEL_Y, "24,5 mi", "10,8 mi", 24.5 / 35.3, title="NORDESTE · VOTOS")
    adv_chip(fr, t, 17.2, 19.6, 465, "L", "≈14 MILHÕES DE VANTAGEM")
    vs_bar(fr, t, 19.8, 27.3, PANEL_Y, "9", "0", 1.0, "ESTADOS LULA", "FLÁVIO", title="ESTADOS VENCIDOS")
    # Sudeste
    adv_chip(fr, t, 28.5, 30.7, 465, "F", "MAIOR COLÉGIO ELEITORAL")
    vs_bar(fr, t, 31.0, 37.5, PANEL_Y, "1 estado", "3 estados", 0.25, title="SUDESTE · ESTADOS")
    adv_chip(fr, t, 33.5, 37.5, 465, "F", "FLÁVIO +2,8 MILHÕES")
    vs_bar(fr, t, 37.6, 41.2, PANEL_Y, "46,15%", "53,85%", 0.4615, title="SÃO PAULO")
    vs_bar(fr, t, 43.8, 48.3, PANEL_Y, "50,43%", "49,57%", 0.5043, title="MINAS GERAIS")
    # Sul
    vs_bar(fr, t, 51.4, 55.6, PANEL_Y, "0", "3", 0.0, "LULA", "ESTADOS FLÁVIO", title="SUL · ESTADOS")
    adv_chip(fr, t, 53.0, 55.6, 465, "F", "FLÁVIO +4,6 MILHÕES")
    vs_bar(fr, t, 55.7, 58.3, PANEL_Y, "30,58%", "69,42%", 0.3058, title="SANTA CATARINA")
    vs_bar(fr, t, 58.35, 60.9, PANEL_Y, "37,42%", "62,58%", 0.3742, title="PARANÁ")
    # Centro-Oeste
    vs_bar(fr, t, 62.1, 67.95, PANEL_Y, "0", "3 + DF", 0.0, "LULA", "FLÁVIO", title="CENTRO-OESTE · ESTADOS")
    adv_chip(fr, t, 65.1, 67.95, 465, "F", "FLÁVIO +1,9 MILHÃO")
    # Norte
    vs_bar(fr, t, 71.3, 78.1, PANEL_Y, "3", "4", 3 / 7, "LULA", "FLÁVIO", title="NORTE · ESTADOS")
    v = counter(t, 79.3, 2.2, 0, 1079); big_num(fr, t, 79.3, 85.4, PANEL_Y + 90, f"{v:,.0f}".replace(",", "."), "VOTOS DE DIFERENÇA NA REGIÃO", (255, 130, 130), 170)
    R.pill(fr, "EMPATE", CX, 470, env(t, 68.4, 71.2), fill=(90, 70, 160), size=46)
    # balança
    k1 = env(t, 85.8, 95.4); k2 = env(t, 90.2, 95.4)
    if k1 > 0:
        lay = Image.new("RGBA", (W, 330), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); x0 = 170; full = 830 / 13.7
        g1 = eo((t - 86.0) / 1.0); d.rounded_rectangle((x0, 40, x0 + int(9.3 * full * g1), 110), 30, fill=FLAV + (255,))
        d.text((x0, 20), "FORA DO NORDESTE · FLÁVIO", font=MF("ExtraBold", 28), fill=(170, 200, 255, 255), anchor="lm")
        d.text((x0 + int(9.3 * full * g1) + 16, 75), "+9,3 mi", font=ANTON(56), fill=WHITE + (255,), anchor="lm")
        if k2 > 0:
            g2 = eo((t - 90.4) / 1.0); d.rounded_rectangle((x0, 170, x0 + int(13.7 * full * g2), 240), 30, fill=LULA + (int(255 * k2),))
            d.text((x0, 150), "NORDESTE · LULA", font=MF("ExtraBold", 28), fill=(255, 170, 170, int(255 * k2)), anchor="lm")
            tx = min(x0 + int(13.7 * full * g2) + 16, 860); d.text((tx, 205), "+13,7 mi", font=ANTON(56), fill=WHITE + (int(255 * k2),), anchor="lm" if tx < 860 else "rm")
        fr.alpha_composite(R.fade(lay, k1), (0, PANEL_Y - 40))
    adv_chip(fr, t, 93.5, 95.4, 465, "L", "= LULA +4,4 MILHÕES")
    # opinião
    big_num(fr, t, 97.1, 103.0, PANEL_Y + 40, "1 VOTO = 1 VOTO", "NORDESTINO OU CATARINENSE", GOLD_L, 120)
    big_num(fr, t, 103.2, 106.6, PANEL_Y + 40, "VOTAR DIFERENTE", "NÃO É O PROBLEMA", WHITE, 100)
    big_num(fr, t, 106.7, 112.3, PANEL_Y + 40, "E NA SUA CIDADE?", "COMENTA AQUI", GOLD_L, 110)
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); img, scr, sc = draw_map(tt); fr = Image.fromarray(img).convert("RGBA")
    labels(fr, tt, scr, sc); callout(fr, tt, scr); draw_title(fr, tt); panels(fr, tt)
    R.credit(fr, "Fonte: TSE · Bloomberg Línea · Exame", W - 30, 168, clamp((tt - 0.5) / 0.4) * clamp((EDIT_END - tt) / 0.3))
    g = np.zeros((480, W, 4), np.uint8); g[..., :3] = (3, 10, 22); g[..., 3] = np.linspace(0, 200, 480)[:, None].astype(np.uint8); fr.alpha_composite(Image.fromarray(g), (0, H - 480))
    M.caption(fr, tt, CAP_Y, 54)
    kc = clamp((tt - 0.6) / 0.4) * (1 - clamp((tt - (EDIT_END - 0.3)) / 0.3)); BAR.lower_card(fr, CARD[0], CARD[1], CARD_Y, kc, fs=40)
    cta = clamp((t - 106.7) / 0.4) if t > 106.7 else 0.0
    BAR.draw_bar(fr, clamp(t / END_IN), "canal", eo((t - 0.2) / 0.6), cta, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(fr, t)
    if t >= END_IN: fr.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return fr.convert("RGB")
def capa(out):
    img, scr, sc = draw_map(95.0); fr = Image.fromarray(img).convert("RGBA")
    d = ImageDraw.Draw(fr)
    put(fr, text_img("O BRASIL", ANTON(150), WHITE, 5, (0, 0, 0)), CX, 270); put(fr, text_img("REGIÃO POR REGIÃO", ANTON(96), GOLD_L, 5, (0, 0, 0)), CX, 410)
    R.pill(fr, "LULA 13 ESTADOS", 380, 1290, 1.0, fill=LULA, size=40); R.pill(fr, "FLÁVIO 13 + DF", 800, 1290, 1.0, fill=FLAV, size=40)
    put(fr, text_img("1.079 VOTOS", ANTON(110), WHITE, 5, (0, 0, 0)), CX, 1450); put(fr, text_img("O EMPATE QUE NINGUÉM VIU", MF("ExtraBold", 40), GOLD_L, 3, (0, 0, 0)), CX, 1550)
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
    ev = [(s[0] - 0.2, sfx.whoosh(0.5), 0.15) for s in SC[1:]]
    ev += [(t0, sfx.click(), 0.10) for t0 in sorted(REVEAL.values())]
    ev += [(a, sfx.thud(0.35), 0.18) for a, *_ in CALL] + [(79.3, sfx.thud(0.45), 0.3), (97.1, sfx.whoosh(0.8), 0.15), (END_IN - 0.3, sfx.whoosh(0.6), 0.2)]
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
