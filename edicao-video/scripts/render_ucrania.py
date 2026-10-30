"""Quanto já custou a guerra na Ucrânia, 9:16, ~55 s, narração do ElevenLabs. Mapa com a área ocupada aproximada (~1/5 com a Crimeia,
Pernambuco na mesma escala), baixas (CSIS: Rússia ~1,4 mi mortos, feridos ou desaparecidos; Ucrânia 525–625 mil; ONU: 17 mil+ civis),
ajuda (Europa ~€70 bi militar, Kiel; EUA US$ 133 bi em ajuda total), reconstrução US$ 588 bi (Banco Mundial/RDNA5) e pergunta ao
público. Sem opinião. Formato loop. Mapa: dados/ucrania_ocupacao_aprox.json (geoBoundaries + linha de frente aproximada)."""
import sys, math, subprocess, importlib.util, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("rex", f"{S}/work/render_exercito.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; eo = R.ease_out; ei = R.ease_in; eio = R.ease_io; bo = R.back_out
V = f"{S}/ucrania"; FD = f"{S}/fontdl"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
EDIT_END = 55.3; TOTAL = EDIT_END; END_IN = TOTAL + 99   # loop: nenhuma tela final
R.FIN_IN = EDIT_END + 99; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
GOLD = R.GOLD; GOLD_L = R.GOLD_L; NAVY = R.NAVY; WHITE = (255, 255, 255); RED = (226, 52, 52); GREEN_BR = (40, 150, 90); YEL = (255, 214, 64); INK = (20, 24, 34)
def ANTON(s): return ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s)
MF = R.MF
# ---------------------------------------------------------------- legenda (texto revisado à mão)
CAPTXT = [(0.05, 3.04, "Quatro anos e oito meses de guerra na Ucrânia."), (3.46, 4.62, "Quanto isso já custou?"), (5.15, 5.75, "Território:"),
          (6.11, 9.48, "a Rússia ocupa quase um quinto da Ucrânia, contando a Crimeia."), (9.87, 12.19, "É mais do que o estado de Pernambuco inteiro."),
          (12.73, 13.37, "Vidas:"), (13.64, 17.2, "segundo o centro americano CSIS,"), (17.3, 20.53, "a Rússia já teve cerca de 1,4 milhão de soldados mortos,"),
          (20.74, 22.58, "feridos ou desaparecidos."), (23.04, 23.76, "A Ucrânia,"), (23.96, 27.29, "entre 525 e 625 mil."),
          (27.82, 31.2, "E a ONU confirmou mais de 17 mil civis mortos."), (31.65, 32.26, "Armas:"), (32.52, 36.91, "só a Europa já mandou cerca de 70 bilhões de euros em ajuda militar."),
          (37.35, 41.48, "Os Estados Unidos, 133 bilhões de dólares em ajuda."), (41.97, 42.62, "Prejuízo:"),
          (43.0, 49.08, "o Banco Mundial calcula que reconstruir o país vai custar 588 bilhões de dólares."), (49.44, 50.59, "E a guerra continua."),
          (51.04, 53.0, "Você acha que ela acaba em 2027?"), (53.42, 54.05, "Comenta aqui"), (54.28, 54.96, "e me segue.")]
HOT = {"GUERRA", "UCRÂNIA.", "CUSTOU?", "TERRITÓRIO:", "QUINTO", "CRIMEIA.", "PERNAMBUCO", "VIDAS:", "CSIS,", "1,4", "MILHÃO", "MORTOS,", "FERIDOS",
       "DESAPARECIDOS.", "525", "625", "ONU", "17", "CIVIS", "ARMAS:", "EUROPA", "70", "BILHÕES", "MILITAR.", "133", "PREJUÍZO:", "BANCO", "MUNDIAL", "588",
       "CONTINUA.", "2027?", "AQUI", "SEGUE."}
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
CARDS = [(0.4, 5.05, "GUERRA NA UCRÂNIA", ["4 ANOS E 8 MESES", "DESDE 24/02/2022"]), (5.05, 12.6, "TERRITÓRIO", ["QUASE 1/5 OCUPADO", "COM A CRIMEIA"]),
         (12.6, 31.5, "VIDAS", ["SOLDADOS: CSIS", "CIVIS: ONU"]), (31.5, 41.9, "AJUDA", ["EUROPA: ~€70 BI MILITAR", "EUA: US$ 133 BI"]),
         (41.9, 49.35, "PREJUÍZO", ["RECONSTRUÇÃO:", "US$ 588 BILHÕES"]), (49.35, EDIT_END + 0.3, "E VOCÊ?", ["COMENTA AQUI"])]
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
# ---------------------------------------------------------------- mapa
GEO = json.load(open("/home/user/next-netlify-starter/edicao-video/dados/ucrania_ocupacao_aprox.json"))
BR = json.load(open(f"{S}/v76/br.json")); PE = [f for f in BR["features"] if f["properties"].get("sigla") == "PE"][0]["geometry"]
def rings(geom):
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    return [np.array(p[0], float) for p in polys]
UKR = rings(GEO["ukraine"]); OCC = rings(GEO["occupied"]); PER = [max(rings(PE), key=len)]   # sem Fernando de Noronha
KM = lambda lat: (111.32 * math.cos(math.radians(lat)), 110.57)
LAT0 = 48.4; PX_KM = 0.52           # mesma escala (px por km) para a Ucrânia e para Pernambuco
allu = np.concatenate(UKR); UCX, UCY = (allu[:, 0].min() + allu[:, 0].max()) / 2, (allu[:, 1].min() + allu[:, 1].max()) / 2
def proj(r, cx_ll, cy_ll, lat0, ox, oy):
    kx, ky = KM(lat0); return np.stack([ox + (r[:, 0] - cx_ll) * kx * PX_KM, oy - (r[:, 1] - cy_ll) * ky * PX_KM], 1)
def ukr_map(fr, t, ta, oy, occ_g, k):
    """contorno da Ucrânia; a área ocupada se pinta de sul para norte conforme occ_g (0-1)"""
    S2 = 2; lay = Image.new("RGBA", (W * S2, 700 * S2), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); top = oy - 350
    for r in UKR:
        p = proj(r, UCX, UCY, LAT0, CX, oy) - [0, top]; d.polygon([tuple(q * S2) for q in p], fill=(26, 52, 92, 255), outline=GOLD + (255,), width=3 * S2)
    if occ_g > 0:
        m = Image.new("L", lay.size, 0); md = ImageDraw.Draw(m)
        for r in OCC:
            p = proj(r, UCX, UCY, LAT0, CX, oy) - [0, top]; md.polygon([tuple(q * S2) for q in p], fill=255)
        ys = 700 * S2; cut = int(ys * (1 - occ_g)); sweep = Image.new("L", lay.size, 0); ImageDraw.Draw(sweep).rectangle((0, cut, lay.width, ys), fill=255)
        from PIL import ImageChops
        red = Image.new("RGBA", lay.size, (214, 36, 44, 235)); lay.paste(red, (0, 0), ImageChops.multiply(m, sweep))
        for r in UKR:
            p = proj(r, UCX, UCY, LAT0, CX, oy) - [0, top]; d.line([tuple(q * S2) for q in p] + [tuple(p[0] * S2)], fill=GOLD + (255,), width=3 * S2)
    put(fr, lay.resize((W, 700), Image.LANCZOS), W / 2, oy, k, 0.92 + 0.08 * eo((t - ta) / 0.5))
def pe_map(fr, t, ta, cx, cy, k):
    S2 = 2; allp = np.concatenate(PER); pcx, pcy = (allp[:, 0].min() + allp[:, 0].max()) / 2, (allp[:, 1].min() + allp[:, 1].max()) / 2
    lay = Image.new("RGBA", (500 * S2, 200 * S2), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for r in PER:
        p = proj(r, pcx, pcy, -8.3, 250, 100); d.polygon([tuple(q * S2) for q in p], fill=(40, 150, 90, 255), outline=WHITE + (255,), width=2 * S2)
    put(fr, lay.resize((500, 200), Image.LANCZOS), cx, cy, k, 0.6 + 0.4 * bo((t - ta) / 0.4, 2))
def counter_txt(fr, t, ta, tb, v1, fmt, cy, col, size=130, x=None):
    if t < ta: return
    v = v1 * eio((t - ta) / max(0.01, tb - ta)); put(fr, txt(fmt(v), ANTON(size), col, 8, NAVY), CX if x is None else x, cy, 1, 1 + 0.04 * (1 - eo((t - ta) / 0.3)))
def overlays(fr, t):
    # 0-5.05: abertura
    k = env(t, 0.0, 5.05, 0.2)
    if k > 0:
        put(fr, chipimg("24/02/2022 → HOJE", GOLD, 38, NAVY), CX, 300, k, 0.8 + 0.2 * bo(t / 0.4))
        put(fr, txt("A GUERRA NA", ANTON(110), WHITE, 7, NAVY), CX, 450, k, 0.85 + 0.15 * bo((t - 0.1) / 0.45))
        put(fr, txt("UCRÂNIA", ANTON(170), GOLD_L, 8, NAVY), CX, 620, k, 0.85 + 0.15 * bo((t - 0.25) / 0.45))
        if t > 1.2: put(fr, txt("4 ANOS E 8 MESES", ANTON(80), WHITE, 6, NAVY), CX, 800, env(t, 1.2, 5.05), 0.8 + 0.2 * bo((t - 1.2) / 0.35))
        if t > 3.4: put(fr, txt("QUANTO JÁ CUSTOU?", ANTON(96), RED, 7, NAVY), CX, 960, env(t, 3.4, 5.05), 0.7 + 0.3 * bo((t - 3.4) / 0.35))
    # 5.05-12.6: território
    k = env(t, 5.05, 12.65)
    if k > 0:
        put(fr, txt("TERRITÓRIO", ANTON(96), WHITE, 6, NAVY), CX, 300, k, 0.85 + 0.15 * bo((t - 5.05) / 0.4))
        ukr_map(fr, t, 5.1, 600, eio((t - 6.1) / 2.6), k)
        if t > 7.4:
            put(fr, txt("QUASE 1/5", ANTON(110), RED, 7, NAVY), CX, 880, env(t, 7.4, 12.65), 0.7 + 0.3 * bo((t - 7.4) / 0.35))
            put(fr, txt("≈ 110 mil km² com a Crimeia · área aproximada", MF("SemiBold", 26), (200, 210, 230), 3), CX, 970, env(t, 7.4, 12.65))
        if t > 9.9:
            pe_map(fr, t, 9.9, CX, 1120, env(t, 9.9, 12.65))
            put(fr, chipimg("PERNAMBUCO · 98 mil km² · mesma escala", (40, 150, 90), 30), CX, 1250, env(t, 10.2, 12.65))
    # 12.6-31.5: vidas
    k = env(t, 12.65, 31.55)
    if k > 0:
        put(fr, txt("VIDAS", ANTON(110), WHITE, 7, NAVY), CX, 300, k, 0.85 + 0.15 * bo((t - 12.65) / 0.4))
        if t > 17.3:
            kk = env(t, 17.3, 31.55); put(fr, chipimg("RÚSSIA", RED, 36), CX, 440, kk)
            counter_txt(fr, t, 17.4, 20.3, 1.4, lambda v: f"{v:.1f} MILHÃO".replace(".", ","), 545, WHITE, 104)
            if t > 20.7: put(fr, txt("mortos, feridos ou desaparecidos · CSIS", MF("SemiBold", 26), (200, 210, 230), 3), CX, 630, env(t, 20.7, 31.55))
        if t > 23.0:
            kk = env(t, 23.0, 31.55); put(fr, chipimg("UCRÂNIA", (36, 104, 226), 36), CX, 730, kk)
            counter_txt(fr, t, 24.0, 26.8, 525, lambda v: f"{v:.0f} A {v * 625 / 525:.0f} MIL", 835, WHITE, 96)
            if t > 25.0: put(fr, txt("mesma conta, estimativa do CSIS", MF("SemiBold", 26), (200, 210, 230), 3), CX, 915, env(t, 25.0, 31.55))
        if t > 27.8:
            kk = env(t, 27.8, 31.55); put(fr, chipimg("CIVIS MORTOS", GOLD, 36, NAVY), CX, 1020, kk)
            counter_txt(fr, t, 28.6, 30.6, 17, lambda v: f"+ DE {v:.0f} MIL", 1120, GOLD_L, 96)
            if t > 29.4: put(fr, txt("confirmados pela ONU · o número real é maior", MF("SemiBold", 26), (200, 210, 230), 3), CX, 1200, env(t, 29.4, 31.55))
    # 31.5-41.9: ajuda
    k = env(t, 31.55, 41.95)
    if k > 0:
        put(fr, txt("ARMAS E AJUDA", ANTON(100), WHITE, 7, NAVY), CX, 300, k, 0.85 + 0.15 * bo((t - 31.55) / 0.4))
        for i, (flag, lab, val, sub, ta, tb) in enumerate([("🇪🇺", "EUROPA", lambda v: f"≈ €{v:.0f} BI", "só ajuda militar · Instituto Kiel", 32.5, 35.5),
                                                            ("🇺🇸", "ESTADOS UNIDOS", lambda v: f"US$ {v * 133 / 70:.0f} BI", "ajuda total, não só armas · Instituto Kiel", 37.35, 40.3)]):
            if t < ta: continue
            y = 520 + i * 360; kk = env(t, ta, 41.95); sc = 0.6 + 0.4 * bo((t - ta) / 0.35, 2)
            box = Image.new("RGBA", (660, 300), (0, 0, 0, 0)); dd = ImageDraw.Draw(box); dd.rounded_rectangle((0, 0, 659, 299), 30, fill=(12, 30, 60, 235), outline=GOLD + (255,), width=3)
            box.alpha_composite(emoji(flag, 90), (30, 30)); dd.text((150, 75), lab, font=MF("ExtraBold", 44), fill=WHITE + (255,), anchor="lm")
            dd.text((330, 255), sub, font=MF("SemiBold", 24), fill=(200, 210, 230, 255), anchor="mm"); put(fr, box, CX, y, kk, sc)
            counter_txt(fr, t, ta + 0.2, tb, 70, val, y + 45, GOLD_L, 100)
    # 41.9-49.35: prejuízo
    k = env(t, 41.95, 49.4)
    if k > 0:
        put(fr, txt("PREJUÍZO", ANTON(110), WHITE, 7, NAVY), CX, 300, k, 0.85 + 0.15 * bo((t - 41.95) / 0.4))
        put(fr, emoji("🏚️", 150), CX, 500, k, 0.6 + 0.4 * bo((t - 42.2) / 0.4))
        if t > 43.0: put(fr, txt("reconstruir o país em 10 anos · Banco Mundial", MF("SemiBold", 26), (200, 210, 230), 3), CX, 640, env(t, 43.0, 49.4))
        counter_txt(fr, t, 44.2, 48.2, 588, lambda v: f"US$ {v:.0f} BI", 760, RED, 140)
        for i, (lab, ta) in enumerate([("TRANSPORTE", 46.0), ("ENERGIA", 46.4), ("MORADIA", 46.8)]):
            if t > ta: put(fr, chipimg(lab, NAVY, 30), CX + (i - 1) * 245, 920, env(t, ta, 49.4), 0.6 + 0.4 * bo((t - ta) / 0.3, 2))
        if t > 47.2: put(fr, txt("setores mais atingidos", MF("SemiBold", 26), (200, 210, 230), 3), CX, 1000, env(t, 47.2, 49.4))
    # 49.35-fim: pergunta + CTA (sem tela final)
    k = env(t, 49.4, EDIT_END + 1, 0.3, 0.01)
    if k > 0:
        put(fr, txt("E A GUERRA", ANTON(110), WHITE, 7, NAVY), CX, 430, k, 0.85 + 0.15 * bo((t - 49.4) / 0.4)); put(fr, txt("CONTINUA", ANTON(130), RED, 7, NAVY), CX, 580, k)
        if t > 51.0: put(fr, txt("ACABA EM 2027?", ANTON(100), GOLD_L, 7, NAVY), CX, 760, env(t, 51.0, 99), 0.7 + 0.3 * bo((t - 51.0) / 0.35))
        if t > 53.3: put(fr, chipimg("COMENTA AQUI", RED, 50), CX, 940, k, (0.6 + 0.4 * bo((t - 53.3) / 0.35, 2.2)) * (1 + 0.03 * math.sin(t * 6)))
        if t > 54.2: put(fr, chipimg("SIGA PARA MAIS", GOLD, 46, NAVY), CX, 1070, k, 0.6 + 0.4 * bo((t - 54.2) / 0.35, 2.2))
    if 0.5 < t < EDIT_END: R.credit(fr, "Fontes: CSIS, ONU, Instituto Kiel, Banco Mundial", W - 30, 168, clamp((t - 0.5) / 0.4))
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); fr = Image.fromarray(OCEAN).convert("RGBA")
    overlays(fr, tt)
    g = np.zeros((520, W, 4), np.uint8); g[..., :3] = (3, 10, 22); g[..., 3] = np.linspace(0, 210, 520)[:, None].astype(np.uint8); fr.alpha_composite(Image.fromarray(g), (0, H - 520))
    M.caption(fr, tt, CAP_Y, 54)
    for a_, b_, kick, lines in CARDS:
        kc = clamp((tt - a_) / 0.4) * (1 - clamp((tt - (b_ - 0.3)) / 0.3))
        if kc > 0: BAR.lower_card(fr, kick, lines, CARD_Y, kc, fs=40)
    cta = clamp((t - 53.3) / 0.4) if t > 53.3 else 0.0
    BAR.draw_bar(fr, clamp(t / TOTAL), "canal", eo((t - 0.2) / 0.6), cta, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(fr, t)
    return fr.convert("RGB")
def capa(out, var="A"):
    fr = Image.fromarray(OCEAN).convert("RGBA")
    if var == "A":
        put(fr, txt("QUANTO JÁ CUSTOU", ANTON(100), WHITE, 7, NAVY), CX, 260); put(fr, txt("A GUERRA NA", ANTON(100), WHITE, 7, NAVY), CX, 380)
        put(fr, txt("UCRÂNIA?", ANTON(150), GOLD_L, 8, NAVY), CX, 530)
        ukr_map(fr, 9, 0, 860, 1.0, 1.0); put(fr, stamp("QUASE 1/5 OCUPADO", RED, 56, -6), CX, 1130)
        put(fr, chipimg("VIDAS · ARMAS · PREJUÍZO", NAVY, 40), CX, 1300)
    else:
        put(fr, txt("4 ANOS E 8 MESES", ANTON(96), WHITE, 7, NAVY), CX, 280); put(fr, txt("DE GUERRA", ANTON(130), GOLD_L, 8, NAVY), CX, 420)
        for i, (lab, val, col) in enumerate([("SOLDADOS RUSSOS", "1,4 MILHÃO", RED), ("RECONSTRUÇÃO", "US$ 588 BI", GOLD_L), ("AJUDA DA EUROPA", "€70 BI", WHITE)]):
            y = 640 + i * 210; put(fr, txt(lab, MF("ExtraBold", 36), (200, 210, 230), 3), CX, y - 60); put(fr, txt(val, ANTON(110), col, 7, NAVY), CX, y + 20)
        put(fr, chipimg("OS NÚMEROS DA GUERRA NA UCRÂNIA", RED, 38), CX, 1320)
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
    ev = [(a - 0.15, sfx.whoosh(0.5), 0.15) for a in (5.05, 12.65, 31.55, 41.95, 49.4)]
    ev += [(x, pop(), 0.3) for x in (1.2, 3.4, 7.4, 9.9, 17.3, 23.0, 27.8, 32.5, 37.35, 46.0, 46.4, 46.8, 53.3, 54.2)]
    ev += [(x, sfx.thud(0.4), 0.28) for x in (6.1, 44.2, 49.4)]
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
