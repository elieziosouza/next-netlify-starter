"""Noite da vitória: "É tetra, é tetra! Eu falei que ia ser histórico, é tetra! Bora, Lula!" (ele com o L). Karaokê + caixa fixa, palavra
"É TETRA" acima da cabeça, trilha funk animada (troque pela "Vai dar PT" no app). Usa os ajudantes do render_exercito."""

import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("rex", f"{S}/work/render_exercito.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
sys.path.insert(0, f"{S}/work")
import cor_fla, sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; eo = R.ease_out
V = f"{S}/v69"
PARTS = [(0.05, 6.55, None), (7.95, 9.60, None), (10.40, 11.50, 4.75)]               # o último trecho (ele sorrindo) vai e volta enquanto a música toca
segs = []; acc = 0.0
for a, b, d in PARTS:
    dur = d or b - a; segs.append(dict(src="me", a=a, b=b, t0=acc, t1=acc + dur, loop=bool(d))); acc += dur
FIN_IN = segs[1]["t1"]; MUS_IN = FIN_IN - 4.87                     # o primeiro "vai dar PT" da música cai logo depois do "bora, Lula!"
R.LYR = [(4.87, 5.73, "VAI DAR PT"), (5.73, 6.73, "VAI DAR"), (6.73, 8.23, "VAI DAR PT"), (8.23, 9.43, "VAI DAR PT")]
EDIT_END = acc; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = FIN_IN; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = MUS_IN
def seg_at(t):
    for i, s in enumerate(segs):
        if t < s["t1"]: return i
    return len(segs) - 1
ME_CAPS = [("É TETRA!", 0.12, 1.25), ("É TETRA!", 1.25, 2.40), ("EU FALEI QUE", 2.40, 3.40), ("IA SER HISTÓRICO!", 3.40, 4.80), ("É TETRA!", 4.80, 6.40),
           ("BORA, LULA!", 8.09, 9.40)]
HOT = {"TETRA!", "HISTÓRICO!", "LULA!"}
CAPS = []
for txt, a, b in ME_CAPS:
    for s in segs:
        a1, b1 = max(a, s["a"]), min(b, s["b"])
        if b1 - a1 < 0.2: continue
        a2, b2 = s["t0"] + a1 - s["a"], s["t0"] + b1 - s["a"]; ws = txt.split(); tot = sum(len(w) + 2 for w in ws); k = 0; ts = []
        for w in ws: ts.append(a2 + (b2 - a2 - 0.08) * k / tot); k += len(w) + 2
        CAPS.append(dict(words=ws, ts=ts, start=a2, end=b2, src="au" if any(w in HOT for w in ws) else "me"))
CAPS.sort(key=lambda c: c["start"]); R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
BIG = [(0.12, 2.40, "É TETRA!"), (4.80, 6.55, "É TETRA!"), (8.0, 9.6, "BORA, LULA!")]
CARD = ("NOITE DE 25/10", ["É TETRA!", "LULA DE NOVO"])
_fr = {}
def src(x):
    if not _fr:
        p = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{V}/me.mp4", "-vf", "fps=30", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        n = len(p) // (W * H * 3); _fr["a"] = np.frombuffer(p[:n * W * H * 3], np.uint8).reshape(n, H, W, 3)
    a = _fr["a"]; return cv2.LUT(a[int(clamp(x * FPS, 0, len(a) - 1))], R.LUT)
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); i = seg_at(tt); s = segs[i]; x = s["a"] + tt - s["t0"]
    if s["loop"]:
        Lp = s["b"] - s["a"]; p_ = ((tt - s["t0"]) * 0.6) % (2 * Lp); x = s["a"] + (p_ if p_ < Lp else 2 * Lp - p_)
    z = (1.0 if i % 2 == 0 else 1.04) + 0.03 * (0.5 - 0.5 * math.cos(2 * math.pi * tt / 7.0))
    fr = Image.fromarray(M.zoom(src(x), z, 540, 760)).convert("RGBA")
    g = np.zeros((560, W, 4), np.uint8); g[..., :3] = (4, 14, 28); g[..., 3] = np.linspace(0, 210, 560)[:, None].astype(np.uint8); fr.alpha_composite(Image.fromarray(g), (0, H - 560))
    for j, (a_, b_, w_) in enumerate(BIG):
        if a_ <= x < b_: lay, dx, y = M.big_layer(w_, R.GOLD_L, x - a_, b_ - a_, True, j); fr.alpha_composite(lay, (dx, y))
    M.caption(fr, tt, 1470, 52)
    kc = clamp((tt - 0.5) / 0.4) * (1 - clamp((tt - (FIN_IN - 0.2)) / 0.3)); BAR.lower_card(fr, CARD[0], CARD[1], 1680, kc, fs=40)
    if tt >= FIN_IN - 0.1: R.lyrics(fr, tt)
    cta = clamp((t - segs[2]["t0"]) / 0.4) if t > segs[2]["t0"] else 0.0
    BAR.draw_bar(fr, clamp(t / END_IN), "canal", eo((t - 0.2) / 0.6), cta, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(fr, t)
    if t >= END_IN: fr.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return fr.convert("RGB")
def capa(out):
    from PIL import ImageDraw
    fr = Image.fromarray(src(6.3)).convert("RGBA")
    g = np.zeros((620, W, 4), np.uint8); g[..., :3] = (4, 14, 28); g[..., 3] = np.linspace(235, 0, 620).astype(np.uint8)[:, None]; fr.alpha_composite(Image.fromarray(g), (0, 0))
    g2 = np.zeros((600, W, 4), np.uint8); g2[..., :3] = (4, 14, 28); g2[..., 3] = np.linspace(0, 230, 600).astype(np.uint8)[:, None]; fr.alpha_composite(Image.fromarray(g2), (0, H - 600))
    d = ImageDraw.Draw(fr); sz = 260
    while R.BIGF(sz).getlength("É TETRA!") > 860: sz -= 4
    d.text((CX, 300), "É TETRA!", font=R.BIGF(sz), fill=R.GOLD_L + (255,), anchor="mm", stroke_width=7, stroke_fill=R.NAVY + (255,))
    d.text((CX, 1640), "EU FALEI QUE IA SER HISTÓRICO", font=R.MF("ExtraBold", 46), fill=(255, 255, 255, 255), anchor="mm", stroke_width=3, stroke_fill=R.NAVY + (255,))
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
        c = me[int(s["a"] * SR):int(s["b"] * SR)].copy()
        if s["loop"]: c *= 0.6; c[:f] *= np.linspace(0, 1, f)[:, None]; c[-f:] *= np.linspace(1, 0, f)[:, None]
        o = int(s["t0"] * SR); vt[o:o + len(c)] += c[:n - o]
    R.writew(f"{V}/voice.wav", vt)
    song = R.readw(f"{S}/v15/song_vox.wav"); o = int(MUS_IN * SR); Ls = min(len(song), n - o); tl = np.arange(Ls) / SR; lead = FIN_IN - MUS_IN
    gain = np.where(tl < lead, 10 ** ((-20 + 14 * tl / lead) / 20), 1.0) * np.clip(1 - (tl - (TOTAL - MUS_IN - 1.6)) / 1.5, 0, 1)
    sg = np.zeros((n, 2), np.float32); sg[o:o + Ls] = song[:Ls] * gain[:, None]
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
