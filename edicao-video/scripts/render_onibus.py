"""Salvador: ônibus parados na garagem no 2º turno; segundo CNN e Metrópoles, o presidente do TRE-BA determinou a prisão em flagrante do
secretário de Mobilidade (Pablo Souza) e mandou a frota inteira para a rua (multa de R$ 1 milhão por hora). Outro lado: prefeitura diz que
foi problema pontual. Padrão: legenda karaokê + caixa fixa (o assunto muda por bloco); tela dividida com a foto/manchete nos trechos de fato;
contador do R$ 1 milhão; palavras grandes acima da cabeça no fechamento; zoom leve. Usa os ajudantes do render_exercito."""
import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("rex", f"{S}/work/render_exercito.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; eo = R.ease_out; ei = R.ease_in
V = f"{S}/v67"; M.ME = f"{V}/me.mp4"; M._ch.clear(); M._gr.clear(); BLUE = M.BLUE
PARTS = [(0.35, 3.95, "full"), (4.15, 8.60, "ponto"), (8.70, 16.10, "r7"), (16.50, 19.10, "g1"), (19.75, 23.40, "g1"), (23.70, 29.10, "full"),
         (29.25, 32.35, "full"), (32.90, 38.35, "full"), (38.80, 41.95, "full"), (42.00, 45.50, "full")]
segs = []; acc = 0.0
for a, b, m in PARTS: segs.append(dict(src="me", a=a, b=b, mode=m, t0=acc, t1=acc + b - a)); acc += b - a
EDIT_END = acc; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = EDIT_END; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
def seg_at(t):
    for i, s in enumerate(segs):
        if t < s["t1"]: return i
    return len(segs) - 1
def om(x):
    for s in segs:
        if s["a"] <= x <= s["b"]: return s["t0"] + x - s["a"]
    return None
ME_CAPS = [("EM PLENO SEGUNDO TURNO EM SALVADOR,", 0.47, 2.20), ("ÔNIBUS FICARAM PARADOS NA GARAGEM.", 2.20, 3.81),
           ("E TINHA ELEITOR NO PONTO ESPERANDO,", 4.28, 6.31), ("SEM CONSEGUIR CHEGAR PRA VOTAR.", 6.84, 8.49),
           ("SEGUNDO A CNN E O METRÓPOLES,", 8.82, 10.60), ("O PRESIDENTE DO TRE DA BAHIA", 10.60, 12.60), ("DETERMINOU A PRISÃO EM FLAGRANTE", 12.60, 14.40),
           ("DO SECRETÁRIO DE MOBILIDADE, PABLO SOUZA.", 14.40, 15.97), ("E MANDOU COLOCAR A FROTA INTEIRA NA RUA,", 16.66, 18.98),
           ("COM MULTA DE 1 MILHÃO DE REAIS", 19.86, 21.80), ("POR HORA SE NÃO CUMPRIR.", 21.80, 23.27),
           ("A PREFEITURA DIZ QUE FOI UM PROBLEMA PONTUAL", 23.80, 26.25), ("NUMA GARAGEM, QUE JÁ NORMALIZOU.", 26.55, 28.97),
           ("O SECRETÁRIO ESTARIA EM PARIS,", 29.37, 30.90), ("NUMA AGENDA OFICIAL.", 30.90, 32.23),
           ("NA MINHA OPINIÃO, TRANSPORTE", 33.02, 34.70), ("NO DIA DA ELEIÇÃO NÃO É FAVOR,", 34.70, 36.40), ("É GARANTIA DO DIREITO DE VOTAR.", 36.40, 38.21),
           ("AGORA É A JUSTIÇA QUE VAI DIZER", 38.90, 40.50), ("QUEM É RESPONSÁVEL.", 40.50, 41.80),
           ("E VOCÊ, CONSEGUIU VOTAR TRANQUILO?", 42.14, 44.36), ("COMENTA AQUI!", 44.60, 45.40)]
HOT = {"SALVADOR,", "GARAGEM.", "VOTAR.", "PRISÃO", "FLAGRANTE", "PABLO", "SOUZA.", "FROTA", "1", "MILHÃO", "PONTUAL", "PARIS,", "FAVOR,", "JUSTIÇA", "RESPONSÁVEL.", "COMENTA"}
CAPS = []
for txt, a, b in ME_CAPS:
    for s in segs:
        a1, b1 = max(a, s["a"]), min(b, s["b"])
        if b1 - a1 < 0.2: continue
        a2, b2 = s["t0"] + a1 - s["a"], s["t0"] + b1 - s["a"]; ws = txt.split(); tot = sum(len(w) + 2 for w in ws); k = 0; ts = []
        for w in ws: ts.append(a2 + (b2 - a2 - 0.08) * k / tot); k += len(w) + 2
        CAPS.append(dict(words=ws, ts=ts, start=a2, end=b2, src="au" if any(w in HOT for w in ws) else "me"))
CAPS.sort(key=lambda c: c["start"]); R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
# caixa fixa: o assunto acompanha o bloco (tempo da fonte)
CARDS = [(0.0, 8.6, "SALVADOR · 2º TURNO", ["ÔNIBUS PARADOS", "NA GARAGEM"]), (8.6, 23.5, "TRE-BA", ["PRISÃO DO SECRETÁRIO", "E FROTA NA RUA"]),
         (23.5, 32.4, "O OUTRO LADO", ["PREFEITURA: PROBLEMA", "PONTUAL, JÁ NORMALIZADO"]), (32.4, 99, "NA MINHA OPINIÃO", ["TRANSPORTE NA ELEIÇÃO", "NÃO É FAVOR"])]
BIG = [(35.30, 36.40, "NÃO É FAVOR", R.GOLD_L, True), (38.90, 41.95, "JUSTIÇA", R.WHITE, False)]
def load(p): return np.asarray(Image.open(p).convert("RGB"))
IMG = {"ponto": load(f"{V}/ponto.webp"), "r7": load(f"{V}/r7.jpg")[95:505], "g1": load(f"{V}/g1.jpg")[0:560]}
CREDIT = {"ponto": "Foto: redes sociais", "r7": "Imagem: Record Bahia / R7", "g1": "Fonte: g1"}
LABEL = {"ponto": ("ELEITORES ESPERANDO NO PONTO", BLUE), "r7": ("SEGUNDO CNN E METRÓPOLES", R.NAVY), "g1": ("TRE: FROTA INTEIRA NA RUA", BLUE)}
FACTS = {"r7": [(12.6, "PRESIDENTE DO TRE-BA DETERMINOU A PRISÃO EM FLAGRANTE"), (14.4, "SECRETÁRIO DE MOBILIDADE: PABLO SOUZA")]}
_card = {}
def card(k, w):
    if (k, w) not in _card:
        im = IMG[k]; h = int(w * im.shape[0] / im.shape[1]); _card[(k, w)] = Image.fromarray(R.rounded(cv2.resize(im, (w, h), interpolation=cv2.INTER_AREA), 22, 4))
    return _card[(k, w)]
NAVY_BG = M.NAVY_BG; SEAM = 860
def money(frame, u, y):
    v = int(round(1_000_000 * eo(clamp(u / 1.6)))); s = "R$ " + f"{v:,}".replace(",", ".")
    d = ImageDraw.Draw(frame); f = R.BIGF(130); d.text((CX + 5, y + 7), s, font=f, fill=(0, 0, 0, 120), anchor="mm")
    d.text((CX, y), s, font=f, fill=R.GOLD_L + (255,), anchor="mm", stroke_width=4, stroke_fill=R.NAVY + (255,))
    R.pill(frame, "POR HORA, SE NÃO CUMPRIR", CX, y + 105, clamp((u - 0.8) / 0.3), fill=BLUE, size=30)
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); i = seg_at(tt); s = segs[i]; u = tt - s["t0"]; x = s["a"] + u
    z = (1.0 if i % 2 == 0 else 1.04) + 0.03 * (0.5 - 0.5 * math.cos(2 * math.pi * tt / 7.0))
    for a, b, w_, c_, shk in BIG:
        if shk and 0 <= x - a < 0.4: z += 0.04 * (1 - (x - a) / 0.4)
    img, idx = M.graded(x)
    if s["mode"] == "full":
        img = M.zoom(img, z, 540, 820); frame = Image.fromarray(img).convert("RGBA")
        for j, (a, b, word, col, shk) in enumerate(BIG):
            if a <= x < b: lay, dx, y = M.big_layer(word, col, x - a, b - a, shk, j); frame.alpha_composite(lay, (dx, y))
        g = np.zeros((520, W, 4), np.uint8); g[..., :3] = (4, 14, 28); g[..., 3] = np.linspace(0, 200, 520)[:, None].astype(np.uint8); frame.alpha_composite(Image.fromarray(g), (0, H - 520))
        M.caption(frame, tt, 1500, 50)
        kc = 1.0
    else:
        top = M.zoom(img, z, 540, 820)[330:1430]; tw = int(1080 * SEAM / 1100); fg = cv2.resize(top, (tw, SEAM), interpolation=cv2.INTER_AREA)
        bg = cv2.resize(cv2.GaussianBlur(cv2.resize(top, (108, 90)), (0, 0), 3), (W, SEAM)).astype(np.float32) * 0.55
        x0 = CX - tw // 2; fm = np.ones((SEAM, tw), np.float32); fm[:, :50] = np.linspace(0, 1, 50)[None]; fm[:, -50:] = np.linspace(1, 0, 50)[None]; fm = fm[..., None]
        xs, xe = max(0, x0), min(W, x0 + tw); bg[:, xs:xe] = bg[:, xs:xe] * (1 - fm[:, xs - x0:xe - x0]) + fg[:, xs - x0:xe - x0] * fm[:, xs - x0:xe - x0]
        base = NAVY_BG.copy(); base[:SEAM] = bg.astype(np.uint8)
        frame = Image.fromarray(base).convert("RGBA"); ImageDraw.Draw(frame).rectangle((0, SEAM - 2, W, SEAM + 3), fill=R.GD)
        k = s["mode"]; first = i == 0 or segs[i - 1]["mode"] != k; kin = eo(u / 0.4) if first else 1.0
        lab, lc = LABEL[k]; R.pill(frame, lab, CX, SEAM + 50, kin, fill=lc, size=28)
        if k == "g1" and s["a"] > 19:                                 # contador do R$ 1 milhão
            ci = card(k, 420); R.paste(frame, ci, CX - 230 - ci.width / 2 + 60, SEAM + 100, 0.6, 22, (10, 26))
            money(frame, x - 19.86, SEAM + 760)
        else:
            w = 920 if k == "ponto" else (640 if k == "r7" else 560); ci = card(k, w)
            R.paste(frame, R.fade(ci, kin), CX - ci.width / 2, SEAM + 100 + 200 * (1 - kin), 0.6, 22, (10, 26))
            y2 = SEAM + 120 + ci.height
            for j, (t0, txt) in enumerate(FACTS.get(k, [])):
                if x >= t0:
                    sz = 28
                    while R.MF("ExtraBold", sz).getlength(txt) + 50 > 900: sz -= 1
                    R.pill(frame, txt, CX, y2 + 40 + j * 80, clamp((x - t0) / 0.25), fill=BLUE if j == 0 else R.NAVY, size=sz)
        R.credit(frame, CREDIT[k], CX, H - 120, kin, anchor="mm")
        M.caption(frame, tt, SEAM - 80, 46)
        kc = 0.0                                                     # caixa fixa some na tela dividida
    for a, b, kick, lines in CARDS:
        if a <= x < b and kc > 0:
            k2 = clamp((tt - 0.5) / 0.4) * (1 - clamp((tt - (EDIT_END - 0.3)) / 0.3)); BAR.lower_card(frame, kick, lines, 1700, k2, fs=38)
    cta = clamp((t - segs[-1]["t0"]) / 0.4) if t > segs[-1]["t0"] else 0.0
    BAR.draw_bar(frame, clamp(t / END_IN), "canal", eo((t - 0.2) / 0.6), cta, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(frame, t)
    for j in range(1, len(segs)):
        if segs[j]["mode"] != segs[j - 1]["mode"] and abs(t - segs[j]["t0"]) < 0.07:
            frame = Image.blend(frame, Image.new("RGBA", frame.size, (255, 255, 255, 255)), (1 - abs(t - segs[j]["t0"]) / 0.07) * 0.3)
    if t >= END_IN: frame.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return frame.convert("RGB")
def capa(out):
    img, _ = M.graded(30.5); TOPH = 760
    base = NAVY_BG.copy(); fh = H - TOPH; src_ = img[290:1600]; fw = int(W * fh / src_.shape[0])
    bgf = cv2.resize(cv2.GaussianBlur(cv2.resize(src_, (108, 131)), (0, 0), 3), (W, fh)); base[TOPH:] = bgf
    fc = cv2.resize(src_, (fw, fh), interpolation=cv2.INTER_AREA); xo = (W - fw) // 2; base[TOPH:, xo:xo + fw] = fc
    ph = IMG["ponto"]; sc = TOPH / ph.shape[0]; pw = int(ph.shape[1] * sc); pr = cv2.resize(ph, (pw, TOPH), interpolation=cv2.INTER_AREA)
    x0 = (pw - W) // 2 - 60; base[:TOPH] = pr[:, x0:x0 + W]
    fr = Image.fromarray(base).convert("RGBA")
    g = np.zeros((TOPH, W, 4), np.uint8); g[..., :3] = (4, 14, 28); g[..., 3] = np.concatenate([np.linspace(150, 40, 260), np.linspace(40, 225, TOPH - 260)]).astype(np.uint8)[:, None]
    fr.alpha_composite(Image.fromarray(g), (0, 0))
    d = ImageDraw.Draw(fr); d.rectangle((0, TOPH - 3, W, TOPH + 3), fill=R.GD)
    for txt, y, sz, col in (("ÔNIBUS NA GARAGEM", 520, 120, (255, 255, 255)), ("NO DIA DA ELEIÇÃO", 645, 104, R.GOLD_L)):
        f = R.BIGF(sz)
        while f.getlength(txt) > 880: sz -= 4; f = R.BIGF(sz)
        d.text((CX, y), txt, font=f, fill=col + (255,), anchor="mm", stroke_width=6, stroke_fill=R.NAVY + (255,))
    R.pill(fr, "TRE-BA DETERMINOU A PRISÃO DO SECRETÁRIO", CX, TOPH + 4, 1.0, fill=(150, 20, 30), size=34)
    BAR.draw_bar(fr, 0.0, "canal"); fr.alpha_composite(R.top, (R.HDX, 0)); fr.convert("RGB").save(out, quality=95)
def main():
    if MODE == "lib": return
    if MODE == "capa": capa(OUTFILE); return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(x_).resize((360, 640), Image.LANCZOS) for x_ in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    if MODE == "info": print("TOTAL", round(TOTAL, 2), [(s["mode"], round(s["t0"], 2)) for s in segs]); return
    vout = f"{V}/video.mp4"
    if not (os.environ.get("REUSE") and os.path.exists(vout)):
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
        for k in range(int(round(TOTAL * FPS))): enc.stdin.write(frame_at(k / FPS).tobytes())
        enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", M.ME, "-ar", "48000", "-ac", "2", f"{V}/me48.wav"], check=True)
    me = R.readw(f"{V}/me48.wav"); vt = np.zeros((n, 2), np.float32); f = int(0.012 * SR)
    for s in segs:
        c = me[int(s["a"] * SR):int(s["b"] * SR)].copy(); c[:f] *= np.linspace(0, 1, f)[:, None]; c[-f:] *= np.linspace(1, 0, f)[:, None]
        o = int(s["t0"] * SR); vt[o:o + len(c)] += c[:n - o]
    R.writew(f"{V}/voice.wav", vt)
    bed = R.readw(f"{S}/v52/tense.wav"); L = min(len(bed), n); tl = np.arange(L) / SR
    gain = (0.16 * np.clip(tl / 1.0, 0, 1) + 0.08 * np.clip((tl - (EDIT_END - 0.3)) / 0.5, 0, 1)) * np.clip(1 - (tl - (TOTAL - 1.6)) / 1.5, 0, 1)
    sg = np.zeros((n, 2), np.float32); sg[:L] = bed[:L] * gain[:, None]; R.writew(f"{V}/song.wav", sg)
    ev = [(0.0, sfx.whoosh(0.4), 0.2), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
    for j in range(1, len(segs)):
        if segs[j]["mode"] != segs[j - 1]["mode"]: ev += [(segs[j]["t0"] - 0.1, sfx.whoosh(0.45), 0.24)]
    for t0 in (12.6, 14.4): ev += [(om(t0), sfx.click(), 0.45)]
    ta = om(19.86); ev += [(ta + k * 0.12, sfx.click(), 0.25) for k in range(12)] + [(ta + 1.6, sfx.thud(0.4), 0.5)]
    for a, b, *_r in BIG:
        t_ = om(a)
        if t_ is not None: ev += [(t_, sfx.whoosh(0.35), 0.22), (t_ + 0.26, sfx.click(), 0.6), (t_ + 0.26, sfx.thud(0.3), 0.2)]
    sfx.build([e for e in ev if e[0] is not None and 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=80,acompressor=threshold=0.08:ratio=2.5:attack=8:release=200:makeup=1.6,asplit=2[vox][k2];[2:a]volume=0.8[sf];[3:a]volume=0.95[sg];"
                    "[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][sgd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
