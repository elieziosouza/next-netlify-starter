"""Duas capas do vídeo de vendas (Teacher): A 'TRAVOU NO AEROPORTO?' e B 'INGLÊS PARA VIAJAR'. Texto dentro da faixa 3:4 (y 240-1680)."""
import sys, math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import video_vendas as V
W, H = 1080, 1920; YEL = V.YEL; WHITE = V.WHITE; NAVY = V.NAVY; INK = V.INK; F = V.F
def bg():
    return Image.fromarray(V.BG).convert("RGBA")
def avatar_ring(n, sz):
    ring = Image.new("RGBA", (sz + 50, sz + 50), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((0, 0, sz + 49, sz + 49), fill=YEL + (255,))
    av = V.AV[n].resize((sz, sz), Image.LANCZOS); m = Image.new("L", (sz, sz), 0); ImageDraw.Draw(m).ellipse((0, 0, sz - 1, sz - 1), fill=255); ring.paste(av, (25, 25), m)
    return V.shadowed(ring, 22, 14, .5)
def chip(fr, text, cy, fill=YEL, col=INK, size=44, pad=70):
    f = F("Montserrat-Black", size); tw = int(ImageDraw.Draw(Image.new("L", (4, 4))).textlength(text, font=f)) + pad * 2
    im = V.rrect(tw, int(size * 2.1), int(size * 1.05), fill + (255,)); ImageDraw.Draw(im).text((tw / 2, im.height / 2 + 2), text, font=f, fill=col + (255,), anchor="mm")
    V.put(fr, V.shadowed(im, 14, 8, .4), W / 2, cy)
def fit(text, fname, size, maxw):
    f = F(fname, size); d = ImageDraw.Draw(Image.new("L", (4, 4)))
    while d.textlength(text, font=f) > maxw: size -= 4; f = F(fname, size)
    return size
# A
A = bg(); V.header(A)
for i, (tx, col, sz) in enumerate((("TRAVOU NO", WHITE, 190), ("AEROPORTO?", YEL, 190))):
    sz = fit(tx, "Anton-Regular", sz, 900); V.put(A, V.txt(tx, F("Anton-Regular", sz), col, 10), W / 2, 420 + i * 215)
A.alpha_composite(avatar_ring(1, 470), (int(W / 2 - 260), 760))
V.put(A, V.emo("✈️", 130), 190, 1130, 1, 1, -12); V.put(A, V.emo("🛂", 130), 890, 1130, 1, 1, 10)
chip(A, "MINI CURSO · INGLÊS PARA VIAJAR", 1380, size=38, pad=50); chip(A, "LINK NA BIO", 1530, fill=WHITE, size=52)
A.convert("RGB").save("capa_A.jpg", quality=95)
# B
B = bg(); V.header(B)
V.put(B, V.txt("MINI CURSO", F("Montserrat-ExtraBold", 56), YEL, 0), W / 2, 330)
V.put(B, V.txt("INGLÊS", F("Anton-Regular", 250), WHITE, 10), W / 2, 520); V.put(B, V.txt("PARA VIAJAR", F("Anton-Regular", 190), YEL, 10), W / 2, 750)
B.alpha_composite(avatar_ring(1, 400), (int(W / 2 - 225), 900))
chip(B, "7 AULAS · PDFs · AULA 1 GRÁTIS", 1420, size=38, pad=50); chip(B, "LINK NA BIO", 1560, fill=WHITE, size=52)
B.convert("RGB").save("capa_B.jpg", quality=95)
sheet = Image.new("RGB", (720, 640)); sheet.paste(Image.open("capa_A.jpg").resize((360, 640)), (0, 0)); sheet.paste(Image.open("capa_B.jpg").resize((360, 640)), (360, 0)); sheet.save("capas_AB.jpg", quality=90); print("ok")
