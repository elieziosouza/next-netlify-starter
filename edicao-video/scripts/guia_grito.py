"""Vídeo-guia (karaokê) para o Eliezio gravar o grito em cima do batidão."""
import sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
S = sys.argv[1]; FD = f"{S}/fontdl"; OUT = f"{S}/musica"
W, H, FPS = 1080, 1920, 30; BAR = 60 / 130 * 4
GOLD = (214, 182, 116); RED = (200, 38, 38); NAVY = (4, 14, 26)
def MF(w, s): return ImageFont.truetype(f"{FD}/Montserrat-{w}.ttf", s)
# (compasso inicial, duração em compassos, texto) — 2 compassos de introdução, letra 2 vezes
LINES = []
for rep in range(2):
    b = 2 + rep * 4
    LINES += [(b, 1, "DIA 25 ESTÁ CHEGANDO"), (b + 1, 1, "O POVO VAI DECIDIR"), (b + 2, 1, "VAI DAR PT"), (b + 3, 1, "VAI DAR PT")]
TOTAL = 10 * BAR + 0.5
fn = MF("ExtraBold", 92); fs = MF("SemiBold", 34)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-i", f"{OUT}/batidao_pt.wav", "-t", f"{TOTAL:.2f}", "-c:v", "libx264", "-crf", "23", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", f"{OUT}/guia_grito.mp4"], stdin=subprocess.PIPE)
for i in range(int(TOTAL * FPS)):
    t = i / FPS; img = Image.new("RGB", (W, H), NAVY); d = ImageDraw.Draw(img)
    beat = int(t / (BAR / 4)); ph = (t % (BAR / 4)) / (BAR / 4)
    for k in range(4):
        r = 22 + (16 * (1 - ph) if k == beat % 4 else 0)
        d.ellipse((W / 2 - 150 + k * 100 - r, 1500 - r, W / 2 - 150 + k * 100 + r, 1500 + r), fill=GOLD if k == beat % 4 else (60, 70, 90))
    cur = [l for l in LINES if l[0] * BAR <= t < (l[0] + l[1]) * BAR]
    nxt = [l for l in LINES if l[0] * BAR > t][:1]
    if t < 2 * BAR:
        d.text((W / 2, 700), "PREPARA…", font=fn, fill=(255, 255, 255), anchor="mm")
        d.text((W / 2, 820), f"entra em {int(2 * BAR - t) + 1}", font=fs, fill=GOLD, anchor="mm")
    for _, _, txt in cur:
        if txt.endswith("PT"):
            pre = txt[:-2]; wp = d.textlength(pre, font=fn); wt = d.textlength("PT", font=fn); x0 = W / 2 - (wp + wt + 30) / 2
            d.text((x0, 760), pre, font=fn, fill=(255, 255, 255), anchor="lm")
            d.rounded_rectangle((x0 + wp + 2, 700, x0 + wp + wt + 34, 822), 16, fill=RED); d.text((x0 + wp + 18, 760), "PT", font=fn, fill=(255, 255, 255), anchor="lm")
        else:
            d.text((W / 2, 760), txt, font=fn, fill=(255, 255, 255), anchor="mm")
    for _, _, txt in nxt: d.text((W / 2, 930), "próximo: " + txt.lower(), font=fs, fill=(150, 160, 180), anchor="mm")
    d.text((W / 2, 260), "GUIA DO GRITO", font=MF("Bold", 40), fill=GOLD, anchor="mm")
    d.text((W / 2, 320), "use fone de ouvido e grite junto", font=fs, fill=(200, 205, 215), anchor="mm")
    enc.stdin.write(img.tobytes())
enc.stdin.close(); enc.wait()
