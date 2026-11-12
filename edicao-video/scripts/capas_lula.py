"""Capas do react (12/11/2026): A e B com o rosto dele em janela dourada, C sem o rosto (vídeo de terceiros desfocado). Texto na faixa 3:4 (y 240-1680)."""
import sys, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import video_react as R
W, H, CX = 1080, 1920, 582
GOLD, GOLD_L, NAVY, WHITE, RED = R.GOLD, R.GOLD_L, R.NAVY, R.WHITE, (206, 34, 40)
MF = R.MF; BAR = R.BAR
def face(t, ww=620, hh=827):
    fr = R.grab("me.mp4", t, 1080, 1920); crop = fr[100:1180, 105:915]
    im = Image.fromarray(crop).resize((ww, hh), Image.LANCZOS); return R.shadowed(R.rounded(im, 34, GOLD, 7), 26, 18, .6)
def text(img, txt, cy, font, col=WHITE, stroke=8, maxw=760):
    f = font; s = f.size
    while f.getlength(txt) > maxw: s -= 4; f = f.font_variant(size=s)
    lay = Image.new("RGBA", (W, int(s * 1.6)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text((CX, lay.height / 2), txt, font=f, fill=col + (255,), anchor="mm", stroke_width=stroke, stroke_fill=NAVY + (255,))
    sh = lay.copy(); sh.putalpha(sh.getchannel("A").point(lambda v: int(v * .6))); sh = sh.filter(ImageFilter.GaussianBlur(14))
    img.alpha_composite(sh, (0, int(cy - lay.height / 2 + 10))); img.alpha_composite(lay, (0, int(cy - lay.height / 2)))
def tag(img, txt, cy):
    f = MF("ExtraBold", 34); tw = f.getlength(txt) + 64; d = ImageDraw.Draw(img)
    d.rounded_rectangle((CX - tw / 2, cy - 30, CX + tw / 2, cy + 30), 10, fill=GOLD + (255,)); d.text((CX, cy + 1), txt, font=f, fill=NAVY + (255,), anchor="mm")
def stamp(img, txt, cy, size=84, rot=-3):
    f = MF("Black", size)
    while f.getlength(txt) > 700: size -= 4; f = MF("Black", size)
    lay = Image.new("RGBA", (int(f.getlength(txt) + 90), int(size * 1.55)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle((6, 6, lay.width - 7, lay.height - 7), 16, fill=RED + (255,), outline=WHITE + (255,), width=6)
    d.text((lay.width / 2, lay.height / 2 + 3), txt, font=f, fill=WHITE + (255,), anchor="mm"); lay = lay.rotate(rot, resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", lay.size, (0, 0, 0, 0)); sh.putalpha(lay.getchannel("A").point(lambda v: int(v * .5))); sh = sh.filter(ImageFilter.GaussianBlur(16))
    img.alpha_composite(sh, (int(CX - lay.width / 2), int(cy - lay.height / 2 + 14))); img.alpha_composite(lay, (int(CX - lay.width / 2), int(cy - lay.height / 2)))
def finish(img):
    BAR.draw_bar(img, 0.0, "canal"); img.alpha_composite(R.top, (R.HDX, 0)); return img.convert("RGB")
# C: sem o rosto, vídeo de terceiros desfocado e escurecido
cl = R.grab("ter.mp4", 17.0, 480, 848); bgc = cv2.resize(cl, (W, int(848 * W / 480)))[: H, :]
bgc = cv2.copyMakeBorder(bgc, 0, max(0, H - bgc.shape[0]), 0, 0, cv2.BORDER_REFLECT); bgc = cv2.GaussianBlur(bgc, (0, 0), 14)
C = Image.fromarray((bgc.astype(np.float32) * 0.42 + np.array([4, 16, 30], np.float32) * 0.58).astype(np.uint8)).convert("RGBA")
tag(C, "COP31 · TURQUIA", 560); text(C, "LULA É", 720, MF("Black", 170)); text(C, "OVACIONADO", 880, MF("Black", 150), GOLD_L)
stamp(C, "VEJA A CENA", 1090, 120); text(C, "SEGUNDO A BNEWS", 1260, MF("ExtraBold", 50), WHITE, 5); finish(C).save("capa_D.jpg", quality=95)
print("ok")
