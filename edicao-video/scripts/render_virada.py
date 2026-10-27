"""Explicativo em colagem de papel: a virada inédita (quem perdeu o 1º turno venceu o 2º), o placar, a prorrogação de 2 horas
(decisão do ministro Zanin) e a contestação do Flávio, mostrada como o outro lado antes da opinião. Mesmo estilo dos vídeos em colagem."""
import sys, math, subprocess, importlib.util, os, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("rex", f"{S}/work/render_exercito.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; eo = R.ease_out; ei = R.ease_in; bo = R.back_out
V = f"{S}/v75"; FD = f"{S}/fontdl"
VO_LEN = 57.26; EDIT_END = 57.35; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
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
HOT = {"HISTÓRIA", "AGORA.", "51,79%.", "48,21%.", "MILHÕES", "QUARTO", "CONTURBADA.", "ÔNIBUS", "HORAS,", "ZANIN.", "ANULAÇÃO", "DIREITO", "OPINIÃO:", "JUSTIÇA,", "DECIDE.", "GENTE.", "DEMOCRACIA", "MANTIDO?", "AQUI."}
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
CARD = ("ELEIÇÕES 2026", ["VIRADA INÉDITA", "E RESULTADO CONTESTADO"])
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
def calendar_d(day, wd):
    w, h = 300, 330; im = Image.new("RGBA", (w, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((0, 20, w - 1, h + 19), fill=OFF + (255,)); d.rectangle((0, 20, w - 1, 100), fill=RED + (255,))
    for x in (70, w - 70): d.rounded_rectangle((x - 8, 0, x + 8, 44), 6, fill=(60, 60, 60, 255))
    d.text((w / 2, 62), "OUTUBRO", font=ANTON(46), fill=(255, 255, 255, 255), anchor="mm"); d.text((w / 2, 215), day, font=ANTON(170), fill=INK + (255,), anchor="mm")
    d.text((w / 2, 318), wd, font=ANTON(36), fill=(90, 86, 80, 255), anchor="mm"); return im
def note2(head, lines, rot=0):
    w, h = 300, 260 if len(lines) > 1 else 220; a = np.ones((h, w, 3), np.float32) * np.array([248, 246, 238], np.float32)
    for y in range(96, h, 44): a[y:y + 2] = (200, 214, 230)
    im = Image.fromarray(np.clip(a + rng.normal(0, 3, (h, w, 1)), 0, 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(im)
    d.text((24, 44), head, font=ANTON(34), fill=RED + (255,), anchor="lm"); d.line((24, 72, w - 40, 72), fill=RED + (255,), width=3)
    for i, l in enumerate(lines):
        fs = 54
        while ANTON(fs).getlength(l) > w - 40: fs -= 2
        d.text((24, 124 + i * 58), l, font=ANTON(fs), fill=INK + (255,), anchor="lm")
    t = tape(120, 40, 4); c = Image.new("RGBA", (w, h + 22), (0, 0, 0, 0)); c.alpha_composite(im, (0, 22)); c.alpha_composite(t, (w // 2 - t.width // 2, 0))
    return c.rotate(rot, Image.BICUBIC, expand=True)
def clock():
    w = 330; im = Image.new("RGBA", (w, w), (0, 0, 0, 0)); d = ImageDraw.Draw(im); c = w / 2
    d.ellipse((6, 6, w - 6, w - 6), fill=OFF + (255,), outline=INK + (255,), width=12)
    for k in range(12):
        a = k * math.pi / 6; r0, r1 = (c - 50, c - 22) if k % 3 == 0 else (c - 36, c - 22)
        d.line((c + r0 * math.sin(a), c - r0 * math.cos(a), c + r1 * math.sin(a), c - r1 * math.cos(a)), fill=INK + (255,), width=7 if k % 3 == 0 else 4)
    d.pieslice((30, 30, w - 30, w - 30), -90 + 150, -90 + 210, fill=RED + (120,))          # das 17h às 19h
    d.line((c, c, c + (c - 90) * math.sin(math.radians(210)), c - (c - 90) * math.cos(math.radians(210))), fill=INK + (255,), width=12)
    d.line((c, c, c, 52), fill=INK + (255,), width=7); d.ellipse((c - 14, c - 14, c + 14, c + 14), fill=INK + (255,))
    return im
IMGS = {"lula": f"{S}/v61/dl/lula.jpg", "flavio": f"{S}/v61/dl/flavio.jpg", "janones": f"{V}/dl/janones.jpg", "nunes": f"{V}/dl/nunes.jpg", "lula2": f"{S}/v71/lula.jpg"}

# ---------------------------------------------------------------- linha do tempo: cenas e elementos
# elemento: dict(t=entrada, out=saída (fim da cena), img, x, y (centro), anim: pop|slide_l|slide_r|slide_u|drop|stamp, z)
SCENES = [(0.0, 5.3), (5.3, 16.4), (16.4, 20.65), (20.65, 30.1), (30.1, 39.5), (39.5, 45.05), (45.05, 53.3), (53.3, 58.5)]
EL = []; FX = []      # FX: riscos, ✓, contadores (desenho por quadro)
def add(t, img, x, y, anim="pop", scene=None, z=0):
    sc = scene if scene is not None else max(i for i, s in enumerate(SCENES) if s[0] <= t + 1e-6)
    EL.append(dict(t=t, out=SCENES[sc][1], img=img, x=x, y=y, anim=anim, z=z, sc=sc))
def strike(t, dur, x0, y0, x1, y1, col=RED, w=12, sc=None):
    s_ = sc if sc is not None else max(i for i, s in enumerate(SCENES) if s[0] <= t + 1e-6); FX.append(dict(kind="strike", t=t, dur=dur, p=(x0, y0, x1, y1), col=col, w=w, out=SCENES[s_][1]))
def check(t, x, y, size=70, col=RED):
    s_ = max(i for i, s in enumerate(SCENES) if s[0] <= t + 1e-6); FX.append(dict(kind="check", t=t, dur=0.3, p=(x, y, size), col=col, w=10, out=SCENES[s_][1]))
def chart(t, dur, box, pts, col, sc=None):
    s_ = max(i for i, s in enumerate(SCENES) if s[0] <= t + 1e-6); FX.append(dict(kind="chart", t=t, dur=dur, box=box, pts=pts, col=col, w=9, out=SCENES[s_][1]))
def graph_paper(w, h, title, sub=None):
    a = np.ones((h, w, 3), np.float32) * np.array([246, 244, 236], np.float32)
    for x in range(0, w, 30): a[:, x:x + 1] = (205, 220, 228)
    for y in range(0, h, 30): a[y:y + 1] = (205, 220, 228)
    im = Image.fromarray(np.clip(a + rng.normal(0, 3, (h, w, 1)), 0, 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(im)
    d.text((26, 34), title, font=ANTON(40), fill=INK + (255,), anchor="lm")
    if sub: d.text((w - 26, 36), sub, font=SER(26), fill=(80, 76, 70, 255), anchor="rm")
    d.line((40, h - 40, w - 30, h - 40), fill=INK + (255,), width=3); d.line((40, 70, 40, h - 40), fill=INK + (255,), width=3)
    im.putalpha(torn_mask(w, h, "lrtb", 4, w + h)); return im
def counter(t, dur, v0, v1, x, y, fmt, size=150, sub=None, out=None):
    s_ = max(i for i, s in enumerate(SCENES) if s[0] <= t + 1e-6); FX.append(dict(kind="count", t=t, dur=dur, v=(v0, v1), p=(x, y), fmt=fmt, size=size, sub=sub, out=out or SCENES[s_][1]))
# 1 · nunca na história
add(0.0, strip(1080, 560, NAVY, "tb", 31), 540, 760, "slide_l", z=-2)
add(0.2, block("NUNCA NA HISTÓRIA", 96, bg=INK, fg=(255, 255, 255), rot=-2), 570, 340, "pop")
add(1.5, block("QUEM PERDEU O 1º TURNO", 62, rot=1), 590, 640, "pop")
add(2.6, block("VIROU NO 2º", 96, bg=GOLD, fg=NAVY, rot=-2), 590, 780, "pop")
add(4.17, stamp("ATÉ AGORA", 110, RED, -8), 590, 1130, "stamp")
# 2 · o placar
add(5.3, strip(560, 1300, GREEN, "lr", 32), 400, 860, "slide_l", z=-2); add(5.35, strip(520, 1300, GOLD, "lr", 33), 860, 860, "slide_r", z=-2)
add(5.46, polaroid(IMGS["lula"], 300, 330, "LULA", None, -4, 0.15), 380, 560, "drop")
counter(6.3, 2.2, 0.0, 51.79, 380, 960, lambda v: f"{v:.2f}%".replace(".", ","), 110)
add(9.34, polaroid(IMGS["flavio"], 300, 330, "FLÁVIO", None, 4, 0.15), 820, 560, "drop")
counter(10.1, 2.0, 0.0, 48.21, 820, 960, lambda v: f"{v:.2f}%".replace(".", ","), 110)
add(12.9, block("DIFERENÇA", 50, bg=INK, fg=(255, 255, 255), rot=-2), 600, 1140, "pop")
add(13.5, block("4,4 MILHÕES DE VOTOS", 74, hl=HL, rot=1), 600, 1260, "pop")
# 3 · quarto mandato
add(16.4, strip(1080, 520, KRAFT, "tb", 34), 540, 700, "slide_r", z=-2)
add(16.5, block("4º MANDATO", 120, bg=INK, fg=(255, 255, 255), rot=-2), 580, 360, "pop")
for k, (yr, x) in enumerate((("2002", 300), ("2006", 520), ("2022", 740), ("2026", 950))):
    add(16.7 + 0.25 * k, note2(yr, ["ELEITO"], (-4, 3, -2, 4)[k]).resize((240, 194), Image.LANCZOS), x, 690, "drop")
add(18.6, block("ELEIÇÃO CONTURBADA", 80, hl=HL, rot=-1), 590, 1060, "pop")
# 4 · ônibus e prorrogação
add(20.65, block("FALTA DE ÔNIBUS", 90, bg=INK, fg=(255, 255, 255), rot=-2), 560, 340, "pop")
add(21.6, textlay("relatos em várias cidades", HAND(66), INK, -2), 590, 480, "pop")
add(24.1, strip(1080, 640, NAVY, "tb", 35), 540, 860, "slide_l", z=-2)
add(24.3, clock(), 380, 860, "drop"); add(25.3, stamp("+2 HORAS", 96, RED, -8), 780, 800, "stamp")
add(26.0, block("VOTAÇÃO PRORROGADA", 50, rot=2), 780, 960, "pop")
add(27.2, block("DECISÃO DO MINISTRO", 54, bg=OFF, rot=-1), 590, 1170, "pop"); add(28.0, block("CRISTIANO ZANIN", 74, bg=GOLD, fg=NAVY, rot=1), 600, 1290, "pop")
# 5 · o outro lado
add(30.1, strip(1080, 240, RED, "tb", 36), 540, 330, "slide_r", z=-2)
add(30.2, textlay("O OUTRO LADO", ANTON(110), (255, 255, 255)), 600, 330, "pop")
add(30.4, polaroid(IMGS["flavio"], 300, 330, "FLÁVIO BOLSONARO", None, -4, 0.15), 380, 740, "drop")
add(31.0, block("CONTESTA", 80, rot=3), 800, 600, "pop"); add(31.6, block("O RESULTADO", 64, rot=-2), 800, 710, "pop")
add(32.8, textlay("diz que vai pedir a", HAND(58), INK, -2), 800, 860, "pop"); add(33.6, stamp("ANULAÇÃO", 70, RED, -8), 800, 980, "stamp")
add(35.6, block("É UM DIREITO DELE", 70, hl=HL, rot=-1), 590, 1220, "pop")
# 6 · opinião
add(39.5, strip(1080, 900, INK, "tb", 37), 540, 840, "slide_u", z=-2)
add(39.75, block("NA MINHA OPINIÃO", 54, bg=OFF, fg=INK), 460, 330, "pop")
add(41.45, block("TEM DÚVIDA?", 96, rot=-2), 580, 640, "pop"); add(42.3, block("VAI À JUSTIÇA", 96, bg=GOLD, fg=NAVY, rot=1.5), 600, 800, "pop")
add(43.57, textlay("e a Justiça decide", HAND(80), (255, 255, 255), -2), 600, 1000, "pop")
# 7 · democracia
add(45.05, strip(1080, 600, GREEN, "tb", 38), 540, 780, "slide_r", z=-2)
counter(45.3, 1.8, 0, 4_400_000, 600, 560, lambda v: f"{v:,.0f}".replace(",", "."), 128, "DE VOTOS DE DIFERENÇA")
add(47.4, textlay("é muita gente", HAND(90), (255, 255, 255), -3), 600, 780, "pop")
add(49.14, block("DEMOCRACIA", 120, bg=INK, fg=(255, 255, 255), rot=-2), 590, 1010, "pop")
add(50.3, block("É ACEITAR O RESULTADO", 64, rot=1), 590, 1150, "pop"); add(51.4, block("GANHANDO OU PERDENDO", 64, hl=HL, rot=-1), 600, 1270, "pop")
# 8 · pergunta
add(53.49, block("E VOCÊ?", 110, bg=INK, fg=(255, 255, 255), rot=-2), 560, 400, "pop")
add(54.2, block("O RESULTADO", 90, rot=1), 570, 630, "pop"); add(54.9, block("VAI SER MANTIDO?", 100, hl=HL, rot=-2), 600, 790, "pop")
add(56.24, textlay("comenta aqui", HAND(80), INK, -3), 600, 1040, "pop"); add(56.4, arrow(150, 70, RED).rotate(-70, Image.BICUBIC, expand=True), 600, 1210, "pop")
CREDIT = [(5.46, 16.4, "Fotos: Wikimedia Commons · Resultado: TSE"), (30.4, 39.5, "Foto: Wikimedia Commons")]
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
        elif f["kind"] == "chart":
            x0, y0, x1, y1 = f["box"]; P = [(x0 + (x1 - x0) * px, y0 + (y1 - y0) * py) for px, py in f["pts"]]
            L = [0.0] + list(np.cumsum([math.dist(P[i], P[i + 1]) for i in range(len(P) - 1)])); tgt = L[-1] * eo(u); seg = [P[0]]
            for i in range(1, len(P)):
                if L[i] <= tgt: seg.append(P[i])
                else:
                    r_ = (tgt - L[i - 1]) / max(1e-6, L[i] - L[i - 1]); seg.append((P[i - 1][0] + (P[i][0] - P[i - 1][0]) * r_, P[i - 1][1] + (P[i][1] - P[i - 1][1]) * r_)); break
            a_ = int(255 * (1 - outk))
            if len(seg) > 1: d.line(seg, fill=f["col"] + (a_,), width=f["w"], joint="curve"); ex, ey = seg[-1]; d.ellipse((ex - 11, ey - 11, ex + 11, ey + 11), fill=f["col"] + (a_,))
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
    cta = clamp((t - 54.2) / 0.4) if t > 54.2 else 0.0
    BAR.draw_bar(fr, clamp(t / END_IN), "canal", eo((t - 0.2) / 0.6), cta, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(fr, t)
    if t >= END_IN: fr.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return fr.convert("RGB")
def capa(out):
    fr = Image.fromarray(PAPER).convert("RGBA")
    put(fr, strip(560, 1500, GREEN, "lr", 32), 400, 1050, shadow=0); put(fr, strip(520, 1500, GOLD, "lr", 33), 860, 1050, shadow=0)
    put(fr, block("VIRADA INÉDITA", 120, bg=INK, fg=(255, 255, 255), rot=-2), 580, 320)
    put(fr, block("NUNCA TINHA ACONTECIDO", 64, hl=HL, rot=1), 590, 470)
    put(fr, polaroid(IMGS["lula"], 300, 330, "LULA", None, -4, 0.15), 380, 800); put(fr, polaroid(IMGS["flavio"], 300, 330, "FLÁVIO", None, 4, 0.15), 820, 800)
    put(fr, block("51,79%", 110, hl=HL, rot=-2), 380, 1150); put(fr, block("48,21%", 110, rot=2), 820, 1150)
    put(fr, stamp("CONTESTADO", 90, RED, -8), 600, 1420)
    BAR.draw_bar(fr, 0.0, "canal"); fr.alpha_composite(R.top, (R.HDX, 0)); fr.convert("RGB").save(out, quality=95)
def audio(vout):
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{V}/vo.mp3", "-ar", "48000", "-ac", "2", f"{V}/vo48.wav"], check=True)
    vo = R.readw(f"{V}/vo48.wav"); vt = np.zeros((n, 2), np.float32); vt[:min(len(vo), n)] = vo[:n]
    bed = R.readw(f"{S}/v49/bed.wav"); xf = int(1.5 * SR); loop = bed.copy()
    while len(loop) < n:
        r = np.linspace(0, 1, xf)[:, None]; loop[-xf:] = loop[-xf:] * (1 - r) + bed[:xf] * r; loop = np.concatenate([loop, bed[xf:]])
    tl = np.arange(n) / SR; gain = 0.10 * np.clip(tl / 1.0, 0, 1) * np.clip(1 - (tl - (TOTAL - 1.8)) / 1.6, 0, 1)
    sg = loop[:n] * gain[:, None]; R.writew(f"{V}/voice.wav", vt); R.writew(f"{V}/song.wav", sg)
    ev = [(SCENES[i][0] - 0.25, sfx.whoosh(0.45), 0.13) for i in range(1, len(SCENES))]
    for e in EL:
        if e["anim"] == "stamp": ev.append((e["t"], sfx.thud(0.4), 0.30))
        elif e["anim"] == "drop": ev.append((e["t"] + 0.25, sfx.paper(0.3), 0.16))
        elif e["anim"] == "pop" and e["z"] >= 0: ev.append((e["t"], sfx.paper(0.25), 0.07))
    for f in FX:
        if f["kind"] in ("strike", "check"): ev.append((f["t"], sfx.marker(0.4), 0.12))
    ev += [(END_IN - 0.3, sfx.whoosh(0.6), 0.2)]
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
