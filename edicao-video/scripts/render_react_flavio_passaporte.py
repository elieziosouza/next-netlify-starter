"""React viral (04/11/2026): Flávio disse em 26/10 que "nunca pensou em sair do país" e que entregaria os passaportes; no dia seguinte
viajou para os EUA (Jovem Pan, CNN Brasil, Correio, Jornal de Brasília; em 3/11 marcou presença no Senado de lá, O Tempo).
Ele abre em tela cheia, a montagem das redes (@joaopaulosilva414: vídeo do Flávio, CNN e um homem criticando quem "foi para os
Estados Unidos") roda no cartão com a caixa fixa embaixo, e ele fecha com "Por que será que ele fugiu, hein?". Formato loop:
sem tela final parada, SIGA PARA MAIS por cima da última frase. Logo da CNN e marcas do TikTok desfocadas; crédito da montagem.
O homem de óculos não é identificado e a fala dele não é atribuída a nenhum caso: só "montagem que circula nas redes"."""
import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
sys.path.insert(0, f"{S}/work")
import sfx, zoom_suave
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; ease_out = R.ease_out; ease_in = R.ease_in
V = f"{S}/react_flavio"; ME = f"{V}/eliezio.mp4"; CL = f"{V}/flavio.mp4"
RED = (235, 60, 60)
# (fonte, início, fim) no tempo de cada arquivo
PARTS = [("me", 1.40, 5.65), ("cl", 0.45, 5.75), ("cl", 5.95, 35.45), ("cl", 36.2, 41.6), ("me", 5.90, 7.80)]
segs = []; acc = 0.0
for src_, a, b in PARTS: segs.append(dict(src=src_, a=a, b=b, t0=acc, t1=acc + b - a)); acc += b - a
EDIT_END = acc; TOTAL = EDIT_END                                   # loop: acaba 0,4 s depois do "hein?", sem tela final
R.FIN_IN = EDIT_END + 99; R.END_IN = EDIT_END + 99; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
def seg_at(t):
    for s in segs:
        if t < s["t1"]: return s
    return segs[-1]
def out_t(src_, x):
    for s in segs:
        if s["src"] == src_ and s["a"] <= x <= s["b"]: return s["t0"] + x - s["a"]
    raise ValueError((src_, x))
FULL = MODE == "full" or MODE.startswith(("frames", "cover"))
MEF = R.decode(ME, 0, 9.7, 1080, 1920) if FULL else None
CLF = R.decode(CL, 0, 42.0, 576, 1024) if FULL else None
def fr_of(arr, x): return arr[int(clamp(x * FPS, 0, len(arr) - 1))]
# ele: tela cheia 12% menor e centrado depois da barra, fundo do próprio quadro desfocado (sem mexer na cor dele)
FIT = 0.88; _fw, _fh = int(W * FIT), int(H * FIT); _fx = CX - _fw // 2; _fy = H - _fh
_fm = np.ones((_fh, _fw), np.float32); _fm[:, :30] = np.linspace(0, 1, 30)[None, :]; _fm[:, -30:] = np.linspace(1, 0, 30)[None, :]; _fm[:30] *= np.linspace(0, 1, 30)[:, None]; _fm = _fm[..., None]
ZOOMS = [(3.9, 5.6, 0.05), (6.0, 7.4, 0.07)]                         # "passaportes" e "por que será que ele fugiu, hein?"
def me_frame(x):
    img = zoom_suave.aplica(fr_of(MEF, x), zoom_suave.nivel(x, ZOOMS), 0.30)
    bg = cv2.resize(cv2.GaussianBlur(cv2.resize(img, (W // 10, H // 10)), (0, 0), 2.5), (W, H)).astype(np.float32) * 0.7
    fg = cv2.resize(img, (_fw, _fh), interpolation=cv2.INTER_AREA).astype(np.float32)
    bg[_fy:, _fx:_fx + _fw] = bg[_fy:, _fx:_fx + _fw] * (1 - _fm) + fg * _fm
    return Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
# montagem: desfoca a logo da CNN (6 a 11,6 s) e as marcas do TikTok
def _mask(rects):
    m = np.zeros((1024, 576), np.float32)
    for x0, y0, x1, y1 in rects: m[y0:y1, x0:x1] = 1
    return cv2.GaussianBlur(m, (0, 0), 10)[..., None]
M_CNN = _mask([(380, 15, 576, 125)]); M_TT1 = _mask([(0, 455, 200, 575)]); M_TT2 = _mask([(420, 690, 576, 825)])
M_BAND = _mask([(0, 430, 576, 660)])                                # legenda gravada do Flávio + símbolo do TikTok (vidro fosco)
_TT2 = np.zeros((1024, 576), np.uint8); _TT2[785:895, 385:576] = 255   # símbolo + @ do TikTok embaixo: preenchido com o fundo
def cl_img(x):
    raw = fr_of(CLF, x)
    fr = cv2.inpaint(raw, _TT2, 5, cv2.INPAINT_TELEA).astype(np.float32); bl = cv2.GaussianBlur(fr, (0, 0), 16); m = np.zeros_like(M_CNN)
    if x < 6.63:                                                   # vidro fosco (até o corte para a apresentadora, 6,63 s): desfoque forte + leve escurecimento azul
        gl = cv2.GaussianBlur(fr, (0, 0), 26) * 0.78 + np.array([4, 14, 30], np.float32) * 0.22
        fr = fr * (1 - M_BAND) + gl * M_BAND
    if 6.6 <= x < 14.05: m = np.maximum(m, M_CNN)                   # logo da CNN (apresentadora: 6,63 a 14,0 s)
    return (fr * (1 - m) + bl * m).astype(np.uint8)
BW = 560; BH = int(BW * 1024 / 576); BY = 300
# legendas (tempo de cada arquivo); só as falas claras na gravação
ME_CAPS = [("ENTÃO, O FLÁVIO DISSE", 1.50, 2.60), ("QUE NUNCA IA FUGIR DO PAÍS,", 2.60, 3.90), ("QUE IA ENTREGAR", 3.95, 4.70), ("OS PASSAPORTES.", 4.70, 5.50),
           ("POR QUE SERÁ", 6.02, 6.60), ("QUE ELE FUGIU, HEIN?", 6.60, 7.40)]
CL_CAPS = [("EU NUNCA PENSEI", 0.60, 1.55), ("EM SAIR DO PAÍS.", 1.55, 2.45), ("EU VOU ENTREGAR", 2.65, 3.55), ("OS MEUS PASSAPORTES", 3.55, 4.45),
           ("E VOU ME DEFENDER", 4.50, 5.15), ("NESSA ABERRAÇÃO.", 5.15, 5.70),
           ("ADIVINHA QUAL FOI O ASSUNTO", 6.05, 7.70), ("DESTA TERÇA-FEIRA?", 7.70, 8.90), ("FLÁVIO BOLSONARO", 9.30, 10.20), ("FUGIU DO BRASIL.", 10.20, 11.10),
           ("FOI PARA OS ESTADOS UNIDOS.", 11.60, 13.70), ("EU NÃO CONCORDEI QUE ELE", 14.30, 15.60), ("FOI EMBORA PRA AMÉRICA.", 15.60, 17.00),
           ("O LÍDER FICA,", 17.20, 18.10), ("PAGA O PREÇO,", 18.10, 19.00), ("VAI PRA CADEIA OU NÃO,", 19.05, 20.20), ("TIPO LULA.", 20.20, 21.00),
           ("TUDO ESTAVA INDICANDO", 21.40, 22.40), ("QUE ELE IA PRA CADEIA.", 22.40, 23.40), ("ELE FUGIU.", 23.50, 24.30), ("NÃO É POSTURA DE UM LÍDER.", 24.40, 25.90),
           ("FICA AÍ, CARA.", 32.30, 33.40), ("AGUENTA O PAU.", 33.40, 35.30)]
HOT = {"FUGIR", "PASSAPORTES.", "PASSAPORTES", "FUGIU,", "FUGIU", "FUGIU.", "NUNCA", "PAÍS.", "PAÍS,", "ABERRAÇÃO.", "ESTADOS", "UNIDOS.", "LÍDER", "LÍDER.", "CADEIA", "CADEIA.", "PREÇO,", "HEIN?"}
CAPS = []
for src_, lst in (("me", ME_CAPS), ("cl", CL_CAPS)):
    for txt, a, b in lst:
        a2 = out_t(src_, a); b2 = out_t(src_, b)
        ws = txt.split(); tot = sum(len(w) + 2 for w in ws); k = 0; ts = []
        for w in ws: ts.append(a2 + (b2 - a2 - 0.1) * k / tot); k += len(w) + 2
        CAPS.append(dict(words=ws, ts=ts, start=a2, end=b2, src="au" if any(w in HOT for w in ws) else "me", kind=src_))
CAPS.sort(key=lambda c: c["start"]); R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
BIG = [("me", 4.70, 5.60, "PASSAPORTES", R.GOLD_L), ("cl", 0.60, 2.45, "NUNCA?", R.WHITE), ("cl", 9.30, 11.10, "FUGIU", RED),
       ("cl", 17.20, 19.00, "O LÍDER FICA", R.WHITE), ("me", 6.60, 7.75, "FUGIU?", RED)]
BIG = [(out_t(s, a), out_t(s, b), w, c) for s, a, b, w, c in BIG]
# fatos conferidos (pílulas embaixo da caixa), com a fonte
PILLS = [(out_t("cl", 0.6), out_t("cl", 5.6), "26/10 · VÍDEO NAS REDES DO FLÁVIO"),
         (out_t("cl", 6.1), out_t("cl", 11.4), "27/10 · VIAJOU PARA OS EUA (JOVEM PAN, CNN)"),
         (out_t("cl", 11.8), out_t("cl", 21.0), "SILAS MALAFAIA, SOBRE A VIAGEM DE JAIR AOS EUA EM 2022"),
         (out_t("cl", 21.3), out_t("cl", 28.0), "A FALA VOLTOU A CIRCULAR DEPOIS DA VIAGEM DO FLÁVIO"),
         (out_t("cl", 28.2), out_t("cl", 35.3), "3/11 · NO SENADO À DISTÂNCIA, DOS EUA (O TEMPO)")]
CARD = ("FLÁVIO E OS PASSAPORTES", ["DISSE QUE NÃO SAIRIA", "E FOI PARA OS EUA"])
CTA = [(out_t("cl", 21.3), out_t("cl", 25.9)), (out_t("me", 6.0), out_t("me", 7.8))]
def cta_level(t): return max([clamp((t - a) / 0.4) * clamp((b - t) / 0.4) for a, b in CTA] + [0.0])
def big_word(frame, t, cy):
    for i, (a, b, word, col) in enumerate(BIG):
        if not (a <= t < b): continue
        u = t - a; k = ease_out(u / 0.28); out = ease_in((t - (b - 0.22)) / 0.22)
        size = 200; f = R.BIGF(size); d0 = ImageDraw.Draw(Image.new("L", (4, 4)))
        while d0.textlength(word, font=f) > 680: size -= 6; f = R.BIGF(size)
        lay = Image.new("RGBA", (W, int(size * 1.3)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.text((W / 2 + 3, lay.height / 2 + 4), word, font=f, fill=(0, 0, 0, 110), anchor="mm"); d.text((W / 2, lay.height / 2), word, font=f, fill=col + (255,), anchor="mm")
        dx = (1 if i % 2 == 0 else -1) * W * 0.95 * (1 - k)
        if u < 0.28:
            L = int(60 * (1 - k)) + 1
            if L > 2: lay = Image.fromarray(cv2.filter2D(np.asarray(lay), -1, np.ones((1, L), np.float32) / L))
        frame.alpha_composite(R.fade(lay, 1 - out), (int(CX - W / 2 + dx), int(cy - lay.height / 2 - 30 * out)))
def layered(rgb, w, h):
    """cartão com duas camadas douradas deslocadas por trás (profundidade, padrão do canal)"""
    pad = 46; lay = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for off, al in ((34, 70), (17, 125)):
        d.rounded_rectangle((pad + off, pad + off, pad + off + w, pad + off + h), 32, outline=R.GOLD + (al,), width=4, fill=(10, 28, 52, int(al * 0.9)))
    box = Image.fromarray(R.rounded(cv2.resize(rgb, (w, h), interpolation=cv2.INTER_LANCZOS4), 30, 5)); lay.alpha_composite(box, (pad, pad))
    return lay, pad
def card3d(frame, fr, t, s):
    """cartão 3D: entra deslizando da lateral girando em profundidade (rotação Y) com desfoque de movimento; depois balança de leve"""
    i = [sg for sg in segs if sg["src"] == "cl"].index(s); side = 1 if i % 2 == 0 else -1
    u = clamp((t - s["t0"]) / 0.5); k = ease_out(u)
    lay, pad = layered(fr, BW, BH)
    tilt = 0.10 * (1 - k) + 0.025 * (0.5 + 0.5 * math.sin(t * 0.9))
    arr = R.persp(np.asarray(lay), "left" if side > 0 else "right", tilt)
    img = Image.fromarray(arr); dx = side * 520 * (1 - k); vel = (side * -60 * (1 - k) if u < 1 else 0, 0)
    R.paste(frame, R.fade(img, clamp(u / 0.4)), CX - img.width / 2 + dx, BY - pad, 0.6, 26, (10, 24), vel)
def card(frame, t, s, y):
    """caixa fixa; some e reaparece na troca de tela (nunca desliza por cima do rosto)"""
    k = ease_out((t - max(s["t0"], 0.6)) / 0.4) * (1 - ease_in((t - (s["t1"] - 0.25)) / 0.25) if s is not segs[-1] else 1)
    if k > 0: BAR.lower_card(frame, CARD[0], CARD[1], y, k, fs=42)
def siga(frame, t):
    """loop: SIGA PARA MAIS e a linha das redes entram por cima da última frase (sem tela final parada)"""
    a = segs[-1]["t0"] + 0.35; k = ease_out((t - a) / 0.4)
    if k <= 0: return
    R.pill(frame, "SIGA PARA MAIS", CX, 1650, k, fill=R.GOLD, tcol=(6, 34, 58, 255), size=46)
    frame.alpha_composite(R.fade(R.HROW, k), (int(CX - R.HROW.width / 2), 1718))
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); s = seg_at(tt); x = s["a"] + tt - s["t0"]
    if s["src"] == "me":
        frame = me_frame(x); big_word(frame, t, 300)
        if s is segs[-1]: siga(frame, t)
        R.draw_caption(frame, t, 1500, 48, ("me", "au"))
        if s is not segs[-1]: card(frame, t, s, 1655)         # no fim, o lugar da caixa é do SIGA PARA MAIS (nunca por cima do rosto)
    else:
        fr = cl_img(x); bg = R.blur_bg(fr, 0.32); frame = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
        card3d(frame, fr, t, s)
        R.credit(frame, "Montagem @joaopaulosilva414 · CNN · Apocalipse nos Trópicos", CX + BW / 2 - 14, BY + BH - 34, 1.0)
        big_word(frame, t, 190)
        card(frame, t, s, BY + BH + 62)
        for a, b, txt in PILLS:
            if a <= t < b: R.pill(frame, txt, CX, 1520, clamp((t - a) / 0.3) * clamp((b - t) / 0.25), fill=R.NAVY, size=24 if len(txt) > 44 else 27)
        R.draw_caption(frame, t, 1665, 46, ("me", "au"))
    BAR.draw_bar(frame, clamp(t / TOTAL), "canal", ease_out((t - 0.2) / 0.6), cta_level(t), 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(frame, t)
    for i, sg in enumerate(segs[1:], 1):                           # flash curto em cada troca de fonte
        if sg["src"] != segs[i - 1]["src"] and abs(t - sg["t0"]) < 0.1:
            frame = Image.blend(frame, Image.new("RGBA", frame.size, (255, 255, 255, 255)), (1 - abs(t - sg["t0"]) / 0.1) * 0.45)
    return frame.convert("RGB")

def main():
    if MODE in ("lib", "cover"): return
    if MODE == "info": print("TOTAL", round(TOTAL, 2), [(s["src"], round(s["t0"], 2), round(s["t1"], 2)) for s in segs]); return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(t).resize((360, 640), Image.LANCZOS) for t in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    vout = f"{V}/video.mp4"
    if not (os.environ.get("REUSE") and os.path.exists(vout)):     # REUSE=1: só refaz o áudio
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
        for i in range(int(round(TOTAL * FPS))): enc.stdin.write(frame_at(i / FPS).tobytes())
        enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    for nm, p in (("me", ME), ("cl", CL)): subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-ar", "48000", "-ac", "2", f"{V}/{nm}48.wav"], check=True)
    srcw = {"me": R.readw(f"{V}/me48.wav") * 0.55, "cl": R.readw(f"{V}/cl48.wav") * 1.0}   # voz dele uns 3 dB acima da montagem
    vt = np.zeros((n, 2), np.float32); f = int(0.03 * SR)
    for s in segs:
        c = srcw[s["src"]][int(s["a"] * SR):int(s["b"] * SR)].copy(); c[:f] *= np.linspace(0, 1, f)[:, None]
        fo = int((0.4 if s is segs[-1] else 0.03) * SR); c[-fo:] *= np.linspace(1, 0, fo)[:, None]   # no fim, sai em 0,4 s
        o = int(s["t0"] * SR); vt[o:o + len(c)] += c[:n - o]
    R.writew(f"{V}/voice.wav", vt)
    ev = [(0.18, sfx.barra(), 0.2)]
    ev += [(sg_["t0"] - 0.12, sfx.whoosh(0.4), 0.2) for i, sg_ in enumerate(segs[1:], 1) if sg_["src"] != segs[i - 1]["src"]]
    ev += [(a, sfx.whoosh(0.3), 0.12) for a, *_ in BIG] + [(a + 0.26, sfx.click(), 0.6) for a, *_ in BIG]
    ev += [(a, sfx.click(), 0.35) for a, *_ in PILLS] + [(a, sfx.barra(), 0.11) for a, b in CTA]
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.6], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-filter_complex",
                    "[1:a]highpass=f=70[vox];[2:a]volume=0.8[sf];"
                    f"[vox][sf]amix=inputs=2:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
