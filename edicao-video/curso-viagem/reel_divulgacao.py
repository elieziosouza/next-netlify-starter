"""Reel vertical de divulgação do curso Inglês para Viajar (08/11/2026).
Monta: capa parada 0,5 s (título + avatar + link na bio) → trecho da aula 16:9 dentro da moldura → cartão final "GOSTOU? LINK NA BIO" com a frase na voz dele.
Uso: python3 reel_divulgacao.py PASTA_PROMO VIDEO_AULA INICIO DURACAO "LINHA 1|LINHA 2" "🍽️🍗🥤" AVATAR.png CTA.mp3 SAIDA.mp4 CAPA.jpg"""
import sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont
P, SRC, A, DUR, TIT, EMO, AV, CTA, OUT, CAPA = sys.argv[1:11]; A, DUR = float(A), float(DUR)
FD = "/home/user/next-netlify-starter/edicao-video/assets/fonts"; W, H = 1080, 1920; YEL = (255, 214, 64)
def F(n, s): return ImageFont.truetype(f"{FD}/{n}.ttf", s)
ref = np.asarray(Image.open(f"{P}/frame_imigracao.png").convert("RGB"))
col = ref[:, 5, :].copy()
for y in range(240, 641): col[y] = col[239] + (col[641].astype(int) - col[239].astype(int)) * (y - 239) // 402
base = np.repeat(col[:, None, :], W, axis=1); base[:240] = ref[:240]; base[1450:] = ref[1450:]
def titulo(im):
    d = ImageDraw.Draw(im)
    for i, l in enumerate(TIT.split("|")):
        s = 130
        while d.textlength(l, font=F("Anton-Regular", s)) > W - 90: s -= 4
        f = F("Anton-Regular", s); w = d.textlength(l, font=f); d.text(((W - w) / 2, 270 + i * 150 + (130 - s) / 2), l, font=f, fill=YEL, stroke_width=8, stroke_fill=(16, 22, 38))
moldura = Image.fromarray(base.copy()); titulo(moldura); moldura.save(f"{P}/_moldura.png")
capa = Image.fromarray(base.copy()); titulo(capa); d = ImageDraw.Draw(capa)
cy = 1080; r = 250
d.ellipse((W / 2 - r - 22, cy - r - 22, W / 2 + r + 22, cy + r + 22), fill=(255, 214, 64, 255)); 
av = Image.open(AV).convert("RGBA").resize((2 * r - 20, 2 * r - 20)); capa.paste(av, (int(W / 2 - r + 10), int(cy - r + 10)), av)
ef = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109) if False else None
capa.convert("RGB").save(CAPA, quality=92)
def run(c): subprocess.run(c, check=True)
f = lambda x: f"{x:.3f}"
run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-t", "0.5", "-i", CAPA, "-ss", f(A), "-t", f(DUR), "-i", SRC, "-loop", "1", "-t", f(DUR), "-i", f"{P}/_moldura.png",
     "-loop", "1", "-t", "10.6", "-i", f"{P}/cta_card.png", "-i", CTA, "-f", "lavfi", "-t", "0.5", "-i", "anullsrc=r=48000:cl=stereo",
     "-filter_complex",
     f"[0:v]scale=1080:1920,fps=30,setsar=1,format=yuv420p[c0];"
     f"[1:v]scale=1080:-2,fps=30,setsar=1[v0];[2:v]fps=30,setsar=1[bg];[bg][v0]overlay=0:760:shortest=1,format=yuv420p,fade=t=out:st={f(DUR-0.3)}:d=0.3[p1];"
     f"[3:v]fps=30,setsar=1,format=yuv420p,fade=t=in:st=0:d=0.3[p2];[c0][p1][p2]concat=n=3:v=1:a=0[v];"
     f"[1:a]afade=t=out:st={f(DUR-0.4)}:d=0.4,aformat=sample_rates=48000:channel_layouts=stereo[a0];"
     f"[4:a]adelay=300|300,apad,atrim=0:10.6,aformat=sample_rates=48000:channel_layouts=stereo[a1];[5:a]aformat=sample_rates=48000:channel_layouts=stereo[a00];"
     f"[a00][a0][a1]concat=n=3:v=0:a=1,loudnorm=I=-14:TP=-1.5[a]",
     "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT])
print("ok", OUT)
