"""Capa do meme do 13: quadro dele fotografando com a tela da câmera por cima (foco nele, f/13 · 1/13 · ISO 13) e o texto amarelo do meme."""
import sys, io, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S, SRC, OUT, T = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4])
W, H = 1080, 1920; YEL = (249, 238, 24); OSB = f"{S}/fontdl/Oswald-Bold.ttf"
p = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(T), "-i", SRC, "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
fr = np.asarray(Image.open(io.BytesIO(p)).convert("RGB")); h0, w0 = fr.shape[:2]
z = 1.35; cxs, cys = 0.60 * w0, 0.52 * h0                                       # aproxima nele
cw, ch = w0 / z, h0 / z; x0 = int(np.clip(cxs - cw / 2, 0, w0 - cw)); y0 = int(np.clip(cys - ch / 2, 0, h0 - ch))
crop = fr[y0:y0 + int(ch), x0:x0 + int(cw)]
big = cv2.resize(crop, (W, H), interpolation=cv2.INTER_LANCZOS4)
big = cv2.addWeighted(big, 1.5, cv2.GaussianBlur(big, (0, 0), 3), -0.5, 0)
img = Image.fromarray(big).convert("RGBA")
sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
for i in range(520): ds.line((0, i, W, i), fill=(0, 0, 0, int(170 * (1 - i / 520))))
for i in range(380): ds.line((0, H - i, W, H - i), fill=(0, 0, 0, int(190 * (1 - i / 380))))
img.alpha_composite(sh); d = ImageDraw.Draw(img)
# visor da câmera: cantos, ponto de foco nele e a barra de ajustes
m, L = 70, 90
for (ax, ay, sx, sy) in ((m, 560, 1, 1), (W - m, 560, -1, 1), (m, H - 470, 1, -1), (W - m, H - 470, -1, -1)):
    d.line((ax, ay, ax + sx * L, ay), fill=(255, 255, 255, 230), width=7); d.line((ax, ay, ax, ay + sy * L), fill=(255, 255, 255, 230), width=7)
fx, fy = int(sys.argv[5]) if len(sys.argv) > 5 else 300, int(sys.argv[6]) if len(sys.argv) > 6 else 660      # foco na cabeça dele
d.rectangle((fx - 70, fy - 70, fx + 70, fy + 70), outline=(60, 230, 90, 255), width=6)
d.ellipse((W - m - 60, 600, W - m - 30, 630), fill=(235, 40, 40, 255))
fm = ImageFont.truetype(OSB, 64); bar_y = H - 400
d.rounded_rectangle((m, bar_y, W - m, bar_y + 110), 18, fill=(0, 0, 0, 175))
items = ["f/13", "1/13", "ISO 13"]; seg = (W - 2 * m) / 3
for i, it in enumerate(items):
    d.text((m + seg * i + seg / 2, bar_y + 55), it, font=fm, fill=YEL + (255,), anchor="mm")
# texto do meme, mesmo estilo (amarelo condensado, contorno preto)
def line(txt, y, size, col=YEL, emo=False):
    f = ImageFont.truetype(OSB, size); t = txt.replace(" ", "  ")
    tw = d.textlength(t, font=f) + (size + 10 if emo else 0); x = (W - tw) / 2
    d.text((x + 3, y + 5), t, font=f, fill=(0, 0, 0, 110), stroke_width=6, stroke_fill=(0, 0, 0, 110))
    d.text((x, y), t, font=f, fill=col + (255,), stroke_width=6, stroke_fill=(0, 0, 0, 255))
    if emo:
        fe = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
        e = Image.new("RGBA", (140, 140), (0, 0, 0, 0)); ImageDraw.Draw(e).text((0, 0), "😂", font=fe, embedded_color=True)
        e = e.resize((int(size * 0.95), int(size * 0.95)), Image.LANCZOS); img.alpha_composite(e, (int(x + tw - size * 0.95), int(y + size * 0.28)))
line("A ANSIEDADE TÁ TÃO GRANDE", 120, 78, (255, 255, 255))
line("ATÉ A CÂMERA", 215, 150)
line("TÁ NO 13", 375, 150, emo=True)
fh = ImageFont.truetype(f"{S}/fontdl/Oswald-SemiBold.ttf", 50); hn = "@ELIEZIO.SOUZA78"
d.text(((W - d.textlength(hn, font=fh)) / 2, H - 240), hn, font=fh, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 255))
img.convert("RGB").save(OUT, quality=95)
