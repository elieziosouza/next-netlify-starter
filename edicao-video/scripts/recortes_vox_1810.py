"""Recortes de jornal da pesquisa Vox Brasil de 18/10/2026 (manchetes refeitas, sem logotipo, fonte escrita embaixo)."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
S = sys.argv[1]; FD = f"{S}/fontdl"; OUT = f"{S}/v30"
RED = (210, 30, 36)
def MF(w, s): return ImageFont.truetype(f"{FD}/Montserrat-{w}.ttf", s)
def SERIF(s): return ImageFont.truetype(f"{FD}/DMSerifDisplay-Regular.ttf", s)
def wrap(text, font, maxw):
    d = ImageDraw.Draw(Image.new("RGB", (4, 4))); lines = [""]
    for w in text.split():
        tst = (lines[-1] + " " + w).strip()
        if d.textlength(tst, font=font) <= maxw: lines[-1] = tst
        else: lines.append(w)
    return lines
def clipping(kicker, headline, source, w=900, seed=1):
    rng = np.random.default_rng(seed); f = SERIF(64); fk = MF("ExtraBold", 26); fs = MF("SemiBold", 22)
    lines = wrap(headline, f, w - 90); h = 70 + 46 + len(lines) * 74 + 70
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    top = [(x, int(rng.integers(0, 12))) for x in range(0, w + 1, 18)]; bot = [(x, h - 1 - int(rng.integers(0, 12))) for x in range(w, -1, -18)]
    d.polygon(top + [(w, h)] + bot + [(0, h)], fill=(244, 240, 229, 255))
    a = np.asarray(im).astype(np.int16); a[..., :3] = np.clip(a[..., :3] + rng.normal(0, 5, (h, w)).astype(np.int16)[..., None], 0, 255)
    im = Image.fromarray(a.astype(np.uint8), "RGBA"); d = ImageDraw.Draw(im)
    d.text((45, 56), kicker, font=fk, fill=RED + (255,), anchor="lm"); d.rectangle((45, 80, w - 45, 82), fill=(30, 30, 34, 200))
    y = 104
    for ln in lines: d.text((45, y), ln, font=f, fill=(20, 20, 24, 255)); y += 74
    d.text((45, h - 42), source, font=fs, fill=(90, 90, 96, 255), anchor="lm")
    return im
RECS = [
    ("PESQUISA VOX BRASIL · 18/10", "Lula tem 46,4% e Flávio Bolsonaro, 44,6%, no 2º turno", "Fonte: Metrópoles e Poder360"),
    ("VOTOS VÁLIDOS", "Lula 51% x 49% Flávio", "Fonte: Poder360 e Gazeta do Paraná"),
    ("EM UMA SEMANA", "Lula foi de 44,2% para 46,4%; a diferença passou de 1,5 para 1,8 ponto", "Fonte: Exame (5 a 7/10) e Metrópoles (15 a 17/10)"),
    ("REJEIÇÃO EMPATADA", "45,3% não votariam em Lula de jeito nenhum; 45,3% não votariam em Flávio", "Fonte: Poder360"),
    ("COMO FOI FEITA", "2.100 entrevistas de 15 a 17/10, margem de 2,15 pontos, registro BR-04332/2026", "Fonte: Metrópoles e Poder360"),
]
ims = []
for i, (k, hl, src) in enumerate(RECS, 1):
    im = clipping(k, hl, src, w=900 if i < 3 else 880, seed=20 + i); im.save(f"{OUT}/recorte_{i}.png"); ims.append(im)
# folha de conferência: recortes sobre a base de corte azul
Wd = 1080; Ht = sum(im.height for im in ims) + 60 * (len(ims) + 1) + 140
yy, xx = np.mgrid[0:Ht, 0:Wd]
mat = (np.array([10, 40, 66], np.float32) + np.zeros((Ht, Wd, 1), np.float32)); mat[(xx % 60 < 2) | (yy % 60 < 2)] += 26
sheet = Image.fromarray(np.clip(mat, 0, 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(sheet)
d.text((Wd / 2, 80), "RECORTES · PESQUISA VOX BRASIL 18/10", font=MF("ExtraBold", 40), fill=(245, 226, 176, 255), anchor="mm")
y = 160
for i, im in enumerate(ims):
    r = im.rotate([-1.5, 1.2, -1.0, 1.6, -1.2][i], resample=Image.BICUBIC, expand=True)
    sheet.alpha_composite(r, ((Wd - r.width) // 2, y)); y += im.height + 60
sheet.convert("RGB").save(f"{OUT}/recortes_vox.jpg", quality=92); print("ok", Ht)
