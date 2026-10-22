"""Reels: cartaz "THE WORLD NEEDS LULA" num ponto de ônibus em Londres, perto do Big Ben (vídeo do Portal Multi+, sem a moldura e o post deles).
Ele provoca em tela cheia, o cartaz entra em tela cheia com ele reagindo numa janelinha (áudio do rapaz sem o palavrão), fecha com o "Postei!"."""
import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
import sfx
BLUE = (14, 62, 120)
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; ease_out = R.ease_out; ease_in = R.ease_in
V = f"{S}/v49"; ME = f"{V}/me.mp4"; CL = f"{V}/cl.mp4"
PARTS = [("me", 0.05, 3.75), ("cl", 13.6, 27.6), ("-", 0, 3.4, "h1"), ("-", 0, 3.8, "h2"), ("me", 4.25, 7.2)]
MUTE = [(19.4, 23.0)]
BIPS = [(5.62, 6.28), (11.42, 12.02), (17.28, 17.88), (22.95, 23.67)]   # palavrões da música, cobertos com bip                                               # palavrão do rapaz: sem o áudio dele aqui
segs = []; acc = 0.0
for p_ in PARTS: src_, a, b = p_[:3]; segs.append(dict(src=src_, a=a, b=b, t0=acc, t1=acc + b - a, card=p_[3] if len(p_) > 3 else None)); acc += b - a
EDIT_END = acc; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = EDIT_END; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
def seg_at(t):
    for s in segs:
        if t < s["t1"]: return s
    return segs[-1]
def segmap(i, x): return segs[i]["t0"] + x - segs[i]["a"]
FULL = MODE == "full" or MODE.startswith("frames")
MEF = R.decode(ME, 0, 8.1, 720, 1280, "scale=720:1280") if FULL else None
LX, LY, LW, LH = 20, 20, 1040, 1340                                  # sem a moldura colorida e o post do portal
CLF = R.decode(CL, 13.5, 27.7, 520, 670, f"crop={LW}:{LH}:{LX}:{LY},scale=520:670") if FULL else None
PAPER = (247, 244, 236); INK = (22, 26, 34)
HEADS = {"h1": ("PORTAL MULTI+", "Painel em Londres homenageia Lula com mensagem sobre soberania da América Latina"),
         "h2": ("MÍDIA NINJA · DOMINGO, 18/10", "Brasileiros se reúnem em Londres em defesa da democracia e em apoio a Lula")}
SUBS = {"h2": "Ato na Parliament Square, ao lado do Big Ben, com a presença de Jeremy Corbyn"}
def wrap(txt, font, maxw):
    lines, cur = [], ""
    for w in txt.split():
        t = (cur + " " + w).strip()
        if font.getlength(t) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]
_hc = {}
def head_card(key):
    """recorte de jornal: papel claro, veículo e data em cima, manchete em serifa (texto conferido, sem logo)"""
    if key in _hc: return _hc[key]
    w = 900; im = Image.new("RGB", (w, 700), PAPER); d = ImageDraw.Draw(im); src, txt = HEADS[key]
    d.rectangle((0, 0, w, 10), fill=BLUE); d.text((44, 52), src, font=R.MF("ExtraBold", 28), fill=BLUE, anchor="lm")
    d.line((44, 84, w - 44, 84), fill=(205, 200, 190), width=2)
    for sz in range(66, 30, -2):
        f = R.SERIF(sz); ls = wrap(txt, f, w - 88)
        if len(ls) * sz * 1.18 <= 330: break
    y = 110
    for l in ls: d.text((44, y), l, font=f, fill=INK); y += sz * 1.18
    if key in SUBS:
        fs_ = R.MF("SemiBold", 30); y += 14
        for l in wrap(SUBS[key], fs_, w - 88): d.text((44, y), l, font=fs_, fill=(70, 74, 84)); y += 40
    _hc[key] = np.asarray(im)[:int(y + 40) // 2 * 2]; return _hc[key]
FOTO = np.asarray(Image.open(f"{V}/foto_bigben.jpg").convert("RGB"))                 # foto do cartaz com o Big Ben (redes sociais)
STILL = None
def fr_of(arr, x): return arr[int(clamp(x * FPS, 0, len(arr) - 1))]
def me_big(x): return cv2.resize(fr_of(MEF, x), (1080, 1920), interpolation=cv2.INTER_LINEAR)
FIT = 0.88; _fw, _fh = int(W * FIT), int(H * FIT); _fx = CX - _fw // 2; _fy = H - _fh
_fm = np.ones((_fh, _fw), np.float32); _fm[:, :30] = np.linspace(0, 1, 30)[None, :]; _fm[:, -30:] = np.linspace(1, 0, 30)[None, :]; _fm[:30] *= np.linspace(0, 1, 30)[:, None]; _fm = _fm[..., None]
def me_full(x):
    img = me_big(x); bg = cv2.resize(cv2.GaussianBlur(cv2.resize(img, (W // 10, H // 10)), (0, 0), 2.5), (W, H)).astype(np.float32) * 0.7
    fg = cv2.resize(cv2.LUT(img, R.LUT), (_fw, _fh), interpolation=cv2.INTER_AREA).astype(np.float32)
    bg[_fy:, _fx:_fx + _fw] = bg[_fy:, _fx:_fx + _fw] * (1 - _fm) + fg * _fm
    return bg
def react_x(t):
    u = (t * 0.5) % 2.4
    return 5.3 + (u if u < 1.2 else 2.4 - u)                        # ele olhando, com cara de "pois é"
ME_CAPS = [("AGORA OS BOLSONARISTAS CHORAM,", 0.15, 1.86), ("MAS EU VOU POSTAR ASSIM MESMO, TÁ?", 2.33, 3.62), ("POSTEI!", 4.44, 4.95)]
CL_CAPS = [("“É ELE MESMO, É O LULA.”", 14.26, 16.07), ("“LEGAL, LEGAL, LEGAL.”", 23.0, 24.8), ("“ACHEI QUE FOSSE INTELIGÊNCIA ARTIFICIAL,", 24.8, 26.6), ("MAS NÃO.”", 26.6, 27.33)]
HOT = {"CHORAM,", "POSTAR", "POSTEI!", "LULA.”", "ARTIFICIAL,", "NÃO.”"}
CAPS = []
for i, s in enumerate(segs):
    for txt, a, b in (ME_CAPS if s["src"] == "me" else CL_CAPS):
        a, b = max(a, s["a"]), min(b, s["b"])
        if b - a < 0.25: continue
        a2, b2 = segmap(i, a), segmap(i, b); ws = txt.split(); tot = sum(len(w) + 2 for w in ws); k = 0; ts = []
        for w in ws: ts.append(a2 + (b2 - a2 - 0.1) * k / tot); k += len(w) + 2
        CAPS.append(dict(words=ws, ts=ts, start=a2, end=b2, src="au" if any(w in HOT for w in ws) else "me"))
CAPS.sort(key=lambda c: c["start"]); R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
BIG = [(0, 0.9, 1.9, "CHORAM", R.WHITE), (2, 0.4, 3.2, "SOBERANIA", R.WHITE), (3, 0.4, 3.6, "AO LADO DO BIG BEN", R.GOLD_L), (1, 16.2, 19.3, "O MUNDO PRECISA DE LULA", R.GOLD_L), (1, 14.3, 16.1, "É O LULA!", R.WHITE),
       (1, 25.0, 27.4, "NÃO É IA", R.GOLD_L), (4, 4.42, 6.4, "POSTEI!", R.GOLD_L)]
BIG = [(segmap(i, a), segmap(i, b), w, c) for i, a, b, w, c in BIG]
PILLS = [(1, 13.8, 19.3, "LONDRES, PERTO DO BIG BEN", R.NAVY), (1, 19.4, 24.8, "TRADUÇÃO: “O MUNDO PRECISA DE LULA”", BLUE),
         (2, 0.6, 3.3, "NO CARTAZ: “A AMÉRICA LATINA NÃO É QUINTAL DO TRUMP”", BLUE)]
PILLS = [(segmap(i, a), segmap(i, b), x, c) for i, a, b, x, c in PILLS]
CARD = ("LONDRES", ["“O MUNDO PRECISA", "DE LULA”"])
CTA = [(segmap(4, 4.4), segmap(4, 7.0))]
def cta_level(t): return max([clamp((t - a) / 0.4) * clamp((b - t) / 0.4) for a, b in CTA] + [0.0])
def caption(frame, t, y, size, tracks):
    old = R.RED; R.RED = BLUE
    try: R.draw_caption(frame, t, y, size, tracks)
    finally: R.RED = old
def big_word(frame, t, zone):
    z0, z1 = zone
    for i, (a, b, word, col) in enumerate(BIG):
        if not (a <= t < b): continue
        u = t - a; k = ease_out(u / 0.28); out = ease_in((t - (b - 0.22)) / 0.22)
        size = 200
        while True:
            f = R.BIGF(size); bb = f.getbbox(word, stroke_width=10)
            if (bb[3] - bb[1]) <= (z1 - z0) - 16 and (bb[2] - bb[0]) <= 680: break
            size -= 4
        lay = Image.new("RGBA", (W, bb[3] - bb[1] + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.text((W / 2 - (bb[0] + bb[2]) / 2 + 5, 10 - bb[1] + 7), word, font=f, fill=(0, 0, 0, 120), stroke_width=10, stroke_fill=(0, 0, 0, 120))
        d.text((W / 2 - (bb[0] + bb[2]) / 2, 10 - bb[1]), word, font=f, fill=col + (255,), stroke_width=10, stroke_fill=R.NAVY + (255,))
        dx = (1 if i % 2 == 0 else -1) * W * 0.95 * (1 - k)
        if u < 0.28:
            Lb = int(60 * (1 - k)) + 1
            if Lb > 2: lay = Image.fromarray(cv2.filter2D(np.asarray(lay), -1, np.ones((1, Lb), np.float32) / Lb))
        frame.alpha_composite(R.fade(lay, 1 - out), (int(CX - W / 2 + dx), int((z0 + z1) / 2 - lay.height / 2)))
def pill_size(txt, size=30):
    while R.MF("ExtraBold", size).getlength(txt) + 50 > 660: size -= 1
    return size
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); s = seg_at(tt); x = s["a"] + min(tt, s["t1"] - 0.02) - s["t0"]
    if s["src"] == "-":                                              # recortes das matérias, ele reagindo na janelinha
        u = t - s["t0"]; im = fr_of(CLF, 3.7)                                       # o ônibus com o Big Ben ao fundo
        frame = Image.fromarray(np.clip(R.blur_bg(im, 0.30), 0, 255).astype(np.uint8)).convert("RGBA")
        card = head_card(s["card"]); kin = ease_out(u / 0.4); cy0 = 470
        ph = FOTO[560:1090, 360:760] if s["card"] == "h1" else FOTO; pw_ = 430 if s["card"] == "h1" else 400
        phi = cv2.resize(cv2.LUT(ph, R.LUT), (pw_, int(pw_ * ph.shape[0] / ph.shape[1])), interpolation=cv2.INTER_AREA)
        pol = Image.new("RGBA", (pw_ + 28, phi.shape[0] + 28), (250, 250, 250, 255)); pol.paste(Image.fromarray(phi), (14, 14))   # foto com borda branca
        pol = pol.rotate(2.5 if s["card"] == "h1" else -2.5, resample=Image.BICUBIC, expand=True)
        kp = ease_out((u - 0.25) / 0.4); py = cy0 + card.shape[0] - 30
        R.paste(frame, R.fade(pol, kp), CX - pol.width / 2 + (60 if s["card"] == "h1" else -60), py + 200 * (1 - kp), 0.6, 22, (10, 26))
        cardi = Image.fromarray(R.rounded(card, 22, 4)).rotate(-1.5 if s["card"] == "h1" else 1.2, resample=Image.BICUBIC, expand=True)
        R.paste(frame, R.fade(cardi, kin), CX - cardi.width / 2, cy0 + 300 * (1 - kin), 0.6, 22, (10, 26))
        win = Image.fromarray(R.rounded(cv2.resize(cv2.LUT(me_big(react_x(t))[260:1460], R.LUT), (300, 300), interpolation=cv2.INTER_AREA), 150, 4))
        R.paste(frame, win, CX - 150, 160, 0.55, 18, (6, 16))
        R.credit(frame, "Recorte: " + HEADS[s["card"]][0].split(" ·")[0] + " · Foto: reprodução redes sociais", CX, 1840, kin, anchor="mm")
        zb = py + pol.height + 10
        for a_, b_, txt, colr in PILLS:
            if a_ <= t < b_: R.pill(frame, txt, CX, zb + 34, clamp((t - a_) / 0.3) * clamp((b_ - t) / 0.25), fill=colr, size=pill_size(txt)); zb += 70
        big_word(frame, t, (zb, 1800))                                          # embaixo da foto e do selo, sem encostar
    elif s["src"] == "cl":                                           # o cartaz em tela cheia, ele reagindo na janelinha
        u = t - s["t0"]; im = fr_of(CLF, x - 13.5)
        bg = np.clip(R.blur_bg(im, 0.35), 0, 255).astype(np.uint8); frame = Image.fromarray(bg).convert("RGBA")
        cw = 980; card = cv2.resize(cv2.LUT(im, R.LUT), (cw, int(cw * im.shape[0] / im.shape[1])), interpolation=cv2.INTER_LINEAR)
        kin = ease_out(u / 0.35); cy0 = 130
        R.paste(frame, R.fade(Image.fromarray(R.rounded(card, 28, 5)), kin), CX - cw / 2, cy0 + 60 * (1 - kin), 0.6, 22, (10, 26))
        R.credit(frame, "Vídeo: reprodução Portal Multi+", CX, 1820, kin, anchor="mm")
        win = Image.fromarray(R.rounded(cv2.resize(cv2.LUT(me_big(react_x(t))[260:1460], R.LUT), (260, 260), interpolation=cv2.INTER_AREA), 130, 4))
        R.paste(frame, win, CX + cw / 2 - 290, cy0 + 30, 0.55, 18, (6, 16))
        big_word(frame, t, (cy0 + card.shape[0] + 10, cy0 + card.shape[0] + 200))
        for a, b, txt, colr in PILLS:
            if a <= t < b: R.pill(frame, txt, CX, cy0 + card.shape[0] - 46, clamp((t - a) / 0.3) * clamp((b - t) / 0.25), fill=colr, size=pill_size(txt))
        caption(frame, t, 1680, 46, ("me", "au"))
    else:
        frame = Image.fromarray(np.clip(me_full(x), 0, 255).astype(np.uint8)).convert("RGBA")
        big_word(frame, t, (130, 430)); caption(frame, t, 1500, 48, ("me", "au"))
        kc = clamp((t - 0.6) / 0.4) * (1 - clamp((t - (END_IN - 0.35)) / 0.35)) if s is segs[-1] else 0.0
        if kc > 0: BAR.lower_card(frame, CARD[0], CARD[1], 1655, kc, fs=40)
    BAR.draw_bar(frame, clamp(t / END_IN), "canal", ease_out((t - 0.2) / 0.6), cta_level(t), 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(frame, t)
    for e in [sg["t0"] for sg in segs[1:]]:
        if abs(t - e) < 0.09: frame = Image.blend(frame, Image.new("RGBA", frame.size, (255, 255, 255, 255)), (1 - abs(t - e) / 0.09) * 0.4)
    if t >= END_IN: frame.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return frame.convert("RGB")

def main():
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(t).resize((360, 640), Image.LANCZOS) for t in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    if MODE == "info": print("TOTAL", round(TOTAL, 2), [(p[0], round(s["t0"], 2)) for p, s in zip(PARTS, segs)]); return
    vout = f"{V}/video.mp4"
    if not (os.environ.get("REUSE") and os.path.exists(vout)):
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
        for i in range(int(round(TOTAL * FPS))): enc.stdin.write(frame_at(i / FPS).tobytes())
        enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", ME, "-ar", "48000", "-ac", "2", f"{V}/me48.wav"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", CL, "-ar", "48000", "-ac", "2", f"{V}/cl48.wav"], check=True)
    srcw = {"me": R.readw(f"{V}/me48.wav") * float(os.environ.get("MEG", "0.55")), "cl": R.readw(f"{V}/cl48.wav") * float(os.environ.get("CLG", "0.6"))}
    for a, b in MUTE:                                                # tira o trecho do palavrão com rampa curta
        i0, i1 = int(a * SR), int(b * SR); srcw["cl"][i0:i1] = 0
    vt = np.zeros((n, 2), np.float32); f = int(0.03 * SR)
    for s in segs:
        if s["src"] == "-": continue
        c = srcw[s["src"]][int(s["a"] * SR):int(s["b"] * SR)].copy(); c[:f] *= np.linspace(0, 1, f)[:, None]; c[-f:] *= np.linspace(1, 0, f)[:, None]
        o = int(s["t0"] * SR); vt[o:o + len(c)] += c[:n - o]
    R.writew(f"{V}/voice.wav", vt)
    if os.environ.get("TRILHA", "funk13") == "funk13":                # a música que ele mandou, com bip nos palavrões
        tr = R.readw(f"{V}/tr/t48.wav").copy(); tt_ = np.arange(len(tr)) / SR
        for a_, b_ in BIPS:
            i0, i1 = int(a_ * SR), min(len(tr), int(b_ * SR)); k_ = np.arange(i1 - i0) / SR
            env_ = np.minimum(1, np.minimum(k_, (i1 - i0) / SR - k_) / 0.01)
            tr[i0:i1] = (0.32 * np.sin(2 * np.pi * 1000 * k_) * env_)[:, None]
        reps = int(np.ceil(n / len(tr))) + 1; bed = np.concatenate([tr] * reps)[:n]
    else: bed = R.readw(f"{V}/bed.wav")
    L = min(len(bed), n); tl = np.arange(L) / SR
    gain = float(os.environ.get("TRG", "0.22")) * np.clip(tl / 0.8, 0, 1) * np.where((tl > segs[1]["t0"]) & (tl < segs[4]["t0"]), 1.8, 1.0) * np.where((tl > segs[2]["t0"]) & (tl < segs[4]["t0"]), 1.6, 1.0) * np.clip(1 - (tl - (TOTAL - 1.6)) / 1.5, 0, 1)
    sg = np.zeros((n, 2), np.float32); sg[:L] = bed[:L] * gain[:, None]; R.writew(f"{V}/song.wav", sg)
    ev = [(segs[2]["t0"], sfx.paper(), 0.5), (segs[3]["t0"], sfx.paper(), 0.5), (0.0, sfx.whoosh(0.4), 0.2), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)] + [(sg_["t0"] - 0.12, sfx.whoosh(0.45), 0.22) for sg_ in segs[1:]]
    ev += [(a, sfx.whoosh(0.35), 0.24) for a, *_ in BIG] + [(a + 0.26, sfx.click(), 0.75) for a, *_ in BIG] + [(a + 0.26, sfx.thud(0.3), 0.18) for a, *_ in BIG]
    ev += [(a, sfx.click(), 0.35) for a, *_ in PILLS] + [(a, sfx.siga(), 0.16) for a, b in CTA]
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=70,acompressor=threshold=0.08:ratio=2.5:attack=8:release=200:makeup=1.6,asplit=2[vox][k2];[2:a]volume=0.8[sf];[3:a]volume=0.95[sg];"
                    "[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][sgd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
