"""Duas opções de capa para o vídeo 1 (Vale a pena comprar na planta?), com a foto recortada do Eliezio.
Uso: python3 capas_planta.py pasta_saida"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
KIT = Path(__file__).resolve().parent.parent; FD = KIT / "assets" / "fonts"; OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
W, H = 1080, 1920; BG = (243, 239, 231); INK = (22, 24, 27); GREEN = (24, 150, 84)
F = lambda n, s: ImageFont.truetype(str(FD / f"{n}.ttf"), s)
FOTO = Image.open(KIT / "assets" / "corretor" / "eliezio_recorte.png").convert("RGBA")

def text_center(d, y, txt, font, fill):
    b = d.textbbox((0, 0), txt, font=font); d.text(((W - (b[2] - b[0])) / 2 - b[0], y - b[1]), txt, font=font, fill=fill)

def foto(c, scale, top):
    f = FOTO.resize((int(FOTO.width * scale), int(FOTO.height * scale)), Image.LANCZOS); x = (W - f.width) // 2
    sh = Image.new("RGBA", f.size, (0, 0, 0, 255)); sh.putalpha(f.getchannel("A").point(lambda v: int(v * 0.35)))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22)), (x + 16, top + 12)); c.alpha_composite(f, (x, top))
    return f, x

def plan(c, ox, oy, sc, col):
    lay = Image.new("RGBA", c.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    walls = [((0, 0), (100, 0)), ((100, 0), (100, 80)), ((100, 80), (0, 80)), ((0, 80), (0, 0)), ((42, 0), (42, 34)), ((42, 46), (42, 80)),
             ((0, 46), (30, 46)), ((36, 46), (42, 46)), ((42, 40), (72, 40)), ((80, 40), (100, 40)), ((72, 0), (72, 26)), ((72, 34), (72, 40))]
    for a, b in walls: d.line([(ox + a[0] * sc, oy + a[1] * sc), (ox + b[0] * sc, oy + b[1] * sc)], fill=col, width=6)
    c.alpha_composite(lay)

# A: fundo claro, palavra "planta" gigante atrás da cabeça
c = Image.new("RGBA", (W, H), BG + (255,)); d = ImageDraw.Draw(c)
plan(c, 90, 300, 9.0, (22, 24, 27, 40)); d = ImageDraw.Draw(c)
text_center(d, 330, "vale a pena comprar na", F("Montserrat-SemiBold", 46), INK)
text_center(d, 430, "planta", F("DMSerifDisplay-Regular", 330), INK)
f, x = foto(c, 1.4, 540)
# a cabeça passa na frente da palavra: o recorte já foi colado por cima
d = ImageDraw.Draw(c)
for i, (txt, col) in enumerate([("BOM NEGÓCIO", GREEN), ("OU CILADA?", (255, 255, 255))]):
    fnt = F("Montserrat-ExtraBoldItalic", 112); b = d.textbbox((0, 0), txt, font=fnt); y = 1500 + i * 135
    d.rounded_rectangle([(W - b[2]) / 2 - 30, y - 10, (W + b[2]) / 2 + 30, y + b[3] + 12], 18, fill=(255, 255, 255) if i == 0 else INK)
    text_center(d, y, txt, fnt, col)
c.convert("RGB").save(OUT / "capa_A.jpg", quality=92)

# B: fundo escuro, título em cima e ele embaixo
c = Image.new("RGBA", (W, H), (16, 18, 20, 255)); d = ImageDraw.Draw(c)
plan(c, 90, 900, 9.0, (255, 255, 255, 22)); d = ImageDraw.Draw(c)
text_center(d, 170, "IMÓVEL NA PLANTA EM SP", F("Montserrat-Bold", 40), GREEN)
text_center(d, 250, "Vale a", F("DMSerifDisplay-Regular", 210), (255, 255, 255))
text_center(d, 470, "pena?", F("DMSerifDisplay-Regular", 210), (255, 255, 255))
text_center(d, 735, "3 COISAS ANTES DE COMPRAR", F("Montserrat-ExtraBoldItalic", 62), GREEN)
foto(c, 1.05, 880)
c.convert("RGB").save(OUT / "capa_B.jpg", quality=92)
