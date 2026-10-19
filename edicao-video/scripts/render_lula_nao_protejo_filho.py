"""Corte do debate da Band (18/10/2026) a partir do vídeo do O Globo: Lula diz que o filho abriu sigilo e devolve com a PF e o Careca do INSS.
Sem a logo do jornal, sem a manchete deles e sem o cronômetro; legendas das falas, palavras grandes com clique, o outro lado em selos,
barra lateral e caixa fixa do canal, final vai dar PT."""
import sys, math, subprocess, importlib.util
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; ease_out = R.ease_out; ease_in = R.ease_in; ease_io = R.ease_io
V = f"{S}/v37"; CL = f"{V}/src.mp4"; CLIP_END = 36.55
CY0, CY1 = 248, 944                                                # só o debate: abaixo da logo do jornal, acima da manchete deles (y 960+), da logo da Band e do cronômetro
FR = R.decode(CL, 0, CLIP_END + 0.1, 1080, CY1 - CY0, f"crop=1080:{CY1 - CY0}:0:{CY0}") if MODE == "full" or MODE.startswith(("frames", "logo", "cover")) else None
def src(t): return FR[int(clamp(t * FPS, 0, len(FR) - 1))]
BW = 960; BH = int(BW * (CY1 - CY0) / 1080); BY = 330
SEGS = [(0.09, 8.12, ["O MEU FILHO ABRIU", "A CONTA BANCÁRIA", "E ABRIU O TELEFONE", "PARA SER INVESTIGADO."]),
        (8.44, 16.48, ["PORQUE EU NÃO SOU UM PAI", "QUE PROTEGE O FILHO", "COMO VOCÊ FOI PROTEGIDO", "PELO SEU PAI.", "SE TIVER INVESTIGAÇÃO,", "SE TIVER PROBLEMA,", "SERÁ INVESTIGADO."]),
        (16.57, 25.21, ["SEJA MEU FILHO,", "SEJA MEU IRMÃO, QUALQUER UM.", "EU NÃO ESCONDO", "NEM MUDO DIRETOR", "DA POLÍCIA FEDERAL", "E NEM MANDO O MINISTRO", "IR EMBORA PORQUE NÃO QUIS", "TROCAR O DIRETOR DA PF."]),
        (25.78, 27.81, ["O QUE EU QUERIA", "DIZER PRA VOCÊ É O SEGUINTE:"]),
        (28.25, 36.44, ["O CARECA É RESULTADO", "DE UMA QUADRILHA", "QUE ELES MONTARAM", "PARA ROUBAR A PREVIDÊNCIA.", "NÓS DESCOBRIMOS A QUADRILHA,", "PRENDEMOS A QUADRILHA", "E JÁ PAGAMOS OS APOSENTADOS."])]
HOT = {"PAI.", "PROTEGIDO", "INVESTIGADO.", "POLÍCIA", "FEDERAL", "PF.", "CARECA", "QUADRILHA", "QUADRILHA,", "PAGAMOS", "APOSENTADOS.", "TELEFONE", "BANCÁRIA"}
CAPS = []
for a, b, chunks in SEGS:
    tot = sum(len(c) + 3 for c in chunks); acc = 0
    for c in chunks:
        ca = a + (b - a) * acc / tot; acc += len(c) + 3; cb = a + (b - a) * acc / tot
        ws = c.split(); wt = sum(len(w) + 2 for w in ws); k = 0; ts = []
        for w in ws: ts.append(ca + (cb - ca - 0.08) * k / wt); k += len(w) + 2
        CAPS.append(dict(words=ws, ts=ts, start=ca, end=cb, src="au" if any(w in HOT for w in ws) else "me"))
R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
BIG = [(3.9, 6.3, "SIGILO ABERTO", R.GOLD_L), (10.7, 13.0, "PROTEGIDO PELO PAI", (235, 60, 60)), (20.2, 22.4, "POLÍCIA FEDERAL", R.WHITE),
       (28.3, 30.2, "CARECA", R.GOLD_L), (32.4, 34.2, "PRENDEMOS", R.WHITE), (34.6, 36.5, "APOSENTADOS PAGOS", R.GOLD_L)]
PILLS = [(0.3, 3.7, "FLÁVIO ACIONOU O TCU CONTRA LULINHA", R.NAVY), (22.6, 25.3, "O OUTRO LADO: BOLSONARO NEGA TER INTERFERIDO NA PF", R.NAVY),
         (30.3, 32.3, "CARECA DO INSS: ANTÔNIO CAMILO ANTUNES", R.RED)]
MUS_IN = 31.0; FIN_IN = CLIP_END
R.MUS_IN = MUS_IN; R.FIN_IN = FIN_IN; FIN_LEN = 9.45 - (FIN_IN - MUS_IN); EDIT_END = FIN_IN + FIN_LEN; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.END_IN = END_IN; R.EDIT_END = EDIT_END
CARD = ("DEBATE NA BAND · 18/10", ["LULA NÃO DEIXOU", "BARATO PRO FLÁVIO"]); CARD_Y = 1048
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
    tt = min(t, EDIT_END - 1e-3); ct = min(tt, 36.2); fr = src(ct)         # o vídeo do jornal acaba em 36,3 s (depois vem a vinheta deles)
    bg = R.blur_bg(fr, 0.32)
    frame = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
    clip = cv2.resize(fr, (BW, BH), interpolation=cv2.INTER_AREA)
    if tt >= FIN_IN:                                               # final: congela no Lula e aproxima devagar
        q = (tt - FIN_IN) / FIN_LEN; sc = 1 + 0.12 * ease_io(q); cx, cy = BW * 0.6, BH * 0.35
        clip = cv2.warpAffine(clip, np.float32([[sc, 0, cx - cx * sc], [0, sc, cy - cy * sc]]), (BW, BH), flags=cv2.INTER_LINEAR)
    k = ease_out(t / 0.35); box = Image.fromarray(R.rounded(clip, 30, 5))
    if k < 1: box = box.resize((int(BW * (0.92 + 0.08 * k)), int(BH * (0.92 + 0.08 * k))), Image.BICUBIC)
    R.paste(frame, R.fade(box, clamp(t / 0.2)), CX - box.width / 2, BY + (BH - box.height) / 2, 0.6, 22, (8, 20))
    R.credit(frame, "Vídeo: reprodução TV Band", CX + BW / 2 - 12, BY + BH - 30, 1.0)
    for a, b, txt, colr in PILLS:
        if a <= t < b: R.pill(frame, txt, CX, 1335, clamp((t - a) / 0.3) * clamp((b - t) / 0.25), fill=colr, size=28)
    big_word(frame, t)
    if tt < FIN_IN:
        kc = ease_out((t - 0.6) / 0.5) * (1 - ease_in((tt - (FIN_IN - 0.35)) / 0.35))
        if kc > 0: BAR.lower_card(frame, CARD[0], CARD[1], CARD_Y, kc, fs=44)
        R.draw_caption(frame, t, 1500, 50, ("me", "au"))
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
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", CL, "-t", str(CLIP_END), "-ar", "48000", "-ac", "2", f"{V}/cl48.wav"], check=True)
    c = R.readw(f"{V}/cl48.wav"); vt = np.zeros((n, 2), np.float32); m = min(len(c), n); f = int(0.15 * SR)
    env = np.ones(m); env[-f:] = np.linspace(1, 0, f); vt[:m] = c[:m] * env[:, None] * 1.25           # áudio de terceiros a 1,25
    R.writew(f"{V}/voice.wav", vt)
    song = R.readw(f"{S}/v15/song_vox.wav"); lead = FIN_IN - MUS_IN; Ls = min(len(song), n - int(MUS_IN * SR)); tl = np.arange(Ls) / SR
    gain = np.where(tl < lead, 10 ** ((-22 + 22 * tl / lead) / 20), 1.0) * np.clip(1 - (tl - (TOTAL - MUS_IN - 1.6)) / 1.5, 0, 1)
    sg = np.zeros((n, 2), np.float32); sg[int(MUS_IN * SR):int(MUS_IN * SR) + Ls] = song[:Ls] * gain[:, None]; R.writew(f"{V}/song.wav", sg)
    ev = [(0.18, sfx.barra(), 0.2), (0.6, sfx.whoosh(0.4), 0.16), (FIN_IN - 0.1, sfx.whoosh(0.5), 0.2), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
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
