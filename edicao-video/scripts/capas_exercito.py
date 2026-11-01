"""Capas do react do canal Exército do Lula no estilo do canal: rosto dele grande (fundo real), poucas palavras e a manchete como destaque."""
import sys, importlib.util
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]
spec = importlib.util.spec_from_file_location("re_", f"{S}/work/render_exercito.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
W, H, CX = R.W, R.H, R.CX; YEL = (255, 214, 0); WHITE = (255, 255, 255); BLUE = (14, 62, 120); BAR = R.BAR; V = M.V
def word(img, txt, cy, size, col, sw=12, rot=0, band=None, tcol=None, maxw=840):
    f = R.BIGF(size)
    while f.getlength(txt) > maxw: size -= 4; f = R.BIGF(size)
    tw = f.getlength(txt); h = int(size * 1.25)
    lay = Image.new("RGBA", (int(tw + 90), h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if band: d.rounded_rectangle((0, 6, lay.width - 1, h + 12), 16, fill=band + (255,), outline=R.GOLD + (255,), width=4)
    d.text((lay.width / 2, lay.height / 2 + 4), txt, font=f, fill=(tcol or col) + (255,), anchor="mm", stroke_width=0 if band else sw, stroke_fill=(0, 0, 0, 255))
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    R.paste(img, lay, CX - lay.width / 2, cy - lay.height / 2, 0.8, 18, (6, 14))
def scene(t1, t2, band, bcol, btc, name, emo):
    img = Image.fromarray(M.NAVY_BG.copy()).convert("RGBA")
    me, idx = M.graded(2.5); m = me[260:1620]; top = 880; ph = H - top; fw = int(m.shape[1] * ph / m.shape[0]); fw = min(fw, 2 * (W - CX) - 4)
    fg = cv2.resize(m, (fw, ph), interpolation=cv2.INTER_AREA); x0 = CX - fw // 2
    lay = np.zeros((ph, W, 4), np.uint8); lay[:, x0:x0 + fw, :3] = fg
    al = np.ones((ph, fw), np.float32); al[:200] *= np.linspace(0, 1, 200)[:, None]; al[:, :70] *= np.linspace(0, 1, 70)[None]; al[:, -70:] *= np.linspace(1, 0, 70)[None]
    lay[:, x0:x0 + fw, 3] = (al * 255).astype(np.uint8); img.alpha_composite(Image.fromarray(lay), (0, top))
    c = Image.fromarray(R.rounded(M.NEWS, 22, 4)).resize((640, int(640 * M.NEWS.shape[0] / M.NEWS.shape[1])), Image.LANCZOS).rotate(-2.5, resample=Image.BICUBIC, expand=True)
    R.paste(img, c, CX - c.width / 2 + 110, 500, 0.8, 26, (10, 26))
    M.pop(img, M.emoji(emo, 200), CX - 330, 640, 1.0, 99, wob=False)
    word(img, t1, 200, 170, WHITE); word(img, t2, 370, 160, YEL)
    word(img, band, 845, 64, btc, band=bcol, tcol=btc, rot=-2)
    BAR.draw_bar(img, 0.0, "canal"); img.alpha_composite(R.top, (R.HDX, 0)); img.convert("RGB").save(f"{V}/{name}.jpg", quality=95)
scene("QUEREM DERRUBAR", "O EXÉRCITO DO LULA", "DOMINGO VOCÊS NÃO ESCAPAM", (150, 20, 30), WHITE, "capa_A", "🚨")
scene("CENSURA?", "A 2 DIAS DA ELEIÇÃO", "O PEDIDO ESTÁ NO TSE", BLUE, WHITE, "capa_B", "⚖️")
sheet = Image.new("RGB", (720, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("AB")]
sheet.save(f"{V}/capas_AB.jpg", quality=90)
