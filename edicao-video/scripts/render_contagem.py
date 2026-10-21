"""Série "Faltam X dias" (21 a 24/10/2026). Abre nele em tela cheia com o contador que vira (placa de relógio), meio com a notícia do dia
(trecho de TV e manchetes conferidas, cada uma com a fonte), fecha nele com o contador indo para o próximo número.
Dia 4 (21/10): Lula autorizou abrir os sigilos no TSE; a campanha do Flávio diz que não aceita o desafio; o outro lado é a fala dele no debate."""
import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
import sfx
BLUE = (14, 62, 120); PAPER = (247, 244, 236); INK = (22, 26, 34)
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; ease_out = R.ease_out; ease_in = R.ease_in; ease_io = R.ease_io
DAY = int(os.environ.get("DAY", "4"))
V = f"{S}/v46"; ME = f"{V}/me.mp4"; CL = f"{S}/v43/cl.mp4"
# (fonte, início, fim, cartão)  fonte "-" = sem áudio de fala (manchete na tela)
PARTS = [("me", 2.4, 5.75, None), ("-", 0, 3.4, "a1"), ("-", 0, 3.6, "a2"), ("cl", 26.15, 30.42, "tv"),
         ("-", 0, 3.0, "h2"), ("-", 0, 3.4, "h4"), ("-", 0, 2.8, "q"),
         ("me", 6.3, 10.6, None)]
HEADS = {"a1": ("METRÓPOLES · HOJE, 21/10", "Lula faz caminhada no centro de BH; Flávio vai a Guarulhos com Tarcísio"),
         "a2": ("O FATOR · HOJE, 21/10", "Caso Ana Clara deve ser o centro do discurso de Lula em BH"),
         "h1": ("GAZETA DE S.PAULO · ONTEM, 20/10", "Lula protocola quebra de sigilo no TSE e Flávio Bolsonaro não aceita desafio de fazer o mesmo"),
         "h2": ("SBT NEWS · ONTEM, 20/10", "Flávio não vai aceitar desafio de Lula para abrir sigilos"),
         "h3": ("CNN BRASIL · ONTEM, 20/10", "Análise: Flávio Bolsonaro trata quebra de sigilo como “factoide”"),
         "h4": ("O OUTRO LADO · DEBATE DA BAND, 18/10", "Flávio diz que não tem “absolutamente nada a esconder”")}
segs = []; acc = 0.0
for src_, a, b, card_ in PARTS: segs.append(dict(src=src_, a=a, b=b, t0=acc, t1=acc + b - a, card=card_)); acc += b - a
EDIT_CUT = acc
def seg_at(t):
    for s in segs:
        if t < s["t1"]: return s
    return segs[-1]
def segmap(i, x): return segs[i]["t0"] + x - segs[i]["a"]
FULL = MODE == "full" or MODE.startswith(("frames", "cover"))
MEF = R.decode(ME, 0, 12.2, 720, 1280, "scale=720:1280") if FULL else None
TVY, TVH = 656, 428
TVF = R.decode(CL, 26.0, 30.6, 1080, TVH, f"crop=1080:{TVH}:0:{TVY}") if FULL else None
def fr_of(arr, x): return arr[int(clamp(x * FPS, 0, len(arr) - 1))]
def me_big(x): return cv2.resize(fr_of(MEF, x), (1080, 1920), interpolation=cv2.INTER_LINEAR)
FIT = 0.88; _fw, _fh = int(W * FIT), int(H * FIT); _fx = CX - _fw // 2; _fy = H - _fh
_fm = np.ones((_fh, _fw), np.float32); _fm[:, :30] = np.linspace(0, 1, 30)[None, :]; _fm[:, -30:] = np.linspace(1, 0, 30)[None, :]; _fm[:30] *= np.linspace(0, 1, 30)[:, None]; _fm = _fm[..., None]
def me_full(x):
    img = me_big(x); bg = cv2.resize(cv2.GaussianBlur(cv2.resize(img, (W // 10, H // 10)), (0, 0), 2.5), (W, H)).astype(np.float32) * 0.7
    fg = cv2.resize(cv2.LUT(img, R.LUT), (_fw, _fh), interpolation=cv2.INTER_AREA).astype(np.float32)
    bg[_fy:, _fx:_fx + _fw] = bg[_fy:, _fx:_fx + _fw] * (1 - _fm) + fg * _fm
    return bg
WIN_W, WIN_H, WIN_Y = 444, 592, 112; WIN_X = CX - WIN_W // 2
CRD_Y, CRD_H = 850, 520; CARD_Y_SPLIT = CRD_Y + CRD_H + 124; CAP_Y_SPLIT = 1744
def win_img(x): return cv2.resize(cv2.LUT(me_big(x)[40:1480], R.LUT), (WIN_W, WIN_H), interpolation=cv2.INTER_AREA)
def listen_x(t):
    u = (t * 0.45) % 2.4
    return 10.0 + (u if u < 1.2 else 2.4 - u)                                       # ele calado, olhando para a câmera
def fit_w(img, w): return cv2.resize(img, (w, int(w * img.shape[0] / img.shape[1])), interpolation=cv2.INTER_LANCZOS4)
def wrap(txt, font, maxw):
    lines, cur = [], ""
    for w in txt.split():
        t = (cur + " " + w).strip()
        if font.getlength(t) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]
_hcache = {}
def head_card(key):
    """manchete em cartão de papel, com o veículo e a data em cima (texto conferido, sem logo)"""
    if key in _hcache: return _hcache[key]
    w = 880; im = Image.new("RGB", (w, 470), PAPER); d = ImageDraw.Draw(im)
    if key == "q":
        im = Image.new("RGB", (w, 470), BLUE); d = ImageDraw.Draw(im)
        for sz in range(104, 40, -4):
            f = R.BIGF(sz); ls = wrap("A DISPUTA ESTÁ APERTADA. CADA VOTO CONTA.", f, w - 90)
            if len(ls) * sz * 1.12 <= 380: break
        y = 235 - len(ls) * sz * 1.12 / 2
        for l in ls: d.text((w / 2, y + sz * 0.56), l, font=f, fill=(255, 214, 0), anchor="mm"); y += sz * 1.12
        _hcache[key] = np.asarray(im); return _hcache[key]
    src, txt = HEADS[key]
    d.rectangle((0, 0, w, 10), fill=BLUE if key != "h4" else (90, 98, 110))
    d.text((44, 52), src, font=R.MF("ExtraBold", 28), fill=BLUE + (255,) if key != "h4" else (90, 98, 110), anchor="lm")
    d.line((44, 84, w - 44, 84), fill=(205, 200, 190), width=2)
    for sz in range(64, 30, -2):
        f = R.SERIF(sz); ls = wrap(txt, f, w - 88)
        if len(ls) * sz * 1.18 <= 330: break
    y = 110
    for l in ls: d.text((44, y), l, font=f, fill=INK); y += sz * 1.18
    _hcache[key] = np.asarray(im)[:max(300, int(y + 44)) // 2 * 2]; return _hcache[key]         # altura justa ao texto
def card_img(s, x):
    if s["card"] == "tv": return fit_w(fr_of(TVF, x - 26.0)[30:], 880), "Imagens: reprodução CNN Brasil"
    cred = {"a1": "Fonte: Metrópoles", "a2": "Fonte: O Fator", "h1": "Manchete: Gazeta de S.Paulo", "h2": "Manchete: SBT News", "h3": "Manchete: CNN Brasil", "h4": "Fonte: CNN Brasil", "q": "Opinião do canal"}[s["card"]]
    return head_card(s["card"]), cred
def persp_top(rgba, a):
    h, w = rgba.shape[:2]; src = np.float32([[0, 0], [w, 0], [w, h], [0, h]]); dst = np.float32([[w * a, h * a * 0.35], [w * (1 - a), h * a * 0.35], [w, h], [0, h]])
    return cv2.warpPerspective(rgba, cv2.getPerspectiveTransform(src, dst), (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
ME_CAPS = [("FALTAM QUATRO DIAS", 2.55, 4.0), ("E EU PRECISO TE MOSTRAR ISSO AQUI.", 4.0, 5.6),
           ("COMPARTILHA COM QUEM", 6.4, 7.4), ("AINDA TÁ EM DÚVIDA", 7.4, 8.3), ("E ME SEGUE.", 8.3, 9.2)]
CL_CAPS = [("LULA JÁ AUTORIZOU", 26.2, 27.45), ("A QUEBRA DE SIGILO", 27.45, 28.6), ("OFICIALMENTE DELE…", 28.6, 29.5), ("E DA FAMÍLIA.", 29.95, 30.4)]
HOT = {"QUATRO", "DIAS", "AUTORIZOU", "SIGILO", "FAMÍLIA.", "COMPARTILHA", "SEGUE."}
CAPS = []
for i, s in enumerate(segs):
    if s["src"] == "-": continue
    for txt, a, b in (ME_CAPS if s["src"] == "me" else CL_CAPS):
        a, b = max(a, s["a"]), min(b, s["b"])
        if b - a < 0.25: continue
        a2, b2 = segmap(i, a), segmap(i, b); ws = txt.split(); tot = sum(len(w) + 2 for w in ws); k = 0; ts = []
        for w in ws: ts.append(a2 + (b2 - a2 - 0.1) * k / tot); k += len(w) + 2
        CAPS.append(dict(words=ws, ts=ts, start=a2, end=b2, src="au" if any(w in HOT for w in ws) else "me"))
CAPS.sort(key=lambda c: c["start"]); R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
BIG = [(1, 0.3, 3.3, "HOJE", R.GOLD_L), (2, 0.3, 3.5, "ANA CLARA", R.WHITE), (3, 26.25, 27.4, "ONTEM", R.WHITE), (3, 27.45, 29.5, "LULA AUTORIZOU", R.GOLD_L),
       (4, 0.2, 2.9, "NÃO ACEITA", R.GOLD_L), (5, 0.3, 3.3, "O OUTRO LADO", R.WHITE)]
BIG = [(segmap(i, a), segmap(i, b), w, c) for i, a, b, w, c in BIG]
PILLS = [(2, 0.4, 3.5, "O PT MOBILIZA AS REDES SOBRE O CASO", R.NAVY), (3, 26.2, 30.4, "ONTEM, NA CNN: LULA AUTORIZOU ABRIR OS SIGILOS NO TSE", R.NAVY),
         (4, 0.3, 2.9, "SBT NEWS: A CAMPANHA NÃO VAI ACEITAR O DESAFIO", R.NAVY)]
PILLS = [(segmap(i, a), segmap(i, b), x, c) for i, a, b, x, c in PILLS]
EDIT_END = EDIT_CUT; FIN_IN = EDIT_END; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = FIN_IN; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
CARD = (f"FALTAM {DAY} DIAS · 25/10", ["O QUE ROLOU", "NA RETA FINAL"])
CTA = [(segmap(7, 6.4), segmap(7, 9.3))]
def cta_level(t): return max([clamp((t - a) / 0.4) * clamp((b - t) / 0.4) for a, b in CTA] + [0.0])
SPLIT_T, SPLIT_END = segs[1]["t0"], segs[7]["t0"]
SWAPS = [s["t0"] for s in segs[2:7]]
FLIP_IN = (0.0, 0.45); FLIP_NEXT = segmap(7, 9.4)                                # contador: entra virando; no fim vira para o próximo número
def caption(frame, t, y, size, tracks):
    old = R.RED; R.RED = BLUE
    try: R.draw_caption(frame, t, y, size, tracks)
    finally: R.RED = old
def big_word(frame, t, zone):
    z0, z1 = zone
    for i, (a, b, word, col) in enumerate(BIG):
        if not (a <= t < b): continue
        u = t - a; k = ease_out(u / 0.28); out = ease_in((t - (b - 0.22)) / 0.22)
        size = 200
        while True:
            f = R.BIGF(size); bb = f.getbbox(word, stroke_width=10)
            if (bb[3] - bb[1]) <= (z1 - z0) - 16 and (bb[2] - bb[0]) <= 680: break
            size -= 4
        lay = Image.new("RGBA", (W, bb[3] - bb[1] + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.text((W / 2 - (bb[0] + bb[2]) / 2 + 5, 10 - bb[1] + 7), word, font=f, fill=(0, 0, 0, 120), stroke_width=10, stroke_fill=(0, 0, 0, 120))
        d.text((W / 2 - (bb[0] + bb[2]) / 2, 10 - bb[1]), word, font=f, fill=col + (255,), stroke_width=10, stroke_fill=R.NAVY + (255,))
        dx = (1 if i % 2 == 0 else -1) * W * 0.95 * (1 - k)
        if u < 0.28:
            Lb = int(60 * (1 - k)) + 1
            if Lb > 2: lay = Image.fromarray(cv2.filter2D(np.asarray(lay), -1, np.ones((1, Lb), np.float32) / Lb))
        frame.alpha_composite(R.fade(lay, 1 - out), (int(CX - W / 2 + dx), int((z0 + z1) / 2 - lay.height / 2)))
def counter(frame, t, n, flip, label_top="FALTAM", label_bot="DIAS", cy=280):
    """placa de relógio com o número: flip 0..1 é a virada (a placa fecha e abre com o novo número)"""
    pw, ph = 250, 300; lay = Image.new("RGBA", (pw + 40, ph + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((20, 20, 20 + pw, 20 + ph), 30, fill=R.NAVY + (255,), outline=R.GOLD_L + (255,), width=6)
    d.text((20 + pw / 2, 20 + ph / 2 + 6), str(n), font=R.BIGF(250), fill=R.GOLD_L + (255,), anchor="mm")
    d.line((26, 20 + ph / 2, 14 + pw, 20 + ph / 2), fill=(0, 0, 0, 160), width=4)
    sy = abs(math.cos(math.pi * clamp(flip)))                                       # fecha e abre
    if sy < 0.999: lay = lay.resize((lay.width, max(2, int(lay.height * sy))), Image.BICUBIC)
    frame.alpha_composite(lay, (int(CX - lay.width / 2), int(cy - lay.height / 2)))
    d2 = ImageDraw.Draw(frame); f = R.BIGF(70)
    d2.text((CX - 215, cy), label_top, font=f, fill=(255, 255, 255, 255), anchor="rm", stroke_width=7, stroke_fill=R.NAVY + (255,))
    d2.text((CX + 215, cy), label_bot, font=f, fill=(255, 255, 255, 255), anchor="lm", stroke_width=7, stroke_fill=R.NAVY + (255,))
def card_k(t):
    k = ease_out((t - 0.6) / 0.4) * (1 - ease_in((t - (END_IN - 0.35)) / 0.35))
    if SPLIT_T - 0.35 <= t < SPLIT_T + 0.6: k *= clamp((SPLIT_T - t) / 0.35)
    elif SPLIT_T + 0.6 <= t < SPLIT_T + 0.95: k *= (t - SPLIT_T - 0.6) / 0.35
    if abs(t - SPLIT_END) < 0.35: k *= abs(t - SPLIT_END) / 0.35
    return k
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); s = seg_at(tt); x = s["a"] + min(tt, s["t1"] - 0.02) - s["t0"]
    if SPLIT_T <= t < SPLIT_END:
        mex = x if s["src"] == "me" else listen_x(t)
        card, cred = card_img(s, x)
        bg = R.blur_bg(card, 0.28) if s["card"] == "tv" else R.blur_bg(me_big(mex), 0.22)
        frame = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
        u = t - SPLIT_T; kw = ease_io(u / 0.55)
        if kw < 1:
            full = me_full(segs[0]["b"] - 0.03 if t < SPLIT_T + 0.6 else mex)
            frame = Image.fromarray(np.clip(full * (1 - kw) + np.asarray(frame.convert("RGB"), np.float32) * kw, 0, 255).astype(np.uint8)).convert("RGBA")
            wx, wy = _fx + (WIN_X - _fx) * kw, _fy + (WIN_Y - _fy) * kw; ww, wh = _fw + (WIN_W - _fw) * kw, _fh + (WIN_H - _fh) * kw
            wimg = cv2.resize(cv2.LUT(me_big(mex)[40:1480], R.LUT), (max(8, int(ww)), max(8, int(wh))), interpolation=cv2.INTER_AREA)
            R.paste(frame, R.fade(Image.fromarray(R.rounded(wimg, int(28 * kw) + 1, 4 if kw > 0.6 else 0)), clamp(kw * 2)), wx, wy, 0.55 * kw, 18, (6, 16))
        else:
            win = Image.fromarray(R.rounded(win_img(mex), 28, 4)); R.paste(frame, win, WIN_X, WIN_Y, 0.55, 18, (6, 16))
        kin = ease_out((u - 0.5) / 0.5); ch, cw = card.shape[:2]; cy0 = CRD_Y + (CRD_H - ch) / 2
        cardi = R.rounded(card, 26, 4)
        if kin < 1: cardi = persp_top(cardi, 0.02 + 0.3 * (1 - kin))
        for sw in SWAPS:
            if 0 <= t - sw < 0.5: cy0 += 300 * (1 - ease_out((t - sw) / 0.5))
        R.paste(frame, R.fade(Image.fromarray(cardi, "RGBA"), clamp(kin * 1.6)), CX - cw / 2, cy0 + 380 * (1 - kin), 0.6, 22, (10, 26))
        R.credit(frame, cred, CX, 1820, kin, anchor="mm")
        big_word(frame, t, (WIN_Y + WIN_H + 20, cy0 - 22))
        for a, b, txt, colr in PILLS:
            if a <= t < b: R.pill(frame, txt, CX, cy0 + ch + 48, clamp((t - a) / 0.3) * clamp((b - t) / 0.25) * kin, fill=colr, size=pill_size(txt))
        kc = card_k(t)
        if kc > 0: BAR.lower_card(frame, CARD[0], CARD[1], CARD_Y_SPLIT, kc, fs=36)
        caption(frame, t, CAP_Y_SPLIT, 42, ("me", "au"))
    else:
        frame = Image.fromarray(np.clip(me_full(x), 0, 255).astype(np.uint8)).convert("RGBA")
        if t < SPLIT_T:
            counter(frame, t, DAY, 0.5 + 0.5 * clamp((t - FLIP_IN[0]) / (FLIP_IN[1] - FLIP_IN[0])))
        else:
            fl = clamp((t - FLIP_NEXT) / 0.5)
            if t >= FLIP_NEXT - 0.6:
                counter(frame, t, DAY if fl < 0.5 else DAY - 1, fl, "FALTAM" if DAY - 1 != 1 else "FALTA", "DIAS" if DAY - 1 != 1 else "DIA")
                if fl > 0.5:
                    ka = ease_out((fl - 0.5) / 0.5); dd = ImageDraw.Draw(frame)
                    dd.text((CX, 520 + 20 * (1 - ka)), "AMANHÃ", font=R.BIGF(84), fill=R.GOLD_L + (int(255 * ka),), anchor="mm", stroke_width=8, stroke_fill=R.NAVY + (255,))
        caption(frame, t, 1500, 48, ("me", "au")); kc = card_k(t)
        if kc > 0: BAR.lower_card(frame, CARD[0], CARD[1], 1655, kc, fs=40)
    BAR.draw_bar(frame, clamp(t / END_IN), "canal", ease_out((t - 0.2) / 0.6), cta_level(t), 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(frame, t)
    for e in [segs[1]["t0"], segs[7]["t0"]] + SWAPS:
        if abs(t - e) < 0.09: frame = Image.blend(frame, Image.new("RGBA", frame.size, (255, 255, 255, 255)), (1 - abs(t - e) / 0.09) * 0.4)
    if t >= END_IN: frame.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return frame.convert("RGB")
def pill_size(txt, size=30):
    while R.MF("ExtraBold", size).getlength(txt) + 50 > 660: size -= 1
    return size

def main():
    if MODE in ("lib", "cover"): return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(t).resize((360, 640), Image.LANCZOS) for t in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    if MODE == "info": print("TOTAL", round(TOTAL, 2), [(p[0], p[3], round(s["t0"], 2)) for p, s in zip(PARTS, segs)]); return
    vout = f"{V}/video.mp4"
    if not (os.environ.get("REUSE") and os.path.exists(vout)):
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
        for i in range(int(round(TOTAL * FPS))): enc.stdin.write(frame_at(i / FPS).tobytes())
        enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", ME, "-ar", "48000", "-ac", "2", f"{V}/me48.wav"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", CL, "-ar", "48000", "-ac", "2", f"{V}/cl48.wav"], check=True)
    srcw = {"me": R.readw(f"{V}/me48.wav") * float(os.environ.get("MEG", "0.55")), "cl": R.readw(f"{V}/cl48.wav") * float(os.environ.get("CLG", "1.15"))}
    vt = np.zeros((n, 2), np.float32); f = int(0.03 * SR)
    def rms(c): v = c[np.abs(c).max(1) > 0.01]; return float(np.sqrt((v ** 2).mean())) if len(v) else 1e-6
    ref = {k: np.median([rms(srcw[k][int(s["a"] * SR):int(s["b"] * SR)]) for s in segs if s["src"] == k]) for k in srcw}
    for s in segs:
        if s["src"] == "-": continue
        c = srcw[s["src"]][int(s["a"] * SR):int(s["b"] * SR)].copy(); c *= min(2.0, ref[s["src"]] / rms(c))
        c[:f] *= np.linspace(0, 1, f)[:, None]; c[-f:] *= np.linspace(1, 0, f)[:, None]
        o = int(s["t0"] * SR); vt[o:o + len(c)] += c[:n - o]
    R.writew(f"{V}/voice.wav", vt)
    bed = R.readw(f"{V}/bed.wav"); L = min(len(bed), n); tl = np.arange(L) / SR
    gain = 0.07 * np.clip(tl / 1.0, 0, 1) * np.where((tl > segs[1]["t0"]) & (tl < segs[7]["t0"]), 4.4, 1.0) * np.clip(1 - (tl - (TOTAL - 1.6)) / 1.5, 0, 1)
    sg = np.zeros((n, 2), np.float32); sg[:L] = bed[:L] * gain[:, None]; R.writew(f"{V}/song.wav", sg)
    ev = [(0.0, sfx.whoosh(0.4), 0.2), (0.05, sfx.click(), 0.8), (0.3, sfx.thud(0.4), 0.3), (END_IN - 0.3, sfx.whoosh(0.6), 0.25),
          (FLIP_NEXT, sfx.click(), 0.8), (FLIP_NEXT + 0.25, sfx.thud(0.4), 0.3), (segs[1]["t0"] - 0.12, sfx.whoosh(0.45), 0.22), (segs[7]["t0"] - 0.12, sfx.whoosh(0.45), 0.22)]
    ev += [(v - 0.1, sfx.paper(), 0.5) for v in SWAPS]
    ev += [(a, sfx.whoosh(0.35), 0.24) for a, *_ in BIG] + [(a + 0.26, sfx.click(), 0.75) for a, *_ in BIG] + [(a + 0.26, sfx.thud(0.3), 0.18) for a, *_ in BIG]
    ev += [(a, sfx.click(), 0.35) for a, *_ in PILLS] + [(a, sfx.siga(), 0.16) for a, b in CTA]
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=70,acompressor=threshold=0.08:ratio=2.5:attack=8:release=200:makeup=1.6,asplit=2[vox][k2];[2:a]volume=0.8[sf];[3:a]volume=0.95[sg];"
                    "[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][sgd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
