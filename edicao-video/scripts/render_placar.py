"""Placar da checagem do debate da Globo (23/10/2026), versão do canal: fundo azul-marinho com grade, linhas de "detector" (calma para o Lula,
picos para o Flávio), barras que crescem, números contando, ponteiros, carimbo FALSO e o que a checagem encontrou. Fonte sempre na tela:
checagemaovivo.org (IA, preliminar). Texto: "falas classificadas como falsas", nunca "mentiu"."""
import sys, math, subprocess, importlib.util, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
sys.path.insert(0, f"{S}/work")
import sfx
W, H, FPS, CX = R.W, R.H, R.FPS, R.CX; clamp = R.clamp; eo = R.ease_out; ei = R.ease_in; bo = R.back_out
V = f"{S}/v61"; MF = R.MF; BIGF = R.BIGF
GREEN = (22, 150, 92); RED = (226, 52, 52); ORANGE = (236, 150, 30); GRAY = (130, 138, 150); WHITE = (255, 255, 255); GOLD = R.GOLD; GOLD_L = R.GOLD_L
L0, L1 = 130, 1035                                                   # área útil à direita da barra lateral
BG = np.clip(R.NAVYBG, 0, 255).astype(np.uint8).copy()
for x in range(L0 % 60, W, 60): BG[:, x] = (BG[:, x].astype(np.int16) + 10).clip(0, 255)
for y in range(0, H, 60): BG[y] = (BG[y].astype(np.int16) + 10).clip(0, 255)
def avatar(path, size, focus=(0.5, 0.33), zoom=0.62):
    im = Image.open(path).convert("RGB"); s = int(min(im.size) * zoom); cx, cy = int(im.width * focus[0]), int(im.height * focus[1])
    im = im.crop((cx - s // 2, max(0, cy - s // 2), cx + s // 2, max(0, cy - s // 2) + s)).resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size, size), 0); ImageDraw.Draw(m).ellipse((0, 0, size - 1, size - 1), fill=255)
    out = Image.new("RGBA", (size + 12, size + 12), (0, 0, 0, 0)); ImageDraw.Draw(out).ellipse((0, 0, size + 11, size + 11), fill=GOLD + (255,))
    im = im.convert("RGBA"); im.putalpha(m); out.alpha_composite(im, (6, 6)); return out
AV = {k: {} for k in "LF"}
def av(k, size):
    if size not in AV[k]: AV[k][size] = avatar(f"{V}/dl/lula.jpg", size, (0.47, 0.30), 0.58) if k == "L" else avatar(f"{V}/dl/flavio.jpg", size, (0.57, 0.27), 0.5)
    return AV[k][size]
def put(fr, im, cx, cy, k=1.0, a=1.0):
    if k <= 0.01 or a <= 0.01: return
    if abs(k - 1) > 0.01: im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.BICUBIC)
    fr.alpha_composite(R.fade(im, a), (int(cx - im.width / 2), int(cy - im.height / 2)))
def text(fr, s, x, y, f, col=WHITE, a=1.0, anchor="mm"):
    if a <= 0.01: return
    lay = Image.new("RGBA", fr.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).text((x, y), s, font=f, fill=col + (int(255 * a),), anchor=anchor); fr.alpha_composite(lay)
def wrap(s, f, maxw):
    out, cur = [], ""
    for w in s.split():
        t = (cur + " " + w).strip()
        if f.getlength(t) <= maxw: cur = t
        else: out.append(cur); cur = w
    return out + [cur]
def para(fr, s, y, f, col=WHITE, a=1.0, maxw=860, lh=1.3, x=None):
    for i, l in enumerate(wrap(s, f, maxw)): text(fr, l, CX if x is None else x, y + i * f.size * lh, f, col, a, "mm" if x is None else "lm")
    return y + len(wrap(s, f, maxw)) * f.size * lh
def trace(fr, x0, x1, y, t, kind, col, amp=1.0, a=1.0, spike_at=None):
    """linha do detector: calma (senoide pequena) ou nervosa (picos); o ponto na ponta pulsa"""
    if a <= 0.01: return
    lay = Image.new("RGBA", fr.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); pts = []; n = 160
    for i in range(n + 1):
        u = i / n; xx = x0 + (x1 - x0) * u; ph = u * 9 - t * 3.2
        if kind == "calm": v = 7 * math.sin(ph * 2.1) + 3 * math.sin(ph * 5.3)
        else:
            v = 10 * math.sin(ph * 3.1) + 6 * math.sin(ph * 7.7)
            r = (math.sin(ph * 1.7) * 43758.5453) % 1
            if r > 0.78: v += (r - 0.78) * 420 * (1 if int(ph * 3) % 2 else -1)
            if spike_at is not None:
                q = clamp((t - spike_at) / 0.9); env = math.exp(-((u - 0.55) / 0.18) ** 2) * math.sin(q * math.pi)
                v += env * 120 * math.sin(u * 140)
        pts.append((xx, y + v * amp))
    d.line(pts, fill=col + (int(235 * a),), width=5, joint="curve")
    pr = 13 + 4 * math.sin(t * 8); ex, ey = pts[-1]; d.ellipse((ex - pr, ey - pr, ex + pr, ey + pr), fill=col + (int(255 * a),)); d.ellipse((ex - pr - 8, ey - pr - 8, ex + pr + 8, ey + pr + 8), outline=col + (int(120 * a),), width=3)
    fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(0.6)))
def chip(fr, s, cx, cy, fill, a=1.0, size=26, tcol=WHITE):
    if a <= 0.01: return
    f = MF("ExtraBold", size); w = f.getlength(s) + 34; h = size + 22
    lay = Image.new("RGBA", fr.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 10, fill=fill + (int(255 * a),)); d.text((cx, cy + 1), s, font=f, fill=tcol + (int(255 * a),), anchor="mm"); fr.alpha_composite(lay)
    return w
_st = None
def stamp(fr, cx, cy, u):
    global _st
    if u < 0: return
    if _st is None:
        f = BIGF(120); w = int(f.getlength("FALSO") + 70); im = Image.new("RGBA", (w, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((6, 6, w - 7, 183), 18, fill=(255, 255, 255, 235), outline=RED + (255,), width=10); d.text((w / 2, 96), "FALSO", font=f, fill=RED + (255,), anchor="mm")
        _st = im.rotate(-8, resample=Image.BICUBIC, expand=True)
    k = 1.7 - 0.7 * eo(u / 0.16); put(fr, _st, cx, cy, k * 0.85, clamp(u / 0.08))
def header(fr, title, sub, k, tag=None):
    fs = 50
    while MF("ExtraBold", fs).getlength(title) > 820: fs -= 2
    text(fr, title, CX, 300, MF("ExtraBold", fs), GOLD_L, k)
    if sub: text(fr, sub, CX, 360, MF("Medium", 32), (190, 205, 222), k)
    if tag: chip(fr, tag, L1 - 40, 300, (30, 60, 96), k, 24)
def bar(fr, x0, y, w, h, segs_, total, k):
    lay = Image.new("RGBA", fr.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); d.rounded_rectangle((x0, y, x0 + w, y + h), 10, fill=(255, 255, 255, 28))
    acc = 0; fn = MF("ExtraBold", 38)
    for n, col in segs_:
        ww = w * n / total * k; xa = x0 + w * acc / total * k
        if ww > 1: d.rectangle((xa, y, xa + ww, y + h), fill=col + (255,))
        if ww > 50: d.text((xa + ww / 2, y + h / 2 + 1), str(n), font=fn, fill=WHITE + (255,), anchor="mm")
        acc += n
    fr.alpha_composite(lay)
def gauge(fr, cx, cy, r, pct, col, u, label):
    lay = Image.new("RGBA", fr.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay); box = (cx - r, cy - r, cx + r, cy + r)
    d.arc(box, 180, 360, fill=(255, 255, 255, 40), width=30); p = pct * eo(u / 1.2)
    if p > 0.005: d.arc(box, 180, 180 + 180 * p, fill=col + (255,), width=30)
    ang = math.pi * (1 + p); d.line((cx, cy, cx + (r - 40) * math.cos(ang), cy + (r - 40) * math.sin(ang)), fill=WHITE + (255,), width=8); d.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=WHITE + (255,))
    fr.alpha_composite(lay); text(fr, f"{int(round(pct * 100 * eo(u / 1.2)))}%", cx, cy + 80, BIGF(96), col); text(fr, label, cx, cy + 150, MF("ExtraBold", 30), (200, 212, 228))
# --- roteiro (s) ---
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
OY = 120; PD = (T5 - T4) / 4; STAMP_AT = 1.5; FOUND_AT = 2.1
def frame_at(t):
    base = Image.fromarray(BG).convert("RGBA"); fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    chip(base, "CONTEÚDO DE OPINIÃO · CHECAGEM: CHECAGEMAOVIVO.ORG (IA)", CX, 205, (2, 10, 22), clamp(t / 0.4), 21, (225, 232, 240))
    if t < T2:                                                       # 1. abertura
        u = t; k = eo(u / 0.5)
        text(fr, "DEBATE DA GLOBO · 23/10/2026", CX, 300, MF("ExtraBold", 34), (190, 205, 222), k)
        put(fr, av("L", 200), L0 + 110, 560, bo(clamp((u - 0.2) / 0.4))); trace(fr, L0 + 240, L1 - 30, 560, t, "calm", GREEN, a=clamp((u - 0.4) / 0.3))
        chip(fr, "LULA", L0 + 110, 690, GREEN, clamp((u - 0.4) / 0.3), 24)
        put(fr, av("F", 200), L0 + 110, 880, bo(clamp((u - 0.5) / 0.4))); trace(fr, L0 + 240, L1 - 30, 880, t, "spike", RED, a=clamp((u - 0.7) / 0.3))
        chip(fr, "FLÁVIO", L0 + 110, 1010, RED, clamp((u - 0.7) / 0.3), 24)
        kk = bo(clamp((u - 1.2) / 0.45), 1.4)
        text(fr, "QUEM TEVE MAIS", CX, 1220, BIGF(int(118 * max(kk, 0.05))), WHITE, clamp((u - 1.2) / 0.2))
        text(fr, "FALAS FALSAS?", CX, 1360, BIGF(int(132 * max(kk, 0.05))), GOLD_L, clamp((u - 1.3) / 0.2))
        a_out = 1 - clamp((u - (T2 - 0.25)) / 0.25)
        if a_out < 1: fr = R.fade(fr, a_out)
    elif t < T3:                                                     # 2. placar
        u = t - T2; header(fr, "PLACAR DA CHECAGEM", "167 falas checadas no debate", eo(u / 0.4))
        for j, (k_, nm, tot, sg, y) in enumerate((("L", "LULA", 63, [(58, GREEN), (5, ORANGE)], 520), ("F", "FLÁVIO", 103, [(8, GREEN), (54, RED), (37, ORANGE), (4, GRAY)], 760))):
            uu = u - 0.3 - j * 0.5; put(fr, av(k_, 170), L0 + 95, y + 30, bo(clamp(uu / 0.4)))
            text(fr, f"{nm}  ·  {tot} falas", L0 + 205, y - 25, MF("ExtraBold", 40), WHITE, clamp(uu / 0.3), "lm")
            bar(fr, L0 + 205, y + 15, L1 - L0 - 215, 74, sg, tot, eo((uu - 0.3) / 1.1))
        ka = clamp((u - 2.6) / 0.3); x = L0 + 30
        for s_, c_ in (("FATO", GREEN), ("FALSO", RED), ("NÃO É BEM ASSIM", ORANGE), ("INCONCLUSIVO", GRAY)):
            w_ = MF("ExtraBold", 24).getlength(s_) + 34; chip(fr, s_, x + w_ / 2, 930, c_, ka, 24); x += w_ + 16
        kb = clamp((u - 3.4) / 0.3); text(fr, "FALAS CLASSIFICADAS COMO FALSAS", CX, 1080, MF("ExtraBold", 36), RED, kb)
        n = int(round(54 * eo(clamp((u - 3.8) / 2.6)))); kn = bo(clamp((u - 3.6) / 0.35))
        text(fr, "0", CX - 230, 1250, BIGF(int(230 * max(kn, .05))), WHITE, kb); text(fr, "x", CX, 1250, MF("ExtraBold", 70), (150, 165, 185), kb)
        text(fr, str(n), CX + 230, 1250, BIGF(int(230 * max(kn, .05)) + (16 if 0 < u - 6.4 < 0.25 else 0)), RED, kb)
        text(fr, "Lula", CX - 230, 1415, MF("ExtraBold", 40), WHITE, kb); text(fr, "Flávio", CX + 230, 1415, MF("ExtraBold", 40), WHITE, kb)
    elif t < T4:                                                     # 3. ponteiros
        u = t - T3; header(fr, "DAS FALAS CHECADAS DE CADA UM", None, eo(u / 0.4))
        put(fr, av("L", 150), CX - 220, 480, bo(clamp(u / 0.4))); put(fr, av("F", 150), CX + 220, 480, bo(clamp((u - 0.2) / 0.4)))
        gauge(fr, CX - 220, 760, 180, 58 / 63, GREEN, u - 0.4, "FATO"); gauge(fr, CX + 220, 760, 180, 54 / 103, RED, u - 0.6, "FALSO")
        para(fr, "Mais da metade das falas checadas de Flávio foi classificada como falsa.", 1080, MF("Bold", 42), WHITE, clamp((u - 2.0) / 0.4), 820)
        text(fr, "Lula: nenhuma falsa.", CX, 1250, MF("ExtraBold", 50), (70, 210, 140), clamp((u - 3.0) / 0.4))
    elif t < T5:                                                     # 4. pontos críticos
        i = min(3, int((t - T4) / PD)); u = t - T4 - i * PD; cat, said, found = POINTS[i]; k = eo(u / 0.35)
        header(fr, "PONTOS CRÍTICOS", None, 1.0 if i else k, f"{i + 1}/4")
        put(fr, av("F", 120), L0 + 75, 470, k); chip(fr, cat, L0 + 160 + (MF("ExtraBold", 24).getlength(cat) + 34) / 2, 440, RED, k, 24)
        text(fr, "FLÁVIO", L0 + 160, 500, MF("ExtraBold", 34), WHITE, k, "lm")
        para(fr, said, 640, MF("Bold", 46), WHITE, clamp((u - 0.2) / 0.3), 840)
        trace(fr, L0 + 20, L1 - 40, 900, t, "spike", RED, 0.6, clamp((u - 0.4) / 0.3), spike_at=T4 + i * PD + STAMP_AT - 0.5)
        stamp(fr, CX, 900, u - STAMP_AT)
        kf = eo((u - FOUND_AT) / 0.35)
        if kf > 0:
            text(fr, "O QUE A CHECAGEM ENCONTROU", CX, 1080, MF("ExtraBold", 28), (70, 210, 140), kf)
            lines = wrap(found, MF("SemiBold", 40), 780); hh = len(lines) * 52 + 60
            lay = Image.new("RGBA", fr.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).rounded_rectangle((L0 + 20, 1120, L1 - 20, 1120 + hh), 18, fill=(255, 255, 255, int(235 * kf)), outline=GREEN + (int(255 * kf),), width=4)
            fr.alpha_composite(lay)
            for j, l in enumerate(lines): text(fr, l, CX, 1150 + 26 + j * 52, MF("SemiBold", 40), (14, 28, 44), kf)
    elif t < T6:                                                     # 5. e o Lula?
        u = t - T5; header(fr, "E O LULA?", None, eo(u / 0.4))
        put(fr, av("L", 150), L0 + 95, 500, bo(clamp(u / 0.4))); trace(fr, L0 + 200, L1 - 30, 500, t, "calm", GREEN, a=clamp((u - 0.3) / 0.3))
        para(fr, "0 falsas e 5 “não é bem assim”, como:", 680, MF("ExtraBold", 44), WHITE, clamp((u - 0.6) / 0.3))
        for j, (s1, s2, t0) in enumerate((("Disse que o túnel Santos-Guarujá tem financiamento do BNDES.", "O financiamento formalizado foi do Banco do Brasil.", 1.4),
                                          ("Falou em 5.600 creches paradas.", "O número inclui outros tipos de obra da educação.", 4.0))):
            kk = eo((u - t0) / 0.35); y = 820 + j * 330
            chip(fr, "NÃO É BEM ASSIM", L0 + 30 + (MF("ExtraBold", 24).getlength("NÃO É BEM ASSIM") + 34) / 2, y, ORANGE, kk, 24)
            yy = para(fr, s1, y + 70, MF("Bold", 40), WHITE, kk, 860, x=L0 + 30)
            para(fr, s2, yy + 10, MF("Medium", 36), (190, 205, 222), eo((u - t0 - 0.8) / 0.35), 860, x=L0 + 30)
    else:                                                            # 6. sobre a checagem
        u = t - T6; header(fr, "SOBRE ESTA CHECAGEM", None, eo(u / 0.4))
        y = para(fr, "O placar é do site checagemaovivo.org, feito com inteligência artificial durante a transmissão.", 470, MF("Bold", 42), WHITE, clamp((u - 0.3) / 0.3), 840)
        y = para(fr, "O próprio site avisa: as análises são preliminares e podem conter erros.", y + 40, MF("Medium", 40), (190, 205, 222), clamp((u - 0.9) / 0.3), 840)
        y = para(fr, "A Agência Lupa também checou: Flávio fez acusações falsas e já desmentidas; Lula repetiu um erro sobre o PIB.", y + 50, MF("Medium", 38), (190, 205, 222), clamp((u - 1.6) / 0.3), 840)
        kk = bo(clamp((u - 2.4) / 0.4)); chip(fr, "2º TURNO: DOMINGO, 25/10", CX, y + 130, (2, 10, 22), kk, 44, GOLD_L)
        R.credit(fr, "Fotos: Ricardo Stuckert/PR e Agência Senado (Wikimedia Commons)", CX, 1580, clamp((u - 2.6) / 0.4), anchor="mm")
    base.alpha_composite(fr, (0, OY)); fr = base
    R.BAR.draw_bar(fr, clamp(t / END_IN), "canal", eo((t - 0.2) / 0.6), clamp((t - T6) / 0.4) if t > T6 else 0.0, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(fr, t)
    for tb in (T2, T3, T4, T4 + PD, T4 + 2 * PD, T4 + 3 * PD, T5, T6):
        if abs(t - tb) < 0.07: fr = Image.blend(fr, Image.new("RGBA", fr.size, (255, 255, 255, 255)), (1 - abs(t - tb) / 0.07) * 0.25)
    if t >= END_IN: fr.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return fr.convert("RGB")
# --- sons próprios ---
SR = 48000
def beep(f=1000, dur=0.09, sq=False):
    tt = np.arange(int(dur * SR)) / SR; w = np.sign(np.sin(2 * np.pi * f * tt)) * 0.5 if sq else np.sin(2 * np.pi * f * tt)
    env = np.minimum(1, tt / 0.004) * np.minimum(1, (dur - tt) / 0.02); return np.stack([w * env] * 2, 1).astype(np.float32)
def buzz(): a = beep(140, 0.32, True) * 0.6 + beep(70, 0.32, True) * 0.4; return a
def ding(): return beep(1320, 0.18) * 0.6 + beep(1980, 0.18) * 0.25
def tick(): return beep(2400, 0.018)
def capa(out):
    base = Image.fromarray(BG).convert("RGBA"); fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    chip(base, "CONTEÚDO DE OPINIÃO · CHECAGEM: CHECAGEMAOVIVO.ORG (IA)", CX, 205, (2, 10, 22), 1.0, 21, (225, 232, 240))
    text(fr, "DEBATE DA GLOBO · 23/10", CX, 190, MF("ExtraBold", 36), (190, 205, 222))
    text(fr, "QUEM TEVE MAIS", CX, 320, BIGF(126), WHITE); text(fr, "FALAS FALSAS?", CX, 470, BIGF(140), GOLD_L)
    put(fr, av("L", 330), CX - 230, 800); put(fr, av("F", 330), CX + 230, 800)
    chip(fr, "LULA", CX - 230, 990, GREEN, 1.0, 34); chip(fr, "FLÁVIO", CX + 230, 990, RED, 1.0, 34)
    text(fr, "0", CX - 230, 1200, BIGF(280), WHITE); text(fr, "x", CX, 1200, MF("ExtraBold", 80), (150, 165, 185)); text(fr, "54", CX + 230, 1200, BIGF(280), RED)
    stamp(fr, CX + 240, 1420, 1.0)
    base.alpha_composite(fr, (0, 120)); R.BAR.draw_bar(base, 0.0, "canal"); base.alpha_composite(R.top, (R.HDX, 0)); base.convert("RGB").save(out, quality=95)
def main():
    if MODE == "capa": capa(OUTFILE); return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(x).resize((360, 640), Image.LANCZOS) for x in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    vout = f"{V}/video.mp4"
    if not (os.environ.get("REUSE") and os.path.exists(vout)):
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
        for k in range(int(round(TOTAL * FPS))): enc.stdin.write(frame_at(k / FPS).tobytes())
        enc.stdin.close(); enc.wait()
    ev = [(0.0, sfx.whoosh(0.4), 0.25)]
    ev += [(0.5 + 0.9 * j, beep(1000, 0.07), 0.18) for j in range(4)] + [(1.2, sfx.thud(0.4), 0.45), (1.3, sfx.whoosh(0.35), 0.25)]
    for tb in (T2, T3, T4, T5, T6): ev += [(tb - 0.12, sfx.whoosh(0.45), 0.3)]
    ev += [(T2 + 0.6, sfx.barra(1.2), 0.35), (T2 + 1.1, sfx.barra(1.2), 0.35)]
    last = -1
    for k in range(int(4.0 * FPS)):                                  # tique a cada número do contador
        u = k / FPS; n = int(round(54 * R.ease_out(clamp(u / 2.6))))
        if n != last and n % 2 == 0: ev += [(T2 + 3.8 + u, tick(), 0.35)]
        last = n
    ev += [(T2 + 6.4, sfx.thud(0.5), 0.6), (T2 + 6.4, buzz(), 0.35)]
    ev += [(T3 + 0.4, sfx.barra(1.2), 0.3), (T3 + 1.6, ding(), 0.35), (T3 + 1.8, buzz(), 0.3)]
    for i in range(4):
        b = T4 + i * PD; ev += [(b + 0.5 + 0.35 * j, beep(1000, 0.06), 0.15) for j in range(3)]
        ev += [(b + STAMP_AT, buzz(), 0.45), (b + STAMP_AT, sfx.thud(0.4), 0.7), (b + FOUND_AT, ding(), 0.3)]
    ev += [(T5 + 1.4, sfx.click(), 0.5), (T5 + 4.0, sfx.click(), 0.5), (T6 + 2.4, sfx.thud(0.4), 0.5), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.5], TOTAL, f"{V}/sfx.wav")
    n = int(TOTAL * SR); bed = R.readw(f"{S}/v52/tense.wav"); L = min(len(bed), n); tl = np.arange(L) / SR
    g = 0.34 * np.clip(tl / 0.8, 0, 1) * np.clip(1 - (tl - (TOTAL - 1.8)) / 1.6, 0, 1); sg = np.zeros((n, 2), np.float32); sg[:L] = bed[:L] * g[:, None]
    R.writew(f"{V}/song.wav", sg)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    f"[1:a]volume=1.0[s];[2:a]volume=1.0[m];[s][m]amix=inputs=2:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.8:level=false[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
