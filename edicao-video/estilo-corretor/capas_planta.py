"""Duas opções de capa para o vídeo 1 (Vale a pena comprar na planta?), com o Eliezio em círculo no canto inferior esquerdo.
Uso: python3 capas_planta.py pasta_saida"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
KIT = Path(__file__).resolve().parent.parent; FD = KIT / "assets" / "fonts"; OUT = Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
W, H = 1080, 1920; BG = (243, 239, 231); INK = (22, 24, 27); GREEN = (24, 150, 84); WHITE = (255, 255, 255)
F = lambda n, s: ImageFont.truetype(str(FD / f"{n}.ttf"), s)

def text_center(d, y, txt, font, fill):
    b = d.textbbox((0, 0), txt, font=font); d.text(((W - (b[2] - b[0])) / 2 - b[0], y - b[1]), txt, font=font, fill=fill)

def plan(c, ox, oy, sc, col):
    lay = Image.new("RGBA", c.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    walls = [((0, 0), (100, 0)), ((100, 0), (100, 80)), ((100, 80), (0, 80)), ((0, 80), (0, 0)), ((42, 0), (42, 34)), ((42, 46), (42, 80)),
             ((0, 46), (30, 46)), ((36, 46), (42, 46)), ((42, 40), (72, 40)), ((80, 40), (100, 40)), ((72, 0), (72, 26)), ((72, 34), (72, 40))]
    for a, b in walls: d.line([(ox + a[0] * sc, oy + a[1] * sc), (ox + b[0] * sc, oy + b[1] * sc)], fill=col, width=6)
    c.alpha_composite(lay)

def circulo(c, cx, cy, dia, ring_col):
    """Eliezio em círculo, com o fundo original da foto, aro verde, aro branco e anel tracejado"""
    n = dia * 4
    ph = Image.open(KIT / "assets" / "corretor" / "eliezio_foto.jpg").convert("RGB").crop((175, 60, 775, 660)).resize((dia, dia), Image.LANCZOS).convert("RGBA")
    m = Image.new("L", (n, n), 0); ImageDraw.Draw(m).ellipse([0, 0, n - 1, n - 1], fill=255); ph.putalpha(m.resize((dia, dia), Image.LANCZOS))
    S = dia + 160; o = S / 2; R = dia / 2; lay = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sh = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([o - R, o - R + 14, o + R, o + R + 14], fill=(0, 0, 0, 110))
    lay.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    g = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse([o - R - 22, o - R - 22, o + R + 22, o + R + 22], fill=GREEN + (90,))
    lay.alpha_composite(g.filter(ImageFilter.GaussianBlur(12)))
    d = ImageDraw.Draw(lay); rr = R + 28
    for k in range(24): d.arc([o - rr, o - rr, o + rr, o + rr], 10 + k * 15, 17 + k * 15, fill=ring_col, width=3)
    d.ellipse([o - R - 13, o - R - 13, o + R + 13, o + R + 13], outline=GREEN + (255,), width=6)
    d.ellipse([o - R - 5, o - R - 5, o + R + 5, o + R + 5], fill=WHITE + (255,))
    lay.alpha_composite(ph, (int(o - R), int(o - R))); c.alpha_composite(lay, (int(cx - o), int(cy - o)))

def etiqueta(d, x, y, cor_nome, cor_sub):
    d.text((x, y), "Corretor Eliezio", font=F("Montserrat-Bold", 46), fill=cor_nome)
    d.text((x, y + 62), "CRECI-SP 209.709", font=F("Montserrat-SemiBold", 30), fill=cor_sub)
    d.text((x, y + 108), "@eliezio.corretordeimoveis", font=F("Montserrat-SemiBold", 30), fill=GREEN)

def pilulas(d, y0, bg2=INK):
    for i, (txt, col, bg) in enumerate([("BOM NEGÓCIO", GREEN, WHITE), ("OU CILADA?", WHITE, bg2)]):
        fnt = F("Montserrat-ExtraBoldItalic", 112); b = d.textbbox((0, 0), txt, font=fnt); y = y0 + i * 150
        d.rounded_rectangle([(W - b[2]) / 2 - 34, y - 12, (W + b[2]) / 2 + 34, y + b[3] + 14], 20, fill=bg)
        text_center(d, y, txt, fnt, col)

# A: fundo claro editorial
c = Image.new("RGBA", (W, H), BG + (255,))
plan(c, 90, 300, 9.0, INK + (38,)); d = ImageDraw.Draw(c)
text_center(d, 150, "IMÓVEL NA PLANTA · SÃO PAULO", F("Montserrat-SemiBold", 30), INK + (150,))
d.line([(W / 2 - 300, 205), (W / 2 + 300, 205)], fill=(22, 24, 27), width=2)
text_center(d, 330, "vale a pena comprar na", F("Montserrat-SemiBold", 48), INK)
text_center(d, 430, "planta", F("DMSerifDisplay-Regular", 330), INK)
pilulas(d, 1060)
circulo(c, 250, 1650, 300, INK + (110,)); d = ImageDraw.Draw(c)
etiqueta(d, 450, 1580, INK, (110, 110, 110))
c.convert("RGB").save(OUT / "capa_A.jpg", quality=92)

# B: fundo escuro
c = Image.new("RGBA", (W, H), (16, 18, 20, 255))
plan(c, 90, 880, 9.0, WHITE + (20,)); d = ImageDraw.Draw(c)
text_center(d, 170, "IMÓVEL NA PLANTA EM SP", F("Montserrat-Bold", 40), GREEN)
text_center(d, 250, "Vale a", F("DMSerifDisplay-Regular", 210), WHITE)
text_center(d, 470, "pena?", F("DMSerifDisplay-Regular", 210), WHITE)
text_center(d, 735, "3 COISAS ANTES DE COMPRAR", F("Montserrat-ExtraBoldItalic", 62), GREEN)
pilulas(d, 1020, GREEN)
circulo(c, 250, 1650, 300, WHITE + (90,)); d = ImageDraw.Draw(c)
etiqueta(d, 450, 1580, WHITE, (170, 170, 170))
c.convert("RGB").save(OUT / "capa_B.jpg", quality=92)
