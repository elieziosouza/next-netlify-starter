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
STYLES = {"canal": [(0, (30, 98, 196)), (0.35, (14, 58, 118)), (0.62, NAVY), (0.85, (150, 120, 62)), (1, GOLD_L)], "ouro": [(0, (24, 92, 190)), (0.45, (10, 46, 96)), (0.8, (150, 112, 46)), (1, GOLD)], "vermelho": [(0, (24, 92, 190)), (0.45, (12, 44, 104)), (0.75, (150, 24, 40)), (1, (225, 36, 46))]}
_cache = {}
def make_bar(style="canal", bw=84):
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
# o YouTube Shorts corta as laterais em celulares compridos (cerca de 50 a 100 px de cada lado): a barra fica recuada da borda
INSET = 0                                                         # barra colada no canto (pedido dele em 18/10)
CARD_X = (242, 922)                                               # caixa centrada no espaço depois da barra (centro x 582)
_cta = {}
def cta_layer(bw, txt="SIGA  ·  COMPARTILHE"):
    if (bw, txt) in _cta: return _cta[(bw, txt)]
    f = MF("ExtraBold", 31); tw = int(ImageDraw.Draw(Image.new("L", (4, 4))).textlength(txt, font=f)) + 70
    lay = Image.new("RGBA", (tw, bw - 18), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((0, 0, tw - 1, bw - 19), (bw - 18) // 2, fill=GOLD + (255,), outline=GOLD_L + (255,), width=2)
    d.text((tw / 2, (bw - 18) / 2 + 1), txt, font=f, fill=NAVY + (255,), anchor="mm")
    lay = lay.rotate(90, expand=True); _cta[(bw, txt)] = lay; return lay
def draw_bar(frame, prog, style="canal", intro=1.0, cta=0.0, pulse=0.0):
    """prog 0..1: o preenchimento dourado desce pela barra; intro 0..1 faz a barra entrar pela esquerda"""
    glow, bar, txt, bw = make_bar(style); dx = INSET + int(-(bw + INSET) * 1.6 * (1 - intro))
    frame.alpha_composite(glow.transform(glow.size, Image.AFFINE, (1, 0, -dx, 0, 1, 0)))
    b = bar.copy(); d = ImageDraw.Draw(b); y = int(H * prog)
    d.rectangle((bw - 7, 0, bw - 1, y), fill=GOLD + (255,)); d.rectangle((bw - 7, y, bw - 1, H), fill=(255, 255, 255, 40))
    d.ellipse((bw - 14, y - 7, bw + 6, y + 13), fill=GOLD_L + (255,))
    if cta < 1:
        tx = txt if cta <= 0 else txt.copy()
        if cta > 0: tx.putalpha(tx.getchannel("A").point(lambda v: int(v * (1 - cta))))
        b.alpha_composite(tx, (0, 0))
    if cta > 0:                                                   # cápsula dourada com o convite, respirando de leve
        c = cta_layer(bw); sc = 0.85 + 0.15 * cta + 0.03 * pulse
        c = c.resize((int(c.width * sc), int(c.height * sc)), Image.BICUBIC); c.putalpha(c.getchannel("A").point(lambda v: int(v * cta)))
        gl = Image.new("RGBA", (c.width + 60, c.height + 60), (0, 0, 0, 0)); gl.alpha_composite(c, (30, 30))
        gl = gl.filter(ImageFilter.GaussianBlur(14)); gl.putalpha(gl.getchannel("A").point(lambda v: int(v * (0.5 + 0.3 * pulse))))
        cx = (bw - 7) // 2; cy = int(H * 0.5)
        b.alpha_composite(gl, (cx - gl.width // 2, cy - gl.height // 2)); b.alpha_composite(c, (cx - c.width // 2, cy - c.height // 2))
    frame.alpha_composite(b.transform(b.size, Image.AFFINE, (1, 0, -dx, 0, 1, 0)))
def lower_card(frame, kicker, lines, y, k=1.0, accent=GOLD, fs=54):
    """caixa fixa do canal numa peça só: barra dourada do lado, aba dourada com o assunto e vidro azul-marinho com contorno dourado.
    Desenhada em 2x e reduzida (bordas lisas); a barra, a aba e o contorno são o mesmo dourado e se emendam sem degrau."""
    if k <= 0: return
    SS = 2; x0, x1 = CARD_X; f = MF("ExtraBold", fs * SS); lh = int(fs * 1.22); h = int(fs * 0.8) + lh * len(lines)
    th, bw, r, ow = 52, 12, 16, 3                                   # aba, barra, raio, espessura do contorno
    fk = MF("ExtraBold", 30); tab_w = int(fk.getlength(" ".join(kicker)) + 64)
    L, T = x0 - bw, y - th; Wc, Hc = (x1 - L) * SS, (h + th) * SS
    bg = frame.crop((L, T, x1, y + h)).filter(ImageFilter.GaussianBlur(18)).resize((Wc, Hc), Image.BILINEAR)
    piece = Image.new("RGBA", (Wc, Hc), (0, 0, 0, 0))
    bx0, by0 = bw * SS, th * SS                                     # canto da parte azul
    glass = bg.crop((bx0, by0, Wc, Hc)).copy(); glass.alpha_composite(Image.new("RGBA", glass.size, NAVY + (215,)))
    sheen = Image.linear_gradient("L").resize(glass.size).point(lambda v: int(60 * (1 - v / 255)))
    hl = Image.new("RGBA", glass.size, (120, 170, 230, 0)); hl.putalpha(sheen); glass.alpha_composite(hl)
    gm = Image.new("L", glass.size, 0); ImageDraw.Draw(gm).rounded_rectangle((0, 0, glass.width - 1, glass.height - 1), r * SS, fill=255, corners=(False, True, True, False))
    glass.putalpha(gm); piece.alpha_composite(glass, (bx0, by0))
    d = ImageDraw.Draw(piece); G = accent + (255,)
    d.rounded_rectangle((bx0 - ow * SS, by0, Wc - 1, Hc - 1), r * SS, outline=G, width=ow * SS, corners=(False, True, True, False))   # contorno: emenda na barra
    d.rounded_rectangle((0, 0, bx0 + 2, Hc - 1), 6 * SS, fill=G, corners=(True, False, False, True))                               # barra: arredonda só por fora
    d.rounded_rectangle((0, 0, bx0 + tab_w * SS, by0 + ow * SS), 12 * SS, fill=G, corners=(True, True, False, False))              # aba: assenta reta no contorno
    d.text((bx0 + 32 * SS, by0 / 2 + SS), " ".join(kicker), font=MF("ExtraBold", 30 * SS), fill=NAVY + (255,), anchor="lm")
    cx = bx0 + (Wc - bx0) / 2
    for i_, ln in enumerate(lines): d.text((cx, by0 + (int(fs * 0.4) + lh * i_ + lh / 2) * SS), ln, font=f, fill=(255, 255, 255, 255), anchor="mm")
    piece = piece.resize((x1 - L, h + th), Image.LANCZOS)
    sh = Image.new("RGBA", (piece.width + 40, piece.height + 40), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((20, 26, piece.width + 20, piece.height + 26), 18, fill=(0, 0, 0, 110))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    off = int(40 * (1 - k)); a = int(255 * min(1, k * 1.5))
    for im, pos in ((sh, (L - 20, T - 20)), (piece, (L, T))):
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
