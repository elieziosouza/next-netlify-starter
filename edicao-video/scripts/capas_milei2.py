"""Capa B (escolhida) refeita: clima de terror. Milei com a motosserra (foto Gage Skidmore, CC BY-SA 2.0) e Flávio em P&B (debate da Band),
fundo escuro com brilho vermelho só na imagem, grão e vinheta; ele embaixo com o rosto inteiro."""
import sys, importlib.util
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
S = sys.argv[1]
spec = importlib.util.spec_from_file_location("rm", f"{S}/work/render_milei.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
W, H, CX = R.W, R.H, R.CX; YEL = (255, 214, 0); WHITE = (255, 255, 255); BLUE = (14, 62, 120); BAR = R.BAR; V = M.V
MIL = np.asarray(Image.open(f"{V}/img/milei.jpg").convert("RGB"))[20:640, 280:800]
FLA = np.asarray(Image.open(f"{V}/img/flavio.png").convert("RGB"))[440:1090, 100:576]
def terror(a, red=0.0, bw=False):
    f = a.astype(np.float32) / 255
    if bw: f = np.repeat(f.mean(2, keepdims=True), 3, 2)
    f = np.clip((f - 0.08) * 1.25, 0, 1) ** 1.15                         # contraste e pretos fundos
    y = f.mean(2, keepdims=True); f = f * 0.75 + y * 0.25                 # cor mais fria e lavada
    f = f * (1 - red) + f * np.array([1.25, 0.72, 0.68]) * red
    return (np.clip(f, 0, 1) * 255).astype(np.uint8)
def word(img, txt, cy, size, col, sw=12, rot=0, band=None, tcol=None, maxw=820):
    f = R.BIGF(size)
    while f.getlength(txt) > maxw: size -= 4; f = R.BIGF(size)
    tw = f.getlength(txt); h = int(size * 1.25)
    lay = Image.new("RGBA", (int(tw + 90), h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if band: d.rounded_rectangle((0, 6, lay.width - 1, h + 12), 16, fill=band + (255,), outline=R.GOLD + (255,), width=4)
    d.text((lay.width / 2, lay.height / 2 + 4), txt, font=f, fill=(tcol or col) + (255,), anchor="mm", stroke_width=0 if band else sw, stroke_fill=(0, 0, 0, 255))
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    R.paste(img, lay, CX - lay.width / 2, cy - lay.height / 2, 0.8, 18, (6, 14))
def photo(img, src, w, x, y, rot=0, glow=None):
    p = cv2.resize(src, (w, int(w * src.shape[0] / src.shape[1])), interpolation=cv2.INTER_LANCZOS4)
    c = Image.fromarray(R.rounded(p, 24, 4))
    if rot: c = c.rotate(rot, resample=Image.BICUBIC, expand=True)
    if glow:
        g = Image.new("RGBA", (c.width + 160, c.height + 160), (0, 0, 0, 0)); ImageDraw.Draw(g).rounded_rectangle((80, 80, c.width + 80, c.height + 80), 30, fill=glow + (200,))
        img.alpha_composite(g.filter(ImageFilter.GaussianBlur(40)), (int(x - 80), int(y - 80)))
    R.paste(img, c, x, y, 0.8, 26, (10, 26)); return c
# fundo: escuro com névoa vermelha
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
base = np.zeros((H, W, 3), np.float32) + [8, 8, 12]
base += np.exp(-(((xx - 640) / 520) ** 2 + ((yy - 820) / 520) ** 2))[..., None] * [110, 14, 10]
base += np.random.default_rng(3).normal(0, 1, (H // 8, W // 8)).repeat(8, 0).repeat(8, 1)[..., None] * 3
img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")
photo(img, terror(FLA, bw=True), 430, CX - 455, 500, rot=-3)
photo(img, terror(MIL, red=0.25), 430, CX + 15, 470, rot=3, glow=(150, 20, 15))
# ele embaixo (rosto inteiro)
me, idx = M.graded(44.0); m = me[200:1650]; top = 1250; ph = H - top; fw = int(m.shape[1] * ph / m.shape[0])
fg = cv2.resize(terror(m, red=0.08), (fw, ph), interpolation=cv2.INTER_AREA); x0 = CX - fw // 2
lay = np.zeros((ph, W, 4), np.uint8); lay[:, x0:x0 + fw, :3] = fg
al = np.ones((ph, fw), np.float32); al[:120] *= np.linspace(0, 1, 120)[:, None]; al[:, :70] *= np.linspace(0, 1, 70)[None]; al[:, -70:] *= np.linspace(1, 0, 70)[None]
lay[:, x0:x0 + fw, 3] = (al * 255).astype(np.uint8); img.alpha_composite(Image.fromarray(lay), (0, top))
# vinheta e grão
v = np.clip(1 - (((xx - CX) / 760) ** 2 + ((yy - 960) / 1150) ** 2), 0, 1) ** 0.6
arr = np.asarray(img.convert("RGB")).astype(np.float32) * (0.35 + 0.65 * v[..., None])
arr += np.random.default_rng(7).normal(0, 9, (H, W, 1))
img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
word(img, "A MOTOSSERRA", 190, 160, WHITE); word(img, "VAI CHEGAR AQUI?", 350, 130, YEL)
word(img, "O QUE ELA FEZ NA ARGENTINA", 1255, 74, WHITE, band=BLUE, tcol=WHITE, rot=-2)
ImageDraw.Draw(img).text((CX, 1172), "Fotos: Gage Skidmore (CC BY-SA 2.0) · TV Band", font=R.MF("SemiBold", 20), fill=(210, 210, 215, 220), anchor="mm")
BAR.draw_bar(img, 0.0, "canal"); img.alpha_composite(R.top, (R.HDX, 0)); img.convert("RGB").save(f"{V}/capa_B2.jpg", quality=95)
