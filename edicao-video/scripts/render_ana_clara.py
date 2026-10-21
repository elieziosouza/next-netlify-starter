"""Corte: caso Ana Clara (roteiro gravado por ele em 21/10/2026). Começa nele em tela cheia; na matéria ele vai para a janela de cima e o cartão
mostra a peça da campanha (ICL, sem o áudio), o recorte da Folha e a mãe (Cristiane) em dois trechos curtos, sem "monstro" nem "assassino".
Proteção jurídica: o PM aparece como réu/acusado, com a negativa dele (Folha) e a resposta do Flávio. Sem jingle no final: trilha própria triste."""
import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
import sfx
BLUE = (14, 62, 120)
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; ease_out = R.ease_out; ease_in = R.ease_in; ease_io = R.ease_io
V = f"{S}/v45"; ME = f"{V}/me.mp4"; MA = f"{V}/mae/mae.mp4"; IC = f"{S}/v44/src.mp4"
POSTER = "/root/.claude/uploads/698dd744-d40f-5d96-b9e9-72023ae79dbf/6b5d6b3b-image.jpg"
# (fonte, início, fim, cartão, início do cartão no vídeo de origem)
PARTS = [("me", 0.44, 2.33, None, 0), ("me", 2.82, 6.77, None, 0),
         ("ma", 26.55, 30.7, "ma", 26.55),
         ("me", 7.2, 11.41, "ic", 0.6), ("me", 12.1, 13.97, "ic", 4.81),
         ("me", 14.84, 17.55, "folha", 0), ("me", 18.4, 19.87, "folha", 2.71),
         ("me", 20.44, 24.29, "ic", 18.6), ("me", 24.88, 26.39, "ic", 22.45),
         ("me", 27.14, 33.23, "ic", 8.3),
         ("ma", 133.6, 137.25, "ma", 133.6),
         ("me", 33.76, 36.93, "ic", 24.0), ("me", 37.24, 38.39, "ic", 27.17),
         ("me", 39.18, 42.35, "ic", 19.0), ("me", 43.04, 47.43, "mamudo", 138.0),
         ("ma", 96.62, 101.2, "ma", 96.62),
         ("me", 48.6, 50.11, None, 0), ("me", 50.84, 53.0, None, 0)]
segs = []; acc = 0.0
for src_, a, b, card_, c0 in PARTS: segs.append(dict(src=src_, a=a, b=b, t0=acc, t1=acc + b - a, card=card_, c0=c0)); acc += b - a
EDIT_CUT = acc
def seg_at(t):
    for s in segs:
        if t < s["t1"]: return s
    return segs[-1]
def segmap(i, x): return segs[i]["t0"] + x - segs[i]["a"]
FULL = MODE == "full" or MODE.startswith(("frames", "cover"))
MEF = R.decode(ME, 0, 7.0, 720, 1280, "scale=720:1280") if FULL else None            # tela cheia do começo, em resolução maior
MEE = R.decode(ME, 48.4, 53.2, 720, 1280, "scale=720:1280") if FULL else None         # tela cheia do fim
MEW = R.decode(ME, 7.0, 60.0, 540, 960, "scale=540:960") if FULL else None            # janela de cima
ICY, ICH = 294, 226                                                                  # só o palco da peça (sem logo, manchete e intérprete)
ICF = R.decode(IC, 0, 30.0, 576, ICH, f"crop=576:{ICH}:0:{ICY}") if FULL else None
MAY, MAH = 110, 620                                                                  # rosto da mãe, sem a legenda queimada e o rodapé
MAC = {k: (a, R.decode(MA, a, b, 720, MAH, f"crop=720:{MAH}:0:{MAY}")) for k, a, b in [("b", 26.45, 30.8), ("v", 133.5, 137.4), ("g", 96.5, 101.3), ("m", 137.8, 142.6)]} if FULL else {}
_pst = np.asarray(Image.open(POSTER).convert("RGB")); FOLHA = _pst[40:604, 20:646].copy()  # recorte da Folha dentro do cartaz
def fr_of(arr, x): return arr[int(clamp(x * FPS, 0, len(arr) - 1))]
def me_big(x):
    if x < 7.0: img = fr_of(MEF, x)
    elif x >= 48.4: img = fr_of(MEE, x - 48.4)
    else: img = fr_of(MEW, x - 7.0)
    return cv2.resize(img, (1080, 1920), interpolation=cv2.INTER_LINEAR)
FIT = 0.88; _fw, _fh = int(W * FIT), int(H * FIT); _fx = CX - _fw // 2; _fy = H - _fh
_fm = np.ones((_fh, _fw), np.float32); _fm[:, :30] = np.linspace(0, 1, 30)[None, :]; _fm[:, -30:] = np.linspace(1, 0, 30)[None, :]; _fm[:30] *= np.linspace(0, 1, 30)[:, None]; _fm = _fm[..., None]
def me_full(x):
    img = me_big(x); bg = cv2.resize(cv2.GaussianBlur(cv2.resize(img, (W // 10, H // 10)), (0, 0), 2.5), (W, H)).astype(np.float32) * 0.7
    fg = cv2.resize(cv2.LUT(img, R.LUT), (_fw, _fh), interpolation=cv2.INTER_AREA).astype(np.float32)
    bg[_fy:, _fx:_fx + _fw] = bg[_fy:, _fx:_fx + _fw] * (1 - _fm) + fg * _fm
    return bg
WIN_W, WIN_H, WIN_Y = 444, 592, 112; WIN_X = CX - WIN_W // 2
CRD_Y, CRD_H = 850, 520; CARD_Y_SPLIT = CRD_Y + CRD_H + 124; CAP_Y_SPLIT = 1744
def win_img(x):
    img = fr_of(MEW, x - 7.0)[20:740]                                                 # mesmo enquadramento da janela (cabeça inteira)
    return cv2.resize(cv2.LUT(img, R.LUT), (WIN_W, WIN_H), interpolation=cv2.INTER_AREA)
def listen_x(t):
    u = (t * 0.7) % 5.0
    return 53.6 + (u if u < 2.5 else 5.0 - u)                                         # ele calado, sério, ouvindo a mãe
def fit_w(img, w): return cv2.resize(img, (w, int(w * img.shape[0] / img.shape[1])), interpolation=cv2.INTER_LANCZOS4)
def fit_h(img, h): return cv2.resize(img, (int(h * img.shape[1] / img.shape[0]), h), interpolation=cv2.INTER_LANCZOS4)
def card_img(s, x):
    u = s["c0"] + x - s["a"]
    if s["card"] == "ic": return fit_w(fr_of(ICF, u), 880), "Imagens: reprodução ICL Notícias / peça da campanha de Lula"
    if s["card"] == "folha":
        z = 1.0 + 0.03 * clamp(u / 4.2); h = 430; im = fit_h(FOLHA, int(h * z)); w = int(h * FOLHA.shape[1] / FOLHA.shape[0])
        y0 = (im.shape[0] - h) // 2; x0 = (im.shape[1] - w) // 2
        return im[y0:y0 + h, x0:x0 + w], "Recorte: Folha de S.Paulo"
    a, arr = next(v for v in MAC.values() if v[0] <= u <= v[0] + len(v[1]) / FPS + 0.2); im = fr_of(arr, u - a)
    return fit_h(im, 440), "Imagens: propaganda eleitoral da Coligação Brasil Pronto pra Mais"
def persp_top(rgba, a):
    h, w = rgba.shape[:2]; src = np.float32([[0, 0], [w, 0], [w, h], [0, h]]); dst = np.float32([[w * a, h * a * 0.35], [w * (1 - a), h * a * 0.35], [w, h], [0, h]])
    return cv2.warpPerspective(rgba, cv2.getPerspectiveTransform(src, dst), (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
# legendas por trecho (tempo do arquivo de origem)
ME_CAPS = [("A ANA CLARA TINHA CINCO ANOS.", 0.54, 2.18), ("FOI ATINGIDA POR UM TIRO DE FUZIL", 2.92, 5.1), ("NA PORTA DE CASA, EM NITERÓI.", 5.1, 6.62),
           ("SEGUNDO O MINISTÉRIO PÚBLICO,", 7.3, 8.9), ("O TIRO SAIU DA ARMA", 8.9, 10.0), ("DE UM POLICIAL MILITAR,", 10.0, 11.26), ("QUE VIROU RÉU PELA MORTE DELA.", 12.2, 13.82),
           ("E SABE QUEM ENTROU", 14.94, 16.1), ("NA DEFESA DESSE POLICIAL?", 16.1, 17.4), ("O FLÁVIO BOLSONARO.", 18.68, 19.72),
           ("ELE ASSINOU UM RECURSO", 20.54, 21.9), ("PRA TENTAR TIRAR O CASO", 21.9, 23.0), ("DO JÚRI POPULAR.", 23.0, 24.14), ("O STJ NEGOU.", 24.98, 26.24),
           ("MAIS DE CINCO ANOS DEPOIS,", 27.24, 29.92), ("A FAMÍLIA DA ANA CLARA", 30.3, 31.7), ("AINDA ESPERA O JULGAMENTO.", 31.7, 33.08),
           ("O FLÁVIO DIZ QUE SÓ FEZ", 33.86, 35.3), ("O TRABALHO DE ADVOGADO.", 35.3, 36.78), ("É DIREITO DELE.", 37.34, 38.24),
           ("MAS A ESCOLHA DE LADO", 39.28, 40.9), ("DIZ MUITO.", 41.0, 42.2), ("QUEM CORREU PRA DEFENDER ESSE POLICIAL", 43.14, 45.3), ("VAI CORRER PRA DEFENDER A SUA FAMÍLIA?", 45.3, 47.28),
           ("DIA 25,", 48.8, 49.96), ("LEMBRA DA ANA CLARA.", 50.94, 52.08)]
MA_CAPS = [("ERA POR VOLTA DE 10 HORAS DA MANHÃ.", 26.65, 28.5), ("ELA ESTAVA NA PORTA", 28.6, 29.5), ("BRINCANDO COM O IRMÃO.", 29.5, 30.4),
           ("EU VI MINHA FILHA MORRER", 133.7, 135.2), ("E NÃO PUDE FAZER NADA", 135.2, 136.2), ("PRA SALVAR ELA.", 136.2, 136.95),
           ("MAS ELE GANHANDO,", 96.7, 97.7), ("EU PERCO TOTAL A ESPERANÇA", 97.7, 99.2), ("DE UM DIA TER JUSTIÇA", 99.2, 100.1), ("PELA MINHA FILHA.", 100.1, 100.87)]
HOT = {"CINCO", "FUZIL", "MINISTÉRIO", "RÉU", "FLÁVIO", "BOLSONARO.", "RECURSO", "JÚRI", "STJ", "NEGOU.", "JULGAMENTO.", "ADVOGADO.", "DIREITO", "LADO",
       "FAMÍLIA?", "25,", "ANA", "CLARA.", "MORRER", "NADA", "JUSTIÇA", "ESPERANÇA"}
CAPS = []
for i, s in enumerate(segs):
    for txt, a, b in (ME_CAPS if s["src"] == "me" else MA_CAPS):
        a, b = max(a, s["a"]), min(b, s["b"])
        if b - a < 0.25: continue
        a2, b2 = segmap(i, a), segmap(i, b); ws = txt.split(); tot = sum(len(w) + 2 for w in ws); k = 0; ts = []
        for w in ws: ts.append(a2 + (b2 - a2 - 0.1) * k / tot); k += len(w) + 2
        CAPS.append(dict(words=ws, ts=ts, start=a2, end=b2, src="au" if any(w in HOT for w in ws) else "me"))
CAPS.sort(key=lambda c: c["start"]); R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
BIG = [(0, 0.54, 2.18, "5 ANOS", R.GOLD_L), (1, 4.3, 6.62, "FUZIL", R.WHITE), (4, 12.2, 13.82, "RÉU", R.GOLD_L),
       (6, 18.68, 19.8, "FLÁVIO", R.GOLD_L), (8, 24.98, 26.3, "STJ NEGOU", R.WHITE), (9, 27.24, 29.92, "+ DE 5 ANOS", R.GOLD_L),
       (14, 45.3, 47.3, "SUA FAMÍLIA?", R.GOLD_L), (16, 48.8, 50.0, "DIA 25", R.GOLD_L), (17, 50.94, 52.4, "ANA CLARA", R.WHITE)]
BIG = [(segmap(i, a), segmap(i, b), w, c) for i, a, b, w, c in BIG]
PILLS = [(2, 26.65, 30.6, "CRISTIANE, MÃE DA ANA CLARA", BLUE), (3, 7.3, 11.3, "DENÚNCIA DO MP-RJ · O PM É RÉU", R.NAVY), (5, 14.94, 19.8, "FOLHA: O CABO NEGA QUE O TIRO SAIU DA ARMA DELE", R.NAVY),
         (7, 20.54, 24.2, "RECURSO NO STJ PARA EVITAR O JÚRI", R.NAVY), (8, 24.98, 26.3, "NEGADO POR 3 VOTOS A 2", BLUE),
         (9, 30.3, 33.1, "O JÚRI AINDA NÃO ACONTECEU", R.NAVY), (10, 133.65, 137.2, "CRISTIANE, MÃE DA ANA CLARA", BLUE),
         (11, 33.86, 38.3, "FLÁVIO DIZ QUE ATUOU COMO ADVOGADO", R.NAVY), (15, 96.66, 101.1, "CRISTIANE, MÃE DA ANA CLARA", BLUE)]
PILLS = [(segmap(i, a), segmap(i, b), x, c) for i, a, b, x, c in PILLS]
EDIT_END = EDIT_CUT; FIN_IN = EDIT_END; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = FIN_IN; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
CARD = ("CASO ANA CLARA", ["FLÁVIO DEFENDEU", "O PM ACUSADO"])
CTA = [(segmap(7, 20.54), segmap(7, 24.2)), (segmap(16, 48.6), segmap(17, 52.0))]
def cta_level(t): return max([clamp((t - a) / 0.4) * clamp((b - t) / 0.4) for a, b in CTA] + [0.0])
SPLIT_T, SPLIT_END = segs[2]["t0"], segs[16]["t0"]
def caption(frame, t, y, size, tracks):
    old = R.RED; R.RED = BLUE
    try: R.draw_caption(frame, t, y, size, tracks)
    finally: R.RED = old
def big_word(frame, t, zone):
    """palavra grande sempre dentro da faixa livre (zone = topo, base): mede o texto de verdade e reduz até caber"""
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
def pill_size(txt, size=30):
    while R.MF("ExtraBold", size).getlength(txt) + 50 > 660: size -= 1
    return size
def card_k(t):
    k = ease_out((t - 0.6) / 0.4) * (1 - ease_in((t - (END_IN - 0.35)) / 0.35))
    if SPLIT_T - 0.35 <= t < SPLIT_T + 0.6: k *= clamp((SPLIT_T - t) / 0.35)
    elif SPLIT_T + 0.6 <= t < SPLIT_T + 0.95: k *= (t - SPLIT_T - 0.6) / 0.35
    if abs(t - SPLIT_END) < 0.35: k *= abs(t - SPLIT_END) / 0.35
    return k
def _cont(p, s): return p["card"] == s["card"] and abs(p["c0"] + p["b"] - p["a"] - s["c0"]) < 0.5
SWAPS = [s["t0"] for j, s in enumerate(segs) if 2 < j < 16 and not _cont(segs[j - 1], s)]          # troca de cartão (o novo sobe)
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); s = seg_at(tt); x = s["a"] + min(tt, s["t1"] - 0.02) - s["t0"]
    if SPLIT_T <= t < SPLIT_END:
        mex = x if s["src"] == "me" else listen_x(t)
        card, cred = card_img(s, x)
        bg = R.blur_bg(card, 0.28); frame = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
        u = t - SPLIT_T; kw = ease_io(u / 0.55)
        if kw < 1:
            full = me_full(segs[1]["b"] - 0.03 if t < SPLIT_T + 0.6 else mex)
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
            if 0 <= t - sw < 0.5: cy0 += 300 * (1 - ease_out((t - sw) / 0.5))       # troca de cartão: o novo sobe
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
        big_word(frame, t, (130, 430))
        for a, b, txt, colr in PILLS:
            if a <= t < b: R.pill(frame, txt, CX, 1392, clamp((t - a) / 0.3) * clamp((b - t) / 0.25), fill=colr, size=pill_size(txt))
        caption(frame, t, 1500, 48, ("me", "au")); kc = card_k(t)
        if kc > 0: BAR.lower_card(frame, CARD[0], CARD[1], 1655, kc, fs=40)
    BAR.draw_bar(frame, clamp(t / END_IN), "canal", ease_out((t - 0.2) / 0.6), cta_level(t), 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(frame, t)
    for e in [segs[2]["t0"], segs[16]["t0"]] + SWAPS:
        if abs(t - e) < 0.09: frame = Image.blend(frame, Image.new("RGBA", frame.size, (255, 255, 255, 255)), (1 - abs(t - e) / 0.09) * 0.4)
    if t >= END_IN: frame.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return frame.convert("RGB")

def main():
    if MODE in ("lib", "cover"): return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(t).resize((360, 640), Image.LANCZOS) for t in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    if MODE == "info":
        print("TOTAL", round(TOTAL, 2), [(p[0], round(s["t0"], 2)) for p, s in zip(PARTS, segs)], "SWAPS", [round(v, 2) for v in SWAPS]); return
    vout = f"{V}/video.mp4"
    if not (os.environ.get("REUSE") and os.path.exists(vout)):
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
        for i in range(int(round(TOTAL * FPS))): enc.stdin.write(frame_at(i / FPS).tobytes())
        enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", ME, "-ar", "48000", "-ac", "2", f"{V}/me48.wav"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", MA, "-ar", "48000", "-ac", "2", f"{V}/ma48.wav"], check=True)
    srcw = {"me": R.readw(f"{V}/me48.wav") * float(os.environ.get("MEG", "0.55")), "ma": R.readw(f"{V}/ma48.wav") * float(os.environ.get("MAG", "0.12"))}
    vt = np.zeros((n, 2), np.float32); f = int(0.03 * SR)
    def rms(c): v = c[np.abs(c).max(1) > 0.01]; return float(np.sqrt((v ** 2).mean())) if len(v) else 1e-6
    ref = {k: np.median([rms(srcw[k][int(s["a"] * SR):int(s["b"] * SR)]) for s in segs if s["src"] == k]) for k in srcw}
    for s in segs:
        c = srcw[s["src"]][int(s["a"] * SR):int(s["b"] * SR)].copy()
        c *= min(2.0, ref[s["src"]] / rms(c))                      # todas as frases dele no mesmo nível (o começo foi gravado mais baixo)
        c[:f] *= np.linspace(0, 1, f)[:, None]; c[-f:] *= np.linspace(1, 0, f)[:, None]
        o = int(s["t0"] * SR); vt[o:o + len(c)] += c[:n - o]
    R.writew(f"{V}/voice.wav", vt)
    bed = R.readw(f"{V}/bed.wav"); L = min(len(bed), n); tl = np.arange(L) / SR
    gain = 0.045 * np.clip(tl / 1.5, 0, 1) * np.where(tl > EDIT_END - 0.5, 1.6, 1.0) * np.clip(1 - (tl - (TOTAL - 1.6)) / 1.5, 0, 1)
    sg = np.zeros((n, 2), np.float32); sg[:L] = bed[:L] * gain[:, None]; R.writew(f"{V}/song.wav", sg)
    ev = [(0.0, sfx.whoosh(0.4), 0.2), (END_IN - 0.3, sfx.whoosh(0.6), 0.25), (segs[2]["t0"] - 0.12, sfx.whoosh(0.45), 0.22), (segs[16]["t0"] - 0.12, sfx.whoosh(0.45), 0.22)]
    ev += [(v - 0.12, sfx.whoosh(0.45), 0.2) for v in SWAPS]
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
