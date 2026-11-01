"""Vinheta de abertura das aulas: clipe do Gemini em 1080p + nome na tela + legenda + marca d'água + cartão final."""
import subprocess, json, math, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = "/tmp/claude-0/-home-user-next-netlify-starter/698dd744-d40f-5d96-b9e9-72023ae79dbf/scratchpad"; FD = S + "/fontdl"
W, H, FPS = 1920, 1080, 24; CLIP = 10.0; END = 2.8; TOT = CLIP + END; N = int(TOT * FPS)
YEL = (255, 214, 64); NAVY = (10, 26, 56); WHITE = (255, 255, 255); RED = (220, 40, 40); INK = (16, 22, 36)
def MF(w, s): return ImageFont.truetype(f"{FD}/Montserrat-{w}.ttf", s)
def ANTON(s): return ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s)
def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def back(x):
    x = min(max(x, 0), 1); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

SEG = json.load(open(S + "/v81/t.json"))
SEG[0]["text"] = "Olá, pessoal! Sejam bem-vindos à nossa aula."
SEG[2]["text"] = "Estou aqui"; SEG[3]["text"] = "para ajudar vocês."
WM = Image.open(S + "/canal/marca-dagua-150.png").convert("RGBA")
WM.putalpha(WM.getchannel("A").point(lambda a: int(a * 0.8)))
AV = Image.open(S + "/canal/foto-perfil-800.png").convert("RGBA")
cm = Image.new("L", AV.size, 0); ImageDraw.Draw(cm).ellipse((0, 0, AV.width - 1, AV.height - 1), fill=255)
AV.putalpha(cm)

def caption(im, t):
    d = ImageDraw.Draw(im); f = MF("ExtraBold", 50)
    for s in SEG:
        if s["start"] - 0.05 <= t <= s["end"] + 0.25:
            words = s["text"].split(); k = int((t - s["start"]) / max(s["end"] - s["start"], 0.1) * len(words))
            sp = f.getlength(" "); tw = sum(f.getlength(w) for w in words) + sp * (len(words) - 1)
            x = W / 2 - tw / 2; y = 985
            d.rounded_rectangle((x - 30, y - 42, x + tw + 30, y + 40), 22, fill=(0, 0, 0, 150))
            for i, w in enumerate(words):
                c = YEL if i == min(k, len(words) - 1) else WHITE
                d.text((x, y), w, font=f, fill=c, anchor="lm", stroke_width=3, stroke_fill=INK)
                x += f.getlength(w) + sp

def lower_third(im, t):
    a, b = 0.5, 5.2
    if not (a <= t <= b + 0.5): return
    p = ease((t - a) / 0.5) if t < b else 1 - ease((t - b) / 0.4)
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    off = int((1 - p) * -700); x0, y0 = 80 + off, 690
    d.rounded_rectangle((x0, y0, x0 + 300, y0 + 52), 26, fill=YEL + (255,))
    d.text((x0 + 150, y0 + 27), "ENGLISH CLASS", font=MF("ExtraBold", 28), fill=INK, anchor="mm")
    f = ANTON(96); tw = f.getlength("TEACHER ELIEZIO")
    d.rounded_rectangle((x0 - 10, y0 + 64, x0 + tw + 40, y0 + 188), 18, fill=NAVY + (235,))
    d.text((x0 + 14, y0 + 68), "TEACHER ", font=f, fill=WHITE)
    d.text((x0 + 14 + f.getlength("TEACHER "), y0 + 68), "ELIEZIO", font=f, fill=YEL)
    d.rectangle((x0 - 10, y0 + 64, x0 - 2, y0 + 188), fill=YEL + (255,))
    lay.putalpha(lay.getchannel("A").point(lambda v: int(v * min(1, p * 1.5))))
    im.alpha_composite(lay)

def end_card(last, t):
    u = t - CLIP; bg = last.filter(ImageFilter.GaussianBlur(4 + 18 * ease(u / 0.5)))
    arr = np.asarray(bg.convert("RGB"), np.float32); k = 0.35 * ease(u / 0.5)
    arr = arr * (1 - k) + np.array(NAVY, np.float32) * k * 1.0
    im = Image.fromarray(arr.astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(im)
    s = back((u - 0.1) / 0.5); r = int(190 * s)
    if r > 4:
        d.ellipse((W / 2 - r - 14, 330 - r - 14, W / 2 + r + 14, 330 + r + 14), fill=YEL + (255,))
        im.alpha_composite(AV.resize((2 * r, 2 * r), Image.LANCZOS), (int(W / 2 - r), int(330 - r))); d = ImageDraw.Draw(im)
    p = ease((u - 0.45) / 0.4)
    if p > 0:
        f = ANTON(130); tw = f.getlength("TEACHER ELIEZIO"); y = 580 + int((1 - p) * 40)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
        dl.text((W / 2 - tw / 2, y), "TEACHER ", font=f, fill=WHITE, stroke_width=6, stroke_fill=INK)
        dl.text((W / 2 - tw / 2 + f.getlength("TEACHER "), y), "ELIEZIO", font=f, fill=YEL, stroke_width=6, stroke_fill=INK)
        dl.text((W / 2, y + 200), "Inglês para o Fundamental e o Médio", font=MF("SemiBold", 40), fill=(220, 230, 250), anchor="mm")
        lay.putalpha(lay.getchannel("A").point(lambda v: int(v * p))); im.alpha_composite(lay); d = ImageDraw.Draw(im)
    q = back((u - 0.9) / 0.4)
    if q > 0.02:
        pulse = 1 + 0.04 * math.sin(max(u - 1.3, 0) * 7)
        bw, bh = int(420 * q * pulse), int(84 * q * pulse)
        d.rounded_rectangle((W / 2 - bw / 2, 870 - bh / 2, W / 2 + bw / 2, 870 + bh / 2), bh // 2, fill=RED + (255,))
        if q > 0.6: d.text((W / 2, 872), "INSCREVA-SE", font=MF("ExtraBold", int(40 * min(q, 1))), fill=WHITE, anchor="mm")
    return im

dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", S + "/v81/gem.mp4", "-vf", f"scale={W}:{H}:flags=lanczos,fps={FPS}",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", S + "/v81/vid.mp4"], stdin=subprocess.PIPE)
last = None
for i in range(N):
    t = i / FPS
    if t < CLIP:
        buf = dec.stdout.read(W * H * 3)
        if len(buf) == W * H * 3: last = Image.frombuffer("RGB", (W, H), buf).convert("RGBA")
        im = last.copy()
        fi = min(t / 0.4, 1)
        if fi < 1: im = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), im, fi)
        lower_third(im, t); caption(im, t); im.alpha_composite(WM, (W - WM.width - 40, 36))
        if t > CLIP - 0.25:  # flash branco na virada
            a = (t - (CLIP - 0.25)) / 0.25; im = Image.blend(im, Image.new("RGBA", (W, H), (255, 255, 255, 255)), a * 0.7)
    else:
        im = end_card(last, t)
        if t < CLIP + 0.2: im = Image.blend(Image.new("RGBA", (W, H), (255, 255, 255, 255)), im, (t - CLIP) / 0.2 * 0.3 + 0.7)
        if t > TOT - 0.35: im = Image.blend(im, Image.new("RGBA", (W, H), (0, 0, 0, 255)), (t - (TOT - 0.35)) / 0.35)
    enc.stdin.write(im.convert("RGB").tobytes())
enc.stdin.close(); enc.wait(); dec.kill(); print("ok", N)
