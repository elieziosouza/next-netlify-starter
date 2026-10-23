"""Milei serve para o Brasil? Ele gravou no carro (63 s). Edição dinâmica: pausas cortadas com zoom alternado, palavras gigantes ATRÁS dele
(recorte U2Net na frente), tela dividida com gráficos animados (inflação caindo, pobreza/desemprego/empresas subindo), ícones e emojis pulando,
manchete do Nexo. Cor: sombras sem magenta + abertura dos médios (cor_milei) e o grading cinema_pele4 do canal.
Números: Indec (inflação 33,4% em 12 meses até set/2026; pobreza 32,3% no 1º sem/2026, era 28,2%; desemprego 7,9% no 2º tri) e Fundar (empresas)."""
import sys, math, subprocess, importlib.util, os, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
sys.path.insert(0, f"{S}/work")
import sfx, grading, cor_milei
from segment_person import PersonSeg
BLUE = (14, 62, 120); PAPER = (247, 244, 236); INK = (22, 26, 34); GREEN = (40, 170, 90)
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; ease_out = R.ease_out; ease_in = R.ease_in; ease_io = R.ease_io
V = f"{S}/v52"; ME = f"{V}/me.mp4"
GRADE = grading.Fast(None, f"{S}/grade/lut_cinema_pele4.npy", 0.08, 6)
SEG = PersonSeg("/root/.cache/edicao-video/seg/u2net_human_seg.onnx")
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
# pausas medidas no áudio (fala abaixo de -31 dB por 0,2 s ou mais); corta o miolo e deixa 0,09 s de cada lado
GAPS = [(2.68, 3.26), (5.22, 5.8), (9.3, 9.7), (11.96, 12.4), (14.34, 14.94), (19.1, 19.72), (22.12, 22.74), (24.92, 25.26), (26.58, 26.94),
        (29.14, 29.52), (32.38, 32.76), (36.72, 37.26), (39.2, 40.14), (42.36, 43.0), (45.02, 45.64), (47.48, 48.0), (50.5, 50.92), (52.46, 52.96),
        (54.12, 54.74), (57.3, 58.3)]
PAD = 0.09
KEEP = []; a0 = 0.45
for g0, g1 in GAPS: KEEP.append((a0, g0 + PAD)); a0 = g1 - PAD
KEEP.append((a0, 61.45))
OFF = []; acc = 0.0
for a, b in KEEP: OFF.append(acc); acc += b - a
EDIT_END = acc; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = EDIT_END; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
def src_of(t):
    for i, (a, b) in enumerate(KEEP):
        if t < OFF[i] + (b - a) or i == len(KEEP) - 1: return a + t - OFF[i], i
def out_of(x):
    for i, (a, b) in enumerate(KEEP):
        if x <= b or i == len(KEEP) - 1: return OFF[i] + max(0.0, x - a)
SPLIT = [(5.6, 12.1), (14.85, 22.3), (26.7, 39.3)]                     # trechos de tela dividida (tempo do vídeo original)
def split_of(x):
    for k, (a, b) in enumerate(SPLIT):
        if a <= x < b: return k
    return None
# legendas (o que ele falou de fato) e tempos do original
ME_CAPS = [("VOCÊ QUER A MOTOSSERRA", 0.54, 1.75), ("DO MILEI AQUI NO BRASIL?", 1.75, 2.76), ("ENTÃO OLHA PRIMEIRO", 3.3, 4.2), ("O QUE ELA FEZ NA ARGENTINA.", 4.2, 5.25),
           ("A CAMPANHA DO FLÁVIO BOLSONARO", 5.82, 7.5), ("CITA O MODELO DO MILEI", 7.5, 8.5), ("COMO INSPIRAÇÃO.", 8.5, 9.3), ("CORTE PESADO DE GASTOS", 9.7, 10.9),
           ("E ESTADO MENOR.", 10.9, 11.96), ("E É JUSTO DIZER:", 12.4, 13.3), ("A INFLAÇÃO CAIU.", 13.3, 14.37), ("ESTAVA PERTO DE 290%", 15.0, 16.9),
           ("AO ANO E HOJE ESTÁ EM 33%,", 16.9, 19.1), ("SEGUNDO O INDEC,", 19.72, 20.9), ("QUE É O IBGE DE LÁ.", 20.9, 22.12), ("MAS OLHA A OUTRA", 22.74, 23.8),
           ("PONTA DA CONTA.", 23.8, 24.92), ("A POBREZA VOLTOU A SUBIR,", 25.26, 26.58), ("ESTÁ EM 32% DA POPULAÇÃO.", 26.94, 29.14), ("O DESEMPREGO", 29.52, 30.6),
           ("SUBIU PARA 7,9%", 30.6, 32.38), ("E MAIS DE 30 MIL EMPRESAS", 32.76, 34.6), ("FECHARAM AS PORTAS", 34.6, 35.6), ("DESDE QUE ELE ASSUMIU,", 35.6, 36.72),
           ("SEGUNDO O LEVANTAMENTO DA FUNDAR.", 37.26, 39.2), ("NA MINHA OPINIÃO,", 40.14, 41.3), ("A PERGUNTA É UMA SÓ:", 41.3, 42.36), ("QUEM PAGA A CONTA", 43.0, 44.1),
           ("DA MOTOSSERRA?", 44.1, 45.02), ("LÁ, QUEM PAGOU", 45.64, 46.5), ("FOI O TRABALHADOR,", 46.5, 47.48), ("O APOSENTADO", 48.0, 49.1), ("E O PEQUENO EMPRESÁRIO.", 49.1, 50.5),
           ("O BRASIL NÃO É A ARGENTINA", 50.92, 52.46), ("E NÃO PRECISA VIRAR.", 52.96, 54.12), ("DOMINGO, PENSA NO SEU BOLSO", 54.74, 56.3), ("ANTES DE VOTAR.", 56.3, 57.3),
           ("COMENTA AQUI O QUE VOCÊ", 58.3, 59.9), ("ACHA DA MOTOSSERRA.", 59.9, 61.38)]
HOT = {"MOTOSSERRA", "MOTOSSERRA?", "MOTOSSERRA.", "MILEI", "ARGENTINA.", "INFLAÇÃO", "CAIU.", "290%", "33%,", "INDEC,", "POBREZA", "32%", "7,9%", "30", "MIL",
       "FECHARAM", "PAGA", "TRABALHADOR,", "APOSENTADO", "EMPRESÁRIO.", "BOLSO", "VOTAR.", "BRASIL", "CORTE", "GASTOS", "MENOR."}
CAPS = []
for txt, a, b in ME_CAPS:
    a2, b2 = out_of(a), out_of(b)
    if b2 - a2 < 0.2: continue
    ws = txt.split(); tot = sum(len(w) + 2 for w in ws); k = 0; ts = []
    for w in ws: ts.append(a2 + (b2 - a2 - 0.08) * k / tot); k += len(w) + 2
    CAPS.append(dict(words=ws, ts=ts, start=a2, end=b2, src="au" if any(w in HOT for w in ws) else "me"))
R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
# palavras gigantes atrás dele (tempo do original): (início, fim, palavra, cor, tremida)
BIG = [(0.55, 2.75, "MOTOSSERRA", R.GOLD_L, True), (12.4, 14.4, "INFLAÇÃO", R.WHITE, False), (22.74, 24.95, "MAS...", R.GOLD_L, True),
       (25.26, 26.6, "POBREZA", R.WHITE, False), (43.0, 47.5, "QUEM PAGA?", R.GOLD_L, True), (50.92, 54.15, "NÃO PRECISA VIRAR", R.WHITE, False),
       (54.74, 57.3, "PENSA NO BOLSO", R.GOLD_L, True), (58.3, 61.45, "COMENTA!", R.WHITE, False)]
# ícones pulando na tela cheia: (início, fim, emoji, x, y, tamanho, rótulo)
ICONS = [(0.9, 2.75, "🪚", 900, 1180, 170, None), (3.3, 5.25, "🇦🇷", 880, 1150, 170, None), (12.9, 14.4, "✅", 890, 1160, 160, None),
         (25.5, 26.6, "📈", 890, 1160, 160, None), (40.3, 42.36, "🤔", 890, 1150, 150, None),
         (46.4, 50.5, "👷", 300, 1600, 130, "TRABALHADOR"), (48.1, 50.5, "👵", 590, 1600, 130, "APOSENTADO"), (49.2, 50.5, "🏪", 880, 1600, 130, "PEQUENO EMPRESÁRIO"),
         (50.95, 54.15, "🇧🇷", 420, 1580, 150, None), (51.5, 54.15, "🇦🇷", 760, 1580, 150, None), (55.4, 57.3, "💰", 880, 1170, 160, None), (58.5, 61.45, "💬", 880, 1170, 160, None)]
_emo = {}
def emoji(ch, size):
    key = (ch, size)
    if key not in _emo:
        f = ImageFont.truetype(EMOJI, 109); im = Image.new("RGBA", (160, 160), (0, 0, 0, 0)); ImageDraw.Draw(im).text((8, 8), ch, font=f, embedded_color=True)
        bb = im.getbbox(); im = im.crop(bb) if bb else im; sc = size / max(im.size); _emo[key] = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    return _emo[key]
def pop(frame, img, cx, cy, u, dur, wob=True):
    if u < 0: return
    k = R.back_out(u / 0.32, 2.4) if u < 0.32 else 1.0; out = ease_in((u - (dur - 0.2)) / 0.2)
    sc = max(0.05, k * (1 - 0.3 * out)); ang = 8 * math.sin(u * 6) if wob else 0
    im = img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))), Image.BICUBIC)
    if ang: im = im.rotate(ang, resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.getchannel("A").point(lambda v: int(v * 0.45)))
    frame.alpha_composite(R.fade(sh, 1 - out), (int(cx - im.width / 2 + 6), int(cy - im.height / 2 + 14)))
    frame.alpha_composite(R.fade(im, 1 - out), (int(cx - im.width / 2), int(cy - im.height / 2)))
# ---------------- fonte ----------------
_ch = {}; _gr = {}; _mk = {}
def raw_frame(x):
    key = int(x // 6)
    if key not in _ch:
        if len(_ch) > 2: _ch.clear()
        p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{key * 6:.3f}", "-t", "6.2", "-i", ME, "-vf", "fps=30", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           capture_output=True).stdout
        n = len(p) // (1080 * 1920 * 3); _ch[key] = np.frombuffer(p[:n * 1080 * 1920 * 3], np.uint8).reshape(n, 1920, 1080, 3)
    fr = _ch[key]; return fr[min(len(fr) - 1, int((x - key * 6) * FPS))], key * 1000 + min(len(fr) - 1, int((x - key * 6) * FPS))
def graded(x):
    fr, idx = raw_frame(x)
    if idx not in _gr:
        if len(_gr) > 40: _gr.clear()
        _gr[idx] = GRADE(cor_milei.fix(fr))
    return _gr[idx], idx
_yy, _xx = np.mgrid[0:1920, 0:1080].astype(np.float32)                 # só a cabeça e o corpo dele (o U2Net pega o encosto e a sombra no teto)
_el = ((_xx - 555) / 300) ** 2 + ((_yy - 935) / 445) ** 2
HEAD_PRIOR = np.maximum(np.clip((1.12 - _el) / 0.24, 0, 1), np.clip((_yy - 1250) / 80, 0, 1))
def person_mask(img, idx):
    if idx not in _mk:
        if len(_mk) > 40: _mk.clear()
        m = SEG(img); m = np.clip((m - 0.35) / 0.35, 0, 1) * HEAD_PRIOR; _mk[idx] = cv2.GaussianBlur(m, (0, 0), 1.6)[..., None]
    return _mk[idx]
def zoom(img, z, cx=540, cy=900):
    if abs(z - 1) < 1e-3: return img
    M = np.float32([[z, 0, cx * (1 - z)], [0, z, cy * (1 - z)]]); return cv2.warpAffine(img, M, (1080, 1920), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
def zoom_level(x, ki, t):
    if 40.0 <= x < 50.6: return 1.06 + 0.12 * ease_io((x - 40.0) / 10.6)          # opinião: aproxima devagar
    base = 1.0 if ki % 2 == 0 else 1.08                                             # pausa cortada = troca de enquadramento
    u = t - OFF[ki]; return base + 0.05 * (1 - ease_out(u / 0.18)) * (ki > 0)       # soquinho na entrada
# ---------------- palavras atrás ----------------
def big_layer(word, col, u, dur, shake, idx):
    """palavra inteira, centrada na área segura, semitransparente; entra crescendo do centro (nunca cortada pela borda)"""
    size = 330; f = R.BIGF(size)
    while f.getlength(word) > 820: size -= 6; f = R.BIGF(size)
    lay = Image.new("RGBA", (W, int(size * 1.35)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text((CX + 5, lay.height / 2 + 7), word, font=f, fill=(0, 0, 0, 70), anchor="mm")
    d.text((CX, lay.height / 2), word, font=f, fill=col + (205,), anchor="mm", stroke_width=4, stroke_fill=R.NAVY + (190,))
    k = ease_out(u / 0.3); out = ease_in((u - (dur - 0.25)) / 0.25)
    sc = 1.18 - 0.18 * k + 0.06 * out
    if abs(sc - 1) > 0.003:
        nw, nh = int(W * sc), int(lay.height * sc); big = lay.resize((nw, nh), Image.BICUBIC); ox = int(CX * sc - CX); oy = (nh - lay.height) // 2
        lay = big.crop((ox, oy, ox + W, oy + lay.height))
    dx = 0; dy = 0
    if shake and 0.3 < u < 1.0: a_ = 7 * (1 - (u - 0.3) / 0.7); dx = a_ * math.sin(u * 90); dy = a_ * 0.6 * math.cos(u * 70)
    return R.fade(lay, k * (1 - out)), int(dx), int(470 - lay.height / 2 + dy)
# ---------------- tela dividida ----------------
SEAM = 900
NAVY_BG = np.clip(R.NAVYBG, 0, 255).astype(np.uint8)
def wrap(txt, font, maxw):
    lines, cur = [], ""
    for w in txt.split():
        t2 = (cur + " " + w).strip()
        if font.getlength(t2) <= maxw: cur = t2
        else: lines.append(cur); cur = w
    return lines + [cur]
def head_card():
    w = 860; im = Image.new("RGB", (w, 520), PAPER); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 10), fill=BLUE); d.text((40, 50), "NEXO · 22/10", font=R.MF("ExtraBold", 28), fill=BLUE, anchor="lm")
    d.line((40, 82, w - 40, 82), fill=(205, 200, 190), width=2); f = R.SERIF(58); y = 104
    for l in wrap("Faz sentido transpor ao Brasil o modelo econômico de Milei?", f, w - 80): d.text((40, y), l, font=f, fill=INK); y += 68
    return np.asarray(im)[:int(y + 34) // 2 * 2]
HEAD = head_card()
def card_bg(w, h, r=26):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), r, fill=(8, 30, 56, 235), outline=R.GOLD + (255,), width=3); return im
def num_txt(v, dec=0, suf="%"):
    s = f"{v:.{dec}f}".replace(".", ","); return s + suf
def inflation_card(u):
    w, h = 820, 700; im = card_bg(w, h); d = ImageDraw.Draw(im)
    d.text((40, 52), "INFLAÇÃO NA ARGENTINA", font=R.MF("ExtraBold", 36), fill=R.GOLD_L + (255,), anchor="lm")
    d.text((40, 96), "acumulada em 12 meses", font=R.MF("SemiBold", 26), fill=(210, 220, 235, 255), anchor="lm")
    k = ease_io(clamp((u - 0.9) / 2.6)); v = 290 + (33.4 - 290) * k
    d.text((w / 2, 230), num_txt(v, 1 if k > 0.97 else 0), font=R.BIGF(170), fill=(255, 255, 255, 255), anchor="mm")
    x0, x1, y0, y1 = 70, w - 70, 360, 600                       # gráfico: linha caindo
    d.line((x0, y1, x1, y1), fill=(120, 140, 170, 255), width=2)
    pts = [(x0 + (x1 - x0) * i / 40, y0 + (y1 - y0 - 30) * (1 - math.exp(-i / 9)) / (1 - math.exp(-40 / 9))) for i in range(41)]
    n = min(len(pts), max(2, int(len(pts) * k) + 1)); d.line(pts[:n], fill=R.GOLD + (255,), width=9, joint="curve")
    ex, ey = pts[n - 1]; d.ellipse((ex - 13, ey - 13, ex + 13, ey + 13), fill=(255, 255, 255, 255), outline=R.GOLD + (255,), width=4)
    d.text((x0, y0 - 26), "antes: ~290%", font=R.MF("Bold", 26), fill=(230, 230, 240, 255), anchor="lm")
    if k > 0.95: d.text((x1, y1 - 60), "set/2026: 33,4%", font=R.MF("ExtraBold", 30), fill=R.GOLD_L + (255,), anchor="rm")
    d.text((w / 2, h - 40), "Fonte: Indec", font=R.MF("SemiBold", 24), fill=(200, 210, 225, 255), anchor="mm")
    return im, k
STATS = [(26.94, "👥", "POBREZA", 28.2, 32.3, 1, "%", "voltou a subir (era 28,2%)", 45), (29.52, "💼", "DESEMPREGO", 7.6, 7.9, 1, "%", "2º tri/2026", 12),
         (32.76, "🏭", "EMPRESAS", 0, 30, 0, " mil+", "fecharam desde a posse", 40)]
def stats_card(x):
    w, h = 860, 760; im = card_bg(w, h); d = ImageDraw.Draw(im)
    for i, (t0, emo, lab, v0, v1, dec, suf, sub, vmax) in enumerate(STATS):
        u = x - t0
        if u < 0: continue
        k = ease_out(u / 0.35); y = 40 + i * 235; row = Image.new("RGBA", (w, 230), (0, 0, 0, 0)); dr = ImageDraw.Draw(row)
        e = emoji(emo, 96); row.alpha_composite(e, (30, 40))
        dr.text((150, 50), lab, font=R.MF("ExtraBold", 36), fill=R.GOLD_L + (255,), anchor="lm")
        dr.text((150, 92), sub, font=R.MF("SemiBold", 24), fill=(205, 215, 230, 255), anchor="lm")
        kc = ease_io(clamp((u - 0.2) / 1.3)); v = v0 + (v1 - v0) * kc
        dr.text((w - 40, 70), num_txt(v, dec, suf), font=R.BIGF(96), fill=(255, 255, 255, 255), anchor="rm")
        bx0, bx1, by = 150, w - 40, 150; dr.rounded_rectangle((bx0, by, bx1, by + 28), 14, fill=(30, 55, 90, 255))
        fw = (bx1 - bx0) * min(1.0, v / vmax); dr.rounded_rectangle((bx0, by, bx0 + max(28, fw), by + 28), 14, fill=R.GOLD + (255,))
        dr.text((bx1 - 4, by + 50), "▲", font=R.MF("ExtraBold", 28), fill=R.GOLD_L + (255,), anchor="rm")
        im.alpha_composite(R.fade(row, k), (int(60 * (1 - k)), y))
    if x > 37.26: d.text((w / 2, h - 30), "Fontes: Indec (2026) · levantamento da Fundar", font=R.MF("SemiBold", 22), fill=(200, 210, 225, 255), anchor="mm")
    return im
def split_scene(x, t, k_idx):
    img, idx = graded(x)
    top = img[330:1430]; tw = int(1080 * SEAM / 1100); fg = cv2.resize(top, (tw, SEAM), interpolation=cv2.INTER_AREA)
    bg = cv2.resize(cv2.GaussianBlur(cv2.resize(top, (108, 90)), (0, 0), 3), (W, SEAM)).astype(np.float32) * 0.55
    x0 = CX - tw // 2; fm = np.ones((SEAM, tw), np.float32); fm[:, :50] = np.linspace(0, 1, 50)[None]; fm[:, -50:] = np.linspace(1, 0, 50)[None]; fm = fm[..., None]
    xs, xe = max(0, x0), min(W, x0 + tw); bg[:, xs:xe] = bg[:, xs:xe] * (1 - fm[:, xs - x0:xe - x0]) + fg[:, xs - x0:xe - x0] * fm[:, xs - x0:xe - x0]
    base = NAVY_BG.copy(); base[:SEAM] = bg.astype(np.uint8)
    frame = Image.fromarray(base).convert("RGBA"); ImageDraw.Draw(frame).rectangle((0, SEAM - 2, W, SEAM + 3), fill=R.GD)
    a, b = SPLIT[k_idx]; u = x - a; kin = ease_out(u / 0.4)
    if k_idx == 0:
        ci = Image.fromarray(R.rounded(HEAD, 22, 4)).rotate(-1.4, resample=Image.BICUBIC, expand=True)
        R.paste(frame, R.fade(ci, kin), CX - ci.width / 2, 990 + 260 * (1 - kin), 0.6, 22, (10, 26)); y2 = 990 + ci.height + 60
        for j, (t0, emo, txt) in enumerate(((9.75, "✂️", "CORTE PESADO DE GASTOS"), (10.95, "🏛️", "ESTADO MENOR"))):
            if x >= t0:
                kk = clamp((x - t0) / 0.25); R.pill(frame, "   " + txt, CX + 30, y2 + j * 110, kk, fill=BLUE, size=38)
                pop(frame, emoji(emo, 70), CX - R.MF("ExtraBold", 38).getlength(txt) / 2 - 20, y2 + j * 110, x - t0, 99, wob=False)
        R.credit(frame, "Manchete: Nexo Jornal", CX, 1772, kin, anchor="mm")
    elif k_idx == 1:
        card, kk = inflation_card(u); R.paste(frame, R.fade(card, kin), CX - card.width / 2, 990 + 240 * (1 - kin), 0.6, 22, (10, 26))
        if kk > 0.98: pop(frame, emoji("✅", 110), CX + card.width / 2 - 60, 1010, u - 3.6, 99)
    else:
        card = stats_card(x); R.paste(frame, R.fade(card, kin), CX - card.width / 2, 975 + 240 * (1 - kin), 0.6, 22, (10, 26))
    R.draw_caption(frame, t, SEAM + 4, 44, ("me", "au")) if False else caption(frame, t, SEAM - 70, 44)
    return frame
def caption(frame, t, y, size):
    old = R.RED; R.RED = BLUE
    try: R.draw_caption(frame, t, y, size, ("me", "au"))
    finally: R.RED = old
CARD = ("ARGENTINA", ["O MODELO MILEI", "SERVE PRO BRASIL?"])
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); x, ki = src_of(tt); sk = split_of(x)
    if sk is not None: frame = split_scene(x, tt, sk)
    else:
        img, idx = graded(x); z = zoom_level(x, ki, tt)
        bigs = [(i, b) for i, b in enumerate(BIG) if b[0] <= x < b[1]]
        if bigs:
            m = person_mask(img, idx); fr = Image.fromarray(img).convert("RGBA")
            for i, (a, b, word, col, shk) in bigs:
                lay, dx, y = big_layer(word, col, x - a, b - a, shk, i); fr.alpha_composite(lay, (dx, y))
            comp = np.asarray(fr.convert("RGB")).astype(np.float32); img = (comp * (1 - m) + img.astype(np.float32) * m).astype(np.uint8)
        img = zoom(img, z)
        frame = Image.fromarray(img).convert("RGBA")
        g = np.zeros((520, W, 4), np.uint8); g[..., :3] = (4, 14, 28); g[..., 3] = np.linspace(0, 200, 520)[:, None].astype(np.uint8); frame.alpha_composite(Image.fromarray(g), (0, H - 520))
        for a, b, ch, cx, cy, sz, lab in ICONS:
            if a <= x < b:
                pop(frame, emoji(ch, sz), cx, cy, x - a, b - a)
                if lab and x - a > 0.15: R.pill(frame, lab, cx, cy + sz / 2 + 40, clamp((x - a - 0.15) / 0.25) * (1 - ease_in((x - (b - 0.2)) / 0.2)), fill=R.NAVY, size=20)
        cy_cap = 1430 if 46.0 <= x < 54.2 else 1520
        caption(frame, tt, cy_cap, 50)
        kc = clamp((tt - 0.6) / 0.4) * (1 - clamp((x - 5.0) / 0.3))
        if kc > 0: BAR.lower_card(frame, CARD[0], CARD[1], 1700, kc, fs=40)
    BAR.draw_bar(frame, clamp(t / END_IN), "canal", ease_out((t - 0.2) / 0.6), 0.0, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(frame, t)
    for i in range(1, len(KEEP)):                                      # flash curto onde muda de modo
        xa = KEEP[i][0]; xb = KEEP[i - 1][1]
        if (split_of(xa) is None) != (split_of(xb) is None) and abs(t - OFF[i]) < 0.08:
            frame = Image.blend(frame, Image.new("RGBA", frame.size, (255, 255, 255, 255)), (1 - abs(t - OFF[i]) / 0.08) * 0.35)
    if t >= END_IN: frame.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return frame.convert("RGB")

def main():
    if MODE == "lib": return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(t).resize((360, 640), Image.LANCZOS) for t in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    if MODE.startswith("src"):                                         # quadros por tempo do original
        xs = [float(v) for v in MODE.split(":")[1].split(",")]; print([round(out_of(v), 2) for v in xs]); return
    if MODE == "info": print("TOTAL", round(TOTAL, 2), "EDIT", round(EDIT_END, 2)); return
    vout = f"{V}/video.mp4"
    if not (os.environ.get("REUSE") and os.path.exists(vout)):
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
        for k in range(int(round(TOTAL * FPS))): enc.stdin.write(frame_at(k / FPS).tobytes())
        enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", ME, "-ar", "48000", "-ac", "2", f"{V}/me48.wav"], check=True)
    me = R.readw(f"{V}/me48.wav"); vt = np.zeros((n, 2), np.float32); f = int(0.012 * SR)
    for i, (a, b) in enumerate(KEEP):
        c = me[int(a * SR):int(b * SR)].copy(); c[:f] *= np.linspace(0, 1, f)[:, None]; c[-f:] *= np.linspace(1, 0, f)[:, None]
        o = int(OFF[i] * SR); vt[o:o + len(c)] += c[:n - o]
    R.writew(f"{V}/voice.wav", vt)
    bed = R.readw(f"{V}/bed.wav"); L = min(len(bed), n); tl = np.arange(L) / SR
    gain = (0.06 * np.clip(tl / 1.0, 0, 1) + 0.05 * np.clip((tl - (EDIT_END - 0.3)) / 0.5, 0, 1)) * np.clip(1 - (tl - (TOTAL - 1.6)) / 1.5, 0, 1)
    sg = np.zeros((n, 2), np.float32); sg[:L] = bed[:L] * gain[:, None]; R.writew(f"{V}/song.wav", sg)
    ev = [(0.0, sfx.whoosh(0.4), 0.2), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
    for i, (a, b, *_r) in enumerate(BIG): ta = out_of(a); ev += [(ta, sfx.whoosh(0.35), 0.24), (ta + 0.26, sfx.click(), 0.7), (ta + 0.26, sfx.thud(0.3), 0.2)]
    for a, b, *_r in ICONS: ev += [(out_of(a), sfx.click(), 0.45)]
    for a, b in SPLIT: ev += [(out_of(a) - 0.1, sfx.whoosh(0.45), 0.24)]
    ev += [(out_of(5.6) + 0.1, sfx.paper(), 0.5), (out_of(9.75), sfx.click(), 0.4), (out_of(10.95), sfx.click(), 0.4)]
    for t0, *_r in STATS: ev += [(out_of(t0), sfx.whoosh(0.3), 0.18)] + [(out_of(t0) + 0.2 + j * 0.11, sfx.click(), 0.18) for j in range(12)]
    ev += [(out_of(14.85) + 0.9 + j * 0.2, sfx.click(), 0.2) for j in range(13)]
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=80,afftdn=nf=-25,acompressor=threshold=0.08:ratio=2.5:attack=8:release=200:makeup=1.6,asplit=2[vox][k2];[2:a]volume=0.8[sf];[3:a]volume=0.95[sg];"
                    "[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][sgd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
