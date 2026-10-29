"""Vídeo 1 da série Imóvel na planta: "Vale a pena comprar na planta?" só com motion design (sem imagem de apoio).
Uso: python3 render_planta_motion.py narracao.mp3 saida.mp4 [pasta_tmp] [preview_segundos...]
Fundo claro editorial, planta baixa se desenhando, palavra gigante em serifa, legenda de uma palavra e destaques em verde."""
import sys, math, subprocess, wave
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
KIT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(KIT / "scripts"))
import sfx

VOICE, OUT = sys.argv[1], sys.argv[2]
TMP = Path(sys.argv[3] if len(sys.argv) > 3 else "/tmp/planta_motion"); TMP.mkdir(parents=True, exist_ok=True)
PREVIEW = [float(x) for x in sys.argv[4:]]
FD = KIT / "assets" / "fonts"; W, H, FPS = 1080, 1920, 30
LEAD = 0.35                       # respiro antes da primeira palavra
BG = (243, 239, 231); INK = (22, 24, 27); GREEN = (24, 150, 84); SOFT = (22, 24, 27, 120)

def F(name, s, _c={}):
    k = (name, s)
    if k not in _c: _c[k] = ImageFont.truetype(str(FD / f"{name}.ttf"), s)
    return _c[k]
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def back(x): x = clamp(x); c = 1.6; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# ---------- falas (tempos da transcrição da narração; palavras distribuídas dentro de cada trecho) ----------
PHR = [("Comprar apartamento na planta em São Paulo:", 0.12, 2.34), ("é bom negócio", 2.65, 3.56), ("ou cilada?", 3.83, 4.55),
       ("Depende de três coisas.", 5.11, 6.55), ("Primeiro,", 6.75, 7.25), ("o preço.", 7.70, 8.26),
       ("Na planta,", 8.80, 9.45), ("costuma sair mais barato que um pronto na mesma região,", 9.75, 12.71),
       ("e a entrada é parcelada durante a obra.", 13.08, 15.81), ("Segundo,", 16.25, 16.97), ("o tempo.", 17.05, 17.95),
       ("A obra leva de dois a quatro anos.", 18.26, 20.30), ("Se você precisa mudar agora, não é pra você.", 20.45, 22.76),
       ("Terceiro,", 23.10, 23.65), ("a entrega.", 23.99, 24.68), ("As parcelas são corrigidas pelo INCC,", 25.18, 27.75),
       ("o saldo vai pro financiamento com os juros daquele momento,", 28.09, 31.01),
       ("e ainda tem ITBI, registro e condomínio.", 31.42, 34.53),
       ("Se você não tem pressa e planeja a entrega desde o começo,", 35.06, 37.45), ("vale muito a pena.", 37.55, 38.85),
       ("Qualquer dúvida,", 39.42, 40.23), ("me chama.", 40.30, 41.13)]
WORDS = []
for txt, st, en in PHR:
    ws = txt.split(); tot = sum(len(w) + 2 for w in ws); acc = 0
    for w in ws:
        a = st + (en - st) * acc / tot; acc += len(w) + 2; b = st + (en - st) * acc / tot
        WORDS.append((w.strip(",.:?"), a + LEAD, b + LEAD))
def wt(word, after=0.0):
    """instante (no vídeo) em que a palavra é dita, procurando a partir de 'after' (tempo do áudio)"""
    for w, a, b in WORDS:
        if w.lower() == word.lower() and a >= after + LEAD - 0.01: return a
    raise KeyError(word)
T = lambda x: x + LEAD            # tempo do áudio -> tempo do vídeo
VOICE_DUR = 41.42; DUR = T(VOICE_DUR) + 3.4

# cenas: (início, fim)
SC_HOOK = (0.0, T(5.0)); SC_TRES = (T(5.0), T(6.65)); SC_PRECO = (T(6.65), T(16.1)); SC_TEMPO = (T(16.1), T(23.0))
SC_ENTREGA = (T(23.0), T(34.95)); SC_VALE = (T(34.95), T(39.3)); SC_FIM = (T(39.3), DUR)
BLUR_AT = [T(6.65), T(16.1), T(23.0), T(34.95), T(39.3)]

# ---------- camadas de texto ----------
_cache = {}
def text_img(text, font, fill, shadow=0.0, spacing=0):
    k = (text, font.path, font.size, fill, shadow, spacing)
    if k in _cache: return _cache[k]
    d = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    if spacing:
        widths = [d.textlength(c, font=font) + spacing for c in text]; tw = int(sum(widths)); b = d.textbbox((0, 0), text, font=font)
        im = Image.new("RGBA", (tw + 60, b[3] - b[1] + 60), (0, 0, 0, 0)); x = 30
        for c, wd in zip(text, widths): ImageDraw.Draw(im).text((x, 30 - b[1]), c, font=font, fill=fill); x += wd
    else:
        b = d.textbbox((0, 0), text, font=font)
        im = Image.new("RGBA", (b[2] - b[0] + 60, b[3] - b[1] + 60), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((30 - b[0], 30 - b[1]), text, font=font, fill=fill)
    if shadow:
        blk = Image.new("RGBA", im.size, (0, 0, 0, 255)); blk.putalpha(im.getchannel("A").point(lambda v: int(v * shadow)))
        out = Image.new("RGBA", im.size, (0, 0, 0, 0)); out.alpha_composite(blk.filter(ImageFilter.GaussianBlur(9)), (0, 6)); out.alpha_composite(im); im = out
    _cache[k] = im; return im

def put(canvas, im, cx, cy, alpha=1.0, blur=0.0, scale=1.0, anchor="c"):
    if alpha <= 0.004: return
    if scale != 1.0: im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    if blur > 0.3: im = im.filter(ImageFilter.GaussianBlur(blur))
    if alpha < 0.999:
        im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    x = int(cx - im.width / 2) if anchor == "c" else int(cx - 30) if anchor == "l" else int(cx - im.width + 30)
    pos = (x, int(cy - im.height / 2))
    if canvas.mode == "RGBA": canvas.alpha_composite(im, pos)
    else: canvas.paste(im, pos, im)          # quadro em RGB: paste com máscara mistura de verdade

def life(t, t0, t1, fin=0.45, fout=0.3):
    """entrada saindo do desfoque e saída suave: devolve (alpha, blur, dy)"""
    if t < t0 or t > t1 + fout: return 0, 0, 0
    a = ease_out((t - t0) / fin); o = 1 - smooth((t - t1) / fout) if t > t1 else 1
    return a * o, (1 - a) * 14 + (1 - o) * 8, (1 - a) * 22

def show(canvas, t, im, cx, cy, t0, t1, grow=0.0, anchor="c", fin=0.45):
    al, bl, dy = life(t, t0, t1, fin)
    if al <= 0: return
    sc = 1 + grow * clamp((t - t0) / max(0.1, t1 - t0))
    put(canvas, im, cx, cy + dy, al, bl, sc, anchor)

# ---------- fundo e planta baixa ----------
def make_bg():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((x - W / 2) / W) ** 2 + ((y - H * 0.45) / H) ** 2)
    base = np.array(BG, np.float32)[None, None, :] * (1.015 - 0.10 * r[..., None] ** 1.6)
    g = np.random.default_rng(3).normal(0, 2.2, (H, W, 1))
    im = np.clip(base + g, 0, 255).astype(np.uint8)
    for gx in range(60, W, 60): im[:, gx] = (im[:, gx] * 0.975).astype(np.uint8)
    for gy in range(40, H, 60): im[gy, :] = (im[gy, :] * 0.975).astype(np.uint8)
    return Image.fromarray(im)
BGIMG = make_bg()

# planta baixa em coordenadas 0..100 (x) e 0..80 (y)
WALLS = [((0, 0), (100, 0)), ((100, 0), (100, 80)), ((100, 80), (0, 80)), ((0, 80), (0, 0)),
         ((42, 0), (42, 34)), ((42, 46), (42, 80)), ((0, 46), (30, 46)), ((36, 46), (42, 46)),
         ((42, 40), (72, 40)), ((80, 40), (100, 40)), ((72, 0), (72, 26)), ((72, 34), (72, 40)),
         ((0, 62), (14, 62)), ((20, 62), (42, 62))]
DOORS = [((30, 46), 6, 0), ((72, 26), 8, 90), ((14, 62), 6, 0), ((42, 34), 6, 90)]
ROOMS = [("SUÍTE", 21, 22), ("SALA", 58, 62), ("COZINHA", 86, 20), ("QUARTO", 21, 54), ("BANHO", 21, 71), ("VARANDA", 86, 62)]
SEGLEN = [math.dist(a, b) for a, b in WALLS]; TOTLEN = sum(SEGLEN)

def plan_layer(prog, alpha, ox, oy, sc, col=INK, labels=1.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    P = lambda p: (ox + p[0] * sc, oy + p[1] * sc)
    a = int(255 * alpha); left = prog * TOTLEN
    for (p0, p1), L in zip(WALLS, SEGLEN):
        if left <= 0: break
        f = min(1, left / L); left -= L
        q = (p0[0] + (p1[0] - p0[0]) * f, p0[1] + (p1[1] - p0[1]) * f)
        d.line([P(p0), P(q)], fill=col + (a,), width=6)
    dp = clamp((prog - 0.8) / 0.2)
    for (c, r, ang) in DOORS:
        if dp <= 0: break
        cx, cy = P(c); R = r * sc
        d.arc([cx - R, cy - R, cx + R, cy + R], ang, ang + 90 * dp, fill=col + (int(a * 0.55),), width=2)
    if labels > 0:
        for name, x, y in ROOMS:
            put(lay, text_img(name, F("Montserrat-SemiBold", 22), col + (255,), spacing=4), *P((x, y)), alpha * labels * 0.6)
    return lay

# ---------- ícones ----------
def check_icon(prog, size=56):
    im = Image.new("RGBA", (size + 8, size + 8), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([4, 4, size + 4, size + 4], fill=GREEN + (int(255 * clamp(prog * 2)),))
    pts = [(size * 0.30 + 4, size * 0.52 + 4), (size * 0.45 + 4, size * 0.67 + 4), (size * 0.72 + 4, size * 0.36 + 4)]
    p = clamp(prog * 2 - 0.6) / 1.0
    if p > 0:
        l1 = math.dist(pts[0], pts[1]); l2 = math.dist(pts[1], pts[2]); s = p * (l1 + l2)
        if s <= l1: d.line([pts[0], (pts[0][0] + (pts[1][0] - pts[0][0]) * s / l1, pts[0][1] + (pts[1][1] - pts[0][1]) * s / l1)], fill=(255, 255, 255, 255), width=6)
        else:
            f = (s - l1) / l2; d.line([pts[0], pts[1], (pts[1][0] + (pts[2][0] - pts[1][0]) * f, pts[1][1] + (pts[2][1] - pts[1][1]) * f)], fill=(255, 255, 255, 255), width=6, joint="curve")
    return im

def key_icon(col=INK):
    im = Image.new("RGBA", (90, 90), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([8, 25, 46, 63], outline=col + (255,), width=6); d.line([(46, 44), (84, 44)], fill=col + (255,), width=6)
    d.line([(72, 44), (72, 58)], fill=col + (255,), width=6); d.line([(82, 44), (82, 54)], fill=col + (255,), width=6)
    return im

def phone_icon(col=GREEN):
    im = Image.new("RGBA", (70, 70), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.ellipse([2, 2, 68, 68], fill=col + (255,))
    d.rounded_rectangle([24, 14, 46, 56], 5, outline=(255, 255, 255, 255), width=4); d.line([(31, 49), (39, 49)], fill=(255, 255, 255, 255), width=3)
    return im

# ---------- elementos fixos ----------
TOPLAB = text_img("IMÓVEL NA PLANTA · SÃO PAULO", F("Montserrat-SemiBold", 25), INK + (150,), spacing=5)
HANDLE = text_img("@eliezio.corretordeimoveis", F("Montserrat-Medium", 26), INK + (140,))
def chrome(c, t):
    a = smooth(t / 0.6) * (1 - smooth((t - SC_FIM[0]) / 0.4))
    put(c, TOPLAB, W / 2, 128, a)
    d = ImageDraw.Draw(c, "RGBA"); lw = 300 * smooth(t / 0.9)
    if lw > 1: d.line([(W / 2 - lw, 168), (W / 2 + lw, 168)], fill=INK + (int(60 * a),), width=2)
    put(c, HANDLE, W / 2, 1812, a)
    d.line([(90, 1860), (W - 90, 1860)], fill=INK + (28,), width=4)
    d.line([(90, 1860), (90 + (W - 180) * clamp(t / DUR), 1860)], fill=GREEN + (230,), width=4)

def big(c, t, kicker, word, t0, t1, y=470, size=230, halo=False):
    """palavra gigante em serifa com a palavra pequena sobreposta no canto superior esquerdo"""
    im = text_img(word, F("DMSerifDisplay-Regular", size), INK + (255,), shadow=0.18)
    if halo:   # mancha clara atrás da palavra para ela ler por cima da planta
        hk = ("halo", word, size)
        if hk not in _cache:
            h = text_img(word, F("DMSerifDisplay-Regular", size), BG + (255,)); a = Image.new("L", (h.width + 120, h.height + 120), 0)
            a.paste(h.getchannel("A"), (60, 60)); a = a.filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(16))
            hh = Image.new("RGBA", a.size, BG + (255,)); hh.putalpha(a); _cache[hk] = hh
        show(c, t, _cache[hk], W / 2, y, t0, t1, grow=0.04, fin=0.6)
    show(c, t, im, W / 2, y, t0, t1, grow=0.04, fin=0.6)
    if kicker:
        k = text_img(kicker, F("Montserrat-Regular", 40), INK + (255,))
        show(c, t, k, W / 2 - im.width / 2 + 60, y - size * 0.60, t0 + 0.12, t1, anchor="l")

def number(c, t, n, t0, t1, y=240):
    im = text_img(n, F("Montserrat-ExtraBold", 44), GREEN + (255,), spacing=6)
    show(c, t, im, W / 2, y, t0, t1)

def accent(c, t, text, cx, cy, t0, t1, size=120, col=GREEN):
    im = text_img(text, F("Montserrat-ExtraBoldItalic", size), col + (255,))
    al, bl, dy = life(t, t0, t1, 0.35)
    if al <= 0: return
    put(c, im, cx, cy + dy, al, bl, 0.86 + 0.14 * back((t - t0) / 0.35))

# ---------- cenas ----------
def sc_hook(c, t):
    t0, t1 = SC_HOOK
    pp = ease_out((t - 0.15) / 2.6); al = 1 - smooth((t - t1 + 0.1) / 0.5)
    lay = plan_layer(pp, 0.85 * al, 115, 330, 8.5, labels=clamp((t - 2.0) / 0.6)); c.paste(lay, (0, 0), lay)
    # faixa clara atrás da palavra grande para ela ler por cima da planta
    big(c, t, "comprar na", "planta", 0.25, t1 - 0.3, y=700, size=250, halo=True)
    accent(c, t, "BOM NEGÓCIO", W / 2, 1180, wt("bom") - 0.05, t1 - 0.3, 104)
    accent(c, t, "OU CILADA?", W / 2, 1320, wt("cilada") - 0.1, t1 - 0.3, 104, INK)

def sc_tres(c, t):
    t0, t1 = SC_TRES
    big(c, t, "depende de", "3 coisas", t0 + 0.05, t1, y=620, size=210)
    for i in range(3):
        ts = T(5.65) + i * 0.28; al, bl, dy = life(t, ts, t1, 0.3)
        if al <= 0: continue
        cx = W / 2 + (i - 1) * 230; s = back((t - ts) / 0.3)
        lay = Image.new("RGBA", (200, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.ellipse([10, 10, 190, 190], outline=GREEN + (255,), width=6)
        n = text_img(str(i + 1), F("DMSerifDisplay-Regular", 120), INK + (255,)); lay.alpha_composite(n, (100 - n.width // 2, 100 - n.height // 2 - 6))
        put(c, lay, cx, 1050, al, bl, 0.6 + 0.4 * s)

def sc_preco(c, t):
    t0, t1 = SC_PRECO
    number(c, t, "01", t0 + 0.1, t1 - 0.2); big(c, t, "primeiro, o", "preço", t0 + 0.15, t1 - 0.2)
    # gráfico de duas barras (ilustrativo, sem números)
    g0 = wt("Na", 8.0); g1 = wt("entrada") - 0.2
    ga = (1 - smooth((t - g1) / 0.4)) if t > g1 else 1
    if t >= g0 and ga > 0:
        d = ImageDraw.Draw(c, "RGBA"); base = 1290
        d.line([(170, base), (910, base)], fill=INK + (int(140 * ga),), width=3)
        for (lab, cx, hmax, col, ts) in [("NA PLANTA", 380, 300, GREEN, g0 + 0.15), ("PRONTO", 700, 450, INK, wt("pronto") - 0.15)]:
            p = ease_out((t - ts) / 0.6)
            if p <= 0: continue
            h = hmax * p; d.rectangle([cx - 100, base - h, cx + 100, base - 2], fill=col + (int(235 * ga),))
            d.polygon([(cx - 100, base - h), (cx - 80, base - h - 16), (cx + 120, base - h - 16), (cx + 100, base - h)], fill=tuple(min(255, v + 45) for v in col) + (int(235 * ga),))
            d.polygon([(cx + 100, base - h), (cx + 120, base - h - 16), (cx + 120, base - 18), (cx + 100, base - 2)], fill=tuple(max(0, v - 30) for v in col) + (int(235 * ga),))
            put(c, text_img(lab, F("Montserrat-Bold", 32), INK + (255,), spacing=3), cx, base + 42, ga * clamp(p * 2))
        tb = wt("barato") - 0.1
        if t > tb: accent(c, t, "MAIS BARATO", 380, 1290 - 300 - 80, tb, g1, 50)
    # entrada parcelada: blocos que vão se preenchendo
    e0 = wt("entrada")
    if t >= e0:
        put(c, text_img("ENTRADA", F("Montserrat-Bold", 34), INK + (255,), spacing=6), W / 2, 830, *life(t, e0, t1 - 0.2)[:2])
        d = ImageDraw.Draw(c, "RGBA"); al = life(t, e0, t1 - 0.2)[0]
        for i in range(12):
            r, k = divmod(i, 6); x = 160 + k * 135; y = 900 + r * 150
            ts = e0 + 0.35 + i * 0.17; f = ease_out((t - ts) / 0.25)
            d.rounded_rectangle([x, y, x + 110, y + 110], 14, outline=INK + (int(120 * al),), width=3)
            if f > 0:
                m = 55 * (1 - f); d.rounded_rectangle([x + m, y + m, x + 110 - m, y + 110 - m], 12, fill=GREEN + (int(235 * al),))
        accent(c, t, "PARCELADA NA OBRA", W / 2, 1270, wt("parcelada") - 0.05, t1 - 0.2, 64)

def sc_tempo(c, t):
    t0, t1 = SC_TEMPO
    number(c, t, "02", t0 + 0.1, t1 - 0.2); big(c, t, "segundo, o", "tempo", wt("Segundo") - 0.05, t1 - 0.2)
    l0 = wt("tempo") + 0.1; l1 = wt("Se", 20.0) - 0.15
    if t >= l0:
        al = life(t, l0, l1)[0]; d = ImageDraw.Draw(c, "RGBA"); y = 1090; xa, xb = 170, 910
        p = ease_out((t - l0) / 0.5); d.line([(xa, y), (xa + (xb - xa) * p, y)], fill=INK + (int(150 * al),), width=4)
        d.ellipse([xa - 16, y - 16, xa + 16, y + 16], fill=INK + (int(255 * al),))
        put(c, text_img("LANÇAMENTO", F("Montserrat-Bold", 28), INK + (255,), spacing=3), xa + 70, y + 60, al)
        put(c, key_icon(), xb, y, al * clamp(p * 1.5 - 0.5))
        put(c, text_img("ENTREGA", F("Montserrat-Bold", 28), INK + (255,), spacing=3), xb - 30, y + 60, al * clamp(p * 1.5 - 0.5))
        m = smooth((t - wt("leva")) / (wt("anos") + 0.4 - wt("leva"))); mx = xa + (xb - 60 - xa) * m
        d.ellipse([mx - 13, y - 13, mx + 13, y + 13], fill=GREEN + (int(255 * al),))
        if t > wt("dois") - 0.1: accent(c, t, "2 A 4 ANOS", W / 2, 900, wt("dois") - 0.1, l1, 110)
    p0 = wt("precisa")
    if t >= p0 - 0.1:
        put(c, text_img("Precisa mudar agora?", F("Montserrat-SemiBold", 60), INK + (255,)), W / 2, 960, *life(t, p0 - 0.1, t1 - 0.2)[:2])
        n0 = wt("não", 21.0)
        if t >= n0 - 0.05:
            accent(c, t, "NÃO É PRA VOCÊ", W / 2, 1110, n0 - 0.05, t1 - 0.2, 92, INK)
            d = ImageDraw.Draw(c, "RGBA"); p = ease_out((t - n0 - 0.35) / 0.35); al = life(t, n0, t1 - 0.2)[0]
            if p > 0: d.line([(W / 2 - 400 * p, 1185), (W / 2 + 400 * p, 1185)], fill=GREEN + (int(255 * al),), width=8)

ITEMS = [("INCC corrige as parcelas", "INCC"), ("Saldo vai pro financiamento", "saldo"), ("Juros da época da entrega", "juros"),
         ("ITBI: 3% em São Paulo", "ITBI"), ("Registro e condomínio", "registro")]
def sc_entrega(c, t):
    t0, t1 = SC_ENTREGA
    number(c, t, "03", t0 + 0.1, t1 - 0.2); big(c, t, "terceiro, a", "entrega", wt("Terceiro") - 0.05, t1 - 0.2)
    for i, (txt, key) in enumerate(ITEMS):
        ts = wt(key) - 0.2; y = 790 + i * 120; al, bl, dy = life(t, ts, t1 - 0.2, 0.4)
        if al <= 0: continue
        put(c, check_icon(clamp((t - ts) / 0.5)), 180, y + dy, al)
        put(c, text_img(txt, F("Montserrat-SemiBold", 48), INK + (255,)), 240, y + dy, al, bl, anchor="l")

def sc_vale(c, t):
    t0, t1 = SC_VALE
    pa = smooth((t - t0) / 0.6) * (1 - smooth((t - t1 + 0.3) / 0.4))
    lay = plan_layer(1.0, 0.16 * pa, 115, 300, 8.5, GREEN, labels=0); c.paste(lay, (0, 0), lay)
    show(c, t, text_img("sem pressa", F("DMSerifDisplay-Regular", 150), INK + (255,), shadow=0.15), W / 2, 560, wt("pressa") - 0.35, t1 - 0.3)
    show(c, t, text_img("+ planejamento", F("DMSerifDisplay-Regular", 130), INK + (255,), shadow=0.15), W / 2, 760, wt("planeja") - 0.1, t1 - 0.3)
    v0 = wt("vale") - 0.1
    if t >= v0:
        accent(c, t, "VALE A PENA", W / 2, 1050, v0, t1 - 0.3, 130)
        d = ImageDraw.Draw(c, "RGBA"); p = ease_out((t - v0 - 0.3) / 0.4)
        if p > 0: d.line([(W / 2 - 380 * p, 1135), (W / 2 + 380 * p, 1135)], fill=INK + (200,), width=4)

FOTO = Image.open(KIT / "assets" / "corretor" / "eliezio_recorte.png").convert("RGBA")   # recorte da foto do Eliezio (sem fundo)
def sc_fim(c, t):
    t0, t1 = SC_FIM
    # foto entra subindo de baixo, com sombra suave; topo da cabeça sempre com folga
    p = ease_out((t - t0 - 0.2) / 0.8)
    if p > 0:
        sh = Image.new("RGBA", FOTO.size, (0, 0, 0, 255)); sh.putalpha(FOTO.getchannel("A").point(lambda v: int(v * 0.35 * p)))
        y = 960 + 140 * (1 - p)
        sh = sh.filter(ImageFilter.GaussianBlur(18)); c.paste(sh, (int(W / 2 - FOTO.width / 2 + 14), int(y + 10)), sh)
        put(c, FOTO, W / 2, y + FOTO.height / 2, p, (1 - p) * 10)
    big(c, t, "qualquer dúvida,", "me chama.", t0 + 0.05, DUR, y=350, size=180)
    s = t0 + 0.8; d = ImageDraw.Draw(c, "RGBA")
    lw = 300 * ease_out((t - s) / 0.5)
    if lw > 1: d.line([(W / 2 - lw, 505), (W / 2 + lw, 505)], fill=GREEN + (255,), width=4)
    show(c, t, text_img("Corretor Eliezio", F("DMSerifDisplay-Regular", 84), INK + (255,)), W / 2, 590, s + 0.1, DUR)
    show(c, t, text_img("CRECI-SP 209.709", F("Montserrat-SemiBold", 34), INK + (170,), spacing=5), W / 2, 675, s + 0.25, DUR)
    al, bl, dy = life(t, s + 0.45, DUR)
    if al > 0:
        tel = text_img("(11) 94087-3190", F("Montserrat-ExtraBold", 68), GREEN + (255,))
        put(c, phone_icon(), W / 2 - tel.width / 2 - 10, 785 + dy, al, bl)
        put(c, tel, W / 2 + 35, 785 + dy, al, bl)
    show(c, t, text_img("eliezioimoveis.com.br  ·  ezbrokers.com.br", F("Montserrat-SemiBold", 32), INK + (210,)), W / 2, 880, s + 0.65, DUR)
    show(c, t, text_img("@eliezio.corretordeimoveis  ·  @ezbrokers", F("Montserrat-SemiBold", 32), (255, 255, 255, 235), shadow=0.5), W / 2, 1790, s + 0.9, DUR)

SCENES = [(SC_HOOK, sc_hook), (SC_TRES, sc_tres), (SC_PRECO, sc_preco), (SC_TEMPO, sc_tempo), (SC_ENTREGA, sc_entrega), (SC_VALE, sc_vale), (SC_FIM, sc_fim)]

# legenda de uma palavra
CAP_FONT = F("Montserrat-SemiBold", 62)
def caption(c, t):
    if t >= SC_FIM[0]: return
    for w, a, b in WORDS:
        if a - 0.02 <= t < b + 0.06:
            im = text_img(w, CAP_FONT, INK + (255,)); p = ease_out((t - a + 0.02) / 0.12)
            pad = Image.new("RGBA", (im.width + 20, im.height), (0, 0, 0, 0)); pad.alpha_composite(im, (10, 0))
            d = ImageDraw.Draw(c, "RGBA"); bw = im.width - 30
            d.rounded_rectangle([W / 2 - bw / 2 - 26, 1585 - 50, W / 2 + bw / 2 + 26, 1585 + 50], 50, fill=(255, 255, 255, int(200 * p)))
            put(c, im, W / 2, 1585, p, (1 - p) * 6); return

def frame(t):
    c = BGIMG.copy()
    for (a, b), fn in SCENES:
        if a - 0.05 <= t <= b + 0.35: fn(c, t)
    chrome(c, t); caption(c, t)
    arr = np.asarray(c)
    for tb in BLUR_AT:                               # transição com desfoque (0,5 s)
        x = (t - tb) / 0.25
        if -1 < x < 1:
            s = 16 * math.cos(x * math.pi / 2) ** 2
            if s > 0.5: arr = cv2.GaussianBlur(arr, (0, 0), s)
    return arr

# ---------- áudio: voz tratada, trilha com ducking e efeitos ----------
def audio():
    subprocess.run(["python3", str(KIT / "scripts" / "music.py"), str(TMP / "music.wav"), f"{DUR:.2f}"], check=True)
    W_, R, C = sfx.whoosh, sfx.thud, sfx.click
    ev = [(0.05, W_(0.5), 0.35), (wt("cilada") - 0.05, R(), 0.55)]
    ev += [(T(5.65) + i * 0.28, C(seed=11 + i), 0.35) for i in range(3)]
    ev += [(tb - 0.25, W_(0.5), 0.30) for tb in BLUR_AT]
    ev += [(wt("Na", 8.0) + 0.15, sfx.paper(), 0.25), (wt("pronto") - 0.15, sfx.paper(), 0.25), (wt("barato") - 0.1, C(seed=21), 0.35)]
    ev += [(wt("entrada") + 0.35 + i * 0.17, C(seed=30 + i), 0.12) for i in range(12)]
    ev += [(wt("dois") - 0.1, R(), 0.35), (wt("não", 21.0) - 0.05, R(), 0.45)]
    ev += [(wt(k) - 0.2, sfx.marker(0.45), 0.18) for _, k in ITEMS]
    ev += [(wt("vale") - 0.1, R(), 0.6), (SC_FIM[0] + 0.5, sfx.hope(2.6), 0.30)]
    sfx.build(ev, DUR, str(TMP / "sfx.wav"))
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", VOICE, "-af", f"adelay={int(LEAD*1000)}|{int(LEAD*1000)},highpass=f=80,acompressor=threshold=-18dB:ratio=2.5:attack=8:release=120,loudnorm=I=-15:TP=-2:LRA=9",
                    "-ar", "48000", "-ac", "2", str(TMP / "voz.wav")], check=True)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", str(TMP / "voz.wav"), "-i", str(TMP / "music.wav"), "-i", str(TMP / "sfx.wav"),
                    "-filter_complex",
                    "[0:a]asplit=2[sc][v1];[1:a]volume=0.30[m];[m][sc]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[md];"
                    "[md][v1][2:a]amix=inputs=3:normalize=0:weights=1 1 0.9,alimiter=limit=0.89[out]",
                    "-map", "[out]", "-t", f"{DUR:.2f}", str(TMP / "mix.wav")], check=True)

if PREVIEW:
    for s in PREVIEW: Image.fromarray(frame(s)).save(TMP / f"prev_{s:05.2f}.jpg", quality=88)
    sys.exit()
audio()
p = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-i", str(TMP / "mix.wav"), "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                      "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
for i in range(int(DUR * FPS)):
    p.stdin.write(frame(i / FPS).tobytes())
p.stdin.close(); p.wait()
