"""Reels cinematográfico "A jornada": violino e piano (vídeo de terceiros, só o áudio) do começo ao fim; abre com o áudio do Gustavo Gayer
(PL-GO), divulgado pelo Poder360, sobre os "demônios do petismo" que "saíram da catacumba do inferno", sobre a cidade à noite; depois um
compilado dos vídeos dele em quatro capítulos (A CAMPANHA, O DEBATE, A VOTAÇÃO, A NOITE), em câmera lenta, cor de cinema, faixas pretas,
grão e fusões; o "É tetra!" dele no clímax; fecha com a foto do Lula com a Constituição em zoom lento e os textos finais."""
import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
W, H, FPS = R.W, R.H, R.FPS; CX = W // 2
clamp = R.clamp; eo = R.ease_out; eio = R.ease_io
V = f"{S}/v71"; MUS = f"{V}/v2.mp4"
BARH = 210                                                          # faixas pretas (cinema)
# trechos: (arquivo, início na fonte, duração na tela, velocidade, capítulo)
SHOTS = [("v71/d2.mp4", 0.5, 3.4, 0.5, None),
         ("v61/intro_raw.mp4", 1.9, 2.6, 0.7, "A CAMPANHA"), ("v55/me.mp4", 2.6, 2.6, 0.7, None), ("v54/me.mp4", 6.0, 2.6, 0.7, None), ("v58/me.mp4", 3.4, 2.6, 0.7, None),
         ("v60/raw.mp4", 2.2, 2.6, 0.7, "O DEBATE"), ("v59/cl.mp4", 14.9, 2.8, 0.7, None), ("v67/me.mp4", 5.5, 2.6, 0.7, None),
         ("GAYER", 3.0, 4.4, 0.5, None),
         ("v65/me.mp4", 5.8, 2.8, 0.7, "A VOTAÇÃO"), ("v53/me.mp4", 35.4, 2.6, 0.7, None),
         ("v68/in.mp4", 3.6, 3.0, 0.7, "A NOITE"), ("v69/me.mp4", 5.6, 2.8, 0.7, None),
         ("FOTO", 0, 12.0, 1.0, None)]
segs = []; acc = 0.0
for f, a, d, sp, ch in SHOTS: segs.append(dict(f=f, a=a, d=d, sp=sp, ch=ch, t0=acc, t1=acc + d)); acc += d
EDIT_END = acc; TOTAL = EDIT_END + 2.5; XF = 0.45
MUS_A = 145.5 - EDIT_END                                           # a música termina junto com a foto
TETRA = next(s for s in segs if s["f"] == "v69/me.mp4")
GQ = ("\u201COs demônios do petismo saíram", "da catacumba do inferno.\u201D")
GSEG = next(s for s in segs if s["f"] == "GAYER")
GA_SRC = (24.40, 27.95)                                            # trecho no áudio do Poder360
# cor de cinema: contraste em S, sombras azuladas, luzes quentes, menos saturação
x_ = np.arange(256) / 255.0; sc = np.clip(0.5 + (x_ - 0.5) * 1.12 + 0.06 * np.sin(2 * np.pi * x_) * -1, 0, 1)
LUT = np.stack([np.clip(sc * 255 * (0.96 + 0.08 * x_), 0, 255), np.clip(sc * 255, 0, 255), np.clip(sc * 255 * (1.06 - 0.10 * x_), 0, 255)], 1).astype(np.uint8)[:, None, :]
def grade(img):
    o = cv2.LUT(img, LUT).astype(np.float32); g = o.mean(2, keepdims=True); o = g + (o - g) * 0.82
    return np.clip(o, 0, 255).astype(np.uint8)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); VIG = (1 - 0.42 * np.clip(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.6)) ** 2, 0, 1) ** 1.4)[..., None]
rng = np.random.default_rng(3); GRAIN = [rng.normal(0, 6, (H // 2, W // 2)).astype(np.float32) for _ in range(5)]
_cache = {}
def frames(f, a, n_sec, sp):
    key = (f, a)
    if key not in _cache:
        p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-t", f"{n_sec * sp + 0.3:.3f}", "-i", f"{S}/{f}", "-vf",
                            f"fps=30,scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        n = len(p) // (W * H * 3); _cache[key] = np.frombuffer(p[:n * W * H * 3], np.uint8).reshape(n, H, W, 3)
    return _cache[key]
PHOTO = None
def photo(u, d):
    global PHOTO
    if PHOTO is None:
        im = np.asarray(Image.open(f"{V}/lula.jpg").convert("RGB")); h = int(im.shape[1] * H / W)
        y0 = max(0, (im.shape[0] - h) // 2); PHOTO = cv2.resize(im[y0:y0 + h] if im.shape[0] >= h else im, (W, H), interpolation=cv2.INTER_AREA)
    z = 1.0 + 0.10 * eio(clamp(u / d)); cy = H * 0.42
    M = np.float32([[z, 0, W / 2 * (1 - z)], [0, z, cy * (1 - z)]]); return cv2.warpAffine(PHOTO, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
def shot_img(s, t):
    u = t - s["t0"]
    if s["f"] == "FOTO": return photo(u, s["d"])
    if s["f"] == "GAYER": s = dict(s, f="v71/d2.mp4")
    fr = frames(s["f"], s["a"], s["d"], s["sp"]); img = fr[int(clamp(u * s["sp"] * FPS, 0, len(fr) - 1))]
    z = 1.04 + 0.05 * eio(clamp(u / s["d"])); M = np.float32([[z, 0, W / 2 * (1 - z)], [0, z, H * 0.45 * (1 - z)]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
def text(d, s, x, y, f, col, a, anchor="mm", track=0):
    if a <= 0.01: return
    if not track: d.text((x, y), s, font=f, fill=col + (int(255 * a),), anchor=anchor); return
    w = sum(f.getlength(c) + track for c in s) - track; x0 = x - w / 2
    for c in s: d.text((x0, y), c, font=f, fill=col + (int(255 * a),), anchor="l" + anchor[1]); x0 += f.getlength(c) + track
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); i = next(k for k, s in enumerate(segs) if tt < s["t1"] or k == len(segs) - 1); s = segs[i]
    img = shot_img(s, tt).astype(np.float32)
    if i + 1 < len(segs) and tt > s["t1"] - XF:                     # fusão para o próximo
        k = eio((tt - (s["t1"] - XF)) / XF); img = img * (1 - k) + shot_img(segs[i + 1], segs[i + 1]["t0"]).astype(np.float32) * k
    img = grade(img.astype(np.uint8)).astype(np.float32)
    if s["f"] in ("v71/d2.mp4", "GAYER"): img *= 0.5
    if i == 0: img *= eo(tt / 1.2)
    img = img * VIG + cv2.resize(GRAIN[int(t * 12) % 5], (W, H))[..., None]
    if s is TETRA and tt - s["t0"] < 0.12: img = img + 70 * (1 - (tt - s["t0"]) / 0.12)
    img = np.clip(img, 0, 255).astype(np.uint8)
    img[:BARH] = 0; img[H - BARH:] = 0
    fr = Image.fromarray(img).convert("RGBA"); d = ImageDraw.Draw(fr)
    if i == 0:
        al = clamp((tt - 0.6) / 0.6) * (1 - clamp((tt - 2.6) / 0.5)); text(d, "A JORNADA", CX, 900, R.MF("SemiBold", 46), (240, 236, 228), al, track=16)
        text(d, "OUTUBRO DE 2026", CX, 975, R.MF("Medium", 24), R.GOLD_L, al, track=8)
    if s is GSEG:                                                   # o áudio do Gayer, no meio
        u = tt - s["t0"]; al = clamp((u - 0.4) / 0.35) * (1 - clamp((u - (s["d"] - 0.4)) / 0.35))
        text(d, GQ[0], CX, 880, R.SERIF(50), (240, 236, 228), al); text(d, GQ[1], CX, 950, R.SERIF(50), (240, 236, 228), al)
        ka = al
        text(d, "GUSTAVO GAYER (PL-GO)", CX, 1110, R.MF("SemiBold", 26), R.GOLD_L, ka, track=6)
        text(d, "Áudio divulgado pelo Poder360", CX, 1155, R.MF("Medium", 22), (170, 176, 186), ka)
        bars = 34
        for j in range(bars):                                       # onda sonora fina
            hgt = 6 + 34 * abs(math.sin(tt * 7 + j * 0.7)) * abs(math.sin(j * 0.33 + tt * 2)) * ka
            x0 = CX - bars * 9 + j * 18; d.rounded_rectangle((x0, 1040 - hgt / 2, x0 + 6, 1040 + hgt / 2), 3, fill=R.GOLD + (int(220 * ka),))
    if s["ch"] and tt - s["t0"] < 2.2:                              # título do capítulo
        u = tt - s["t0"]; al = clamp(u / 0.4) * (1 - clamp((u - 1.7) / 0.5))
        text(d, s["ch"], CX, BARH + 70, R.MF("SemiBold", 30), (235, 235, 235), al, track=10)
        d.line((CX - 60, BARH + 105, CX + 60, BARH + 105), fill=R.GOLD + (int(255 * al),), width=2)
    if s is TETRA:
        u = tt - s["t0"]; al = clamp((u - 0.05) / 0.15) * (1 - clamp((u - 1.9) / 0.3))
        sz = 210; f = R.BIGF(sz)
        d.text((CX + 5, H - BARH - 230 + 7), "É TETRA!", font=f, fill=(0, 0, 0, int(120 * al)), anchor="mm")
        d.text((CX, H - BARH - 230), "É TETRA!", font=f, fill=R.GOLD_L + (int(255 * al),), anchor="mm", stroke_width=5, stroke_fill=R.NAVY + (int(255 * al),))
    if s["f"] == "FOTO":
        u = tt - s["t0"]
        g = np.zeros((560, W, 4), np.uint8); g[..., 3] = (np.linspace(0, 200, 560) * clamp(u / 1.0)).astype(np.uint8)[:, None]; fr.alpha_composite(Image.fromarray(g), (0, H - BARH - 560))
        d = ImageDraw.Draw(fr)
        a1 = clamp((u - 1.2) / 0.8) * (1 - clamp((u - 6.2) / 0.6)); a2 = clamp((u - 6.8) / 0.8)
        text(d, "Das catacumbas…", CX, H - BARH - 330, R.SERIF(78), (245, 240, 230), a1)
        text(d, "às urnas.", CX, H - BARH - 230, R.SERIF(96), R.GOLD_L, clamp((u - 2.6) / 0.8) * (1 - clamp((u - 6.2) / 0.6)))
        text(d, "25 · 10 · 2026", CX, H - BARH - 330, R.MF("SemiBold", 44), (245, 240, 230), a2, track=10)
        text(d, "O povo decidiu.", CX, H - BARH - 230, R.SERIF(92), R.GOLD_L, clamp((u - 7.8) / 0.8))
        text(d, "Foto: Ricardo Stuckert", W - 70, H - BARH - 40, R.MF("Medium", 18), (170, 176, 186), clamp((u - 1) / 0.5), anchor="rm")
        text(d, "@eliezio.souza78", CX, H - BARH / 2, R.MF("SemiBold", 26), R.GOLD_L, clamp((u - 8.5) / 0.6), track=3)
    if t >= EDIT_END: fr.alpha_composite(R.fade(R.end_card(t - EDIT_END + R.END_IN), clamp((t - EDIT_END) / 0.5)))
    return fr.convert("RGB")
def capa(out):
    fr = Image.fromarray(np.clip(grade(photo(8, 12.5)).astype(np.float32) * VIG, 0, 255).astype(np.uint8)).convert("RGBA")
    g = np.zeros((700, W, 4), np.uint8); g[..., 3] = np.linspace(0, 220, 700).astype(np.uint8)[:, None]; fr.alpha_composite(Image.fromarray(g), (0, H - 700))
    d = ImageDraw.Draw(fr)
    text(d, "A JORNADA", CX, 1460, R.MF("SemiBold", 40), (235, 235, 235), 1.0, track=14)
    text(d, "Das catacumbas…", CX, 1580, R.SERIF(92), (245, 240, 230), 1.0)
    text(d, "às urnas.", CX, 1700, R.SERIF(110), R.GOLD_L, 1.0)
    fr.alpha_composite(R.top, (R.HDX, 0)); fr.convert("RGB").save(out, quality=95)
def main():
    if MODE == "lib": return
    if MODE == "capa": capa(OUTFILE); return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(x).resize((360, 640), Image.LANCZOS) for x in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    if MODE == "info": print("TOTAL", round(TOTAL, 2), [(s["f"], round(s["t0"], 2)) for s in segs]); return
    vout = f"{V}/video.mp4"
    if not (os.environ.get("REUSE") and os.path.exists(vout)):
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
        for k in range(int(round(TOTAL * FPS))): enc.stdin.write(frame_at(k / FPS).tobytes())
        enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{MUS_A}", "-t", f"{TOTAL:.2f}", "-i", MUS, "-ar", "48000", "-ac", "2", f"{V}/mus.wav"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{GA_SRC[0]}", "-t", f"{GA_SRC[1] - GA_SRC[0]:.2f}", "-i", f"{V}/vio.mp4", "-ar", "48000", "-ac", "2", f"{V}/gayer.wav"], check=True)
    mus = R.readw(f"{V}/mus.wav"); m = np.zeros((n, 2), np.float32); L = min(len(mus), n); m[:L] = mus[:L]
    tl = np.arange(n) / SR
    g = np.clip(tl / 2.0, 0, 1) * np.clip(1 - (tl - (TOTAL - 2.2)) / 2.0, 0, 1)
    g = g * (1 - 0.72 * np.clip(np.minimum((tl - GSEG["t0"] + 0.3) / 0.4, (GSEG["t1"] + 0.2 - tl) / 0.4), 0, 1))   # abre espaço para o Gayer
    m *= g[:, None]
    def rms(c): return float(np.sqrt((c ** 2).mean())) + 1e-6
    ga = R.readw(f"{V}/gayer.wav"); ga *= 0.12 / rms(ga); o = int((GSEG["t0"] + 0.4) * SR); m[o:o + len(ga)] += ga[:n - o]
    R.writew(f"{V}/mix.wav", m)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/mix.wav", "-filter_complex", f"[1:a]alimiter=limit=0.85:level=false,atrim=0:{TOTAL:.2f}[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
