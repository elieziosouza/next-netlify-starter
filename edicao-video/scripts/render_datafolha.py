"""Corte "analisando": ele em tela cheia, mão no queixo, e a reportagem da CNN Brasil sobre o Datafolha (22/10) num card na frente dele.
Só trechos de frase inteira da repórter; o dado dos votos totais (Flávio 47%, Lula 46%) entra junto com o empate nos válidos.
Linha de fonte da pesquisa fixa na tela (instituto, datas, margem de erro); o registro no TSE entra por REG quando confirmado."""
import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
import sfx
BLUE = (14, 62, 120)
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; ease_out = R.ease_out; ease_in = R.ease_in
V = f"{S}/v51"; ME = f"{V}/in.mp4"; CL = f"{V}/cl.mp4"
REG = os.environ.get("REG", "")
PARTS = [(0.05, 6.85), (22.9, 43.5), (51.95, 63.4), (79.8, 85.6), (125.5, 130.35)]
segs = []; acc = 0.0
for a, b in PARTS: segs.append(dict(a=a, b=b, t0=acc, t1=acc + b - a)); acc += b - a
def segmap(i, x): return segs[i]["t0"] + x - segs[i]["a"]
def seg_at(t):
    for i, s in enumerate(segs):
        if t < s["t1"]: return i
    return len(segs) - 1
EDIT_END = acc; FIN_IN = EDIT_END; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = FIN_IN; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
FULL = MODE == "full" or MODE.startswith("frames")
CW, CH = 400, 460; CY0 = 1300; DY = 40                             # card da CNN e quanto ele desce na tela
MEF = R.decode(ME, 0, 13.4, 1080, 1920) if FULL else None
CLP = [R.decode(CL, a, b, CW, CH, f"crop=1080:1242:0:0,scale={CW}:{CH}") for a, b in PARTS] if FULL else None
def fr_of(arr, x): return arr[int(clamp(x * FPS, 0, len(arr) - 1))]
def me_x(t):                                                        # vai e volta, pra pose não "pular"
    L = (len(MEF) - 2) / FPS; p = t % (2 * L); return p if p < L else 2 * L - p
# legendas (texto conferido no áudio; tempos das frases do ASR, palavras distribuídas)
CL_CAPS = [("ACABA DE SAIR A PESQUISA", 0.12, 1.6), ("DATAFOLHA", 1.6, 3.11), ("COM CENÁRIOS PARA A DISPUTA", 3.35, 5.2), ("DE SEGUNDO TURNO.", 5.2, 6.76),
           ("FLÁVIO BOLSONARO", 23.0, 24.04), ("E LULA", 24.41, 25.29), ("APARECEM ABSOLUTAMENTE", 25.75, 27.1), ("EMPATADOS.", 27.1, 28.33),
           ("50% DAS INTENÇÕES", 28.95, 30.7), ("DE VOTO.", 30.7, 32.36), ("AÍ, AGORA", 32.92, 33.96), ("NA SUA TELA.", 34.23, 35.4), ("50%", 35.4, 36.81),
           ("PARA CADA UM.", 37.05, 38.47), ("EMPATE NUMÉRICO.", 39.51, 41.3), ("ISSO DOS VOTOS VÁLIDOS.", 41.3, 43.4),
           ("NO NÚMERO DE VOTOS TOTAIS,", 52.06, 54.0), ("O FLÁVIO BOLSONARO ESTÁ", 54.0, 55.6), ("A UM PONTO NA FRENTE", 55.6, 57.0),
           ("COM 47% DOS VOTOS TOTAIS", 57.0, 58.6), ("E 46% PARA", 58.6, 59.65), ("O PRESIDENTE LULA,", 59.93, 61.4), ("CANDIDATO À REELEIÇÃO.", 61.4, 63.3),
           ("AQUELE MOVIMENTO DE APROXIMAÇÃO", 79.9, 82.0), ("DOS DOIS SE CONFIRMOU.", 82.0, 83.6), ("LENTO, MAS SE CONFIRMOU.", 83.6, 85.51),
           ("DITO ISSO, O MOVIMENTO DETECTADO", 125.62, 127.6), ("É FAVORÁVEL AO PRESIDENTE LULA", 127.6, 129.3), ("NESSE MOMENTO.", 129.3, 130.21)]
HOT = {"DATAFOLHA", "EMPATADOS.", "50%", "VÁLIDOS.", "47%", "46%", "TOTAIS", "CONFIRMOU.", "FAVORÁVEL", "LULA", "LULA,"}
CAPS = []
for i, s in enumerate(segs):
    for txt, a, b in CL_CAPS:
        a, b = max(a, s["a"]), min(b, s["b"])
        if b - a < 0.25: continue
        a2, b2 = segmap(i, a), segmap(i, b); ws = txt.split(); tot = sum(len(w) + 2 for w in ws); k = 0; ts = []
        for w in ws: ts.append(a2 + (b2 - a2 - 0.1) * k / tot); k += len(w) + 2
        CAPS.append(dict(words=ws, ts=ts, start=a2, end=b2, src="au" if any(w in HOT for w in ws) else "me"))
CAPS.sort(key=lambda c: c["start"]); R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
BIG = [(0, 1.5, 3.4, "DATAFOLHA", R.GOLD_L), (1, 25.7, 28.4, "EMPATE", R.WHITE), (1, 35.2, 38.6, "50% A 50%", R.GOLD_L),
       (2, 56.9, 59.7, "47% A 46%", R.WHITE), (3, 82.0, 85.5, "SE CONFIRMOU", R.GOLD_L), (4, 127.5, 130.3, "FAVORÁVEL A LULA", R.GOLD_L)]
BIG = [(segmap(i, a), segmap(i, b), w, c) for i, a, b, w, c in BIG]
PILLS = [(1, 22.9, 43.5, "VOTOS VÁLIDOS · 2º TURNO", BLUE), (2, 51.95, 63.4, "VOTOS TOTAIS: FLÁVIO 47%, LULA 46%", R.NAVY),
         (3, 79.8, 85.6, "ANÁLISE · CNN BRASIL", R.NAVY), (4, 125.5, 130.35, "ANÁLISE · CNN BRASIL", R.NAVY)]
PILLS = [(segmap(i, a), segmap(i, b), x, c) for i, a, b, x, c in PILLS]
SRC_LINE = "Pesquisa Datafolha · 20 a 22/10 · margem de erro: 2 pontos · 95% de confiança" + (f" · TSE {REG}" if REG else "")
def caption(frame, t, y, size, tracks):
    old = R.RED; R.RED = BLUE
    try: R.draw_caption(frame, t, y, size, tracks)
    finally: R.RED = old
def big_word(frame, t, z0, z1):
    for i, (a, b, word, col) in enumerate(BIG):
        if not (a <= t < b): continue
        u = t - a; k = ease_out(u / 0.28); out = ease_in((t - (b - 0.22)) / 0.22); size = 170
        while True:
            f = R.BIGF(size); bb = f.getbbox(word, stroke_width=10)
            if (bb[3] - bb[1]) <= (z1 - z0) - 16 and (bb[2] - bb[0]) <= 680: break
            size -= 4
        lay = Image.new("RGBA", (W, bb[3] - bb[1] + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.text((W / 2 - (bb[0] + bb[2]) / 2 + 5, 10 - bb[1] + 7), word, font=f, fill=(0, 0, 0, 120), stroke_width=10, stroke_fill=(0, 0, 0, 120))
        d.text((W / 2 - (bb[0] + bb[2]) / 2, 10 - bb[1]), word, font=f, fill=col + (255,), stroke_width=10, stroke_fill=R.NAVY + (255,))
        dx = (1 if i % 2 == 0 else -1) * W * 0.95 * (1 - k); dy = 0
        if 0.28 < u < 0.9: a_ = 8 * (1 - (u - 0.28) / 0.62); dx += a_ * math.sin(u * 95); dy = a_ * 0.6 * math.cos(u * 77)   # tremidinha
        frame.alpha_composite(R.fade(lay, 1 - out), (int(CX - W / 2 + dx), int((z0 + z1) / 2 - lay.height / 2 + dy)))
def pill_size(txt, size=30):
    while R.MF("ExtraBold", size).getlength(txt) + 50 > 640: size -= 1
    return size
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); i = seg_at(tt); s = segs[i]
    me = fr_of(MEF, me_x(tt)); z = 1.03 + 0.02 * math.sin(tt * 0.35)
    big = cv2.resize(cv2.LUT(me, R.LUT), (int(1080 * z), int(1920 * z)), interpolation=cv2.INTER_LINEAR)
    ox = (big.shape[1] - 1080) // 2; base = np.zeros((1920, 1080, 3), np.uint8); base[:] = big[0:1, ox:ox + 1080].mean(axis=(0, 1)).astype(np.uint8)
    base[DY:] = big[0:1920 - DY, ox:ox + 1080]
    frame = Image.fromarray(base).convert("RGBA")
    top = Image.new("RGBA", (W, 420), (0, 0, 0, 0)); g = np.zeros((420, W, 4), np.uint8); g[..., :3] = (4, 14, 28)
    g[..., 3] = (np.linspace(200, 0, 420) ** 1.0)[:, None].astype(np.uint8); frame.alpha_composite(Image.fromarray(g))   # escurece o topo p/ as palavras
    bot = np.zeros((560, W, 4), np.uint8); bot[..., :3] = (4, 14, 28); bot[..., 3] = np.linspace(0, 210, 560)[:, None].astype(np.uint8)
    frame.alpha_composite(Image.fromarray(bot), (0, 1920 - 560))
    # card da CNN na frente dele
    kin = ease_out((t - 0.25) / 0.45) * (1 - ease_in((t - (END_IN - 0.3)) / 0.3))
    if kin > 0:
        cimg = fr_of(CLP[i], tt - s["t0"]); card = R.rounded(cv2.LUT(cimg, R.LUT), 24, 4)
        ci = Image.fromarray(card).rotate(-1.5, resample=Image.BICUBIC, expand=True)
        R.paste(frame, R.fade(ci, kin), CX - ci.width / 2, CY0 + 260 * (1 - kin), 0.65, 24, (10, 26))
        for a, b, txt, col in PILLS:
            if a <= tt < b: R.pill(frame, txt, CX, CY0 - 34, clamp((tt - a) / 0.25) * clamp((b - tt) / 0.25) * kin, fill=col, size=pill_size(txt))
    big_word(frame, tt, 110, 300)
    caption(frame, tt, 1690, 44, ("me", "au"))
    R.credit(frame, SRC_LINE, CX, 1790, kin, anchor="mm")
    BAR.draw_bar(frame, clamp(t / END_IN), "canal", ease_out((t - 0.2) / 0.6), 0.0, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(frame, t)
    for e in [sg["t0"] for sg in segs[1:]]:
        if abs(t - e) < 0.08: frame = Image.blend(frame, Image.new("RGBA", frame.size, (255, 255, 255, 255)), (1 - abs(t - e) / 0.08) * 0.3)
    if t >= END_IN: frame.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return frame.convert("RGB")

def main():
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(t).resize((360, 640), Image.LANCZOS) for t in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    if MODE == "info": print("TOTAL", round(TOTAL, 2), [round(s["t0"], 2) for s in segs]); return
    vout = f"{V}/video.mp4"
    if not (os.environ.get("REUSE") and os.path.exists(vout)):
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
        for k in range(int(round(TOTAL * FPS))): enc.stdin.write(frame_at(k / FPS).tobytes())
        enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", CL, "-ar", "48000", "-ac", "2", f"{V}/cl48.wav"], check=True)
    cl = R.readw(f"{V}/cl48.wav") * float(os.environ.get("CLG", "1.1")); vt = np.zeros((n, 2), np.float32); f = int(0.03 * SR)
    def rms(c): v = c[np.abs(c).max(1) > 0.01]; return float(np.sqrt((v ** 2).mean())) if len(v) else 1e-6
    ref = np.median([rms(cl[int(s["a"] * SR):int(s["b"] * SR)]) for s in segs])
    for s in segs:
        c = cl[int(s["a"] * SR):int(s["b"] * SR)].copy(); c *= min(2.0, ref / rms(c))
        c[:f] *= np.linspace(0, 1, f)[:, None]; c[-f:] *= np.linspace(1, 0, f)[:, None]
        o = int(s["t0"] * SR); vt[o:o + len(c)] += c[:n - o]
    R.writew(f"{V}/voice.wav", vt)
    bed = R.readw(f"{V}/bed.wav"); L = min(len(bed), n); tl = np.arange(L) / SR
    gain = (0.05 * np.clip(tl / 1.0, 0, 1) + 0.05 * np.clip((tl - (EDIT_END - 0.3)) / 0.5, 0, 1)) * np.clip(1 - (tl - (TOTAL - 1.6)) / 1.5, 0, 1)
    sg = np.zeros((n, 2), np.float32); sg[:L] = bed[:L] * gain[:, None]; R.writew(f"{V}/song.wav", sg)
    ev = [(0.0, sfx.whoosh(0.4), 0.2), (0.25, sfx.whoosh(0.5), 0.2), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
    ev += [(sg_["t0"] - 0.12, sfx.whoosh(0.45), 0.2) for sg_ in segs[1:]]
    ev += [(a, sfx.whoosh(0.35), 0.22) for a, *_ in BIG] + [(a + 0.26, sfx.click(), 0.7) for a, *_ in BIG] + [(a + 0.26, sfx.thud(0.3), 0.16) for a, *_ in BIG]
    ev += [(a, sfx.click(), 0.3) for a, *_ in PILLS]
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=70,acompressor=threshold=0.08:ratio=2.5:attack=8:release=200:makeup=1.6,asplit=2[vox][k2];[2:a]volume=0.8[sf];[3:a]volume=0.95[sg];"
                    "[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][sgd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
