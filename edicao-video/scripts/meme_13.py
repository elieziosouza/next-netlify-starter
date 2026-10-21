"""Meme do número 13 (áudio do vídeo de referência) refeito no vídeo dele fotografando: texto amarelo condensado, contorno preto e sombra,
emoji colorido no fim, @ embaixo. Texto em baixo, sobre o corpo e o chão, para não cobrir o rosto."""
import sys
from PIL import Image, ImageDraw, ImageFont
S, OUT, HANDLE = sys.argv[1], sys.argv[2], sys.argv[3]; LINES = sys.argv[4].split("|")
W, H = 1080, 1920; YEL = (249, 238, 24)                      # mesmo amarelo do vídeo de referência
f = ImageFont.truetype(f"{S}/fontdl/Oswald-Bold.ttf", 92); fe = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)
img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
fs = 92
while max(d.textlength(l.replace("😂", "").replace(" ", " \u2009"), font=f) + (96 if "😂" in l else 0) for l in LINES) > 960:
    fs -= 2; f = ImageFont.truetype(f"{S}/fontdl/Oswald-Bold.ttf", fs)               # a linha mais longa cabe na largura
lh = int(fs * 1.22); y = int(sys.argv[5]) if len(sys.argv) > 5 else 980
for line in LINES:
    emo = line.endswith("😂"); txt = line.replace("😂", "").rstrip().replace(" ", " \u2009")   # espaço largo entre palavras, como no original
    tw = d.textlength(txt, font=f) + (96 if emo else 0); x = (W - tw) / 2
    d.text((x + 2, y + 3), txt, font=f, fill=(0, 0, 0, 90), stroke_width=4, stroke_fill=(0, 0, 0, 90))
    d.text((x, y), txt, font=f, fill=YEL + (255,), stroke_width=4, stroke_fill=(0, 0, 0, 255))
    if emo:
        tw -= 0
        e = Image.new("RGBA", (140, 140), (0, 0, 0, 0)); ImageDraw.Draw(e).text((0, 0), "😂", font=fe, embedded_color=True)
        e = e.resize((84, 84), Image.LANCZOS); img.alpha_composite(e, (int(x + tw - 84), int(y + 16)))
    y += lh
if HANDLE:
    fh = ImageFont.truetype(f"{S}/fontdl/Oswald-SemiBold.ttf", 54)
    HANDLE = HANDLE.upper(); hw = d.textlength(HANDLE, font=fh)                   # @ em branco e maiúsculo, como no original
    d.text(((W - hw) / 2 + 2, y + 93), HANDLE, font=fh, fill=(0, 0, 0, 90), stroke_width=3, stroke_fill=(0, 0, 0, 90))
    d.text(((W - hw) / 2, y + 90), HANDLE, font=fh, fill=(255, 255, 255, 255), stroke_width=3, stroke_fill=(0, 0, 0, 255))
img.save(OUT)
