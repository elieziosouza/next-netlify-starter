"""Noite de 25/10: Lula abraçado e o coro "Olê... povo brasileiro... guerreiro do povo brasileiro". Vídeo de terceiros (WhatsApp) num card
grande sobre fundo desfocado, legenda karaokê do coro, caixa fixa embaixo, áudio original. Sem afirmar resultado na tela até confirmação.
Usa os ajudantes do render_exercito."""
import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
TITLE = os.environ.get("TITULO", "")
spec = importlib.util.spec_from_file_location("rex", f"{S}/work/render_exercito.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; eo = R.ease_out
V = f"{S}/v68"; A, B = 0.30, 7.20
EDIT_END = B - A; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = EDIT_END; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
CAPW = [("OLÊ!", 0.63, 1.40), ("POVO BRASILEIRO!", 1.78, 3.20), ("GUERREIRO DO POVO BRASILEIRO!", 4.25, 6.90)]
HOT = {"GUERREIRO", "BRASILEIRO!"}
CAPS = []
for txt, a, b in CAPW:
    a2, b2 = a - A, b - A; ws = txt.split(); tot = sum(len(w) + 2 for w in ws); k = 0; ts = []
    for w in ws: ts.append(a2 + (b2 - a2 - 0.08) * k / tot); k += len(w) + 2
    CAPS.append(dict(words=ws, ts=ts, start=a2, end=b2, src="au" if any(w in HOT for w in ws) else "me"))
R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
CARD = ("NOITE DE 25/10", ["O CORO PARA O LULA:", "GUERREIRO DO POVO"])
CW, CHh, CY0 = 800, 1413, 170
_fr = {}
def src(x):
    if not _fr:
        p = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{V}/in.mp4", "-vf", f"fps=30,scale={CW}:{CHh}:flags=lanczos", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        n = len(p) // (CW * CHh * 3); _fr["a"] = np.frombuffer(p[:n * CW * CHh * 3], np.uint8).reshape(n, CHh, CW, 3)
    a = _fr["a"]; return cv2.LUT(a[int(clamp(x * FPS, 0, len(a) - 1))], R.LUT)
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); x = A + tt; img = src(x)
    bg = cv2.resize(cv2.GaussianBlur(cv2.resize(img, (80, 141)), (0, 0), 3), (W, H)).astype(np.float32) * 0.32
    fr = Image.fromarray(bg.astype(np.uint8)).convert("RGBA")
    z = 1.0 + 0.04 * (0.5 - 0.5 * math.cos(2 * math.pi * tt / 7.0))
    c = cv2.warpAffine(img, np.float32([[z, 0, CW / 2 * (1 - z)], [0, z, CHh * 0.4 * (1 - z)]]), (CW, CHh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    kin = eo(tt / 0.4); ci = Image.fromarray(R.rounded(c, 28, 3)); R.paste(fr, R.fade(ci, kin), CX - CW / 2, CY0 + 120 * (1 - kin), 0.6, 24, (10, 26))
    g = np.zeros((420, W, 4), np.uint8); g[..., :3] = (4, 14, 28); g[..., 3] = np.linspace(0, 190, 420)[:, None].astype(np.uint8); fr.alpha_composite(Image.fromarray(g), (0, CY0 + CHh - 420))
    M.caption(fr, tt, 1400, 54)
    R.credit(fr, "Vídeo: redes sociais", CX - CW / 2 + 6, CY0 + CHh + 22, kin, anchor="lm")
    kc = clamp((tt - 0.4) / 0.4); BAR.lower_card(fr, CARD[0], CARD[1], 1700, kc, fs=40)
    cta = clamp((t - (EDIT_END - 2.5)) / 0.4) if t > EDIT_END - 2.5 else 0.0
    BAR.draw_bar(fr, clamp(t / END_IN), "canal", eo((t - 0.2) / 0.6), cta, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(fr, t)
    if t >= END_IN: fr.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return fr.convert("RGB")
def capa(out):
    img = src(4.6); bg = cv2.resize(cv2.GaussianBlur(cv2.resize(img, (80, 141)), (0, 0), 3), (W, H)).astype(np.float32) * 0.32
    fr = Image.fromarray(bg.astype(np.uint8)).convert("RGBA")
    c = img[180:1300]; ci = Image.fromarray(R.rounded(c, 28, 3)); R.paste(fr, ci, CX - CW / 2, 560, 0.6, 24, (10, 26))
    d0 = ImageDraw.Draw(fr)
    d = ImageDraw.Draw(fr)
    lines = [("LULA 51,69%", 170, R.GOLD_L), ("GUERREIRO DO POVO BRASILEIRO", 80, (255, 255, 255))] if not TITLE else [(TITLE, 170, R.GOLD_L), ("GUERREIRO DO POVO BRASILEIRO", 80, (255, 255, 255))]
    R.pill(fr, "COM 93,82% DAS URNAS APURADAS · TSE", CX, 500, 1.0, fill=(14, 62, 120), size=32)
    y = 215
    for txt, sz, col in lines:
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
    sfx.build([(0.0, sfx.whoosh(0.4), 0.2), (END_IN - 0.3, sfx.whoosh(0.6), 0.22)], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-ss", f"{A}", "-i", f"{V}/in.mp4", "-i", f"{V}/sfx.wav", "-filter_complex",
                    f"[1:a]aresample=48000,apad,atrim=0:{TOTAL:.2f},afade=t=out:st={EDIT_END - 0.3:.2f}:d=0.4[v];[v][2:a]amix=inputs=2:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.8:level=false[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
