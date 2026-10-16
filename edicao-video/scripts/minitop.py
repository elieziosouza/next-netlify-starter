import numpy as np
from PIL import Image, ImageDraw, ImageFont
def _icon(kind, size, col):
    s = size * 4; im = Image.new("RGBA", (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = col + (255,); w = int(s * (0.11 if kind == "tt" else 0.085))
    if kind == "ig":
        d.rounded_rectangle((w, w, s - w, s - w), int(s * 0.28), outline=c, width=w)
        r = s * 0.2; d.ellipse((s / 2 - r, s / 2 - r, s / 2 + r, s / 2 + r), outline=c, width=w)
        q = s * 0.06; d.ellipse((s * 0.72 - q, s * 0.28 - q, s * 0.72 + q, s * 0.28 + q), fill=c)
    elif kind == "yt":
        d.rounded_rectangle((0, s * 0.18, s, s * 0.82), int(s * 0.2), fill=c)
        d.polygon([(s * 0.40, s * 0.33), (s * 0.40, s * 0.67), (s * 0.70, s * 0.5)], fill=(0, 0, 0, 0))
    elif kind == "tt":
        r = s * 0.2; cx, cy = s * 0.36, s * 0.70
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=c, width=w)
        d.line((cx + r - w / 2, cy, cx + r - w / 2, s * 0.08), fill=c, width=w)
        d.arc((cx + r - w / 2, s * 0.08 - s * 0.05, cx + r + s * 0.32, s * 0.08 + s * 0.30), 90, 180, fill=c, width=w)
    elif kind == "kw":   # Kwai: câmera estilizada simples (sem logo oficial)
        d.rounded_rectangle((w, s * 0.26, s * 0.70, s * 0.80), int(s * 0.14), outline=c, width=w)
        d.polygon([(s * 0.74, s * 0.42), (s * 0.97, s * 0.30), (s * 0.97, s * 0.76), (s * 0.74, s * 0.64)], fill=c)
        r = s * 0.10; d.ellipse((s * 0.37 - r, s * 0.53 - r, s * 0.37 + r, s * 0.53 + r), fill=c)
    im = im.resize((size, size), Image.LANCZOS)
    if kind == "yt":   # punch the play triangle through
        pass
    return im

# redes do canal (TikTok e Kwai usam o mesmo @)
ITEMS = [(["ig"], "@ezvideos_cortes"), (["tt", "kw"], "@elieziosouza78"), (["yt"], "@eliezio.souza78")]

def make_minitop(W, font_path, gold=(214, 182, 116), height=150, cy=70):
    """minimal top: soft navy fade with one line of social handles and a thin gold hairline"""
    top = Image.new("RGBA", (W, height), (0, 0, 0, 0))
    a = (np.clip(1 - np.linspace(0, 1, height) ** 1.6, 0, 1) * 215).astype(np.uint8)
    g = np.zeros((height, W, 4), np.uint8); g[..., 0] = 4; g[..., 1] = 16; g[..., 2] = 30; g[..., 3] = a[:, None]
    top = Image.fromarray(g, "RGBA")
    f = ImageFont.truetype(font_path, 27)
    items = ITEMS
    d = ImageDraw.Draw(top); isz = 30; gap_i = 10; gap = 36
    widths = [len(k) * (isz + 6) - 6 + gap_i + d.textlength(t, font=f) for k, t in items]
    total = sum(widths) + gap * (len(items) - 1)
    x = (W - total) / 2                        # cy 70: barra mais alta (pedido de 16/10/2026)
    for (ks, t), wdt in zip(items, widths):
        for j, k in enumerate(ks): top.alpha_composite(_icon(k, isz, gold), (int(x + j * (isz + 6)), int(cy - isz / 2)))
        d.text((x + len(ks) * (isz + 6) - 6 + gap_i, cy), t, font=f, fill=(255, 255, 255, 240), anchor="lm")
        x += wdt + gap
    # hairline with fading ends
    hl = np.zeros((2, W, 4), np.uint8); xs = np.linspace(-1, 1, W)
    hl[..., 0], hl[..., 1], hl[..., 2] = gold; hl[..., 3] = (np.clip(1 - np.abs(xs) / 0.45, 0, 1) * 200).astype(np.uint8)
    top.alpha_composite(Image.fromarray(hl, "RGBA"), (0, int(cy + 34)))
    return top, int(cy + 40)

def handles_row(W, font_path, gold=(214, 182, 116), size=27, isz=30):
    f = ImageFont.truetype(font_path, size)
    items = ITEMS
    d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4))); gap_i, gap = 10, 36
    widths = [len(k) * (isz + 6) - 6 + gap_i + d0.textlength(t, font=f) for k, t in items]
    total = int(sum(widths) + gap * (len(items) - 1)) + 4
    row = Image.new("RGBA", (total, isz + 10), (0, 0, 0, 0)); d = ImageDraw.Draw(row); x = 2; cy = (isz + 10) / 2
    for (ks, t), wdt in zip(items, widths):
        for j, k in enumerate(ks): row.alpha_composite(_icon(k, isz, gold), (int(x + j * (isz + 6)), int(cy - isz / 2)))
        d.text((x + len(ks) * (isz + 6) - 6 + gap_i, cy), t, font=f, fill=(255, 255, 255, 240), anchor="lm"); x += wdt + gap
    return row

def make_minifooter(W, font_path, gold=(214, 182, 116), height=150):
    """minimal footer: soft fade from the bottom, a thin track line (progress) and the channel tagline"""
    a = (np.clip(np.linspace(0, 1, height) ** 1.4, 0, 1) * 220).astype(np.uint8)
    g = np.zeros((height, W, 4), np.uint8); g[..., 0] = 4; g[..., 1] = 16; g[..., 2] = 30; g[..., 3] = a[:, None]
    foot = Image.fromarray(g, "RGBA"); d = ImageDraw.Draw(foot)
    f = ImageFont.truetype(font_path, 23)
    parts = [("OPINIÃO", (255, 255, 255, 235)), ("  •  ", (255, 255, 255, 120)), ("ATUALIDADES", gold + (255,)),
             ("  •  ", (255, 255, 255, 120)), ("REAÇÕES", (255, 255, 255, 235))]
    total = sum(d.textlength(t, font=f) for t, _ in parts); x = (W - total) / 2; y = 104
    for t, c in parts:
        d.text((x, y), t, font=f, fill=c, anchor="lm"); x += d.textlength(t, font=f)
    return foot, 62   # y of the progress line inside the footer
