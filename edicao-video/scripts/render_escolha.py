"""'Não é uma escolha difícil': ele no carro e, embaixo, menino de amarelo fazendo arminha x menina de vermelho erguendo um livro.
Os dois são crianças: rosto desfocado (posições marcadas à mão a cada 0,25 s e interpoladas). Cor do carro de dia (cor_fla), legenda minimalista
em Inter no peito dele (entre o rosto e os vídeos), sem zoom para não cortar os vídeos de baixo."""
import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
sys.path.insert(0, f"{S}/work")
import cor_fla, sfx
W, H, FPS, CX = R.W, R.H, R.FPS, R.CX; clamp = R.clamp; eo = R.ease_out
V = f"{S}/v62"; FD = f"{S}/fontdl"
def I(w, s): return ImageFont.truetype(f"{FD}/Inter-{w}.ttf", s)
BOY = [(0.25, 329, 1503), (0.5, 332, 1507), (0.75, 319, 1512), (1.0, 320, 1530), (1.25, 338, 1522), (1.5, 362, 1522), (1.75, 391, 1563), (2.0, 404, 1574),
       (2.25, 383, 1576), (2.5, 343, 1552), (2.75, 294, 1522), (3.0, 287, 1530), (3.25, 286, 1533), (3.5, 317, 1513), (3.75, 378, 1526), (4.0, 455, 1451),
       (4.25, 527, 1433), (4.5, 505, 1444), (4.75, 446, 1460), (5.0, 393, 1450), (5.25, 329, 1444), (5.5, 292, 1420), (5.75, 346, 1417), (6.0, 449, 1385),
       (6.25, 481, 1427), (6.5, 460, 1428), (6.75, 394, 1433), (7.0, 326, 1472), (7.25, 283, 1530), (7.5, 287, 1584), (7.75, 340, 1584)]
GIRL = [(0.25, 691, 1644), (0.75, 686, 1603), (1.25, 742, 1593), (1.75, 751, 1603), (2.25, 737, 1598), (2.75, 715, 1598), (3.25, 731, 1601), (3.75, 702, 1607),
        (4.25, 713, 1611), (4.75, 724, 1613), (5.25, 731, 1611), (5.75, 743, 1616), (6.25, 738, 1603), (6.75, 734, 1606), (7.25, 731, 1603), (7.75, 721, 1595)]
def at(track, t):
    ts = [p[0] for p in track]; return np.interp(t, ts, [p[1] for p in track]), np.interp(t, ts, [p[2] for p in track])
PANELS = {"boy": (270, 549, 74, 84), "girl": (553, 812, 50, 60)}  # x0, x1 do painel, raios do desfoque
def blur_faces(img, t):
    out = img.copy()
    for nm, tr in (("boy", BOY), ("girl", GIRL)):
        x0, x1, rx, ry = PANELS[nm]; cx, cy = at(tr, t); ya, yb = int(max(1290, cy - ry - 30)), int(min(H, cy + ry + 30))
        reg = out[ya:yb, x0:x1]; sm = cv2.resize(cv2.resize(reg, (max(1, reg.shape[1] // 14), max(1, reg.shape[0] // 14)), interpolation=cv2.INTER_AREA), (reg.shape[1], reg.shape[0]), interpolation=cv2.INTER_LINEAR)
        sm = cv2.GaussianBlur(sm, (0, 0), 6); m = np.zeros(reg.shape[:2], np.float32)
        cv2.ellipse(m, (int(cx - x0), int(cy - ya)), (rx, ry), 0, 0, 360, 1.0, -1); m = cv2.GaussianBlur(m, (0, 0), 6)[..., None]
        out[ya:yb, x0:x1] = (reg * (1 - m) + sm * m).astype(np.uint8)
    return out
_fr = {}
def src(t):
    if not _fr:
        p = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{V}/in.mp4", "-vf", "fps=30", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        n = len(p) // (W * H * 3); _fr["a"] = np.frombuffer(p[:n * W * H * 3], np.uint8).reshape(n, H, W, 3)
    a = _fr["a"]; return a[int(clamp(t * FPS, 0, len(a) - 1))]
D = 7.95; EDIT_END = D; END_IN = D + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = EDIT_END; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
CAPS = [(1.34, 2.95, [("Não", 1.34), ("é", 1.55), ("uma", 1.66), ("escolha", 1.92), ("difícil.", 2.35)]),
        (3.2, 4.75, [("Onde", 3.26), ("a", 3.5), ("gente", 3.6), ("se", 3.9), ("perdeu,", 4.0), ("hein?", 4.35)]),
        (5.66, 7.95, [("Não", 5.72), ("é", 5.92), ("uma", 6.03), ("escolha", 6.28), ("difícil.", 6.7)])]
HOTW = {"difícil.", "perdeu,"}
def caption(fr, t):
    for a, b, ws in CAPS:
        if not (a - 0.05 <= t < b): continue
        ko = 1 - clamp((t - (b - 0.15)) / 0.15); f1 = I(600, 62); f2 = I(800, 62); sp = f1.getlength(" ")
        ff = lambda w: f2 if w in HOTW else f1; tot = sum(ff(w).getlength(w) for w, _ in ws) + sp * (len(ws) - 1); x = CX - tot / 2
        lay = Image.new("RGBA", fr.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        for w, t0 in ws:
            al = clamp((t - t0 + 0.06) / 0.14) * ko; col = (255, 214, 92) if w in HOTW else (245, 246, 248)
            d.text((x + 3, 1196 + 10 * (1 - al) + 3), w, font=ff(w), fill=(0, 0, 0, int(140 * al)), anchor="lm")
            d.text((x, 1196 + 10 * (1 - al)), w, font=ff(w), fill=col + (int(255 * al),), anchor="lm"); x += ff(w).getlength(w) + sp
        fr.alpha_composite(lay)
def frame_at(t):
    tt = min(t, D - 1 / FPS); img = blur_faces(cor_fla.fix(src(tt)), tt); fr = Image.fromarray(img).convert("RGBA")
    g = np.zeros((300, W, 4), np.uint8); g[..., 3] = (np.sin(np.linspace(0, np.pi, 300)) * 120).astype(np.uint8)[:, None]; fr.alpha_composite(Image.fromarray(g), (0, 1050))
    caption(fr, tt)
    R.BAR.draw_bar(fr, clamp(t / END_IN), "canal", eo((t - 0.2) / 0.6), clamp((t - 5.6) / 0.4) if t > 5.6 else 0.0, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(fr, t)
    if t >= END_IN: fr.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return fr.convert("RGB")
def capa(out):
    img = blur_faces(cor_fla.fix(src(4.2)), 4.2); sh = 200
    base = np.zeros_like(img); base[sh:] = img[:H - sh]; base[:sh] = cv2.GaussianBlur(cv2.resize(img[:60], (W, sh)), (0, 0), 12)
    fr = Image.fromarray(base).convert("RGBA")
    g = np.zeros((560, W, 4), np.uint8); g[..., 3] = np.linspace(235, 0, 560).astype(np.uint8)[:, None]; fr.alpha_composite(Image.fromarray(g), (0, 0))
    d = ImageDraw.Draw(fr)
    d.text((CX, 235), "Não é uma", font=I(300, 92), fill=(245, 246, 248), anchor="mm")
    d.text((CX, 340), "escolha difícil.", font=I(800, 96), fill=(255, 214, 92), anchor="mm")
    R.BAR.draw_bar(fr, 0.0, "canal"); fr.alpha_composite(R.top, (R.HDX, 0)); fr.convert("RGB").save(out, quality=95)
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
    sfx.build([(END_IN - 0.3, sfx.whoosh(0.6), 0.25)], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/in.mp4", "-i", f"{V}/sfx.wav", "-filter_complex",
                    f"[1:a]apad,atrim=0:{TOTAL:.2f},afade=t=out:st={D - 0.2:.2f}:d=0.25[v];[v][2:a]amix=inputs=2:normalize=0:duration=longest,atrim=0:{TOTAL:.2f}[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
