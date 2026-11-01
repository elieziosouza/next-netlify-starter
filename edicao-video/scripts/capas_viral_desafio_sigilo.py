"""Capas do corte viral do desafio (A ele + Lula, B Lula de perto, C Lula e Flávio no palco)."""
import sys, importlib.util
import numpy as np, cv2
S = sys.argv[1]
spec = importlib.util.spec_from_file_location("rd", f"{S}/work/render_desafio.py"); sys.argv = [sys.argv[0], S, "/dev/null", "cover"]
G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G); R = G.R
from PIL import Image, ImageDraw
W, H = R.W, R.H; MF = R.MF; V = G.V; BAR = R.BAR; CX = R.CX
def big(img, txt, cy, size, col=R.GOLD_L, band=None, tcol=None, rot=0):
    f = R.BIGF(size); d0 = ImageDraw.Draw(Image.new("L", (4, 4)))
    while d0.textlength(txt, font=f) > 680: size -= 4; f = R.BIGF(size)
    tw = d0.textlength(txt, font=f); h = int(size * 1.3)
    lay = Image.new("RGBA", (int(tw + 80), h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if band: d.rounded_rectangle((0, 0, lay.width - 1, h - 1), 18, fill=band + (255,), outline=R.GOLD + (255,), width=5)
    d.text((lay.width / 2, h / 2 + 4), txt, font=f, fill=(tcol or col) + (255,), anchor="mm", stroke_width=0 if band else 9, stroke_fill=R.NAVY + (255,))
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    R.paste(img, lay, CX - lay.width / 2, cy - lay.height / 2, 0.6, 16, (5, 12))
def debate(x, w, y, img, ch=1.0):
    fr = G.eh_img(x); fr = fr[:int(fr.shape[0] * ch)]
    h = int(w * fr.shape[0] / fr.shape[1]); box = Image.fromarray(R.rounded(cv2.resize(fr, (w, h), interpolation=cv2.INTER_LANCZOS4), 30, 5))
    R.paste(img, box, CX - w / 2, y, 0.6, 22, (8, 20)); return y + h
def navy(): return Image.fromarray(np.clip(R.NAVYBG, 0, 255).astype(np.uint8)).convert("RGBA")
def credit(img, y): ImageDraw.Draw(img).text((CX, y), "Vídeo: reprodução TV Band", font=MF("SemiBold", 22), fill=(220, 220, 228, 230), anchor="mm")
def me_panel(img, top, x):
    me = cv2.LUT(G.fr_of(G.MEF, x), R.LUT); ph = H - top
    bgp = cv2.resize(cv2.GaussianBlur(cv2.resize(me[380:1500], (W // 10, ph // 10)), (0, 0), 2.5), (W, ph)) * 0.7; fw = int(W * ph / 1120)
    fg = cv2.resize(me[380:1500], (fw, ph), interpolation=cv2.INTER_AREA); x0 = CX - fw // 2
    fm = np.ones((ph, fw), np.float32); fm[:, :40] = np.linspace(0, 1, 40)[None, :]; fm[:, -40:] = np.linspace(1, 0, 40)[None, :]; fm = fm[..., None]
    bgp[:, x0:x0 + fw] = bgp[:, x0:x0 + fw] * (1 - fm) + fg * fm
    img.paste(Image.fromarray(bgp.astype(np.uint8)), (0, top)); ImageDraw.Draw(img).rectangle((0, top - 3, W, top + 2), fill=R.GD)
A = navy(); me_panel(A, 1180, 7.9); y = debate(13.6, 700, 330, A, ch=0.95)
big(A, "EU DESAFIO VOCÊ", 222, 150); big(A, "FLÁVIO DEVE ACEITAR?", 1180, 76, band=R.RED, tcol=R.WHITE, rot=-2)
credit(A, y - 22); BAR.draw_bar(A, 0.0, "canal"); A.alpha_composite(R.top, (R.HDX, 0))
B = navy(); big(B, "ABRE O SIGILO!", 230, 160); y = debate(25.9, 820, 340, B)
big(B, "LULA ABRE O DA FAMÍLIA", y + 110, 84, band=R.NAVY, tcol=R.WHITE); big(B, "O FLÁVIO DEVE ACEITAR?", y + 250, 84, band=R.RED, tcol=R.WHITE, rot=-2)
credit(B, y + 30); BAR.draw_bar(B, 0.0, "canal"); B.alpha_composite(R.top, (R.HDX, 0))
C = navy(); big(C, "EU DESAFIO VOCÊ", 230, 160, col=(245, 90, 90)); y = debate(1.0, 820, 340, C)
big(C, "LULA X FLÁVIO", y + 110, 100, band=R.NAVY, tcol=R.WHITE); big(C, "QUEM TOPA ABRIR?", y + 260, 96, band=R.GOLD, tcol=R.NAVY, rot=-2)
credit(C, y + 30); BAR.draw_bar(C, 0.0, "canal"); C.alpha_composite(R.top, (R.HDX, 0))
for k, im in zip("ABC", (A, B, C)): im.convert("RGB").save(f"{V}/desafio_capa_{k}.jpg", quality=95)
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/desafio_capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas_desafio_ABC.jpg", quality=90); print("ok")
