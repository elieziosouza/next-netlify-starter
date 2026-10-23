"""Capa do meme da mochila: quadro dele arrumando a mochila, texto grande no estilo do canal e a pergunta-provocação."""
import sys, importlib.util, subprocess, io
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
S = sys.argv[1]; V = f"{S}/v57"
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
W, H, CX = R.W, R.H, R.CX; YEL = (255, 214, 0); WHITE = (255, 255, 255); BAR = R.BAR
p = subprocess.run(["ffmpeg", "-v", "error", "-ss", "7.3", "-i", f"{V}/me.mp4", "-frames:v", "1", "-vf", "scale=1080:1920", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
fr = Image.open(io.BytesIO(p)).convert("RGBA")
g = np.zeros((H, W, 4), np.uint8); g[..., :3] = (4, 14, 28); a = np.zeros(H); a[380:1280] = 150 * np.sin(np.linspace(0, np.pi, 900)); g[..., 3] = a[:, None].astype(np.uint8)
fr.alpha_composite(Image.fromarray(g))                                                       # escurece só a faixa do meio, onde vai o texto
def word(img, txt, cy, size, col, sw=12, rot=0, band=None, tcol=None, maxw=860):
    f = R.BIGF(size)
    while f.getlength(txt) > maxw: size -= 4; f = R.BIGF(size)
    tw = f.getlength(txt); h = int(size * 1.25)
    lay = Image.new("RGBA", (int(tw + 90), h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if band: d.rounded_rectangle((0, 6, lay.width - 1, h + 12), 16, fill=band + (255,), outline=R.GOLD + (255,), width=4)
    d.text((lay.width / 2, lay.height / 2 + 4), txt, font=f, fill=(tcol or col) + (255,), anchor="mm", stroke_width=0 if band else sw, stroke_fill=(0, 0, 0, 255))
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    R.paste(img, lay, CX - lay.width / 2, cy - lay.height / 2, 0.8, 18, (6, 14))
word(fr, "“IMPOSSÍVEL O LULA", 520, 150, WHITE); word(fr, "GANHAR”", 690, 170, WHITE)
word(fr, "EU, ARRUMANDO A MOCHILA:", 930, 82, R.NAVY, band=YEL, tcol=R.NAVY, rot=-2)
word(fr, "500 KM PRA VOTAR", 1095, 140, YEL)
fe = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109); e = Image.new("RGBA", (140, 140), (0, 0, 0, 0)); ImageDraw.Draw(e).text((0, 0), "😂", font=fe, embedded_color=True)
fr.alpha_composite(e.resize((170, 170), Image.LANCZOS), (CX + 330, 1175))
BAR.draw_bar(fr, 0.0, "canal"); fr.alpha_composite(R.top, (R.HDX, 0)); fr.convert("RGB").save(f"{V}/capa.jpg", quality=95)
