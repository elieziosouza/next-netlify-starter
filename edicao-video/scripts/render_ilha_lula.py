"""Corte: Lula entra no caso da ilha do Richarlison (vídeo dele nas redes) depois do meu vídeo da ilha passar de 64 mil views.
Ele abre em tela cheia; o print do vídeo da ilha com as views; o Lula em trechos de frase inteira (sem a legenda queimada dele),
com o outro lado na tela (Flávio nega; Willer Tomaz contesta e pediu a retirada dos vídeos; posse dada em 2025 a empresa ligada a Tomaz)."""
import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
import sfx
BLUE = (14, 62, 120); PAPER = (247, 244, 236); INK = (22, 26, 34)
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; ease_out = R.ease_out; ease_in = R.ease_in; ease_io = R.ease_io
V = f"{S}/v48"; ME = f"{V}/me.mp4"; CL = f"{V}/cl.mp4"
SHOT = "/root/.claude/uploads/698dd744-d40f-5d96-b9e9-72023ae79dbf/f26217e3-image.jpg"
PARTS = [("me", 0.85, 7.25, None), ("me", 7.85, 13.3, "views"), ("me", 13.65, 19.45, "lprev"),
         ("cl", 20.75, 32.95, "lula"), ("cl", 41.45, 47.75, "lula"), ("cl", 47.85, 58.3, "lula"), ("cl", 58.95, 66.0, "lula")]
segs = []; acc = 0.0
for src_, a, b, card_ in PARTS: segs.append(dict(src=src_, a=a, b=b, t0=acc, t1=acc + b - a, card=card_)); acc += b - a
EDIT_CUT = acc
def seg_at(t):
    for s in segs:
        if t < s["t1"]: return s
    return segs[-1]
def segmap(i, x): return segs[i]["t0"] + x - segs[i]["a"]
FULL = MODE == "full" or MODE.startswith(("frames", "cover"))
MEF = R.decode(ME, 0, 20.4, 720, 1280, "scale=720:1280") if FULL else None
LUY, LUH = 40, 750                                                                 # Lula sem a legenda queimada dele
LUF = R.decode(CL, 8.0, 66.2, 720, LUH, f"crop=720:{LUH}:0:{LUY}") if FULL else None
_shot = np.asarray(Image.open(SHOT).convert("RGB")); VIEWS = _shot[330:1208, 137:1027].copy()  # o vídeo da ilha no meu perfil
PRINT = _shot.copy()                                                               # print inteiro, com as fotos e os nomes de quem comentou desfocados
for x0, y0, x1, y1 in [(40, 1085, 135, 1180), (140, 1092, 385, 1132), (40, 1228, 135, 1322), (140, 1236, 220, 1274), (40, 1372, 135, 1468), (140, 1383, 490, 1420)]:
    a, b, c, d_ = [int(v * 1.17) for v in (x0, y0, x1, y1)]
    PRINT[b:d_, a:c] = cv2.GaussianBlur(PRINT[b:d_, a:c], (0, 0), 14)
_ph = H; _pw = int(PRINT.shape[1] * H / PRINT.shape[0]); PRINT_S = cv2.resize(PRINT, (_pw, _ph), interpolation=cv2.INTER_AREA)
PRINT_BG = np.clip(R.blur_bg(PRINT, 0.35), 0, 255).astype(np.uint8)
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
    u = (t * 0.45) % 2.0
    return 19.6 + (u if u < 1.0 else 2.0 - u)                                       # ele calado, olhando para a câmera
def fit_w(img, w): return cv2.resize(img, (w, int(w * img.shape[0] / img.shape[1])), interpolation=cv2.INTER_LANCZOS4)
def fit_h(img, h): return cv2.resize(img, (int(h * img.shape[1] / img.shape[0]), h), interpolation=cv2.INTER_LANCZOS4)
_vcache = {}
def views_card():
    if "v" in _vcache: return _vcache["v"]
    im = Image.fromarray(fit_h(VIEWS, 520)).convert("RGBA"); d = ImageDraw.Draw(im)
    f = R.BIGF(64); txt = "▶ 64,7 MIL VIEWS"; tw = R.MF("ExtraBold", 40).getlength(txt)
    d.rounded_rectangle((im.width / 2 - 200, im.height - 96, im.width / 2 + 200, im.height - 24), 18, fill=(0, 0, 0, 200))
    d.text((im.width / 2, im.height - 60), "64,7 MIL VIEWS", font=R.BIGF(50), fill=R.GOLD_L + (255,), anchor="mm")
    _vcache["v"] = np.asarray(im.convert("RGB")); return _vcache["v"]
def card_img(s, x):
    if s["card"] == "views": return views_card(), "Print do meu TikTok"
    u = (x - 7.0) * 0.9 + 8.3 if s["card"] == "lprev" else x                      # prévia do Lula sem som enquanto ele fala
    return fit_h(fr_of(LUF, u - 8.0), 520), "Vídeo: reprodução redes sociais (Lula)"
def persp_top(rgba, a):
    h, w = rgba.shape[:2]; src = np.float32([[0, 0], [w, 0], [w, h], [0, h]]); dst = np.float32([[w * a, h * a * 0.35], [w * (1 - a), h * a * 0.35], [w, h], [0, h]])
    return cv2.warpPerspective(rgba, cv2.getPerspectiveTransform(src, dst), (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
ME_CAPS = [("PESSOAL, EU TINHA FEITO UM VÍDEO", 0.92, 2.9), ("FALANDO DESSE CASO DO RICHARLISON,", 2.9, 4.9), ("QUE DIZ QUE TOMARAM A ILHA DELE", 4.9, 6.2), ("NA MÃO GRANDE.", 6.2, 7.14),
           ("LÁ NO TIKTOK", 7.96, 9.2), ("ELE TÁ EM MAIS OU MENOS", 9.2, 11.2), ("65 MIL VIEWS JÁ.", 11.2, 13.19),
           ("AGORA O NOSSO PRESIDENTE TÁ FALANDO", 13.75, 15.6), ("QUE VAI MANDAR A POLÍCIA FEDERAL INVESTIGAR.", 15.6, 17.16), ("DÁ UMA OLHADA AÍ", 17.56, 18.4), ("NO QUE O PRESIDENTE DISSE.", 18.4, 19.37)]
CL_CAPS = [("E, DE REPENTE, ELE", 20.9, 21.9), ("VIU A ILHA DELE DESAPARECER.", 21.9, 23.0), ("O ADVOGADO WILLER TOMAZ,", 23.0, 25.5), ("AMIGO DO FLÁVIO BOLSONARO,", 25.5, 26.9),
           ("E O FLÁVIO BOLSONARO", 26.9, 28.0), ("FORAM NA ILHA DESSE RAPAZ,", 28.0, 30.2), ("FILMARAM A ILHA COM DRONE, SABE,", 30.2, 32.8),
           ("ESSE WILLER TOMAZ,", 41.75, 42.9), ("POSSIVELMENTE COM AJUDA DO FLÁVIO,", 42.9, 45.0), ("CONSEGUIU TOMAR A ILHA", 45.0, 46.5), ("DO RICHARLISON.", 46.5, 47.55),
           ("TÔ PEDINDO PRA POLÍCIA FEDERAL INVESTIGAR,", 47.96, 50.0), ("PRA SABER AONDE É", 50.0, 51.0), ("QUE FOI FEITO O TRAMBIQUE QUE TIRARAM", 51.0, 54.2),
           ("DO PAI DO BEBÊ", 55.06, 56.0), ("UMA ILHA QUE ELE TINHA PAGADO DEZ MILHÕES.", 56.0, 58.2),
           ("NÓS ESTAMOS INVESTIGANDO.", 59.1, 60.2), ("PODE FICAR CERTO, MEU QUERIDO,", 60.2, 62.0), ("NÓS VAMOS DAR A VERDADE PRA VOCÊ.", 62.0, 63.6),
           ("TENHA PACIÊNCIA, QUE AS COISAS", 63.6, 64.9), ("VÃO SER ESCLARECIDAS.", 64.9, 65.9)]
HOT = {"RICHARLISON,", "MÃO", "GRANDE.", "65", "VIEWS", "POLÍCIA", "FEDERAL", "DRONE,", "POSSIVELMENTE", "TOMAR", "INVESTIGAR,", "MILHÕES.", "VERDADE", "PACIÊNCIA,"}
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
BIG = [(0, 3.2, 4.9, "RICHARLISON", R.GOLD_L), (2, 15.6, 17.2, "POLÍCIA FEDERAL", R.GOLD_L),
       (3, 30.4, 32.9, "DRONE", R.WHITE), (4, 42.9, 45.0, "“POSSIVELMENTE”", R.GOLD_L), (5, 56.0, 58.2, "R$ 10 MILHÕES", R.WHITE), (6, 63.6, 65.9, "PACIÊNCIA", R.GOLD_L)]
BIG = [(segmap(i, a), segmap(i, b), w, c) for i, a, b, w, c in BIG]
PILLS = [(3, 20.9, 26.9, "LULA, EM VÍDEO NAS REDES", R.NAVY),
         (3, 27.0, 32.9, "O OUTRO LADO: FLÁVIO NEGA TER RELAÇÃO COM A ILHA", R.NAVY), (4, 41.75, 47.6, "WILLER TOMAZ CONTESTA O JOGADOR", R.NAVY),
         (5, 48.0, 53.0, "TOMAZ PEDIU À JUSTIÇA A RETIRADA DOS VÍDEOS DO JOGADOR", R.NAVY), (5, 53.2, 58.2, "EM 2025, A POSSE FOI DADA A EMPRESA LIGADA A TOMAZ", R.NAVY)]
PILLS = [(segmap(i, a), segmap(i, b), x, c) for i, a, b, x, c in PILLS]
EDIT_END = EDIT_CUT; FIN_IN = EDIT_END; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = FIN_IN; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
CARD = ("ILHA DO RICHARLISON", ["LULA PEDE À PF", "PARA INVESTIGAR"])
CTA = [(segmap(1, 8.0), segmap(1, 13.2))]
def cta_level(t): return max([clamp((t - a) / 0.4) * clamp((b - t) / 0.4) for a, b in CTA] + [0.0])
SPLIT_T, SPLIT_END = segs[2]["t0"], EDIT_END + 10
SWAPS = [segs[3]["t0"]]
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
        bg = R.blur_bg(card, 0.28)
        frame = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
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
            if 0 <= t - sw < 0.5: cy0 += 300 * (1 - ease_out((t - sw) / 0.5))
        R.paste(frame, R.fade(Image.fromarray(cardi, "RGBA"), clamp(kin * 1.6)), CX - cw / 2, cy0 + 380 * (1 - kin), 0.6, 22, (10, 26))
        R.credit(frame, cred, CX, 1820, kin, anchor="mm")
        big_word(frame, t, (WIN_Y + WIN_H + 20, cy0 - 22))
        for a, b, txt, colr in PILLS:
            if a <= t < b: R.pill(frame, txt, CX, cy0 + ch + 30, clamp((t - a) / 0.3) * clamp((b - t) / 0.25) * kin, fill=colr, size=pill_size(txt))
        kc = card_k(t)
        if kc > 0: BAR.lower_card(frame, CARD[0], CARD[1], CARD_Y_SPLIT, kc, fs=36)
        caption(frame, t, CAP_Y_SPLIT, 42, ("me", "au"))
    else:
        if s is segs[1]:                                                        # print inteiro do TikTok num cartão alto, aproximando das views
            u = t - s["t0"]; z = 1.0 + 0.18 * ease_io(clamp((u - 1.0) / 3.8))
            PH_, PW_ = 1380, int(1380 * PRINT.shape[1] / PRINT.shape[0]); py0 = 150
            big_ = cv2.resize(PRINT, (int(PW_ * z), int(PH_ * z)), interpolation=cv2.INTER_AREA)
            ox, oy = int((big_.shape[1] - PW_) * 0.05), int((big_.shape[0] - PH_) * 0.98); card = big_[oy:oy + PH_, ox:ox + PW_]
            frame = Image.fromarray(PRINT_BG).convert("RGBA")
            kin = ease_out(u / 0.35); R.paste(frame, R.fade(Image.fromarray(R.rounded(card, 30, 5)), kin), CX - PW_ / 2, py0 + 80 * (1 - kin), 0.6, 22, (10, 26))
            vx = CX - PW_ / 2 + (117 / 1080 * PW_ * z - ox); vy = py0 + (2229 / 2340 * PH_ * z - oy)
            ring = clamp((u - 1.4) / 0.4); dr = ImageDraw.Draw(frame)
            if ring > 0:
                dr.rounded_rectangle((vx - 34, vy - 42, vx + 190, vy + 42), 28, outline=R.GOLD_L + (int(255 * ring),), width=8)
                st = Image.new("RGBA", (330, 130), (0, 0, 0, 0)); ds = ImageDraw.Draw(st)
                ds.rounded_rectangle((6, 6, 324, 124), 22, fill=R.GOLD_L + (255,), outline=R.NAVY + (255,), width=6)
                ds.text((165, 66), "64,7 MIL!", font=R.BIGF(78), fill=R.NAVY + (255,), anchor="mm")
                st = st.rotate(-6, resample=Image.BICUBIC, expand=True); kk = ease_out(ring)
                st = st.resize((max(2, int(st.width * kk)), max(2, int(st.height * kk))), Image.BICUBIC)
                frame.alpha_composite(st, (int(vx + 260 - st.width / 2), int(vy - 40 - st.height / 2)))
            win = Image.fromarray(R.rounded(cv2.resize(cv2.LUT(me_big(x)[200:1400], R.LUT), (280, 280), interpolation=cv2.INTER_AREA), 140, 4))
            R.paste(frame, win, W - 320, 110, 0.55, 18, (6, 16))
            caption(frame, t, 1650, 46, ("me", "au"))
            BAR.draw_bar(frame, clamp(t / END_IN), "canal", ease_out((t - 0.2) / 0.6), cta_level(t), 0.5 + 0.5 * math.sin(t * 5)); R.draw_banners(frame, t)
            return frame.convert("RGB")
        frame = Image.fromarray(np.clip(me_full(x), 0, 255).astype(np.uint8)).convert("RGBA")
        big_word(frame, t, (130, 430))
        caption(frame, t, 1500, 48, ("me", "au")); kc = card_k(t)
        if kc > 0: BAR.lower_card(frame, CARD[0], CARD[1], 1655, kc, fs=40)
    BAR.draw_bar(frame, clamp(t / END_IN), "canal", ease_out((t - 0.2) / 0.6), cta_level(t), 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(frame, t)
    for e in [segs[1]["t0"]] + SWAPS:
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
    gain = 0.05 * np.clip(tl / 1.0, 0, 1) * np.where(tl < segs[3]["t0"], 1.0, 0.0) + 0.09 * np.clip((tl - (EDIT_END - 0.3)) / 0.5, 0, 1)
    gain = gain * np.clip(1 - (tl - (TOTAL - 1.6)) / 1.5, 0, 1)                                    # sem trilha por baixo do Lula (o vídeo dele já tem música)
    sg = np.zeros((n, 2), np.float32); sg[:L] = bed[:L] * gain[:, None]; R.writew(f"{V}/song.wav", sg)
    ev = [(0.0, sfx.whoosh(0.4), 0.2), (END_IN - 0.3, sfx.whoosh(0.6), 0.25),
          (segs[1]["t0"] - 0.12, sfx.whoosh(0.45), 0.22)]
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
