"""Recortes do idoso atropelado em ato pró-Lula em Belo Horizonte (17/10/2026). O motorista não tem filiação política
noticiada: nada de rótulo; a versão dele entra como "o outro lado"."""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; FD = f"{S}/fontdl"; OUT = f"{S}/v35/rec"
RED = (210, 30, 36); NAVY = (6, 34, 58); GOLD = (214, 182, 116); INK = (20, 20, 24)
def MF(w, s): return ImageFont.truetype(f"{FD}/Montserrat-{w}.ttf", s)
def SERIF(s): return ImageFont.truetype(f"{FD}/DMSerifDisplay-Regular.ttf", s)
def BIG(s): return ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s)
def wrap(text, font, maxw):
    d = ImageDraw.Draw(Image.new("RGB", (4, 4))); lines = [""]
    for w in text.split():
        t = (lines[-1] + " " + w).strip()
        if d.textlength(t, font=font) <= maxw: lines[-1] = t
        else: lines.append(w)
    return lines
def ilustra(kind, w, h):
    """quadro de 'foto' desenhado: fundo azul-marinho em degradê e traço dourado"""
    im = Image.new("RGB", (w, h)); a = np.zeros((h, w, 3), np.float32)
    yy, xx = np.mgrid[0:h, 0:w]; r = np.sqrt(((xx - w / 2) / w) ** 2 + ((yy - h * 0.4) / h) ** 2)
    a[:] = np.array([4, 14, 30]) + np.array([20, 60, 110]) * np.clip(1 - r * 1.6, 0, 1)[..., None]
    im = Image.fromarray(a.astype(np.uint8)); d = ImageDraw.Draw(im); g = GOLD; lw = 5
    if kind == "casa":
        cx, base = w / 2, h * 0.82; ww = w * 0.7
        d.line((cx - ww / 2, base, cx + ww / 2, base), fill=g, width=lw)
        d.rectangle((cx - ww / 2, base - h * 0.32, cx + ww / 2, base), outline=g, width=lw)
        d.polygon([(cx - w * 0.16, base - h * 0.32), (cx, base - h * 0.48), (cx + w * 0.16, base - h * 0.32)], outline=g, width=lw)
        for i in range(-3, 4):                                          # colunas do pórtico
            x = cx + i * w * 0.045; d.line((x, base - h * 0.30, x, base - 4), fill=g, width=4)
        for side in (-1, 1):                                            # janelas das alas
            for j in range(3):
                x = cx + side * (w * 0.22 + j * w * 0.045); d.rectangle((x - 9, base - h * 0.24, x + 9, base - h * 0.12), outline=g, width=3)
        d.line((cx, base - h * 0.48, cx, base - h * 0.60), fill=g, width=3); d.rectangle((cx, base - h * 0.60, cx + 34, base - h * 0.55), fill=g)
    else:                                                               # púlpito com microfones
        cx = w / 2; top = h * 0.48
        d.polygon([(cx - w * 0.17, top), (cx + w * 0.17, top), (cx + w * 0.13, h * 0.92), (cx - w * 0.13, h * 0.92)], outline=g, width=lw)
        d.ellipse((cx - 40, top + h * 0.12, cx + 40, top + h * 0.12 + 80), outline=g, width=4)
        for dx in (-26, 26):
            d.line((cx + dx, top, cx + dx * 1.6, top - h * 0.18), fill=g, width=4); d.ellipse((cx + dx * 1.6 - 9, top - h * 0.18 - 14, cx + dx * 1.6 + 9, top - h * 0.18 + 6), fill=g)
        d.text((w * 0.08, h * 0.1), "SALA DE IMPRENSA", font=MF("ExtraBold", 26), fill=g)
    d.text((w - 16, h - 12), "ilustração", font=MF("SemiBold", 18), fill=(200, 200, 210), anchor="rs")
    return im
def clipping(kicker, headline, source, kind=None, w=900, seed=1):
    rng = np.random.default_rng(seed); f = SERIF(62); fk = MF("ExtraBold", 26); fs = MF("SemiBold", 22)
    lines = wrap(headline, f, w - 90); ph = 330 if kind else 0
    h = 70 + (ph + 24 if kind else 0) + 46 + len(lines) * 72 + 70
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    top = [(x, int(rng.integers(0, 12))) for x in range(0, w + 1, 18)]; bot = [(x, h - 1 - int(rng.integers(0, 12))) for x in range(w, -1, -18)]
    d.polygon(top + [(w, h)] + bot + [(0, h)], fill=(244, 240, 229, 255))
    a = np.asarray(im).astype(np.int16); a[..., :3] = np.clip(a[..., :3] + rng.normal(0, 5, (h, w)).astype(np.int16)[..., None], 0, 255)
    im = Image.fromarray(a.astype(np.uint8), "RGBA"); d = ImageDraw.Draw(im)
    d.text((45, 56), kicker, font=fk, fill=RED + (255,), anchor="lm"); d.rectangle((45, 80, w - 45, 82), fill=(30, 30, 34, 200))
    y = 100
    if kind == "foto":
        src = Image.open(f"{S}/v34/img/ilha_user.jpg").convert("RGB"); tw_, th_ = w - 90, ph
        sc = max(tw_ / src.width, th_ / src.height); src = src.resize((int(src.width * sc) + 1, int(src.height * sc) + 1), Image.LANCZOS)
        ph_im = src.crop(((src.width - tw_) // 2, (src.height - th_) // 2, (src.width - tw_) // 2 + tw_, (src.height - th_) // 2 + th_))
        ImageDraw.Draw(ph_im).text((tw_ - 14, th_ - 10), "Foto: reprodução", font=MF("SemiBold", 18), fill=(255, 255, 255), anchor="rs", stroke_width=2, stroke_fill=(0, 0, 0))
        im.paste(ph_im, (45, y)); y += ph + 24
    elif kind:
        ph_im = ilustra(kind, w - 90, ph); im.paste(ph_im, (45, y)); y += ph + 24
    for ln in lines: d.text((45, y), ln, font=f, fill=INK + (255,)); y += 72
    d.text((45, h - 42), source, font=fs, fill=(90, 90, 96, 255), anchor="lm")
    return im
RECS = [
    ("BELO HORIZONTE · 17/10", "Motorista atropela idoso em ato pró-Lula e é preso", "Fonte: Poder360 e Gazeta do Povo", None),
    ("A VÍTIMA", "Hilário da Silveira, 67 anos, teve fratura no tornozelo e foi levado ao hospital", "Fonte: Poder360 e Jovem Pan", None),
    ("PRISÃO", "Motorista de 45 anos é preso em flagrante por tentativa de homicídio", "Fonte: Diário do RN e Poder360", None),
    ("O OUTRO LADO", "Motorista diz que jogaram latas e garrafas no carro e que acelerou sem perceber", "Fonte: Gazeta do Povo", None),
]
ims = []
for i, (k, hl, src, kind) in enumerate(RECS, 1):
    im = clipping(k, hl, src, kind, w=900 if kind else 880, seed=40 + i); im.save(f"{OUT}/recorte_{i}.png"); ims.append(im)
Wd = 1080; Ht = sum(im.height for im in ims) + 60 * (len(ims) + 1) + 140
yy, xx = np.mgrid[0:Ht, 0:Wd]; mat = np.array([10, 40, 66], np.float32) + np.zeros((Ht, Wd, 1), np.float32); mat[(xx % 60 < 2) | (yy % 60 < 2)] += 26
sheet = Image.fromarray(np.clip(mat, 0, 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(sheet)
d.text((Wd / 2, 80), "RECORTES · ATROPELAMENTO EM BH", font=MF("ExtraBold", 38), fill=(245, 226, 176, 255), anchor="mm")
y = 160
for i, im in enumerate(ims):
    r = im.rotate([-1.4, 1.2, -1.0, 1.4][i], resample=Image.BICUBIC, expand=True); sheet.alpha_composite(r, ((Wd - r.width) // 2, y)); y += im.height + 60
sheet.convert("RGB").save(f"{OUT}/recortes_porta_voz.jpg", quality=92); print("ok")
