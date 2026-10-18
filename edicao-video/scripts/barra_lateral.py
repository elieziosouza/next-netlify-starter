"""Barra lateral do canal (inspirada no reels da BandNews): faixa vertical na borda esquerda com brilho que vaza para o vídeo,
nome do canal escrito na vertical e a própria barra servindo de progresso do vídeo. Mais o cartão de manchete de vidro fosco."""
import sys
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FD = None
W, H = 1080, 1920
NAVY = (6, 34, 58); NAVY_L = (18, 70, 120); GOLD = (214, 182, 116); GOLD_L = (245, 226, 176); RED = (210, 30, 36)
def MF(w, s): return ImageFont.truetype(f"{FD}/Montserrat-{w}.ttf", s)
def grad(h, stops):
    ys = np.linspace(0, 1, h); out = np.zeros((h, 3), np.float32)
    for (a, ca), (b, cb) in zip(stops, stops[1:]):
        m = (ys >= a) & (ys <= b); k = ((ys[m] - a) / (b - a))[:, None]; out[m] = np.array(ca) * (1 - k) + np.array(cb) * k
    return out
STYLES = {"ouro": [(0, (24, 92, 190)), (0.45, (10, 46, 96)), (0.8, (150, 112, 46)), (1, GOLD)], "vermelho": [(0, (24, 92, 190)), (0.45, (12, 44, 104)), (0.75, (150, 24, 40)), (1, (225, 36, 46))]}
_cache = {}
def make_bar(style="ouro", bw=84):
    """camadas fixas da barra: brilho, faixa e texto vertical"""
    key = (style, bw)
    if key in _cache: return _cache[key]
    g = grad(H, STYLES[style]); band = np.repeat(g[:, None, :], bw, 1)
    shade = np.linspace(1.15, 0.85, bw)[None, :, None]; band = band * shade                    # leve volume, mais claro na borda de fora
    bar = np.zeros((H, W, 4), np.float32); bar[:, :bw, :3] = band; bar[:, :bw, 3] = 255
    glow = np.zeros((H, W, 4), np.float32); glow[:, :bw + 10, :3] = np.repeat(g[:, None, :], bw + 10, 1); glow[:, :bw + 10, 3] = 255
    glow = cv2.GaussianBlur(glow, (0, 0), 38); glow[..., 3] = np.clip(glow[..., 3] * 1.25, 0, 255)
    txt = Image.new("RGBA", (H, bw), (0, 0, 0, 0)); d = ImageDraw.Draw(txt); f = MF("Bold", 24)
    s = "  ·  ".join(["OPINIÃO", "ATUALIDADES", "REAÇÕES"]); spaced = " ".join(s)
    d.text((H * 0.52, bw / 2), spaced, font=f, fill=(255, 255, 255, 170), anchor="mm")
    txt = txt.rotate(90, expand=True)
    _cache[key] = (Image.fromarray(np.clip(glow, 0, 255).astype(np.uint8), "RGBA"), Image.fromarray(np.clip(bar, 0, 255).astype(np.uint8), "RGBA"), txt, bw)
    return _cache[key]
def draw_bar(frame, prog, style="ouro", intro=1.0):
    """prog 0..1: o preenchimento dourado desce pela barra; intro 0..1 faz a barra entrar pela esquerda"""
    glow, bar, txt, bw = make_bar(style); dx = int(-bw * 1.6 * (1 - intro))
    frame.alpha_composite(glow, (dx, 0)) if dx == 0 else frame.alpha_composite(glow.transform(glow.size, Image.AFFINE, (1, 0, -dx, 0, 1, 0)))
    b = bar.copy(); d = ImageDraw.Draw(b); y = int(H * prog)
    d.rectangle((bw - 7, 0, bw - 1, y), fill=GOLD + (255,)); d.rectangle((bw - 7, y, bw - 1, H), fill=(255, 255, 255, 40))
    d.ellipse((bw - 14, y - 7, bw + 6, y + 13), fill=GOLD_L + (255,))
    b.alpha_composite(txt, (0, 0))
    frame.alpha_composite(b.transform(b.size, Image.AFFINE, (1, 0, -dx, 0, 1, 0)) if dx else b)
def lower_card(frame, kicker, lines, y, k=1.0, accent=RED):
    """cartão de vidro fosco com aba do assunto em cima (como o letreiro da BandNews, nas cores do canal)"""
    if k <= 0: return
    x0, x1 = 150, W - 70; f = MF("ExtraBold", 54); lh = 66; h = 50 + lh * len(lines)
    region = frame.crop((x0, y, x1, y + h)).filter(ImageFilter.GaussianBlur(18))
    glass = Image.new("RGBA", region.size, (255, 255, 255, 0)); glass.alpha_composite(region)
    tint = Image.new("RGBA", region.size, (250, 246, 236, 205)); glass.alpha_composite(tint)
    m = Image.new("L", region.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, region.width - 1, h - 1), 16, fill=255); glass.putalpha(m)
    d = ImageDraw.Draw(glass)
    for i, ln in enumerate(lines): d.text((region.width / 2, 25 + lh * i + lh / 2), ln, font=f, fill=NAVY + (255,), anchor="mm")
    fk = MF("ExtraBold", 30); tab_w = int(ImageDraw.Draw(glass).textlength(" ".join(kicker), font=fk) + 60)
    tab = Image.new("RGBA", (tab_w, 58), (0, 0, 0, 0)); dt = ImageDraw.Draw(tab)
    dt.rounded_rectangle((0, 0, tab_w - 1, 70), 12, fill=accent + (255,)); dt.text((30, 30), " ".join(kicker), font=fk, fill=(255, 255, 255, 255), anchor="lm")
    side = Image.new("RGBA", (12, h + 58), accent + (255,))
    off = int(40 * (1 - k)); a = int(255 * min(1, k * 1.5))
    for im, pos in ((side, (x0 - 16, y - 58)), (tab, (x0 - 4, y - 58)), (glass, (x0, y))):
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: v * a // 255)); frame.alpha_composite(im, (pos[0] + off, pos[1]))
if __name__ == "__main__":
    S = sys.argv[1]; FD = f"{S}/fontdl"; sys.path.insert(0, f"{S}/work")
    from minitop import make_minitop
    import subprocess
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", "18.6", "-i", f"{S}/v29/me.mp4", "-frames:v", "1", "-vf", "scale=1080:1920", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    me = np.frombuffer(p, np.uint8).reshape(H, W, 3)
    top, TOPH = make_minitop(W, f"{FD}/Montserrat-SemiBold.ttf")
    outs = []
    for style, prog, kick, lines, acc in (("ouro", 0.42, "ELEIÇÕES 2026", ["PESQUISA VOX BRASIL:", "LULA 51% x 49% FLÁVIO"], RED),
                                         ("vermelho", 0.7, "AO VIVO HOJE", ["DEBATE NA BAND", "LULA x FLÁVIO ÀS 20H"], GOLD)):
        fr = Image.fromarray(me).convert("RGBA"); draw_bar(fr, prog, style); fr.alpha_composite(top)
        lower_card(fr, kick, lines, 1600, 1.0, acc); outs.append(fr.convert("RGB"))
    sheet = Image.new("RGB", (1080, 960)); [sheet.paste(o.resize((540, 960)), (i * 540, 0)) for i, o in enumerate(outs)]
    sheet.save(f"{S}/v31/barra_lateral_AB.jpg", quality=92)
    for i, o in enumerate(outs): o.save(f"{S}/v31/barra_{'AB'[i]}.jpg", quality=92)
    print("ok")
