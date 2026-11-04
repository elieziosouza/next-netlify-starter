"""Capas do react "Flávio e os passaportes" (04/11/2026): A ele + Flávio, B ele de perto, C sem o rosto dele (só o Flávio).
Textos só com o que as fontes confirmam: disse em 26/10 que não sairia do país e foi para os EUA (Jovem Pan, CNN Brasil, Correio)."""
import sys, importlib.util
import numpy as np, cv2
S = sys.argv[1]; X_ARG = sys.argv[2] if len(sys.argv) > 2 else "8.4"
spec = importlib.util.spec_from_file_location("rf", f"{S}/work/render_react_flavio_passaporte.py"); sys.argv = [sys.argv[0], S, "/dev/null", "cover"]
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
def clip(x, w, y, img, y0=0.0, y1=0.42):
    """só a parte de cima da montagem (o vídeo do Flávio), sem a mulher rindo embaixo"""
    fr = G.cl_img(x); fr = fr[int(fr.shape[0] * y0):int(fr.shape[0] * y1)]
    h = int(w * fr.shape[0] / fr.shape[1]); lay, pad = G.layered(fr, w, h)                 # cartão com as camadas douradas, levemente em 3D
    lay = Image.fromarray(R.persp(np.asarray(lay), "left", 0.035))
    R.paste(img, lay, CX - lay.width / 2, y - pad, 0.6, 22, (8, 20)); return y + h
def navy(): return Image.fromarray(np.clip(R.NAVYBG, 0, 255).astype(np.uint8)).convert("RGBA")
def credit(img, y): ImageDraw.Draw(img).text((CX, y + 40), "Vídeo: reprodução redes sociais", font=MF("SemiBold", 22), fill=(220, 220, 228, 230), anchor="mm")
ME_Y0 = 120                                                        # recorte dele começa acima da cabeça: o topo da cabeça nunca sai
def me_panel(img, top, x, y1=1500):
    me = G.fr_of(G.MEF, x)[ME_Y0:y1]; ph = H - top; fw = int(me.shape[1] * ph / me.shape[0])
    bgp = cv2.resize(cv2.GaussianBlur(cv2.resize(me, (W // 10, ph // 10)), (0, 0), 2.5), (W, ph)).astype(np.float32) * 0.7
    fg = cv2.resize(me, (fw, ph), interpolation=cv2.INTER_AREA).astype(np.float32); x0 = CX - fw // 2
    fm = np.ones((ph, fw), np.float32); fm[:, :40] = np.linspace(0, 1, 40)[None, :]; fm[:, -40:] = np.linspace(1, 0, 40)[None, :]; fm = fm[..., None]
    a0, a1 = max(0, x0), min(W, x0 + fw); bgp[:, a0:a1] = bgp[:, a0:a1] * (1 - fm[:, a0 - x0:a1 - x0]) + fg[:, a0 - x0:a1 - x0] * fm[:, a0 - x0:a1 - x0]
    img.paste(Image.fromarray(np.clip(bgp, 0, 255).astype(np.uint8)), (0, top)); ImageDraw.Draw(img).rectangle((0, top - 3, W, top + 2), fill=R.GD)
X_ME = float(X_ARG)                                                # quadro dele: olhos abertos, boca fechada (8,4 s)
A = navy(); me_panel(A, 1120, X_ME); y = clip(1.6, 640, 330, A)
big(A, "NUNCA?", 230, 170); big(A, "E FOI PARA OS EUA", 1120, 84, band=R.RED, tcol=R.WHITE, rot=-2)
credit(A, y - 22); BAR.draw_bar(A, 0.0, "canal"); A.alpha_composite(R.top, (R.HDX, 0))
B = navy(); me_panel(B, 840, X_ME); big(B, "FUGIU?", 300, 230, col=(245, 90, 90))   # textos acima dele: nada por cima do rosto
big(B, "DISSE QUE NÃO SAIRIA DO PAÍS", 520, 64, band=R.NAVY, tcol=R.WHITE); big(B, "E FOI PARA OS EUA", 660, 92, band=R.RED, tcol=R.WHITE, rot=-2)
BAR.draw_bar(B, 0.0, "canal"); B.alpha_composite(R.top, (R.HDX, 0))
C = navy(); big(C, "\"NUNCA PENSEI EM SAIR\"", 230, 110); y = clip(3.0, 820, 330, C)
big(C, "1 DIA DEPOIS: EUA", y + 170, 104, band=R.RED, tcol=R.WHITE, rot=-2); big(C, "FLÁVIO E OS PASSAPORTES", y + 320, 70, band=R.NAVY, tcol=R.WHITE)
credit(C, y + 26); BAR.draw_bar(C, 0.0, "canal"); C.alpha_composite(R.top, (R.HDX, 0))
for k, im in zip("ABC", (A, B, C)): im.convert("RGB").save(f"{V}/capa_{k}.jpg", quality=95)
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas_ABC.jpg", quality=90); print("ok")
