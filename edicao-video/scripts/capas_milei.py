"""Capas do corte Milei serve para o Brasil?: ele com a palavra gigante atrás (recorte), emoji da motosserra e os números do Indec."""
import sys, importlib.util
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]
spec = importlib.util.spec_from_file_location("rm", f"{S}/work/render_milei.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
W, H, CX = R.W, R.H, R.CX; YEL = (255, 214, 0); WHITE = (255, 255, 255); BLUE = (14, 62, 120); BAR = R.BAR
def word(img, txt, cy, size, col, sw=12, rot=0, band=None, tcol=None, maxw=820):
    f = R.BIGF(size)
    while f.getlength(txt) > maxw: size -= 4; f = R.BIGF(size)
    tw = f.getlength(txt); h = int(size * 1.25)
    lay = Image.new("RGBA", (int(tw + 90), h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if band: d.rounded_rectangle((0, 6, lay.width - 1, h + 12), 16, fill=band + (255,), outline=R.GOLD + (255,), width=4)
    d.text((lay.width / 2, lay.height / 2 + 4), txt, font=f, fill=(tcol or col) + (255,), anchor="mm", stroke_width=0 if band else sw, stroke_fill=R.NAVY + (255,))
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    R.paste(img, lay, CX - lay.width / 2, cy - lay.height / 2, 0.7, 18, (6, 14))
def behind(x, txt, col, dy=0):
    img, idx = M.graded(x); m = M.person_mask(img, idx)
    sh = np.zeros_like(img); sh[dy:] = img[:H - dy] if dy else img; mm = np.zeros_like(m); mm[dy:] = m[:H - dy] if dy else m
    fr = Image.fromarray(sh).convert("RGBA"); size = 330; f = R.BIGF(size)
    while f.getlength(txt) > 880: size -= 6; f = R.BIGF(size)
    d = ImageDraw.Draw(fr); d.text((CX + 7, 560 + 9), txt, font=f, fill=(0, 0, 0, 120), anchor="mm"); d.text((CX, 560), txt, font=f, fill=col + (255,), anchor="mm", stroke_width=7, stroke_fill=R.NAVY + (255,))
    comp = np.asarray(fr.convert("RGB")).astype(np.float32); out = (comp * (1 - mm) + sh.astype(np.float32) * mm).astype(np.uint8)
    im = Image.fromarray(out).convert("RGBA")
    g = np.zeros((700, W, 4), np.uint8); g[..., :3] = (4, 14, 28); g[..., 3] = np.linspace(0, 230, 700)[:, None].astype(np.uint8); im.alpha_composite(Image.fromarray(g), (0, H - 700))
    g2 = np.zeros((360, W, 4), np.uint8); g2[..., :3] = (4, 14, 28); g2[..., 3] = np.linspace(220, 0, 360)[:, None].astype(np.uint8); im.alpha_composite(Image.fromarray(g2))
    return im
def finish(img, name):
    BAR.draw_bar(img, 0.0, "canal"); img.alpha_composite(R.top, (R.HDX, 0)); img.convert("RGB").save(f"{M.V}/{name}.jpg", quality=95)
def chips(img, y):
    for txt, cx in (("POBREZA 32%", CX - 215), ("DESEMPREGO 7,9%", CX + 200)):
        f = R.BIGF(56); tw = f.getlength(txt); lay = Image.new("RGBA", (int(tw + 44), 84), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.rounded_rectangle((0, 0, lay.width - 1, 83), 14, fill=R.NAVY + (255,), outline=R.GOLD + (255,), width=4); d.text((lay.width / 2, 44), txt, font=f, fill=WHITE + (255,), anchor="mm")
        R.paste(img, lay, cx - lay.width / 2, y, 0.6, 14, (4, 10))
A = behind(44.0, "MOTOSSERRA", R.GOLD_L, 60); word(A, "MILEI NO BRASIL?", 200, 150, WHITE)
M.pop(A, M.emoji("🪚", 210), 900, 1200, 1.0, 99, wob=False); M.pop(A, M.emoji("🇦🇷", 150), 250, 1180, 1.0, 99, wob=False)
word(A, "QUEM PAGA A CONTA?", 1560, 100, R.NAVY, band=YEL, tcol=R.NAVY, rot=-3); chips(A, 1700); finish(A, "capa_A")
B = behind(24.0, " ", R.GOLD_L, 80); word(B, "A MOTOSSERRA", 190, 140, WHITE); word(B, "VAI CHEGAR AQUI?", 340, 120, YEL)
M.pop(B, M.emoji("🪚", 210), 900, 1200, 1.0, 99, wob=False)
word(B, "O QUE ELA FEZ NA ARGENTINA", 1560, 76, WHITE, band=BLUE, tcol=WHITE, rot=-2); chips(B, 1700); finish(B, "capa_B")
sheet = Image.new("RGB", (720, 640)); [sheet.paste(Image.open(f"{M.V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("AB")]
sheet.save(f"{M.V}/capas_AB.jpg", quality=90)
