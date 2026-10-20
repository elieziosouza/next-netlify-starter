"""Corte viral: Lula autoriza a quebra dos próprios sigilos e da família no TSE (CNN Brasil, 20/10/2026), com a condição de o Flávio fazer
o mesmo. Gancho em tela cheia com a CNN; ele na janela de cima com a foto do debate, o documento do TSE e a CNN no cartão embaixo;
fecha nele com "dia 25 vai ser inevitável" + L e vai dar PT. Palavras grandes medidas para caber na faixa livre."""
import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
import sfx
BLUE = (14, 62, 120)                                                # azul do canal para destaques (no lugar do vermelho)
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; ease_out = R.ease_out; ease_in = R.ease_in; ease_io = R.ease_io
V = f"{S}/v43"; ME = f"{V}/me.mp4"; CL = f"{V}/cl.mp4"
PARTS = [("me", 1.6, 11.3), ("cl", 26.15, 30.42), ("cl", 97.95, 126.6), ("me", 14.0, 19.6)]   # a fala da repórter só corta em fim de frase   # começa nele em tela cheia (pedido de 20/10)
segs = []; acc = 0.0
for src_, a, b in PARTS: segs.append(dict(src=src_, a=a, b=b, t0=acc, t1=acc + b - a)); acc += b - a
EDIT_CUT = acc
def seg_at(t):
    for s in segs:
        if t < s["t1"]: return s
    return segs[-1]
def segmap(i, x): return segs[i]["t0"] + x - segs[i]["a"]
FULL = MODE == "full" or MODE.startswith(("frames", "cover"))
MEF = R.decode(ME, 0, 21.0, 720, 1280, "scale=720:1280") if FULL else None
TVY, TVH = 656, 428                                                 # o quadro da TV dentro do vídeo deles (fora a tarja, a manchete e a faixa da CNN)
CLR = {k: (a, R.decode(CL, a, b, 1080, TVH, f"crop=1080:{TVH}:0:{TVY}")) for k, a, b in [("h", 26.0, 30.6), ("p", 117.3, 126.7)]} if FULL else {}
def tv_at(x):
    for a, arr in CLR.values():
        if a <= x <= a + len(arr) / FPS: return arr[int(clamp((x - a) * FPS, 0, len(arr) - 1))]
    return list(CLR.values())[0][1][0]
def fr_of(arr, x): return arr[int(clamp(x * FPS, 0, len(arr) - 1))]
def me_big(x): return cv2.resize(fr_of(MEF, x), (1080, 1920), interpolation=cv2.INTER_LINEAR)
# cartões: a foto do debate, o documento do TSE mostrado pela CNN (recorte legível) e a própria CNN
FOTO = np.asarray(Image.open(f"{V}/foto.jpg").convert("RGB"))
_d = subprocess.run(["ffmpeg", "-v", "error", "-ss", "40", "-i", CL, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
DOC = np.frombuffer(_d, np.uint8).reshape(1920, 1080, 3)[TVY:TVY + TVH, 30:600].copy()
PHOTO = FOTO
FIT = 0.88; _fw, _fh = int(W * FIT), int(H * FIT); _fx = CX - _fw // 2; _fy = H - _fh
_fm = np.ones((_fh, _fw), np.float32); _fm[:, :30] = np.linspace(0, 1, 30)[None, :]; _fm[:, -30:] = np.linspace(1, 0, 30)[None, :]; _fm[:30] *= np.linspace(0, 1, 30)[:, None]; _fm = _fm[..., None]
def me_full(x):
    img = me_big(x); bg = cv2.resize(cv2.GaussianBlur(cv2.resize(img, (W // 10, H // 10)), (0, 0), 2.5), (W, H)).astype(np.float32) * 0.7
    fg = cv2.resize(cv2.LUT(img, R.LUT), (_fw, _fh), interpolation=cv2.INTER_AREA).astype(np.float32)
    bg[_fy:, _fx:_fx + _fw] = bg[_fy:, _fx:_fx + _fw] * (1 - _fm) + fg * _fm
    return bg
# layout do resumo v3
WIN_W, WIN_H, WIN_Y = 444, 592, 112; WIN_X = CX - WIN_W // 2      # janela dele maior (pedido de 20/10)
CRD_Y, CRD_H = 850, 520; CARD_Y_SPLIT = CRD_Y + CRD_H + 124; CAP_Y_SPLIT = 1744   # faixa do cartão; selos na borda de baixo, palavra grande livre em cima
def win_img(x): return cv2.resize(cv2.LUT(me_big(x)[40:1480], R.LUT), (WIN_W, WIN_H), interpolation=cv2.INTER_AREA)
def listen_x(t):
    u = (t * 0.7) % 5.2
    return 11.3 + (u if u < 2.6 else 5.2 - u)                     # ele calado ouvindo (11,3 a 13,9 s), em vaivém
def fit_w(img, w): return cv2.resize(img, (w, int(w * img.shape[0] / img.shape[1])), interpolation=cv2.INTER_LANCZOS4)
def tv_card(x, w): return fit_w(tv_at(x)[30:], w)                 # sem a marca da emissora no alto da imagem
def doc_card(x, w, t):
    z = 1.0 + 0.08 * clamp((x - 98.1) / 20)                         # aproxima devagar no documento
    im = fit_w(DOC, int(w * z)); h = int(w * DOC.shape[0] / DOC.shape[1]); y0 = (im.shape[0] - h) // 4; x0 = (im.shape[1] - w) // 2
    return im[y0:y0 + h, x0:x0 + w]
def persp_top(rgba, a):
    h, w = rgba.shape[:2]; src = np.float32([[0, 0], [w, 0], [w, h], [0, h]]); dst = np.float32([[w * a, h * a * 0.35], [w * (1 - a), h * a * 0.35], [w, h], [0, h]])
    return cv2.warpPerspective(rgba, cv2.getPerspectiveTransform(src, dst), (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
# legendas por trecho (tempo de cada arquivo)
ME_CAPS = [("VOCÊ VIU ISSO AQUI?", 1.7, 2.75), ("O LULA JÁ ABRIU O SIGILO BANCÁRIO DELE", 2.75, 4.6), ("E DE TODA A FAMÍLIA DELE.", 4.6, 6.1),
           ("AGORA TÁ SÓ AGUARDANDO", 6.65, 7.9), ("O FLÁVIO BOLSONARO", 7.9, 8.8), ("FAZER A MESMA COISA.", 8.8, 9.7), ("DÁ UMA OLHADINHA NESSA MATÉRIA.", 9.85, 11.25),
           ("DIA 25", 14.05, 15.1), ("VAI SER INEVITÁVEL.", 15.55, 16.75)]
CL_CAPS = [("LULA JÁ AUTORIZOU", 26.2, 27.45), ("A QUEBRA DE SIGILO", 27.45, 28.6), ("OFICIALMENTE DELE…", 28.6, 29.5), ("E DA FAMÍLIA.", 29.95, 30.4),
           ("EM DECORRÊNCIA DO DESAFIO", 98.15, 99.9), ("LANÇADO DURANTE", 99.9, 100.7), ("O DEBATE PRESIDENCIAL", 100.7, 102.0), ("AO QUAL ME REFERIA,", 102.0, 102.8),
           ("NA REDE BANDEIRANTES DE COMUNICAÇÃO,", 103.65, 105.6), ("AUTORIZAR", 105.6, 106.5), ("A LIBERAÇÃO DOS SIGILOS", 107.0, 109.6), ("BANCÁRIO E FISCAL", 109.9, 111.4),
           ("E TELEFÔNICO", 112.3, 113.2), ("DE SUA PESSOA FÍSICA", 113.9, 115.5), ("E DE SEUS FAMILIARES.", 115.9, 117.1),
           ("E AÍ NÓS TEMOS AQUI", 117.82, 119.1), ("O NOME DESSES FAMILIARES", 119.45, 120.95), ("QUE EU VOU CONTAR PRA VOCÊS.", 120.95, 122.2),
           ("ROSÂNGELA LULA DA SILVA,", 122.65, 124.5), ("ESPOSA DO PRESIDENTE DA REPÚBLICA.", 124.5, 126.4)]
HOT = {"ABRIU", "SIGILO", "BANCÁRIO", "FAMÍLIA", "FLÁVIO", "MESMA", "AUTORIZOU", "QUEBRA", "FAMÍLIA.", "DESAFIO", "DEBATE", "AUTORIZAR", "SIGILOS", "FISCAL", "TELEFÔNICO",
       "FAMILIARES.", "ESPOSA", "25", "INEVITÁVEL.", "MATÉRIA."}
CAPS = []
for i, s in enumerate(segs):
    for txt, a, b in (ME_CAPS if s["src"] == "me" else CL_CAPS):
        a, b = max(a, s["a"]), min(b, s["b"])
        if b - a < 0.25: continue
        a2, b2 = segmap(i, a), segmap(i, b); ws = txt.split(); tot = sum(len(w) + 2 for w in ws); k = 0; ts = []
        for w in ws: ts.append(a2 + (b2 - a2 - 0.1) * k / tot); k += len(w) + 2
        CAPS.append(dict(words=ws, ts=ts, start=a2, end=b2, src="au" if any(w in HOT for w in ws) else "me"))
CAPS.sort(key=lambda c: c["start"]); R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
BIG = [(1, 27.45, 29.5, "QUEBRA DE SIGILO", R.GOLD_L), (0, 2.75, 4.6, "JÁ ABRIU", R.GOLD_L), (0, 7.9, 9.7, "E O FLÁVIO?", R.GOLD_L),
       (2, 103.65, 105.6, "DEBATE DA BAND", R.WHITE), (2, 109.9, 111.4, "BANCÁRIO E FISCAL", R.GOLD_L), (2, 112.3, 113.4, "TELEFÔNICO", R.WHITE),
       (2, 115.9, 117.15, "E DA FAMÍLIA", R.GOLD_L), (2, 124.4, 126.4, "ATÉ A JANJA", R.GOLD_L), (3, 14.05, 15.1, "DIA 25", R.GOLD_L), (3, 15.55, 16.75, "INEVITÁVEL", R.GOLD_L)]
BIG = [(segmap(i, a), segmap(i, b), w, c) for i, a, b, w, c in BIG]
PILLS = [(0, 2.75, 6.1, "SEGUNDO A CNN BRASIL: PEDIDO FEITO AO TSE", R.NAVY), (0, 6.65, 9.7, "CONDIÇÃO: O FLÁVIO AUTORIZAR O MESMO", BLUE),
         (2, 98.15, 102.8, "PETIÇÃO CÍVEL NO TSE · 20/10/2026", R.NAVY), (2, 103.65, 109.6, "O DESAFIO FOI FEITO NO DEBATE DA BAND", R.NAVY),
         (2, 122.65, 126.4, "ROSÂNGELA (JANJA), ESPOSA DO PRESIDENTE", R.NAVY)]
PILLS = [(segmap(i, a), segmap(i, b), x, c) for i, a, b, x, c in PILLS]
FIN_IN = segmap(3, 16.8); FIN_LEN = EDIT_CUT - FIN_IN; MUS_IN = FIN_IN - (9.45 - FIN_LEN)
R.MUS_IN = MUS_IN; R.FIN_IN = FIN_IN; EDIT_END = EDIT_CUT; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.END_IN = END_IN; R.EDIT_END = EDIT_END
CARD = ("DESAFIO DO SIGILO", ["O LULA AUTORIZOU.", "E O FLÁVIO?"])
CTA = [(segmap(2, 107.0), segmap(2, 111.4)), (segmap(3, 14.05), segmap(3, 16.75))]
def cta_level(t): return max([clamp((t - a) / 0.4) * clamp((b - t) / 0.4) for a, b in CTA] + [0.0])
SPLIT_T, SPLIT_END = segs[1]["t0"], segs[3]["t0"]
def caption(frame, t, y, size, tracks):
    old = R.RED; R.RED = BLUE                                       # palavra quente da legenda em azul do canal
    try: R.draw_caption(frame, t, y, size, tracks)
    finally: R.RED = old
def big_word(frame, t, zone):
    """palavra grande sempre dentro da faixa livre (zone = topo, base): mede o texto de verdade e reduz até caber, sem encostar em nada"""
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
    while R.MF("ExtraBold", size).getlength(txt) + 50 > 660: size -= 1          # selo nunca passa da largura segura
    return size
def card_k(t):
    k = ease_out((t - 0.6) / 0.4) * (1 - ease_in((t - (FIN_IN - 0.35)) / 0.35))
    if SPLIT_T - 0.35 <= t < SPLIT_T + 0.6: k *= clamp((SPLIT_T - t) / 0.35)            # some antes de ele encolher
    elif SPLIT_T + 0.6 <= t < SPLIT_T + 0.95: k *= (t - SPLIT_T - 0.6) / 0.35           # e volta só com ele já na janela
    if abs(t - SPLIT_END) < 0.35: k *= abs(t - SPLIT_END) / 0.35
    return k
FREEZE = 19.3
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); s = seg_at(tt); x = s["a"] + min(tt, s["t1"] - 0.02) - s["t0"]
    if s is segs[-1] and tt >= FIN_IN: x = min(x, FREEZE)
    if False:                                                      # (sem gancho da CNN: o vídeo começa nele em tela cheia)
        card = tv_card(x, 980); bg = R.blur_bg(tv_at(x), 0.30); frame = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
        pz = 1.10 - 0.10 * ease_out(t / 0.25); hh = card.shape[0]
        img = cv2.resize(card, (int(980 * pz), int(hh * pz)), interpolation=cv2.INTER_LINEAR); y0 = (img.shape[0] - hh) // 2; x0 = (img.shape[1] - 980) // 2
        R.paste(frame, Image.fromarray(R.rounded(img[y0:y0 + hh, x0:x0 + 980], 30, 5)), CX - 490, 360, 0.6, 22, (8, 20))
        R.credit(frame, "Imagens: reprodução CNN Brasil", CX + 490 - 14, 360 + hh - 46, 1.0)
        if t < segmap(0, 27.45):
            fs_ = 104
            while R.BIGF(fs_).getlength("SAIU AGORA NA CNN:") > 660: fs_ -= 2      # cabe na largura segura
            f = R.BIGF(fs_); d = ImageDraw.Draw(frame); k = ease_out(t / 0.2)
            d.text((CX, 230 - 20 * (1 - k)), "SAIU AGORA NA CNN:", font=f, fill=R.GOLD_L + (int(255 * k),), anchor="mm", stroke_width=8, stroke_fill=R.NAVY + (255,))
        big_word(frame, t, (120, 350))
        caption(frame, t, 360 + hh + 190, 54, ("me", "au"))
    elif SPLIT_T <= t < SPLIT_END:
        mex = x if s["src"] == "me" else listen_x(t)
        if s is segs[2] and x < 117.5: card = doc_card(x, 640, t); kind = "doc"
        else: card = tv_card(x, 880); kind = "tv"
        bg = R.blur_bg(card, 0.28); frame = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
        u = t - SPLIT_T; kw = ease_io(u / 0.55)
        kin = ease_out((u - 0.3) / 0.6)                     # ele encolhe da tela cheia até a janela de cima
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
        sw = s["t0"] if s is segs[2] and x < 117.5 else segmap(2, 117.5) if s is segs[2] else None
        if sw is not None and 0 <= t - sw < 0.5:                   # troca de cartão: o novo sobe
            kk = ease_out((t - sw) / 0.5); cy0 += 300 * (1 - kk)
        R.paste(frame, R.fade(Image.fromarray(cardi, "RGBA"), clamp(kin * 1.6)), CX - cw / 2, cy0 + 380 * (1 - kin), 0.6, 22, (10, 26))
        R.credit(frame, "Foto: reprodução" if kind == "foto" else "Imagens: reprodução CNN Brasil", CX, 1820, kin, anchor="mm")   # crédito embaixo, fora de tudo
        big_word(frame, t, (WIN_Y + WIN_H + 20, cy0 - 22))           # entre a janela e o cartão, sem encostar em nenhum dos dois
        for a, b, txt, colr in PILLS:
            if a <= t < b: R.pill(frame, txt, CX, cy0 + ch + 48, clamp((t - a) / 0.3) * clamp((b - t) / 0.25), fill=colr, size=pill_size(txt))
        kc = card_k(t)
        if kc > 0: BAR.lower_card(frame, CARD[0], CARD[1], CARD_Y_SPLIT, kc, fs=36)
        caption(frame, t, CAP_Y_SPLIT, 42, ("me", "au"))
    else:
        frame = Image.fromarray(np.clip(me_full(x), 0, 255).astype(np.uint8)).convert("RGBA")
        big_word(frame, t, (130, 430))
        if tt < FIN_IN:
            for a, b, txt, colr in PILLS:
                if a <= t < b: R.pill(frame, txt, CX, 1392, clamp((t - a) / 0.3) * clamp((b - t) / 0.25), fill=colr, size=pill_size(txt))
            caption(frame, t, 1500, 48, ("me", "au")); kc = card_k(t)
            if kc > 0: BAR.lower_card(frame, CARD[0], CARD[1], 1655, kc, fs=40)
        else: R.lyrics(frame, t)
    BAR.draw_bar(frame, clamp(t / END_IN), "canal", ease_out((t - 0.2) / 0.6), cta_level(t), 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(frame, t)
    for e in [sg["t0"] for sg in segs[1:]] + [segmap(2, 117.5)]:
        if abs(t - e) < 0.09: frame = Image.blend(frame, Image.new("RGBA", frame.size, (255, 255, 255, 255)), (1 - abs(t - e) / 0.09) * 0.4)
    if t >= END_IN: frame.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return frame.convert("RGB")

def main():
    if MODE in ("lib", "cover"): return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(t).resize((360, 640), Image.LANCZOS) for t in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    if MODE == "info": print("TOTAL", round(TOTAL, 2), [(p[0], round(s["t0"], 2)) for p, s in zip(PARTS, segs)], "FIN", round(FIN_IN, 2)); return
    vout = f"{V}/video.mp4"
    if not (os.environ.get("REUSE") and os.path.exists(vout)):     # REUSE=1: só refaz o áudio
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
        for i in range(int(round(TOTAL * FPS))): enc.stdin.write(frame_at(i / FPS).tobytes())
        enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", ME, "-ar", "48000", "-ac", "2", f"{V}/me48.wav"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", CL, "-ar", "48000", "-ac", "2", f"{V}/cl48.wav"], check=True)
    srcw = {"me": R.readw(f"{V}/me48.wav") * float(os.environ.get("MEG", "0.55")), "cl": R.readw(f"{V}/cl48.wav") * float(os.environ.get("CLG", "1.75"))}
    vt = np.zeros((n, 2), np.float32); f = int(0.03 * SR)
    for s in segs:
        c = srcw[s["src"]][int(s["a"] * SR):int(s["b"] * SR)].copy(); c[:f] *= np.linspace(0, 1, f)[:, None]; c[-f:] *= np.linspace(1, 0, f)[:, None]
        o = int(s["t0"] * SR); vt[o:o + len(c)] += c[:n - o]
    R.writew(f"{V}/voice.wav", vt)
    song = R.readw(f"{S}/v15/song_vox.wav"); Ls = min(len(song), n - int(MUS_IN * SR)); tl = np.arange(Ls) / SR; lead = FIN_IN - MUS_IN
    gain = np.where(tl < lead, 10 ** ((-22 + 22 * tl / lead) / 20), 1.0) * np.clip(1 - (tl - (TOTAL - MUS_IN - 1.6)) / 1.5, 0, 1)
    sg = np.zeros((n, 2), np.float32); sg[int(MUS_IN * SR):int(MUS_IN * SR) + Ls] = song[:Ls] * gain[:, None]; R.writew(f"{V}/song.wav", sg)
    ev = [(0.0, sfx.whoosh(0.4), 0.2), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
    ev += [(sg_["t0"] - 0.12, sfx.whoosh(0.45), 0.22) for sg_ in segs[1:]] + [(segmap(2, 117.4), sfx.whoosh(0.45), 0.22)]
    ev += [(a, sfx.whoosh(0.35), 0.24) for a, *_ in BIG] + [(a + 0.26, sfx.click(), 0.75) for a, *_ in BIG] + [(a + 0.26, sfx.thud(0.3), 0.18) for a, *_ in BIG]   # palavra grande: sopro, clique e batida leve
    ev += [(a, sfx.click(), 0.35) for a, *_ in PILLS] + [(a, sfx.siga(), 0.16) for a, b in CTA]   # siga: duas notas suaves
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=70,asplit=2[vox][k2];[2:a]volume=0.8[sf];[3:a]volume=0.95[sg];"
                    "[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][sgd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
