"""Corte do debate: Flávio chamou o Lula de "nove dedos". Abre direto no trecho do Lula (debate da Globo, 5.3-20.0 s, para antes do "miliciano")
num card grande com o gancho em cima e ele reagindo num círculo; depois o fechamento dele em tela cheia (palavras acima da cabeça, legenda,
♿ e 👷, zoom leve contínuo). Usa os ajudantes do render_exercito."""
import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("rex", f"{S}/work/render_exercito.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; ease_out = R.ease_out; ease_in = R.ease_in; ease_io = R.ease_io
V = f"{S}/v60"; M.ME = f"{V}/raw.mp4"; M._ch.clear(); M._gr.clear(); CL = f"{S}/v59/cl.mp4"; BLUE = M.BLUE
PARTS = [("cl", 5.30, 20.0, "clip"), ("me", 0.45, 7.10, "full"), ("me", 7.30, 10.05, "full"), ("me", 10.38, 12.70, "full"), ("me", 12.98, 15.55, "full")]
segs = []; acc = 0.0
for src_, a, b, mode in PARTS: segs.append(dict(src=src_, a=a, b=b, mode=mode, t0=acc, t1=acc + b - a)); acc += b - a
EDIT_END = acc; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = EDIT_END; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
def seg_at(t):
    for i, s in enumerate(segs):
        if t < s["t1"]: return i
    return len(segs) - 1
def om(src_, x):
    for s in segs:
        if s["src"] == src_ and s["a"] <= x <= s["b"]: return s["t0"] + x - s["a"]
    return None
ME_CAPS = [("QUEM PERDE UM DEDO TRABALHANDO", 0.57, 2.05), ("NÃO TEM DO QUE SE ENVERGONHAR.", 2.1, 3.34), ("NA MINHA OPINIÃO,", 3.53, 4.35),
           ("ESSE DEBOCHE", 4.4, 5.25), ("OFENDEU CADA PESSOA", 5.35, 6.2), ("COM DEFICIÊNCIA", 6.2, 7.0), ("E CADA TRABALHADOR", 7.4, 8.25),
           ("QUE JÁ SE MACHUCOU", 8.3, 9.05), ("NO SERVIÇO.", 9.1, 10.0), ("QUANDO FALTA ARGUMENTO,", 10.46, 11.5), ("SOBRA OFENSA.", 11.55, 12.62),
           ("E VOCÊ, O QUE VOCÊ ACHOU?", 13.07, 14.25), ("COMENTA AQUI ABAIXO.", 14.38, 15.45)]
HOT = {"DEDO", "ENVERGONHAR.", "DEBOCHE", "DEFICIÊNCIA", "TRABALHADOR", "MACHUCOU", "ARGUMENTO,", "OFENSA.", "COMENTA"}
CAPS = []
for txt, a, b in ME_CAPS:
    for s in segs:
        if s["src"] != "me": continue
        a1, b1 = max(a, s["a"]), min(b, s["b"])
        if b1 - a1 < 0.25: continue
        a2, b2 = s["t0"] + a1 - s["a"], s["t0"] + b1 - s["a"]; ws = txt.split(); tot = sum(len(w) + 2 for w in ws); k = 0; ts = []
        for w in ws: ts.append(a2 + (b2 - a2 - 0.08) * k / tot); k += len(w) + 2
        CAPS.append(dict(words=ws, ts=ts, start=a2, end=b2, src="au" if any(w in HOT for w in ws) else "me"))
CAPS.sort(key=lambda c: c["start"]); R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
# palavras grandes ACIMA da cabeça (tempo da fonte "me"), sem recorte
BIG = [(0.57, 3.4, "DIGNIDADE", R.WHITE, False), (4.4, 7.1, "DEBOCHE", R.GOLD_L, True), (7.38, 10.05, "TRABALHADOR", R.WHITE, False),
       (10.46, 11.55, "FALTA ARGUMENTO", R.WHITE, False), (11.55, 12.7, "SOBRA OFENSA", R.GOLD_L, True), (14.38, 15.55, "COMENTA", R.GOLD_L, True)]
ICONS = [(5.35, 7.1, "♿", 880, 1150, 150), (7.4, 10.05, "👷", 880, 1150, 150), (13.07, 15.55, "💬", 880, 1150, 150)]
CLIP_POPS = [(5.55, "😳", 900, 420), (15.0, "☝️", 180, 900)]
CW = 640; CH = 1131; CY0 = 335
_cl = {}
def cl_frame(x):
    if not _cl:
        p = subprocess.run(["ffmpeg", "-v", "error", "-i", CL, "-vf", f"fps=30,scale={CW}:{CH}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        n = len(p) // (CW * CH * 3); _cl["a"] = np.frombuffer(p[:n * CW * CH * 3], np.uint8).reshape(n, CH, CW, 3)
    a = _cl["a"]; return a[int(clamp(x * FPS, 0, len(a) - 1))]
def listen_x(t):                                                       # ele calado no fim do vídeo, vai e volta em câmera lenta
    L = 1.2; p = (t * 0.4) % (2 * L); return 16.0 + (p if p < L else 2 * L - p)
def top_word(frame, txt, cy, col, k, maxh=130, maxw=900):
    size = 200; f = R.BIGF(size)
    while f.getlength(txt) > maxw or (f.getbbox(txt)[3] - f.getbbox(txt)[1]) > maxh: size -= 4; f = R.BIGF(size)
    lay = Image.new("RGBA", (W, int(size * 1.4)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text((CX + 4, lay.height / 2 + 6), txt, font=f, fill=(0, 0, 0, 110), anchor="mm")
    d.text((CX, lay.height / 2), txt, font=f, fill=col + (255,), anchor="mm", stroke_width=5, stroke_fill=R.NAVY + (255,))
    sc = 1.15 - 0.15 * ease_out(k / 0.3)
    if abs(sc - 1) > 0.003:
        nw, nh = int(W * sc), int(lay.height * sc); bg = lay.resize((nw, nh), Image.BICUBIC); ox = int(CX * sc - CX); oy = (nh - lay.height) // 2
        lay = bg.crop((ox, oy, ox + W, oy + lay.height))
    frame.alpha_composite(R.fade(lay, ease_out(k / 0.25)), (0, int(cy - lay.height / 2)))
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); i = seg_at(tt); s = segs[i]; u = tt - s["t0"]; x = s["a"] + u
    if s["mode"] == "clip":
        bgm, _ = M.graded(listen_x(tt))
        base = cv2.resize(cv2.GaussianBlur(cv2.resize(bgm, (108, 192)), (0, 0), 3), (W, H)).astype(np.float32) * 0.35
        frame = Image.fromarray(base.astype(np.uint8)).convert("RGBA")
        kin = ease_out(u / 0.35); zc = 1.0 + 0.03 * (0.5 - 0.5 * math.cos(2 * math.pi * tt / 7.0))
        card = cl_frame(x)
        if zc > 1.001: card = cv2.warpAffine(card, np.float32([[zc, 0, CW / 2 * (1 - zc)], [0, zc, CH * 0.4 * (1 - zc)]]), (CW, CH), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        ci = Image.fromarray(R.rounded(card, 26, 4))
        R.paste(frame, R.fade(ci, kin), CX - ci.width / 2, CY0 + 200 * (1 - kin), 0.65, 24, (10, 26))
        if u < 3.4:                                                    # gancho
            R.pill(frame, "NO DEBATE, O FLÁVIO CHAMOU O LULA DE", CX, 128, clamp(u / 0.25), fill=BLUE, size=30)
            top_word(frame, "“NOVE DEDOS”", 262, R.GOLD_L, u, maxh=105)
        else:
            R.pill(frame, "AGORA OLHA A RESPOSTA DO LULA", CX, 128, clamp((u - 3.4) / 0.25), fill=R.NAVY, size=30)
            top_word(frame, "A RESPOSTA", 262, R.WHITE, u - 3.4, maxh=105)
        R.credit(frame, "Debate do 2º turno · TV Globo", CX, CY0 + CH + 30, kin, anchor="mm")
        if x >= 14.9:
            kk = clamp((x - 14.9) / 0.25); txt = "LULA PERDEU O DEDO NUMA METALÚRGICA EM 1964"; sz = 32
            while R.MF("ExtraBold", sz).getlength(txt) + 50 > 820: sz -= 1
            R.pill(frame, txt, CX + 30, 1665, kk, fill=BLUE, size=sz)
            M.pop(frame, M.emoji("👷", 64), CX + 30 - (R.MF("ExtraBold", sz).getlength(txt) + 50) / 2 - 42, 1665, x - 14.9, 99, wob=False)
        for t0, ch, cx, cy in CLIP_POPS:
            if 0 <= x - t0 < 1.5: M.pop(frame, M.emoji(ch, 140), cx, cy, x - t0, 1.5)
        pip, _ = M.graded(listen_x(tt)); pw = 250
        pc = cv2.resize(pip[300:1300, 30:1030], (pw, pw), interpolation=cv2.INTER_AREA)
        mask = np.zeros((pw, pw), np.uint8); cv2.circle(mask, (pw // 2, pw // 2), pw // 2 - 2, 255, -1)
        pim = Image.fromarray(pc).convert("RGBA"); pim.putalpha(Image.fromarray(mask))
        ring = Image.new("RGBA", (pw + 14, pw + 14), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((0, 0, pw + 13, pw + 13), fill=R.GOLD + (255,)); ring.alpha_composite(pim, (7, 7))
        kp = R.back_out(clamp((u - 0.5) / 0.35), 2.0); rs = ring.resize((max(1, int(ring.width * kp)), max(1, int(ring.height * kp))))
        R.paste(frame, rs, CX + 330 - rs.width / 2, CY0 + CH + 10 - rs.height / 2, 0.6, 16, (6, 14))
    else:
        z = M.zoom_level(tt, i)
        for a, b, w_, c_, shk in BIG:
            if shk and 0 <= x - a < 0.4: z += 0.04 * (1 - (x - a) / 0.4)
        img, idx = M.graded(x); img = M.zoom(img, z); frame = Image.fromarray(img).convert("RGBA")
        for j, (a, b, word, col, shk) in enumerate(BIG):
            if a <= x < b: lay, dx, y = M.big_layer(word, col, x - a, b - a, shk, j); frame.alpha_composite(lay, (dx, y))
        g = np.zeros((520, W, 4), np.uint8); g[..., :3] = (4, 14, 28); g[..., 3] = np.linspace(0, 200, 520)[:, None].astype(np.uint8); frame.alpha_composite(Image.fromarray(g), (0, H - 520))
        for a, b, ch, cx, cy, sz in ICONS:
            if a <= x < b: M.pop(frame, M.emoji(ch, sz), cx, cy, x - a, b - a)
        M.caption(frame, tt, 1520, 50)
    cta = clamp((t - segs[-1]["t0"]) / 0.4) if t >= segs[-1]["t0"] else 0.0
    BAR.draw_bar(frame, clamp(t / END_IN), "canal", ease_out((t - 0.2) / 0.6), cta, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(frame, t)
    for j in range(1, len(segs)):
        if segs[j]["mode"] != segs[j - 1]["mode"] and abs(t - segs[j]["t0"]) < 0.08:
            frame = Image.blend(frame, Image.new("RGBA", frame.size, (255, 255, 255, 255)), (1 - abs(t - segs[j]["t0"]) / 0.08) * 0.35)
    if t >= END_IN: frame.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return frame.convert("RGB")
def main():
    if MODE == "lib": return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(t).resize((360, 640), Image.LANCZOS) for t in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    if MODE == "info": print("TOTAL", round(TOTAL, 2), [(s["src"], s["mode"], round(s["t0"], 2)) for s in segs]); return
    vout = f"{V}/video.mp4"
    if not (os.environ.get("REUSE") and os.path.exists(vout)):
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
        for k in range(int(round(TOTAL * FPS))): enc.stdin.write(frame_at(k / FPS).tobytes())
        enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    for nm, p in (("me", M.ME), ("cl", CL)): subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-ar", "48000", "-ac", "2", f"{V}/{nm}48.wav"], check=True)
    src = {"me": R.readw(f"{V}/me48.wav"), "cl": R.readw(f"{V}/cl48.wav")}
    def rms(c): v = c[np.abs(c).max(1) > 0.01]; return float(np.sqrt((v ** 2).mean())) if len(v) else 1e-6
    ref = {k: np.median([rms(src[k][int(s["a"] * SR):int(s["b"] * SR)]) for s in segs if s["src"] == k]) for k in src}
    vt = np.zeros((n, 2), np.float32); f = int(0.012 * SR)
    for s in segs:
        c = src[s["src"]][int(s["a"] * SR):int(s["b"] * SR)].copy()
        if s["src"] == "cl": c *= 10 ** (-1.0 / 20) * ref["me"] / ref["cl"]
        else: c *= min(2.0, ref["me"] / rms(c))
        fl = int(0.08 * SR) if s["src"] == "cl" else f
        c[:fl] *= np.linspace(0, 1, fl)[:, None]; c[-fl:] *= np.linspace(1, 0, fl)[:, None]
        o = int(s["t0"] * SR); vt[o:o + len(c)] += c[:n - o]
    R.writew(f"{V}/voice.wav", vt)
    bed = R.readw(os.environ.get("BED", f"{S}/v52/tense.wav")); L = min(len(bed), n); tl = np.arange(L) / SR
    gain = (float(os.environ.get("BEDG", "0.15")) * np.clip(tl / 1.0, 0, 1) + 0.08 * np.clip((tl - (EDIT_END - 0.3)) / 0.5, 0, 1)) * np.clip(1 - (tl - (TOTAL - 1.6)) / 1.5, 0, 1)
    sg = np.zeros((n, 2), np.float32); sg[:L] = bed[:L] * gain[:, None]; R.writew(f"{V}/song.wav", sg)
    ev = [(0.0, sfx.whoosh(0.4), 0.2), (0.05, sfx.thud(0.5), 0.4), (3.4, sfx.whoosh(0.35), 0.22), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
    ev += [(om("cl", t0), sfx.click(), 0.45) for t0, *_r in CLIP_POPS] + [(om("cl", 14.9), sfx.click(), 0.45)]
    for a, b, w_, c_, shk in BIG:
        ta = om("me", a)
        if ta is not None: ev += [(ta, sfx.whoosh(0.35), 0.22)] + ([(ta + 0.26, sfx.click(), 0.7), (ta + 0.26, sfx.thud(0.3), 0.2)] if shk else [])
    for a, *_r in ICONS:
        ta = om("me", a)
        if ta is not None: ev += [(ta, sfx.click(), 0.45)]
    ev += [(segs[1]["t0"] - 0.1, sfx.whoosh(0.45), 0.26)]
    sfx.build([e for e in ev if e[0] is not None and 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=80,acompressor=threshold=0.08:ratio=2.5:attack=8:release=200:makeup=1.6,asplit=2[vox][k2];[2:a]volume=0.8[sf];[3:a]volume=0.95[sg];"
                    "[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][sgd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
