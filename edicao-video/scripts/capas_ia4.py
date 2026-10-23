"""Capas da bolha da IA no estilo do canal (marinho e dourado), melhoradas: rosto dele maior, menos palavras, card "META -7%" como destaque."""
import sys, importlib.util, math
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]
spec = importlib.util.spec_from_file_location("ri", f"{S}/work/render_ia.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
W, H, CX = R.W, R.H, R.CX; YEL = (255, 214, 0); WHITE = (255, 255, 255); BLUE = (14, 62, 120); BAR = R.BAR; V = M.V
def word(img, txt, cy, size, col, sw=12, rot=0, band=None, tcol=None, maxw=820):
    f = R.BIGF(size)
    while f.getlength(txt) > maxw: size -= 4; f = R.BIGF(size)
    tw = f.getlength(txt); h = int(size * 1.25)
    lay = Image.new("RGBA", (int(tw + 90), h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if band: d.rounded_rectangle((0, 6, lay.width - 1, h + 12), 16, fill=band + (255,), outline=R.GOLD + (255,), width=4)
    d.text((lay.width / 2, lay.height / 2 + 4), txt, font=f, fill=(tcol or col) + (255,), anchor="mm", stroke_width=0 if band else sw, stroke_fill=(0, 0, 0, 255))
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    R.paste(img, lay, CX - lay.width / 2, cy - lay.height / 2, 0.8, 18, (6, 14))
def meta_card():
    w, h = 820, 560; im = M.card_bg(w, h); d = ImageDraw.Draw(im)
    d.text((w / 2, 70), "META", font=R.BIGF(90), fill=(255, 255, 255, 255), anchor="mm")
    d.text((w / 2, 220), "-7%", font=R.BIGF(210), fill=YEL + (255,), anchor="mm")
    d.text((w / 2, 345), "EM UM DIA", font=R.MF("ExtraBold", 44), fill=(255, 255, 255, 255), anchor="mm")
    pts = [(80 + i * 33, 420 + 110 * (i / 20) ** 1.6 + 14 * math.sin(i * 1.7)) for i in range(21)]
    d.line(pts, fill=(200, 30, 40, 255), width=10, joint="curve"); ex, ey = pts[-1]
    d.polygon([(ex + 26, ey + 4), (ex - 6, ey - 20), (ex - 10, ey + 24)], fill=(200, 30, 40, 255))
    return im
def scene(t1, t2, band, bcol, btc, name, emo="🫧"):
    global EMO; EMO = emo
    img = Image.fromarray(M.NAVY_BG.copy()).convert("RGBA")
    me, idx = M.graded(53.5); m = me[380:1560]; top = 840; ph = H - top; fw = int(m.shape[1] * ph / m.shape[0])
    fg = cv2.resize(m, (fw, ph), interpolation=cv2.INTER_AREA); x0 = CX - fw // 2
    lay = np.zeros((ph, W, 4), np.uint8); lay[:, x0:x0 + fw, :3] = fg
    al = np.ones((ph, fw), np.float32); al[:200] *= np.linspace(0, 1, 200)[:, None]; al[:, :70] *= np.linspace(0, 1, 70)[None]; al[:, -70:] *= np.linspace(1, 0, 70)[None]
    lay[:, x0:x0 + fw, 3] = (al * 255).astype(np.uint8); img.alpha_composite(Image.fromarray(lay), (0, top))
    c = meta_card().resize((574, 392), Image.LANCZOS).rotate(-3, resample=Image.BICUBIC, expand=True); R.paste(img, c, CX - c.width / 2 + 150, 470, 0.8, 26, (10, 26))
    M.pop(img, M.emoji(EMO, 210), CX - 300, 640, 1.0, 99, wob=False)
    word(img, t1, 200, 175, WHITE); word(img, t2, 370, 165, YEL)
    word(img, band, 1795, 66, btc, band=bcol, tcol=btc, rot=-2)
    BAR.draw_bar(img, 0.0, "canal"); img.alpha_composite(R.top, (R.HDX, 0)); img.convert("RGB").save(f"{V}/{name}.jpg", quality=95)
scene("BOLHA DA IA", "VAI ESTOURAR?", "NASDAQ -2,6% EM UM DIA", (150, 20, 30), WHITE, "capa4_A")
scene("A IA CHEGOU", "NO SEU BOLSO", "DÓLAR VOLTOU PARA R$ 5", BLUE, WHITE, "capa4_B", "💸")
sheet = Image.new("RGB", (720, 640)); [sheet.paste(Image.open(f"{V}/capa4_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("AB")]
sheet.save(f"{V}/capas4_AB.jpg", quality=90)
