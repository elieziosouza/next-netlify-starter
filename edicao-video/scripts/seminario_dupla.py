"""Edição da apresentação em dupla (23/11/2026): borda preta cortada, color grading de ambiente escolar, áudio tratado.
Vertical 1080x1920: quadrado 1:1 sobre fundo desfocado, empurrões de zoom suaves e 3 planos fechados; título animado, crédito e confete nos aplausos.
Uso: python3 montar_dupla.py SAIDA.mp4"""
import sys, os, subprocess, importlib.util, wave, math
import numpy as np, cv2
os.environ["MODO"] = "limpo"
spec = importlib.util.spec_from_file_location("M", "/home/user/next-netlify-starter/edicao-video/scripts/seminario_viral_8b.py"); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
from PIL import Image
W, H, FPS = 1080, 1920, 30
SRC = "orig/apresentacao.mp4"; DUR = 92.0
BORDA = "crop=1804:1012:58:34"
GRADE = ("colorchannelmixer=rr=1.20:gg=1.20:bb=1.26,curves=all='0/0 0.22/0.18 0.5/0.52 0.78/0.83 1/1',eq=saturation=1.14:contrast=1.04,"
         "colorbalance=rm=0.03:gm=0.005:bm=-0.02,hqdn3d=2.5:2:4:3,unsharp=5:5:0.5:5:5:0.0")
SQ = 1012                      # lado do quadrado (altura útil)
CX_PAR = 892                   # centro da dupla, em coordenadas da imagem sem borda
# plano: (ini, dur, modo, zoom_ini, zoom_fim)   modo: "sq" quadrado · "pt" retrato (dupla)
PLANOS = [(0.0, 14.0, "sq", 1.0, 1.06), (14.0, 6.0, "pt", 1.0, 1.05), (20.0, 24.0, "sq", 1.14, 1.0), (44.0, 6.0, "pt", 1.05, 1.0), (50.0, 24.0, "sq", 1.0, 1.1),
          (74.0, 6.0, "pt", 1.0, 1.05), (80.0, 12.0, "sq", 1.0, 1.12)]
CORTES = [14.0, 20.0, 44.0, 50.0, 74.0, 80.0]
TOTAL = DUR
M.TOTAL = TOTAL

def ease(x): x = min(1, max(0, x)); return x * x * (3 - 2 * x)

def frames(ini, dur, modo):
    if modo == "sq":
        x0 = min(max(CX_PAR - SQ // 2, 0), 1804 - SQ); vf = f"{BORDA},{GRADE},crop={SQ}:{SQ}:{x0}:0"; w, h = SQ, SQ
    else:
        w, h = 570, SQ; x0 = min(max(CX_PAR - w // 2, 0), 1804 - w); vf = f"{BORDA},{GRADE},crop={w}:{h}:{x0}:0"
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{ini:.3f}", "-t", f"{dur:.3f}", "-i", SRC, "-an", "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, bufsize=w * h * 3 * 4)
    n = int(round(dur * FPS)); k = 0; last = None
    while k < n:
        b = p.stdout.read(w * h * 3)
        if len(b) < w * h * 3: break
        last = np.frombuffer(b, np.uint8).reshape(h, w, 3); k += 1; yield last
    while k < n and last is not None: k += 1; yield last
    p.stdout.close(); p.wait()

def compor(fr, modo, z):
    h, w = fr.shape[:2]
    cw, ch = int(w / z), int(h / z); yy = int((h - ch) * 0.35); xx = (w - cw) // 2
    rec = fr[yy:yy + ch, xx:xx + cw]
    if modo == "sq":
        fg = cv2.resize(rec, (W, W), interpolation=cv2.INTER_CUBIC if z > 1.01 else cv2.INTER_AREA).astype(np.float32)
        bgsm = cv2.resize(rec, (W // 12, H // 12), interpolation=cv2.INTER_AREA); bgsm = cv2.GaussianBlur(bgsm, (0, 0), 3)
        bg = cv2.resize(bgsm, (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32); gray = bg.mean(2, keepdims=True); bg = (gray + (bg - gray) * 1.25) * 0.55
        vig = 1 - 0.35 * (np.linspace(-1, 1, H)[:, None, None] ** 2); canvas = bg * vig; y0 = (H - W) // 2 - 60; canvas[y0:y0 + W] = fg
        return canvas
    out = cv2.resize(rec, (W, H), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    # um toque de nitidez para compensar a ampliação e um grão leve
    blur = cv2.GaussianBlur(out, (0, 0), 2.0); out = np.clip(out + 0.5 * (out - blur), 0, 255)
    return out

def audio():
    w = wave.open("a48_tratado.wav"); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, 2) / 32768
    return a[:int(TOTAL * 48000)]

def motion(frame, t):
    M.titulo_cinetico(frame, t, 0.15, 2.7, [("ENGLISH", (255, 214, 64)), ("SEMINAR", (255, 255, 255))], 300)
    M.barra_credito(frame, t, 6.2, 9.4, y=1260)
    M.barra_credito(frame, t, TOTAL - 4.2, TOTAL - 0.3, y=1260)
    M.confete(frame, t, 84.0, dur=2.6)
    return frame

def main():
    out = sys.argv[1]
    M.OV.clear()
    M.OV.append((3.0, TOTAL, M.pill("ENGLISH SEMINAR", 32), 205, "fade"))
    M.OV.append((3.0, 6.0, M.pill("Apresentação em dupla", 44), 1340, "pop"))
    M.OV.append((68.0, 71.5, M.pill("A sala riu", 44), 1340, "pop"))
    M.OV.append((83.6, 88.0, M.texto("E A SALA APLAUDIU", M.ANTON(112), M.GOLD, maxw=1000), 330, "pop"))
    au = audio(); sr = 48000
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for ini, dur, modo, z0, z1 in PLANOS:
        for i, fr in enumerate(frames(ini, dur, modo)):
            t = ini + i / FPS; u = ease(i / max(1, int(dur * FPS) - 1)); z = z0 + (z1 - z0) * u
            frame = compor(fr, modo, z)
            frame = M.punch(frame, t, CORTES, dur=0.22, z=0.04); M.flash(frame, t, CORTES, dur=0.10, forca=0.35)
            M.overlays(frame, t); frame = motion(frame, t)
            enc.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())
    enc.stdin.close(); enc.wait(); print("ok")
if __name__ == "__main__": main()
