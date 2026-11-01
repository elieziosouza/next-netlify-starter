"""Bolha da IA? Meta cai quase 7% e derruba a Nasdaq (fechamento de 22/10). Ele no carro, edição dinâmica: barras caindo, números da bolsa
brasileira e do dólar, ícones, palavras acima da cabeça, trilha e convite para seguir. Números: DGABC, Money Times, ADVFN, InfoMoney."""
import sys, math, subprocess, importlib.util, os, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
sys.path.insert(0, f"{S}/work")
import sfx, grading, cor_fla
from segment_person import PersonSeg
BLUE = (14, 62, 120); PAPER = (247, 244, 236); INK = (22, 26, 34); GREEN = (40, 170, 90)
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; ease_out = R.ease_out; ease_in = R.ease_in; ease_io = R.ease_io
V = f"{S}/v54"; ME = f"{V}/me.mp4"
GRADE = grading.Fast(None, f"{S}/grade/lut_cinema_pele4.npy", 0.08, 6)
SEG = PersonSeg("/root/.cache/edicao-video/seg/u2net_human_seg.onnx")
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
GAPS = [(4.38, 4.7), (6.64, 6.98), (10.4, 10.8), (11.96, 12.32), (18.12, 18.36), (19.08, 19.48), (25.3, 25.88), (27.9, 28.54), (33.0, 33.48),
        (34.86, 35.18), (39.86, 40.44), (42.22, 42.72), (44.48, 44.86), (47.7, 53.98)]            # 47,7-54: repetição do "comenta e me segue"
PAD = 0.09
KEEP = []; a0 = 0.40
for g0, g1 in GAPS: KEEP.append((a0, g0 + PAD)); a0 = g1 - PAD
KEEP.append((a0, 58.72))
OFF = []; acc = 0.0
for a, b in KEEP: OFF.append(acc); acc += b - a
EDIT_END = acc; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = EDIT_END; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
def src_of(t):
    for i, (a, b) in enumerate(KEEP):
        if t < OFF[i] + (b - a) or i == len(KEEP) - 1: return a + t - OFF[i], i
def out_of(x):
    for i, (a, b) in enumerate(KEEP):
        if x <= b or i == len(KEEP) - 1: return OFF[i] + max(0.0, x - a)
SPLIT = [(10.6, 19.3), (33.3, 40.2)]
def split_of(x):
    for k, (a, b) in enumerate(SPLIT):
        if a <= x < b: return k
    return None
ME_CAPS = [("UMA EMPRESA PERDEU", 0.47, 1.6), ("QUASE 7% EM UM DIA.", 1.6, 3.3), ("SÓ POR ANUNCIAR QUE", 3.3, 4.38), ("IA INVESTIR MAIS", 4.7, 5.5),
           ("EM INTELIGÊNCIA ARTIFICIAL.", 5.5, 6.64), ("NÃO FOI UMA EMPRESA QUALQUER,", 6.98, 8.4), ("FOI A META,", 8.4, 9.0), ("DONA DO INSTAGRAM E DO WHATSAPP.", 9.0, 10.4),
           ("E O MEDO SE ESPALHOU.", 10.8, 11.96), ("A NASDAQ, A BOLSA DA TECNOLOGIA,", 12.32, 14.3), ("CAIU 2,6%", 14.3, 16.0), ("E O S&P 500 CAIU", 16.0, 18.12),
           ("1,2%.", 18.36, 19.08), ("WALL STREET INTEIRA", 19.48, 20.6), ("COMEÇOU A SE PERGUNTAR", 20.6, 21.8), ("A MESMA COISA:", 21.8, 22.6),
           ("ESSE DINHEIRO TODO DA IA", 22.6, 24.0), ("VAI VOLTAR?", 24.0, 25.3), ("OU É UMA BOLHA PRESTES A ESTOURAR?", 25.88, 27.9),
           ("PARA PIORAR, O PETRÓLEO SUBIU", 28.54, 30.3), ("COM A TENSÃO NO MUNDO.", 30.3, 31.5), ("PETRÓLEO CARO VIRA INFLAÇÃO.", 31.5, 33.0),
           ("E ISSO CHEGA NO SEU BOLSO.", 33.48, 34.86), ("AQUI NO BRASIL, A BOLSA", 35.18, 36.5), ("CAIU MAIS DE 1%", 36.5, 37.8), ("E O DÓLAR VOLTOU", 37.8, 38.8),
           ("PARA CIMA DE 5 REAIS.", 38.8, 39.86), ("NA MINHA OPINIÃO,", 40.44, 41.3), ("A IA VEIO PARA FICAR,", 41.3, 42.22), ("MAS NEM TODO MUNDO", 42.72, 43.6),
           ("VAI GANHAR COM ELA.", 43.6, 44.48), ("E VOCÊ, ACHA QUE É", 44.86, 46.0), ("UMA BOLHA OU FUTURO?", 46.0, 47.7), ("COMENTA AQUI EMBAIXO", 54.01, 55.3),
           ("E ME SEGUE,", 55.3, 56.0), ("PORQUE EU EXPLICO", 56.0, 56.9), ("O QUE ACONTECE NO MUNDO", 56.9, 57.8), ("E COMO ISSO CHEGA NO SEU BOLSO.", 57.8, 58.68)]
HOT = {"7%", "META,", "INSTAGRAM", "WHATSAPP.", "MEDO", "2,6%", "1,2%.", "BOLHA", "PETRÓLEO", "INFLAÇÃO.", "BOLSO.", "1%", "DÓLAR", "5", "FICAR,",
       "FUTURO?", "COMENTA", "SEGUE,", "VOLTAR?"}
CAPS = []
for txt, a, b in ME_CAPS:
    a2, b2 = out_of(a), out_of(b)
    if b2 - a2 < 0.2: continue
    ws = txt.split(); tot = sum(len(w) + 2 for w in ws); k = 0; ts = []
    for w in ws: ts.append(a2 + (b2 - a2 - 0.08) * k / tot); k += len(w) + 2
    CAPS.append(dict(words=ws, ts=ts, start=a2, end=b2, src="au" if any(w in HOT for w in ws) else "me"))
R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
BIG = [(1.6, 4.38, "-7% EM 1 DIA", R.GOLD_L, True), (8.4, 10.4, "META", R.WHITE, True), (22.6, 25.3, "VAI VOLTAR?", R.WHITE, False),
       (25.88, 27.9, "BOLHA?", R.GOLD_L, True), (28.54, 33.0, "PETRÓLEO EM ALTA", R.WHITE, False), (44.86, 47.7, "BOLHA OU FUTURO?", R.GOLD_L, True),
       (54.01, 58.72, "COMENTA E ME SEGUE", R.WHITE, True)]
ICONS = [(1.7, 4.38, "📉", 880, 1170, 160, None), (9.0, 10.4, "📱", 880, 1170, 150, None), (19.6, 22.5, "🏦", 880, 1170, 150, None),
         (22.7, 25.3, "💸", 880, 1170, 150, None), (25.9, 27.9, "🫧", 880, 1170, 170, None), (28.6, 33.0, "🛢️", 880, 1170, 160, None),
         (41.3, 44.48, "🤖", 880, 1170, 150, None), (45.0, 47.7, "🫧", 380, 1590, 140, "BOLHA"), (46.0, 47.7, "🚀", 780, 1590, 140, "FUTURO"),
         (54.1, 56.0, "💬", 880, 1170, 150, None), (55.3, 58.72, "🔔", 880, 1170, 150, None)]
_emo = {}
def emoji(ch, size):
    key = (ch, size)
    if key not in _emo:
        f = ImageFont.truetype(EMOJI, 109); im = Image.new("RGBA", (160, 160), (0, 0, 0, 0)); ImageDraw.Draw(im).text((8, 8), ch, font=f, embedded_color=True)
        bb = im.getbbox(); im = im.crop(bb) if bb else im; sc = size / max(im.size); _emo[key] = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    return _emo[key]
def pop(frame, img, cx, cy, u, dur, wob=True):
    if u < 0: return
    k = R.back_out(u / 0.32, 2.4) if u < 0.32 else 1.0; out = ease_in((u - (dur - 0.2)) / 0.2)
    sc = max(0.05, k * (1 - 0.3 * out)); ang = 8 * math.sin(u * 6) if wob else 0
    im = img.resize((max(1, int(img.width * sc)), max(1, int(img.height * sc))), Image.BICUBIC)
    if ang: im = im.rotate(ang, resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.getchannel("A").point(lambda v: int(v * 0.45)))
    frame.alpha_composite(R.fade(sh, 1 - out), (int(cx - im.width / 2 + 6), int(cy - im.height / 2 + 14)))
    frame.alpha_composite(R.fade(im, 1 - out), (int(cx - im.width / 2), int(cy - im.height / 2)))
# ---------------- fonte ----------------
_ch = {}; _gr = {}; _mk = {}
def raw_frame(x):
    key = int(x // 6)
    if key not in _ch:
        if len(_ch) > 2: _ch.clear()
        p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{key * 6:.3f}", "-t", "6.2", "-i", ME, "-vf", "fps=30", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           capture_output=True).stdout
        n = len(p) // (1080 * 1920 * 3); _ch[key] = np.frombuffer(p[:n * 1080 * 1920 * 3], np.uint8).reshape(n, 1920, 1080, 3)
    fr = _ch[key]; return fr[min(len(fr) - 1, int((x - key * 6) * FPS))], key * 1000 + min(len(fr) - 1, int((x - key * 6) * FPS))
def graded(x):
    fr, idx = raw_frame(x)
    if idx not in _gr:
        if len(_gr) > 40: _gr.clear()
        _gr[idx] = GRADE(cor_fla.fix(fr))
    return _gr[idx], idx
_yy, _xx = np.mgrid[0:1920, 0:1080].astype(np.float32)                 # só a cabeça e o corpo dele (o U2Net pega o encosto e a sombra no teto)
_el = ((_xx - 555) / 300) ** 2 + ((_yy - 935) / 445) ** 2
HEAD_PRIOR = np.maximum(np.clip((1.12 - _el) / 0.24, 0, 1), np.clip((_yy - 1250) / 80, 0, 1))
def person_mask(img, idx):
    if idx not in _mk:
        if len(_mk) > 40: _mk.clear()
        m = SEG(img); m = np.clip((m - 0.35) / 0.35, 0, 1) * HEAD_PRIOR; _mk[idx] = cv2.GaussianBlur(m, (0, 0), 1.6)[..., None]
    return _mk[idx]
def zoom(img, z, cx=540, cy=900):
    if abs(z - 1) < 1e-3: return img
    M = np.float32([[z, 0, cx * (1 - z)], [0, z, cy * (1 - z)]]); return cv2.warpAffine(img, M, (1080, 1920), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
def zoom_level(x, ki, t):
    if 40.4 <= x < 47.8: return 1.06 + 0.10 * ease_io((x - 40.4) / 7.4) * (1 - 0.35 * ease_io(clamp((x - 46.0) / 1.8)))          # opinião: aproxima devagar
    base = 1.0 if ki % 2 == 0 else 1.08                                             # pausa cortada = troca de enquadramento
    u = t - OFF[ki]; return base + 0.05 * (1 - ease_out(u / 0.18)) * (ki > 0) + 0.03 * (0.5 - 0.5 * math.cos(2 * math.pi * t / 7.0))   # soquinho + zoom lento entrando e saindo
# ---------------- palavras atrás ----------------
def big_layer(word, col, u, dur, shake, idx):
    """palavra inteira, centrada na área segura, semitransparente; entra crescendo do centro (nunca cortada pela borda)"""
    size = 330; f = R.BIGF(size)
    while f.getlength(word) > 820 or (f.getbbox(word)[3] - f.getbbox(word)[1]) > 230: size -= 6; f = R.BIGF(size)
    lay = Image.new("RGBA", (W, int(size * 1.35)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text((CX + 5, lay.height / 2 + 7), word, font=f, fill=(0, 0, 0, 70), anchor="mm")
    d.text((CX, lay.height / 2), word, font=f, fill=col + (205,), anchor="mm", stroke_width=4, stroke_fill=R.NAVY + (190,))
    k = ease_out(u / 0.3); out = ease_in((u - (dur - 0.25)) / 0.25)
    sc = 1.18 - 0.18 * k + 0.06 * out
    if abs(sc - 1) > 0.003:
        nw, nh = int(W * sc), int(lay.height * sc); big = lay.resize((nw, nh), Image.BICUBIC); ox = int(CX * sc - CX); oy = (nh - lay.height) // 2
        lay = big.crop((ox, oy, ox + W, oy + lay.height))
    dx = 0; dy = 0
    if shake and 0.3 < u < 1.0: a_ = 7 * (1 - (u - 0.3) / 0.7); dx = a_ * math.sin(u * 90); dy = a_ * 0.6 * math.cos(u * 70)
    return R.fade(lay, k * (1 - out)), int(dx), int(300 - lay.height / 2 + dy)
# ---------------- tela dividida ----------------
SEAM = 900
NAVY_BG = np.clip(R.NAVYBG, 0, 255).astype(np.uint8)
def wrap(txt, font, maxw):
    lines, cur = [], ""
    for w in txt.split():
        t2 = (cur + " " + w).strip()
        if font.getlength(t2) <= maxw: cur = t2
        else: lines.append(cur); cur = w
    return lines + [cur]
def card_bg(w, h, r=26):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), r, fill=(8, 30, 56, 235), outline=R.GOLD + (255,), width=3); return im
def num_txt(v, dec=1, suf="%", pre=""):
    return pre + f"{v:.{dec}f}".replace(".", ",") + suf
BARS = [(12.32, "NASDAQ", -2.6, "bolsa da tecnologia"), (16.0, "S&P 500", -1.2, "as 500 maiores dos EUA")]
def bars_card(x):
    w, h = 860, 760; im = card_bg(w, h); d = ImageDraw.Draw(im)
    d.text((w / 2, 52), "WALL STREET · 22/10", font=R.MF("ExtraBold", 34), fill=R.GOLD_L + (255,), anchor="mm")
    d.line((60, 170, w - 60, 170), fill=(140, 160, 190, 255), width=3); d.text((w - 60, 150), "0%", font=R.MF("Bold", 24), fill=(200, 210, 225, 255), anchor="rm")
    for i, (t0, lab, v, sub) in enumerate(BARS):
        u = x - t0
        cx = 240 + i * 380
        d.text((cx, 120), lab, font=R.MF("ExtraBold", 36), fill=(255, 255, 255, 255), anchor="mm")
        if u < 0: continue
        k = ease_out(clamp(u / 1.0)); hb = 320 * (-v / 2.6) * k
        d.rounded_rectangle((cx - 85, 172, cx + 85, 172 + max(8, hb)), 14, fill=(200, 30, 40, 255))
        d.text((cx, 172 + hb + 50), num_txt(v * k), font=R.BIGF(84), fill=(255, 255, 255, 255), anchor="mm")
        d.text((cx, 172 + hb + 105), sub, font=R.MF("SemiBold", 22), fill=(200, 210, 225, 255), anchor="mm")
    d.text((w / 2, h - 34), "Dow Jones: estável (+0,02%) · Fontes: DGABC, Money Times", font=R.MF("SemiBold", 22), fill=(200, 210, 225, 255), anchor="mm")
    return im
BR = [(35.18, "📉", "IBOVESPA", -1.15, 2, "%", ""), (37.8, "💵", "DÓLAR", 5.03, 2, "", "R$ ")]
def brasil_card(x):
    w, h = 860, 620; im = card_bg(w, h); d = ImageDraw.Draw(im)
    im.alpha_composite(emoji("🇧🇷", 70), (40, 22)); d.text((130, 60), "E NO BRASIL? · 22/10", font=R.MF("ExtraBold", 34), fill=R.GOLD_L + (255,), anchor="lm")
    for i, (t0, emo, lab, v, dec, suf, pre) in enumerate(BR):
        u = x - t0
        if u < 0: continue
        k = ease_out(u / 0.35); row = Image.new("RGBA", (w, 220), (0, 0, 0, 0)); dr = ImageDraw.Draw(row)
        row.alpha_composite(emoji(emo, 100), (40, 50)); dr.text((170, 100), lab, font=R.MF("ExtraBold", 44), fill=(255, 255, 255, 255), anchor="lm")
        kc = ease_io(clamp((u - 0.15) / 1.1)); dr.text((w - 50, 100), num_txt(v * kc, dec, suf, pre), font=R.BIGF(110), fill=R.GOLD_L + (255,), anchor="rm")
        im.alpha_composite(R.fade(row, k), (int(60 * (1 - k)), 130 + i * 220))
    d.text((w / 2, h - 34), "Fonte: InfoMoney · não é recomendação de investimento", font=R.MF("SemiBold", 22), fill=(200, 210, 225, 255), anchor="mm")
    return im
def split_scene(x, t, k_idx):
    img, idx = graded(x)
    top = img[330:1430]; tw = int(1080 * SEAM / 1100); fg = cv2.resize(top, (tw, SEAM), interpolation=cv2.INTER_AREA)
    bg = cv2.resize(cv2.GaussianBlur(cv2.resize(top, (108, 90)), (0, 0), 3), (W, SEAM)).astype(np.float32) * 0.55
    x0 = CX - tw // 2; fm = np.ones((SEAM, tw), np.float32); fm[:, :50] = np.linspace(0, 1, 50)[None]; fm[:, -50:] = np.linspace(1, 0, 50)[None]; fm = fm[..., None]
    xs, xe = max(0, x0), min(W, x0 + tw); bg[:, xs:xe] = bg[:, xs:xe] * (1 - fm[:, xs - x0:xe - x0]) + fg[:, xs - x0:xe - x0] * fm[:, xs - x0:xe - x0]
    base = NAVY_BG.copy(); base[:SEAM] = bg.astype(np.uint8)
    frame = Image.fromarray(base).convert("RGBA"); ImageDraw.Draw(frame).rectangle((0, SEAM - 2, W, SEAM + 3), fill=R.GD)
    a, b = SPLIT[k_idx]; u = x - a; kin = ease_out(u / 0.4)
    card = bars_card(x) if k_idx == 0 else brasil_card(x)
    R.paste(frame, R.fade(card, kin), CX - card.width / 2, 985 + 240 * (1 - kin), 0.6, 22, (10, 26))
    caption(frame, t, SEAM - 70, 44)
    return frame
def caption(frame, t, y, size):
    old = R.RED; R.RED = BLUE
    try: R.draw_caption(frame, t, y, size, ("me", "au"))
    finally: R.RED = old
CARD = ("WALL STREET", ["MEDO DA IA", "DERRUBA A NASDAQ"])
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); x, ki = src_of(tt); sk = split_of(x)
    if sk is not None: frame = split_scene(x, tt, sk)
    else:
        img, idx = graded(x); z = zoom_level(x, ki, tt)
        img = zoom(img, z)
        frame = Image.fromarray(img).convert("RGBA")
        for i, (a, b, word, col, shk) in enumerate(BIG):                     # palavra grande ACIMA da cabeça (o fundo do carro não deixa recortar limpo)
            if a <= x < b: lay, dx, y = big_layer(word, col, x - a, b - a, shk, i); frame.alpha_composite(lay, (dx, y))
        g = np.zeros((520, W, 4), np.uint8); g[..., :3] = (4, 14, 28); g[..., 3] = np.linspace(0, 200, 520)[:, None].astype(np.uint8); frame.alpha_composite(Image.fromarray(g), (0, H - 520))
        for a, b, ch, cx, cy, sz, lab in ICONS:
            if a <= x < b:
                pop(frame, emoji(ch, sz), cx, cy, x - a, b - a)
                if lab and x - a > 0.15: R.pill(frame, lab, cx, cy + sz / 2 + 40, clamp((x - a - 0.15) / 0.25) * (1 - ease_in((x - (b - 0.2)) / 0.2)), fill=R.NAVY, size=20)
        cy_cap = 1430 if 44.9 <= x < 47.8 else 1520
        caption(frame, tt, cy_cap, 50)
        kc = clamp((tt - 0.6) / 0.4) * (1 - clamp((x - 6.5) / 0.3))
        if kc > 0: BAR.lower_card(frame, CARD[0], CARD[1], 1700, kc, fs=40)
    BAR.draw_bar(frame, clamp(t / END_IN), "canal", ease_out((t - 0.2) / 0.6), clamp((src_of(min(t, EDIT_END - 1e-3))[0] - 54.0) / 0.4), 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(frame, t)
    for i in range(1, len(KEEP)):                                      # flash curto onde muda de modo
        xa = KEEP[i][0]; xb = KEEP[i - 1][1]
        if (split_of(xa) is None) != (split_of(xb) is None) and abs(t - OFF[i]) < 0.08:
            frame = Image.blend(frame, Image.new("RGBA", frame.size, (255, 255, 255, 255)), (1 - abs(t - OFF[i]) / 0.08) * 0.35)
    if t >= END_IN: frame.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return frame.convert("RGB")

def main():
    if MODE == "lib": return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(t).resize((360, 640), Image.LANCZOS) for t in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    if MODE.startswith("src"):                                         # quadros por tempo do original
        xs = [float(v) for v in MODE.split(":")[1].split(",")]; print([round(out_of(v), 2) for v in xs]); return
    if MODE == "info": print("TOTAL", round(TOTAL, 2), "EDIT", round(EDIT_END, 2)); return
    vout = f"{V}/video.mp4"
    if not (os.environ.get("REUSE") and os.path.exists(vout)):
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
        for k in range(int(round(TOTAL * FPS))): enc.stdin.write(frame_at(k / FPS).tobytes())
        enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", ME, "-ar", "48000", "-ac", "2", f"{V}/me48.wav"], check=True)
    me = R.readw(f"{V}/me48.wav"); vt = np.zeros((n, 2), np.float32); f = int(0.012 * SR)
    for i, (a, b) in enumerate(KEEP):
        c = me[int(a * SR):int(b * SR)].copy(); c[:f] *= np.linspace(0, 1, f)[:, None]; c[-f:] *= np.linspace(1, 0, f)[:, None]
        o = int(OFF[i] * SR); vt[o:o + len(c)] += c[:n - o]
    R.writew(f"{V}/voice.wav", vt)
    bed = R.readw(os.environ.get("BED", f"{V}/bed.wav")); L = min(len(bed), n); tl = np.arange(L) / SR
    gain = (float(os.environ.get("BEDG", "0.06")) * np.clip(tl / 1.0, 0, 1) + 0.08 * np.clip((tl - (EDIT_END - 0.3)) / 0.5, 0, 1)) * np.clip(1 - (tl - (TOTAL - 1.6)) / 1.5, 0, 1)
    sg = np.zeros((n, 2), np.float32); sg[:L] = bed[:L] * gain[:, None]; R.writew(f"{V}/song.wav", sg)
    ev = [(0.0, sfx.whoosh(0.4), 0.2), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
    for i, (a, b, *_r) in enumerate(BIG): ta = out_of(a); ev += [(ta, sfx.whoosh(0.35), 0.24), (ta + 0.26, sfx.click(), 0.7), (ta + 0.26, sfx.thud(0.3), 0.2)]
    for a, b, *_r in ICONS: ev += [(out_of(a), sfx.click(), 0.45)]
    for a, b in SPLIT: ev += [(out_of(a) - 0.1, sfx.whoosh(0.45), 0.24)]
    ev += [(out_of(t0), sfx.whoosh(0.3), 0.2) for t0, *_r in BARS + BR] + [(out_of(t0) + 0.2 + j * 0.12, sfx.click(), 0.16) for t0, *_r in BARS + BR for j in range(8)]
    ev += [(out_of(54.05), sfx.siga(), 0.18)]
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=80,afftdn=nf=-25,acompressor=threshold=0.08:ratio=2.5:attack=8:release=200:makeup=1.6,asplit=2[vox][k2];[2:a]volume=0.8[sf];[3:a]volume=0.95[sg];"
                    "[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][sgd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
