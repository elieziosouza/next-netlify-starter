"""Capas do corte 'não protejo meu filho' (A ele + debate, B Lula de perto, C Lula x Flávio no palco)."""
import sys, importlib.util
import numpy as np, cv2
S = sys.argv[1]
spec = importlib.util.spec_from_file_location("rg", f"{S}/work/render_globo.py"); sys.argv = [sys.argv[0], S, "/dev/null", "cover"]
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
def debate(t, w, y, img, zoom=1.0, fx=0.5, fy=0.0, cwf=1.0):
    fr = G.src(t)
    if cwf < 1: cw = int(fr.shape[1] * cwf); x0 = int(min(max(fx * fr.shape[1] - cw / 2, 0), fr.shape[1] - cw)); fr = fr[:, x0:x0 + cw]
    if zoom > 1:
        h0, w0 = fr.shape[:2]; cw, ch = int(w0 / zoom), int(h0 / zoom); x0 = int(min(max(fx * w0 - cw / 2, 0), w0 - cw)); y0 = int(fy * (h0 - ch)); fr = fr[y0:y0 + ch, x0:x0 + cw]
    h = int(w * fr.shape[0] / fr.shape[1]); box = Image.fromarray(R.rounded(cv2.resize(fr, (w, h), interpolation=cv2.INTER_LANCZOS4), 30, 5))
    R.paste(img, box, CX - w / 2, y, 0.6, 22, (8, 20)); return y + h
def navy(): return Image.fromarray(np.clip(R.NAVYBG, 0, 255).astype(np.uint8)).convert("RGBA")
def credit(img, y): ImageDraw.Draw(img).text((CX, y), "Vídeo: reprodução TV Band", font=MF("SemiBold", 22), fill=(220, 220, 228, 230), anchor="mm")
def me_panel(img, top):
    me = cv2.LUT(np.asarray(Image.open(f"{S}/v36/me_face.png").convert("RGB")), R.LUT); ph = H - top
    bgp = cv2.resize(cv2.GaussianBlur(cv2.resize(me[300:1430], (W // 10, ph // 10)), (0, 0), 2.5), (W, ph)) * 0.7; fw = int(W * ph / 1130)
    fg = cv2.resize(me[300:1430], (fw, ph), interpolation=cv2.INTER_AREA); x0 = CX - fw // 2
    fm = np.ones((ph, fw), np.float32); fm[:, :40] = np.linspace(0, 1, 40)[None, :]; fm[:, -40:] = np.linspace(1, 0, 40)[None, :]; fm = fm[..., None]
    bgp[:, x0:x0 + fw] = bgp[:, x0:x0 + fw] * (1 - fm) + fg * fm
    img.paste(Image.fromarray(bgp.astype(np.uint8)), (0, top)); ImageDraw.Draw(img).rectangle((0, top - 3, W, top + 2), fill=R.GD)
# A: Lula em cima, ele embaixo
A = navy(); me_panel(A, 1180); y = debate(20.0, 900, 330, A, fx=0.55, cwf=0.82)
big(A, "PROTEGIDO PELO PAI?", 222, 150); big(A, "“NÃO SOU PAI QUE PROTEGE FILHO”", 1180, 64, band=R.RED, tcol=R.WHITE, rot=-2)
credit(A, y - 22); BAR.draw_bar(A, 0.0, "canal"); A.alpha_composite(R.top, (R.HDX, 0))
# B: Lula de perto
B = navy(); big(B, "LULA X FLÁVIO", 230, 170); y = debate(1.5, 960, 340, B, fx=0.5, cwf=0.72)
big(B, "“NÃO PROTEJO MEU FILHO", y + 130, 92, band=R.NAVY, tcol=R.WHITE); big(B, "COMO VOCÊ FOI PELO SEU PAI”", y + 270, 84, band=R.GOLD, tcol=R.NAVY, rot=-2)
credit(B, y + 30); BAR.draw_bar(B, 0.0, "canal"); B.alpha_composite(R.top, (R.HDX, 0))
# C: os dois no palco
C = navy(); big(C, "LAPADA NA PF", 230, 170); y = debate(27.6, 960, 340, C, fx=0.52, cwf=0.86)
big(C, "“EU NÃO MUDO DIRETOR DA PF”", y + 130, 88, band=R.NAVY, tcol=R.WHITE); big(C, "LULA RESPONDE FLÁVIO", y + 270, 96, band=R.RED, tcol=R.WHITE, rot=-2)
credit(C, y + 30); BAR.draw_bar(C, 0.0, "canal"); C.alpha_composite(R.top, (R.HDX, 0))
for k, im in zip("ABC", (A, B, C)): im.convert("RGB").save(f"{V}/globo_capa_{k}.jpg", quality=95)
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/globo_capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas_globo_ABC.jpg", quality=90); print("ok")
