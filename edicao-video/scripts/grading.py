import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
FD = "/home/user/next-netlify-starter/edicao-video/assets/fonts"
x_ = np.arange(256) / 255.0

def current(img):
    s = np.clip(x_ + 0.16 * (x_ - 0.5) * (1 - abs(2 * x_ - 1)), 0, 1)
    c = lambda lo, hi: np.clip((s + lo * (1 - x_) ** 2.2 + hi * x_ ** 2.2) * 255, 0, 255).astype(np.uint8)
    L = np.stack([c(-0.010, 0.022), c(0.003, 0.010), c(0.026, -0.015)], 1)[:, None, :]
    return cv2.LUT(img, L)

def skin_mask(f):
    hsv = cv2.cvtColor((f * 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    h, s, v = hsv[..., 0], hsv[..., 1] / 255, hsv[..., 2] / 255
    m = np.clip(1 - np.abs(h - 12) / 12, 0, 1) * np.clip((s - 0.12) / 0.1, 0, 1) * np.clip((s - 0.75) / -0.1, 0, 1) * np.clip((v - 0.2) / 0.15, 0, 1)
    return (cv2.GaussianBlur(m, (0, 0), 3) if BLUR_SKIN else m)[..., None]

BLUR_SKIN = True
def lum(f): return (f * [0.2126, 0.7152, 0.0722]).sum(2, keepdims=True)

def tone(f, strength, pivot=0.45, black=0.0, white=1.0):
    """curva S suave em luminância, ombro que segura os claros"""
    y = lum(f); t = y
    t = np.where(t < pivot, pivot * (t / pivot) ** (1 + strength), 1 - (1 - pivot) * ((1 - t) / (1 - pivot)) ** (1 + strength * 0.7))
    t = black + t * (white - black)
    return np.clip(f * (t / np.maximum(y, 1e-4)), 0, 1), y

def split(f, y, shadow, high, amt=1.0):
    ws = np.clip(1 - y / 0.5, 0, 1) ** 1.5; wh = np.clip((y - 0.5) / 0.5, 0, 1) ** 1.5
    return np.clip(f + amt * (ws * np.array(shadow) + wh * np.array(high)), 0, 1)

def sat(f, k, skin=None, skin_k=None):
    y = lum(f); out = y + (f - y) * k
    if skin is not None: out = out * (1 - skin) + (y + (f - y) * skin_k) * skin
    return np.clip(out, 0, 1)

def clarity(f, k, r=10):
    y = lum(f); d = y - cv2.GaussianBlur(y[..., 0], (0, 0), r)[..., None]
    return np.clip(f + k * d, 0, 1)

def tame_green(f, k):
    hsv = cv2.cvtColor((f * 255).astype(np.uint8), cv2.COLOR_RGB2HSV).astype(np.float32)
    m = np.clip(1 - np.abs(hsv[..., 0] - 62) / 28, 0, 1)[..., None]
    y = lum(f); return np.clip(f * (1 - m * k) + (y + (f - y) * 0.35) * m * k, 0, 1)

def premium(img):          # B: limpo de telejornal premium
    f = img.astype(np.float32) / 255; sk = skin_mask(f)
    f = np.clip(f * [0.985, 1.0, 1.02], 0, 1)                         # tira o amarelado da parede
    f, y = tone(f, 0.18, 0.45, 0.008, 0.975)
    f = split(f, y, [-0.008, 0.0, 0.016], [0.012, 0.006, -0.006])
    f = tame_green(f, 0.55); f = clarity(f, 0.12, 6)
    f = sat(f, 1.04, sk, 0.96)
    return (f * 255).astype(np.uint8)

def cinema(img):           # C: cinema marinho e dourado (cores do canal)
    f = img.astype(np.float32) / 255; sk = skin_mask(f)
    f = tame_green(f, 0.85)
    f, y = tone(f, 0.30, 0.42, 0.012, 0.965)
    f = split(f, y, [-0.025, 0.01, 0.05], [0.03, 0.016, -0.02])
    f = sat(f, 0.8, sk, 1.08); f = clarity(f, 0.1, 6)
    f = f * (1 - sk * 0.12) + (f * [1.03, 1.0, 0.97]) * sk * 0.12
    return (np.clip(f, 0, 1) * 255).astype(np.uint8)

def investig(img):         # D: documentário investigativo
    f = img.astype(np.float32) / 255; sk = skin_mask(f)
    f = tame_green(f, 0.9)
    f, y = tone(f, 0.30, 0.45, 0.05, 0.94)                           # preto fosco
    f = split(f, y, [-0.015, 0.01, 0.04], [0.0, 0.005, 0.01])
    f = sat(f, 0.65, sk, 0.8); f = clarity(f, 0.16, 6)
    return (np.clip(f, 0, 1) * 255).astype(np.uint8)

GRADES = [("ATUAL", current), ("B · PREMIUM LIMPO", premium), ("C · CINEMA AZUL E DOURADO", cinema), ("D · DOCUMENTÁRIO", investig)]
if __name__ == "__main__":
    me = cv2.cvtColor(cv2.imread("me.png"), cv2.COLOR_BGR2RGB); fl = cv2.cvtColor(cv2.imread("fl.png"), cv2.COLOR_BGR2RGB)
    me = cv2.resize(me, (420, 747), interpolation=cv2.INTER_AREA); fl = cv2.resize(fl, (420, 389), interpolation=cv2.INTER_AREA)
    f = ImageFont.truetype(f"{FD}/Montserrat-ExtraBold.ttf", 22)
    sheet = Image.new("RGB", (4 * 430 + 10, 747 + 389 + 70), (6, 14, 26)); d = ImageDraw.Draw(sheet)
    for i, (name, fn) in enumerate(GRADES):
        x = 10 + i * 430
        d.text((x + 210, 28), name, font=f, fill=(214, 182, 116), anchor="mm")
        sheet.paste(Image.fromarray(fn(me)), (x, 55)); sheet.paste(Image.fromarray(fn(fl)), (x, 55 + 747 + 10))
    sheet.save("comparativo_grading.jpg", quality=92)

def no_clarity(f, k, r=10): return f
def bake(fn, path):
    """grava a parte por pixel do grading numa tabela 256^3 (a clareza fica fora, é espacial)"""
    import os
    if os.path.exists(path): return np.load(path)
    global BLUR_SKIN, clarity
    BLUR_SKIN = False; keep = clarity; clarity = no_clarity
    idx = np.arange(256 ** 3, dtype=np.uint32); lut = np.empty((256 ** 3, 3), np.uint8)
    for c in range(0, 256 ** 3, 1 << 20):
        i = idx[c:c + (1 << 20)]
        img = np.stack([(i >> 16) & 255, (i >> 8) & 255, i & 255], 1).astype(np.uint8).reshape(1024, 1024, 3)
        lut[c:c + (1 << 20)] = fn(img).reshape(-1, 3)
    BLUR_SKIN = True; clarity = keep
    np.save(path, lut); return lut

class Fast:
    def __init__(self, fn, path, clar=0.1, r=6):
        self.lut = bake(fn, path); self.clar = clar; self.r = r
    def __call__(self, a, r=None):
        a = np.ascontiguousarray(a)
        i = (a[..., 0].astype(np.uint32) << 16) | (a[..., 1].astype(np.uint32) << 8) | a[..., 2]
        out = self.lut[i]
        if self.clar:
            y = cv2.cvtColor(out, cv2.COLOR_RGB2GRAY).astype(np.float32)
            d = (y - cv2.GaussianBlur(y, (0, 0), r or self.r)) * self.clar
            out = np.clip(out.astype(np.float32) + d[..., None], 0, 255).astype(np.uint8)
        return out
