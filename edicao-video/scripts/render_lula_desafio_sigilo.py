"""Corte da entrevista do Lula depois do debate da Band (18/10/2026): desafia Flávio a abrir os sigilos bancário e telefônico.
Sem as logos da Band, a manchete deles e o começo da fala ("foi uma participação normal"); legendas, palavras grandes com clique,
selos de contexto, barra lateral e caixa fixa do canal, hashtag da campanha e final vai dar PT."""
import sys, math, subprocess, importlib.util
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; ease_out = R.ease_out; ease_in = R.ease_in; ease_io = R.ease_io
V = f"{S}/v39"; CL = f"{V}/src.mp4"; T0 = 3.6; CLIP_END = 46.55 - T0      # começa no "eu resolvi fazer um desafio"
CX0, CX1, CY0, CY1 = 20, 920, 160, 1060                            # só o Lula: fora as logos da Band (à direita e embaixo) e a manchete deles (y 1270+)
FR = R.decode(CL, T0, T0 + CLIP_END + 0.1, CX1 - CX0, CY1 - CY0, f"crop={CX1 - CX0}:{CY1 - CY0}:{CX0}:{CY0}") if MODE == "full" or MODE.startswith(("frames", "logo", "cover")) else None
def src(t): return FR[int(clamp(t * FPS, 0, len(FR) - 1))]
BW = 860; BH = int(BW * (CY1 - CY0) / (CX1 - CX0)); BY = 330
SEGS = [(3.65, 7.4, ["EU RESOLVI FAZER UM DESAFIO", "AO MEU ADVERSÁRIO, PORQUE"]),
        (7.8, 11.2, ["NÃO É POSSÍVEL QUE VOCÊ FIQUE", "FAZENDO DEBATE", "FALANDO DE CORRUPÇÃO"]),
        (11.2, 16.0, ["E VOCÊ NÃO TOMA ATITUDE.", "EU TOMEI ATITUDE", "E DESAFIEI ELE A ABRIR"]),
        (16.0, 21.0, ["O SIGILO TELEFÔNICO DELE,", "O SIGILO BANCÁRIO,", "PRA SABER QUEM É"]),
        (21.0, 26.0, ["QUE É CORRUPTO NESSE PAÍS.", "PORQUE TODO MUNDO", "ACUSA TODO MUNDO", "E NÃO APURA NADA.", "ENTÃO É O SEGUINTE:"]),
        (26.0, 31.5, ["VAMOS APURAR.", "EU ME DISPONHO", "E VOU FICAR FAZENDO DESAFIO", "PRA ELE ATÉ O PRÓXIMO DEBATE"]),
        (31.5, 37.6, ["PRA QUE A GENTE FAÇA", "A ABERTURA DO NOSSO SIGILO", "BANCÁRIO E TELEFÔNICO", "PRA SE APURAR"]),
        (37.7, 42.2, ["QUEM É QUE FAZ CORRUPÇÃO", "NESTE PAÍS,", "QUEM É QUE ENRIQUECE", "ILICITAMENTE NESTE PAÍS,"]),
        (42.2, 46.5, ["PORQUE NÃO É POSSÍVEL", "FICAR NESSA", "ACUSAÇÃO BARATA", "DE UM CONTRA O OUTRO."])]
CAPS_TXT = []
for a, b, chunks in SEGS:
    tot = sum(len(c) + 3 for c in chunks); acc = 0
    for c in chunks:
        ca = a + (b - a) * acc / tot; acc += len(c) + 3; CAPS_TXT.append((c, ca - T0, a + (b - a) * acc / tot - T0))
HOT = {"DESAFIO", "CORRUPÇÃO", "ATITUDE.", "ATITUDE", "SIGILO", "TELEFÔNICO", "BANCÁRIO,", "BANCÁRIO", "CORRUPTO", "APURAR.", "APURA", "DEBATE", "ILICITAMENTE", "BARATA", "ENRIQUECE"}
CAPS = []
for txt, a, b in CAPS_TXT:
    ws = txt.split(); tot = sum(len(w) + 2 for w in ws); acc = 0; ts = []
    for w in ws: ts.append(a + (b - a - 0.1) * acc / tot); acc += len(w) + 2
    CAPS.append(dict(words=ws, ts=ts, start=a, end=b, src="au" if any(w in HOT for w in ws) else "me"))
R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
BIG = [(a - T0, b - T0, w, c) for a, b, w, c in [(4.3, 6.2, "DESAFIO", R.GOLD_L), (9.6, 11.2, "CORRUPÇÃO", (235, 60, 60)), (12.6, 14.4, "ATITUDE", R.WHITE),
       (16.0, 18.4, "SIGILO", R.GOLD_L), (26.0, 27.6, "VAMOS APURAR", R.WHITE), (33.9, 36.0, "BANCÁRIO E TELEFÔNICO", R.GOLD_L),
       (39.7, 42.1, "ENRIQUECE?", (235, 60, 60)), (44.0, 46.4, "ACUSAÇÃO BARATA", R.WHITE)]]
PILLS = [(0.2, 3.6, "ENTREVISTA LOGO DEPOIS DO DEBATE NA BAND", R.NAVY), (28.0 - T0, 31.4 - T0, "LULA: VAI REPETIR O DESAFIO ATÉ O PRÓXIMO DEBATE", R.RED)]
TAG = "#AbreASigiloFlavio"                                         # hashtag que o Eliezio pediu, na tela no fim
MUS_IN = CLIP_END - 5.5; FIN_IN = CLIP_END
R.MUS_IN = MUS_IN; R.FIN_IN = FIN_IN; FIN_LEN = 9.45 - (FIN_IN - MUS_IN); EDIT_END = FIN_IN + FIN_LEN; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.END_IN = END_IN; R.EDIT_END = EDIT_END
CARD = ("DEPOIS DO DEBATE · 18/10", ["LULA DESAFIA:", "ABRE O SIGILO, FLÁVIO"]); CARD_Y = 1262
CTA = [(14.0, 16.4), (EDIT_END - 3.0, EDIT_END)]
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
    tt = min(t, EDIT_END - 1e-3); ct = min(tt, CLIP_END - 0.05); fr = src(ct)
    bg = R.blur_bg(fr, 0.32)
    frame = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
    clip = cv2.resize(fr, (BW, BH), interpolation=cv2.INTER_LANCZOS4)
    if tt >= FIN_IN:                                               # final: congela no Lula e aproxima devagar
        q = (tt - FIN_IN) / FIN_LEN; sc = 1 + 0.12 * ease_io(q); cx, cy = BW * 0.55, BH * 0.4
        clip = cv2.warpAffine(clip, np.float32([[sc, 0, cx - cx * sc], [0, sc, cy - cy * sc]]), (BW, BH), flags=cv2.INTER_LINEAR)
    k = ease_out(t / 0.35); box = Image.fromarray(R.rounded(clip, 30, 5))
    if k < 1: box = box.resize((int(BW * (0.92 + 0.08 * k)), int(BH * (0.92 + 0.08 * k))), Image.BICUBIC)
    R.paste(frame, R.fade(box, clamp(t / 0.2)), CX - box.width / 2, BY + (BH - box.height) / 2, 0.6, 22, (8, 20))
    R.credit(frame, "Vídeo: reprodução Band Jornalismo", CX + BW / 2 - 12, BY + BH - 30, 1.0)
    for a, b, txt, colr in PILLS:
        if a <= t < b: R.pill(frame, txt, CX, 1470, clamp((t - a) / 0.3) * clamp((b - t) / 0.25), fill=colr, size=28)
    big_word(frame, t)
    kt = clamp((t - (CLIP_END - 3.2)) / 0.35)                      # hashtag da campanha nos últimos segundos e no final
    if kt > 0 and t < END_IN: R.pill(frame, TAG, CX, 1470 if tt < FIN_IN else 1440, kt, fill=R.NAVY, size=44)
    if tt < FIN_IN:
        kc = ease_out((t - 0.6) / 0.5) * (1 - ease_in((tt - (FIN_IN - 0.35)) / 0.35))
        if kc > 0: BAR.lower_card(frame, CARD[0], CARD[1], CARD_Y, kc, fs=44)
        R.draw_caption(frame, t, 1625, 50, ("me", "au"))
    else: R.lyrics(frame, t)
    BAR.draw_bar(frame, clamp(t / END_IN), "canal", ease_out((t - 0.2) / 0.6), cta_level(t), 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(frame, t)
    if t >= END_IN: frame.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return frame.convert("RGB")

def main():
    if MODE in ("lib", "cover"): return
    if MODE.startswith("frames"):
        ts = [float(x) for x in MODE.split(":")[1].split(",")]
        outs = [frame_at(t).resize((360, 640), Image.LANCZOS) for t in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    if MODE.startswith("logo"): Image.fromarray(np.hstack([src(float(MODE[5:]))[0:300, 0:600], src(float(MODE[5:]))[0:300, 0:600]])).save(OUTFILE); return
    if MODE == "info": print("TOTAL", TOTAL, "FIN", FIN_IN, "MUS", MUS_IN); return
    import os
    vout = f"{V}/video.mp4"
    if not (os.environ.get("REUSE") and os.path.exists(vout)):     # REUSE=1: só refaz o áudio
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
        for i in range(int(round(TOTAL * FPS))): enc.stdin.write(frame_at(i / FPS).tobytes())
        enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(T0), "-i", CL, "-t", str(CLIP_END), "-ar", "48000", "-ac", "2", f"{V}/cl48.wav"], check=True)
    c = R.readw(f"{V}/cl48.wav"); vt = np.zeros((n, 2), np.float32); m = min(len(c), n); f = int(0.15 * SR)
    env = np.ones(m); env[-f:] = np.linspace(1, 0, f); vt[:m] = c[:m] * env[:, None] * 1.25           # áudio de terceiros a 1,25
    R.writew(f"{V}/voice.wav", vt)
    song = R.readw(f"{S}/v15/song_vox.wav"); lead = FIN_IN - MUS_IN; Ls = min(len(song), n - int(MUS_IN * SR)); tl = np.arange(Ls) / SR
    gain = np.where(tl < lead, 10 ** ((-22 + 22 * tl / lead) / 20), 1.0) * np.clip(1 - (tl - (TOTAL - MUS_IN - 1.6)) / 1.5, 0, 1)
    sg = np.zeros((n, 2), np.float32); sg[int(MUS_IN * SR):int(MUS_IN * SR) + Ls] = song[:Ls] * gain[:, None]; R.writew(f"{V}/song.wav", sg)
    ev = [(0.18, sfx.barra(), 0.2), (0.6, sfx.whoosh(0.4), 0.16), (FIN_IN - 0.1, sfx.whoosh(0.5), 0.2), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
    ev += [(a, sfx.whoosh(0.3), 0.12) for a, *_ in BIG] + [(a + 0.26, sfx.click(), 0.6) for a, *_ in BIG]
    ev += [(a, sfx.click(), 0.35) for a, *_ in PILLS] + [(CLIP_END - 3.2, sfx.click(), 0.45)] + [(a, sfx.barra(), 0.11) for a, b in CTA]
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=70,asplit=2[vox][k2];[2:a]volume=0.8[sf];[3:a]volume=0.95[sg];"
                    "[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][sgd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
