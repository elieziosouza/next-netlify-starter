"""Capas do corte do debate da Band: Lula pede o voto do pai do Flávio (A debate + ele, B ele em tela cheia, C só o debate)."""
import sys, importlib.util
import numpy as np, cv2
S = sys.argv[1]
spec = importlib.util.spec_from_file_location("rl", f"{S}/work/render_lapada.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
L = importlib.util.module_from_spec(spec); spec.loader.exec_module(L); R = L.R
from PIL import Image, ImageDraw
W, H = R.W, R.H; MF = R.MF; V = L.V; BAR = R.BAR; CX = R.CX
def big(img, txt, cy, size, col=R.GOLD_L, band=None, tcol=None, rot=0):
    f = R.BIGF(size); d0 = ImageDraw.Draw(Image.new("L", (4, 4)))
    while d0.textlength(txt, font=f) > 680: size -= 4; f = R.BIGF(size)
    tw = d0.textlength(txt, font=f); h = int(size * 1.3)
    lay = Image.new("RGBA", (int(tw + 80), h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if band: d.rounded_rectangle((0, 0, lay.width - 1, h - 1), 18, fill=band + (255,), outline=R.GOLD + (255,), width=5)
    d.text((lay.width / 2, h / 2 + 4), txt, font=f, fill=(tcol or col) + (255,), anchor="mm", stroke_width=0 if band else 9, stroke_fill=R.NAVY + (255,))
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    R.paste(img, lay, CX - lay.width / 2, cy - lay.height / 2, 0.6, 16, (5, 12))
def debate(t, w, y, img, zoom=1.0, fx=0.5):
    fr = L.src(L.INTRO + t)[L.CROP[1]:L.CROP[3], L.CROP[0]:L.CROP[2]]
    if zoom > 1:
        h0, w0 = fr.shape[:2]; cw, ch = int(w0 / zoom), int(h0 / zoom); x0 = int(clampx(fx * w0 - cw / 2, 0, w0 - cw)); fr = fr[0:ch, x0:x0 + cw]
    h = int(w * fr.shape[0] / fr.shape[1]); box = Image.fromarray(R.rounded(cv2.resize(fr, (w, h), interpolation=cv2.INTER_LANCZOS4), 30, 5))
    R.paste(img, box, CX - w / 2, y, 0.6, 22, (8, 20)); return y + h
def clampx(v, a, b): return max(a, min(b, v))
def navy(): return Image.fromarray(np.clip(R.NAVYBG, 0, 255).astype(np.uint8)).convert("RGBA")
def credit(img, y): ImageDraw.Draw(img).text((CX, y), "Vídeo: reprodução TV Band", font=MF("SemiBold", 22), fill=(220, 220, 228, 230), anchor="mm")
# C: só o debate, Lula apontando
C = navy(); big(C, "LAPADA", 330, 230); y = debate(9.3, 980, 470, C, 1.35, 0.62)
big(C, "“BOLSONARO, VOTE EM MIM”", y + 120, 92, band=R.NAVY, tcol=R.WHITE); big(C, "LULA FOI PEDIR VOTO NA CASA DO FLÁVIO", y + 290, 96, band=R.GOLD, tcol=R.NAVY, rot=-2)
credit(C, y + 30); BAR.draw_bar(C, 0.0, "canal"); C.alpha_composite(R.top, (R.HDX, 0))
# A: debate em cima (Lula apontando), ele embaixo com a cara de lapada
A = navy(); me = cv2.LUT(L.me_src(1.2), R.LUT); ph = H - 1130
bgp = cv2.resize(cv2.GaussianBlur(cv2.resize(me[300:1430], (W // 10, ph // 10)), (0, 0), 2.5), (W, ph)) * 0.7; fw = int(W * ph / 1130)
fg = cv2.resize(me[300:1430], (fw, ph), interpolation=cv2.INTER_AREA); x0 = CX - fw // 2   # rosto inteiro, centrado depois da barra
fm = np.ones((ph, fw), np.float32); fm[:, :40] = np.linspace(0, 1, 40)[None, :]; fm[:, -40:] = np.linspace(1, 0, 40)[None, :]; fm = fm[..., None]
bgp[:, x0:x0 + fw] = bgp[:, x0:x0 + fw] * (1 - fm) + fg * fm
A.paste(Image.fromarray(bgp.astype(np.uint8)), (0, 1130))
ImageDraw.Draw(A).rectangle((0, 1127, W, 1132), fill=R.GD); y = debate(9.3, 880, 335, A, 1.2, 0.6)
big(A, "LAPADA", 222, 150); big(A, "“BOLSONARO, VOTE EM MIM”", 1130, 70, band=R.RED, tcol=R.WHITE, rot=-2)
credit(A, y - 22); BAR.draw_bar(A, 0.0, "canal"); A.alpha_composite(R.top, (R.HDX, 0))
# B: ele em tela cheia
B = L.me_frame(1.2); big(B, "LAPADA", 300, 230)
big(B, "LULA NO FLÁVIO", 1560, 110, band=R.NAVY, tcol=R.WHITE); big(B, "“BOLSONARO, VOTE EM MIM”", 1720, 84, band=R.GOLD, tcol=R.NAVY, rot=-2)
BAR.draw_bar(B, 0.0, "canal"); B.alpha_composite(R.top, (R.HDX, 0))
for k, im in zip("ABC", (A, B, C)): im.convert("RGB").save(f"{V}/lapada_capa_{k}.jpg", quality=95)
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/lapada_capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas_lapada_ABC.jpg", quality=90); print("ok")
