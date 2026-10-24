# Recursos de storymaker para o story_aaa.py: texto atrás da pessoa, letras animadas, "clique da foto"
# (congela, flash, vira foto com borda), vazamento de luz, pulso na batida, brilho de cinema e granulação.
import os, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, SR = 1080, 1920, 48000
ease = lambda u: u * u * (3 - 2 * u)
rng = np.random.default_rng(5)

# ---------------- som ----------------
def obturador():
    """Clique de câmera: espelho subindo, cortina, espelho descendo (sintetizado, sem direitos)."""
    n = int(0.16 * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for t0, g, dec in [(0.0, 1.0, 900), (0.012, 0.5, 300), (0.075, 0.8, 700), (0.085, 0.35, 250)]:
        i0 = int(t0 * SR); m = n - i0; tt = np.arange(m) / SR
        r = rng.normal(0, 1, m); r = np.diff(r, prepend=0)
        x[i0:] += g * r * np.exp(-tt * dec)
    corpo = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 60) * 0.25
    x = (x + corpo); x /= np.abs(x).max() + 1e-9
    return np.stack([x, x], 1) * 0.5

def swish(dur=0.5):
    n = int(dur * SR); t = np.arange(n) / SR; p = t / dur
    x = rng.normal(0, 1, n); x = np.diff(x, prepend=0)
    k = 64; x = np.convolve(x, np.ones(k) / k, 'same')     # ar macio
    env = np.sin(np.pi * p) ** 2
    pan = p
    x = x / (np.abs(x).max() + 1e-9) * env
    return np.stack([x * (1 - 0.6 * pan), x * (0.4 + 0.6 * pan)], 1) * 0.6

# ---------------- acabamento de imagem ----------------
GRAO = [(rng.normal(0, 1, (H // 2, W // 2)) * 255).astype(np.float32) for _ in range(6)]

def cinema(fr, i, grao=3.2, brilho=0.16):
    """Brilho suave nos claros (bloom) + granulação fina de filme."""
    pq = cv2.resize(fr, (W // 4, H // 4), interpolation=cv2.INTER_AREA).astype(np.float32)
    claro = np.clip(pq - 185, 0, None) * 2.6
    bl = cv2.GaussianBlur(claro, (0, 0), 9)
    bl = cv2.resize(bl, (W, H), interpolation=cv2.INTER_LINEAR)
    f = fr.astype(np.float32)
    f = 255 - (255 - f) * (1 - np.clip(bl * brilho / 255, 0, 0.6))        # screen
    g = cv2.resize(GRAO[i % len(GRAO)], (W, H), interpolation=cv2.INTER_LINEAR) / 255 * grao
    L = f.mean(2, keepdims=True) / 255
    f += g[..., None] * (0.6 + 0.8 * L * (1 - L) * 4) * 0.5             # grão mais visível nos meios-tons
    return np.clip(f, 0, 255).astype(np.uint8)

def pulso(fr, forca):
    """Batida: brilho rápido (o zoom do pulso é aplicado junto com o zoom da cena)."""
    if forca <= 0.01: return fr
    return cv2.convertScaleAbs(fr, alpha=1 + 0.07 * forca, beta=4 * forca)

def vazamento(fr, p, semente=0):
    """Vazamento de luz quente atravessando a tela. p de 0 a 1 ao longo da transição."""
    a = np.sin(np.pi * np.clip(p, 0, 1)) ** 1.3
    if a < 0.01: return fr
    w, h = W // 8, H // 8; yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    r = np.random.default_rng(semente)
    lz = np.zeros((h, w, 3), np.float32)
    for cor, rx, ry, vel, y0 in [((80, 150, 255), 0.55, 0.35, 1.4, r.uniform(0.2, 0.5)),
                                 ((120, 90, 255), 0.40, 0.30, 1.0, r.uniform(0.5, 0.8)),
                                 ((140, 210, 255), 0.30, 0.22, 1.8, r.uniform(0.1, 0.9))]:
        cx = (-0.4 + 1.8 * p * vel / 1.4) * w; cy = y0 * h
        g = np.exp(-(((xx - cx) / (rx * w)) ** 2 + ((yy - cy) / (ry * h)) ** 2))
        lz += g[..., None] * np.array(cor, np.float32)                     # BGR
    lz = cv2.resize(lz, (W, H), interpolation=cv2.INTER_LINEAR) * a * 0.95
    f = fr.astype(np.float32)
    return np.clip(255 - (255 - f) * (1 - np.clip(lz / 255, 0, 1)), 0, 255).astype(np.uint8)

# ---------------- clique da foto ----------------
def foto(base, p, angulo=-4.0):
    """Quadro congelado vira foto com borda branca e sombra, sobre o próprio quadro desfocado. p de 0 a 1."""
    q = ease(min(1, p / 0.35))
    fundo = cv2.GaussianBlur(base, (0, 0), 2 + 16 * q)
    fundo = cv2.convertScaleAbs(fundo, alpha=1 - 0.45 * q)
    s = 1 - 0.2 * q; ang = angulo * q; borda = int(26 * q)
    cw, ch = int(W * s), int(H * s)
    img = cv2.resize(base, (cw, ch), interpolation=cv2.INTER_AREA)
    if borda: img = cv2.copyMakeBorder(img, borda, borda * 3, borda, borda, cv2.BORDER_CONSTANT, value=(250, 250, 248))
    hh, ww = img.shape[:2]
    alpha = np.full((hh, ww), 255, np.uint8)
    M = cv2.getRotationMatrix2D((ww / 2, hh / 2), ang, 1.0)
    M[0, 2] += W / 2 - ww / 2; M[1, 2] += H / 2 - hh / 2 + 30 * q
    card = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR)
    am = cv2.warpAffine(alpha, M, (W, H), flags=cv2.INTER_LINEAR).astype(np.float32) / 255
    sombra = cv2.GaussianBlur(np.roll(am, (22, 12), (0, 1)), (0, 0), 22) * 0.55 * q
    out = fundo.astype(np.float32) * (1 - sombra[..., None])
    out = out * (1 - am[..., None]) + card.astype(np.float32) * am[..., None]
    if p < 0.12: out = out + (255 - out) * (1 - p / 0.12) * 0.85              # flash
    return np.clip(out, 0, 255).astype(np.uint8)

# ---------------- lettering animado ----------------
def letras(texto, fonte, tam, cor=(255, 255, 255), sombra=True, largura_max=W - 80, espaco=0):
    """Sprites de cada letra (RGBA float) e posição x, numa faixa. Devolve (sprites, altura_da_faixa)."""
    while True:
        f = ImageFont.truetype(fonte, tam); tmp = ImageDraw.Draw(Image.new('L', (1, 1)))
        larg = [tmp.textlength(ch, font=f) for ch in texto]; tw = sum(larg) + espaco * (len(texto) - 1)
        if tw <= largura_max or tam < 40: break
        tam = int(tam * 0.95)
    asc, desc = f.getmetrics(); hb = asc + desc + 40
    x = (W - tw) / 2; out = []
    for ch, lw in zip(texto, larg):
        if ch.strip():
            im = Image.new('RGBA', (int(lw) + 60, hb), (0, 0, 0, 0))
            if sombra:
                s = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(s).text((30, 24), ch, font=f, fill=(0, 0, 0, 110))
                im = Image.alpha_composite(im, s.filter(ImageFilter.GaussianBlur(10)))
            ImageDraw.Draw(im).text((30, 20), ch, font=f, fill=cor + (255,))
            out.append((np.array(im).astype(np.float32) / 255, x - 30))
        x += lw + espaco
    return out, hb, tam

def camada_letras(sprites, hb, t, t0, passo=0.045, dur=0.42, subida=36):
    """Faixa RGBA (hb x W) com as letras entrando uma a uma (sobe + aparece)."""
    faixa = np.zeros((hb, W, 4), np.float32)
    for k, (sp, x) in enumerate(sprites):
        u = (t - t0 - k * passo) / dur
        if u <= 0: continue
        u = ease(min(1, u)); dy = int(subida * (1 - u))
        h, w = sp.shape[:2]; x0 = int(round(x)); xa, xb = max(0, x0), min(W, x0 + w)
        if xb <= xa: continue
        src = sp[max(0, -dy):h - max(0, dy), xa - x0:xb - x0]; y0 = max(0, dy)
        reg = faixa[y0:y0 + src.shape[0], xa:xb]
        al = src[..., 3:4] * u
        reg[..., :3] = reg[..., :3] * (1 - al) + src[..., :3] * al
        reg[..., 3:4] = reg[..., 3:4] * (1 - al) + al
    return faixa

def aplica_faixa(fr, faixa, y, alfa=1.0, mascara=None):
    """Cola a faixa no quadro em y. Com máscara de pessoa (0..1, H x W), o texto fica atrás dela."""
    hb = faixa.shape[0]; y0, y1 = max(0, y), min(H, y + hb)
    if y1 <= y0: return fr
    f = faixa[y0 - y:y1 - y]; al = f[..., 3:4] * alfa
    if mascara is not None: al = al * (1 - mascara[y0:y1, :, None])
    reg = fr[y0:y1].astype(np.float32)
    fr[y0:y1] = (reg * (1 - al) + f[..., :3] * 255 * al).astype(np.uint8)
    return fr

# ---------------- recorte da pessoa ----------------
class Pessoa:
    def __init__(self, modelo):
        import onnxruntime as ort
        o = ort.SessionOptions(); o.intra_op_num_threads = 4
        self.s = ort.InferenceSession(modelo, o, providers=['CPUExecutionProvider']); self.inp = self.s.get_inputs()[0].name
    def __call__(self, bgr):
        x = cv2.resize(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB), (320, 320), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
        x = ((x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]).transpose(2, 0, 1)[None].astype(np.float32)
        m = self.s.run(None, {self.inp: x})[0][0, 0]; m = (m - m.min()) / (m.max() - m.min() + 1e-6)
        m = cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR)
        m = np.clip((m - 0.35) / 0.3, 0, 1)
        return cv2.GaussianBlur(m, (0, 0), 2.5)

def linhas_letras(sprites):
    """Primeira e última linha (dentro da faixa) onde há tinta das letras."""
    a = np.max([sp[..., 3].max(1) for sp, _ in sprites], 0); r = np.where(a > 0.5)[0]
    return int(r[0]), int(r[-1])

def faixa_atras(mascara, hb, topo_min=230, letras=None):
    """y da faixa de texto atrás da pessoa: a cabeça cobre a metade de baixo das letras (dá profundidade e
    ainda deixa ler). Sem subir para a área do Instagram. None se não houver cabeça clara no quadro."""
    larg = (mascara > 0.5).sum(1); r = np.where(larg > 40)[0]
    if len(r) == 0: return None
    topo = int(r[0]); l0, l1 = letras if letras else (int(hb * 0.22), int(hb * 0.78))
    y = int(topo + 0.5 * (l1 - l0) - l1)
    if y + l0 < topo_min or topo > H * 0.6: return None
    return y
