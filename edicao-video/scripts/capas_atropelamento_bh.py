"""Capas do idoso atropelado em ato pró-Lula em BH (A e B com o rosto dele, C sem rosto). Sem rótulo político para o motorista."""
import sys, importlib.util
import numpy as np, cv2
S = sys.argv[1]; sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
from PIL import Image, ImageDraw
W, H = R.W, R.H; MF = R.MF; V = R.V; BAR = R.BAR; CX = R.CX
def big(img, txt, cy, size, col=R.GOLD_L, band=None, tcol=None, rot=0):
    f = R.BIGF(size); d0 = ImageDraw.Draw(Image.new("L", (4, 4)))
    while d0.textlength(txt, font=f) > 680: size -= 4; f = R.BIGF(size)
    tw = d0.textlength(txt, font=f); h = int(size * 1.3)
    lay = Image.new("RGBA", (int(tw + 80), h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if band: d.rounded_rectangle((0, 0, lay.width - 1, h - 1), 18, fill=band + (255,), outline=R.GOLD + (255,), width=5)
    d.text((lay.width / 2, h / 2 + 4), txt, font=f, fill=(tcol or col) + (255,), anchor="mm", stroke_width=0 if band else 9, stroke_fill=R.NAVY + (255,))
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    R.paste(img, lay, CX - lay.width / 2, cy - lay.height / 2, 0.6, 16, (5, 12))
def car_bg(hgt, ct=5.5):
    fr = R.clip_img(ct); full = cv2.resize(fr, (W, 1069), interpolation=cv2.INTER_LANCZOS4)[170:1069]
    bg = Image.fromarray(np.clip(R.NAVYBG, 0, 255).astype(np.uint8)).convert("RGBA")
    top = Image.fromarray(cv2.resize(full, (int(W * hgt / 899), hgt))).convert("RGBA"); bg.paste(top, (int((W - top.width) / 2), 0))
    fadeh = 240; g = Image.linear_gradient("L").resize((W, fadeh)); dk = Image.new("RGBA", (W, fadeh), (4, 14, 30, 255)); dk.putalpha(g); bg.alpha_composite(dk, (0, hgt - fadeh))
    return bg
def ring(img, x, y, rx, ry):
    d = ImageDraw.Draw(img)
    for w_, c in ((18, (255, 255, 255, 140)), (10, R.RED + (255,))): d.ellipse((x - rx, y - ry, x + rx, y + ry), outline=c, width=w_)
def credit(img, y): ImageDraw.Draw(img).text((CX, y), "Vídeo: reprodução O Dia", font=MF("SemiBold", 22), fill=(220, 220, 228, 230), anchor="mm")
me = np.ascontiguousarray(R.me_src(42.5)[:, ::-1])                  # fazendo o L, espelhado como no vídeo
# C: sem rosto
C = car_bg(1150); ring(C, 640, 1150 * 780 / 899, 330, 150)
big(C, "ATROPELADO", 1270, 170); big(C, "EM ATO PRÓ-LULA", 1440, 120, band=R.NAVY, tcol=R.WHITE); big(C, "IDOSO DE 67 ANOS", 1600, 96, band=R.GOLD, tcol=R.NAVY, rot=-2)
credit(C, 1720); BAR.draw_bar(C, 0.0, "canal"); C.alpha_composite(R.top, (R.HDX, 0))
# A: carro em cima, ele embaixo
A = car_bg(900); ring(A, 640, 900 * 780 / 899, 300, 130)
A.alpha_composite(Image.fromarray(R.me_panel(me)).convert("RGBA"), (0, R.SEAM)); ImageDraw.Draw(A).rectangle((0, R.SEAM - 3, W, R.SEAM + 2), fill=R.GD)
big(A, "ATROPELOU NO ATO", 300, 120); big(A, "IDOSO DE 67 ANOS", 470, 96, band=R.RED, tcol=R.WHITE, rot=-2)
credit(A, 1000); BAR.draw_bar(A, 0.0, "canal"); A.alpha_composite(R.top, (R.HDX, 0))
# B: ele em tela cheia com a caixa
fb = R.big_behind(R.fit_frame(me), 38.6); B = Image.fromarray(fb).convert("RGBA")
big(B, "POLÍTICA NÃO É GUERRA", 1560, 100, band=R.NAVY, tcol=R.WHITE); big(B, "IDOSO ATROPELADO EM BH", 1720, 84, band=R.GOLD, tcol=R.NAVY, rot=-2)
BAR.draw_bar(B, 0.0, "canal"); B.alpha_composite(R.top, (R.HDX, 0))
for k, im in zip("ABC", (A, B, C)): im.convert("RGB").save(f"{V}/capa_{k}.jpg", quality=95)
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas_atrop_ABC.jpg", quality=90); print("ok")
