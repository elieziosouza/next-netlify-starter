"""Explicativo em colagem de papel (modelo do vídeo de referência, com a marca do canal): "Exército do Lula", narração do ElevenLabs.
Papel bege envelhecido, tiras rasgadas (azul-marinho, dourado, verde, kraft; vermelho só em detalhe), fotos P&B presas com fita,
celular com o canal, bilhetes de missão com ✓, contadores, calendário. Legenda karaokê da marca + caixa fixa + barra lateral.
Fatos checados (CNN, g1, Metrópoles, TSE). Frase de opinião marcada como opinião. Usa os ajudantes do render_exercito."""
import sys, math, subprocess, importlib.util, os, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("rex", f"{S}/work/render_exercito.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; eo = R.ease_out; ei = R.ease_in; bo = R.back_out
V = f"{S}/v73"; FD = f"{S}/fontdl"
VO_LEN = 81.32; EDIT_END = 81.45; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = EDIT_END; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
NAVY = R.NAVY; GOLD = R.GOLD; GOLD_L = R.GOLD_L; INK = (20, 20, 22); RED = (196, 34, 38); GREEN = (22, 120, 84); KRAFT = (190, 150, 100)
HL = (246, 206, 70); OFF = (244, 240, 230)
def ANTON(s): return ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s)
def HAND(s): return ImageFont.truetype(f"{FD}/CaveatBrush-Regular.ttf", s)
def SER(s): return ImageFont.truetype(f"{FD}/DMSerifDisplay-Regular.ttf", s)
MF = R.MF
rng = np.random.default_rng(7)

# ---------------------------------------------------------------- legenda karaokê (frases da narração, em blocos de até 4 palavras)
VO = json.load(open(f"{V}/vo_fix.json"))                        # texto revisado à mão (o Whisper errou nomes)
FIX = {"fúzil": "fuzil", "No dia seguinte.": "No dia seguinte,", "Um canal": "um canal"}
HOT = {"EXÉRCITO", "10", "MILHÕES", "PRIMEIRO", "TURNO", "WHATSAPP", "LULA.", "JANONES.", "MILHÃO", "MISSÕES.", "CONTRA-ATAQUE.", "TSE",
       "DERRUBADO.", "REATIVAR.", "PROPAGANDA.", "UTI", "ARRITMIA.", "MISSÃO.", "51,79%", "REELEITO", "GENERAL.", "AJUDA.", "EXÉRCITO?", "OPINIÃO,"}
CAPS = []
for sg in VO:
    txt = sg["text"]
    for a_, b_ in FIX.items(): txt = txt.replace(a_, b_)
    txt = txt.replace("10 milhões", "10 MILHÕES").replace("51,79%", "51,79%").replace('"', "").replace("'", "")
    ws = txt.upper().split(); n = len(ws); a, b = sg["start"], sg["end"]
    k = max(1, math.ceil(n / 4)); per = math.ceil(n / k); chunks = [ws[i:i + per] for i in range(0, n, per)]
    tot = sum(len(w) + 2 for w in ws); acc = 0
    for ch in chunks:
        c0 = a + (b - a) * acc / tot; ts = []
        for w in ch: ts.append(a + (b - a - 0.06) * acc / tot); acc += len(w) + 2
        c1 = a + (b - a) * acc / tot
        CAPS.append(dict(words=ch, ts=ts, start=c0, end=c1 + (0.25 if ch is chunks[-1] else 0.0), src="au" if any(w in HOT for w in ch) else "me"))
for i in range(len(CAPS) - 1): CAPS[i]["end"] = min(CAPS[i]["end"], CAPS[i + 1]["start"])
R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
CARD = ("ELEIÇÕES 2026", ["EXÉRCITO DO LULA:", "A HISTÓRIA DO CANAL"])
CAP_Y, CARD_Y = 1500, 1712

# ---------------------------------------------------------------- materiais (papel, tiras rasgadas, fita, blocos de texto, fotos)
def noise(h, w, s, amp):
    n = cv2.resize(rng.normal(0, 1, (max(2, h // s), max(2, w // s))).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC); return n * amp
def make_paper():
    base = np.ones((H, W, 3), np.float32) * np.array([226, 216, 196], np.float32)
    base += noise(H, W, 220, 9)[..., None] + noise(H, W, 40, 5)[..., None] + rng.normal(0, 5, (H, W, 1)).astype(np.float32)
    fib = np.zeros((H, W), np.float32)
    for _ in range(900):
        x, y = rng.integers(0, W), rng.integers(0, H); L_ = rng.integers(8, 40); a = rng.uniform(0, math.pi)
        cv2.line(fib, (int(x), int(y)), (int(x + L_ * math.cos(a)), int(y + L_ * math.sin(a))), float(rng.uniform(-14, 10)), 1)
    base += cv2.GaussianBlur(fib, (0, 0), 0.7)[..., None]
    for _ in range(14):                                               # manchas de envelhecimento
        m = np.zeros((H, W), np.float32); cv2.circle(m, (int(rng.integers(0, W)), int(rng.integers(0, H))), int(rng.integers(60, 260)), 1.0, -1)
        base -= cv2.GaussianBlur(m, (0, 0), 70)[..., None] * np.array([6, 9, 16], np.float32) * rng.uniform(0.4, 1.0)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2)
    base *= np.clip(1.06 - 0.55 * r ** 2, 0, 1.1)[..., None]
    return np.clip(base, 0, 255).astype(np.uint8)
PAPER = make_paper()
def torn_mask(w, h, edges="tb", amp=14, seed=0):
    g = np.random.default_rng(seed); m = Image.new("L", (w, h), 0); pts = []
    def jag(n, a): v = np.cumsum(g.normal(0, a * 0.45, n)); v = v - np.linspace(v[0], v[-1], n); return np.clip(v, -a, a) + g.uniform(-a * 0.4, a * 0.4, n)
    nx, ny = max(8, w // 14), max(8, h // 14)
    top = jag(nx, amp) if "t" in edges else np.zeros(nx); bot = jag(nx, amp) if "b" in edges else np.zeros(nx)
    lef = jag(ny, amp) if "l" in edges else np.zeros(ny); rig = jag(ny, amp) if "r" in edges else np.zeros(ny)
    for i in range(nx): pts.append((i * (w - 1) / (nx - 1), amp + top[i]))
    for i in range(ny): pts.append((w - 1 - amp - rig[i], i * (h - 1) / (ny - 1)))
    for i in range(nx - 1, -1, -1): pts.append((i * (w - 1) / (nx - 1), h - 1 - amp - bot[i]))
    for i in range(ny - 1, -1, -1): pts.append((amp + lef[i], i * (h - 1) / (ny - 1)))
    if "t" not in edges: pts = [(x, 0 if y <= amp + 0.1 else y) for x, y in pts]
    ImageDraw.Draw(m).polygon(pts, fill=255); return m
def strip(w, h, col, edges="tb", seed=0, tex=10):
    a = np.ones((h, w, 3), np.float32) * np.array(col, np.float32) + noise(h, w, 60, tex * 0.45)[..., None] + rng.normal(0, 4, (h, w, 1)).astype(np.float32)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"); m = torn_mask(w, h, edges, 16, seed)
    ma = np.asarray(m, np.float32); edge = ma - cv2.erode(ma, np.ones((7, 7), np.uint8))           # borda branca de papel rasgado
    rgb = np.asarray(im, np.float32); e_ = edge[..., None] / 255 * 0.85; rgb[..., :3] = rgb[..., :3] * (1 - e_) + np.array([236, 228, 212]) * e_
    im = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)); im.putalpha(m); return im
def tape(w=150, h=46, rot=0):
    a = np.ones((h, w, 4), np.float32) * np.array([232, 222, 190, 170], np.float32); a[..., :3] += noise(h, w, 6, 6)[..., None]
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)); m = torn_mask(w, h, "lr", 5, int(w + h)); m = Image.fromarray((np.asarray(m) * 0.72).astype(np.uint8)); im.putalpha(m)
    return im.rotate(rot, Image.BICUBIC, expand=True)
def block(txt, size, fg=INK, bg=OFF, pad=(28, 14), font=None, hl=None, rot=0, torn=True):
    f = font or ANTON(size); bb = f.getbbox(txt); tw, th = bb[2] - bb[0], bb[3] - bb[1]
    w, h = tw + pad[0] * 2, th + pad[1] * 2 + 8
    a = np.ones((h, w, 3), np.float32) * np.array(bg, np.float32) + rng.normal(0, 3, (h, w, 1)).astype(np.float32)
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(im)
    if hl: d.rectangle((pad[0] - 8, h // 2 - th * 0.05, pad[0] + tw + 8, h - pad[1] + 2), fill=hl + (255,))
    d.text((pad[0] - bb[0], pad[1] - bb[1] + 4), txt, font=f, fill=fg + (255,))
    if torn: im.putalpha(torn_mask(w, h, "lrtb", 3, len(txt) * 7 + size))
    return im.rotate(rot, Image.BICUBIC, expand=True) if rot else im
def textlay(txt, font, col, rot=0, stroke=0, scol=None):
    bb = font.getbbox(txt); im = Image.new("RGBA", (bb[2] - bb[0] + 20 + stroke * 2, bb[3] - bb[1] + 20 + stroke * 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10 - bb[0] + stroke, 10 - bb[1] + stroke), txt, font=font, fill=col + (255,), stroke_width=stroke, stroke_fill=(scol or col) + (255,))
    return im.rotate(rot, Image.BICUBIC, expand=True) if rot else im
def bw_photo(path, w, h, focus=0.3, color=False):
    src = Image.open(path).convert("RGB"); sc = max(w / src.width, h / src.height); im = src.resize((int(src.width * sc) + 1, int(src.height * sc) + 1), Image.LANCZOS)
    x0 = (im.width - w) // 2; y0 = int((im.height - h) * focus); im = np.asarray(im.crop((x0, y0, x0 + w, y0 + h)), np.float32)
    if not color:
        g = im @ np.array([0.3, 0.59, 0.11]); g = np.clip((g - 128) * 1.25 + 128, 0, 255); im = np.repeat(g[..., None], 3, 2) * np.array([1.0, 0.98, 0.93])
    im += rng.normal(0, 7, (h, w, 1)); return Image.fromarray(np.clip(im, 0, 255).astype(np.uint8))
def polaroid(path, w, h, cap=None, sub=None, rot=0, focus=0.3, color=False, tapes=True):
    ph = bw_photo(path, w, h, focus, color); bt = 92 if cap else 26; card = Image.new("RGBA", (w + 36, h + 18 + bt), OFF + (255,))
    card.paste(ph, (18, 18)); d = ImageDraw.Draw(card)
    if cap:
        fs = 40
        while ANTON(fs).getlength(cap) > card.width - 24: fs -= 2
        d.text((card.width / 2, h + 18 + (36 if sub else bt / 2)), cap, font=ANTON(fs), fill=INK + (255,), anchor="mm")
    if sub: d.text((card.width / 2, h + 18 + 72), sub, font=SER(26), fill=(70, 66, 60, 255), anchor="mm")
    if tapes:
        t = tape(140, 44, -6); card2 = Image.new("RGBA", (card.width, card.height + 26), (0, 0, 0, 0)); card2.alpha_composite(card, (0, 26))
        card2.alpha_composite(t, (card.width // 2 - t.width // 2, 0)); card = card2
    return card.rotate(rot, Image.BICUBIC, expand=True) if rot else card
def stamp(txt, size, col, rot=-8):
    f = ANTON(size); bb = f.getbbox(txt); w, h = bb[2] - bb[0] + 60, bb[3] - bb[1] + 50
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, w - 5, h - 5), 10, outline=col + (255,), width=8); d.text((30 - bb[0], 25 - bb[1]), txt, font=f, fill=col + (255,))
    a = np.asarray(im).copy(); holes = (rng.random(a.shape[:2]) < 0.10) | (noise(h, w, 5, 1) > 1.1); a[..., 3] = np.where(holes, a[..., 3] * 0.25, a[..., 3])
    return Image.fromarray(a).rotate(rot, Image.BICUBIC, expand=True)
def note(num, lines, rot=0):
    w, h = 300, 300; a = np.ones((h, w, 3), np.float32) * np.array([248, 246, 238], np.float32)
    for y in range(96, h, 40): a[y:y + 2] = (200, 214, 230)
    im = Image.fromarray(np.clip(a + rng.normal(0, 3, (h, w, 1)), 0, 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(im)
    d.text((24, 44), f"MISSÃO {num:02d}", font=ANTON(38), fill=RED + (255,), anchor="lm"); d.line((24, 74, 200, 74), fill=RED + (255,), width=3)
    for i, l in enumerate(lines): d.text((24, 112 + i * 42), l, font=ANTON(36), fill=INK + (255,), anchor="lm")
    t = tape(120, 40, 4); c = Image.new("RGBA", (w, h + 22), (0, 0, 0, 0)); c.alpha_composite(im, (0, 22)); c.alpha_composite(t, (w // 2 - t.width // 2, 0))
    return c.rotate(rot, Image.BICUBIC, expand=True)
def phone(state="normal"):
    w, h = 400, 780; im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 54, fill=(24, 26, 30, 255)); d.rounded_rectangle((14, 14, w - 15, h - 15), 42, fill=(240, 236, 228, 255))
    d.rounded_rectangle((w / 2 - 60, 26, w / 2 + 60, 50), 12, fill=(24, 26, 30, 255))
    d.rectangle((14, 64, w - 15, 158), fill=(20, 94, 70, 255)); d.ellipse((34, 82, 94, 142), fill=GOLD + (255,)); d.text((64, 112), "EL", font=ANTON(30), fill=NAVY + (255,), anchor="mm")
    d.text((110, 98), "Exército do Lula", font=MF("Bold", 28), fill=(255, 255, 255, 255), anchor="lm"); d.text((110, 130), "Canal", font=MF("Medium", 22), fill=(210, 240, 225, 255), anchor="lm")
    def bubble(y, h_, title, body):
        d.rounded_rectangle((32, y, w - 32, y + h_), 16, fill=(255, 255, 255, 255))
        d.text((52, y + 26), title, font=MF("ExtraBold", 21), fill=(20, 110, 80, 255), anchor="lm")
        for i, l in enumerate(body): d.text((52, y + 62 + i * 30), l, font=MF("Medium", 20), fill=(60, 60, 64, 255), anchor="lm")
    bubble(186, 150, "MISSÃO DO DIA", ["Compartilha o vídeo", "em 5 grupos de família."])
    d.rounded_rectangle((32, 358, w - 32, 540), 16, fill=(40, 42, 48, 255)); d.polygon([(w / 2 - 26, 412), (w / 2 - 26, 486), (w / 2 + 34, 449)], fill=(255, 255, 255, 255))
    bubble(562, 150, "MISSÃO DO DIA", ["Comenta no post e", "traz mais um pro canal."])
    if state == "off":
        ov = Image.new("RGBA", (w - 28, h - 28), (0, 0, 0, 0)); ImageDraw.Draw(ov).rounded_rectangle((0, 0, w - 29, h - 29), 42, fill=(30, 30, 34, 200)); im.alpha_composite(ov, (14, 14))
    return im
def arrow(w=180, h=70, col=INK):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); pts = [(6, h * 0.6), (w * 0.4, h * 0.45), (w * 0.75, h * 0.5), (w - 12, h * 0.42)]
    d.line(pts, fill=col + (255,), width=6, joint="curve"); d.line([(w - 12, h * 0.42), (w - 44, h * 0.12)], fill=col + (255,), width=6); d.line([(w - 12, h * 0.42), (w - 40, h * 0.78)], fill=col + (255,), width=6)
    return im
def calendar():
    w, h = 300, 330; im = Image.new("RGBA", (w, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((0, 20, w - 1, h + 19), fill=OFF + (255,)); d.rectangle((0, 20, w - 1, 100), fill=RED + (255,))
    for x in (70, w - 70): d.rounded_rectangle((x - 8, 0, x + 8, 44), 6, fill=(60, 60, 60, 255))
    d.text((w / 2, 62), "OUTUBRO", font=ANTON(46), fill=(255, 255, 255, 255), anchor="mm"); d.text((w / 2, 215), "25", font=ANTON(170), fill=INK + (255,), anchor="mm")
    d.text((w / 2, 318), "DOMINGO", font=ANTON(36), fill=(90, 86, 80, 255), anchor="mm"); return im
IMGS = {"lula": f"{S}/v61/dl/lula.jpg", "flavio": f"{S}/v61/dl/flavio.jpg", "janones": f"{V}/dl/janones.jpg", "nunes": f"{V}/dl/nunes.jpg", "lula2": f"{S}/v71/lula.jpg"}

# ---------------------------------------------------------------- linha do tempo: cenas e elementos
# elemento: dict(t=entrada, out=saída (fim da cena), img, x, y (centro), anim: pop|slide_l|slide_r|slide_u|drop|stamp, z)
SCENES = [(0.0, 6.95), (6.95, 12.45), (12.45, 19.35), (19.35, 27.0), (27.0, 36.3), (36.3, 46.85), (46.85, 50.25), (50.25, 57.9), (57.9, 66.9), (66.9, 70.45), (70.45, 82.0)]
EL = []; FX = []      # FX: riscos, ✓, contadores (desenho por quadro)
def add(t, img, x, y, anim="pop", scene=None, z=0):
    sc = scene if scene is not None else max(i for i, s in enumerate(SCENES) if s[0] <= t + 1e-6)
    EL.append(dict(t=t, out=SCENES[sc][1], img=img, x=x, y=y, anim=anim, z=z, sc=sc))
def strike(t, dur, x0, y0, x1, y1, col=RED, w=12, sc=None):
    s_ = sc if sc is not None else max(i for i, s in enumerate(SCENES) if s[0] <= t + 1e-6); FX.append(dict(kind="strike", t=t, dur=dur, p=(x0, y0, x1, y1), col=col, w=w, out=SCENES[s_][1]))
def check(t, x, y, size=70, col=RED):
    s_ = max(i for i, s in enumerate(SCENES) if s[0] <= t + 1e-6); FX.append(dict(kind="check", t=t, dur=0.3, p=(x, y, size), col=col, w=10, out=SCENES[s_][1]))
def counter(t, dur, v0, v1, x, y, fmt, size=150, sub=None, out=None):
    s_ = max(i for i, s in enumerate(SCENES) if s[0] <= t + 1e-6); FX.append(dict(kind="count", t=t, dur=dur, v=(v0, v1), p=(x, y), fmt=fmt, size=size, sub=sub, out=out or SCENES[s_][1]))
L0 = 150                                                    # margem esquerda útil (depois da barra)
# 1 · o maior exército
add(0.0, strip(900, 1150, NAVY, "lr", 1), 640, 820, "slide_u", z=-2)
add(0.1, block("O MAIOR", 70, bg=INK, fg=(255, 255, 255)), 380, 330, "pop")
add(0.35, block("EXÉRCITO", 150, hl=None), 560, 470, "pop")
add(0.65, block("DO BRASIL", 90, bg=GOLD, fg=NAVY, rot=-2), 700, 610, "pop")
add(1.55, block("NÃO TEM TANQUE", 84, rot=1), 600, 820, "pop"); strike(1.95, 0.35, 395, 822, 840, 812)
add(2.85, block("NÃO TEM FUZIL", 84, rot=-1), 600, 960, "pop"); strike(3.25, 0.35, 395, 962, 820, 970)
counter(4.3, 1.8, 0, 10_000_000, 600, 1150, lambda v: f"{v:,.0f}".replace(",", "."), 128, "DE SOLDADOS")
# 2 · primeiro turno
add(6.95, strip(1080, 700, KRAFT, "tb", 2), 540, 900, "slide_l", z=-2)
add(7.2, block("4 DE OUTUBRO", 46, bg=INK, fg=(255, 255, 255)), 380, 300, "pop")
add(8.75, block("PRIMEIRO TURNO", 104, hl=HL, rot=-1.5), 600, 420, "pop")
add(9.95, polaroid(IMGS["lula"], 300, 330, "LULA", None, -5, 0.15), 410, 860, "drop")
add(10.4, polaroid(IMGS["flavio"], 300, 330, "FLÁVIO BOLSONARO", None, 4, 0.15), 790, 820, "drop")
add(11.0, stamp("2º", 80, RED, 10), 260, 640, "stamp"); add(11.3, stamp("1º", 80, NAVY, -8), 930, 600, "stamp")
add(10.0, textlay("por pouco", HAND(60), INK, 4), 600, 1180, "pop")
# 3 · um canal de WhatsApp
add(12.45, strip(560, 1300, GREEN, "lr", 3), 760, 860, "slide_u", z=-2)
add(12.6, block("5 DE OUTUBRO", 46, bg=INK, fg=(255, 255, 255)), 380, 300, "pop")
add(13.7, phone(), 760, 870, "slide_u")
add(14.6, block("CENTRAL DE", 64, rot=-3), 360, 620, "pop"); add(15.2, block("MOBILIZAÇÃO", 64, hl=HL, rot=-3), 380, 710, "pop")
add(17.0, textlay("o nome:", HAND(64), INK, 5), 330, 940, "pop")
add(17.8, block("EXÉRCITO DO LULA", 92, bg=GOLD, fg=NAVY, rot=-2), 600, 1180, "pop")
# 4 · o general e o crescimento
add(19.35, strip(1080, 620, NAVY, "tb", 4), 540, 560, "slide_r", z=-2)
add(19.45, block("O GENERAL", 70, bg=INK, fg=(255, 255, 255), rot=-2), 400, 330, "pop")
add(20.4, polaroid(IMGS["janones"], 330, 380, "ANDRÉ JANONES", "deputado federal (MG)", -4, 0.12), 400, 720, "drop")
add(21.9, block("EM MENOS DE 2 DIAS", 54, hl=HL, rot=2), 790, 400, "pop")
counter(22.6, 0.01, 50_000, 50_000, 790, 600, lambda v: "50 MIL", 110)
add(23.9, arrow(160, 80), 790, 730, "pop")
counter(24.6, 1.6, 50_000, 1_000_000, 790, 880, lambda v: f"{v:,.0f}".replace(",", ".") if v < 1_000_000 else "+1 MILHÃO", 96, "PESSOAS NO CANAL")
add(26.0, stamp("EM 2 DIAS", 70, RED, -9), 760, 1130, "stamp")
# 5 · o segredo: missões
add(27.0, strip(1080, 520, KRAFT, "tb", 5), 540, 1000, "slide_l", z=-2)
add(27.05, block("O SEGREDO", 100, bg=INK, fg=(255, 255, 255)), 470, 330, "pop")
add(28.2, block("PEDIR VOTO", 70, rot=-1), 420, 480, "pop"); strike(28.65, 0.35, 260, 488, 590, 474)
add(29.7, block("ELE DAVA", 70), 420, 610, "pop"); add(30.0, block("MISSÕES", 92, hl=HL, rot=-2), 760, 610, "pop")
add(31.2, note(1, ["COMPARTILHA", "ESSE VÍDEO"], -4), 300, 1000, "drop"); check(32.1, 380, 1110)
add(32.9, note(2, ["COMENTA", "NAQUELE", "POST"], 3), 610, 990, "drop"); check(33.8, 690, 1110)
add(34.6, note(3, ["TRAZ MAIS", "GENTE PRO", "CANAL"], -2), 900, 1010, "drop"); check(35.5, 975, 1130)
# 6 · contra-ataque
add(36.3, strip(1080, 230, RED, "tb", 6), 540, 330, "slide_r", z=-2)
add(36.45, textlay("CONTRA-ATAQUE", ANTON(110), (255, 255, 255)), 600, 330, "pop")
add(38.1, polaroid(IMGS["flavio"], 260, 290, "CAMPANHA DE FLÁVIO", None, -4, 0.15), 360, 680, "drop")
add(39.2, arrow(170, 80, RED), 590, 640, "pop"); add(39.5, block("TSE", 110, bg=NAVY, fg=(255, 255, 255), rot=3), 790, 640, "pop")
add(40.8, block("11 DE OUTUBRO", 46, bg=INK, fg=(255, 255, 255)), 390, 960, "pop")
add(41.0, polaroid(IMGS["nunes"], 240, 260, "NUNES MARQUES", "ministro do TSE", 3, 0.1), 380, 1180, "drop")
add(41.5, phone("off").resize((230, 448), Image.LANCZOS).rotate(-4, Image.BICUBIC, expand=True), 800, 1000, "slide_u")
add(42.1, stamp("DERRUBADO", 58, RED, -12), 800, 960, "stamp")
add(43.3, block("NO MESMO DIA", 50, hl=HL, rot=-2), 800, 1290, "pop", scene=5)
add(45.4, stamp("REATIVADO", 58, GREEN, 8), 800, 1080, "stamp", scene=5)
# 7 · efeito contrário
add(46.85, strip(1080, 420, INK, "tb", 7), 540, 1100, "slide_l", z=-2)
add(47.0, block("EFEITO CONTRÁRIO", 96, rot=-1.5), 600, 420, "pop")
add(47.4, textlay("cada tentativa de calar", HAND(70), INK, 0), 640, 640, "pop")
add(48.9, textlay("virou", HAND(70), INK, 0), 400, 760, "pop"); add(49.5, textlay("e o canal só cresceu", HAND(80), (255, 255, 255), -2), 600, 1100, "pop"); add(49.2, block("PROPAGANDA", 80, hl=HL, rot=2), 740, 770, "pop")
# 8 · UTI
add(50.25, strip(820, 900, (30, 30, 34), "tblr", 8), 600, 830, "slide_u", z=-2)
add(50.35, block("DEBATE DA BAND", 50, bg=OFF, fg=INK), 420, 330, "pop")
add(51.0, polaroid(IMGS["janones"], 340, 390, "ANDRÉ JANONES", None, 3, 0.12), 600, 760, "drop")
add(52.4, block("UTI", 120, bg=RED, fg=(255, 255, 255), rot=-6), 330, 1100, "pop"); add(53.4, textlay("arritmia", HAND(80), (255, 255, 255), -4), 640, 1110, "pop")
add(55.6, block("SAIU DO HOSPITAL", 56, rot=2), 640, 1230, "pop"); add(56.4, stamp("VOLTOU PRA MISSÃO", 58, GREEN, -6), 640, 1350, "stamp")
# 9 · 25 de outubro
add(57.9, strip(560, 1300, GREEN, "lr", 9), 400, 860, "slide_l", z=-2); add(57.95, strip(520, 1300, GOLD, "lr", 10), 860, 860, "slide_r", z=-2)
add(58.05, calendar(), 330, 470, "drop"); add(58.6, block("2º TURNO", 50, bg=INK, fg=(255, 255, 255), rot=-3), 330, 700, "pop")
add(59.8, polaroid(IMGS["lula2"], 360, 400, "LULA", None, 4, 0.12, color=True), 780, 640, "drop")
add(60.6, stamp("REELEITO", 84, RED, -8), 780, 950, "stamp")
counter(61.6, 2.2, 50.0, 51.79, 560, 1130, lambda v: f"{v:.2f}%".replace(".", ","), 150, "DOS VOTOS VÁLIDOS")
# 10 · mais de 10 milhões e o "general"
add(66.9, strip(1080, 640, NAVY, "tb", 11), 540, 620, "slide_r", z=-2)
counter(65.0, 1.8, 0, 10_000_000, 600, 560, lambda v: "+" + f"{v:,.0f}".replace(",", "."), 120, "PESSOAS NO CANAL", out=70.45)
add(67.5, polaroid(IMGS["lula"], 230, 250, None, None, -6, 0.15), 360, 980, "drop"); add(67.8, polaroid(IMGS["janones"], 230, 250, None, None, 5, 0.12), 820, 980, "drop")
add(68.4, textlay("“GENERAL”", ANTON(110), INK, -3), 590, 1240, "pop")
# 11 · a pergunta e o fechamento
add(70.45, strip(1080, 300, GREEN, "tb", 12), 540, 700, "slide_l", z=-2)
add(70.6, block("NA MINHA OPINIÃO", 48, bg=INK, fg=(255, 255, 255)), 420, 320, "pop")
add(73.75, block("UM CANAL DE", 66, rot=-1), 470, 560, "pop"); add(74.3, textlay("WHATSAPP", ANTON(130), (255, 255, 255)), 600, 700, "pop")
add(75.2, block("AJUDA A ELEGER", 66, rot=1), 600, 860, "pop"); add(75.9, block("UM PRESIDENTE?", 66, hl=HL, rot=-1), 640, 970, "pop")
add(77.1, stamp("AJUDA.", 150, RED, -8), 610, 1180, "stamp")
add(78.1, textlay("e você, entrou pro exército?", HAND(66), INK, -2), 610, 1350, "pop")
CREDIT = [(9.9, 12.45, "Fotos: Wikimedia Commons (Agência Senado / Ricardo Stuckert-PR)"), (20.4, 27.0, "Foto: Wikimedia Commons (TSE)"),
          (41.0, 46.85, "Fotos: Wikimedia Commons (TSE / STF)"), (51.0, 57.9, "Foto: Wikimedia Commons (TSE)"), (59.8, 66.9, "Foto: Ricardo Stuckert-PR")]
EL.sort(key=lambda e: (e["z"], e["t"]))

# ---------------------------------------------------------------- desenho por quadro
_cnt = {}
def anim_xy(e, t):
    u = t - e["t"]; outk = ei((t - (e["out"] - 0.22)) / 0.22) if t > e["out"] - 0.22 else 0.0
    jit = int(t * 12)                                                      # leve tremido de stop motion (12 qps)
    j = np.random.default_rng(jit * 131 + int(e["x"] * 7 + e["y"])); jx, jy, jr = j.uniform(-1.6, 1.6), j.uniform(-1.6, 1.6), j.uniform(-0.35, 0.35)
    sc, al, dx, dy, rot = 1.0, 1.0, 0.0, 0.0, jr
    a = e["anim"]
    if a == "pop": k = bo(u / 0.28, 2.0); sc = 0.4 + 0.6 * k; al = clamp(u / 0.08)
    elif a == "drop": k = eo(u / 0.35); dy = -260 * (1 - k); rot += 10 * (1 - k); al = clamp(u / 0.1)
    elif a == "stamp": k = clamp(u / 0.16); sc = 1.9 - 0.9 * eo(k); al = clamp(u / 0.06)
    elif a in ("slide_l", "slide_r", "slide_u"):
        k = eo(u / 0.38); off = 1 - k
        if a == "slide_l": dx = -1300 * off
        elif a == "slide_r": dx = 1300 * off
        else: dy = 1500 * off
    sc *= 1 - 0.15 * outk; al *= 1 - outk; dy += 60 * outk
    return sc, al, dx + jx, dy + jy, rot
def put(fr, img, cx, cy, sc=1.0, al=1.0, rot=0.0, shadow=0.45):
    if al <= 0.01 or sc <= 0.02: return
    im = img
    if abs(sc - 1) > 0.004: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
    if abs(rot) > 0.05: im = im.rotate(rot, Image.BICUBIC, expand=True)
    R.paste(fr, R.fade(im, al), cx - im.width / 2, cy - im.height / 2, shadow * al, 10, (5, 12))
def draw_fx(fr, t):
    d = ImageDraw.Draw(fr)
    for f in FX:
        if t < f["t"] or t >= f["out"]: continue
        outk = ei((t - (f["out"] - 0.22)) / 0.22) if t > f["out"] - 0.22 else 0.0; u = clamp((t - f["t"]) / max(f["dur"], 1e-3))
        if f["kind"] == "strike":
            x0, y0, x1, y1 = f["p"]; k = eo(u); xm, ym = x0 + (x1 - x0) * k, y0 + (y1 - y0) * k
            lay = Image.new("RGBA", fr.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(lay)
            pts = [(x0 + (xm - x0) * s, y0 + (ym - y0) * s + 4 * math.sin(s * 9)) for s in np.linspace(0, 1, 16)]
            dl.line(pts, fill=f["col"] + (int(235 * (1 - outk)),), width=f["w"], joint="curve"); fr.alpha_composite(lay)
        elif f["kind"] == "check":
            x, y, s = f["p"]; pts = [(x - s * 0.45, y - s * 0.05), (x - s * 0.1, y + s * 0.35), (x + s * 0.55, y - s * 0.55)]
            k = eo(u) * 2; seg = [pts[0]]
            if k > 0: seg.append(tuple(np.array(pts[0]) + (np.array(pts[1]) - np.array(pts[0])) * min(1, k)))
            if k > 1: seg.append(tuple(np.array(pts[1]) + (np.array(pts[2]) - np.array(pts[1])) * (k - 1)))
            d.line(seg, fill=f["col"] + (int(255 * (1 - outk)),), width=f["w"], joint="curve")
        elif f["kind"] == "count":
            v0, v1 = f["v"]; v = v0 + (v1 - v0) * (1 - (1 - u) ** 3); txt = f["fmt"](v); key = (id(f), txt)
            if key not in _cnt:
                if len(_cnt) > 400: _cnt.clear()
                b = block(txt, f["size"], hl=HL, torn=False); im = Image.new("RGBA", (max(b.width, 10), b.height + (70 if f["sub"] else 0)), (0, 0, 0, 0))
                im.alpha_composite(b, ((im.width - b.width) // 2, 0))
                if f["sub"]:
                    s_ = block(f["sub"], 38, bg=INK, fg=(255, 255, 255), torn=False)
                    if s_.width > im.width: im2 = Image.new("RGBA", (s_.width, im.height), (0, 0, 0, 0)); im2.alpha_composite(im, ((s_.width - im.width) // 2, 0)); im = im2
                    im.alpha_composite(s_, ((im.width - s_.width) // 2, b.height + 4))
                _cnt[key] = im
            k = bo((t - f["t"]) / 0.28, 1.8); put(fr, _cnt[key], f["p"][0], f["p"][1], 0.5 + 0.5 * k, clamp((t - f["t"]) / 0.08) * (1 - outk), -1.5)
def wipe_k(t):
    """tira de papel rasgado atravessando a tela na troca de cena: devolve deslocamento da folha (ou None)"""
    for a, _ in SCENES[1:]:
        u = (t - (a - 0.22)) / 0.44
        if 0 <= u <= 1: return u
    return None
WIPE_R = strip(W + 200, 520, (236, 228, 212), "tb", 99, tex=6).rotate(-3, Image.BICUBIC, expand=True)
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); fr = Image.fromarray(PAPER).convert("RGBA")
    for e in EL:
        if tt < e["t"] or tt >= e["out"]: continue
        sc, al, dx, dy, rot = anim_xy(e, tt); put(fr, e["img"], e["x"] + dx, e["y"] + dy, sc, al, rot, 0.0 if e["z"] < 0 else 0.45)
    draw_fx(fr, tt)
    for a, b, txt in CREDIT:
        if a <= tt < b: R.credit(fr, txt, W - 30, 168, clamp((tt - a) / 0.3) * clamp((b - tt) / 0.2))
    sci = max(i for i, s in enumerate(SCENES) if s[0] <= tt); s0, s1 = SCENES[sci]
    z = 1.0 + 0.035 * clamp((tt - s0) / max(1, s1 - s0))                   # aproximação lenta dentro de cada cena
    if z > 1.001:
        a = np.asarray(fr); fr = Image.fromarray(cv2.warpAffine(a, np.float32([[z, 0, CX * (1 - z)], [0, z, 800 * (1 - z)]]), (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT))
    wk = wipe_k(tt)
    if wk is not None:
        y = int(H + 260 - (H + 1040) * wk); R.paste(fr, WIPE_R, -100, y, 0.4, 14, (0, -10))
    g = np.zeros((520, W, 4), np.uint8); g[..., :3] = (4, 14, 28); g[..., 3] = np.linspace(0, 150, 520)[:, None].astype(np.uint8); fr.alpha_composite(Image.fromarray(g), (0, H - 520))
    M.caption(fr, tt, CAP_Y, 54)
    kc = clamp((tt - 0.6) / 0.4) * (1 - clamp((tt - (EDIT_END - 0.3)) / 0.3)); BAR.lower_card(fr, CARD[0], CARD[1], CARD_Y, kc, fs=40)
    cta = clamp((t - 78.1) / 0.4) if t > 78.1 else 0.0
    BAR.draw_bar(fr, clamp(t / END_IN), "canal", eo((t - 0.2) / 0.6), cta, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(fr, t)
    if t >= END_IN: fr.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return fr.convert("RGB")
def capa(out):
    fr = Image.fromarray(PAPER).convert("RGBA")
    put(fr, strip(900, 1400, NAVY, "lr", 1), 640, 1060, shadow=0)
    put(fr, block("COMO UM CANAL", 92, rot=-2), 560, 330); put(fr, block("DE WHATSAPP", 120, bg=GOLD, fg=NAVY, rot=1), 600, 480)
    put(fr, block("AJUDOU A ELEGER", 92, rot=-1), 580, 640); put(fr, block("UM PRESIDENTE", 92, hl=HL, rot=1), 600, 780)
    put(fr, phone().rotate(-5, Image.BICUBIC, expand=True), 830, 1340); put(fr, polaroid(IMGS["lula2"], 330, 370, "LULA", None, 5, 0.12, color=True), 390, 1240)
    put(fr, stamp("+10 MILHÕES", 70, RED, -8), 520, 1640)
    BAR.draw_bar(fr, 0.0, "canal"); fr.alpha_composite(R.top, (R.HDX, 0)); fr.convert("RGB").save(out, quality=95)
def audio(vout):
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{V}/vo.mp3", "-ar", "48000", "-ac", "2", f"{V}/vo48.wav"], check=True)
    vo = R.readw(f"{V}/vo48.wav"); vt = np.zeros((n, 2), np.float32); vt[:min(len(vo), n)] = vo[:n]
    bed = R.readw(f"{S}/v49/bed.wav"); xf = int(1.5 * SR); loop = bed.copy()
    while len(loop) < n:
        r = np.linspace(0, 1, xf)[:, None]; loop[-xf:] = loop[-xf:] * (1 - r) + bed[:xf] * r; loop = np.concatenate([loop, bed[xf:]])
    tl = np.arange(n) / SR; gain = 0.10 * np.clip(tl / 1.0, 0, 1) * np.clip(1 - (tl - (TOTAL - 1.8)) / 1.6, 0, 1)
    gain *= np.where((tl > 76.2) & (tl < 77.1), 0.35, 1.0)                     # respira antes do "Ajuda."
    sg = loop[:n] * gain[:, None]; R.writew(f"{V}/voice.wav", vt); R.writew(f"{V}/song.wav", sg)
    ev = [(SCENES[i][0] - 0.25, sfx.whoosh(0.45), 0.13) for i in range(1, len(SCENES))]
    for e in EL:
        if e["anim"] == "stamp": ev.append((e["t"], sfx.thud(0.4), 0.30))
        elif e["anim"] == "drop": ev.append((e["t"] + 0.25, sfx.paper(0.3), 0.16))
        elif e["anim"] == "pop" and e["z"] >= 0: ev.append((e["t"], sfx.paper(0.25), 0.07))
    for f in FX:
        if f["kind"] in ("strike", "check"): ev.append((f["t"], sfx.marker(0.4), 0.12))
    ev += [(76.1, sfx.riser(1.0, 0.7), 0.30), (END_IN - 0.3, sfx.whoosh(0.6), 0.2)]
    sfx.build(ev, TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=70,acompressor=threshold=0.1:ratio=2.2:attack=8:release=200:makeup=1.4,asplit=2[vox][k2];[2:a]volume=0.9[sf];[3:a]volume=1.0[sg];"
                    "[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][sgd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
def main():
    if MODE == "lib": return
    if MODE == "capa": capa(OUTFILE); return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(x).resize((360, 640), Image.LANCZOS) for x in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    NF = int(round(TOTAL * FPS))
    if MODE.startswith("part"):                                            # part:i:n → pedaço i de n (render em paralelo)
        i, nparts = map(int, MODE.split(":")[1:]); a, b = NF * i // nparts, NF * (i + 1) // nparts
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", OUTFILE], stdin=subprocess.PIPE)
        for k in range(a, b): enc.stdin.write(frame_at(k / FPS).tobytes())
        enc.stdin.close(); enc.wait(); print("part done", i); return
    if MODE == "mux": audio(f"{V}/video.mp4"); print("done"); return
main()
