"""Capas do caso Ana Clara. Sem foto da menina (criança vítima) e sem foto do PM (réu, ainda não julgado): Flávio em preto e branco,
a mãe ou ele sério, fita branca com "ANA CLARA, 5 ANOS". Textos em amarelo, branco e azul do canal."""
import sys, importlib.util, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
W, H = R.W, R.H; BAR = R.BAR; CX = R.CX; V = f"{S}/v45"
YEL = (255, 214, 0); WHITE = (255, 255, 255); BLUE = (14, 62, 120)
POSTER = "/root/.claude/uploads/698dd744-d40f-5d96-b9e9-72023ae79dbf/6b5d6b3b-image.jpg"
pst = np.asarray(Image.open(POSTER).convert("RGB")); FLAV = pst[0:300, 676:1104].copy()          # Flávio em preto e branco, do cartaz
FLAV = cv2.cvtColor(cv2.cvtColor(FLAV, cv2.COLOR_RGB2GRAY), cv2.COLOR_GRAY2RGB)
def grab(path, t, vf=""):
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", path, "-frames:v", "1"] + (["-vf", vf] if vf else []) + ["-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    return np.asarray(Image.open(__import__("io").BytesIO(p)).convert("RGB"))
ME = grab(f"{V}/me.mp4", 55.0)                     # ele calado, sério (depois da fala)
MAE = grab(f"{V}/mae/mae.mp4", 140.2)[110:730]     # a mãe, sem a legenda queimada
def word(img, txt, cy, size, col, stroke=R.NAVY, sw=12, rot=0, band=None, tcol=None, maxw=700):
    f = R.BIGF(size)
    while f.getlength(txt) > maxw: size -= 4; f = R.BIGF(size)
    tw = f.getlength(txt); h = int(size * 1.25)
    lay = Image.new("RGBA", (int(tw + 90), h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    if band: d.rounded_rectangle((0, 6, lay.width - 1, h + 12), 16, fill=band + (255,))
    d.text((lay.width / 2, lay.height / 2 + 4), txt, font=f, fill=(tcol or col) + (255,), anchor="mm", stroke_width=0 if band else sw, stroke_fill=stroke + (255,))
    if rot: lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    R.paste(img, lay, CX - lay.width / 2, cy - lay.height / 2, 0.7, 18, (6, 14))
def base(src, k=0.30): return Image.fromarray(np.clip(R.blur_bg(src, k), 0, 255).astype(np.uint8)).convert("RGBA")
def photo(img, src, w, x, y, rad=28, lut=True):
    s = cv2.LUT(src, R.LUT) if lut else src
    c = Image.fromarray(R.rounded(cv2.resize(s, (w, int(w * s.shape[0] / s.shape[1])), interpolation=cv2.INTER_LANCZOS4), rad, 5)); R.paste(img, c, x, y, 0.6, 22, (8, 20)); return c
def ribbon(img, cx, cy, txt="ANA CLARA, 5 ANOS"):
    """fita branca de luto + nome em letras delicadas"""
    lay = Image.new("RGBA", (820, 210), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); x0, y0 = 70, 20
    d.polygon([(x0, y0 + 10), (x0 + 30, y0), (x0 + 75, y0 + 120), (x0 + 50, y0 + 165), (x0 + 38, y0 + 120)], fill=(250, 250, 250, 255))
    d.polygon([(x0 + 60, y0 + 10), (x0 + 30, y0), (x0 - 15, y0 + 120), (x0 + 10, y0 + 165), (x0 + 22, y0 + 120)], fill=(225, 225, 230, 255))
    fs = 54
    while R.MF("ExtraBold", fs).getlength(txt) > 600: fs -= 2
    f = R.MF("ExtraBold", fs); d.text((x0 + 110, 92), txt, font=f, fill=WHITE + (255,), anchor="lm", stroke_width=3, stroke_fill=(0, 0, 0, 160))
    R.paste(img, lay, cx - 380, cy - 105, 0.6, 14, (4, 10))
def finish(img, name):
    BAR.draw_bar(img, 0.0, "canal"); img.alpha_composite(R.top, (R.HDX, 0)); img.convert("RGB").save(f"{V}/{name}.jpg", quality=95)
# A: Flávio grande em P&B + "ELE DEFENDEU O PM" + ele na janela
A = base(FLAV, 0.22); word(A, "ELE DEFENDEU", 250, 170, YEL); word(A, "O PM ACUSADO", 430, 170, YEL)
c = photo(A, FLAV, 760, CX - 380, 560, lut=False)
photo(A, ME[200:1500], 300, CX + 120, 560 + c.height - 300)
word(A, "DA MORTE DA ANA CLARA, 5 ANOS", 560 + c.height + 190, 64, R.NAVY, band=YEL, tcol=R.NAVY, rot=-2)
ribbon(A, CX, 560 + c.height + 360, "JUSTIÇA POR ANA CLARA")
word(A, "O JÚRI AINDA NÃO ACONTECEU", 560 + c.height + 500, 70, WHITE, sw=8)
finish(A, "capa_A")
# B: Flávio P&B x a mãe + fita
B = base(MAE, 0.25); word(B, "E SE FOSSE", 240, 160, WHITE); word(B, "SUA FILHA?", 420, 190, YEL)
photo(B, FLAV, 760, CX - 380, 540, lut=False); photo(B, MAE, 360, CX + 80, 900)
word(B, "FLÁVIO DEFENDEU O PM ACUSADO", 1330, 66, R.NAVY, band=YEL, tcol=R.NAVY, rot=-2)
ribbon(B, CX, 1490); word(B, "A MÃE AINDA ESPERA JUSTIÇA", 1650, 64, WHITE, sw=8)
finish(B, "capa_B")
# C: ele sério em tela cheia + texto gigante
C = Image.fromarray(np.clip(R.blur_bg(ME, 0.5), 0, 255).astype(np.uint8)).convert("RGBA")
fw = 980; me = cv2.LUT(cv2.resize(ME, (fw, int(fw * ME.shape[0] / ME.shape[1]))), R.LUT); C.paste(Image.fromarray(me), (CX - fw // 2, H - me.shape[0]))
word(C, "QUEM DEFENDEU", 230, 160, WHITE); word(C, "ESSE PM", 410, 200, YEL)
photo(C, FLAV, 420, CX - 440, 560, lut=False)
word(C, "VAI DEFENDER SUA FAMÍLIA?", 1300, 76, R.NAVY, band=YEL, tcol=R.NAVY, rot=-2)
ribbon(C, CX, 1480)
finish(C, "capa_C")
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("ABC")]
sheet.save(f"{V}/capas_ABC.jpg", quality=90)
# B2/B3: versões mais chamativas da B (pedido de 21/10): texto gigante, rosto da mãe grande
MAE2 = grab(f"{V}/mae/mae.mp4", 135.4)[60:900]
def bigtxt(img, txt, cy, size, col, sw=14, maxw=760):
    f = R.BIGF(size)
    while f.getlength(txt) > maxw: size -= 4; f = R.BIGF(size)
    lay = Image.new("RGBA", (W, int(size * 1.3)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text((W / 2 + 8, lay.height / 2 + 10), txt, font=f, fill=(0, 0, 0, 150), anchor="mm", stroke_width=sw, stroke_fill=(0, 0, 0, 150))
    d.text((W / 2, lay.height / 2), txt, font=f, fill=col + (255,), anchor="mm", stroke_width=sw, stroke_fill=R.NAVY + (255,))
    img.alpha_composite(lay, (CX - W // 2, int(cy - lay.height / 2)))
def fullbg(src, y0=0):
    s = cv2.LUT(src, R.LUT); h = int(W * s.shape[0] / s.shape[1]); im = cv2.resize(s, (W, h), interpolation=cv2.INTER_LANCZOS4)
    base_ = np.zeros((H, W, 3), np.float32) + 8; base_[y0:y0 + h] = im[:H - y0]
    g = np.ones((H, 1, 1), np.float32); yy = np.arange(H)[:, None, None]
    g = np.clip(1 - (yy - (y0 + h - 420)) / 420, 0.12, 1) * np.clip(0.55 + (yy - y0) / 600, 0, 1)
    return Image.fromarray(np.clip(base_ * g, 0, 255).astype(np.uint8)).convert("RGBA")
# B2: a mãe chorando ocupa o alto; texto enorme embaixo; Flávio P&B no canto
B2 = fullbg(MAE, 140)
bigtxt(B2, "E SE FOSSE", 1060, 190, WHITE); bigtxt(B2, "SUA FILHA?", 1270, 240, YEL)
photo(B2, FLAV, 330, CX + 70, 1410, lut=False)
word(B2, "FLÁVIO DEFENDEU", 1470, 64, R.NAVY, band=YEL, tcol=R.NAVY, rot=-3, maxw=360)
for i_, l_ in enumerate(["O PM ACUSADO", "DA MORTE DA", "ANA CLARA, 5 ANOS"]):
    d_ = ImageDraw.Draw(B2); f_ = R.MF("ExtraBold", 40); d_.text((CX - 180, 1580 + i_ * 52), l_, font=f_, fill=WHITE + (255,), anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0, 200))
finish(B2, "capa_B2")
# B3: texto gigante no topo, mãe grande x Flávio P&B, frase dela entre aspas
B3 = base(MAE2, 0.22)
bigtxt(B3, "E SE FOSSE", 240, 200, WHITE); bigtxt(B3, "SUA FILHA?", 460, 250, YEL)
photo(B3, MAE2, 520, CX - 330, 610)
photo(B3, FLAV, 420, CX + 10, 1060, lut=False)
word(B3, "“EU VI MINHA FILHA MORRER”", 1480, 70, WHITE, band=BLUE, tcol=WHITE, rot=-2)
word(B3, "A MÃE DA ANA CLARA · O FLÁVIO DEFENDEU O PM ACUSADO", 1610, 40, WHITE, sw=6, maxw=740)
finish(B3, "capa_B3")
sheet = Image.new("RGB", (1080, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate(["B", "B2", "B3"])]
sheet.save(f"{V}/capas_B.jpg", quality=90)
