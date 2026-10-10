import random, math, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

F = "/usr/share/fonts/truetype/crosextra/"
I = "/usr/share/fonts/opentype/inter/"
def font(p, s): return ImageFont.truetype(p, s)

CARDS = [
  dict(kicker="UBATUBA  ·  ZONA AZUL",
       head="Após salto de 150% na Zona Azul, Ubatuba propõe aumento de 80% na TPA",
       hl=(1, 6), src="Manchete: Nova Imprensa  ·  set. 2026",
       stamp="R$ 20 → R$ 50", seed=3, rot=-2.5),
  dict(kicker="UBATUBA  ·  POLÍTICA",
       head="Prefeita de Ubatuba rebate críticas sobre alta da Zona Azul: “Paguei R$ 130 em São Paulo”",
       hl=(3, 4), src="Manchete: Nova Imprensa  ·  set. 2026",
       stamp=None, seed=7, rot=2.0),
  dict(kicker="UBATUBA  ·  TAXA AMBIENTAL",
       head="Prefeitura de Ubatuba quer aumentar em 80% valor da TPA (Taxa de Preservação Ambiental)",
       hl=(4, 6), src="Manchete: Notícias das Praias  ·  29 set. 2026",
       stamp="+80%", seed=11, rot=-1.8),
]

W = 900
PAD = 54

def wrap(draw, words, f, maxw):
    lines, cur = [], []
    for i, w in enumerate(words):
        test = " ".join(x for _, x in cur + [(i, w)])
        if cur and draw.textlength(test, font=f) > maxw:
            lines.append(cur); cur = [(i, w)]
        else:
            cur.append((i, w))
    lines.append(cur)
    return lines

def torn_mask(w, h, rnd, amp=9):
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    pts = []
    step = 14
    for x in range(0, w + 1, step): pts.append((x, amp + rnd.uniform(-amp, amp) * 0.9))
    for y in range(0, h + 1, step): pts.append((w - amp * 0.5 + rnd.uniform(-amp, amp) * 0.4, y))
    for x in range(w, -1, -step): pts.append((x, h - amp + rnd.uniform(-amp, amp) * 0.9))
    for y in range(h, -1, -step): pts.append((amp * 0.5 + rnd.uniform(-amp, amp) * 0.4, y))
    d.polygon(pts, fill=255)
    return m.filter(ImageFilter.GaussianBlur(0.8))

def build(c):
    rnd = random.Random(c["seed"])
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    fk = font(I + "Inter-Bold.otf", 22)
    fh = font(F + "Caladea-Bold.ttf", 62)
    fs = font(I + "Inter-Medium.otf", 21)
    words = c["head"].split()
    lines = wrap(tmp, words, fh, W - 2 * PAD)
    lh = 70
    y_head = PAD + 22 + 26 + 18
    body_y = y_head + len(lines) * lh + 26
    H = body_y + 4 * 26 + 40 + 40 + PAD // 2
    # paper
    base = np.array([243, 238, 226], np.float32)
    noise = np.random.default_rng(c["seed"]).normal(0, 7, (H, W, 1)).astype(np.float32)
    grad = np.linspace(0, -10, H, dtype=np.float32)[:, None, None]
    paper = np.clip(base + noise + grad, 0, 255).astype(np.uint8)
    img = Image.fromarray(paper, "RGB").convert("RGBA")
    d = ImageDraw.Draw(img)
    ink = (22, 20, 18, 255)
    # kicker + rule
    d.text((PAD, PAD), c["kicker"], font=fk, fill=(178, 24, 32, 255))
    d.line((PAD, PAD + 38, W - PAD, PAD + 38), fill=ink, width=3)
    d.line((PAD, PAD + 44, W - PAD, PAD + 44), fill=ink, width=1)
    # headline, recording highlight boxes per line
    boxes = []
    a, b = c["hl"]
    for li, ln in enumerate(lines):
        x = PAD; y = y_head + li * lh
        seg = None
        for i, w in ln:
            ww = d.textlength(w, font=fh); sp = d.textlength(" ", font=fh)
            if a <= i <= b:
                seg = [seg[0] if seg else x - 6, y + 10, x + ww + 6, y + lh - 4]
            x += ww + sp
        if seg: boxes.append(seg)
    text_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(text_layer)
    for li, ln in enumerate(lines):
        td.text((PAD, y_head + li * lh), " ".join(w for _, w in ln), font=fh, fill=ink)
    # faux body text (blurred grey lines = decoration)
    bl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bl)
    for k in range(4):
        y = body_y + k * 26
        x = PAD
        end = W - PAD - (rnd.randint(120, 300) if k == 3 else 0)
        while x < end:
            wl = min(rnd.randint(30, 110), end - x)
            if wl < 24: break
            bd.rounded_rectangle((x, y, x + wl, y + 11), 4, fill=(90, 86, 80, 150))
            x += wl + 12
    bl = bl.filter(ImageFilter.GaussianBlur(1.6))
    # source line
    sy = body_y + 4 * 26 + 24
    d.line((PAD, sy, W - PAD, sy), fill=(60, 56, 50, 255), width=1)
    td.text((PAD, sy + 12), c["src"], font=fs, fill=(80, 74, 66, 255))
    mask = torn_mask(W, H, rnd)
    return dict(paper=img, text=text_layer, body=bl, boxes=boxes, mask=mask, H=H)

def stamp_img(txt):
    f = font(I + "Inter-Black.otf", 74)
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    tw = int(tmp.textlength(txt, font=f)); th = 92
    w, h = tw + 70, th + 40
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    red = (200, 22, 30, 255)
    d.rounded_rectangle((4, 4, w - 4, h - 4), 16, outline=red, width=7)
    d.text((35, 18), txt, font=f, fill=red)
    # ink texture: knock out random specks
    a = np.array(im)
    rng = np.random.default_rng(5)
    specks = rng.random(a.shape[:2]) < 0.08
    a[..., 3] = np.where(specks, (a[..., 3] * 0.35).astype(np.uint8), a[..., 3])
    return Image.fromarray(a).filter(ImageFilter.GaussianBlur(0.5))

def render(card, hl_progress):
    """compose card at given highlighter progress 0..1; returns RGBA with shadow-ready alpha."""
    im = card["paper"].copy()
    if hl_progress > 0:
        hl = Image.new("RGBA", im.size, (0, 0, 0, 0))
        hd = ImageDraw.Draw(hl)
        total = sum(b[2] - b[0] for b in card["boxes"])
        left = hl_progress * total
        for x0, y0, x1, y1 in card["boxes"]:
            seg = min(left, x1 - x0)
            if seg <= 0: break
            hd.rounded_rectangle((x0, y0, x0 + seg, y1), 6, fill=(255, 222, 40, 200))
            left -= seg
        im = Image.alpha_composite(im, hl)
    im = Image.alpha_composite(im, card["body"])
    im = Image.alpha_composite(im, card["text"])
    im.putalpha(card["mask"])
    return im

if __name__ == "__main__":
    out = sys.argv[1]
    for k, c in enumerate(CARDS):
        cd = build(c)
        render(cd, 1.0).save(f"{out}/card{k}.png")
    stamp_img("R$ 20 → R$ 50").save(f"{out}/stamp0.png")
