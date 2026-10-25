"""Dia da eleição: "Bora votar, gente! ... levando minhas duas armas secretas aqui" (ele no carro com duas senhoras atrás).
Chamado APARTIDÁRIO: sem candidato, número, partido, cor de campanha ou gesto. Padrão de volta: legenda karaokê da marca + caixa fixa.
Cor do carro de dia (cor_fla), zoom leve contínuo, corta a tela do CapCut. Usa os ajudantes do render_exercito."""
import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("rex", f"{S}/work/render_exercito.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
sys.path.insert(0, f"{S}/work")
import cor_fla, sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; eo = R.ease_out
V = f"{S}/v65"
PARTS = [(1.15, 2.85), (3.30, 7.30), (8.45, 10.70)]
segs = []; acc = 0.0
for a, b in PARTS: segs.append(dict(src="me", a=a, b=b, t0=acc, t1=acc + b - a)); acc += b - a
EDIT_END = acc; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = EDIT_END; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
def seg_at(t):
    for i, s in enumerate(segs):
        if t < s["t1"]: return i
    return len(segs) - 1
ME_CAPS = [("BORA VOTAR, GENTE!", 1.30, 2.20), ("BORA!", 2.20, 2.75), ("ESTOU INDO VOTAR AGORA.", 3.45, 4.60),
           ("LEVANDO MINHAS DUAS", 5.15, 6.10), ("ARMAS SECRETAS AQUI.", 6.10, 7.20), ("BORA VOTAR!", 8.70, 9.60)]
HOT = {"VOTAR,", "VOTAR!", "VOTAR", "ARMAS", "SECRETAS"}
CAPS = []
for txt, a, b in ME_CAPS:
    for s in segs:
        a1, b1 = max(a, s["a"]), min(b, s["b"])
        if b1 - a1 < 0.2: continue
        a2, b2 = s["t0"] + a1 - s["a"], s["t0"] + b1 - s["a"]; ws = txt.split(); tot = sum(len(w) + 2 for w in ws); k = 0; ts = []
        for w in ws: ts.append(a2 + (b2 - a2 - 0.08) * k / tot); k += len(w) + 2
        CAPS.append(dict(words=ws, ts=ts, start=a2, end=b2, src="au" if any(w in HOT for w in ws) else "me"))
CAPS.sort(key=lambda c: c["start"]); R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
CARD = ("DOMINGO · 25/10", ["HOJE É DIA", "DE VOTAR"])
_fr = {}
def src(x):
    if not _fr:
        p = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{V}/me.mp4", "-vf", "fps=30", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        n = len(p) // (W * H * 3); _fr["a"] = np.frombuffer(p[:n * W * H * 3], np.uint8).reshape(n, H, W, 3)
    a = _fr["a"]; return cor_fla.fix(a[int(clamp(x * FPS, 0, len(a) - 1))])
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); i = seg_at(tt); s = segs[i]; x = s["a"] + tt - s["t0"]
    z = (1.0 if i % 2 == 0 else 1.04) + 0.03 * (0.5 - 0.5 * math.cos(2 * math.pi * tt / 7.0))
    fr = Image.fromarray(M.zoom(src(x), z, 540, 760)).convert("RGBA")
    g = np.zeros((560, W, 4), np.uint8); g[..., :3] = (4, 14, 28); g[..., 3] = np.linspace(0, 210, 560)[:, None].astype(np.uint8); fr.alpha_composite(Image.fromarray(g), (0, H - 560))
    M.caption(fr, tt, 1470, 52)
    kc = clamp((tt - 0.5) / 0.4) * (1 - clamp((tt - (EDIT_END - 0.3)) / 0.3)); BAR.lower_card(fr, CARD[0], CARD[1], 1680, kc, fs=40)
    cta = clamp((t - segs[2]["t0"]) / 0.4) if t > segs[2]["t0"] else 0.0
    BAR.draw_bar(fr, clamp(t / END_IN), "canal", eo((t - 0.2) / 0.6), cta, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(fr, t)
    if t >= END_IN: fr.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return fr.convert("RGB")
def capa(out):
    from PIL import ImageDraw
    fr = Image.fromarray(src(6.4)).convert("RGBA")
    g = np.zeros((620, W, 4), np.uint8); g[..., :3] = (4, 14, 28); g[..., 3] = np.linspace(235, 0, 620).astype(np.uint8)[:, None]; fr.alpha_composite(Image.fromarray(g), (0, 0))
    g2 = np.zeros((700, W, 4), np.uint8); g2[..., :3] = (4, 14, 28); g2[..., 3] = np.linspace(0, 230, 700).astype(np.uint8)[:, None]; fr.alpha_composite(Image.fromarray(g2), (0, H - 700))
    d = ImageDraw.Draw(fr); sz = 210
    while R.BIGF(sz).getlength("BORA VOTAR!") > 860: sz -= 4
    f = R.BIGF(sz)
    d.text((CX, 300), "BORA VOTAR!", font=f, fill=R.GOLD_L + (255,), anchor="mm", stroke_width=6, stroke_fill=R.NAVY + (255,))
    d.text((CX, 1560), "COM MINHAS DUAS", font=R.MF("ExtraBold", 66), fill=(255, 255, 255, 255), anchor="mm", stroke_width=3, stroke_fill=R.NAVY + (255,))
    d.text((CX, 1650), "ARMAS SECRETAS", font=R.MF("ExtraBold", 66), fill=R.GOLD_L + (255,), anchor="mm", stroke_width=3, stroke_fill=R.NAVY + (255,))
    BAR.draw_bar(fr, 0.0, "canal"); fr.alpha_composite(R.top, (R.HDX, 0)); fr.convert("RGB").save(out, quality=95)
def main():
    if MODE == "lib": return
    if MODE == "capa": capa(OUTFILE); return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(x).resize((360, 640), Image.LANCZOS) for x in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    vout = f"{V}/video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
    for k in range(int(round(TOTAL * FPS))): enc.stdin.write(frame_at(k / FPS).tobytes())
    enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{V}/me.mp4", "-ar", "48000", "-ac", "2", f"{V}/me48.wav"], check=True)
    me = R.readw(f"{V}/me48.wav"); vt = np.zeros((n, 2), np.float32); f = int(0.012 * SR)
    for s in segs:
        c = me[int(s["a"] * SR):int(s["b"] * SR)].copy(); c[:f] *= np.linspace(0, 1, f)[:, None]; c[-f:] *= np.linspace(1, 0, f)[:, None]
        o = int(s["t0"] * SR); vt[o:o + len(c)] += c[:n - o]
    R.writew(f"{V}/voice.wav", vt)
    bed = R.readw(f"{S}/v49/bed.wav"); L = min(len(bed), n); tl = np.arange(L) / SR
    gain = 0.07 * np.clip(tl / 0.8, 0, 1) * np.clip(1 - (tl - (TOTAL - 1.6)) / 1.5, 0, 1); sg = np.zeros((n, 2), np.float32); sg[:L] = bed[:L] * gain[:, None]
    R.writew(f"{V}/song.wav", sg)
    ev = [(0.0, sfx.whoosh(0.4), 0.2), (0.5, sfx.whoosh(0.35), 0.18)] + [(s["t0"] - 0.05, sfx.whoosh(0.3), 0.14) for s in segs[1:]] + [(END_IN - 0.3, sfx.whoosh(0.6), 0.22)]
    sfx.build(ev, TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=80,acompressor=threshold=0.08:ratio=2.5:attack=8:release=200:makeup=1.6,asplit=2[vox][k2];[2:a]volume=0.8[sf];[3:a]volume=0.95[sg];"
                    "[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][sgd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
