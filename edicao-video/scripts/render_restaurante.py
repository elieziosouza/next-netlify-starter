"""Humor: "vou levar minha esposa nesse restaurante, me disseram que o atendimento lá é muito bom" + o vídeo do restaurante temático de Natal
(atendimento "do Nordeste antigo", ELLO TV) num card com ele reagindo no canto + a cara séria dele no fim com zoom lento ("MUDEI DE IDEIA").
O áudio do restaurante sai (tem música, risco de direitos); entram a trilha nossa e efeitos. Usa os ajudantes do render_exercito."""
import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("rex", f"{S}/work/render_exercito.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; ease_out = R.ease_out; ease_in = R.ease_in; ease_io = R.ease_io
V = f"{S}/v56"; M.ME = f"{V}/me.mp4"; M._ch.clear(); M._gr.clear(); CL = f"{V}/cl.mp4"; BLUE = M.BLUE
PARTS = [("me", 0.55, 4.66, "full"), ("cl", 0.2, 12.6, "clip"), ("me", 4.9, 9.3, "stare")]
segs = []; acc = 0.0
for src_, a, b, mode in PARTS: segs.append(dict(src=src_, a=a, b=b, mode=mode, t0=acc, t1=acc + b - a)); acc += b - a
EDIT_END = acc; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = EDIT_END; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
def seg_at(t):
    for i, s in enumerate(segs):
        if t < s["t1"]: return i
    return len(segs) - 1
ME_CAPS = [("ACHO QUE EU VOU LEVAR", 0.62, 1.5), ("A MINHA ESPOSA", 1.5, 2.2), ("NESSE RESTAURANTE AQUI.", 2.2, 3.0), ("ME DISSERAM QUE O ATENDIMENTO", 3.0, 3.9),
           ("LÁ É MUITO BOM.", 3.9, 4.6)]
HOT = {"ESPOSA", "RESTAURANTE", "ATENDIMENTO", "MUITO", "BOM."}
CAPS = []
for txt, a, b in ME_CAPS:
    a2, b2 = a - 0.55, b - 0.55; ws = txt.split(); tot = sum(len(w) + 2 for w in ws); k = 0; ts = []
    for w in ws: ts.append(a2 + (b2 - a2 - 0.08) * k / tot); k += len(w) + 2
    CAPS.append(dict(words=ws, ts=ts, start=a2, end=b2, src="au" if any(w in HOT for w in ws) else "me"))
R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
BIG = [(1.5, 3.0, "MINHA ESPOSA", R.GOLD_L, False), (3.9, 4.66, "MUITO BOM", R.WHITE, True), (6.4, 9.3, "MUDEI DE IDEIA", R.GOLD_L, True)]
ICONS = [(1.6, 3.0, "😍", 880, 1150, 150), (3.0, 4.66, "🍽️", 880, 1150, 150), (6.6, 9.3, "😅", 880, 1150, 170)]
CLIP_POPS = [(1.4, "😳", 230, 520), (4.2, "🍽️", 880, 560), (6.9, "😱", 230, 1200), (9.4, "😂", 880, 1150), (11.0, "🤣", 230, 560)]
_cl = {}
def cl_frame(x):
    if not _cl:
        p = subprocess.run(["ffmpeg", "-v", "error", "-i", CL, "-vf", "fps=30,crop=720:980:0:20,scale=700:953", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        n = len(p) // (700 * 953 * 3); _cl["a"] = np.frombuffer(p[:n * 700 * 953 * 3], np.uint8).reshape(n, 953, 700, 3)
    a = _cl["a"]; return a[int(clamp(x * FPS, 0, len(a) - 1))]
def me_layer(x, z):
    img, idx = M.graded(x); img = M.zoom(img, z); return img
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); i = seg_at(tt); s = segs[i]; u = tt - s["t0"]; x = s["a"] + u
    if s["mode"] == "clip":
        bgm, _ = M.graded(5.2 + (tt * 0.3) % 1.5)
        base = cv2.resize(cv2.GaussianBlur(cv2.resize(bgm, (108, 192)), (0, 0), 3), (W, H)).astype(np.float32) * 0.35
        frame = Image.fromarray(base.astype(np.uint8)).convert("RGBA")
        kin = ease_out(u / 0.4); card = R.rounded(cv2.LUT(cl_frame(x), R.LUT), 26, 4)
        ci = Image.fromarray(card).rotate(-1.2, resample=Image.BICUBIC, expand=True)
        R.paste(frame, R.fade(ci, kin), CX - ci.width / 2, 260 + 250 * (1 - kin), 0.65, 24, (10, 26))
        R.pill(frame, "RESTAURANTE TEMÁTICO EM NATAL · VÍDEO: ELLO TV", CX, 230, clamp(u / 0.3), fill=BLUE, size=26)
        for t0, ch, cx, cy in CLIP_POPS:
            if 0 <= x - t0 < 1.4: M.pop(frame, M.emoji(ch, 150), cx, cy, x - t0, 1.4)
        pip, _ = M.graded(5.2 + (tt * 0.35) % 1.4); pw = 300
        pc = cv2.resize(pip[380:1380, 40:1040], (pw, pw), interpolation=cv2.INTER_AREA)
        mask = np.zeros((pw, pw), np.uint8); cv2.circle(mask, (pw // 2, pw // 2), pw // 2 - 2, 255, -1)
        pim = Image.fromarray(pc).convert("RGBA"); pim.putalpha(Image.fromarray(mask))
        ring = Image.new("RGBA", (pw + 16, pw + 16), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((0, 0, pw + 15, pw + 15), fill=R.GOLD + (255,)); ring.alpha_composite(pim, (8, 8))
        kp = R.back_out(clamp((u - 0.3) / 0.35), 2.0); rs = ring.resize((max(1, int(ring.width * kp)), max(1, int(ring.height * kp))))
        R.paste(frame, rs, CX + 250 - rs.width / 2, 1500 - rs.height / 2, 0.6, 16, (6, 14))
    else:
        if s["mode"] == "stare": z = 1.0 + 0.22 * ease_io(clamp(u / 3.8))           # zoom lento no olhar sério
        else: z = 1.0 + 0.03 * (0.5 - 0.5 * math.cos(2 * math.pi * tt / 7.0))
        img = me_layer(x, z); frame = Image.fromarray(img).convert("RGBA")
        for j, (a, b, word, col, shk) in enumerate(BIG):
            if a <= x < b: lay, dx, y = M.big_layer(word, col, x - a, b - a, shk, j); frame.alpha_composite(lay, (dx, y))
        g = np.zeros((520, W, 4), np.uint8); g[..., :3] = (4, 14, 28); g[..., 3] = np.linspace(0, 200, 520)[:, None].astype(np.uint8); frame.alpha_composite(Image.fromarray(g), (0, H - 520))
        for a, b, ch, cx, cy, sz in ICONS:
            if a <= x < b: M.pop(frame, M.emoji(ch, sz), cx, cy, x - a, b - a)
        if s["mode"] == "full": M.caption(frame, tt, 1520, 50)
    BAR.draw_bar(frame, clamp(t / END_IN), "canal", ease_out((t - 0.2) / 0.6), 0.0, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(frame, t)
    for j in range(1, len(segs)):
        if abs(t - segs[j]["t0"]) < 0.08: frame = Image.blend(frame, Image.new("RGBA", frame.size, (255, 255, 255, 255)), (1 - abs(t - segs[j]["t0"]) / 0.08) * 0.35)
    if t >= END_IN: frame.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return frame.convert("RGB")
def main():
    if MODE == "lib": return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(t).resize((360, 640), Image.LANCZOS) for t in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    if MODE == "info": print("TOTAL", round(TOTAL, 2), [(s["mode"], round(s["t0"], 2)) for s in segs]); return
    vout = f"{V}/video.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
    for k in range(int(round(TOTAL * FPS))): enc.stdin.write(frame_at(k / FPS).tobytes())
    enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", M.ME, "-ar", "48000", "-ac", "2", f"{V}/me48.wav"], check=True)
    me = R.readw(f"{V}/me48.wav"); vt = np.zeros((n, 2), np.float32); s0 = segs[0]; f = int(0.012 * SR)
    c = me[int(s0["a"] * SR):int(s0["b"] * SR)].copy(); c[:f] *= np.linspace(0, 1, f)[:, None]; c[-f:] *= np.linspace(1, 0, f)[:, None]; vt[:len(c)] += c
    R.writew(f"{V}/voice.wav", vt)
    bed = R.readw(f"{S}/v49/bed.wav"); L = min(len(bed), n); tl = np.arange(L) / SR
    gain = np.where(tl < segs[1]["t0"], 0.06, np.where(tl < segs[2]["t0"], 0.30, 0.0)) * np.clip(1 - (tl - (TOTAL - 1.6)) / 1.5, 0, 1)
    gain = gain + 0.10 * np.clip((tl - END_IN) / 0.3, 0, 1) * (tl >= END_IN)
    sg = np.zeros((n, 2), np.float32); sg[:L] = bed[:L] * gain[:, None]; R.writew(f"{V}/song.wav", sg)
    ev = [(0.0, sfx.whoosh(0.4), 0.2), (segs[1]["t0"] - 0.12, sfx.whoosh(0.5), 0.3), (segs[2]["t0"], sfx.thud(0.6), 0.6), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
    ev += [(segs[1]["t0"] + t0 - 0.2, sfx.click(), 0.5) for t0, *_r in CLIP_POPS]
    ev += [(a - 0.55, sfx.click(), 0.6) for a, *_r in BIG if a < 5] + [(segs[2]["t0"] + 6.4 - 4.9, sfx.thud(0.4), 0.5), (segs[2]["t0"] + 6.4 - 4.9 + 0.26, sfx.click(), 0.7)]
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=80,acompressor=threshold=0.08:ratio=2.5:attack=8:release=200:makeup=1.6[vox];[2:a]volume=0.8[sf];[3:a]volume=0.95[sg];"
                    f"[vox][sf][sg]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
