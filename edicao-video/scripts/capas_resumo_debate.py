"""Capas do resumo do debate (A ele + Lula, B Lula x Flávio, C ele com a tela dividida)."""
import sys, importlib.util
import numpy as np, cv2
S = sys.argv[1]
spec = importlib.util.spec_from_file_location("rr", f"{S}/work/render_resumo_debate.py"); sys.argv = [sys.argv[0], S, "/dev/null", "cover"]
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
def navy(): return Image.fromarray(np.clip(R.NAVYBG, 0, 255).astype(np.uint8)).convert("RGBA")
def debate(x, w, y, img):
    fr = G.fr_of(G.CLF, x); h = int(w * fr.shape[0] / fr.shape[1])
    box = Image.fromarray(R.rounded(cv2.resize(fr, (w, h), interpolation=cv2.INTER_LANCZOS4), 30, 5)); R.paste(img, box, CX - w / 2, y, 0.6, 22, (8, 20)); return y + h
def credit(img, y): ImageDraw.Draw(img).text((CX, y), "Vídeo: reprodução TV Band", font=MF("SemiBold", 22), fill=(220, 220, 228, 230), anchor="mm")
# A: tela dividida igual ao vídeo, ele embaixo
A = Image.fromarray(np.clip(G.split_frame(0, G.top_for(101.5), 2.0), 0, 255).astype(np.uint8)).convert("RGBA")
big(A, "RESUMO DO DEBATE", 300, 170); big(A, "LULA X FLÁVIO", G.SEAM, 96, band=R.RED, tcol=R.WHITE, rot=-2)
BAR.draw_bar(A, 0.0, "canal"); A.alpha_composite(R.top, (R.HDX, 0))
# B: os dois no palco
B = navy(); big(B, "QUEM NÃO VIU, VÊ AQUI", 230, 130); y = debate(4.0, 900, 340, B)
big(B, "O RESUMO DO DEBATE", y + 120, 96, band=R.NAVY, tcol=R.WHITE); big(B, "LULA X FLÁVIO", y + 260, 110, band=R.GOLD, tcol=R.NAVY, rot=-2)
credit(B, y + 30); BAR.draw_bar(B, 0.0, "canal"); B.alpha_composite(R.top, (R.HDX, 0))
# C: ele em tela cheia
C = Image.fromarray(np.clip(G.me_full(2.0), 0, 255).astype(np.uint8)).convert("RGBA")
big(C, "PERDEU O DEBATE?", 300, 160); big(C, "EU RESUMO PRA VOCÊ", 1560, 96, band=R.NAVY, tcol=R.WHITE); big(C, "LULA X FLÁVIO", 1720, 96, band=R.RED, tcol=R.WHITE, rot=-2)
BAR.draw_bar(C, 0.0, "canal"); C.alpha_composite(R.top, (R.HDX, 0))
for k, im in zip("ABC", (A, B, C)): im.convert("RGB").save(f"{V}/resumo_capa_{k}.jpg", quality=95)
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/resumo_capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas_resumo_ABC.jpg", quality=90); print("ok")
