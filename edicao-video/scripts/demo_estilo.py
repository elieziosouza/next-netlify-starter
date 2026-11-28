"""Demonstração das peças novas (referência enviada em 28/11/2026) aplicadas ao vídeo do Eliezio:
1 ícones em neon desenhados · 2 preto e branco com palavra colorida · 3 número subindo · 4 celulares flutuando com corações · 5 cartão de contato.
Transição com borrão de movimento entre os trechos. Uso: python3 demo_estilo.py SAIDA.mp4 | frames:t1,t2"""
import sys, math, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
K = "/home/user/next-netlify-starter/edicao-video"; sys.path.insert(0, K + "/scripts"); FD = K + "/assets/fonts"
import sfx
W, H, FPS = 1080, 1920, 30
GOLD = (214, 182, 116); GOLD_L = (245, 226, 176); NAVY = (6, 34, 58); WHITE = (255, 255, 255); NEON = (110, 215, 255); ORANGE = (255, 140, 20)
SEGS = [(0.0, 3.6, "ÍCONES EM NEON"), (12.4, 15.75, "PRETO E BRANCO + PALAVRA"), (38.2, 43.6, "NÚMERO SUBINDO"), (84.0, 89.9, "CELULARES FLUTUANDO"), (167.9, 171.1, "CARTÃO DE CONTATO")]
OFF = []; acc = 0.0
for a, b, _ in SEGS: OFF.append(acc); acc += b - a
TOTAL = acc
def F(n, s): return ImageFont.truetype(f"{FD}/{n}.ttf", s)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def back(x, s=1.6): x = clamp(x) - 1; return 1 + (s + 1) * x ** 3 + s * x ** 2
def grab(t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", "src.mp4", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(H, W, 3)
# ---------- 1 neon
def balao(cx, cy, w, h):
    pts = []; r = 40
    for k in range(0, 91, 10): a = math.radians(180 + k); pts.append((cx - w / 2 + r + r * math.cos(a), cy - h / 2 + r + r * math.sin(a)))
    for k in range(0, 91, 10): a = math.radians(270 + k); pts.append((cx + w / 2 - r + r * math.cos(a), cy - h / 2 + r + r * math.sin(a)))
    for k in range(0, 91, 10): a = math.radians(k); pts.append((cx + w / 2 - r + r * math.cos(a), cy + h / 2 - r + r * math.sin(a)))
    pts += [(cx - w * 0.05, cy + h / 2), (cx - w * 0.28, cy + h / 2 + 60), (cx - w * 0.22, cy + h / 2)]
    for k in range(90, 181, 10): a = math.radians(k); pts.append((cx - w / 2 + r + r * math.cos(a), cy + h / 2 - r + r * math.sin(a)))
    pts.append(pts[0]); return pts
def interrog(cx, cy, s):
    pts = [(cx + s * math.cos(math.radians(a)), cy - s * 0.6 + s * math.sin(math.radians(a))) for a in range(200, 361 + 80, 12)]
    pts += [(cx + s * 0.1, cy + s * 0.25), (cx, cy + s * 0.55)]; return pts
ICONS = [(0.15, balao(300, 520, 330, 210)), (0.55, balao(760, 300, 250, 160)), (0.9, [(230, 500), (370, 500)]), (1.0, [(230, 550), (330, 550)]), (1.25, [(700, 300), (712, 300)]), (1.35, [(760, 300), (772, 300)]), (1.45, [(820, 300), (832, 300)])]
def poly_part(pts, k):
    L = [0.0]
    for i in range(1, len(pts)): L.append(L[-1] + math.dist(pts[i - 1], pts[i]))
    tgt = L[-1] * k; out = [pts[0]]
    for i in range(1, len(pts)):
        if L[i] <= tgt: out.append(pts[i])
        else:
            f = (tgt - L[i - 1]) / max(1e-6, L[i] - L[i - 1]); out.append((pts[i - 1][0] + (pts[i][0] - pts[i - 1][0]) * f, pts[i - 1][1] + (pts[i][1] - pts[i - 1][1]) * f)); break
    return out
def neon(fr, u):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for t0, pts in ICONS:
        k = eo((u - t0) / 0.6)
        if k > 0:
            p = poly_part(pts, k)
            if len(p) > 1: d.line(p, fill=NEON + (255,), width=9, joint="curve")
    for txt, x, y, t0 in [("PAPO", 300, 365, 0.7), ("IDEIA", 760, 190, 1.1)]:
        a = eo((u - t0) / 0.3)
        if a > 0: d.text((x, y), txt, font=F("Montserrat-ExtraBold", 44), fill=NEON + (int(255 * a),), anchor="mm")
    flick = 0.85 + 0.15 * math.sin(u * 23) * math.sin(u * 7)
    glow = lay.filter(ImageFilter.GaussianBlur(14)); glow.putalpha(glow.getchannel("A").point(lambda v: int(min(255, v * 1.8 * flick))))
    fr.alpha_composite(glow); fr.alpha_composite(lay)
# ---------- 2 preto e branco
def pb(frame, u, tw):
    g = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY); g = cv2.convertScaleAbs(g, alpha=1.12, beta=-8)
    k = clamp((u - 0.05) / 0.25); return (frame * (1 - k) + np.dstack([g] * 3) * k).astype(np.uint8)
def palavra(fr, u, tw, txt):
    a = u - tw
    if a < 0: return
    s = max(0.05, back(a / 0.35)); f = F("Anton-Regular", 250); lay = Image.new("RGBA", (W, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text((W / 2, 210), txt, font=f, fill=GOLD + (255,), anchor="mm")
    sh = lay.copy(); sh.putalpha(sh.getchannel("A").point(lambda v: int(v * .5))); sh = sh.filter(ImageFilter.GaussianBlur(18))
    if s != 1: lay = lay.resize((int(W * s), int(420 * s)), Image.BICUBIC); sh = sh.resize(lay.size, Image.BICUBIC)
    fr.alpha_composite(sh, (int(W / 2 - lay.width / 2), int(330 - lay.height / 2 + 10))); fr.alpha_composite(lay, (int(W / 2 - lay.width / 2), int(330 - lay.height / 2)))
# ---------- 3 número subindo
def contador(fr, u, t0, val, sub):
    if u < t0 - 0.15: return
    k = eo((u - t0) / 1.0); n = int(round(val * k)); a = clamp((u - t0 + 0.15) / 0.2)
    d = ImageDraw.Draw(fr); y = 300 + 30 * (1 - eo((u - t0 + 0.15) / 0.3))
    pop = 1 + 0.08 * math.exp(-max(0, u - t0 - 1.0) * 8) if u > t0 + 1.0 else 1
    f = F("Anton-Regular", int(300 * pop)); d.text((W / 2 + 6, y + 8), str(n), font=f, fill=(0, 0, 0, int(120 * a)), anchor="mm")
    d.text((W / 2, y), str(n), font=f, fill=ORANGE + (int(255 * a),), anchor="mm")
    if u > t0 + 0.5: d.text((W / 2, y + 190), sub, font=F("Montserrat-Black", 74), fill=WHITE + (int(255 * clamp((u - t0 - 0.5) / 0.2)),), anchor="mm", stroke_width=5, stroke_fill=NAVY + (255,))
# ---------- 4 celulares
_cel = {}
def celular(t_src, rot):
    if t_src in _cel: return _cel[t_src]
    img = Image.fromarray(grab(t_src)).resize((236, 420)); wph, hph = 260, 470
    ph = Image.new("RGBA", (wph, hph), (0, 0, 0, 0)); d = ImageDraw.Draw(ph); d.rounded_rectangle((0, 0, wph - 1, hph - 1), 38, fill=(18, 18, 22, 255))
    m = Image.new("L", img.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, img.width - 1, img.height - 1), 28, fill=255); ph.paste(img, (12, 25), m)
    ImageDraw.Draw(ph).rounded_rectangle((95, 8, 165, 18), 5, fill=(0, 0, 0, 255))
    ph = ph.rotate(rot, resample=Image.BICUBIC, expand=True); _cel[t_src] = ph; return ph
def coracao(d, cx, cy, s, a):
    d.ellipse((cx - s, cy - s, cx + s, cy + s), fill=(235, 40, 60, int(255 * a)))
    r = s * 0.28; d.ellipse((cx - 2 * r, cy - 1.5 * r, cx, cy + 0.5 * r), fill=(255, 255, 255, int(255 * a))); d.ellipse((cx, cy - 1.5 * r, cx + 2 * r, cy + 0.5 * r), fill=(255, 255, 255, int(255 * a)))
    d.polygon([(cx - 2 * r, cy - 0.3 * r), (cx + 2 * r, cy - 0.3 * r), (cx, cy + 2 * r)], fill=(255, 255, 255, int(255 * a)))
def tela(t_src):
    if t_src in _cel: return _cel[t_src]
    img = Image.fromarray(grab(t_src)).resize((236, 420)); wph, hph = 260, 470
    ph = Image.new("RGBA", (wph, hph), (0, 0, 0, 0)); d = ImageDraw.Draw(ph); d.rounded_rectangle((0, 0, wph - 1, hph - 1), 38, fill=(18, 18, 22, 255))
    m = Image.new("L", img.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, img.width - 1, img.height - 1), 28, fill=255); ph.paste(img, (12, 25), m)
    ImageDraw.Draw(ph).rounded_rectangle((95, 8, 165, 18), 5, fill=(0, 0, 0, 255))
    body = Image.new("RGBA", (wph, hph), (0, 0, 0, 0)); ImageDraw.Draw(body).rounded_rectangle((0, 0, wph - 1, hph - 1), 38, fill=(70, 74, 84, 255))
    _cel[t_src] = (np.array(ph), np.array(body)); return _cel[t_src]
def proj(w, h, th, ph_, cx, cy, sc, dz=0.0):
    """cantos do retângulo w×h girado th (eixo Y) e ph_ (eixo X), em perspectiva"""
    f = 1500.0; out = []
    for x, y in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        x1 = x * math.cos(th); z1 = x * math.sin(th) + dz; y1 = y * math.cos(ph_) - z1 * math.sin(ph_); z2 = y * math.sin(ph_) + z1 * math.cos(ph_)
        out.append((cx + sc * x1 * f / (f + z2), cy + sc * y1 * f / (f + z2)))
    return np.float32(out)
def warp(rgba, quad):
    h, w = rgba.shape[:2]; M = cv2.getPerspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]), quad)
    return cv2.warpPerspective(rgba, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
def celulares(fr, u):
    lay = np.zeros((H, W, 4), np.uint8)
    for k, (ts, x, y, base, t0) in enumerate([(20.0, 240, 560, 24, 0.2), (130.0, 470, 360, -22, 0.6)]):
        a = u - t0
        if a < 0: continue
        sc = back(a / 0.55); th = math.radians(base + 12 * math.sin(u * 1.4 + k * 2)); ph_ = math.radians(8 * math.sin(u * 1.1 + k)); bob = 14 * math.sin(u * 2.0 + k)
        front, body = tela(ts)
        for dz in (16, 11, 6):   # espessura: camadas do corpo atrás da tela
            q = proj(260, 470, th, ph_, x, y + bob, sc, dz); lb = warp(body, q); al = lb[..., 3:4] / 255.0; lay[:] = (lb * al + lay * (1 - al)).astype(np.uint8)
        q = proj(260, 470, th, ph_, x, y + bob, sc); lf = warp(front, q)
        # brilho do vidro: faixa diagonal que passa conforme o giro
        gl = np.zeros((470, 260, 4), np.uint8); xx = np.arange(260)[None, :] + np.arange(470)[:, None] * 0.45; c = 130 + 120 * math.sin(th * 2.2)
        band = np.clip(1 - np.abs(xx - c) / 38, 0, 1); gl[..., :3] = 255; gl[..., 3] = (band * 70).astype(np.uint8); gl[..., 3] = np.minimum(gl[..., 3], front[..., 3])
        lg = warp(gl, q); al = lf[..., 3:4] / 255.0; lay[:] = (lf * al + lay * (1 - al)).astype(np.uint8)
        ag = lg[..., 3:4] / 255.0; lay[..., :3] = (lg[..., :3] * ag + lay[..., :3] * (1 - ag)).astype(np.uint8)
    im = Image.fromarray(lay, "RGBA")
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.getchannel("A").point(lambda v: int(v * .5))); sh = sh.filter(ImageFilter.GaussianBlur(22))
    fr.alpha_composite(sh, (14, 30)); fr.alpha_composite(im)
    d = ImageDraw.Draw(fr)
    for i in range(9):
        t0 = 0.9 + i * 0.45; a = u - t0
        if a < 0 or a > 2.2: continue
        cx = 120 + 60 * math.sin(i * 1.7) + 30 * math.sin(a * 3 + i); cy = 1150 - a * 330; s2 = 44 if i % 3 == 0 else 28
        coracao(d, cx, cy, s2 * back(a / 0.3), clamp((2.2 - a) / 0.6))
# ---------- 5 cartão de contato
_face = None
def cartao(fr, u):
    global _face
    if _face is None:
        f = Image.fromarray(grab(168.9)).crop((560, 400, 980, 820)).resize((140, 140)); m = Image.new("L", (140, 140), 0); ImageDraw.Draw(m).ellipse((0, 0, 139, 139), fill=255); _face = (f, m)
    a = u - 0.4
    if a < 0: return
    k = back(a / 0.55); x = W + 40 - (W + 40 - 120) * k; y = 300
    card = Image.new("RGBA", (840, 190), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, 839, 189), 95, fill=(255, 255, 255, 240), outline=GOLD + (255,), width=4)
    card.paste(_face[0], (25, 25), _face[1]); d.ellipse((23, 23, 167, 167), outline=GOLD + (255,), width=4)
    d.text((195, 62), "Eliezio Souza", font=F("Montserrat-ExtraBold", 52), fill=NAVY + (255,), anchor="lm")
    d.text((195, 128), "@eliezio.souza78", font=F("Montserrat-SemiBold", 40), fill=(60, 70, 90, 255), anchor="lm")
    b = clamp((u - 1.1) / 0.3)
    if b > 0: d.rounded_rectangle((650, 100, 820, 158), 29, fill=(206, 34, 40, int(255 * b))); d.text((735, 129), "SEGUIR", font=F("Montserrat-ExtraBold", 30), fill=WHITE + (int(255 * b),), anchor="mm")
    sh = Image.new("RGBA", card.size, (0, 0, 0, 0)); sh.putalpha(card.getchannel("A").point(lambda v: int(v * .4))); sh = sh.filter(ImageFilter.GaussianBlur(18))
    fr.alpha_composite(sh, (int(x), y + 16)); fr.alpha_composite(card, (int(x), y))
# ---------- etiqueta do exemplo e transição
def etiqueta(fr, i, u):
    a = eo(u / 0.3); txt = f"EXEMPLO {i + 1}  ·  {SEGS[i][2]}"; f = F("Montserrat-ExtraBold", 34); tw = int(f.getlength(txt)) + 60
    lay = Image.new("RGBA", (tw, 66), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); d.rounded_rectangle((0, 0, tw - 1, 65), 33, fill=NAVY + (225,), outline=GOLD + (255,), width=3)
    d.text((tw / 2, 34), txt, font=f, fill=GOLD_L + (255,), anchor="mm"); lay.putalpha(lay.getchannel("A").point(lambda v: int(v * a)))
    fr.alpha_composite(lay, (int(W / 2 - tw / 2), 70))
def borrao(img, k, sgn):
    if k <= 0.01: return img
    n = max(3, int(140 * k)) | 1; ker = np.zeros((n, n), np.float32); ker[n // 2, :] = 1.0 / n
    out = cv2.filter2D(img, -1, ker); M = np.float32([[1, 0, sgn * 160 * k], [0, 1, 0]])
    return cv2.warpAffine(out, M, (W, H), borderMode=cv2.BORDER_REFLECT)
FIT = 0.88; IMG_CX = 505
def caber(img):
    bg = cv2.resize(img, (W // 8, H // 8)); bg = cv2.GaussianBlur(bg, (0, 0), 4); bg = cv2.resize(bg, (W, H)); bg = (bg.astype(np.float32) * 0.72).astype(np.uint8)
    sw, sh = int(W * FIT), int(H * FIT); sm = cv2.resize(img, (sw, sh), interpolation=cv2.INTER_AREA); x0 = IMG_CX - sw // 2; y0 = H - sh; out = bg.copy()
    m = np.ones((sh, sw), np.float32); f = 40; r = np.linspace(0, 1, f); m[:, :f] *= r; m[:, -f:] *= r[::-1]; m[:f, :] *= r[:, None]
    reg = out[y0:y0 + sh, x0:x0 + sw]; mm = m[..., None]; reg[:] = (sm * mm + reg * (1 - mm)).astype(np.uint8); return out
def compose(i, u, src):
    a, b, _ = SEGS[i]; dur = b - a
    if i == 1: src = pb(src, u, 0)
    src = caber(src)
    k_in = clamp(1 - u / 0.2) if i > 0 else 0; k_out = clamp((u - (dur - 0.2)) / 0.2) if i < len(SEGS) - 1 else 0
    src = borrao(src, max(k_in, k_out), -1 if k_out > 0 else 1)
    fr = Image.fromarray(src).convert("RGBA")
    if i == 0: neon(fr, u)
    if i == 1: palavra(fr, u, 15.2 - a, "GUERRA?")
    if i == 2: contador(fr, u, 41.3 - a, 47, "ANOS")
    if i == 3: celulares(fr, u)
    if i == 4: cartao(fr, u)
    etiqueta(fr, i, u)
    return fr.convert("RGB")
def audio(out):
    ev = []
    for i, (a, b, _) in enumerate(SEGS):
        o = OFF[i]
        if i: ev.append((o - 0.15, sfx.whoosh(0.35), 0.22))
    ev += [(t, sfx.click(4), 0.18) for t in (0.15, 0.55, 0.95)]
    ev += [(OFF[1] + 15.2 - 12.4, sfx.thud(), 0.3)]
    ev += [(OFF[2] + 41.3 - 38.2 + k * 0.09, sfx.click(9), 0.10) for k in range(11)] + [(OFF[2] + 41.3 - 38.2 + 1.0, sfx.thud(), 0.3)]
    ev += [(OFF[3] + t, sfx.click(2), 0.16) for t in (0.2, 0.6)] + [(OFF[3] + 0.9 + k * 0.45, sfx.click(13), 0.07) for k in range(9)]
    ev += [(OFF[4] + 0.4, sfx.whoosh(0.3), 0.18), (OFF[4] + 1.1, sfx.click(5), 0.2)]
    sfx.build([(max(0.02, t), s, g) for t, s, g in ev], TOTAL + 0.5, "demo_sfx.wav")
    parts = "".join(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={b - a - 0.05}:d=0.05[a{i}];" for i, (a, b, _) in enumerate(SEGS))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "src.mp4", "-i", "demo_sfx.wav", "-filter_complex", parts + "".join(f"[a{i}]" for i in range(len(SEGS))) + f"concat=n={len(SEGS)}:v=0:a=1[v];[v][1:a]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5[o]", "-map", "[o]", "-ar", "48000", out], check=True)
def frames_of(i):
    a, b, _ = SEGS[i]; n = int(round((b - a) * FPS))
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-i", "src.mp4", "-frames:v", str(n), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    for k in range(n):
        raw = p.stdout.read(W * H * 3)
        if len(raw) < W * H * 3: break
        yield k / FPS, np.frombuffer(raw, np.uint8).reshape(H, W, 3).copy()
    p.stdout.close(); p.wait()
if __name__ == "__main__":
    arg = sys.argv[1]
    if arg.startswith("frames:"):
        for ts in arg[7:].split(","):
            t = float(ts); i = max(j for j in range(len(SEGS)) if OFF[j] <= t); u = t - OFF[i]
            compose(i, u, grab(SEGS[i][0] + u)).save(f"demo_{ts}.jpg", quality=86)
        sys.exit()
    audio("demo_mix.wav")
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "demo_mix.wav", "-map", "0:v", "-map", "1:a",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", arg], stdin=subprocess.PIPE)
    for i in range(len(SEGS)):
        for u, src in frames_of(i): enc.stdin.write(compose(i, u, src).tobytes())
    enc.stdin.close(); enc.wait(); print("ok", arg, round(TOTAL, 2))
