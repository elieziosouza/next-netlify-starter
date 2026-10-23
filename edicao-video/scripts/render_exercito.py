"""React: querem derrubar o canal Exército do Lula. Ele (parede lisa, recorte limpo) com palavras gigantes ATRÁS dele, o vídeo do Bê Moreira
e do Janones num card na frente dele (frases inteiras, sem o "vagabundo do PL"), tela dividida com a manchete e os fatos checados
(Flávio pediu ao TSE em 10/10; corregedor deu 72 h; TSE ainda não decidiu) e o final "domingo vocês não escapam". Zoom lento contínuo."""
import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
sys.path.insert(0, f"{S}/work")
import sfx, grading
from segment_person import PersonSeg
BLUE = (14, 62, 120); PAPER = (247, 244, 236); INK = (22, 26, 34)
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; ease_out = R.ease_out; ease_in = R.ease_in; ease_io = R.ease_io
V = f"{S}/v55"; ME = f"{V}/me.mp4"; CL = f"{V}/cl.mp4"
GRADE = grading.Fast(None, f"{S}/grade/lut_cinema_pele4.npy", 0.08, 6)
SEG = PersonSeg("/root/.cache/edicao-video/seg/u2net_human_seg.onnx")
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
# (fonte, início, fim, modo): me = ele em tela cheia; cl = vídeo deles num card na frente dele; news = tela dividida com os fatos
PARTS = [("me", 0.40, 3.55, "full"), ("me", 3.79, 7.46, "full"), ("cl", 0.10, 9.52, "react"), ("cl", 12.0, 19.46, "react"),
         ("me", 8.28, 12.70, "news"), ("me", 12.92, 16.36, "news"), ("me", 16.86, 18.82, "full"), ("me", 19.12, 23.16, "full"), ("me", 23.42, 25.45, "full")]
segs = []; acc = 0.0
for src_, a, b, mode in PARTS: segs.append(dict(src=src_, a=a, b=b, mode=mode, t0=acc, t1=acc + b - a)); acc += b - a
EDIT_END = acc; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = EDIT_END; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
def seg_at(t):
    for i, s in enumerate(segs):
        if t < s["t1"]: return i
    return len(segs) - 1
def om(src_, x):                                                     # tempo de saída de um instante da fonte
    for s in segs:
        if s["src"] == src_ and s["a"] <= x <= s["b"]: return s["t0"] + x - s["a"]
    return None
ME_CAPS = [("E VOCÊS VIRAM ESSA ÚLTIMA?", 0.40, 1.9), ("ELES ESTÃO DESESPERADOS.", 1.9, 3.5), ("ESTÃO QUERENDO DERRUBAR", 3.84, 5.0),
           ("O CANAL DO EXÉRCITO DO LULA.", 5.0, 6.4), ("ISSO É UMA VERGONHA.", 6.4, 7.42), ("ESTÃO QUERENDO USAR", 8.3, 9.4),
           ("OS MINISTROS DO BOLSONARO", 9.4, 10.9), ("QUE ESTÃO LÁ NO TSE PARA FAZER ISSO.", 10.9, 12.64), ("SE ISSO ACONTECER,", 12.98, 14.0),
           ("É UMA VERGONHA.", 14.0, 14.9), ("ISSO SÓ MOSTRA QUE VOCÊS VÃO PERDER.", 14.9, 16.3), ("DOMINGO, DIA 25,", 16.88, 18.78),
           ("VAI SER INEVITÁVEL.", 19.16, 20.4), ("VOCÊS PODEM ATÉ DERRUBAR", 20.4, 21.8), ("O CANAL DO EXÉRCITO DO LULA,", 21.8, 23.12),
           ("MAS DOMINGO", 23.48, 24.24), ("VOCÊS NÃO ESCAPAM.", 24.44, 25.4)]
CL_CAPS = [("VÃO DERRUBAR O CANAL EXÉRCITO DO LULA", 0.12, 3.3), ("A QUALQUER MOMENTO", 3.3, 4.4), ("SE A GENTE NÃO SE MOBILIZAR.", 4.4, 5.38),
           ("QUEREM CENSURAR,", 5.6, 6.6), ("PORQUE SABEM QUE AQUI", 6.6, 7.32), ("VIROU A ELEIÇÃO IGUAL EM 2022.", 7.62, 9.5),
           ("ESTÁ NA MÃO JÁ DO MINISTRO", 12.0, 13.54), ("KASSIO NUNES", 13.8, 14.8), ("O PEDIDO DE DERRUBADA", 14.8, 16.2),
           ("DO CANAL EXÉRCITO DO LULA.", 16.2, 17.8), ("A GENTE VAI PRA CIMA.", 17.8, 19.44)]
HOT = {"DESESPERADOS.", "DERRUBAR", "EXÉRCITO", "LULA.", "LULA,", "VERGONHA.", "MINISTROS", "BOLSONARO", "TSE", "PERDER.", "DOMINGO,", "25,", "INEVITÁVEL.",
       "ESCAPAM.", "CENSURAR,", "2022.", "KASSIO", "NUNES", "CIMA."}
CAPS = []
for src_, lst in (("me", ME_CAPS), ("cl", CL_CAPS)):
    for txt, a, b in lst:
        for s in segs:
            if s["src"] != src_: continue
            a1, b1 = max(a, s["a"]), min(b, s["b"])
            if b1 - a1 < 0.25: continue
            a2, b2 = s["t0"] + a1 - s["a"], s["t0"] + b1 - s["a"]; ws = txt.split(); tot = sum(len(w) + 2 for w in ws); k = 0; ts = []
            for w in ws: ts.append(a2 + (b2 - a2 - 0.08) * k / tot); k += len(w) + 2
            CAPS.append(dict(words=ws, ts=ts, start=a2, end=b2, src="au" if any(w in HOT for w in ws) else "me"))
CAPS.sort(key=lambda c: c["start"]); R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
# palavras gigantes ATRÁS dele (tempo da fonte "me")
BIG = [(3.84, 6.35, "DERRUBAR O CANAL?", R.WHITE, False), (6.35, 7.46, "VERGONHA", R.GOLD_L, True), (16.88, 18.82, "DOMINGO, 25", R.GOLD_L, True),
       (19.16, 20.4, "INEVITÁVEL", R.WHITE, False), (23.48, 25.45, "NÃO ESCAPAM", R.GOLD_L, True)]
ICONS = [(0.5, 3.5, "😱", 880, 1150, 150, None), (20.4, 23.1, "📺", 880, 1150, 150, None), (23.6, 25.45, "🗳️", 880, 1150, 160, None)]
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
    frame.alpha_composite(R.fade(im, 1 - out), (int(cx - im.width / 2), int(cy - im.height / 2)))
_ch = {}; _gr = {}; _mk = {}
def raw_frame(x):
    key = int(x // 6)
    if key not in _ch:
        if len(_ch) > 2: _ch.clear()
        p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{key * 6:.3f}", "-t", "6.2", "-i", ME, "-vf", "fps=30", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        n = len(p) // (1080 * 1920 * 3); _ch[key] = np.frombuffer(p[:n * 1080 * 1920 * 3], np.uint8).reshape(n, 1920, 1080, 3)
    fr = _ch[key]; i = min(len(fr) - 1, int((x - key * 6) * FPS)); return fr[i], key * 1000 + i
def graded(x):
    fr, idx = raw_frame(x)
    if idx not in _gr:
        if len(_gr) > 40: _gr.clear()
        _gr[idx] = GRADE(fr)
    return _gr[idx], idx
_yy, _xx = np.mgrid[0:1920, 0:1080].astype(np.float32)
_el = ((_xx - 530) / 290) ** 2 + ((_yy - 790) / 470) ** 2
HEAD_PRIOR = np.maximum(np.clip((1.12 - _el) / 0.24, 0, 1), np.clip((_yy - 1180) / 80, 0, 1))
def person_mask(img, idx):
    if idx not in _mk:
        if len(_mk) > 40: _mk.clear()
        m = SEG(img); m = np.clip((m - 0.35) / 0.35, 0, 1) * HEAD_PRIOR; _mk[idx] = cv2.GaussianBlur(m, (0, 0), 1.6)[..., None]
    return _mk[idx]
def zoom(img, z, cx=530, cy=820):
    if abs(z - 1) < 1e-3: return img
    M = np.float32([[z, 0, cx * (1 - z)], [0, z, cy * (1 - z)]]); return cv2.warpAffine(img, M, (1080, 1920), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
def zoom_level(t, i):
    base = 1.0 if i % 2 == 0 else 1.07; u = t - segs[i]["t0"]
    z = base + 0.05 * (1 - ease_out(u / 0.18)) * (i > 0) + 0.03 * (0.5 - 0.5 * math.cos(2 * math.pi * t / 7.0))
    return z
def big_layer(word, col, u, dur, shake, idx, cy=262):
    size = 300; f = R.BIGF(size)
    while f.getlength(word) > 840 or (f.getbbox(word)[3] - f.getbbox(word)[1]) > 205: size -= 6; f = R.BIGF(size)
    lay = Image.new("RGBA", (W, int(size * 1.35)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text((CX + 5, lay.height / 2 + 7), word, font=f, fill=(0, 0, 0, 70), anchor="mm")
    d.text((CX, lay.height / 2), word, font=f, fill=col + (205,), anchor="mm", stroke_width=4, stroke_fill=R.NAVY + (190,))
    k = ease_out(u / 0.3); out = ease_in((u - (dur - 0.25)) / 0.25); sc = 1.18 - 0.18 * k + 0.06 * out
    if abs(sc - 1) > 0.003:
        nw, nh = int(W * sc), int(lay.height * sc); bg = lay.resize((nw, nh), Image.BICUBIC); ox = int(CX * sc - CX); oy = (nh - lay.height) // 2
        lay = bg.crop((ox, oy, ox + W, oy + lay.height))
    dx = dy = 0
    if shake and 0.3 < u < 1.0: a_ = 7 * (1 - (u - 0.3) / 0.7); dx = a_ * math.sin(u * 90); dy = a_ * 0.6 * math.cos(u * 70)
    return R.fade(lay, k * (1 - out)), int(dx), int(cy - lay.height / 2 + dy)
def caption(frame, t, y, size):
    old = R.RED; R.RED = BLUE
    try: R.draw_caption(frame, t, y, size, ("me", "au"))
    finally: R.RED = old
def wrap(txt, font, maxw):
    lines, cur = [], ""
    for w in txt.split():
        t2 = (cur + " " + w).strip()
        if font.getlength(t2) <= maxw: cur = t2
        else: lines.append(cur); cur = w
    return lines + [cur]
def paper(src_txt, head, w=860, fs=54):
    im = Image.new("RGB", (w, 560), PAPER); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 10), fill=BLUE); d.text((40, 50), src_txt, font=R.MF("ExtraBold", 28), fill=BLUE, anchor="lm")
    d.line((40, 82, w - 40, 82), fill=(205, 200, 190), width=2); f = R.SERIF(fs); y = 104
    for l in wrap(head, f, w - 80): d.text((40, y), l, font=f, fill=INK); y += int(fs * 1.18)
    return np.asarray(im)[:int(y + 34) // 2 * 2]
NEWS = paper("CORREIO BRAZILIENSE · 10/10", "Flávio pede derrubada de canal pró-Lula; TSE pede esclarecimentos")
FACTS = [(8.6, "📅", "10/10: FLÁVIO PEDIU AO TSE A SUSPENSÃO DO CANAL"), (10.4, "⏱️", "O CORREGEDOR DEU 72 HORAS PARA ELE SE EXPLICAR"),
         (13.2, "⚖️", "ATÉ AGORA, O TSE NÃO DECIDIU"), (14.6, "ℹ️", "NUNES MARQUES E MENDONÇA: INDICADOS POR BOLSONARO")]
NAVY_BG = np.clip(R.NAVYBG, 0, 255).astype(np.uint8)
SEAM = 900
_cl = {}
def cl_frame(x):
    if not _cl:
        p = subprocess.run(["ffmpeg", "-v", "error", "-i", CL, "-vf", "fps=30,scale=460:818", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        n = len(p) // (460 * 818 * 3); _cl["a"] = np.frombuffer(p[:n * 460 * 818 * 3], np.uint8).reshape(n, 818, 460, 3)
    a = _cl["a"]; return a[int(clamp(x * FPS, 0, len(a) - 1))]
def listen_x(t):                                                       # ele ouvindo: vai e volta num trecho calado do fim
    L = 0.7; p = (t * 0.35) % (2 * L); return 7.50 + (p if p < L else 2 * L - p)        # pausa entre as frases, em câmera lenta
CARD = ("DENÚNCIA", ["QUEREM DERRUBAR O", "EXÉRCITO DO LULA"])
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); i = seg_at(tt); s = segs[i]; u = tt - s["t0"]; x = s["a"] + u
    if s["mode"] == "news":
        img, idx = graded(x)
        top = img[300:1400]; tw = int(1080 * SEAM / 1100); fg = cv2.resize(top, (tw, SEAM), interpolation=cv2.INTER_AREA)
        bg = cv2.resize(cv2.GaussianBlur(cv2.resize(top, (108, 90)), (0, 0), 3), (W, SEAM)).astype(np.float32) * 0.55
        x0 = CX - tw // 2; fm = np.ones((SEAM, tw), np.float32); fm[:, :50] = np.linspace(0, 1, 50)[None]; fm[:, -50:] = np.linspace(1, 0, 50)[None]; fm = fm[..., None]
        xs, xe = max(0, x0), min(W, x0 + tw); bg[:, xs:xe] = bg[:, xs:xe] * (1 - fm[:, xs - x0:xe - x0]) + fg[:, xs - x0:xe - x0] * fm[:, xs - x0:xe - x0]
        base = NAVY_BG.copy(); base[:SEAM] = bg.astype(np.uint8)
        frame = Image.fromarray(base).convert("RGBA"); ImageDraw.Draw(frame).rectangle((0, SEAM - 2, W, SEAM + 3), fill=R.GD)
        u0 = x - 8.28; kin = ease_out(u0 / 0.4)
        ci = Image.fromarray(R.rounded(NEWS, 22, 4)).rotate(-1.4, resample=Image.BICUBIC, expand=True)
        R.paste(frame, R.fade(ci, kin), CX - ci.width / 2, 975 + 260 * (1 - kin), 0.6, 22, (10, 26)); y2 = 975 + ci.height + 60
        for j, (t0, emo, txt) in enumerate(FACTS):
            if x >= t0:
                kk = clamp((x - t0) / 0.25); sz = 26
                while R.MF("ExtraBold", sz).getlength(txt) + 50 > 780: sz -= 1
                R.pill(frame, txt, CX + 30, y2 + j * 86, kk, fill=BLUE if j < 3 else R.NAVY, size=sz)
                pop(frame, emoji(emo, 56), CX + 30 - (R.MF("ExtraBold", sz).getlength(txt) + 50) / 2 - 42, y2 + j * 86, x - t0, 99, wob=False)
        R.credit(frame, "Fontes: Correio Braziliense, Brasil de Fato, SBT News", CX, 1830, kin, anchor="mm")
        caption(frame, tt, SEAM - 70, 44)
    else:
        mx = listen_x(tt) if s["mode"] == "react" else x
        img, idx = graded(mx); z = zoom_level(tt, i)
        bigs = [(j, b) for j, b in enumerate(BIG) if s["src"] == "me" and b[0] <= x < b[1]]
        if bigs:
            m = person_mask(img, idx); fr = Image.fromarray(img).convert("RGBA")
            for j, (a, b, word, col, shk) in bigs:
                lay, dx, y = big_layer(word, col, x - a, b - a, shk, j); fr.alpha_composite(lay, (dx, y))
            comp = np.asarray(fr.convert("RGB")).astype(np.float32); img = (comp * (1 - m) + img.astype(np.float32) * m).astype(np.uint8)
            for a, b, w_, c_, shk in BIG:
                if shk and 0 <= x - a < 0.4: z += 0.04 * (1 - (x - a) / 0.4)
        img = zoom(img, z)
        frame = Image.fromarray(img).convert("RGBA")
        g = np.zeros((520, W, 4), np.uint8); g[..., :3] = (4, 14, 28); g[..., 3] = np.linspace(0, 200, 520)[:, None].astype(np.uint8); frame.alpha_composite(Image.fromarray(g), (0, H - 520))
        if s["mode"] == "react":
            kin = ease_out((tt - segs[2]["t0"]) / 0.45)
            card = R.rounded(cv2.LUT(cl_frame(x), R.LUT), 24, 4); ci = Image.fromarray(card).rotate(-1.5, resample=Image.BICUBIC, expand=True)
            R.paste(frame, R.fade(ci, kin), CX - ci.width / 2, 1010 + 300 * (1 - kin), 0.65, 24, (10, 26))
            lab = "BÊ MOREIRA E ANDRÉ JANONES · REDES SOCIAIS" if s["a"] < 10 else "SEGUNDO ELES, O PEDIDO ESTÁ COM KASSIO NUNES MARQUES"
            R.pill(frame, lab, CX, 975, clamp(u / 0.3), fill=BLUE if s["a"] < 10 else R.NAVY, size=24)
            pass                                                         # o vídeo deles já tem legenda queimada
        else:
            for a, b, ch, cx, cy, sz, lab in ICONS:
                if a <= x < b: pop(frame, emoji(ch, sz), cx, cy, x - a, b - a)
            caption(frame, tt, 1520, 50)
            kc = clamp((tt - 0.6) / 0.4) * (1 - clamp((tt - (segs[1]["t1"] - 0.4)) / 0.3)) if i <= 1 else 0
            if kc > 0: BAR.lower_card(frame, CARD[0], CARD[1], 1700, kc, fs=40)
    BAR.draw_bar(frame, clamp(t / END_IN), "canal", ease_out((t - 0.2) / 0.6), 0.0, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(frame, t)
    for j in range(1, len(segs)):
        if segs[j]["mode"] != segs[j - 1]["mode"] and abs(t - segs[j]["t0"]) < 0.08:
            frame = Image.blend(frame, Image.new("RGBA", frame.size, (255, 255, 255, 255)), (1 - abs(t - segs[j]["t0"]) / 0.08) * 0.35)
    if t >= END_IN: frame.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return frame.convert("RGB")

def main():
    if MODE == "lib": return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(t).resize((360, 640), Image.LANCZOS) for t in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    if MODE == "info": print("TOTAL", round(TOTAL, 2), [(s["src"], s["mode"], round(s["t0"], 2)) for s in segs]); return
    vout = f"{V}/video.mp4"
    if not (os.environ.get("REUSE") and os.path.exists(vout)):
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
        for k in range(int(round(TOTAL * FPS))): enc.stdin.write(frame_at(k / FPS).tobytes())
        enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    for nm, p in (("me", ME), ("cl", CL)): subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-ar", "48000", "-ac", "2", f"{V}/{nm}48.wav"], check=True)
    src = {"me": R.readw(f"{V}/me48.wav"), "cl": R.readw(f"{V}/cl48.wav") * float(os.environ.get("CLG", "0.9"))}
    def rms(c): v = c[np.abs(c).max(1) > 0.01]; return float(np.sqrt((v ** 2).mean())) if len(v) else 1e-6
    ref = {k: np.median([rms(src[k][int(s["a"] * SR):int(s["b"] * SR)]) for s in segs if s["src"] == k]) for k in src}
    vt = np.zeros((n, 2), np.float32); f = int(0.012 * SR)
    for s in segs:
        c = src[s["src"]][int(s["a"] * SR):int(s["b"] * SR)].copy(); c *= min(2.0, ref[s["src"]] / rms(c))
        if s["src"] == "cl": c *= 10 ** (-3.5 / 20) * ref["me"] / ref["cl"]          # voz dele 3-4 dB acima da de terceiros
        c[:f] *= np.linspace(0, 1, f)[:, None]; c[-f:] *= np.linspace(1, 0, f)[:, None]
        o = int(s["t0"] * SR); vt[o:o + len(c)] += c[:n - o]
    R.writew(f"{V}/voice.wav", vt)
    bed = R.readw(os.environ.get("BED", f"{S}/v52/tense.wav")); L = min(len(bed), n); tl = np.arange(L) / SR
    gain = (float(os.environ.get("BEDG", "0.17")) * np.clip(tl / 1.0, 0, 1) + 0.08 * np.clip((tl - (EDIT_END - 0.3)) / 0.5, 0, 1)) * np.clip(1 - (tl - (TOTAL - 1.6)) / 1.5, 0, 1)
    sg = np.zeros((n, 2), np.float32); sg[:L] = bed[:L] * gain[:, None]; R.writew(f"{V}/song.wav", sg)
    ev = [(0.0, sfx.whoosh(0.4), 0.2), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
    for a, b, *_r in BIG:
        ta = om("me", a)
        if ta is not None: ev += [(ta, sfx.whoosh(0.35), 0.24), (ta + 0.26, sfx.click(), 0.7), (ta + 0.26, sfx.thud(0.3), 0.2)]
    for a, b, *_r in ICONS:
        ta = om("me", a)
        if ta is not None: ev += [(ta, sfx.click(), 0.45)]
    for j in range(1, len(segs)):
        if segs[j]["mode"] != segs[j - 1]["mode"]: ev += [(segs[j]["t0"] - 0.1, sfx.whoosh(0.45), 0.24)]
    for t0, *_r in FACTS:
        ta = om("me", t0)
        if ta is not None: ev += [(ta, sfx.click(), 0.4)]
    ev += [(segs[4]["t0"] + 0.1, sfx.paper(), 0.5)]
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=80,acompressor=threshold=0.08:ratio=2.5:attack=8:release=200:makeup=1.6,asplit=2[vox][k2];[2:a]volume=0.8[sf];[3:a]volume=0.95[sg];"
                    "[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][sgd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
