"""Corte do debate da Band (18/10/2026): Lula responde Flávio e pede o voto de Jair Bolsonaro ("vote em mim, você conhece o seu filho").
Só o trecho do debate (sem o tweet de terceiro por cima), legendas apenas das falas confirmadas na imprensa, palavras grandes com clique,
barra lateral e caixa fixa do canal, final vai dar PT."""
import sys, math, subprocess, importlib.util
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; MF = R.MF; clamp = R.clamp; ease_out = R.ease_out; ease_in = R.ease_in; ease_io = R.ease_io; back_out = R.back_out
V = f"{S}/v36"; CL = f"{V}/cl.mp4"; ME = f"{V}/me.mp4"; CLIP_LEN = 20.25
INTRO = 4.45                                                     # abertura com o Eliezio antes do corte
CLIP_END = INTRO + CLIP_LEN
FR = R.decode(CL, 0, CLIP_LEN + 0.1, 720, 960); MEFR = R.decode(ME, 0, 8.0, 1080, 1920)
def src(t): return FR[int(clamp((t - INTRO) * FPS, 0, len(FR) - 1))]
def me_src(t): return MEFR[int(clamp(t * FPS, 0, len(MEFR) - 1))]
FIT = 0.88; _fw, _fh = int(W * FIT), int(H * FIT); _fx = CX - _fw // 2; _fy = H - _fh   # ele 12% menor e centrado depois da barra: espaço para a palavra acima da cabeça
_fm = np.ones((_fh, _fw), np.float32); _fm[:, :30] = np.linspace(0, 1, 30)[None, :]; _fm[:, -30:] = np.linspace(1, 0, 30)[None, :]; _fm[:30] *= np.linspace(0, 1, 30)[:, None]; _fm = _fm[..., None]
def me_frame(t):
    img = me_src(t); bg = cv2.resize(cv2.GaussianBlur(cv2.resize(img, (W // 10, H // 10)), (0, 0), 2.5), (W, H)).astype(np.float32) * 0.7
    fg = cv2.resize(cv2.LUT(img, R.LUT), (_fw, _fh), interpolation=cv2.INTER_AREA).astype(np.float32)
    bg[_fy:, _fx:_fx + _fw] = bg[_fy:, _fx:_fx + _fw] * (1 - _fm) + fg * _fm
    return Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
CROP = (36, 345, 684, 850)                                         # só o debate: sem o tweet de cima nem o cronômetro de baixo
BW = 960; BH = int(BW * (CROP[3] - CROP[1]) / (CROP[2] - CROP[0])); BY = 330
# legendas só das falas confirmadas pela imprensa (Jovem Pan, NC News)
CAPS_TXT = [("ELE ESTARIA VOTANDO", 9.1, 10.0), ("NUM CARA MELHOR.", 10.0, 10.9), ("ELE CONHECE,", 10.9, 12.1), ("ELE SABE QUE EU SOU MELHOR QUE VOCÊ.", 12.1, 13.7),
            ("BOLSONARO,", 14.8, 16.0), ("VOTE EM MIM,", 16.1, 17.1), ("VOCÊ CONHECE O SEU FILHO,", 17.1, 18.5), ("VOCÊ SABE QUE EU SOU", 18.5, 19.4), ("MELHOR DO QUE ELE.", 19.4, 20.3)]
HOT = {"MELHOR", "BOLSONARO,", "VOTE", "MIM,", "FILHO,"}
CAPS_TXT = [("DEPOIS DESSA LAPADA AÍ,", 0.15, 1.9), ("ATÉ O BOLSONARO VAI VOTAR NO LULA.", 1.9, 4.3)] + [(x, a + INTRO, b + INTRO) for x, a, b in CAPS_TXT]
HOT = HOT | {"LAPADA", "LULA."}
CAPS = []
for txt, a, b in CAPS_TXT:
    ws = txt.split(); tot = sum(len(w) + 2 for w in ws); acc = 0; ts = []
    for w in ws: ts.append(a + (b - a - 0.1) * acc / tot); acc += len(w) + 2
    CAPS.append(dict(words=ws, ts=ts, start=a, end=b, src="au" if any(w in HOT for w in ws) else "me"))
R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
BIG = [(0.25, 1.8, "PRESÍDIOS", R.GOLD_L), (12.1, 13.75, "MELHOR", R.WHITE), (16.1, 17.2, "VOTE EM MIM", R.GOLD_L), (17.2, 18.5, "SEU FILHO", R.WHITE), (19.3, 20.3, "MELHOR DO QUE ELE", (235, 60, 60))]
BIG = [(0.5, 1.95, "LAPADA", R.GOLD_L), (2.6, 4.3, "VOTAR NO LULA", (235, 60, 60))] + [(a + INTRO, b + INTRO, w, c) for a, b, w, c in BIG]
PILLS = [(0.1, 2.3, "FLÁVIO CUTUCA COM OS PRESÍDIOS...", R.NAVY), (2.4, 7.6, "...E O LULA DEVOLVE COM JUROS", R.RED)]
PILLS = [(a + INTRO, b + INTRO, x, c) for a, b, x, c in PILLS]
MUS_IN = INTRO + 14.8; FIN_IN = CLIP_END
R.MUS_IN = MUS_IN; R.FIN_IN = FIN_IN; FIN_LEN = 9.45 - (FIN_IN - MUS_IN); EDIT_END = FIN_IN + FIN_LEN; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.END_IN = END_IN; R.EDIT_END = EDIT_END
CARD = ("DEBATE NA BAND · 18/10", ["LULA FOI PEDIR VOTO", "NA CASA DO FLÁVIO"]); CARD_Y = 1150
CTA = [(INTRO + 5.0, INTRO + 7.6), (EDIT_END - 3.0, EDIT_END)]
def cta_level(t): return max([clamp((t - a) / 0.4) * clamp((b - t) / 0.4) for a, b in CTA] + [0.0])

def big_word(frame, t):
    for i, (a, b, word, col) in enumerate(BIG):
        if not (a <= t < b): continue
        u = t - a; k = ease_out(u / 0.28); out = ease_in((t - (b - 0.22)) / 0.22)
        size = 200; f = R.BIGF(size); d0 = ImageDraw.Draw(Image.new("L", (4, 4)))
        while d0.textlength(word, font=f) > 680: size -= 6; f = R.BIGF(size)
        lay = Image.new("RGBA", (W, int(size * 1.3)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.text((W / 2 + 3, lay.height / 2 + 4), word, font=f, fill=(0, 0, 0, 110), anchor="mm"); d.text((W / 2, lay.height / 2), word, font=f, fill=col + (255,), anchor="mm")
        dx = (1 if i % 2 == 0 else -1) * W * 0.95 * (1 - k)
        if u < 0.28:
            L = int(60 * (1 - k)) + 1
            if L > 2: lay = Image.fromarray(cv2.filter2D(np.asarray(lay), -1, np.ones((1, L), np.float32) / L))
        frame.alpha_composite(R.fade(lay, 1 - out), (int(CX - W / 2 + dx), int(225 - lay.height / 2 - 30 * out)))

def frame_at(t):
    tt = min(t, EDIT_END - 1e-3)
    if t < INTRO: return intro_at(t)
    # final: congela no Lula com zoom lento (ele preferiu sem o L dele no fim)
    ct = min(tt, CLIP_END - 0.02); fr = src(ct)
    bg = R.blur_bg(fr[CROP[1]:CROP[3], CROP[0]:CROP[2]], 0.32)
    frame = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
    clip = cv2.resize(fr[CROP[1]:CROP[3], CROP[0]:CROP[2]], (BW, BH), interpolation=cv2.INTER_LANCZOS4)
    if tt >= FIN_IN:                                               # final: congela no Lula e aproxima devagar
        q = (tt - FIN_IN) / FIN_LEN; sc = 1 + 0.12 * ease_io(q); cx, cy = BW * 0.78, BH * 0.35
        clip = cv2.warpAffine(clip, np.float32([[sc, 0, cx - cx * sc], [0, sc, cy - cy * sc]]), (BW, BH), flags=cv2.INTER_LINEAR)
    k = ease_out((t - INTRO) / 0.35); box = Image.fromarray(R.rounded(clip, 30, 5))
    if k < 1: box = box.resize((int(BW * (0.92 + 0.08 * k)), int(BH * (0.92 + 0.08 * k))), Image.BICUBIC)
    R.paste(frame, R.fade(box, clamp((t - INTRO) / 0.2)), CX - box.width / 2, BY + (BH - box.height) / 2, 0.6, 22, (8, 20))
    R.credit(frame, "Vídeo: reprodução TV Band", CX + BW / 2 - 12, BY + BH - 52, 1.0)
    for a, b, txt, colr in PILLS:
        if a <= t < b: R.pill(frame, txt, CX, 1425, (t - a) / 0.3 * (1 if t < b - 0.25 else 0) + (0 if t < b - 0.25 else 1 - (t - (b - 0.25)) / 0.25), fill=colr, size=34)
    big_word(frame, t)
    if tt < FIN_IN:
        kc = ease_out((t - INTRO - 0.3) / 0.4) * (1 - ease_in((tt - (FIN_IN - 0.35)) / 0.35))
        if kc > 0: BAR.lower_card(frame, CARD[0], CARD[1], CARD_Y, kc, fs=44)
        R.draw_caption(frame, t, 1560, 52, ("me", "au"))
    else: R.lyrics(frame, t)
    BAR.draw_bar(frame, clamp(t / END_IN), "canal", ease_out((t - 0.2) / 0.6), cta_level(t), 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(frame, t)
    if t >= END_IN: frame.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return frame.convert("RGB")

def intro_at(t):
    frame = me_frame(t); big_word(frame, t)
    R.draw_caption(frame, t, 1510, 48, ("me", "au"))
    kc = ease_out((t - 0.6) / 0.5) * (1 - ease_in((t - (INTRO - 0.3)) / 0.3))   # caixa embaixo da legenda; reaparece no corte
    if kc > 0: BAR.lower_card(frame, CARD[0], CARD[1], 1655, kc, fs=44)
    BAR.draw_bar(frame, clamp(t / END_IN), "canal", ease_out((t - 0.2) / 0.6), cta_level(t), 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(frame, t)
    if t > INTRO - 0.12: frame = Image.blend(frame, Image.new("RGBA", frame.size, (255, 255, 255, 255)), (t - (INTRO - 0.12)) / 0.12 * 0.5)   # flash curto na troca
    return frame.convert("RGB")

L_FROM, L_TO = 4.3, 7.75                                         # ele fazendo o L no fim da gravação (já do lado certo, sem espelhar)
def finale_at(t, tt):
    frame = me_frame(min(L_TO, L_FROM + (tt - FIN_IN) * 0.85)); R.lyrics(frame, t)
    BAR.draw_bar(frame, clamp(t / END_IN), "canal", 1.0, cta_level(t), 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(frame, t)
    if tt < FIN_IN + 0.12: frame = Image.blend(frame, Image.new("RGBA", frame.size, (255, 255, 255, 255)), (1 - (tt - FIN_IN) / 0.12) * 0.5)
    if t >= END_IN: frame.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return frame.convert("RGB")

def main():
    if MODE == "lib": return
    if MODE.startswith("frames"):
        ts = [float(x) for x in MODE.split(":")[1].split(",")]
        outs = [frame_at(t).resize((360, 640), Image.LANCZOS) for t in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    if MODE == "info": print("TOTAL", TOTAL, "FIN", FIN_IN, "MUS", MUS_IN); return
    vout = f"{V}/video.mp4"
    import os
    if os.environ.get("REUSE") and os.path.exists(vout): enc = None                 # REUSE=1: só refaz o áudio
    else: enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
    if enc:
        for i in range(int(round(TOTAL * FPS))): enc.stdin.write(frame_at(i / FPS).tobytes())
        enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", CL, "-t", str(CLIP_END), "-ar", "48000", "-ac", "2", f"{V}/cl48.wav"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", ME, "-t", str(INTRO), "-ar", "48000", "-ac", "2", f"{V}/me48.wav"], check=True)
    e = R.readw(f"{V}/me48.wav")[:int(INTRO * SR)]; vt = np.zeros((n, 2), np.float32); f = int(0.08 * SR); e[-f:] *= np.linspace(1, 0, f)[:, None]; vt[:len(e)] = e * 0.6        # voz dele no nível do debate
    c = R.readw(f"{V}/cl48.wav"); o = int(INTRO * SR); m = min(len(c), n - o); f = int(0.15 * SR)
    env = np.ones(m); env[-f:] = np.linspace(1, 0, f); vt[o:o + m] = c[:m] * env[:, None] * 1.25           # áudio de terceiros a 1,25
    R.writew(f"{V}/voice.wav", vt)
    song = R.readw(f"{S}/v15/song_vox.wav"); lead = FIN_IN - MUS_IN; Ls = min(len(song), n - int(MUS_IN * SR)); tl = np.arange(Ls) / SR
    gain = np.where(tl < lead, 10 ** ((-22 + 22 * tl / lead) / 20), 1.0) * np.clip(1 - (tl - (TOTAL - MUS_IN - 1.6)) / 1.5, 0, 1)
    sg = np.zeros((n, 2), np.float32); sg[int(MUS_IN * SR):int(MUS_IN * SR) + Ls] = song[:Ls] * gain[:, None]; R.writew(f"{V}/song.wav", sg)
    ev = [(0.18, sfx.barra(), 0.2), (0.6, sfx.whoosh(0.4), 0.16), (FIN_IN - 0.1, sfx.whoosh(0.5), 0.2), (INTRO - 0.15, sfx.whoosh(0.4), 0.22), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
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
