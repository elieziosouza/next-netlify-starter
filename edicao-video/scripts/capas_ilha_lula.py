"""Capas do corte Lula x ilha do Richarlison: Lula no vídeo dele, Richarlison (print do meu vídeo) e Flávio em P&B. Textos atribuídos ("LULA PEDE À PF")."""
import sys, io, subprocess, importlib.util
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; V = f"{S}/v48"
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
W, H = R.W, R.H; BAR = R.BAR; CX = R.CX; YEL = (255, 214, 0); WHITE = (255, 255, 255); BLUE = (14, 62, 120)
def grab(path, t, crop=None):
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", path, "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    a = np.asarray(Image.open(io.BytesIO(p)).convert("RGB")); return a if crop is None else a[crop[1]:crop[3], crop[0]:crop[2]]
LULA = grab(f"{V}/cl.mp4", 40.6, (0, 40, 720, 760))
shot = np.asarray(Image.open("/root/.claude/uploads/698dd744-d40f-5d96-b9e9-72023ae79dbf/f26217e3-image.jpg").convert("RGB")); RICH = shot[420:1150, 180:990]
pst = np.asarray(Image.open("/root/.claude/uploads/698dd744-d40f-5d96-b9e9-72023ae79dbf/6b5d6b3b-image.jpg").convert("RGB")); FLAV = pst[0:300, 676:1104]
FLAV = cv2.cvtColor(cv2.cvtColor(FLAV, cv2.COLOR_RGB2GRAY), cv2.COLOR_GRAY2RGB)
def word(img, txt, cy, size, col, stroke=R.NAVY, sw=12, rot=0, band=None, tcol=None, maxw=720):
    f = R.BIGF(size)
    while f.getlength(txt) > maxw: size -= 4; f = R.BIGF(size)
    tw = f.getlength(txt); h = int(size * 1.25)
    lay = Image.new("RGBA", (int(tw + 90), h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if band: d.rounded_rectangle((0, 6, lay.width - 1, h + 12), 16, fill=band + (255,))
    d.text((lay.width / 2, lay.height / 2 + 4), txt, font=f, fill=(tcol or col) + (255,), anchor="mm", stroke_width=0 if band else sw, stroke_fill=stroke + (255,))
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    R.paste(img, lay, CX - lay.width / 2, cy - lay.height / 2, 0.7, 18, (6, 14))
def photo(img, src, w, x, y, lut=True, rad=26):
    s = cv2.LUT(src, R.LUT) if lut else src
    c = Image.fromarray(R.rounded(cv2.resize(s, (w, int(w * s.shape[0] / s.shape[1])), interpolation=cv2.INTER_LANCZOS4), rad, 5)); R.paste(img, c, x, y, 0.6, 22, (8, 20)); return c
def base(src, k=0.3): return Image.fromarray(np.clip(R.blur_bg(src, k), 0, 255).astype(np.uint8)).convert("RGBA")
def finish(img, name):
    BAR.draw_bar(img, 0.0, "canal"); img.alpha_composite(R.top, (R.HDX, 0)); img.convert("RGB").save(f"{V}/{name}.jpg", quality=95)
# A: Lula grande, Richarlison e Flávio em P&B nos cantos
A = base(LULA); word(A, "LULA ENTROU", 230, 190, YEL); word(A, "NA BRIGA!", 420, 210, YEL)
c = photo(A, LULA, 700, CX - 350, 560)
photo(A, RICH, 330, CX - 470, 560 + c.height - 230); photo(A, FLAV, 330, CX + 140, 560 + c.height - 200, lut=False)
word(A, "PEDIU À PF: INVESTIGUE A ILHA", 560 + c.height + 170, 66, R.NAVY, band=YEL, tcol=R.NAVY, rot=-3)
word(A, "E AGORA, FLÁVIO?", 560 + c.height + 320, 130, WHITE, sw=10)
finish(A, "capa_A")
# B: frente a frente, Lula x Flávio, Richarlison no meio
B = base(RICH, 0.25); word(B, "A ILHA DO RICHARLISON", 210, 120, WHITE, sw=10); word(B, "CHEGOU NO LULA", 370, 160, YEL)
photo(B, LULA, 470, CX - 500, 520); photo(B, FLAV, 470, CX + 20, 600, lut=False)
d = ImageDraw.Draw(B); d.ellipse((CX - 85, 760, CX + 85, 930), fill=YEL + (255,), outline=R.NAVY + (255,), width=8)
d.text((CX, 845), "X", font=R.BIGF(120), fill=R.NAVY + (255,), anchor="mm")
photo(B, RICH, 430, CX - 215, 1060)
word(B, "“TÔ PEDINDO PRA PF INVESTIGAR”", 1560, 64, WHITE, band=BLUE, tcol=WHITE, rot=-2)
word(B, "E AGORA, FLÁVIO?", 1700, 110, YEL, sw=10)
finish(B, "capa_B")
sheet = Image.new("RGB", (720, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("AB")]
sheet.save(f"{V}/capas_AB.jpg", quality=90)
