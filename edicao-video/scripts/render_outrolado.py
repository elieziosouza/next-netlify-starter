"""Humor: a reação do pessoal do Flávio assistindo a apuração (vídeo das redes), num card grande; a legenda gravada ("laiakkaka") fica
desfocada; caixa fixa no começo e, depois, a música "vai dar PT" com a letra (PT na pílula vermelha). Câmera lenta no final (o close).
Sem xingamento nem texto ofensivo. Usa os ajudantes do render_exercito."""
import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("rex", f"{S}/work/render_exercito.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; eo = R.ease_out
V = f"{S}/v70"
# (início, fim, velocidade) no vídeo deles
PARTS = [(0.0, 9.8, 1.0), (9.8, 14.8, 0.6)]
segs = []; acc = 0.0
for a, b, sp in PARTS: segs.append(dict(a=a, b=b, sp=sp, t0=acc, t1=acc + (b - a) / sp)); acc += (b - a) / sp
EDIT_END = acc; MUS_IN = EDIT_END - 9.6; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = MUS_IN; R.MUS_IN = MUS_IN; R.END_IN = END_IN; R.EDIT_END = EDIT_END
R.LYR = [(0.0, 1.43, "ESSE ANO"), (1.43, 2.87, "O LULA BOTA"), (2.87, 3.87, "O BOLSONARO"), (3.87, 4.87, "PRA MAMAR"),
         (4.87, 5.73, "VAI DAR PT"), (5.73, 6.73, "VAI DAR"), (6.73, 8.23, "VAI DAR PT"), (8.23, 9.43, "VAI DAR PT")]
R.CAPS = []; R._capcache.clear()
CARD = ("NOITE DE 25/10", ["A REAÇÃO DO", "OUTRO LADO"])
CW, CHh, CY0 = 800, 1422, 150
def src_t(t):
    for s in segs:
        if t < s["t1"]: return s["a"] + (t - s["t0"]) * s["sp"]
    return segs[-1]["b"] - 1e-3
_fr = {}
def clip(x):
    if not _fr:
        p = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{V}/in.mp4", "-vf", f"fps=30,scale={CW}:{CHh}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        n = len(p) // (CW * CHh * 3); _fr["a"] = np.frombuffer(p[:n * CW * CHh * 3], np.uint8).reshape(n, CHh, CW, 3)
    a = _fr["a"]; f = a[int(clamp(x * FPS, 0, len(a) - 1))].copy()
    y0, y1 = int(995 * CHh / 1280), int(1090 * CHh / 1280); band = f[y0:y1]          # legenda gravada desfocada
    f[y0:y1] = cv2.GaussianBlur(cv2.resize(cv2.resize(band, (CW // 24, max(1, band.shape[0] // 24))), (CW, band.shape[0])), (0, 0), 8)
    return cv2.LUT(f, R.LUT)
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); x = src_t(tt); img = clip(x)
    bg = cv2.resize(cv2.GaussianBlur(cv2.resize(img, (80, 142)), (0, 0), 3), (W, H)).astype(np.float32) * 0.3
    fr = Image.fromarray(bg.astype(np.uint8)).convert("RGBA")
    slow = tt >= segs[1]["t0"]; z = 1.0 + (0.10 * R.ease_io(clamp((tt - segs[1]["t0"]) / (segs[1]["t1"] - segs[1]["t0"]))) if slow else 0.02 * (0.5 - 0.5 * math.cos(2 * math.pi * tt / 6)))
    c = cv2.warpAffine(img, np.float32([[z, 0, CW / 2 * (1 - z)], [0, z, CHh * 0.4 * (1 - z)]]), (CW, CHh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    kin = eo(tt / 0.4); ci = Image.fromarray(R.rounded(c, 28, 3)); R.paste(fr, R.fade(ci, kin), CX - CW / 2, CY0 + 120 * (1 - kin), 0.6, 24, (10, 26))
    R.pill(fr, "A APURAÇÃO VISTA DO OUTRO LADO", CX, CY0 + 50, kin, fill=M.BLUE, size=30)
    if slow: R.pill(fr, "CÂMERA LENTA", CX + CW / 2 - 130, CY0 + 120, clamp((tt - segs[1]["t0"]) / 0.3), fill=R.NAVY, size=24)
    R.credit(fr, "Vídeo: redes sociais", CX - CW / 2 + 6, CY0 + 30 + CHh - 60, kin * (1 - clamp((tt - MUS_IN + 0.3) / 0.3)), anchor="lm")
    kc = clamp((tt - 0.4) / 0.4) * (1 - clamp((tt - (MUS_IN - 0.3)) / 0.3))
    if kc > 0: BAR.lower_card(fr, CARD[0], CARD[1], 1700, kc, fs=40)
    if tt >= MUS_IN - 0.1: R.lyrics(fr, tt)
    cta = clamp((t - (EDIT_END - 4)) / 0.4) if t > EDIT_END - 4 else 0.0
    BAR.draw_bar(fr, clamp(t / END_IN), "canal", eo((t - 0.2) / 0.6), cta, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(fr, t)
    if abs(t - segs[1]["t0"]) < 0.07: fr = Image.blend(fr, Image.new("RGBA", fr.size, (255, 255, 255, 255)), (1 - abs(t - segs[1]["t0"]) / 0.07) * 0.3)
    if t >= END_IN: fr.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return fr.convert("RGB")
def capa(out):
    img = clip(12.5); bg = cv2.resize(cv2.GaussianBlur(cv2.resize(img, (80, 142)), (0, 0), 3), (W, H)).astype(np.float32) * 0.3
    fr = Image.fromarray(bg.astype(np.uint8)).convert("RGBA")
    c = img[60:1090]; ci = Image.fromarray(R.rounded(c, 28, 3)); R.paste(fr, ci, CX - CW / 2, 560, 0.6, 24, (10, 26))
    d = ImageDraw.Draw(fr); y = 230
    for txt, sz, col in (("A REAÇÃO", 170, R.GOLD_L), ("DO OUTRO LADO", 110, (255, 255, 255))):
        f = R.BIGF(sz)
        while f.getlength(txt) > 880: sz -= 4; f = R.BIGF(sz)
        d.text((CX, y), txt, font=f, fill=col + (255,), anchor="mm", stroke_width=6, stroke_fill=R.NAVY + (255,)); y += int(sz * 1.05)
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
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{V}/in.mp4", "-ar", "48000", "-ac", "2", f"{V}/cl48.wav"], check=True)
    cl = R.readw(f"{V}/cl48.wav"); vt = np.zeros((n, 2), np.float32)
    s0 = segs[0]; c = cl[int(s0["a"] * SR):int(s0["b"] * SR)].copy(); vt[:len(c)] += c[:n]
    tl = np.arange(n) / SR; duck = np.clip(1 - (tl - (MUS_IN - 0.5)) / 0.8, 0.12, 1.0); vt *= duck[:, None]
    song = R.readw(f"{S}/v15/song_vox.wav"); o = int(MUS_IN * SR); Ls = min(len(song), n - o); ts = np.arange(Ls) / SR
    g = np.clip(ts / 0.3, 0, 1) * np.clip(1 - (ts - (TOTAL - MUS_IN - 1.6)) / 1.5, 0, 1); sg = np.zeros((n, 2), np.float32); sg[o:o + Ls] = song[:Ls] * g[:, None]
    R.writew(f"{V}/voice.wav", vt); R.writew(f"{V}/song.wav", sg)
    sfx.build([(0.0, sfx.whoosh(0.4), 0.2), (segs[1]["t0"] - 0.1, sfx.whoosh(0.45), 0.25), (END_IN - 0.3, sfx.whoosh(0.6), 0.22)], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    f"[1:a][2:a][3:a]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.8:level=false[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
