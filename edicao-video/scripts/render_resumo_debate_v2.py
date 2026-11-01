"""Resumo do debate da Band (18/10/2026), até 2 min (exceção pedida por ele): Eliezio abre em tela cheia ("pra quem não assistiu... vou dividir
a minha tela"), a tela divide (debate em cima, ele embaixo ouvindo) e entram os melhores trechos da compilação; fecha nele em tela cheia
("dia 25 é inevitável" + L) com o vai dar PT. Falas do Flávio identificadas; acusações com selo de afirmação do Lula ou do outro lado.
v2 (pedido dele): no estilo de sempre, debate grande na caixa no meio e ele num card pequeno embaixo, para mostrar mais o Lula e o Flávio."""
import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; ease_out = R.ease_out; ease_in = R.ease_in; ease_io = R.ease_io
V = f"{S}/v41"; ME = f"{V}/me.mp4"; CL = f"{V}/cl.mp4"
SPLIT_AT = 4.4                                                     # no "vou dividir a minha tela aqui" a tela divide
PARTS = [("me", 0.45, 6.95), ("cl", 0.05, 2.37), ("cl", 3.23, 7.77), ("cl", 24.97, 31.07), ("cl", 41.93, 51.83), ("cl", 52.67, 65.3),
         ("cl", 66.17, 77.33), ("cl", 95.3, 117.2), ("me", 9.85, 15.95)]
segs = []; acc = 0.0
for src_, a, b in PARTS: segs.append(dict(src=src_, a=a, b=b, t0=acc, t1=acc + b - a)); acc += b - a
EDIT_CUT = acc
def seg_at(t):
    for s in segs:
        if t < s["t1"]: return s
    return segs[-1]
def out_t(src_, x):
    for s in segs:
        if s["src"] == src_ and s["a"] - 1e-6 <= x <= s["b"] + 1e-6: return s["t0"] + x - s["a"]
    raise ValueError((src_, x))
FULL = MODE == "full" or MODE.startswith(("frames", "cover"))
MEF = R.decode(ME, 0, 16.0, 1080, 1920) if FULL else None
CY0, CY1 = 510, 1040                                               # metade de baixo da compilação: fora a tarja "POV" e o cronômetro
CLF = R.decode(CL, 0, 118.0, 576, CY1 - CY0, f"crop=576:{CY1 - CY0}:0:{CY0}") if FULL else None
def fr_of(arr, x): return arr[int(clamp(x * FPS, 0, len(arr) - 1))]
SEAM = 1060; PH = H - SEAM
BW = 960; BH = int(BW * (CY1 - CY0) / 576); BY = 300               # debate inteiro (sem cortar as laterais) na caixa do meio
PIP_W, PIP_H, PIP_Y = 230, 265, 1580                               # card pequeno dele, acima do rodapé
def pip_img(x):
    face = cv2.LUT(fr_of(MEF, x)[380:1460, 90:990], R.LUT)       # rosto e ombros
    return cv2.resize(face, (PIP_W, PIP_H), interpolation=cv2.INTER_AREA)
FIT = 0.88; _fw, _fh = int(W * FIT), int(H * FIT); _fx = CX - _fw // 2; _fy = H - _fh
_fm = np.ones((_fh, _fw), np.float32); _fm[:, :30] = np.linspace(0, 1, 30)[None, :]; _fm[:, -30:] = np.linspace(1, 0, 30)[None, :]; _fm[:30] *= np.linspace(0, 1, 30)[:, None]; _fm = _fm[..., None]
def me_full(x):
    img = fr_of(MEF, x); bg = cv2.resize(cv2.GaussianBlur(cv2.resize(img, (W // 10, H // 10)), (0, 0), 2.5), (W, H)).astype(np.float32) * 0.7
    fg = cv2.resize(cv2.LUT(img, R.LUT), (_fw, _fh), interpolation=cv2.INTER_AREA).astype(np.float32)
    bg[_fy:, _fx:_fx + _fw] = bg[_fy:, _fx:_fx + _fw] * (1 - _fm) + fg * _fm
    return bg
_pw = int(1200 * 0 + W * PH / 1110)                                # painel dele: rosto inteiro (linhas 330 a 1440), centrado depois da barra
_pm = np.ones((PH, _pw), np.float32); _pm[:, :40] = np.linspace(0, 1, 40)[None, :]; _pm[:, -40:] = np.linspace(1, 0, 40)[None, :]; _pm = _pm[..., None]
def me_panel(x):
    band = cv2.LUT(fr_of(MEF, x)[330:1440], R.LUT)
    bg = cv2.resize(cv2.GaussianBlur(cv2.resize(band, (W // 10, PH // 10)), (0, 0), 2.5), (W, PH)).astype(np.float32) * 0.7
    fg = cv2.resize(band, (_pw, PH), interpolation=cv2.INTER_AREA).astype(np.float32); x0 = CX - _pw // 2
    bg[:, x0:x0 + _pw] = bg[:, x0:x0 + _pw] * (1 - _pm) + fg * _pm
    return bg
def listen_x(t):
    """enquanto o debate roda, ele aparece ouvindo: trecho calado (7,0 a 9,8 s) em vaivém e mais lento"""
    u = (t * 0.7) % 5.6
    return 7.0 + (u if u < 2.8 else 5.6 - u)
def split_frame(t, top_rgb, me_x):
    out = np.zeros((H, W, 3), np.float32)
    top = cv2.resize(top_rgb, (W, SEAM), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    out[:SEAM] = top; out[SEAM:] = me_panel(me_x)
    out[SEAM - 3:SEAM + 3] = np.array(R.GOLD, np.float32)
    return out
def cl_top(x): return fr_of(CLF, x)[:, :, :] if True else None
def top_for(x):
    if 59.1 < x < 60.06: x = 59.1                                 # a metade de baixo da compilação fica preta aqui: segura o último quadro
    fr = fr_of(CLF, x); want = W / SEAM; h0, w0 = fr.shape[:2]          # recorta para a proporção do painel de cima
    cw = int(h0 * want)
    if cw <= w0: x0 = (w0 - cw) // 2; return fr[:, x0:x0 + cw]
    ch = int(w0 / want); y0 = max(0, (h0 - ch) // 3); return fr[y0:y0 + ch]
# legendas: (fonte, texto, início, fim, trilha)  trilha "me" = branca, "au" = palavra quente, "rc" = fala do Flávio
L = [("me", "E PRA QUEM NÃO ASSISTIU", 0.5, 1.6), ("me", "O DEBATE ONTEM,", 1.6, 2.55), ("me", "EU VOU RESUMIR PRA VOCÊ.", 2.6, 4.35),
     ("me", "VOU DIVIDIR A MINHA TELA AQUI", 4.4, 5.5), ("me", "E VOU RESUMIR PRA VOCÊ.", 5.75, 6.95),
     ("cl", "POR QUE ELE CONSEGUE", 0.1, 1.2), ("cl", "SER PIOR DO QUE O PAI.", 1.2, 2.35),
     ("cl", "AS PESSOAS MENTEM PELOS OLHOS.", 3.3, 5.0), ("cl", "EU ESTOU VENDO NO SEU OLHO", 5.1, 6.4), ("cl", "MUITA MENTIRA.", 6.4, 7.7),
     ("cl", "VOCÊ TEM QUE EXPLICAR", 25.0, 26.7), ("cl", "…DO VORCARO,", 26.7, 28.5), ("cl", "QUE VOCÊ DIZ QUE NÃO PEGOU", 28.5, 29.9), ("cl", "E PEGOU.", 29.9, 31.0),
     ("cl", "VOCÊ FOI O ÚNICO", 43.3, 44.4), ("cl", "QUE VOTOU CONTRA", 44.4, 45.6), ("cl", "A MULHER TER DOIS MESES A MAIS", 46.1, 47.6), ("cl", "PRA CUIDAR DA CRIANÇA.", 47.6, 48.9),
     ("cl", "…QUE VOCÊ TEM CONTRA AS MULHERES.", 49.1, 51.8),
     ("fl", "VAI EXPLICAR POR QUE AQUI", 52.7, 54.3), ("fl", "73% DOS PRESIDIÁRIOS VOTARAM EM VOCÊ?", 54.3, 56.1),
     ("cl", "EU QUERO QUE VOTE 100%,", 56.2, 57.6), ("cl", "ATÉ TEU PAI!", 57.8, 59.0), ("cl", "BOLSONARO, VOTE EM MIM.", 59.0, 61.0),
     ("cl", "VOCÊ CONHECE SEU FILHO,", 61.0, 62.9), ("cl", "VOCÊ SABE QUE EU SOU MELHOR DO QUE ELE.", 62.9, 65.2),
     ("cl", "EU SOU PRESIDENTE HÁ 12 ANOS", 66.2, 68.2), ("cl", "E TENHO UM APARTAMENTO", 68.5, 69.8), ("cl", "DE 190 METROS QUADRADOS", 69.8, 71.2), ("cl", "DE 1,5 MILHÃO.", 71.2, 72.5),
     ("cl", "ESSE CIDADÃO, COM O MESMO SALÁRIO QUE EU,", 72.5, 74.6), ("cl", "COMPROU UMA CASA DE 10 MILHÕES.", 75.2, 77.3),
     ("cl", "EU DESAFIO VOCÊ:", 95.3, 96.5), ("cl", "ABRE O TELEFONE,", 96.7, 97.5), ("cl", "O SIGILO TELEFÔNICO,", 97.7, 99.2), ("cl", "A SUA CONTA BANCÁRIA, MEU CARO.", 99.2, 101.0),
     ("cl", "EU ABRO DA MINHA FAMÍLIA INTEIRA", 101.0, 102.3), ("cl", "E VOCÊ ABRE DA SUA FAMÍLIA.", 102.5, 104.2), ("cl", "E VAMOS PEDIR PRA JUSTIÇA:", 104.2, 105.5),
     ("cl", "ENTREGAMOS AO PRESIDENTE DA SUPREMA CORTE,", 105.5, 107.5), ("cl", "ENTREGAMOS AO PRESIDENTE DO TSE", 107.8, 109.5), ("cl", "O SEU DOCUMENTO E O MEU", 110.2, 111.6),
     ("cl", "PRA QUE AVALIE ANTES DAS ELEIÇÕES.", 111.8, 113.6), ("cl", "O POVO SABER QUEM É QUEM", 113.8, 115.2), ("cl", "NA HISTÓRIA DESTE PAÍS.", 115.4, 117.1),
     ("me", "DIA 25", 9.9, 11.15), ("me", "É INEVITÁVEL.", 11.8, 12.85)]
HOT = {"RESUMIR", "DIVIDIR", "PIOR", "PAI.", "MENTIRA.", "MENTEM", "VORCARO,", "PEGOU.", "CONTRA", "MULHERES.", "CRIANÇA.", "73%", "100%,", "PAI!", "MIM.", "FILHO,", "MELHOR",
       "12", "1,5", "190", "10", "MILHÕES.", "DESAFIO", "TELEFÔNICO,", "BANCÁRIA,", "INTEIRA", "FAMÍLIA.", "TSE", "ELEIÇÕES.", "25", "INEVITÁVEL."}
CAPS = []
for src_, txt, a, b in L:
    s0 = "cl" if src_ == "fl" else src_; a2, b2 = out_t(s0, a), out_t(s0, b)
    ws = txt.split(); tot = sum(len(w) + 2 for w in ws); k = 0; ts = []
    for w in ws: ts.append(a2 + (b2 - a2 - 0.1) * k / tot); k += len(w) + 2
    tr = "rc" if src_ == "fl" else ("au" if any(w in HOT for w in ws) else "me")
    CAPS.append(dict(words=ws, ts=ts, start=a2, end=b2, src=tr))
CAPS.sort(key=lambda c: c["start"]); R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
BIG = [("me", 2.6, 4.35, "RESUMO DO DEBATE", R.GOLD_L), ("cl", 1.2, 2.35, "PIOR QUE O PAI", (235, 60, 60)), ("cl", 6.4, 7.7, "MENTIRA", R.WHITE),
       ("cl", 26.7, 28.5, "VORCARO", R.GOLD_L), ("cl", 49.1, 51.8, "CONTRA AS MULHERES", (235, 60, 60)), ("cl", 54.3, 56.1, "73%?", R.WHITE),
       ("cl", 57.8, 59.0, "ATÉ TEU PAI", R.GOLD_L), ("cl", 59.0, 61.0, "VOTE EM MIM", R.WHITE), ("cl", 71.2, 72.5, "R$ 1,5 MILHÃO", R.GOLD_L),
       ("cl", 75.2, 77.3, "10 MILHÕES", (235, 60, 60)), ("cl", 95.3, 96.5, "EU DESAFIO VOCÊ", R.GOLD_L), ("cl", 101.0, 104.2, "FAMÍLIA INTEIRA", R.WHITE),
       ("cl", 107.8, 109.5, "TSE", R.GOLD_L), ("me", 9.9, 11.15, "DIA 25", (235, 60, 60)), ("me", 11.8, 12.85, "INEVITÁVEL", R.GOLD_L)]
BIG = [(out_t(s, a), out_t(s, b), w, c) for s, a, b, w, c in BIG]
PILLS = [("cl", 0.1, 2.3, "LULA", R.RED), ("cl", 28.5, 31.0, "O OUTRO LADO: FLÁVIO NEGA", R.NAVY), ("cl", 43.3, 51.7, "AFIRMAÇÃO DO LULA NO DEBATE", R.NAVY),
         ("cl", 52.7, 56.1, "FLÁVIO", R.NAVY), ("cl", 56.2, 58.6, "LULA", R.RED), ("cl", 75.2, 77.3, "IMPRENSA: MANSÃO DE R$ 6 MI, COM R$ 3,1 MI DO BRB", R.NAVY),
         ("cl", 104.2, 109.5, "PROPOSTA DO LULA: ENTREGAR OS DADOS À JUSTIÇA", R.NAVY)]
PILLS = [(out_t(s, a), out_t(s, b), x, c) for s, a, b, x, c in PILLS]
FIN_IN = out_t("me", 12.85); FIN_LEN = EDIT_CUT - FIN_IN; MUS_IN = FIN_IN - (9.45 - FIN_LEN)
R.MUS_IN = MUS_IN; R.FIN_IN = FIN_IN; EDIT_END = EDIT_CUT; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.END_IN = END_IN; R.EDIT_END = EDIT_END
CARD = ("DEBATE NA BAND · 18/10", ["O RESUMO DE QUEM", "NÃO ASSISTIU"])
CTA = [(out_t("cl", 66.2), out_t("cl", 71.0)), (out_t("cl", 113.8), out_t("cl", 117.1))]
def cta_level(t): return max([clamp((t - a) / 0.4) * clamp((b - t) / 0.4) for a, b in CTA] + [0.0])
SPLIT_T = out_t("me", SPLIT_AT)
def is_split(t): return SPLIT_T <= t < segs[-1]["t0"]
def big_word(frame, t, cy):
    for i, (a, b, word, col) in enumerate(BIG):
        if not (a <= t < b): continue
        u = t - a; k = ease_out(u / 0.28); out = ease_in((t - (b - 0.22)) / 0.22)
        size = 190; f = R.BIGF(size); d0 = ImageDraw.Draw(Image.new("L", (4, 4)))
        while d0.textlength(word, font=f) > 680: size -= 6; f = R.BIGF(size)
        lay = Image.new("RGBA", (W, int(size * 1.3)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.text((W / 2, lay.height / 2), word, font=f, fill=col + (255,), anchor="mm", stroke_width=8, stroke_fill=R.NAVY + (255,))
        dx = (1 if i % 2 == 0 else -1) * W * 0.95 * (1 - k)
        if u < 0.28:
            Lb = int(60 * (1 - k)) + 1
            if Lb > 2: lay = Image.fromarray(cv2.filter2D(np.asarray(lay), -1, np.ones((1, Lb), np.float32) / Lb))
        frame.alpha_composite(R.fade(lay, 1 - out), (int(CX - W / 2 + dx), int(cy - lay.height / 2 - 30 * out)))
def card_k(t):
    k = ease_out((t - 0.6) / 0.4) * (1 - ease_in((t - (FIN_IN - 0.35)) / 0.35))
    for edge in (SPLIT_T, segs[-1]["t0"]):                        # some e reaparece na troca de tela
        k *= min(1.0, abs(t - edge) / 0.3) if abs(t - edge) < 0.3 else 1.0
    return k
FREEZE = 15.6
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); s = seg_at(tt); x = s["a"] + min(tt, s["t1"] - 0.02) - s["t0"]
    if s is segs[-1] and tt >= FIN_IN: x = min(x, FREEZE)
    if is_split(t):
        fr = fr_of(CLF, min(x, 59.1) if 59.1 < x < 60.06 else x) if s["src"] == "cl" else fr_of(CLF, 0.05)
        bg = R.blur_bg(fr, 0.32); frame = Image.fromarray(np.clip(bg, 0, 255).astype(np.uint8)).convert("RGBA")
        k = ease_out((t - SPLIT_T) / 0.35)
        box = Image.fromarray(R.rounded(cv2.resize(fr, (BW, BH), interpolation=cv2.INTER_LANCZOS4), 30, 5))
        if k < 1: box = box.resize((int(BW * (0.9 + 0.1 * k)), int(BH * (0.9 + 0.1 * k))), Image.BICUBIC)
        R.paste(frame, R.fade(box, clamp((t - SPLIT_T) / 0.2)), CX - box.width / 2, BY + (BH - box.height) / 2, 0.6, 22, (8, 20))
        R.credit(frame, "Vídeo: reprodução TV Band", CX + BW / 2 - 14, BY + BH - 30, 1.0)
        mex = x if s["src"] == "me" else listen_x(t)                # card pequeno com ele embaixo
        pip = Image.fromarray(R.rounded(pip_img(mex), 26, 5)); kp = ease_out((t - SPLIT_T - 0.15) / 0.35)
        if kp > 0: R.paste(frame, R.fade(pip, kp), CX - PIP_W / 2, PIP_Y + 40 * (1 - kp), 0.6, 18, (6, 14))
        big_word(frame, t, 200)
        for a, b, txt, colr in PILLS:
            if a <= t < b: R.pill(frame, txt, CX, BY + 50, clamp((t - a) / 0.3) * clamp((b - t) / 0.25), fill=colr, size=32)
        kc = card_k(t)
        if kc > 0: BAR.lower_card(frame, CARD[0], CARD[1], BY + BH + 68, kc, fs=40)
        R.draw_caption(frame, t, BY + BH + 318, 44, ("me", "au", "rc"))
    else:
        frame = Image.fromarray(np.clip(me_full(x), 0, 255).astype(np.uint8)).convert("RGBA")
        big_word(frame, t, 300)
        if tt < FIN_IN:
            R.draw_caption(frame, t, 1500, 48, ("me", "au")); kc = card_k(t)
            if kc > 0: BAR.lower_card(frame, CARD[0], CARD[1], 1655, kc, fs=44)
        else: R.lyrics(frame, t)
    BAR.draw_bar(frame, clamp(t / END_IN), "canal", ease_out((t - 0.2) / 0.6), cta_level(t), 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(frame, t)
    for e in [SPLIT_T, segs[-1]["t0"]] + [sg["t0"] for sg in segs[2:-1]]:
        if abs(t - e) < 0.09: frame = Image.blend(frame, Image.new("RGBA", frame.size, (255, 255, 255, 255)), (1 - abs(t - e) / 0.09) * 0.4)
    if t >= END_IN: frame.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return frame.convert("RGB")

def main():
    if MODE in ("lib", "cover"): return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(t).resize((360, 640), Image.LANCZOS) for t in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    if MODE == "info": print("TOTAL", round(TOTAL, 2), "SPLIT", round(SPLIT_T, 2), "FIN", round(FIN_IN, 2), [(p[0], round(s["t0"], 2)) for p, s in zip(PARTS, segs)]); return
    vout = f"{V}/video.mp4"
    if not (os.environ.get("REUSE") and os.path.exists(vout)):     # REUSE=1: só refaz o áudio
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
        for i in range(int(round(TOTAL * FPS))): enc.stdin.write(frame_at(i / FPS).tobytes())
        enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    for nm, p in (("me", ME), ("cl", CL)): subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", p, "-ar", "48000", "-ac", "2", f"{V}/{nm}48.wav"], check=True)
    srcw = {"me": R.readw(f"{V}/me48.wav") * 0.55, "cl": R.readw(f"{V}/cl48.wav") * 0.6}   # voz dele 3 a 4 dB acima do debate (a compilação já vem alta)
    vt = np.zeros((n, 2), np.float32); f = int(0.03 * SR)
    for s in segs:
        c = srcw[s["src"]][int(s["a"] * SR):int(s["b"] * SR)].copy(); c[:f] *= np.linspace(0, 1, f)[:, None]; c[-f:] *= np.linspace(1, 0, f)[:, None]
        o = int(s["t0"] * SR); vt[o:o + len(c)] += c[:n - o]
    R.writew(f"{V}/voice.wav", vt)
    song = R.readw(f"{S}/v15/song_vox.wav"); Ls = min(len(song), n - int(MUS_IN * SR)); tl = np.arange(Ls) / SR; lead = FIN_IN - MUS_IN
    gain = np.where(tl < lead, 10 ** ((-22 + 22 * tl / lead) / 20), 1.0) * np.clip(1 - (tl - (TOTAL - MUS_IN - 1.6)) / 1.5, 0, 1)
    sg = np.zeros((n, 2), np.float32); sg[int(MUS_IN * SR):int(MUS_IN * SR) + Ls] = song[:Ls] * gain[:, None]; R.writew(f"{V}/song.wav", sg)
    ev = [(0.18, sfx.barra(), 0.2), (SPLIT_T - 0.12, sfx.whoosh(0.5), 0.25), (segs[-1]["t0"] - 0.12, sfx.whoosh(0.5), 0.22), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
    ev += [(sg_["t0"] - 0.1, sfx.whoosh(0.3), 0.14) for sg_ in segs[2:-1]]
    ev += [(a, sfx.whoosh(0.3), 0.12) for a, *_ in BIG] + [(a + 0.26, sfx.click(), 0.6) for a, *_ in BIG]
    ev += [(a, sfx.click(), 0.35) for a, *_ in PILLS] + [(a, sfx.barra(), 0.11) for a, b in CTA]
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=70,asplit=2[vox][k2];[2:a]volume=0.8[sf];[3:a]volume=0.95[sg];"
                    "[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][sgd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
