"""Comercial de 30 s do Ares do Horto (Plano&Plano) para a corretora Ana Paula. Projeto avulso, fora dos canais do Eliezio.
Minimalista: fundo off-white, verde profundo, DM Serif Display + Inter, planta 3D ilustrativa em camadas (piso, paredes, móveis).

Uso: python3 render_ares.py SAIDA MODO   (MODO: frames:t1,t2 | part:i:n | music | mux)
"""
import sys, os, math, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
FD = "/tmp/claude-0/-home-user-next-netlify-starter/698dd744-d40f-5d96-b9e9-72023ae79dbf/scratchpad/fontdl"
sys.path.insert(0, "/home/user/next-netlify-starter/edicao-video/scripts")
OUT = sys.argv[1]; MODE = sys.argv[2] if len(sys.argv) > 2 else "frames:1"
W, H, FPS, TOTAL = 1080, 1920, 30, 30.0
BG = (244, 241, 234); INK = (30, 38, 34); GREEN = (38, 74, 58); SAGE = (148, 172, 150); MUTED = (120, 128, 122); CREAM = (244, 238, 224); WARM = (196, 164, 126); GOLD = (190, 160, 108)
def SERIF(s): return ImageFont.truetype(f"{FD}/DMSerifDisplay-Regular.ttf", s)
def INTER(w, s): return ImageFont.truetype(f"{FD}/Inter-{w}.ttf", s)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def eio(x): x = clamp(x); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
def bo(x, s=1.6): x = clamp(x) - 1; return 1 + (s + 1) * x ** 3 + s * x ** 2

# ---------- texto ----------
_cache = {}
def timg(text, font, fill, track=0):
    k = (text, font.path, font.size, fill, track)
    if k in _cache: return _cache[k]
    asc, desc = font.getmetrics(); ws = [font.getlength(c) for c in text]; w = int(sum(ws) + track * (len(text) - 1)) + 8
    im = Image.new("RGBA", (max(w, 1), asc + desc + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = 4
    if track == 0: d.text((4, 4), text, font=font, fill=fill)
    else:
        for c, cw in zip(text, ws): d.text((x, 4), c, font=font, fill=fill); x += cw + track
    _cache[k] = im; return im
def alpha(im, a):
    if a >= 0.999: return im
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * a))); return im
def reveal(fr, im, x, y, p, a=1.0, anchor="c"):
    """texto subindo de trás de uma linha (máscara na base da caixa)"""
    p = eo(p)
    if p <= 0 or a <= 0: return
    w, h = im.size; off = int((1 - p) * h)
    if off >= h: return
    x0 = int(x - w / 2) if anchor == "c" else int(x)
    part = alpha(im.crop((0, 0, w, h - off)), a * clamp(p * 1.5)); fr.alpha_composite(part, (x0, int(y + off)))
def put(fr, im, x, y, a=1.0, anchor="c"):
    if a <= 0: return
    x0 = int(x - im.width / 2) if anchor == "c" else int(x); fr.alpha_composite(alpha(im, a), (x0, int(y)))
def hline(d, x0, x1, y, col, w=3): d.line((x0, y, x1, y), fill=col, width=w)

# ---------- planta 3D em camadas (planta oficial: laje, piso e paredes extrudadas) ----------
from PIL import ImageFilter
AS = f"{HERE}/assets"; PS = 0.6
_P = {}
def plan_assets():
    if _P: return _P
    im = Image.open(f"{AS}/planta_horiz_varanda.webp").convert("RGB"); a = np.asarray(im).astype(int)
    wall = Image.fromarray(((np.abs(a - 91).max(2) <= 5) * 255).astype("uint8")).filter(ImageFilter.MinFilter(11)).filter(ImageFilter.MaxFilter(11))
    closed = Image.fromarray(((a.min(2) < 240) * 255).astype("uint8")).filter(ImageFilter.MaxFilter(25)).filter(ImageFilter.MinFilter(25))
    ImageDraw.floodfill(closed, (60, 40), 128, thresh=0); fm = np.asarray(closed) != 128; fm[:30] = fm[-30:] = False; fm[:, :30] = fm[:, -30:] = False; foot = Image.fromarray((fm * 255).astype("uint8"))
    sz = (int(im.width * PS), int(im.height * PS))
    fl = np.asarray(im).copy(); fl[np.asarray(wall) > 0] = (228, 224, 216)
    flo = Image.fromarray(fl).resize(sz, Image.LANCZOS).convert("RGBA"); flo.putalpha(foot.resize(sz, Image.LANCZOS))
    _P.update(floor=flo, wall=wall.resize(sz, Image.LANCZOS), foot=foot.resize(sz, Image.LANCZOS), size=sz); return _P
ROOMS = [("Varanda", 450, 190), ("Sala", 380, 520), ("Cozinha", 215, 1060), ("Dormitório", 1010, 560), ("Dormitório", 1585, 1020), ("Banho", 905, 1300), ("Serviço", 640, 1290)]
def affine(yaw, pitch, k, T, lift):
    c, s = math.cos(yaw), math.sin(yaw); sp = math.sin(pitch); P = plan_assets(); cx, cy = P["size"][0] / 2, P["size"][1] / 2
    M = np.array([[c, -s], [s * sp, c * sp]]) * k; Mi = np.linalg.inv(M); t = np.array([T[0], T[1] - lift])
    off = -Mi @ t + np.array([cx, cy]); return (Mi[0, 0], Mi[0, 1], off[0], Mi[1, 0], Mi[1, 1], off[1]), M, t, (cx, cy)
def warp(img, data, size, res=Image.BICUBIC): return img.transform(size, Image.AFFINE, data, resample=res)
def extrude(canvas, mask, h, col_lo, col_hi, top):
    bb = mask.getbbox()
    if not bb: return
    x0, y0, x1, y1 = bb; m = mask.crop(bb); h = max(1, int(h))
    for i in range(h):
        f = i / max(1, h - 1); col = tuple(int(col_lo[j] + (col_hi[j] - col_lo[j]) * f) for j in range(3))
        canvas.paste(col + (255,), (x0, y0 - i, x1, y1 - i), m)
    canvas.paste(top + (255,), (x0, y0 - h, x1, y1 - h), m)
def plan3d(yaw, pitch, k, offs, size=(1080, 1200)):
    P = plan_assets(); cv = Image.new("RGBA", size, (0, 0, 0, 0)); T = (size[0] / 2, size[1] / 2); cp = math.cos(pitch)
    d0, _, _, _ = affine(yaw, pitch, k, T, 0)
    sh = warp(P["foot"], d0, size).resize((size[0] // 4, size[1] // 4)).filter(ImageFilter.GaussianBlur(6)).resize(size)
    cv.paste((30, 40, 34, 255), (0, 26, size[0], size[1] + 26), sh.point(lambda v: int(v * 0.18)))
    dS, _, _, _ = affine(yaw, pitch, k, T, offs[0]); extrude(cv, warp(P["foot"], dS, size), 16 * k * cp, (200, 194, 182), (232, 227, 217), (240, 236, 228))
    dF, _, _, _ = affine(yaw, pitch, k, T, offs[1] + 16 * k * cp + 1); cv.alpha_composite(warp(P["floor"], dF, size))
    dW, _, _, _ = affine(yaw, pitch, k, T, offs[2] + 16 * k * cp + 1)
    wm = warp(P["wall"], dW, size).point(lambda v: 255 if v > 110 else 0)
    extrude(cv, wm, 70 * k * cp, (196, 200, 194), (250, 248, 243), GREEN)
    return cv
def plan_point(x, y, yaw, pitch, k, T, lift):
    _, M, t, (cx, cy) = affine(yaw, pitch, k, T, lift); q = M @ (np.array([x * PS, y * PS]) - np.array([cx, cy])) + t; return q
# ---------- ícones de linha ----------
def arc(cx, cy, r, a0, a1, n=24, ry=None): ry = r if ry is None else ry; return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
def wave_(y, x0=0.1, x1=0.9, a=0.035): return [(x0 + (x1 - x0) * i / 20, y + a * math.sin(i / 20 * 4 * math.pi)) for i in range(21)]
ICONS = {
    "piscina": [arc(0.3, 0.2, 0.06, 180, 360) + [(0.36, 0.2), (0.36, 0.56)], arc(0.58, 0.2, 0.06, 180, 360) + [(0.64, 0.2), (0.64, 0.56)], [(0.36, 0.32), (0.64, 0.32)], [(0.36, 0.44), (0.64, 0.44)], wave_(0.66), wave_(0.8), wave_(0.94)],
    "playground": [[(0.08, 0.92), (0.95, 0.92)], [(0.2, 0.92), (0.2, 0.2)], [(0.36, 0.92), (0.36, 0.2)], [(0.2, 0.42), (0.36, 0.42)], [(0.2, 0.64), (0.36, 0.64)], [(0.2, 0.2), (0.36, 0.2)],
                   [(0.36 + 0.56 * (i / 20), 0.2 + 0.7 * (i / 20) ** 0.6) for i in range(21)]],
    "pet": [arc(0.5, 0.68, 0.2, 0, 360, 40, 0.16), arc(0.25, 0.4, 0.07, 0, 360), arc(0.41, 0.24, 0.07, 0, 360), arc(0.59, 0.24, 0.07, 0, 360), arc(0.75, 0.4, 0.07, 0, 360)],
    "churrasqueira": [[(0.16, 0.42), (0.84, 0.42)], arc(0.5, 0.42, 0.34, 0, 180), [(0.36, 0.7), (0.26, 0.94)], [(0.64, 0.7), (0.74, 0.94)],
                      [(0.42 + 0.03 * math.sin(i / 8 * 2 * math.pi), 0.3 - 0.24 * i / 8) for i in range(9)], [(0.58 + 0.03 * math.sin(i / 8 * 2 * math.pi), 0.3 - 0.24 * i / 8) for i in range(9)]],
}
def draw_icon(d, name, x, y, size, p, col, w=6):
    lines = [[(x + a * size, y + b * size) for a, b in l] for l in ICONS[name]]
    lens = [sum(math.dist(l[i], l[i + 1]) for i in range(len(l) - 1)) for l in lines]; budget = sum(lens) * clamp(p)
    for l, L in zip(lines, lens):
        if budget <= 0: break
        pts = [l[0]]
        for i in range(len(l) - 1):
            sl = math.dist(l[i], l[i + 1])
            if budget >= sl: pts.append(l[i + 1]); budget -= sl
            else:
                f = budget / sl; pts.append((l[i][0] + (l[i + 1][0] - l[i][0]) * f, l[i][1] + (l[i + 1][1] - l[i][1]) * f)); budget = 0; break
        if len(pts) > 1: d.line(pts, fill=col, width=w, joint="curve")
        for q in (pts[0], pts[-1]): d.ellipse((q[0] - w / 2 + 0.5, q[1] - w / 2 + 0.5, q[0] + w / 2 - 0.5, q[1] + w / 2 - 0.5), fill=col)
LEAF = [[(0.5 + 0.36 * math.sin(math.pi * i / 30) * (1 - i / 30) ** 0.3 * 0.9, 1 - i / 30) for i in range(31)],
        [(0.5 - 0.36 * math.sin(math.pi * i / 30) * (1 - i / 30) ** 0.3 * 0.9, 1 - i / 30) for i in range(31)],
        [(0.5, 1.12), (0.5, 0.12)]]
ICONS["folha"] = LEAF

# ---------- fotos ----------
_PH = {}
def photo(name, w):
    k = (name, w)
    if k not in _PH: im = Image.open(f"{AS}/{name}.webp").convert("RGB"); _PH[k] = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
    return _PH[k]
def kb(name, bw, bh, p, cxf=0.5, z0=1.0, z1=1.08, src_w=1400):
    im = photo(name, src_w); z = z0 + (z1 - z0) * p; ar = bw / bh
    ch = im.height / z; cw = ch * ar
    if cw > im.width: cw = im.width / z; ch = cw / ar
    x = clamp(im.width * cxf - cw / 2, 0, im.width - cw); y = (im.height - ch) / 2
    return im.crop((int(x), int(y), int(x + cw), int(y + ch))).resize((bw, bh), Image.BICUBIC)
def rmask(w, h, r):
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255); return m
_RM = {}
def card(fr, img, x, y, r=36, a=1.0):
    k = img.size + (r,)
    if k not in _RM: _RM[k] = rmask(img.width, img.height, r)
    m = _RM[k] if a >= 0.999 else _RM[k].point(lambda v: int(v * a)); fr.paste(img, (int(x), int(y)), m)

# ---------- cenas ----------
S1, S2, S3, S4, S5 = 0.0, 4.35, 9.2, 14.7, 20.6
VO_OFF = 0.3
def life(t, a, b, fo=0.35): return clamp((b - t) / fo) if t < b else 0.0
def sc1(fr, d, t):
    a = life(t, S1, S2)
    if a <= 0: return
    ph = kb("fachada", 1080, 1300, t / S2, 0.47, 1.0, 1.1, 1600)
    gr = Image.new("L", (1080, 1300), 255); gd = ImageDraw.Draw(gr)
    for y in range(900, 1300): gd.line((0, y, 1080, y), fill=int(255 * (1 - ((y - 900) / 400) ** 1.4)))
    fr.paste(ph, (0, 0), gr if a >= 0.999 else gr.point(lambda v: int(v * a)))
    reveal(fr, timg("PLANO&PLANO APRESENTA", INTER(500, 26), MUTED, 7), 540, 1250, (t - 0.5) / 0.6, a)
    reveal(fr, timg("Ares do Horto", SERIF(150), INK), 540, 1295, (t - 0.8) / 0.7, a)
    w = 240 * eio((t - 1.5) / 0.6)
    if w > 1: hline(d, 540 - w / 2, 540 + w / 2, 1520, GOLD + (int(255 * a),), 3)
    reveal(fr, timg("Viva perto do verde.", INTER(400, 46), GREEN), 540, 1550, (t - 1.8) / 0.6, a)
def sc2(fr, d, t):
    u = t - S2; a = clamp(u / 0.35) * life(t, S2, S3)
    if a <= 0: return
    r = 250 * eo(u / 0.9); ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.ellipse((540 - r * 1.05 - 40, 760 - r * 0.95, 540 + r * 1.05 - 40, 760 + r * 0.95), fill=SAGE + (70,))
    r2 = r * 0.72; od.ellipse((620 - r2, 820 - r2 * 0.9, 620 + r2, 820 + r2 * 0.9), fill=SAGE + (95,))
    for k in range(3):   # ondas do pino
        pu = ((u - 1.0 - k * 0.5) % 1.5) / 1.5
        if u > 1.0 + k * 0.5:
            rr = 30 + 150 * eo(pu); od.ellipse((540 - rr, 860 - rr * 0.45, 540 + rr, 860 + rr * 0.45), outline=GREEN + (int(160 * (1 - pu)),), width=3)
    py = 860 - 260 * (1 - bo((u - 0.5) / 0.6, 1.2)) if u > 0.5 else -999
    if py > -900:
        od.ellipse((540 - 46, py - 150, 540 + 46, py - 58), fill=GREEN + (255,)); od.polygon([(506, py - 92), (574, py - 92), (540, py)], fill=GREEN + (255,))
        od.ellipse((540 - 17, py - 121, 540 + 17, py - 87), fill=BG + (255,))
    fr.alpha_composite(alpha(ov, a))
    reveal(fr, timg("LOCALIZAÇÃO", INTER(600, 26), GREEN, 8), 540, 1140, (u - 0.7) / 0.5, a)
    reveal(fr, timg("Horto do Ipê", SERIF(130), INK), 540, 1190, (u - 0.9) / 0.6, a)
    reveal(fr, timg("Zona Sul · São Paulo", INTER(400, 46), MUTED), 540, 1370, (u - 1.2) / 0.6, a)
    reveal(fr, timg("Estrada do Campo Limpo, 1501", INTER(500, 32), GREEN, 1), 540, 1450, (u - 1.5) / 0.6, a)
def sc3(fr, d, t):
    u = t - S3; a = clamp(u / 0.4) * life(t, S3, S4, 0.45)
    if a <= 0: return
    reveal(fr, timg("PLANTA ILUSTRATIVA", INTER(600, 26), GREEN, 8), 540, 215, (u - 0.2) / 0.5, a)
    reveal(fr, timg("2 dormitórios", SERIF(124), INK), 540, 262, (u - 0.35) / 0.6, a)
    reveal(fr, timg("com varanda", INTER(400, 44), MUTED), 540, 420, (u - 0.55) / 0.6, a)
    D = S4 - S3; E = [0.0, 150.0, 300.0]; df, dw = eio((u - 0.5) / 0.9), eio((u - 1.0) / 0.9); up = 0.0
    offs = [0.0, E[1] * (1 - df + 0.6 * up), E[2] * (1 - dw + 0.6 * up)]
    yaw = math.radians(-28 + 22 * eio(u / D)); pitch = math.radians(42 + 10 * eio(u / D)); k = 0.62 + 0.05 * eo(u / 2.5)
    top = 460; im = plan3d(yaw, pitch, k, offs)
    fr.alpha_composite(alpha(im, a), (0, top))
    T = (540, 600 + top); cp = math.cos(pitch)
    for i, (name, x, y) in enumerate(ROOMS):
        pu = (u - 2.1 - i * 0.24) / 0.35; la = a * clamp(pu)
        if la <= 0: continue
        px, py = plan_point(x, y, yaw, pitch, k, T, offs[1] + 16 * k * cp + 1)
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov); ly = py - 60 * eo(pu)
        od.ellipse((px - 7, py - 7, px + 7, py + 7), fill=GREEN + (255,)); od.ellipse((px - 13, py - 13, px + 13, py + 13), outline=GREEN + (255,), width=2)
        od.line((px, py - 13, px, ly), fill=GREEN + (255,), width=2)
        tx = timg(name, INTER(600, 28), CREAM); pw = tx.width + 30
        od.rounded_rectangle((px - pw / 2, ly - 46, px + pw / 2, ly), 23, fill=GREEN + (255,)); ov.alpha_composite(tx, (int(px - tx.width / 2), int(ly - 44)))
        fr.alpha_composite(alpha(ov, la))
    reveal(fr, timg("Sala e cozinha integradas", INTER(400, 44), INK), 540, 1500, (u - 3.3) / 0.6, a)
    reveal(fr, timg("Opções com e sem varanda", INTER(400, 40), MUTED), 540, 1558, (u - 3.5) / 0.6, a)
CARDS = [("piscina", "Piscinas adulto e infantil", 0.55), ("academia", "Academia", 0.5), ("portaria", "Portaria", 0.62)]
def sc4(fr, d, t):
    u = t - S4; a = clamp(u / 0.4) * life(t, S4, S5)
    if a <= 0: return
    reveal(fr, timg("LAZER E CONFORTO", INTER(600, 26), GREEN, 8), 540, 215, (u - 0.1) / 0.5, a)
    reveal(fr, timg("Para viver bem", SERIF(110), INK), 540, 258, (u - 0.25) / 0.6, a)
    seg = (S5 - S4) / 3; bw, bh, y0 = 940, 1060, 450
    for i, (name, label, cxf) in enumerate(CARDS):
        st = i * seg - (0.0 if i == 0 else 0.45); p = (u - st) / 0.6
        if p <= 0: continue
        if i < 2 and u > (i + 1) * seg + 0.3: continue
        x = 70 + (1080 if i else 0) * (1 - eo(p)); pz = clamp((u - st) / (seg + 0.6))
        img = kb(name, bw, bh, pz, cxf, 1.02, 1.12)
        card(fr, img, x, y0, 36, a * (clamp(p * 2) if i == 0 else 1))
        tx = timg(label, INTER(600, 34), INK); cw = tx.width + 44; la = a * clamp((u - st - 0.4) / 0.4)
        if la > 0:
            ov = Image.new("RGBA", (cw, 64), (0, 0, 0, 0)); ImageDraw.Draw(ov).rounded_rectangle((0, 0, cw - 1, 63), 32, fill=(250, 248, 243, 240)); ov.alpha_composite(tx, (22, 8))
            put(fr, ov, x + 34, y0 + bh - 98, la, "l")
    rows = [["Playground", "Pet place", "Churrasqueira", "Redário"], ["Lounge", "Espaço delivery", "e muito mais"]]
    k = 0
    for r_, row in enumerate(rows):
        ims = [timg(n, INTER(500, 26), GREEN if n != "e muito mais" else CREAM) for n in row]; ws = [im.width + 36 for im in ims]
        x = 540 - (sum(ws) + 12 * (len(ws) - 1)) / 2; y = 1532 + r_ * 62
        for n, im, w_ in zip(row, ims, ws):
            p = (u - 0.9 - k * 0.12) / 0.4; k += 1
            if p > 0:
                ov = Image.new("RGBA", (int(w_), 50), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
                if n == "e muito mais": od.rounded_rectangle((0, 0, w_ - 1, 49), 25, fill=GREEN + (255,))
                else: od.rounded_rectangle((0, 0, w_ - 1, 49), 25, fill=(250, 248, 243, 255), outline=(214, 206, 190, 255), width=2)
                ov.alpha_composite(im, (18, 6)); put(fr, ov, x, y + 10 * (1 - eo(p)), a * clamp(p * 1.5), "l")
            x += w_ + 12
_AP = {}
def ana(d_):
    if d_ not in _AP:
        im = Image.open(f"{AS}/ana_paula.jpg").convert("RGB").crop((60, 250, 1060, 1250)).resize((d_, d_), Image.LANCZOS)
        m = Image.new("L", (d_ * 4, d_ * 4), 0); ImageDraw.Draw(m).ellipse((0, 0, d_ * 4 - 1, d_ * 4 - 1), fill=255); _AP[d_] = (im, m.resize((d_, d_), Image.LANCZOS))
    return _AP[d_]
def sc5(fr, d, t):
    u = t - S5
    if u < 0: return
    r = 1300 * eio(u / 0.8); d.ellipse((540 - r, 960 - r, 540 + r, 960 + r), fill=GREEN)
    reveal(fr, timg("AGENDE SUA VISITA", INTER(600, 28), SAGE, 9), 540, 300, (u - 0.5) / 0.5)
    pu = (u - 0.7) / 0.7
    if pu > 0:
        D = 340; s_ = 0.85 + 0.15 * bo(pu); dd = int(D * s_); im, m = ana(dd); a_ = clamp(pu * 1.8)
        ring = int(dd + 16); d.ellipse((540 - ring / 2, 560 - ring / 2, 540 + ring / 2, 560 + ring / 2), outline=GOLD, width=3) if a_ > 0.5 else None
        fr.paste(im, (540 - dd // 2, 560 - dd // 2), m.point(lambda v: int(v * a_)))
    reveal(fr, timg("Ana Paula", SERIF(150), CREAM), 540, 760, (u - 1.0) / 0.7)
    reveal(fr, timg("Corretora de Imóveis", INTER(400, 46), CREAM), 540, 960, (u - 1.2) / 0.6)
    w = 220 * eio((u - 1.4) / 0.6)
    if w > 1: hline(d, 540 - w / 2, 540 + w / 2, 1045, GOLD, 3)
    reveal(fr, timg("CRECI-SP 201.926", INTER(600, 40), SAGE, 2), 540, 1070, (u - 1.5) / 0.6)
    pu = (u - 2.0) / 0.6
    if pu > 0:
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov); s_ = 0.9 + 0.1 * bo(pu); hw, hh = 400 * s_, 70 * s_; cy = 1280
        od.rounded_rectangle((540 - hw, cy - hh, 540 + hw, cy + hh), int(hh), fill=CREAM + (255,))
        ix = 540 - hw + 78; od.ellipse((ix - 34, cy - 34, ix + 34, cy + 34), outline=GREEN + (255,), width=5); od.polygon([(ix - 30, cy + 18), (ix - 40, cy + 40), (ix - 14, cy + 30)], fill=GREEN + (255,))
        od.rounded_rectangle((ix - 13, cy - 16, ix + 13, cy + 16), 6, outline=GREEN + (255,), width=4)
        tx = timg("(11) 97246-9161", INTER(700, 62), GREEN); ov.alpha_composite(tx, (int(540 - hw + 140), int(cy - 40)))
        fr.alpha_composite(alpha(ov, clamp(pu * 1.6)))
    reveal(fr, timg("Chame no WhatsApp", INTER(500, 32), SAGE, 2), 540, 1375, (u - 2.4) / 0.5)
    reveal(fr, timg("Ares do Horto  ·  Plano&Plano", INTER(500, 34), CREAM, 2), 540, 1560, (u - 2.7) / 0.6)
    reveal(fr, timg("Imagens e planta meramente ilustrativas. Informações sujeitas a alteração.", INTER(400, 22), SAGE), 540, 1790, (u - 3.0) / 0.6)
def chrome(fr, d, t):
    a = clamp((t - S2 + 0.1) / 0.5) * life(t, S2, S5 + 0.3, 0.4)
    if a > 0:
        put(fr, timg("ARES DO HORTO", INTER(600, 22), INK, 6), 72, 92, a, "l"); im = timg("PLANO&PLANO", INTER(500, 22), MUTED, 6); put(fr, im, W - 72 - im.width, 92, a, "l")
        hline(d, 72, W - 72, 140, (210, 204, 192, int(255 * a)), 2)
    # marca d'água da corretora: foto em círculo no canto inferior + nome, CRECI e telefone
    wa = clamp((t - 0.8) / 0.6) * life(t, 0, S5 + 0.2, 0.4)
    if wa <= 0: return
    D = 128; im, m = ana(D); x0, y0 = 72, 1700
    d.ellipse((x0 - 5, y0 - 5, x0 + D + 5, y0 + D + 5), outline=GOLD + (int(255 * wa),), width=2)
    fr.paste(im, (x0, y0), m.point(lambda v: int(v * wa)))
    tx = 72 + D + 26
    put(fr, timg("Ana Paula", INTER(600, 30), INK), tx, y0 + 14, wa, "l")
    put(fr, timg("Corretora  ·  CRECI-SP 201.926", INTER(400, 22), MUTED, 1), tx, y0 + 56, wa, "l")
    put(fr, timg("(11) 97246-9161", INTER(600, 24), GREEN, 1), tx, y0 + 86, wa, "l")
_VIG = None
def finish(img, t):
    global _VIG
    if _VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
        _VIG = (1 - 0.16 * np.clip(r - 0.55, 0, 1) ** 1.6)[..., None].astype(np.float32)
    a = np.asarray(img).astype(np.float32) * _VIG
    rng = np.random.default_rng(int(t * FPS)); a += rng.normal(0, 2.2, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1)
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
def frame_at(t):
    fr = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(fr)
    sc1(fr, d, t); sc2(fr, d, t); sc3(fr, d, t); sc4(fr, d, t); chrome(fr, d, t); sc5(fr, d, t)
    return finish(fr.convert("RGB"), t)

# ---------- trilha própria (F maior, 100 BPM) ----------
def music(path):
    SR = 48000; N = int((TOTAL + 0.5) * SR); out = np.zeros((N, 2)); bar = 2.4; beat = 0.6
    def midi(m): return 440 * 2 ** ((m - 69) / 12)
    def add(i0, sig, pan=0.0, g=1.0):
        if i0 >= N: return
        i1 = min(N, i0 + len(sig)); s_ = sig[:i1 - i0] * g; out[i0:i1, 0] += s_ * (1 - pan); out[i0:i1, 1] += s_ * (1 + pan)
    prog = [(53, [57, 60, 64, 65]), (57, [57, 60, 64, 67]), (50, [57, 62, 65, 69]), (46, [58, 62, 65, 69])]
    for b in range(13):
        root, ch = prog[b % 4]; t0 = b * bar; n = int((bar + 1.0) * SR); tt = np.arange(n) / SR
        last = t0 >= 26.0
        if last: root, ch = prog[0]; n = int(4.5 * SR); tt = np.arange(n) / SR
        env = np.clip(tt / 0.7, 0, 1) * (np.exp(-np.maximum(tt - 2.6, 0) / 0.8) if last else np.clip((bar + 1.0 - tt) / 1.0, 0, 1))
        for m in ch:
            f = midi(m); sig = sum(g * np.sin(2 * np.pi * f * h * (1 + dt) * tt) for h, g, dt in ((1, 1, 0), (1, 0.6, 0.003), (2, 0.25, -0.002), (3, 0.08, 0)))
            add(int(t0 * SR), sig * env, 0.0, 0.016)
        if last:
            break
        if t0 >= 2.4:   # arpejo de piano suave em colcheias
            arp = ch + [ch[2] + 12, ch[1] + 12]; pat = [0, 2, 1, 3, 4, 3, 2, 1]
            for k in range(8):
                f = midi(arp[pat[k]] + 12); m_ = int(1.2 * SR); tk = np.arange(m_) / SR
                sig = np.sin(2 * np.pi * f * tk) * np.exp(-tk * 5) + 0.35 * np.sin(4 * np.pi * f * tk) * np.exp(-tk * 9)
                sig *= np.clip(tk / 0.004, 0, 1); add(int((t0 + k * beat / 2) * SR), sig, 0.35 if k % 2 else -0.35, 0.05)
        if t0 >= 4.8:   # baixo
            for off in (0, 1.5 * beat):
                m_ = int(1.2 * SR); tk = np.arange(m_) / SR; f = midi(root - 12)
                add(int((t0 + off) * SR), (np.sin(2 * np.pi * f * tk) + 0.2 * np.sin(4 * np.pi * f * tk)) * np.exp(-tk * 2.2) * np.clip(tk / 0.01, 0, 1), 0, 0.11)
        if S3 - 1.0 <= t0 < S5:   # batida macia e chocalho
            rng = np.random.default_rng(b)
            for k in range(4):
                tk = np.arange(int(0.4 * SR)) / SR
                if k % 2 == 0: add(int((t0 + k * beat) * SR), np.sin(2 * np.pi * (50 + 70 * np.exp(-tk * 30)) * tk) * np.exp(-tk * 9), 0, 0.2)
                nz = rng.normal(0, 1, int(0.08 * SR)); nz = np.diff(np.concatenate([[0], nz])) * np.exp(-np.arange(len(nz)) / SR * 50)
                add(int((t0 + k * beat + beat / 2) * SR), nz, 0.2, 0.012)
    ir_n = int(2.2 * SR); rng = np.random.default_rng(3); ti = np.arange(ir_n) / SR
    for c in range(2):
        ir = rng.normal(0, 1, ir_n) * np.exp(-ti / 0.55); ir[0] = 0; ir /= np.sqrt((ir ** 2).sum())
        L = 1 << int(np.ceil(np.log2(N + ir_n))); wet = np.fft.irfft(np.fft.rfft(out[:, c], L) * np.fft.rfft(ir, L), L)[:N]
        out[:, c] = out[:, c] + 0.35 * wet
    out = np.tanh(out * 1.4) / 1.4; out *= 0.9 / (np.abs(out).max() + 1e-9)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32000).astype(np.int16).tobytes())
def mux(video):
    import sfx
    music(f"{HERE}/music.wav")
    ev = [(S2 - 0.25, sfx.whoosh(0.5), 0.1), (S3 - 0.25, sfx.whoosh(0.5), 0.1), (S4 - 0.25, sfx.whoosh(0.5), 0.1), (S5 - 0.1, sfx.whoosh(0.6), 0.12),
          (S2 + 1.05, sfx.thud(0.4), 0.18), (S3 + 1.0, sfx.thud(0.4), 0.12), (S3 + 1.8, sfx.thud(0.4), 0.12)]
    ev += [(S3 + 3.3 + i * 0.45, sfx.click(seed=i), 0.07) for i in range(5)] + [(S4 + 0.8 + i * 0.3, sfx.click(seed=10 + i), 0.06) for i in range(4)]
    sfx.build(ev, TOTAL, f"{HERE}/sfx.wav")
    vd = int(VO_OFF * 1000)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", f"{HERE}/music.wav", "-i", f"{HERE}/sfx.wav", "-i", f"{HERE}/narracao.mp3", "-filter_complex",
                    f"[3:a]aresample=48000,aformat=channel_layouts=stereo,adelay={vd}|{vd},highpass=f=75,acompressor=threshold=0.12:ratio=2.5:attack=6:release=180:makeup=1.6,"
                    f"equalizer=f=3200:t=q:w=1.2:g=2,asplit=2[vo][key];[1:a]volume=0.55[m0];[m0][key]sidechaincompress=threshold=0.04:ratio=6:attack=25:release=450[m];[2:a]volume=0.6[s];"
                    f"[vo][m][s]amix=inputs=3:normalize=0,atrim=0:{TOTAL},afade=t=out:st={TOTAL - 1.2}:d=1.2,loudnorm=I=-14:TP=-1.5:LRA=11[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUT], check=True)
def main():
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]; outs = [frame_at(x).resize((360, 640), Image.LANCZOS) for x in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUT, quality=90); return
    if MODE.startswith("part"):
        i, n = map(int, MODE.split(":")[1:]); NF = int(TOTAL * FPS); a, b = NF * i // n, NF * (i + 1) // n
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
        for k in range(a, b): enc.stdin.write(frame_at(k / FPS).tobytes())
        enc.stdin.close(); enc.wait(); print("part done", i); return
    if MODE == "mux": mux(f"{HERE}/video.mp4"); print("done")
main()
