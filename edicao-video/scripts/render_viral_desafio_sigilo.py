"""Corte viral: Eliezio abre ("as eleições estão pegando fogo"), Lula faz no debate da Band o desafio de abrir os sigilos (vídeo repostado
pela Erika Hilton, imagens da Band), e Eliezio fecha perguntando se o Flávio deve aceitar, chamando para comentar e lembrando do dia 25.
Tela cheia nele, caixa com o debate no meio; legendas, palavras grandes com clique, barra lateral e caixa fixa.
Sem o vai dar PT nem música de campanha: ele quer que o vídeo sirva para os dois lados."""
import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; ease_out = R.ease_out; ease_in = R.ease_in; ease_io = R.ease_io
V = f"{S}/v40"; ME = f"{V}/me.mp4"; EH = f"{V}/eh.mp4"
# (fonte, início, fim) no tempo de cada arquivo
PARTS = [("me", 3.05, 4.95), ("eh", 0.15, 6.0), ("eh", 9.9, 19.15), ("eh", 24.8, 29.35), ("eh", 33.0, 39.0), ("eh", 42.3, 47.65),
         ("me", 4.95, 8.6), ("me", 9.0, 12.2), ("me", 15.6, 20.5)]
segs = []; acc = 0.0
for src_, a, b in PARTS: segs.append(dict(src=src_, a=a, b=b, t0=acc, t1=acc + b - a)); acc += b - a
EDIT_CUT = acc                                                     # fim da fala; depois vem o vai dar PT com ele congelado
def seg_at(t):
    for s in segs:
        if t < s["t1"]: return s
    return segs[-1]
def out_t(src_, x):
    for s in segs:
        if s["src"] == src_ and s["a"] <= x <= s["b"]: return s["t0"] + x - s["a"]
    raise ValueError(x)
FULL = MODE == "full" or MODE.startswith(("frames", "cover"))
MEF = R.decode(ME, 0, 20.6, 1080, 1920) if FULL else None
EY1 = 644                                                          # par: o ffmpeg arredonda alturas ímpares
EHF = R.decode(EH, 0, 47.8, 576, EY1, f"crop=576:{EY1}:0:0") if FULL else None
def fr_of(arr, x): return arr[int(clamp(x * FPS, 0, len(arr) - 1))]
FIT = 0.88; _fw, _fh = int(W * FIT), int(H * FIT); _fx = CX - _fw // 2; _fy = H - _fh   # ele 12% menor e centrado depois da barra
_fm = np.ones((_fh, _fw), np.float32); _fm[:, :30] = np.linspace(0, 1, 30)[None, :]; _fm[:, -30:] = np.linspace(1, 0, 30)[None, :]; _fm[:30] *= np.linspace(0, 1, 30)[:, None]; _fm = _fm[..., None]
def me_frame(x):
    img = fr_of(MEF, x); bg = cv2.resize(cv2.GaussianBlur(cv2.resize(img, (W // 10, H // 10)), (0, 0), 2.5), (W, H)).astype(np.float32) * 0.7
    fg = cv2.resize(cv2.LUT(img, R.LUT), (_fw, _fh), interpolation=cv2.INTER_AREA).astype(np.float32)
    bg[_fy:, _fx:_fx + _fw] = bg[_fy:, _fx:_fx + _fw] * (1 - _fm) + fg * _fm
    return Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
_lm = np.zeros((EY1, 576), np.float32); _lm[0:205, 468:] = 1; _lm = cv2.GaussianBlur(_lm, (0, 0), 14)[..., None]
def eh_img(x):
    """debate sem a legenda queimada, o cronômetro e a janela de Libras (y 650+); logo da emissora no canto desfocada"""
    fr = fr_of(EHF, x).astype(np.float32); bl = cv2.GaussianBlur(fr, (0, 0), 18)
    return (fr * (1 - _lm) + bl * _lm).astype(np.uint8)
BW = 780; BH = int(BW * EY1 / 576); BY = 300
# legendas (tempo de cada arquivo)
ME_CAPS = [("E AS ELEIÇÕES", 3.1, 3.95), ("ESTÃO PEGANDO FOGO!", 3.95, 4.95),
           ("O QUE VOCÊ ACHA DESSE DESAFIO", 4.98, 6.55), ("QUE O LULA FEZ PRO FLÁVIO BOLSONARO?", 6.55, 7.75), ("ELE DEVE ACEITAR OU NÃO?", 7.75, 8.6),
           ("O BRASIL PRECISA SABER", 9.0, 10.3), ("DISSO OU NÃO?", 10.3, 11.0), ("DEIXA AQUI NOS COMENTÁRIOS.", 11.0, 12.2),
           ("E DIA 25,", 15.65, 17.6), ("VOCÊ DECIDE", 17.85, 18.7), ("QUEM VAI SER O NOSSO", 18.7, 19.6), ("PRÓXIMO PRESIDENTE.", 19.6, 20.5)]
EH_CAPS = [("Ô, FLÁVIO, AQUI MUITO", 0.2, 1.3), ("SE FALOU DE CORRUPÇÃO.", 1.3, 2.45), ("EU VOU FAZER UMA", 2.85, 3.7), ("PROPOSTA PRA VOCÊ.", 3.7, 4.6), ("EU DESAFIO VOCÊ:", 4.9, 6.0),
           ("ABRIMOS A NOSSA", 9.95, 11.0), ("CONTA BANCÁRIA,", 11.0, 12.0), ("ABRIMOS O NOSSO", 12.6, 13.6), ("SIGILO TELEFÔNICO,", 13.6, 14.8),
           ("PARA QUE O POVO", 15.5, 16.6), ("BRASILEIRO SAIBA", 16.6, 17.5), ("QUEM É LADRÃO NESSE PAÍS.", 17.75, 19.1),
           ("A SUA CONTA, MEU CARO:", 24.85, 25.9), ("EU ABRO DA MINHA", 25.9, 26.8), ("FAMÍLIA INTEIRA", 26.8, 27.75), ("E VOCÊ ABRE DA SUA FAMÍLIA.", 27.85, 29.35),
           ("ENTREGAMOS AO PRESIDENTE", 33.05, 34.1), ("DO TSE", 34.1, 35.0), ("O SEU DOCUMENTO E O MEU", 35.4, 37.0), ("PRA QUE AVALIE", 37.1, 38.0), ("ANTES DAS ELEIÇÕES.", 38.0, 39.0),
           ("PRA SABER QUEM É CORRUPTO,", 42.35, 43.6), ("QUEM É LADRÃO.", 43.6, 44.5), ("PORQUE SENÃO O POVO", 44.6, 46.1), ("VAI SER ENGANADO OUTRA VEZ.", 46.1, 47.6)]
HOT = {"FOGO!", "DESAFIO", "ACEITAR", "CORRUPÇÃO.", "PROPOSTA", "DESAFIO", "BANCÁRIA,", "SIGILO", "TELEFÔNICO,", "LADRÃO", "INTEIRA", "FAMÍLIA.", "TSE", "ELEIÇÕES.",
       "CORRUPTO,", "LADRÃO.", "ENGANADO", "COMENTÁRIOS.", "25,", "PRESIDENTE.", "NÃO?"}
CAPS = []
for src_, lst in (("me", ME_CAPS), ("eh", EH_CAPS)):
    for txt, a, b in lst:
        a2, b2 = out_t(src_, a), out_t(src_, min(b, [s["b"] for s in segs if s["src"] == src_ and s["a"] <= a <= s["b"]][0]))
        ws = txt.split(); tot = sum(len(w) + 2 for w in ws); k = 0; ts = []
        for w in ws: ts.append(a2 + (b2 - a2 - 0.1) * k / tot); k += len(w) + 2
        CAPS.append(dict(words=ws, ts=ts, start=a2, end=b2, src="au" if any(w in HOT for w in ws) else "me", kind=src_))
CAPS.sort(key=lambda c: c["start"]); R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
BIG = [("me", 3.9, 4.95, "PEGANDO FOGO", (235, 60, 60)), ("eh", 4.9, 6.0, "EU DESAFIO VOCÊ", R.GOLD_L), ("eh", 9.95, 12.0, "CONTA BANCÁRIA", R.WHITE),
       ("eh", 12.6, 14.8, "SIGILO", R.GOLD_L), ("eh", 17.75, 19.1, "LADRÃO?", (235, 60, 60)), ("eh", 25.9, 29.3, "FAMÍLIA INTEIRA", R.WHITE),
       ("eh", 33.05, 35.0, "TSE", R.GOLD_L), ("eh", 46.1, 47.6, "ENGANADO", (235, 60, 60)), ("me", 7.75, 8.6, "ACEITA?", R.GOLD_L),
       ("me", 11.0, 12.2, "COMENTA AÍ", R.WHITE), ("me", 15.65, 17.6, "DIA 25", (235, 60, 60))]
BIG = [(out_t(s, a), out_t(s, b), w, c) for s, a, b, w, c in BIG]
PILLS = [(out_t("eh", 0.3), out_t("eh", 4.6), "DEBATE NA BAND · 18/10", R.NAVY), (out_t("eh", 33.1), out_t("eh", 38.9), "PROPOSTA DO LULA: ENTREGAR OS DADOS À JUSTIÇA", R.NAVY)]
MUS_IN = EDIT_CUT - 4.87; FIN_IN = EDIT_CUT                       # o "vai dar PT" da música cai no fim da fala dele
R.MUS_IN = MUS_IN; R.FIN_IN = FIN_IN; FIN_LEN = 0.9; EDIT_END = FIN_IN + FIN_LEN; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.END_IN = END_IN; R.EDIT_END = EDIT_END
CARD = ("DEBATE NA BAND · 18/10", ["LULA DESAFIA FLÁVIO:", "ABRE O SIGILO"])
CTA = [(out_t("eh", 15.5), out_t("eh", 19.1)), (out_t("me", 9.0), out_t("me", 12.2))]
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
def card(frame, t, s, y):
    """caixa fixa; some e reaparece na troca de tela (nunca desliza por cima do rosto)"""
    k = ease_out((t - max(s["t0"], 0.6)) / 0.4) * (1 - ease_in((t - (s["t1"] - 0.25)) / 0.25) if s is not segs[-1] else 1)
    if s is segs[-1]: k *= 1 - ease_in((t - (FIN_IN - 0.35)) / 0.35)
    if k > 0: BAR.lower_card(frame, CARD[0], CARD[1], y, k, fs=44)
FREEZE_X = 2.3                                                     # pedido dele: no fim, um quadro que o favoreça (boca fechada, olhando para a câmera)
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); s = seg_at(min(tt, EDIT_CUT - 1e-3)); x = s["a"] + min(tt, s["t1"] - 0.02) - s["t0"]
    if s["src"] == "me":
        if tt >= FIN_IN: x = FREEZE_X                              # final congelado num quadro em que ele está de boca fechada
        frame = me_frame(x); big_word(frame, t, 300)
        if tt < FIN_IN: R.draw_caption(frame, t, 1500, 48, ("me", "au")); card(frame, t, s, 1655)
    else:
        fr = eh_img(x); bg = R.blur_bg(fr, 0.32); frame = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
        k = ease_out((t - s["t0"]) / 0.3) if s is segs[1] else 1.0
        box = Image.fromarray(R.rounded(cv2.resize(fr, (BW, BH), interpolation=cv2.INTER_LANCZOS4), 30, 5))
        if k < 1: box = box.resize((int(BW * (0.92 + 0.08 * k)), int(BH * (0.92 + 0.08 * k))), Image.BICUBIC)
        R.paste(frame, R.fade(box, clamp((t - s["t0"]) / 0.15) if s is segs[1] else 1.0), CX - box.width / 2, BY + (BH - box.height) / 2, 0.6, 22, (8, 20))
        R.credit(frame, "Vídeo: reprodução TV Band", CX + BW / 2 - 12, BY + BH - 30, 1.0)
        big_word(frame, t, 190)
        card(frame, t, s, BY + BH + 70)
        for a, b, txt, colr in PILLS:
            if a <= t < b: R.pill(frame, txt, CX, 1500, clamp((t - a) / 0.3) * clamp((b - t) / 0.25), fill=colr, size=30)
        R.draw_caption(frame, t, 1650, 48, ("me", "au"))
    BAR.draw_bar(frame, clamp(t / END_IN), "canal", ease_out((t - 0.2) / 0.6), cta_level(t), 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(frame, t)
    for sg in segs[1:]:                                            # flash curto em cada troca de fonte
        if sg["src"] != segs[segs.index(sg) - 1]["src"] and abs(t - sg["t0"]) < 0.1:
            frame = Image.blend(frame, Image.new("RGBA", frame.size, (255, 255, 255, 255)), (1 - abs(t - sg["t0"]) / 0.1) * 0.45)
    if abs(t - FIN_IN) < 0.1: frame = Image.blend(frame, Image.new("RGBA", frame.size, (255, 255, 255, 255)), (1 - abs(t - FIN_IN) / 0.1) * 0.45)
    if t >= END_IN: frame.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return frame.convert("RGB")

def main():
    if MODE in ("lib", "cover"): return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(t).resize((360, 640), Image.LANCZOS) for t in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    if MODE == "info": print("TOTAL", TOTAL, "CUT", EDIT_CUT, [(p[0], round(s["t0"], 2)) for p, s in zip(PARTS, segs)]); return
    vout = f"{V}/video.mp4"
    if not (os.environ.get("REUSE") and os.path.exists(vout)):     # REUSE=1: só refaz o áudio
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
        for i in range(int(round(TOTAL * FPS))): enc.stdin.write(frame_at(i / FPS).tobytes())
        enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    for nm, p in (("me", ME), ("eh", EH)): subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-ar", "48000", "-ac", "2", f"{V}/{nm}48.wav"], check=True)
    srcw = {"me": R.readw(f"{V}/me48.wav") * 0.37, "eh": R.readw(f"{V}/eh48.wav") * 1.25}   # voz dele no nível do debate
    vt = np.zeros((n, 2), np.float32); f = int(0.03 * SR)
    for s in segs:
        c = srcw[s["src"]][int(s["a"] * SR):int(s["b"] * SR)].copy(); c[:f] *= np.linspace(0, 1, f)[:, None]; c[-f:] *= np.linspace(1, 0, f)[:, None]
        o = int(s["t0"] * SR); vt[o:o + len(c)] += c[:n - o]
    R.writew(f"{V}/voice.wav", vt)
    ev = [(0.18, sfx.barra(), 0.2), (FIN_IN - 0.1, sfx.whoosh(0.5), 0.2), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
    ev += [(sg_["t0"] - 0.12, sfx.whoosh(0.4), 0.2) for i, sg_ in enumerate(segs[1:], 1) if sg_["src"] != segs[i - 1]["src"]]
    ev += [(a, sfx.whoosh(0.3), 0.12) for a, *_ in BIG] + [(a + 0.26, sfx.click(), 0.6) for a, *_ in BIG]
    ev += [(a, sfx.click(), 0.35) for a, *_ in PILLS] + [(a, sfx.barra(), 0.11) for a, b in CTA]
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-filter_complex",
                    "[1:a]highpass=f=70[vox];[2:a]volume=0.8[sf];"
                    f"[vox][sf]amix=inputs=2:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
