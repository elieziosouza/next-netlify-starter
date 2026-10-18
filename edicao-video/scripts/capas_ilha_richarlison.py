"""Capas do caso da ilha (A e B com o rosto dele, C sem rosto): foto da ilha, Richarlison e Flávio recortados, título grande.
A frase "na mão grande" vai sempre entre aspas, atribuída ao jogador."""
import sys, importlib.util
import numpy as np, cv2
S = sys.argv[1]; sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("ri", f"{S}/work/render_ilha.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
from PIL import Image, ImageDraw, ImageFilter
W, H = R.W, R.H; MF = R.MF; V = R.V; BAR = R.BAR; CX = 636
def cutout(path, h):
    """pessoa recortada pela máscara, com contorno suave"""
    im = Image.open(path).convert("RGB"); a = np.asarray(im)
    m = R.SEG(cv2.resize(a, (478, 850), interpolation=cv2.INTER_AREA)); m = cv2.resize(m, (a.shape[1], a.shape[0]))
    m = cv2.GaussianBlur(np.clip((m - 0.3) / 0.3, 0, 1).astype(np.float32), (0, 0), 1.5)
    rgba = np.dstack([a, (m * 255).astype(np.uint8)]); out = Image.fromarray(rgba, "RGBA")
    bb = out.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox(); out = out.crop(bb)
    return out.resize((int(out.width * h / out.height), h), Image.LANCZOS)
def glow(im, col=(214, 182, 116), r=10):
    a = im.getchannel("A"); g = Image.new("RGBA", (im.width + 4 * r, im.height + 4 * r), (0, 0, 0, 0))
    edge = Image.new("RGBA", im.size, col + (255,)); edge.putalpha(a); g.alpha_composite(edge, (2 * r, 2 * r))
    g = g.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(4)); g.alpha_composite(im, (2 * r, 2 * r)); return g
def big(img, txt, cy, size, col=R.GOLD_L, band=None, tcol=None, rot=0, stroke=R.NAVY):
    f = R.BIGF(size); d0 = ImageDraw.Draw(Image.new("L", (4, 4)))
    while d0.textlength(txt, font=f) > 680: size -= 4; f = R.BIGF(size)
    tw = d0.textlength(txt, font=f); h = int(size * 1.3)
    lay = Image.new("RGBA", (int(tw + 80), h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if band: d.rounded_rectangle((0, 0, lay.width - 1, h - 1), 18, fill=band + (255,), outline=R.GOLD + (255,), width=5)
    d.text((lay.width / 2, h / 2 + 4), txt, font=f, fill=(tcol or col) + (255,), anchor="mm", stroke_width=0 if band else 9, stroke_fill=stroke + (255,))
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    R.paste(img, lay, CX - lay.width / 2, cy - lay.height / 2, 0.6, 16, (5, 12))
def island_bg(h_top):
    isl = Image.open(f"{R.IMG}/ilha_user.jpg").convert("RGB"); sc = max(W / isl.width, h_top / isl.height)
    isl = isl.resize((int(isl.width * sc) + 1, int(isl.height * sc) + 1), Image.LANCZOS); x0 = int((isl.width - W) * 0.3)
    top = isl.crop((x0, 0, x0 + W, h_top))
    bg = Image.fromarray(np.clip(R.NAVYBG, 0, 255).astype(np.uint8)).convert("RGBA"); bg.paste(top, (0, 0))
    fadeh = 260; grad = Image.linear_gradient("L").resize((W, fadeh)); dark = Image.new("RGBA", (W, fadeh), (4, 14, 30, 255)); dark.putalpha(grad)
    bg.alpha_composite(dark, (0, h_top - fadeh)); return bg
RICH = glow(cutout(f"{R.IMG}/rich_user.jpg", 900)); FLAV = glow(cutout(f"{R.IMG}/flavio_user.jpg", 860))
def duo(img, bottom, wmax=430):
    """os dois lado a lado, sem um cobrir o outro, dentro da área segura (x 200 a 980)"""
    out = []
    for c in (RICH, FLAV):
        sc = min(wmax / c.width, 1.0); out.append(c.resize((int(c.width * sc), int(c.height * sc)), Image.LANCZOS))
    r, f = out; img.alpha_composite(r, (int(CX - 200 - r.width / 2), int(bottom - r.height))); img.alpha_composite(f, (int(CX + 190 - f.width / 2), int(bottom - f.height)))
def credit(img, y): ImageDraw.Draw(img).text((CX, y), "Fotos: reprodução", font=MF("SemiBold", 22), fill=(220, 220, 228, 230), anchor="mm")   # crédito em área livre, sem encostar em nada

# C: sem rosto — ilha em cima, os dois embaixo, título no meio
C = island_bg(1000)
duo(C, H + 30, 400)
big(C, "RICHARLISON", 760, 190); big(C, "ACUSA FLÁVIO", 930, 130, band=R.NAVY, tcol=R.WHITE); big(C, "“NA MÃO GRANDE”", 1090, 104, band=R.GOLD, tcol=R.NAVY, rot=-2)
BAR.draw_bar(C, 0.0, "canal"); C.alpha_composite(R.top, (R.HDX, 0)); credit(C, 1215)

# A: ele embaixo fazendo o L, os dois em círculos sobre a ilha
me = np.ascontiguousarray(R.me_src(41.2)[:, ::-1])  # espelhado: L do lado certo
#                                        # olhando para a câmera, boca fechada, fazendo o L
A = island_bg(900)
A.alpha_composite(Image.fromarray(R.me_panel(me)).convert("RGBA"), (0, R.SEAM)); ImageDraw.Draw(A).rectangle((0, R.SEAM - 3, W, R.SEAM + 2), fill=R.GD)
def circ(path, d, focus):
    src = Image.open(path).convert("RGB"); sc = d / min(src.size) * 1.25; src = src.resize((int(src.width * sc), int(src.height * sc)), Image.LANCZOS)
    x0 = (src.width - d) // 2; y0 = int((src.height - d) * focus); c = src.crop((x0, y0, x0 + d, y0 + d)).convert("RGBA")
    m = Image.new("L", (d, d), 0); ImageDraw.Draw(m).ellipse((0, 0, d - 1, d - 1), fill=255); c.putalpha(m)
    ImageDraw.Draw(c).ellipse((2, 2, d - 3, d - 3), outline=R.GOLD + (255,), width=10); return c
cr = circ(f"{R.IMG}/rich_user.jpg", 320, 0.05); cf = circ(f"{R.IMG}/flavio_user.jpg", 320, 0.05)
R.paste(A, cr, CX - 340, 180, 0.6, 18, (6, 14)); R.paste(A, cf, CX + 20, 180, 0.6, 18, (6, 14))
big(A, "RICHARLISON x FLÁVIO", 680, 120); big(A, "“NA MÃO GRANDE”", 850, 96, band=R.GOLD, tcol=R.NAVY, rot=-2)
BAR.draw_bar(A, 0.0, "canal"); A.alpha_composite(R.top, (R.HDX, 0)); credit(A, 945)

# B: ilha em tela cheia com os dois recortados e ele num círculo
B = island_bg(1350)
duo(B, 1500, 380)
mf = me[300:1500, 90:990]; mc = Image.fromarray(cv2.resize(mf, (300, 400))).convert("RGBA")
mc = Image.fromarray(cv2.resize(mf, (390, 520))).convert("RGBA"); d_ = 390; mc = mc.crop((0, 20, 390, 410)); m = Image.new("L", (d_, d_), 0); ImageDraw.Draw(m).ellipse((0, 0, d_ - 1, d_ - 1), fill=255); mc.putalpha(m); ImageDraw.Draw(mc).ellipse((2, 2, d_ - 3, d_ - 3), outline=R.GOLD + (255,), width=9)
big(B, "TOMARAM A ILHA?", 330, 150); big(B, "RICHARLISON ACUSA FLÁVIO", 520, 100, band=R.NAVY, tcol=R.WHITE)
R.paste(B, mc, CX - d_ / 2, 1430, 0.6, 18, (6, 14))
BAR.draw_bar(B, 0.0, "canal"); B.alpha_composite(R.top, (R.HDX, 0)); credit(B, 610)

for k, im in zip("ABC", (A, B, C)): im.convert("RGB").save(f"{V}/capa_{k}.jpg", quality=95)
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas_ilha_ABC.jpg", quality=90); print("ok")
