"""Corte viral: Flávio apaga posts do 'bolsa-farelo' (UOL) + áudio da economista do candidato sobre o Bolsa Família.
Gancho em tela cheia com o áudio ("não podem ficar presas pra sempre no Bolsa Família"); depois o layout do resumo v3: ele na janela de
cima, matéria do UOL e o áudio (com forma de onda nossa) no cartão embaixo; fecha nele com "dia 25" + L e vai dar PT. O outro lado em selo."""
import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; ease_out = R.ease_out; ease_in = R.ease_in; ease_io = R.ease_io
V = f"{S}/v42"; ME = f"{V}/me.mp4"; CL = f"{V}/cl.mp4"
PARTS = [("cl", 18.2, 21.65), ("me", 1.3, 15.0), ("cl", 0.15, 25.35), ("me", 20.3, 27.2)]
segs = []; acc = 0.0
for src_, a, b in PARTS: segs.append(dict(src=src_, a=a, b=b, t0=acc, t1=acc + b - a)); acc += b - a
EDIT_CUT = acc
def seg_at(t):
    for s in segs:
        if t < s["t1"]: return s
    return segs[-1]
def segmap(i, x): return segs[i]["t0"] + x - segs[i]["a"]
FULL = MODE == "full" or MODE.startswith(("frames", "cover"))
MEF = R.decode(ME, 0, 29.2, 720, 1280, "scale=720:1280") if FULL else None
def fr_of(arr, x): return arr[int(clamp(x * FPS, 0, len(arr) - 1))]
def me_big(x): return cv2.resize(fr_of(MEF, x), (1080, 1920), interpolation=cv2.INTER_LINEAR)
# fotos dos cartões: a foto do vídeo de terceiros (sem a tarja, a legenda e a logo deles) e a matéria do UOL (sem a logo)
_c = subprocess.run(["ffmpeg", "-v", "error", "-ss", "5", "-i", CL, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
PHOTO = np.frombuffer(_c, np.uint8).reshape(1280, 720, 3)[165:600].copy()
UOL = np.asarray(Image.open(f"{V}/uol.jpg").convert("RGB"))[690:1975].copy()
# forma de onda do áudio (nossa, desenhada a partir do som)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", CL, "-ar", "48000", "-ac", "2", f"{V}/cl48.wav"], check=True)
_aw = R.readw(f"{V}/cl48.wav").mean(1); ENV = np.array([np.sqrt(np.mean(_aw[i:i + 1600] ** 2)) for i in range(0, len(_aw) - 1600, 1600)]); ENV = ENV / (ENV.max() + 1e-6)
def env_at(x): return ENV[int(clamp(x * 30, 0, len(ENV) - 1))]
FIT = 0.88; _fw, _fh = int(W * FIT), int(H * FIT); _fx = CX - _fw // 2; _fy = H - _fh
_fm = np.ones((_fh, _fw), np.float32); _fm[:, :30] = np.linspace(0, 1, 30)[None, :]; _fm[:, -30:] = np.linspace(1, 0, 30)[None, :]; _fm[:30] *= np.linspace(0, 1, 30)[:, None]; _fm = _fm[..., None]
def me_full(x):
    img = me_big(x); bg = cv2.resize(cv2.GaussianBlur(cv2.resize(img, (W // 10, H // 10)), (0, 0), 2.5), (W, H)).astype(np.float32) * 0.7
    fg = cv2.resize(cv2.LUT(img, R.LUT), (_fw, _fh), interpolation=cv2.INTER_AREA).astype(np.float32)
    bg[_fy:, _fx:_fx + _fw] = bg[_fy:, _fx:_fx + _fw] * (1 - _fm) + fg * _fm
    return bg
# layout do resumo v3
WIN_W, WIN_H, WIN_Y = 384, 512, 112; WIN_X = CX - WIN_W // 2
BIG_Y_SPLIT = 678; CRD_Y, CRD_H = 762, 707; CARD_Y_SPLIT = CRD_Y + CRD_H + 70; CAP_Y_SPLIT = 1748
def win_img(x): return cv2.resize(cv2.LUT(me_big(x)[40:1480], R.LUT), (WIN_W, WIN_H), interpolation=cv2.INTER_AREA)
def listen_x(t):
    u = (t * 0.7) % 9.6
    return 15.2 + (u if u < 4.8 else 9.6 - u)                     # ele calado ouvindo (15,2 a 20,0 s), em vaivém
def audio_card(x, w):
    """foto + forma de onda nossa embaixo, no estilo do canal"""
    ph = cv2.resize(PHOTO, (w, int(w * PHOTO.shape[0] / 720)), interpolation=cv2.INTER_LANCZOS4)
    wh = 120; card = np.zeros((ph.shape[0] + wh, w, 3), np.uint8); card[:ph.shape[0]] = ph; card[ph.shape[0]:] = (6, 22, 40)
    im = Image.fromarray(card); d = ImageDraw.Draw(im); n = 46; bw = (w - 80) / n; yc = ph.shape[0] + wh / 2
    for i in range(n):
        v = env_at(x - (n / 2 - i) * 0.03) * (0.55 + 0.45 * abs(math.sin(i * 1.7)))
        hgt = 6 + 84 * v; xx = 40 + i * bw + bw / 2
        d.rounded_rectangle((xx - bw * 0.3, yc - hgt / 2, xx + bw * 0.3, yc + hgt / 2), 3, fill=R.GOLD_L if i % 2 == 0 else (255, 255, 255))
    return np.asarray(im)
def uol_card(x, w): return cv2.resize(UOL, (w, int(w * UOL.shape[0] / UOL.shape[1])), interpolation=cv2.INTER_AREA)
def persp_top(rgba, a):
    h, w = rgba.shape[:2]; src = np.float32([[0, 0], [w, 0], [w, h], [0, h]]); dst = np.float32([[w * a, h * a * 0.35], [w * (1 - a), h * a * 0.35], [w, h], [0, h]])
    return cv2.warpPerspective(rgba, cv2.getPerspectiveTransform(src, dst), (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
# legendas por trecho (tempo de cada arquivo)
ME_CAPS = [("E O FLÁVIO BOLSONARO", 1.4, 3.1), ("APAGA POSTAGENS", 3.3, 4.5), ("EM QUE CRITICAVA O BOLSA FAMÍLIA,", 4.5, 6.6), ("QUE ELE CHAMAVA DE BOLSA FARELO.", 6.6, 7.9),
           ("E VOCÊS VIRAM TAMBÉM O ÁUDIO", 8.6, 10.2), ("DESSA FUTURA MINISTRA DELE?", 10.2, 11.9), ("O QUE ELA FALA A RESPEITO", 11.9, 12.9), ("DO BOLSA FAMÍLIA?", 12.9, 13.6),
           ("DÁ UMA OLHADINHA AÍ.", 13.95, 15.0), ("SÓ SEI QUE DIA 25", 20.4, 21.9), ("A GENTE ESCOLHE", 22.5, 23.4), ("QUEM CUIDA DO POVO.", 23.4, 24.4)]
CL_CAPS = [("E PRINCIPALMENTE QUEM ESTÁ", 0.2, 1.75), ("NO BOLSA FAMÍLIA, ANDRÉ:", 1.75, 3.3), ("VAI TER UMA REGRA DE TRANSIÇÃO", 3.5, 5.7), ("COMO TEVE NA ÉPOCA", 5.7, 6.85),
           ("DO PRESIDENTE BOLSONARO,", 6.85, 7.8), ("DE DOIS ANOS,", 7.8, 9.1), ("PARA QUE POSSA ABRIR O SEU NEGÓCIO", 9.3, 11.3), ("OU ACEITAR UM EMPREGO", 11.6, 13.0),
           ("DE CARTEIRA ASSINADA,", 13.0, 15.0), ("COM UMA REGRA DE TRANSIÇÃO", 15.15, 16.45), ("POR DOIS ANOS.", 16.45, 17.8), ("MAS AS PESSOAS NÃO PODEM", 17.9, 19.55),
           ("FICAR PRESAS PRA SEMPRE", 19.55, 20.5), ("NO BOLSA FAMÍLIA.", 20.5, 21.6), ("AQUILO É UMA PROTEÇÃO,", 21.6, 22.85), ("MAS É O INÍCIO DE UMA JORNADA…", 23.1, 25.3)]
HOT = {"APAGA", "FARELO.", "ÁUDIO", "MINISTRA", "TRANSIÇÃO", "DOIS", "ANOS,", "ANOS.", "PRESAS", "SEMPRE", "PROTEÇÃO,", "JORNADA…", "25", "POVO.", "BOLSONARO,", "NEGÓCIO", "CARTEIRA"}
CAPS = []
for i, s in enumerate(segs):
    for txt, a, b in (ME_CAPS if s["src"] == "me" else CL_CAPS):
        a, b = max(a, s["a"]), min(b, s["b"])
        if b - a < 0.25: continue
        a2, b2 = segmap(i, a), segmap(i, b); ws = txt.split(); tot = sum(len(w) + 2 for w in ws); k = 0; ts = []
        for w in ws: ts.append(a2 + (b2 - a2 - 0.1) * k / tot); k += len(w) + 2
        CAPS.append(dict(words=ws, ts=ts, start=a2, end=b2, src="au" if any(w in HOT for w in ws) else "me"))
CAPS.sort(key=lambda c: c["start"]); R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
BIG = [(0, 19.55, 21.6, "PRESAS PRA SEMPRE?", (235, 60, 60)), (1, 3.3, 4.6, "APAGOU OS POSTS", R.GOLD_L), (1, 6.6, 7.9, "BOLSA FARELO", (235, 60, 60)),
       (1, 13.95, 15.0, "OUÇA O ÁUDIO", R.WHITE), (2, 7.8, 9.1, "2 ANOS", R.GOLD_L), (2, 19.55, 21.6, "PRESAS PRA SEMPRE?", (235, 60, 60)),
       (3, 20.4, 21.9, "DIA 25", (235, 60, 60)), (3, 23.4, 24.4, "QUEM CUIDA DO POVO", R.GOLD_L)]
BIG = [(segmap(i, a), segmap(i, b), w, c) for i, a, b, w, c in BIG]
PILLS = [(1, 3.3, 7.9, "NA IMPRENSA: UOL", R.NAVY), (1, 8.6, 13.6, "NO VÍDEO: “ECONOMISTA DO CANDIDATO”", R.NAVY), (2, 0.2, 7.0, "ÁUDIO DA ECONOMISTA DO CANDIDATO", R.NAVY),
         (2, 21.6, 25.3, "O OUTRO LADO: FLÁVIO DIZ QUE É “DIREITO ADQUIRIDO”", R.NAVY)]
PILLS = [(segmap(i, a), segmap(i, b), x, c) for i, a, b, x, c in PILLS]
FIN_IN = segmap(3, 24.45); FIN_LEN = EDIT_CUT - FIN_IN; MUS_IN = FIN_IN - (9.45 - FIN_LEN)
R.MUS_IN = MUS_IN; R.FIN_IN = FIN_IN; EDIT_END = EDIT_CUT; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.END_IN = END_IN; R.EDIT_END = EDIT_END
CARD = ("BOLSA FAMÍLIA", ["DE “BOLSA FARELO”", "A “PRESAS PRA SEMPRE”"])
CTA = [(segmap(2, 9.3), segmap(2, 13.0)), (segmap(3, 22.5), segmap(3, 24.4))]
def cta_level(t): return max([clamp((t - a) / 0.4) * clamp((b - t) / 0.4) for a, b in CTA] + [0.0])
SPLIT_T, SPLIT_END = segs[1]["t0"], segs[3]["t0"]
def big_word(frame, t, zone):
    """palavra grande sempre dentro da faixa livre (zone = topo, base): mede o texto de verdade e reduz até caber, sem encostar em nada"""
    z0, z1 = zone
    for i, (a, b, word, col) in enumerate(BIG):
        if not (a <= t < b): continue
        u = t - a; k = ease_out(u / 0.28); out = ease_in((t - (b - 0.22)) / 0.22)
        size = 200
        while True:
            f = R.BIGF(size); bb = f.getbbox(word, stroke_width=8)
            if (bb[3] - bb[1]) <= (z1 - z0) - 16 and (bb[2] - bb[0]) <= 680: break
            size -= 4
        lay = Image.new("RGBA", (W, bb[3] - bb[1] + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.text((W / 2 - (bb[0] + bb[2]) / 2, 10 - bb[1]), word, font=f, fill=col + (255,), stroke_width=8, stroke_fill=R.NAVY + (255,))
        dx = (1 if i % 2 == 0 else -1) * W * 0.95 * (1 - k)
        if u < 0.28:
            Lb = int(60 * (1 - k)) + 1
            if Lb > 2: lay = Image.fromarray(cv2.filter2D(np.asarray(lay), -1, np.ones((1, Lb), np.float32) / Lb))
        frame.alpha_composite(R.fade(lay, 1 - out), (int(CX - W / 2 + dx), int((z0 + z1) / 2 - lay.height / 2)))
def pill_size(txt, size=30):
    while R.MF("ExtraBold", size).getlength(txt) + 50 > 660: size -= 1          # selo nunca passa da largura segura
    return size
def card_k(t):
    k = ease_out((t - SPLIT_T - 0.4) / 0.4) * (1 - ease_in((t - (FIN_IN - 0.35)) / 0.35))
    if abs(t - SPLIT_END) < 0.3: k *= abs(t - SPLIT_END) / 0.3
    return k
FREEZE = 26.9
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); s = seg_at(tt); x = s["a"] + min(tt, s["t1"] - 0.02) - s["t0"]
    if s is segs[-1] and tt >= FIN_IN: x = min(x, FREEZE)
    if s is segs[0]:                                               # gancho: o áudio em tela cheia, com soco de zoom
        card = audio_card(x, 980); bg = R.blur_bg(PHOTO, 0.30); frame = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
        pz = 1.10 - 0.10 * ease_out(t / 0.25); hh = card.shape[0]
        img = cv2.resize(card, (int(980 * pz), int(hh * pz)), interpolation=cv2.INTER_LINEAR); y0 = (img.shape[0] - hh) // 2; x0 = (img.shape[1] - 980) // 2
        R.paste(frame, Image.fromarray(R.rounded(img[y0:y0 + hh, x0:x0 + 980], 30, 5)), CX - 490, 360, 0.6, 22, (8, 20))
        R.credit(frame, "Áudio: reprodução redes sociais", CX + 490 - 14, 360 + hh - 166, 1.0)
        if t < segmap(0, 19.55):
            fs_ = 104
            while R.BIGF(fs_).getlength("A ECONOMISTA DO FLÁVIO:") > 660: fs_ -= 2      # cabe na largura segura
            f = R.BIGF(fs_); d = ImageDraw.Draw(frame); k = ease_out(t / 0.2)
            d.text((CX, 230 - 20 * (1 - k)), "A ECONOMISTA DO FLÁVIO:", font=f, fill=R.GOLD_L + (int(255 * k),), anchor="mm", stroke_width=8, stroke_fill=R.NAVY + (255,))
        big_word(frame, t, (120, 350))
        R.draw_caption(frame, t, 360 + hh + 170, 54, ("me", "au"))
    elif SPLIT_T <= t < SPLIT_END:
        mex = x if s["src"] == "me" else listen_x(t)
        if s is segs[1] and x < 8.45: card = uol_card(x, 540); kind = "uol"
        else: card = audio_card(x if s["src"] == "cl" else 0.0, 740); kind = "aud"
        bg = R.blur_bg(PHOTO if kind == "aud" else UOL, 0.28); frame = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
        u = t - SPLIT_T; kw = ease_out(u / 0.4)
        win = Image.fromarray(R.rounded(win_img(mex), 28, 4)); R.paste(frame, R.fade(win, kw), WIN_X, WIN_Y - 40 * (1 - kw), 0.55, 18, (6, 16))
        kin = ease_out((u - 0.2) / 0.6); ch, cw = card.shape[:2]; cy0 = CRD_Y + (CRD_H - ch) / 2
        cardi = R.rounded(card, 26, 4)
        if kin < 1: cardi = persp_top(cardi, 0.02 + 0.3 * (1 - kin))
        if s is segs[2] and t - s["t0"] < 0.5:                      # troca da matéria pelo áudio: o cartão novo sobe
            kk = ease_out((t - s["t0"]) / 0.5); cy0 += 300 * (1 - kk)
        R.paste(frame, R.fade(Image.fromarray(cardi, "RGBA"), clamp(kin * 1.6)), CX - cw / 2, cy0 + 380 * (1 - kin), 0.6, 22, (10, 26))
        R.credit(frame, "Reprodução: UOL · Foto: Gabriela Biló/Folhapress" if kind == "uol" else "Áudio: reprodução redes sociais", CX + cw / 2 - 14,
                 cy0 + ch - (46 if kind == "uol" else 166), kin)
        pill_on = any(a <= t < b for a, b, *_ in PILLS)
        big_word(frame, t, (WIN_Y + WIN_H + 20, cy0 - (56 if pill_on else 22)))       # entre a janela e o cartão (ou o selo dele)
        for a, b, txt, colr in PILLS:
            if a <= t < b: R.pill(frame, txt, CX, cy0 - 4, clamp((t - a) / 0.3) * clamp((b - t) / 0.25), fill=colr, size=pill_size(txt))
        kc = card_k(t)
        if kc > 0: BAR.lower_card(frame, CARD[0], CARD[1], CARD_Y_SPLIT, kc, fs=36)
        R.draw_caption(frame, t, CAP_Y_SPLIT, 42, ("me", "au"))
    else:
        frame = Image.fromarray(np.clip(me_full(x), 0, 255).astype(np.uint8)).convert("RGBA")
        big_word(frame, t, (130, 430))
        if tt < FIN_IN:
            R.draw_caption(frame, t, 1500, 48, ("me", "au")); kc = card_k(t)
            if kc > 0: BAR.lower_card(frame, CARD[0], CARD[1], 1655, kc, fs=40)
        else: R.lyrics(frame, t)
    BAR.draw_bar(frame, clamp(t / END_IN), "canal", ease_out((t - 0.2) / 0.6), cta_level(t), 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(frame, t)
    for e in [segs[1]["t0"], segs[2]["t0"], segs[3]["t0"]]:
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
    srcw = {"me": R.readw(f"{V}/me48.wav") * float(os.environ.get("MEG", "0.55")), "cl": R.readw(f"{V}/cl48.wav") * float(os.environ.get("CLG", "0.75"))}
    vt = np.zeros((n, 2), np.float32); f = int(0.03 * SR)
    for s in segs:
        c = srcw[s["src"]][int(s["a"] * SR):int(s["b"] * SR)].copy(); c[:f] *= np.linspace(0, 1, f)[:, None]; c[-f:] *= np.linspace(1, 0, f)[:, None]
        o = int(s["t0"] * SR); vt[o:o + len(c)] += c[:n - o]
    R.writew(f"{V}/voice.wav", vt)
    song = R.readw(f"{S}/v15/song_vox.wav"); Ls = min(len(song), n - int(MUS_IN * SR)); tl = np.arange(Ls) / SR; lead = FIN_IN - MUS_IN
    gain = np.where(tl < lead, 10 ** ((-22 + 22 * tl / lead) / 20), 1.0) * np.clip(1 - (tl - (TOTAL - MUS_IN - 1.6)) / 1.5, 0, 1)
    sg = np.zeros((n, 2), np.float32); sg[int(MUS_IN * SR):int(MUS_IN * SR) + Ls] = song[:Ls] * gain[:, None]; R.writew(f"{V}/song.wav", sg)
    ev = [(0.0, sfx.whoosh(0.4), 0.2), (0.18, sfx.barra(), 0.2), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
    ev += [(sg_["t0"] - 0.12, sfx.whoosh(0.45), 0.22) for sg_ in segs[1:]]
    ev += [(a, sfx.whoosh(0.3), 0.12) for a, *_ in BIG] + [(a + 0.26, sfx.click(), 0.6) for a, *_ in BIG]
    ev += [(a, sfx.click(), 0.35) for a, *_ in PILLS] + [(a, sfx.barra(), 0.11) for a, b in CTA]
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=70,asplit=2[vox][k2];[2:a]volume=0.8[sf];[3:a]volume=0.95[sg];"
                    "[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][sgd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
