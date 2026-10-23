"""Flamengo eliminado pelo Estudiantes (22/10, Maracanã): ele no carro, edição dinâmica. Placar animado (0x0, 0x0, pênaltis 2x3),
disputa de pênaltis num placar animado nosso (sem imagem de TV, sem risco de direitos), manchete do Lance com os motivos, ícones, palavras acima da cabeça e trilha."""
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
V = f"{S}/v53"; ME = f"{V}/me.mp4"
GRADE = grading.Fast(None, f"{S}/grade/lut_cinema_pele4.npy", 0.08, 6)
SEG = PersonSeg("/root/.cache/edicao-video/seg/u2net_human_seg.onnx")
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
GAPS = [(2.92, 3.3), (5.76, 6.14), (9.7, 10.1), (11.2, 11.46), (12.4, 12.74), (15.24, 15.6), (16.36, 16.76), (19.24, 19.6), (21.44, 21.88), (24.04, 24.44),
        (27.68, 28.12), (29.3, 29.84), (31.74, 32.0), (34.32, 34.78), (35.56, 36.0), (37.84, 38.16), (39.92, 40.32), (41.64, 44.36), (45.88, 49.7),
        (50.64, 50.98), (53.74, 54.08)]                                    # 41,6-44,4 e 45,9-49,7: repetições do "agora só sobrou"
PAD = 0.09
KEEP = []; a0 = 0.58
for g0, g1 in GAPS: KEEP.append((a0, g0 + PAD)); a0 = g1 - PAD
KEEP.append((a0, 54.84))
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
SPLIT = [(10.0, 15.45), (15.45, 21.62), (21.62, 34.5)]
def split_of(x):
    for k, (a, b) in enumerate(SPLIT):
        if a <= x < b: return k
    return None
ME_CAPS = [("O FLAMENGO TINHA TUDO", 0.68, 1.8), ("PARA IR PARA A FINAL.", 1.8, 2.92), ("TINHA O MARACANÃ LOTADO", 3.3, 4.6), ("E CAIU NOS PÊNALTIS.", 4.6, 5.76),
           ("FORAM DOIS JOGOS", 6.14, 7.2), ("CONTRA O ESTUDIANTES", 7.2, 8.4), ("E NENHUM GOL DO FLAMENGO.", 8.4, 9.7), ("ZERO A ZERO LÁ", 10.1, 11.2),
           ("E ZERO A ZERO AQUI.", 11.46, 12.4), ("NOS PÊNALTIS,", 12.74, 13.7), ("3 A 2 PARA OS ARGENTINOS.", 13.7, 15.24), ("JORGINHO,", 15.6, 16.36),
           ("PAQUETÁ E BRUNO HENRIQUE", 16.76, 18.2), ("PERDERAM AS COBRANÇAS.", 18.2, 19.24), ("E AÍ ACABOU", 19.6, 20.5), ("O SONHO DO TETRA.", 20.5, 21.44),
           ("MAS O PROBLEMA", 21.88, 22.9), ("NÃO FOI SÓ O PÊNALTI.", 22.9, 24.04), ("A PRÓPRIA IMPRENSA ESPORTIVA DISSE:", 24.44, 26.3), ("O FLAMENGO CAIU ANTES,", 26.3, 27.68),
           ("PORQUE CRIOU POUCO,", 28.12, 29.3), ("NÃO FEZ GOL EM 180 MINUTOS", 29.84, 31.74), ("E NÃO APROVEITOU QUANDO", 32.0, 33.2), ("TEVE UM JOGADOR A MAIS.", 33.2, 34.32),
           ("NA MINHA OPINIÃO,", 34.78, 35.56), ("COM O ELENCO MAIS CARO DO BRASIL,", 36.0, 37.84), ("NÃO DÁ PARA JOGAR", 38.16, 39.0), ("UMA SEMIFINAL ASSIM.", 39.0, 39.92),
           ("O TORCEDOR MERECIA MAIS.", 40.32, 41.64), ("AGORA SÓ SOBROU", 44.36, 45.1), ("O BRASILEIRÃO.", 45.1, 45.88), ("E VOCÊ, TORCEDOR?", 49.7, 50.64),
           ("A CULPA É DO TÉCNICO,", 50.98, 52.2), ("DOS JOGADORES OU DA DIRETORIA?", 52.2, 53.74), ("COMENTA AÍ!", 54.08, 54.84)]
HOT = {"FINAL.", "MARACANÃ", "PÊNALTIS.", "PÊNALTIS,", "NENHUM", "GOL", "ZERO", "3", "2", "JORGINHO,", "PAQUETÁ", "BRUNO", "HENRIQUE", "TETRA.", "ANTES,", "POUCO,",
       "180", "MAIS.", "CARO", "MERECIA", "BRASILEIRÃO.", "TÉCNICO,", "JOGADORES", "DIRETORIA?", "COMENTA"}
CAPS = []
for txt, a, b in ME_CAPS:
    a2, b2 = out_of(a), out_of(b)
    if b2 - a2 < 0.2: continue
    ws = txt.split(); tot = sum(len(w) + 2 for w in ws); k = 0; ts = []
    for w in ws: ts.append(a2 + (b2 - a2 - 0.08) * k / tot); k += len(w) + 2
    CAPS.append(dict(words=ws, ts=ts, start=a2, end=b2, src="au" if any(w in HOT for w in ws) else "me"))
R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
BIG = [(0.68, 2.92, "TINHA TUDO", R.WHITE, False), (4.6, 5.76, "PÊNALTIS", R.GOLD_L, True), (8.4, 9.7, "0 GOLS", R.WHITE, True),
       (40.32, 41.64, "MERECIA MAIS", R.GOLD_L, True), (44.36, 45.88, "SÓ O BRASILEIRÃO", R.WHITE, False), (49.7, 53.74, "DE QUEM É A CULPA?", R.GOLD_L, True),
       (54.08, 54.84, "COMENTA!", R.WHITE, False)]
ICONS = [(3.3, 5.76, "🏟️", 880, 1170, 160, None), (6.2, 9.7, "⚽", 880, 1170, 150, None), (36.0, 37.84, "💸", 880, 1170, 150, None),
         (40.4, 41.64, "💔", 880, 1170, 150, None), (51.0, 53.74, "📋", 300, 1600, 130, "TÉCNICO"), (51.8, 53.74, "👟", 590, 1600, 130, "JOGADORES"),
         (52.5, 53.74, "💼", 880, 1600, 130, "DIRETORIA"), (54.1, 54.84, "💬", 880, 1170, 150, None)]
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
    if 34.7 <= x < 41.7: return 1.06 + 0.12 * ease_io((x - 34.7) / 7.0)          # opinião: aproxima devagar
    base = 1.0 if ki % 2 == 0 else 1.08                                             # pausa cortada = troca de enquadramento
    u = t - OFF[ki]; return base + 0.05 * (1 - ease_out(u / 0.18)) * (ki > 0)       # soquinho na entrada
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
PEN = f"{V}/pen.mp4"
CLIPS = [(9.3, 11.5, "JORGINHO", "PERDEU"), (23.3, 25.2, "3ª COBRANÇA", "PERDEU"), (37.0, 39.1, "5ª COBRANÇA", "DEFESA DO GOLEIRO")]
_pc = {}
def pen_frame(pt):
    key = int(pt * FPS)
    if not _pc:
        p = subprocess.run(["ffmpeg", "-v", "error", "-i", PEN, "-vf", "fps=30,crop=1080:650:0:660,scale=900:542", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        n = len(p) // (900 * 542 * 3); _pc["a"] = np.frombuffer(p[:n * 900 * 542 * 3], np.uint8).reshape(n, 542, 900, 3)
    a = _pc["a"]; return a[min(len(a) - 1, key)]
def paper(src_txt, head, w=860, fs=56):
    im = Image.new("RGB", (w, 560), PAPER); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 10), fill=BLUE); d.text((40, 50), src_txt, font=R.MF("ExtraBold", 28), fill=BLUE, anchor="lm")
    d.line((40, 82, w - 40, 82), fill=(205, 200, 190), width=2); f = R.SERIF(fs); y = 104
    for l in wrap(head, f, w - 80): d.text((40, y), l, font=f, fill=INK); y += int(fs * 1.18)
    return np.asarray(im)[:int(y + 34) // 2 * 2]
LANCE = paper("LANCE! · ANÁLISE", "Flamengo cai na Libertadores, mas fracasso começa antes dos pênaltis")
def card_bg(w, h, r=26):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), r, fill=(8, 30, 56, 235), outline=R.GOLD + (255,), width=3); return im
def chip(d, x, y, txt, fill, w=150):
    d.rounded_rectangle((x, y, x + w, y + 70), 14, fill=fill); d.text((x + w / 2, y + 36), txt, font=R.BIGF(48), fill=(255, 255, 255, 255), anchor="mm")
ROWS = [(10.1, "JOGO DE IDA", 0, 0, False), (11.46, "JOGO DE VOLTA · MARACANÃ", 0, 0, False), (12.74, "PÊNALTIS", 2, 3, True)]
def score_card(x):
    w, h = 860, 720; im = card_bg(w, h); d = ImageDraw.Draw(im)
    d.text((w / 2, 56), "SEMIFINAL DA LIBERTADORES", font=R.MF("ExtraBold", 34), fill=R.GOLD_L + (255,), anchor="mm")
    for i, (t0, lab, a, b, count) in enumerate(ROWS):
        u = x - t0
        if u < 0: continue
        k = ease_out(u / 0.35); row = Image.new("RGBA", (w, 200), (0, 0, 0, 0)); dr = ImageDraw.Draw(row)
        dr.text((w / 2, 22), lab, font=R.MF("Bold", 26), fill=(205, 215, 230, 255), anchor="mm")
        chip(dr, 60, 60, "FLA", (150, 20, 30, 255)); chip(dr, w - 210, 60, "EST", (120, 20, 30, 255))
        if count: kc = clamp((u - 0.25) / 1.2); va, vb = round(a * kc), round(b * kc)
        else: va, vb = a, b
        dr.text((w / 2, 96), f"{va}  ×  {vb}", font=R.BIGF(110), fill=(255, 255, 255, 255), anchor="mm")
        im.alpha_composite(R.fade(row, k), (0, 110 + i * 195 + int(40 * (1 - k))))
    return im
KICKS = [("FLA", 1), ("EST", 1), ("FLA", 0), ("EST", 0), ("FLA", 0), ("EST", 1), ("FLA", 1), ("EST", 1), ("FLA", 0)]   # ordem real das cobranças
TAGS = {2: "JORGINHO", 4: "PERDEU", 8: "PERDEU"}
def shoot_board(n, u_last):
    w, h = 880, 600; im = card_bg(w, h); d = ImageDraw.Draw(im)
    d.text((w / 2, 50), "DISPUTA DE PÊNALTIS", font=R.MF("ExtraBold", 34), fill=R.GOLD_L + (255,), anchor="mm")
    got = {"FLA": 0, "EST": 0}; cnt = {"FLA": 0, "EST": 0}
    for row, team, fill in ((0, "FLA", (150, 20, 30, 255)), (1, "EST", (120, 20, 30, 255))):
        y = 120 + row * 170; chip(d, 40, y + 25, team, fill, w=140)
        for j in range(5): d.ellipse((215 + j * 115, y + 20, 215 + j * 115 + 80, y + 100), outline=(90, 110, 140, 255), width=4)
    for i in range(min(n, len(KICKS))):
        team, ok = KICKS[i]; j = cnt[team]; cnt[team] += 1; got[team] += ok
        y = 120 + (0 if team == "FLA" else 1) * 170; cx = 255 + j * 115; cy = y + 60
        k = R.back_out(clamp((u_last if i == n - 1 else 9) / 0.25), 2.6); r = 40 * k
        if ok: d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(40, 170, 90, 255)); d.text((cx, cy + 2), "✓" if False else "", fill=(255, 255, 255, 255))
        else:
            d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(200, 30, 40, 255))
            if r > 10: d.line((cx - r * 0.5, cy - r * 0.5, cx + r * 0.5, cy + r * 0.5), fill=(255, 255, 255, 255), width=9); d.line((cx - r * 0.5, cy + r * 0.5, cx + r * 0.5, cy - r * 0.5), fill=(255, 255, 255, 255), width=9)
        if ok and r > 10: d.line((cx - r * 0.45, cy, cx - r * 0.1, cy + r * 0.38, cx + r * 0.5, cy - r * 0.4), fill=(255, 255, 255, 255), width=9, joint="curve")
    d.text((w / 2, 505), f"{got['FLA']}  ×  {got['EST']}", font=R.BIGF(120), fill=(255, 255, 255, 255), anchor="mm")
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
    if k_idx == 0:
        card = score_card(x); R.paste(frame, R.fade(card, kin), CX - card.width / 2, 990 + 240 * (1 - kin), 0.6, 22, (10, 26))
        R.credit(frame, "Fonte: imprensa esportiva (Lance!, site do Flamengo)", CX, 1772, kin, anchor="mm")
    elif k_idx == 1:
        uo = t - out_of(a); tot = out_of(b) - out_of(a); step = (tot - 0.6) / len(KICKS)
        n = min(len(KICKS), int(uo / step) + 1); u_last = uo - (n - 1) * step
        card = shoot_board(n, u_last); miss = (not KICKS[n - 1][1]) and u_last < 0.35
        sx = int(12 * math.sin(u_last * 80) * (1 - u_last / 0.35)) if miss else 0
        R.paste(frame, R.fade(card, kin), CX - card.width / 2 + sx, 1000 + 240 * (1 - kin), 0.6, 22, (10, 26))
        tag = [TAGS[i] for i in TAGS if i < n]
        if n - 1 in TAGS and u_last < step * 1.6: R.pill(frame, TAGS[n - 1], CX, 1660, clamp(u_last / 0.2), fill=(150, 20, 30), size=40)
        if n > 4: R.pill(frame, "PAQUETÁ E BRUNO HENRIQUE TAMBÉM PERDERAM", CX, 1745, clamp((uo - 4 * step) / 0.3), fill=BLUE, size=26)
        if miss:                                                          # flash vermelho no erro
            fl = Image.new("RGBA", frame.size, (200, 20, 30, int(70 * (1 - u_last / 0.35)))); frame.alpha_composite(fl)
    else:
        ci = Image.fromarray(R.rounded(LANCE, 22, 4)).rotate(-1.4, resample=Image.BICUBIC, expand=True)
        R.paste(frame, R.fade(ci, kin), CX - ci.width / 2, 980 + 260 * (1 - kin), 0.6, 22, (10, 26)); y2 = 980 + ci.height + 70
        for j, (t0, emo, txt) in enumerate(((28.12, "📉", "CRIOU POUCO"), (29.84, "⏱️", "0 GOLS EM 180 MINUTOS"), (32.0, "👥", "NÃO APROVEITOU O JOGADOR A MAIS"))):
            if x >= t0:
                if j == 1: txt = f"0 GOLS EM {int(180 * ease_out(clamp((x - t0) / 1.3)))} MINUTOS"
                kk = clamp((x - t0) / 0.25); R.pill(frame, txt, CX + 35, y2 + j * 100, kk, fill=BLUE, size=34)
                pop(frame, emoji(emo, 64), CX + 35 - (R.MF("ExtraBold", 34).getlength(txt) + 50) / 2 - 48, y2 + j * 100, x - t0, 99, wob=False)
        R.credit(frame, "Fonte: Lance! (análise)", CX, 1820, kin, anchor="mm")
    caption(frame, t, SEAM - 70, 44)
    return frame
def caption(frame, t, y, size):
    old = R.RED; R.RED = BLUE
    try: R.draw_caption(frame, t, y, size, ("me", "au"))
    finally: R.RED = old
CARD = ("LIBERTADORES", ["FLAMENGO ELIMINADO", "NOS PÊNALTIS"])
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); x, ki = src_of(tt); sk = split_of(x)
    if sk is not None: frame = split_scene(x, tt, sk)
    else:
        img, idx = graded(x); z = zoom_level(x, ki, tt)
        for a_, b_, w_, c_, shk in BIG:
            if shk and 0 <= x - a_ < 0.4: z += 0.04 * (1 - (x - a_) / 0.4)          # soco de zoom junto com a palavra
        img = zoom(img, z)
        for a_, b_, w_, c_, shk in BIG:
            if shk and 0.05 <= x - a_ < 0.45:
                amp = 14 * (1 - (x - a_ - 0.05) / 0.4); M_ = np.float32([[1, 0, amp * math.sin((x - a_) * 70)], [0, 1, amp * 0.6 * math.cos((x - a_) * 55)]])
                img = cv2.warpAffine(img, M_, (1080, 1920), borderMode=cv2.BORDER_REFLECT)
        frame = Image.fromarray(img).convert("RGBA")
        for i, (a, b, word, col, shk) in enumerate(BIG):                     # palavra grande ACIMA da cabeça (o fundo do carro não deixa recortar limpo)
            if a <= x < b: lay, dx, y = big_layer(word, col, x - a, b - a, shk, i); frame.alpha_composite(lay, (dx, y))
        g = np.zeros((520, W, 4), np.uint8); g[..., :3] = (4, 14, 28); g[..., 3] = np.linspace(0, 200, 520)[:, None].astype(np.uint8); frame.alpha_composite(Image.fromarray(g), (0, H - 520))
        for a, b, ch, cx, cy, sz, lab in ICONS:
            if a <= x < b:
                pop(frame, emoji(ch, sz), cx, cy, x - a, b - a)
                if lab and x - a > 0.15: R.pill(frame, lab, cx, cy + sz / 2 + 40, clamp((x - a - 0.15) / 0.25) * (1 - ease_in((x - (b - 0.2)) / 0.2)), fill=R.NAVY, size=20)
        cy_cap = 1430 if 50.9 <= x < 53.8 else 1520
        caption(frame, tt, cy_cap, 50)
        kc = clamp((tt - 0.6) / 0.4) * (1 - clamp((x - 5.5) / 0.3))
        if kc > 0: BAR.lower_card(frame, CARD[0], CARD[1], 1700, kc, fs=40)
    BAR.draw_bar(frame, clamp(t / END_IN), "canal", ease_out((t - 0.2) / 0.6), 0.0, 0.5 + 0.5 * math.sin(t * 5))
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
    ev += [(out_of(21.62) + 0.1, sfx.paper(), 0.5)] + [(out_of(t0), sfx.click(), 0.4) for t0 in (28.12, 29.84, 32.0)] + [(out_of(t0), sfx.click(), 0.4) for t0, *_r in ROWS]
    ev += [(out_of(t0) + 0.25 + j * 0.4, sfx.click(), 0.25) for t0 in (12.74,) for j in range(5)]
    _st = (out_of(21.62) - out_of(15.45) - 0.6) / len(KICKS)
    ev += [(out_of(15.45) + j * _st, sfx.thud(0.3) if not KICKS[j][1] else sfx.click(), 0.5 if not KICKS[j][1] else 0.4) for j in range(len(KICKS))]
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=80,afftdn=nf=-25,acompressor=threshold=0.08:ratio=2.5:attack=8:release=200:makeup=1.6,asplit=2[vox][k2];[2:a]volume=0.8[sf];[3:a]volume=0.95[sg];"
                    "[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][sgd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
