"""Série de Shorts virais 9:16 (~10 s, sem narração) do Teacher Eliezio, no formato dos canais de inglês que estouram (uma tela só,
para ler e rever em loop). Tipos: "troca" (básico ❌ → fluente ✅), "lista" (um item por linha) e "teste" (frases com IS/ARE e a
resposta revelada). Escolha o vídeo com a variável VIRAL=<nome>."""
import sys, os, math, re, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.path.insert(0, f"{S}/work")
import sfx
VIRAL = os.environ.get("VIRAL", "basico"); V = f"{S}/viral_{VIRAL}"; os.makedirs(V, exist_ok=True); FD = f"{S}/fontdl"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H, FPS = 1080, 1920, 30
CUT = (0.0, 0.0)
TOTAL = 10.5; VO_LEN = TOTAL
NAVY = (12, 28, 58); INK = (16, 22, 36); WHITE = (255, 255, 255); YEL = (255, 214, 64); YEL_D = (64, 48, 0)
C_AM = (236, 84, 84); C_IS = (64, 150, 255); C_ARE = (52, 190, 110); C_MOR = (255, 196, 60); C_AFT = (255, 140, 60); C_EVE = (150, 100, 220); C_NIG = (64, 110, 220); GREEN = (46, 184, 92); C_ING = (255, 214, 64); MUTED = (180, 196, 224); RED_B = (220, 40, 40)
def MF(w, s): return ImageFont.truetype(f"{FD}/Montserrat-{w}.ttf", s)
def ANTON(s): return ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def eio(x): x = clamp(x); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
def bo(x, s=1.7): x = clamp(x) - 1; return 1 + (s + 1) * x ** 3 + s * x ** 2
def env(t, a, b, fi=0.3, fo=0.25): return clamp((t - a) / fi) * clamp((b - t) / fo)
def fade(img, a):
    if a >= 1: return img
    img = img.copy(); img.putalpha(img.getchannel("A").point(lambda v: int(v * max(0, a)))); return img
def put(fr, im, x, y, al=1.0, sc=1.0):
    if al <= 0.01: return
    if abs(sc - 1) > 0.004: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
    fr.alpha_composite(fade(im, al), (int(x - im.width / 2), int(y - im.height / 2)))
def sput(fr, im, x, y, al=1.0, sc=1.0):
    if al <= 0.01: return
    if abs(sc - 1) > 0.004: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
    sh = Image.new("RGBA", (im.width + 60, im.height + 60), (0, 0, 0, 0)); blk = Image.new("RGBA", im.size, (0, 0, 0, 255)); blk.putalpha(im.getchannel("A").point(lambda v: int(v * 0.45)))
    sh.alpha_composite(blk, (30, 42)); sh = sh.filter(ImageFilter.GaussianBlur(14)); fr.alpha_composite(fade(sh, al), (int(x - im.width / 2 - 30), int(y - im.height / 2 - 30)))
    put(fr, im, x, y, al)
_tc = {}
def txt(t_, f, col, stroke=0, scol=INK):
    key = (t_, f.path, f.size, col, stroke)
    if key not in _tc:
        bb = f.getbbox(t_); im = Image.new("RGBA", (bb[2] - bb[0] + 20 + 2 * stroke, bb[3] - bb[1] + 20 + 2 * stroke), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10 - bb[0] + stroke, 10 - bb[1] + stroke), t_, font=f, fill=col + (255,), stroke_width=stroke, stroke_fill=scol + (255,)); _tc[key] = im
    return _tc[key]
def chip(t_, fill, col=WHITE, size=40, pad=26, rad=None):
    f = MF("ExtraBold", size); w = int(f.getlength(t_)) + pad * 2; h = int(size * 1.7)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), rad if rad is not None else h // 2, fill=fill + (255,)); d.text((w / 2, h / 2 + 1), t_, font=f, fill=col + (255,), anchor="mm"); return im
_emo = {}
def emoji(ch, size):
    key = (ch, size)
    if key not in _emo:
        f = ImageFont.truetype(EMOJI, 109); im = Image.new("RGBA", (180, 160), (0, 0, 0, 0)); ImageDraw.Draw(im).text((8, 8), ch, font=f, embedded_color=True)
        bb = im.getbbox(); im = im.crop(bb) if bb else im; sc = size / max(im.size); _emo[key] = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    return _emo[key]
# ---------------------------------------------------------------- fundo
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.38) / H) ** 2)
BG = np.array(NAVY, np.float32) + np.array([26, 52, 96], np.float32) * np.clip(1 - r * 1.5, 0, 1)[..., None]
for g in range(0, W, 60): BG[:, g:g + 1] += 6
for g in range(0, H, 60): BG[g:g + 1, :] += 6
BG = Image.fromarray(np.clip(BG, 0, 255).astype(np.uint8)).convert("RGBA"); del yy, xx, r
hd = ImageDraw.Draw(BG); hd.rounded_rectangle((300, 70, 780, 130), 30, fill=WHITE + (255,)); hd.text((540, 100), "ENGLISH CLASS · Teacher Eliezio", font=MF("ExtraBold", 24), fill=INK + (255,), anchor="mm")
# ---------------------------------------------------------------- avatar (1 sorrindo, 2 desconfiado, 7 surpreso, 8 piscando)
AV = [Image.open(f"{S}/v77/av3d_{k}.png").convert("RGBA").resize((360, 360), Image.LANCZOS) for k in range(1, 9)]
EXPR = [(0, 7), (0.8, 1), (7.8, 8), (9.0, 1)]
AMP = None
def amp_at(t):
    i = int(t * 100); return float(AMP[i]) if 0 <= i < len(AMP) else 0.0
def avatar(fr, t):
    cx, cy = 540, 1715; a = amp_at(t)
    i = max(k for k, e in enumerate(EXPR) if e[0] <= t); cur = EXPR[i][1]; prv = EXPR[i - 1][1] if i else cur; k = clamp((t - EXPR[i][0]) / 0.18)
    face = AV[cur - 1] if k >= 1 else Image.blend(AV[prv - 1], AV[cur - 1], k)
    rot = 2.0 * math.sin(t * 2.3) * (0.3 + a); face = face.rotate(rot, Image.BICUBIC) if abs(rot) > 0.05 else face
    bob = -10 * a + 3 * math.sin(t * 1.7); sc = 1 + 0.04 * a
    g = Image.new("RGBA", (480, 480), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse((40, 40, 440, 440), fill=YEL + (int(90 + 90 * a),)); put(fr, g.filter(ImageFilter.GaussianBlur(24)), cx, cy + bob, 1, sc)
    ring = Image.new("RGBA", (396, 396), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((0, 0, 395, 395), fill=YEL + (255,))
    put(fr, ring, cx, cy + bob, 1, sc); put(fr, face, cx, cy + bob, 1, sc)
# ---------------------------------------------------------------- palavras que se juntam
def boxword(w, f, fill):
    """palavra branca dentro de caixa colorida (forma comparativa)"""
    bb = f.getbbox(w); im = Image.new("RGBA", (bb[2] - bb[0] + 44, bb[3] - bb[1] + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), 22, fill=fill + (255,)); d.text((22 - bb[0], 20 - bb[1]), w, font=f, fill=WHITE + (255,)); return im
def suffix_join(fr, base, suf, t, a, t0, y, k, col):
    """BASE aparece em a; o sufixo cai do alto e encaixa no fim em t0 (TALL -> TALL|ER)"""
    if t < a: return
    f = ANTON(150); bi = txt(base, f, WHITE, 6); si = boxword(suf, f, col); g = eo((t - t0) / 0.4) if t >= t0 else 0
    tw = bi.width + (si.width - 10) * g; x0 = 540 - tw / 2; sc = 0.6 + 0.4 * bo((t - a) / 0.35, 2)
    if sc < 0.999: put(fr, bi, 540, y, k, sc); return
    put(fr, bi, x0 + bi.width / 2, y, k)
    if g > 0: sput(fr, si, x0 + bi.width - 10 + si.width / 2, y - 160 * (1 - g), k * min(1, g * 2))
def prefix_join(fr, base, pre, t, a, t0, y, k, col):
    """BASE aparece em a; MORE cai na frente em t0 e empurra a palavra"""
    if t < a: return
    f = ANTON(130); bi = txt(base, f, WHITE, 6); pi = boxword(pre, f, col); g = eo((t - t0) / 0.4) if t >= t0 else 0
    gap = 24; tw = bi.width + (pi.width + gap) * g; x0 = 540 - tw / 2; sc = 0.6 + 0.4 * bo((t - a) / 0.35, 2)
    if sc < 0.999: put(fr, bi, 540, y, k, sc); return
    put(fr, bi, x0 + (pi.width + gap) * g + bi.width / 2, y, k)
    if g > 0: sput(fr, pi, x0 + pi.width / 2, y - 160 * (1 - g), k * min(1, g * 2))
def pop(fr, im, x, y, t, a, k, shadow=True):
    if t < a: return
    (sput if shadow else put)(fr, im, x, y, k, 0.5 + 0.5 * bo((t - a) / 0.35, 2.2))
# ---------------------------------------------------------------- os vídeos da série
CFG = {
  "basico": dict(kind="troca", t1="PARE DE FALAR", t2="BÁSICO!", ha="BÁSICO", hb="FLUENTE", rows=[("Very good", "Awesome", "muito bom"), ("Very tired", "Exhausted", "muito cansado"),
             ("Very big", "Huge", "muito grande"), ("Very happy", "Thrilled", "muito feliz"), ("I don't know", "I have no idea", "não sei")]),
  "very": dict(kind="troca", t1="PARE DE FALAR", t2="VERY!", ha="BÁSICO", hb="FLUENTE", rows=[("Very cold", "Freezing", "muito frio"), ("Very hungry", "Starving", "com muita fome"),
             ("Very small", "Tiny", "muito pequeno"), ("Very beautiful", "Gorgeous", "muito bonito"), ("Very scared", "Terrified", "com muito medo")]),
  "brasileiro": dict(kind="troca", t1="BRASILEIRO FALA", t2="× NATIVO FALA", ha="BRASILEIRO", hb="NATIVO", rows=[("I have 20 years", "I'm 20 years old", "tenho 20 anos"),
             ("I am agree", "I agree", "eu concordo"), ("Make a question", "Ask a question", "fazer uma pergunta"), ("I'm boring", "I'm bored", "estou entediado"),
             ("I pretend to travel", "I plan to travel", "pretendo viajar")]),
  "obrigado": dict(kind="lista", t1="PARE DE FALAR SÓ", t2="THANK YOU!", sub="3 jeitos de agradecer em inglês", rows=[("Thanks a lot!", "muito obrigado!"),
             ("I really appreciate it.", "eu agradeço muito."), ("I owe you one!", "fico te devendo essa!")]),
  "isare": dict(kind="teste", t1="TESTE RÁPIDO:", t2="IS OU ARE?", rows=[("The kids ___ happy.", "ARE"), ("My mom ___ at home.", "IS"), ("There ___ two cars.", "ARE")]),
}
C = CFG[VIRAL]
RED_X = (226, 60, 60); OKG = (46, 184, 92)
def header(fr, t):
    f1 = ANTON(110 if len(C["t1"]) < 15 else 92); put(fr, txt(C["t1"], f1, WHITE, 7), 540, 250, 1, 0.9 + 0.1 * bo(t / 0.35))
    f2 = ANTON(150 if len(C["t2"]) < 10 else 110); put(fr, txt(C["t2"], f2, YEL, 8), 540, 390, 1, 0.85 + 0.15 * bo((t - 0.15) / 0.35))
def troca(fr, t):
    d = ImageDraw.Draw(fr)
    d.text((300, 545), C["ha"], font=MF("ExtraBold", 34), fill=(255, 140, 140, 255), anchor="mm"); d.text((780, 545), C["hb"], font=MF("ExtraBold", 34), fill=(140, 230, 160, 255), anchor="mm")
    for i, (bad, good, pt) in enumerate(C["rows"]):
        ta = 0.7 + i * 0.75; y = 640 + i * 148
        if t < ta: continue
        u = bo((t - ta) / 0.3, 2); g = clamp((t - ta - 0.25) / 0.3); fs = 40 if len(bad) < 14 else 32
        lb = chip(bad, (70, 40, 50), (255, 190, 190), fs, 22, 22); put(fr, lb, 290, y, 1, 0.6 + 0.4 * u)
        if g > 0:
            ImageDraw.Draw(fr).line((290 - lb.width / 2 + 14, y, 290 - lb.width / 2 + 14 + (lb.width - 28) * g, y), fill=RED_X + (255,), width=6)
            put(fr, txt("→", MF("ExtraBold", 54), YEL), 540, y, g)
        if t > ta + 0.35:
            v = bo((t - ta - 0.35) / 0.3, 2.2); put(fr, chip(good, OKG, WHITE, 44 if len(good) < 13 else 34, 24, 22), 790, y, 1, 0.5 + 0.5 * v)
            put(fr, txt(pt, MF("SemiBold", 24), (200, 214, 240), 2), 540, y + 52, clamp((t - ta - 0.5) / 0.3))
def lista(fr, t):
    put(fr, txt(C["sub"], MF("ExtraBold", 38), (200, 214, 240), 3), 540, 520, clamp((t - 0.4) / 0.3))
    for i, (en_, pt) in enumerate(C["rows"]):
        ta = 0.9 + i * 1.1; y = 700 + i * 210
        if t < ta: continue
        u = bo((t - ta) / 0.35, 2)
        put(fr, chip(str(i + 1), YEL, INK, 50, 26, 40), 150, y, 1, 0.5 + 0.5 * u)
        put(fr, chip(en_, OKG, WHITE, 50 if len(en_) < 16 else 40, 28, 24), 590, y, 1, 0.6 + 0.4 * u)
        put(fr, txt(pt, MF("SemiBold", 30), (200, 214, 240), 2), 590, y + 70, clamp((t - ta - 0.3) / 0.3))
def teste(fr, t):
    for i, (sent, ans) in enumerate(C["rows"]):
        ta = 0.8 + i * 2.2; rv = ta + 1.4; y = 620 + i * 240
        if t < ta: continue
        u = bo((t - ta) / 0.3, 2); shown = sent.replace("___", ans if t >= rv else "___")
        put(fr, txt(shown, MF("ExtraBold", 54), WHITE, 4), 540, y, 1, 0.7 + 0.3 * u)
        for j, opt in enumerate(("IS", "ARE")):
            ok = opt == ans; c = (OKG if ok else (70, 80, 100)) if t >= rv else (90, 104, 136)
            put(fr, chip(opt, c, WHITE, 44, 28, 22), 440 + j * 200, y + 85, 1 if (t < rv or ok) else 0.45, (1 + 0.08 * bo((t - rv) / 0.3, 3) - 0.08) if t >= rv and ok else 1)
        if ta + 0.4 <= t < rv:   # contadorzinho de 1 s
            n_ = 1; put(fr, txt("⏱", MF("ExtraBold", 10), YEL), 0, 0, 0)
            ImageDraw.Draw(fr).arc((850, y + 50, 920, y + 120), -90, -90 + 360 * (1 - (t - ta - 0.4) / 1.0), fill=YEL + (255,), width=8)
        if t >= rv: put(fr, emoji("✅", 56), 885, y + 85, 1, 0.5 + 0.5 * bo((t - rv) / 0.3, 2))
def frame_at(t):
    fr = BG.copy(); header(fr, t)
    {"troca": troca, "lista": lista, "teste": teste}[C["kind"]](fr, t)
    if t > T_SALVA: put(fr, chip("SALVA PRA REVISAR" if C["kind"] != "teste" else "QUANTAS VOCÊ ACERTOU? COMENTA!", YEL, INK, 38 if C["kind"] != "teste" else 32), 540, 1370, 1, (0.6 + 0.4 * bo((t - T_SALVA) / 0.35, 2.2)) * (1 + 0.03 * math.sin(t * 6)))
    if t > T_SIGA: put(fr, chip("SIGA @teachereliezio", WHITE, INK, 38), 540, 1450, 1, 0.6 + 0.4 * bo((t - T_SIGA) / 0.35, 2.2))
    avatar(fr, t); progress(fr, t); return fr.convert("RGB")
T_SALVA = {"troca": 5.0, "lista": 4.6, "teste": 7.6}[C["kind"]]; T_SIGA = T_SALVA + 1.8
TOTAL = {"troca": 10.5, "lista": 9.5, "teste": 10.5}[C["kind"]]; VO_LEN = TOTAL
def progress(fr, t):
    d = ImageDraw.Draw(fr); d.rounded_rectangle((60, 1880, 1020, 1892), 6, fill=(60, 84, 128, 255)); d.rounded_rectangle((60, 1880, 60 + 960 * clamp(t / TOTAL), 1892), 6, fill=YEL + (255,))
def capa(out): frame_at(TOTAL - 0.3).save(out, quality=95)
def load_amp():
    global AMP
    AMP = np.zeros(int(TOTAL * 100) + 10)
def audio(vout):
    SR = 48000; n = int(TOTAL * SR)
    def readw(p):
        w = wave.open(p); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; return x.reshape(-1, w.getnchannels())
    def writew(p, x):
        w = wave.open(p, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
    bed = readw(f"{S}/v49/bed.wav"); loop = bed
    while len(loop) < n: loop = np.concatenate([loop, bed])
    tl = np.arange(n) / SR; gain = 0.30 * np.clip(tl / 0.2, 0, 1) * np.clip((TOTAL - tl) / 0.4, 0, 1)
    writew(f"{V}/song.wav", loop[:n] * gain[:, None])
    ding = readw(f"{S}/v81/ding.wav"); k_ = C["kind"]
    if k_ == "troca": ev = [(0.7 + i * 0.75 + 0.25, sfx.click(seed=i), 0.25) for i in range(5)] + [(0.7 + i * 0.75 + 0.35, sfx.thud(0.25), 0.12) for i in range(5)]
    elif k_ == "lista": ev = [(0.9 + i * 1.1, sfx.thud(0.3), 0.18) for i in range(3)] + [(0.9 + i * 1.1, sfx.click(seed=i), 0.2) for i in range(3)]
    else: ev = [(0.8 + i * 2.2, sfx.click(seed=i), 0.2) for i in range(3)] + [(0.8 + i * 2.2 + 1.4, ding, 0.35) for i in range(3)]
    ev += [(0.05, sfx.whoosh(0.4), 0.18), (T_SALVA, sfx.click(seed=9), 0.2), (T_SIGA, sfx.click(seed=10), 0.2)]
    sfx.build(ev, TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    f"[1:a][2:a]amix=inputs=2:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.89:level=false[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
def main():
    load_amp()
    if MODE == "capa": capa(OUTFILE); return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(x).resize((360, 640), Image.LANCZOS) for x in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    NF = int(round(TOTAL * FPS))
    if MODE.startswith("part"):
        i, nparts = map(int, MODE.split(":")[1:]); a, b = NF * i // nparts, NF * (i + 1) // nparts
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", OUTFILE], stdin=subprocess.PIPE)
        for k in range(a, b): enc.stdin.write(frame_at(k / FPS).tobytes())
        enc.stdin.close(); enc.wait(); print("part done", i); return
    if MODE == "mux": audio(f"{V}/video.mp4"); print("done"); return
main()
