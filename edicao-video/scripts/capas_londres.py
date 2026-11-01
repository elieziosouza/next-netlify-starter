"""Capas do reels do cartaz em Londres: o cartaz "THE WORLD NEEDS LULA" com o Big Ben e ele com cara de provocação."""
import sys, io, subprocess, importlib.util
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; V = f"{S}/v49"
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
W, H = R.W, R.H; BAR = R.BAR; CX = R.CX; YEL = (255, 214, 0); WHITE = (255, 255, 255); BLUE = (14, 62, 120)
def grab(path, t, crop=None):
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", path, "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    a = np.asarray(Image.open(io.BytesIO(p)).convert("RGB")); return a if crop is None else a[crop[1]:crop[3], crop[0]:crop[2]]
BENS = grab(f"{V}/cl.mp4", 17.2, (20, 20, 1060, 1360))                 # ônibus vermelho, cartaz e o Big Ben
POST = grab(f"{V}/cl.mp4", 21.5, (20, 20, 1060, 1360))                 # o cartaz de perto
ME = grab(f"{V}/me.mp4", 5.6)[200:1500]
FOTO = np.asarray(Image.open(f"{V}/foto_bigben.jpg").convert("RGB"))                # cartaz com o Big Ben (redes sociais)
def word(img, txt, cy, size, col, stroke=R.NAVY, sw=12, rot=0, band=None, tcol=None, maxw=720):
    f = R.BIGF(size)
    while f.getlength(txt) > maxw: size -= 4; f = R.BIGF(size)
    tw = f.getlength(txt); h = int(size * 1.25)
    lay = Image.new("RGBA", (int(tw + 90), h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if band: d.rounded_rectangle((0, 6, lay.width - 1, h + 12), 16, fill=band + (255,))
    d.text((lay.width / 2, lay.height / 2 + 4), txt, font=f, fill=(tcol or col) + (255,), anchor="mm", stroke_width=0 if band else sw, stroke_fill=stroke + (255,))
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    R.paste(img, lay, CX - lay.width / 2, cy - lay.height / 2, 0.7, 18, (6, 14))
def photo(img, src, w, x, y, rad=26):
    c = Image.fromarray(R.rounded(cv2.resize(cv2.LUT(src, R.LUT), (w, int(w * src.shape[0] / src.shape[1])), interpolation=cv2.INTER_LANCZOS4), rad, 5)); R.paste(img, c, x, y, 0.6, 22, (8, 20)); return c
def base(src, k=0.3): return Image.fromarray(np.clip(R.blur_bg(src, k), 0, 255).astype(np.uint8)).convert("RGBA")
def finish(img, name):
    BAR.draw_bar(img, 0.0, "canal"); img.alpha_composite(R.top, (R.HDX, 0)); img.convert("RGB").save(f"{V}/{name}.jpg", quality=95)
A = base(FOTO); word(A, "BOLSONARISTA,", 220, 150, WHITE); word(A, "NÃO SURTA!", 400, 200, YEL)
c = photo(A, FOTO[0:1150], 640, CX - 320, 520); photo(A, ME, 250, CX - 470, 520 + c.height - 300)
word(A, "TEM LULA ATÉ EM LONDRES", 520 + c.height + 90, 84, R.NAVY, band=YEL, tcol=R.NAVY, rot=-3)
word(A, "PERTO DO BIG BEN", 520 + c.height + 220, 70, WHITE, sw=8)
finish(A, "capa_A")
B = base(BENS); word(B, "O MUNDO PRECISA", 210, 130, WHITE); word(B, "DE LULA", 380, 210, YEL)
c = photo(B, FOTO[540:1100, 350:770], 620, CX - 310, 520); photo(B, ME, 300, CX - 470, 520 + c.height - 260)
word(B, "CARTAZ EM LONDRES", 520 + c.height + 130, 90, R.NAVY, band=YEL, tcol=R.NAVY, rot=-2)
word(B, "E AGORA, BOLSONARISTA?", 520 + c.height + 270, 90, WHITE, sw=8)
finish(B, "capa_B")
sheet = Image.new("RGB", (720, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("AB")]
sheet.save(f"{V}/capas_AB.jpg", quality=90)
