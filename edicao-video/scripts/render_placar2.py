"""Placar da checagem do debate da Globo, versão minimalista: fundo escuro liso, Inter fina, linhas e barras finas, anéis no lugar de
ponteiros, um acento de cor por candidato, entradas suaves (sobe e aparece). Fonte sempre na tela: checagemaovivo.org (IA, preliminar)."""
import sys, math, subprocess, importlib.util, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
sys.path.insert(0, f"{S}/work")
import sfx
W, H, FPS, CX = R.W, R.H, R.FPS, R.CX; clamp = R.clamp; eo = R.ease_out; ei = R.ease_in; eio = R.ease_io; bo = R.back_out
V = f"{S}/v61"; FD = f"{S}/fontdl"
_f = {}
def I(w, s):
    if (w, s) not in _f: _f[(w, s)] = ImageFont.truetype(f"{FD}/Inter-{w}.ttf", s)
    return _f[(w, s)]
WH = (240, 242, 245); MUT = (138, 146, 160); DIM = (70, 78, 92); TRK = (34, 39, 48)
GREEN = (52, 211, 153); RED = (248, 86, 86); AMBER = (245, 172, 64); GRAY = (96, 104, 118)
L0, L1 = 160, 1010
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
_r = np.sqrt(((xx - CX) / W) ** 2 + ((yy - H * 0.45) / H) ** 2)
BG = (np.array([9, 11, 15], np.float32) + np.array([9, 11, 15], np.float32) * np.clip(1 - _r * 2.2, 0, 1)[..., None]).astype(np.uint8)
def avatar(path, size, focus, zoom):
    im = Image.open(path).convert("RGB"); s = int(min(im.size) * zoom); cx, cy = int(im.width * focus[0]), int(im.height * focus[1])
    y0 = max(0, cy - s // 2); im = im.crop((cx - s // 2, y0, cx + s // 2, y0 + s)).resize((size * 2, size * 2), Image.LANCZOS)
    m = Image.new("L", (size * 2, size * 2), 0); ImageDraw.Draw(m).ellipse((0, 0, size * 2 - 1, size * 2 - 1), fill=255)
    im = im.convert("RGBA"); im.putalpha(m); im = im.resize((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size + 8, size + 8), (0, 0, 0, 0)); ImageDraw.Draw(out).ellipse((0, 0, size + 7, size + 7), outline=(255, 255, 255, 70), width=2)
    out.alpha_composite(im, (4, 4)); return out
_av = {}
def av(k, size):
    if (k, size) not in _av: _av[(k, size)] = avatar(f"{V}/dl/lula.jpg", size, (0.47, 0.30), 0.58) if k == "L" else avatar(f"{V}/dl/flavio.jpg", size, (0.57, 0.27), 0.5)
    return _av[(k, size)]
class C:                                                             # camada de conteúdo com alfa e deslocamento de entrada
    def __init__(s, fr): s.fr = fr; s.d = ImageDraw.Draw(fr)
def A(c, a): return c + (int(255 * clamp(a)),)
def text(L, s, x, y, f, col=WH, a=1.0, anchor="mm", track=0):
    if a <= 0.01: return
    if not track: L.d.text((x, y), s, font=f, fill=A(col, a), anchor=anchor); return
    w = sum(f.getlength(ch) + track for ch in s) - track; x0 = x - w / 2 if anchor[0] == "m" else x
    for ch in s: L.d.text((x0, y), ch, font=f, fill=A(col, a), anchor="l" + anchor[1]); x0 += f.getlength(ch) + track
def eyebrow(L, s, y, col=MUT, a=1.0, x=None): text(L, s, CX if x is None else x, y, I(600, 25), col, a, "mm" if x is None else "lm", track=5)
def wrap(s, f, maxw):
    out, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if f.getlength(t) <= maxw: cur = t
        else: out.append(cur); cur = w
    return out + [cur]
def para(L, s, y, f, col=WH, a=1.0, maxw=850, lh=1.32, x=None):
    ls = wrap(s, f, maxw)
    for i, l in enumerate(ls): text(L, l, CX if x is None else x, y + i * f.size * lh, f, col, a, "mm" if x is None else "lm")
    return y + len(ls) * f.size * lh
def put(L, im, cx, cy, a=1.0, k=1.0):
    if a <= 0.01 or k <= 0.01: return
    if abs(k - 1) > 0.01: im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.BICUBIC)
    L.fr.alpha_composite(R.fade(im, a), (int(cx - im.width / 2), int(cy - im.height / 2)))
def trace(L, x0, x1, y, t, kind, col, a=1.0, amp=1.0, spike_at=None):
    if a <= 0.01: return
    pts = []; n = 200
    for i in range(n + 1):
        u = i / n; ph = u * 9 - t * 3.0
        if kind == "calm": v = 5 * math.sin(ph * 2.1) + 2 * math.sin(ph * 5.3)
        else:
            v = 7 * math.sin(ph * 3.1) + 4 * math.sin(ph * 7.7); r = (math.sin(ph * 1.7) * 43758.5453) % 1
            if r > 0.8: v += (r - 0.8) * 330 * (1 if int(ph * 3) % 2 else -1)
            if spike_at is not None:
                q = clamp((t - spike_at) / 0.9); v += math.exp(-((u - 0.6) / 0.16) ** 2) * math.sin(q * math.pi) * 95 * math.sin(u * 150)
        pts.append((x0 + (x1 - x0) * u, y + v * amp))
    fade_pts = len(pts)
    for i in range(fade_pts - 1):                                    # traço que some à esquerda
        al = a * (0.15 + 0.85 * (i / fade_pts) ** 1.5); L.d.line((pts[i], pts[i + 1]), fill=A(col, al), width=3)
    ex, ey = pts[-1]; pr = 7 + 2 * math.sin(t * 8); L.d.ellipse((ex - pr, ey - pr, ex + pr, ey + pr), fill=A(col, a))
    g = 18 + 6 * (0.5 + 0.5 * math.sin(t * 4)); L.d.ellipse((ex - g, ey - g, ex + g, ey + g), outline=A(col, a * 0.35), width=2)
def thinbar(L, x0, y, w, segs_, total, k, a=1.0):
    h = 16; L.d.rounded_rectangle((x0, y, x0 + w, y + h), 8, fill=A(TRK, a)); acc = 0; gap = 5
    for n, col in segs_:
        xa = x0 + w * acc / total * k; ww = w * n / total * k - gap
        if ww > 2: L.d.rounded_rectangle((xa, y, xa + ww, y + h), 8, fill=A(col, a))
        acc += n
def ring(L, cx, cy, r, pct, col, u, a=1.0):
    box = (cx - r, cy - r, cx + r, cy + r); L.d.ellipse(box, outline=A(TRK, a), width=12); p = pct * eio(clamp(u / 1.3))
    if p > 0.003: L.d.arc(box, -90, -90 + 360 * p, fill=A(col, a), width=12)
    text(L, f"{int(round(pct * 100 * eio(clamp(u / 1.3))))}%", cx, cy - 6, I(300, 104), WH, a)
def falso(L, cx, cy, u):
    if u < 0: return
    k = 1.25 - 0.25 * eo(u / 0.18); a = clamp(u / 0.08); f = I(800, 44); s = "FALSO"; tr = 10
    w = sum(f.getlength(c) + tr for c in s) - tr + 70; h = 84; dx = 6 * math.sin(u * 70) * max(0, 1 - u / 0.3)
    lay = Image.new("RGBA", (int(w) + 10, h + 10), (0, 0, 0, 0)); LL = C(lay)
    LL.d.rounded_rectangle((4, 4, w + 4, h + 4), 42, fill=(RED[0], RED[1], RED[2], 38), outline=RED + (255,), width=3)
    text(LL, s, (w + 8) / 2, (h + 8) / 2 + 2, f, RED, 1.0, "mm", track=tr)
    put(L, lay, cx + dx, cy, a, k)
# --- roteiro ---
T1, T2, T3, T4, T5, T6 = 0.0, 4.6, 14.6, 20.6, 39.6, 47.6
EDIT_END = 53.0; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = EDIT_END; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
POINTS = [("FILME DO BOLSONARO", "Disse que um relatório da PF concluiu que não houve dinheiro público no filme de Jair Bolsonaro.",
           "A conclusão citada era de uma perícia privada. A PF ainda investiga o destino dos recursos."),
          ("PATRIMÔNIO DE LULA", "Disse que Lula tirou todos os bens do próprio nome.",
           "Na declaração ao TSE, Lula informa R$ 4,77 milhões em bens: imóveis, aplicações e um carro."),
          ("SANEAMENTO", "Disse que, por causa de Lula, a meta de saneamento ficou para depois de 2050.",
           "A meta legal continua em 2033. A extensão excepcional até 2040 já existia desde 2020."),
          ("MEIO AMBIENTE", "Disse que o governo não combate o desmatamento nem nenhuma queimada.",
           "A checagem cita fiscalização, combate a incêndios, prisões e queda do desmatamento.")]
PD = (T5 - T4) / 4; STAMP_AT = 1.5; FOUND_AT = 2.1
def ent(u, d=0.0): return eo((u - d) / 0.5)                         # entrada suave
def scene_bounds(t):
    for a, b in ((T1, T2), (T2, T3), (T3, T4), (T4, T4 + PD), (T4 + PD, T4 + 2 * PD), (T4 + 2 * PD, T4 + 3 * PD), (T4 + 3 * PD, T5), (T5, T6), (T6, EDIT_END + 9)):
        if t < b: return a, b
    return T6, EDIT_END + 9
def gfx_at(t):
    base = Image.fromarray(BG).convert("RGBA")
    text(C(base), "Conteúdo de opinião  ·  Checagem: checagemaovivo.org (IA)", CX, 190, I(400, 23), MUT, clamp(t / 0.5))
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); L = C(lay); OY = 70
    if t < T2:
        u = t; eyebrow(L, "DEBATE DA GLOBO  ·  23/10", 420, MUT, ent(u))
        put(L, av("L", 120), L0 + 60, 620, ent(u, 0.2)); text(L, "Lula", L0 + 60, 712, I(600, 28), WH, ent(u, 0.2))
        trace(L, L0 + 150, L1, 620, t, "calm", GREEN, ent(u, 0.35))
        put(L, av("F", 120), L0 + 60, 840, ent(u, 0.4)); text(L, "Flávio", L0 + 60, 932, I(600, 28), WH, ent(u, 0.4))
        trace(L, L0 + 150, L1, 840, t, "spike", RED, ent(u, 0.55))
        k1 = ent(u, 1.1); k2 = ent(u, 1.35)
        text(L, "Quem teve mais", CX, 1130 + 30 * (1 - k1), I(300, 92), WH, k1)
        text(L, "falas falsas?", CX, 1245 + 30 * (1 - k2), I(800, 104), RED, k2)
    elif t < T3:
        u = t - T2; eyebrow(L, "PLACAR DA CHECAGEM", 400, MUT, ent(u)); text(L, "167 falas checadas no debate", CX, 452, I(400, 34), MUT, ent(u, 0.1))
        rows = (("L", "Lula", "63 falas", [(58, GREEN), (5, AMBER)], 63, [("58 fato", GREEN), ("5 não é bem assim", AMBER)], 600),
                ("F", "Flávio", "103 falas", [(8, GREEN), (54, RED), (37, AMBER), (4, GRAY)], 103, [("8 fato", GREEN), ("54 falso", RED), ("37 não é bem assim", AMBER), ("4 inconclusivas", GRAY)], 820))
        for j, (k_, nm, cnt, sg, tot, leg, y) in enumerate(rows):
            kk = ent(u, 0.3 + j * 0.4); put(L, av(k_, 92), L0 + 46, y, kk)
            text(L, nm, L0 + 120, y - 22, I(700, 40), WH, kk, "lm"); text(L, cnt, L1, y - 22, I(400, 32), MUT, kk, "rm")
            thinbar(L, L0 + 120, y + 18, L1 - L0 - 120, sg, tot, eio(clamp((u - 0.7 - j * 0.4) / 1.2)), kk)
            x = L0 + 120; kl = ent(u, 1.9 + j * 0.2)
            for s_, c_ in leg:
                text(L, s_, x, y + 70, I(600, 25), c_, kl, "lm"); x += I(600, 25).getlength(s_) + 26
        kb = ent(u, 3.2); eyebrow(L, "FALAS CLASSIFICADAS COMO FALSAS", 1030, MUT, kb)
        n = int(round(54 * eo(clamp((u - 3.6) / 2.6))))
        text(L, "0", CX - 210, 1210, I(300, 250), WH, kb); text(L, str(n), CX + 210, 1210, I(300, 250), RED, kb)
        L.d.line((CX, 1120, CX, 1300), fill=A(DIM, kb), width=2)
        text(L, "Lula", CX - 210, 1365, I(500, 34), MUT, kb); text(L, "Flávio", CX + 210, 1365, I(500, 34), MUT, kb)
    elif t < T4:
        u = t - T3; eyebrow(L, "DAS FALAS CHECADAS DE CADA UM", 400, MUT, ent(u))
        put(L, av("L", 84), CX - 215, 520, ent(u, 0.1)); put(L, av("F", 84), CX + 215, 520, ent(u, 0.2))
        ring(L, CX - 215, 760, 150, 58 / 63, GREEN, u - 0.4, ent(u, 0.3)); ring(L, CX + 215, 760, 150, 54 / 103, RED, u - 0.6, ent(u, 0.4))
        text(L, "fato", CX - 215, 960, I(600, 30), GREEN, ent(u, 0.5)); text(L, "falso", CX + 215, 960, I(600, 30), RED, ent(u, 0.6))
        para(L, "Mais da metade das falas checadas de Flávio foi classificada como falsa.", 1110, I(500, 42), WH, ent(u, 2.0), 800)
        text(L, "Lula: nenhuma falsa.", CX, 1265, I(700, 44), GREEN, ent(u, 3.0))
    elif t < T5:
        i = min(3, int((t - T4) / PD)); u = t - T4 - i * PD; cat, said, found = POINTS[i]
        eyebrow(L, "PONTOS CRÍTICOS", 400, MUT, 1.0 if i else ent(u)); text(L, f"{i + 1}/4", L1, 400, I(600, 26), DIM, ent(u), "rm")
        put(L, av("F", 64), L0 + 32, 520, ent(u)); text(L, "Flávio", L0 + 80, 507, I(700, 32), WH, ent(u), "lm")
        text(L, cat, L0 + 80, 542, I(600, 22), RED, ent(u), "lm", track=4)
        para(L, said, 660, I(600, 50), WH, ent(u, 0.2), 850, 1.3, x=L0)
        trace(L, L0, L1, 960, t, "spike", RED, ent(u, 0.35), 0.75, spike_at=T4 + i * PD + STAMP_AT - 0.5)
        falso(L, CX, 960, u - STAMP_AT)
        kf = ent(u, FOUND_AT)
        if kf > 0:
            eyebrow(L, "O QUE A CHECAGEM ENCONTROU", 1110, GREEN, kf, x=L0 + 30)
            y2 = para(L, found, 1175, I(400, 42), WH, kf, 820, 1.35, x=L0 + 30)
            L.d.line((L0, 1092, L0, y2 - 18), fill=A(GREEN, kf), width=4)
    elif t < T6:
        u = t - T5; eyebrow(L, "E O LULA?", 400, MUT, ent(u))
        put(L, av("L", 92), L0 + 46, 530, ent(u, 0.1)); trace(L, L0 + 120, L1, 530, t, "calm", GREEN, ent(u, 0.25))
        text(L, "0 falsas  ·  5 “não é bem assim”", CX, 680, I(600, 44), WH, ent(u, 0.5))
        for j, (s1, s2, t0) in enumerate((("Disse que o túnel Santos-Guarujá tem financiamento do BNDES.", "O financiamento formalizado foi do Banco do Brasil.", 1.3),
                                          ("Falou em 5.600 creches paradas.", "O número inclui outros tipos de obra da educação.", 3.8))):
            kk = ent(u, t0); y = 800 + j * 300
            eyebrow(L, "NÃO É BEM ASSIM", y, AMBER, kk, x=L0)
            yy_ = para(L, s1, y + 60, I(600, 40), WH, kk, 850, x=L0)
            para(L, s2, yy_ + 6, I(400, 36), MUT, ent(u, t0 + 0.7), 850, x=L0)
    else:
        u = t - T6; eyebrow(L, "SOBRE ESTA CHECAGEM", 400, MUT, ent(u))
        y = para(L, "O placar é do site checagemaovivo.org, feito com inteligência artificial durante a transmissão.", 520, I(500, 42), WH, ent(u, 0.2), 820)
        y = para(L, "O próprio site avisa: as análises são preliminares e podem conter erros.", y + 40, I(400, 38), MUT, ent(u, 0.8), 820)
        y = para(L, "A Agência Lupa também checou: Flávio fez acusações falsas e já desmentidas; Lula repetiu um erro sobre o PIB.", y + 40, I(400, 38), MUT, ent(u, 1.5), 820)
        kk = ent(u, 2.3); L.d.line((CX - 60, y + 70, CX + 60, y + 70), fill=A(DIM, kk), width=2)
        text(L, "2º turno  ·  domingo, 25/10", CX, y + 140, I(700, 50), WH, kk)
        text(L, "Fotos: Ricardo Stuckert/PR e Agência Senado (Wikimedia Commons)", CX, 1560, I(400, 20), DIM, ent(u, 2.6))
    a0, b0 = scene_bounds(t); ko = 1 - eio(clamp((t - (b0 - 0.3)) / 0.3)) if b0 < EDIT_END else 1.0
    ki = eo(clamp((t - a0) / 0.45)); dy = int(OY + 40 * (1 - ki) - 30 * (1 - ko))
    base.alpha_composite(R.fade(lay, ko), (0, dy)); fr = base
    R.BAR.draw_bar(fr, clamp(t / END_IN), "canal", eo((t - 0.2) / 0.6), clamp((t - T6) / 0.4) if t > T6 else 0.0, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(fr, t)
    if t >= END_IN: fr.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return fr.convert("RGB")
# --- abertura dele (carro, luz do dia): "E bora ver quem mentiu no debate ontem." ---
import cor_fla
IA, IB = 0.15, 2.95; TI = IB - IA; XF = 0.3
_in = {}
def intro_frame(x):
    if not _in:
        p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{IA}", "-t", f"{TI + 0.1}", "-i", f"{V}/intro_raw.mp4", "-vf", "fps=30", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        n = len(p) // (W * H * 3); _in["a"] = np.frombuffer(p[:n * W * H * 3], np.uint8).reshape(n, H, W, 3)
    a = _in["a"]; return cor_fla.fix(a[int(clamp(x * FPS, 0, len(a) - 1))])
IWORDS = [("E", 0.19), ("bora", 0.35), ("ver", 0.75), ("quem", 0.98), ("mentiu", 1.25), ("no", 1.62), ("debate", 1.78), ("ontem.", 2.15)]
def intro_at(t):
    z = 1.0 + 0.05 * eio(clamp(t / TI)); img = intro_frame(t)
    M = np.float32([[z, 0, CX * (1 - z)], [0, z, 760 * (1 - z)]]); import cv2; img = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    fr = Image.fromarray(img).convert("RGBA")
    g = np.zeros((620, W, 4), np.uint8); g[..., 3] = np.linspace(0, 210, 620)[:, None].astype(np.uint8); fr.alpha_composite(Image.fromarray(g), (0, H - 620))
    L = C(fr); f1 = I(600, 60); f2 = I(800, 60)
    lines = [IWORDS[:4], IWORDS[4:]]
    for li, ws in enumerate(lines):
        y = 1450 + li * 80; ff = lambda w: f2 if w in ("mentiu", "debate") else f1; sp = f1.getlength(" ")
        tot = sum(ff(w).getlength(w) for w, _ in ws) + sp * (len(ws) - 1); x = CX - tot / 2
        for w, t0 in ws:
            a = clamp((t - t0 + 0.08) / 0.15); col = RED if w == "mentiu" else WH
            text(L, w, x, y + 12 * (1 - a), ff(w), col, a, "lm"); x += ff(w).getlength(w) + sp
    R.BAR.draw_bar(fr, 0.0, "canal", eo((t - 0.2) / 0.6), 0.0, 0.0); R.draw_banners(fr, t)
    return fr
def frame_at(t):
    if t < TI - XF: return intro_at(t).convert("RGB")
    if t < TI:
        k = eio((t - (TI - XF)) / XF); return Image.blend(intro_at(t).convert("RGB"), gfx_at(0.0), k)
    return gfx_at(t - TI)
def capa(out):
    base = Image.fromarray(BG).convert("RGBA"); L = C(base)
    text(L, "Conteúdo de opinião  ·  Checagem: checagemaovivo.org (IA)", CX, 190, I(400, 23), MUT)
    eyebrow(L, "DEBATE DA GLOBO  ·  23/10", 330)
    text(L, "Quem teve mais", CX, 450, I(300, 104), WH); text(L, "falas falsas?", CX, 575, I(800, 116), RED)
    put(L, av("L", 280), CX - 215, 860); put(L, av("F", 280), CX + 215, 860)
    text(L, "Lula", CX - 215, 1040, I(600, 40), WH); text(L, "Flávio", CX + 215, 1040, I(600, 40), WH)
    text(L, "0", CX - 215, 1260, I(300, 300), WH); text(L, "54", CX + 215, 1260, I(300, 300), RED); L.d.line((CX, 1150, CX, 1370), fill=A(DIM, 1), width=2)
    falso(L, CX + 215, 1470, 1.0)
    R.BAR.draw_bar(base, 0.0, "canal"); base.alpha_composite(R.top, (R.HDX, 0)); base.convert("RGB").save(out, quality=95)
SR = 48000
def tone(f, dur, amp=1.0, decay=None):
    tt = np.arange(int(dur * SR)) / SR; env = np.minimum(1, tt / 0.003) * (np.exp(-tt / decay) if decay else np.minimum(1, (dur - tt) / 0.02))
    return np.stack([np.sin(2 * np.pi * f * tt) * env * amp] * 2, 1).astype(np.float32)
def mix(*xs):
    n = max(len(x) for x in xs); o = np.zeros((n, 2), np.float32)
    for x in xs: o[:len(x)] += x
    return o
def blip(): return tone(1400, 0.06) * 0.6
def tick(): return tone(3000, 0.015)
def soft_hit(): return mix(tone(90, 0.5, 1.0, 0.12), tone(180, 0.3, 0.4, 0.06))
def chime(): return mix(tone(1046, 0.6, 0.5, 0.18), tone(1568, 0.6, 0.3, 0.14))
def err(): return mix(tone(220, 0.22, 0.7), tone(233, 0.22, 0.5))
def main():
    if MODE == "capa": capa(OUTFILE); return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(x).resize((360, 640), Image.LANCZOS) for x in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    vout = f"{V}/video2.mp4"
    if not (os.environ.get("REUSE") and os.path.exists(vout)):
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
        for k in range(int(round((TOTAL + TI) * FPS))): enc.stdin.write(frame_at(k / FPS).tobytes())
        enc.stdin.close(); enc.wait()
    ev = [(0.6 + 0.8 * j, blip(), 0.12) for j in range(4)] + [(1.1, sfx.whoosh(0.35), 0.15), (1.35, soft_hit(), 0.35)]
    for tb in (T2, T3, T4, T4 + PD, T4 + 2 * PD, T4 + 3 * PD, T5, T6): ev += [(tb - 0.1, sfx.whoosh(0.4), 0.14)]
    last = -1
    for k in range(int(3.0 * FPS)):
        u = k / FPS; n = int(round(54 * R.ease_out(clamp(u / 2.6))))
        if n != last and n % 2 == 0: ev += [(T2 + 3.6 + u, tick(), 0.22)]
        last = n
    ev += [(T2 + 6.2, soft_hit(), 0.45), (T2 + 6.2, err(), 0.18), (T3 + 1.7, chime(), 0.22)]
    for i in range(4):
        b = T4 + i * PD; ev += [(b + STAMP_AT, soft_hit(), 0.5), (b + STAMP_AT, err(), 0.2), (b + FOUND_AT, chime(), 0.18)]
    ev += [(T5 + 1.3, blip(), 0.15), (T5 + 3.8, blip(), 0.15), (T6 + 2.3, chime(), 0.2), (END_IN - 0.3, sfx.whoosh(0.6), 0.2)]
    ev = [(e[0] + TI, *e[1:]) for e in ev] + [(TI - 0.2, sfx.whoosh(0.45), 0.2)]; TT = TOTAL + TI
    sfx.build([e for e in ev if 0 <= e[0] < TT - 0.5], TT, f"{V}/sfx2.wav")
    n = int(TT * SR); bed = R.readw(f"{S}/v52/tense.wav"); o = int(TI * SR); L_ = min(len(bed), n - o); tl = np.arange(L_) / SR
    g = 0.30 * np.clip(tl / 0.8, 0, 1) * np.clip(1 - (tl - (TOTAL - 1.8)) / 1.6, 0, 1); sg = np.zeros((n, 2), np.float32); sg[o:o + L_] = bed[:L_] * g[:, None]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{IA}", "-t", f"{TI}", "-i", f"{V}/intro_raw.mp4", "-ar", "48000", "-ac", "2", f"{V}/intro48.wav"], check=True)
    vo = R.readw(f"{V}/intro48.wav"); fl = int(0.15 * SR); vo[-fl:] *= np.linspace(1, 0, fl)[:, None]
    pk = np.sqrt((vo ** 2).mean()); vo *= 0.12 / max(pk, 1e-6); sg[:len(vo)] += vo[:n]
    R.writew(f"{V}/song2.wav", sg)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/sfx2.wav", "-i", f"{V}/song2.wav", "-filter_complex",
                    f"[1:a][2:a]amix=inputs=2:normalize=0:duration=longest,atrim=0:{TT:.2f},alimiter=limit=0.8:level=false[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
