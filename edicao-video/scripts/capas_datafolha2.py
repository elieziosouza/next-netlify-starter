"""Capas do corte Datafolha (CNN, 22/10): ele analisando, mão no queixo, e a repórter da CNN."""
import sys, io, subprocess, importlib.util
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; V = f"{S}/v51"
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
W, H = R.W, R.H; BAR = R.BAR; CX = R.CX; YEL = (255, 214, 0); WHITE = (255, 255, 255); BLUE = (14, 62, 120)
def grab(path, t, crop=None):
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", path, "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    a = np.asarray(Image.open(io.BytesIO(p)).convert("RGB")); return a if crop is None else a[crop[1]:crop[3], crop[0]:crop[2]]
def word(img, txt, cy, size, col, stroke=R.NAVY, sw=12, rot=0, band=None, tcol=None, maxw=720):
    f = R.BIGF(size)
    while f.getlength(txt) > maxw: size -= 4; f = R.BIGF(size)
    tw = f.getlength(txt); h = int(size * 1.25)
    lay = Image.new("RGBA", (int(tw + 90), h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if band: d.rounded_rectangle((0, 6, lay.width - 1, h + 12), 16, fill=band + (255,))
    d.text((lay.width / 2, lay.height / 2 + 4), txt, font=f, fill=(tcol or col) + (255,), anchor="mm", stroke_width=0 if band else sw, stroke_fill=stroke + (255,))
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    R.paste(img, lay, CX - lay.width / 2, cy - lay.height / 2, 0.7, 18, (6, 14))
def photo(img, src, w, x, y, rad=26):
    c = Image.fromarray(R.rounded(cv2.resize(cv2.LUT(src, R.LUT), (w, int(w * src.shape[0] / src.shape[1])), interpolation=cv2.INTER_LANCZOS4), rad, 5)); R.paste(img, c, x, y, 0.6, 22, (8, 20)); return c
def base(src, k=0.3): return Image.fromarray(np.clip(R.blur_bg(src, k), 0, 255).astype(np.uint8)).convert("RGBA")
def finish(img, name):
    BAR.draw_bar(img, 0.0, "canal"); img.alpha_composite(R.top, (R.HDX, 0)); img.convert("RGB").save(f"{V}/{name}.jpg", quality=95)
ME = grab(f"{V}/in.mp4", 6.0)                                          # ele, 1080x1920
CNN = grab(f"{V}/cl.mp4", 2.0, (0, 0, 1080, 1242))
def scene(src_me, dy=40):
    img = Image.fromarray(np.zeros((H, W, 3), np.uint8)).convert("RGBA"); m = cv2.LUT(src_me, R.LUT)
    a = np.zeros((H, W, 3), np.uint8); a[:] = m[0:1].mean(axis=(0, 1)).astype(np.uint8); a[dy:] = m[:H - dy]
    img = Image.fromarray(a).convert("RGBA")
    g = np.zeros((600, W, 4), np.uint8); g[..., :3] = (4, 14, 28); g[..., 3] = np.linspace(235, 0, 600)[:, None].astype(np.uint8); img.alpha_composite(Image.fromarray(g))
    g2 = np.zeros((700, W, 4), np.uint8); g2[..., :3] = (4, 14, 28); g2[..., 3] = np.linspace(0, 235, 700)[:, None].astype(np.uint8); img.alpha_composite(Image.fromarray(g2), (0, H - 700))
    return img
def cnn_card(img, w, y, rot=-2):
    c = Image.fromarray(R.rounded(cv2.resize(cv2.LUT(CNN, R.LUT), (w, int(w * CNN.shape[0] / CNN.shape[1])), interpolation=cv2.INTER_LANCZOS4), 24, 5)).rotate(rot, resample=Image.BICUBIC, expand=True)
    R.paste(img, c, CX - c.width / 2, y, 0.65, 24, (10, 26)); return c
LULA = np.asarray(Image.open(f"{V}/full49.png").convert("RGB"))[440:1090, 0:430]
FLAV = np.asarray(Image.open(f"{V}/full53.7.png").convert("RGB"))[440:1090, 146:576]
FLAV_BW = cv2.cvtColor(cv2.cvtColor(FLAV, cv2.COLOR_RGB2GRAY), cv2.COLOR_GRAY2RGB)
def me_bottom(img, top):                                             # ele embaixo, de ponta a ponta, com fusão em cima e nas laterais
    m = cv2.LUT(ME, R.LUT)[200:1650]; ph = H - top; fw = int(m.shape[1] * ph / m.shape[0])
    fg = cv2.resize(m, (fw, ph), interpolation=cv2.INTER_AREA); x0 = CX - fw // 2
    bgp = cv2.resize(cv2.GaussianBlur(cv2.resize(m, (W // 10, ph // 10)), (0, 0), 2.5), (W, ph)).astype(np.float32) * 0.65
    fm = np.ones((ph, fw), np.float32); fm[:, :60] = np.linspace(0, 1, 60)[None, :]; fm[:, -60:] = np.linspace(1, 0, 60)[None, :]; fm = fm[..., None]
    xs, xe = max(0, x0), min(W, x0 + fw); bgp[:, xs:xe] = bgp[:, xs:xe] * (1 - fm[:, xs - x0:xe - x0]) + fg[:, xs - x0:xe - x0] * fm[:, xs - x0:xe - x0]
    lay = np.zeros((ph, W, 4), np.uint8); lay[..., :3] = bgp.astype(np.uint8)
    al = np.ones((ph, W), np.float32); al[:180] *= np.linspace(0, 1, 180)[:, None]; lay[..., 3] = (al * 255).astype(np.uint8)
    img.alpha_composite(Image.fromarray(lay), (0, top))
def duo(img, y, w=400, flav=FLAV_BW, lab=("LULA 50%", "FLÁVIO 50%")):
    a = photo(img, LULA, w, CX - w - 18, y); photo(img, flav, w, CX + 18, y + 30)
    d = ImageDraw.Draw(img); r = 78; cy = y + a.height // 2 + 15
    d.ellipse((CX - r, cy - r, CX + r, cy + r), fill=YEL + (255,), outline=R.NAVY + (255,), width=8); d.text((CX, cy + 4), "X", font=R.BIGF(110), fill=R.NAVY + (255,), anchor="mm")
    for txt, cx, col, tc, yy in ((lab[0], CX - w / 2 - 18, YEL, R.NAVY, y + a.height - 10), (lab[1], CX + w / 2 + 18, R.NAVY, WHITE, y + a.height + 20)):
        f = R.BIGF(64); tw = f.getlength(txt); lay = Image.new("RGBA", (int(tw + 50), 92), (0, 0, 0, 0)); dd = ImageDraw.Draw(lay)
        dd.rounded_rectangle((0, 0, lay.width - 1, 91), 14, fill=col + (255,), outline=R.GOLD + (255,), width=4); dd.text((lay.width / 2, 48), txt, font=f, fill=tc + (255,), anchor="mm")
        R.paste(img, lay, cx - lay.width / 2, yy, 0.6, 14, (4, 10))
    return y + a.height + 120
def navy_bg(): return Image.fromarray(np.clip(R.NAVYBG, 0, 255).astype(np.uint8)).convert("RGBA")
def cred(img): ImageDraw.Draw(img).text((CX, 1868), "Imagens: reprodução TV Band · Pesquisa Datafolha 20 a 22/10", font=R.MF("SemiBold", 22), fill=(225, 225, 232, 230), anchor="mm")
A = navy_bg(); me_bottom(A, 1150); word(A, "EMPATOU!", 190, 210, YEL); word(A, "ATÉ DOMINGO, VIRA!", 345, 96, WHITE, sw=9)
yb = duo(A, 450); word(A, "DATAFOLHA · VOTOS VÁLIDOS", 1225, 64, WHITE, band=BLUE, tcol=WHITE, rot=-2); cred(A); finish(A, "capa_A")
B = navy_bg(); me_bottom(B, 1150); word(B, "LULA EMPATOU", 190, 170, WHITE); word(B, "E VAI VIRAR!", 360, 150, YEL)
duo(B, 470, flav=FLAV); word(B, "DATAFOLHA: 50% × 50%", 1225, 70, R.NAVY, band=YEL, tcol=R.NAVY, rot=-2); cred(B); finish(B, "capa_B")
sheet = Image.new("RGB", (720, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("AB")]
sheet.save(f"{V}/capas_AB.jpg", quality=90)
