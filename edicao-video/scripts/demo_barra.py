"""Demonstração animada da barra lateral: entra pela esquerda, o dourado desce como progresso e o cartão de manchete desliza."""
import sys, subprocess
import numpy as np
from PIL import Image
S = sys.argv[1]; sys.path.insert(0, f"{S}/work")
import barra_lateral as B
B.FD = f"{S}/fontdl"
from minitop import make_minitop
W, H, FPS, A, D = 1080, 1920, 30, 16.3, 5.0
p = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{S}/v29/me.mp4", "-ss", str(A), "-t", str(D), "-vf", "fps=30,scale=1080:1920", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
fr = np.frombuffer(p, np.uint8).reshape(-1, H, W, 3); top, _ = make_minitop(W, f"{B.FD}/Montserrat-SemiBold.ttf")
def eo(x): x = min(1, max(0, x)); return 1 - (1 - x) ** 3
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", "30", "-i", "-", "-ss", str(A), "-t", str(D), "-i", f"{S}/v29/me.mp4",
                        "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", f"{S}/v31/demo_barra_lateral.mp4"], stdin=subprocess.PIPE)
for i in range(len(fr)):
    t = i / FPS; f = Image.fromarray(fr[i]).convert("RGBA")
    B.draw_bar(f, t / D, "canal", eo(t / 0.6)); f.alpha_composite(top)
    B.lower_card(f, "ELEIÇÕES 2026", ["PESQUISA VOX BRASIL:", "LULA 51% x 49% FLÁVIO"], 1600, eo((t - 0.8) / 0.5))
    enc.stdin.write(f.convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); print("ok")
