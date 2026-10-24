"""IA no seu bolso · EP. 01 — 3 tarefas chatas que a IA faz por você. Escritório dele (fundo com LED, sem recorte): palavras acima da cabeça,
selo dourado com o número de cada tarefa + ícone, linha de ícones na tarefa 2, pausas cortadas com zoom alternado e zoom lento, convite para seguir.
A vinheta da série entra antes (montagem final)."""
import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("rex", f"{S}/work/render_exercito.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; ease_out = R.ease_out; ease_in = R.ease_in; ease_io = R.ease_io
V = f"{S}/v58"; M.ME = f"{V}/me.mp4"; M._ch.clear(); M._gr.clear(); BLUE = M.BLUE
GAPS = [(4.62, 4.9), (5.76, 6.12), (9.56, 9.8), (11.82, 12.02), (14.3, 14.74), (16.98, 17.26), (18.18, 18.42), (21.44, 21.82), (22.42, 22.8),
        (24.04, 24.26), (25.8, 26.08), (28.26, 28.78), (30.48, 30.78), (32.2, 32.48)]
PAD = 0.09; KEEP = []; a0 = 0.42
for g0, g1 in GAPS: KEEP.append((a0, g0 + PAD)); a0 = g1 - PAD
KEEP.append((a0, 34.5)); OFF = []; acc = 0.0
for a, b in KEEP: OFF.append(acc); acc += b - a
EDIT_END = acc; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = EDIT_END; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
def src_of(t):
    for i, (a, b) in enumerate(KEEP):
        if t < OFF[i] + (b - a) or i == len(KEEP) - 1: return a + t - OFF[i], i
def out_of(x):
    for i, (a, b) in enumerate(KEEP):
        if x <= b or i == len(KEEP) - 1: return OFF[i] + max(0.0, x - a)
ME_CAPS = [("TEM AQUELA TAREFA QUE VOCÊ", 0.5, 1.9), ("PERDE MEIA HORA FAZENDO", 1.9, 3.3), ("E A INTELIGÊNCIA ARTIFICIAL", 3.3, 4.62), ("FAZ PRA VOCÊ EM UM MINUTO.", 4.9, 5.76),
           ("PRIMEIRO: RESUMIR.", 6.12, 7.3), ("COLOCA AQUELE TEXTO ENORME,", 7.3, 8.3), ("AQUELE CONTRATO,", 8.3, 8.9), ("AQUELA CONVERSA LONGA E PEDE:", 8.9, 9.56),
           ("“ME EXPLICA ISSO EM CINCO LINHAS”.", 9.8, 11.82), ("SEGUNDA: ESCREVER", 12.02, 13.1), ("A MENSAGEM DIFÍCIL.", 13.1, 14.3), ("COBRAR UM CLIENTE,", 14.74, 15.9),
           ("RESPONDER UMA RECLAMAÇÃO,", 15.9, 16.98), ("PEDIR UM AUMENTO.", 17.26, 18.18), ("VOCÊ CONTA A SITUAÇÃO", 18.42, 19.6), ("E ELA ESCREVE COM EDUCAÇÃO", 19.6, 20.6),
           ("E FIRMEZA.", 20.6, 21.44), ("TERCEIRA:", 21.82, 22.42), ("ORGANIZAR A SEMANA.", 22.8, 24.04), ("FALA TUDO QUE VOCÊ TEM PRA FAZER", 24.26, 25.8),
           ("E PEDE UM PLANO DIA A DIA.", 26.08, 27.4), ("SIMPLES ASSIM.", 27.4, 28.26), ("QUAL DESSAS VOCÊ VAI TESTAR HOJE?", 28.78, 30.48),
           ("COMENTA AQUI E ME SEGUE,", 30.78, 32.2), ("QUE AMANHÃ TEM MAIS UMA", 32.48, 33.4), ("DO IA NO SEU BOLSO.", 33.4, 34.5)]
HOT = {"MEIA", "HORA", "MINUTO.", "RESUMIR.", "CINCO", "DIFÍCIL.", "CLIENTE,", "RECLAMAÇÃO,", "AUMENTO.", "EDUCAÇÃO", "FIRMEZA.", "SEMANA.", "DIA", "TESTAR",
       "COMENTA", "SEGUE,", "BOLSO."}
CAPS = []
for txt, a, b in ME_CAPS:
    a2, b2 = out_of(a), out_of(b)
    if b2 - a2 < 0.2: continue
    ws = txt.split(); tot = sum(len(w) + 2 for w in ws); k = 0; ts = []
    for w in ws: ts.append(a2 + (b2 - a2 - 0.08) * k / tot); k += len(w) + 2
    CAPS.append(dict(words=ws, ts=ts, start=a2, end=b2, src="au" if any(w in HOT for w in ws) else "me"))
R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
BIG = [(0.5, 3.3, "MEIA HORA", R.WHITE, False), (3.3, 5.76, "1 MINUTO", R.GOLD_L, True), (6.12, 7.3, "RESUMIR", R.GOLD_L, True),
       (12.02, 14.3, "MENSAGEM DIFÍCIL", R.GOLD_L, True), (22.8, 24.04, "ORGANIZAR", R.GOLD_L, True), (27.4, 28.26, "SIMPLES ASSIM", R.WHITE, True),
       (30.78, 34.5, "COMENTA E SEGUE", R.WHITE, False)]
BADGES = [(6.12, 11.82, "1", "📄"), (12.02, 21.44, "2", "✉️"), (21.82, 28.26, "3", "📅")]
ROW = [(14.74, "💸", 300, "COBRAR"), (15.9, "😤", 590, "RECLAMAÇÃO"), (17.26, "📈", 880, "AUMENTO")]
ICONS = [(0.6, 3.3, "⏳", 880, 1150, 150), (3.4, 5.76, "⚡", 880, 1150, 150), (7.4, 9.56, "📑", 880, 1150, 140), (9.9, 11.8, "✅", 880, 1150, 140),
         (24.3, 27.4, "🗓️", 880, 1150, 140), (28.9, 30.48, "🤔", 880, 1150, 150), (30.9, 32.2, "💬", 880, 1150, 150), (32.5, 34.5, "🔔", 880, 1150, 150)]
def zoom_level(x, ki, t):
    base = 1.0 if ki % 2 == 0 else 1.07; u = t - OFF[ki]
    z = base + 0.05 * (1 - ease_out(u / 0.18)) * (ki > 0) + 0.03 * (0.5 - 0.5 * math.cos(2 * math.pi * t / 7.0))
    for a, b, w_, c_, shk in BIG:
        if shk and 0 <= x - a < 0.4: z += 0.04 * (1 - (x - a) / 0.4)
    return z
def badge(frame, num, emo, u, dur):
    k = R.back_out(clamp(u / 0.35), 2.2); out = ease_in((u - (dur - 0.2)) / 0.2); sc = max(0.05, k * (1 - 0.4 * out))
    r = 105; lay = Image.new("RGBA", (2 * r + 20, 2 * r + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.ellipse((10, 10, 2 * r + 10, 2 * r + 10), fill=R.GOLD + (255,), outline=(255, 255, 255, 255), width=6)
    d.text((r + 10, r + 14), num, font=R.BIGF(150), fill=R.NAVY + (255,), anchor="mm")
    lay = lay.resize((max(1, int(lay.width * sc)), max(1, int(lay.height * sc))), Image.BICUBIC)
    R.paste(frame, R.fade(lay, 1 - out), 215 - lay.width / 2, 760 - lay.height / 2, 0.6, 14, (5, 12))
    if u > 0.2: M.pop(frame, M.emoji(emo, 120), 215, 935, u - 0.2, dur - 0.2, wob=False)
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); x, ki = src_of(tt)
    img, idx = M.graded(x); img = M.zoom(img, zoom_level(x, ki, tt), 540, 760)
    frame = Image.fromarray(img).convert("RGBA")
    for j, (a, b, word, col, shk) in enumerate(BIG):
        if a <= x < b: lay, dx, y = M.big_layer(word, col, x - a, b - a, shk, j); frame.alpha_composite(lay, (dx, y))
    g = np.zeros((520, W, 4), np.uint8); g[..., :3] = (4, 14, 28); g[..., 3] = np.linspace(0, 200, 520)[:, None].astype(np.uint8); frame.alpha_composite(Image.fromarray(g), (0, H - 520))
    for a, b, num, emo in BADGES:
        if a <= x < b: badge(frame, num, emo, x - a, b - a)
    row_on = 14.6 <= x < 18.4
    for t0, emo, cx, lab in ROW:
        if row_on and x >= t0:
            u = x - t0; M.pop(frame, M.emoji(emo, 120), cx, 1330, u, 18.4 - t0)
            if u > 0.15: R.pill(frame, lab, cx, 1420, clamp((u - 0.15) / 0.25) * (1 - ease_in((x - 18.2) / 0.2)), fill=R.NAVY, size=22)
    for a, b, ch, cx, cy, sz in ICONS:
        if a <= x < b and not (6.12 <= x < 28.26 and cx < 400): M.pop(frame, M.emoji(ch, sz), cx, cy, x - a, b - a)
    M.caption(frame, tt, 1600 if row_on else 1540, 50)
    cta = clamp((x - 30.7) / 0.4)
    BAR.draw_bar(frame, clamp(t / END_IN), "canal", ease_out((t - 0.2) / 0.6), cta, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(frame, t)
    if t >= END_IN: frame.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return frame.convert("RGB")
def main():
    if MODE == "lib": return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(t).resize((360, 640), Image.LANCZOS) for t in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    if MODE.startswith("src"): print([round(out_of(float(v)), 2) for v in MODE.split(":")[1].split(",")]); return
    if MODE == "info": print("TOTAL", round(TOTAL, 2)); return
    vout = f"{V}/video.mp4"
    if not (os.environ.get("REUSE") and os.path.exists(vout)):
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
        for k in range(int(round(TOTAL * FPS))): enc.stdin.write(frame_at(k / FPS).tobytes())
        enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", M.ME, "-ar", "48000", "-ac", "2", f"{V}/me48.wav"], check=True)
    me = R.readw(f"{V}/me48.wav"); vt = np.zeros((n, 2), np.float32); f = int(0.012 * SR)
    for i, (a, b) in enumerate(KEEP):
        c = me[int(a * SR):int(b * SR)].copy(); c[:f] *= np.linspace(0, 1, f)[:, None]; c[-f:] *= np.linspace(1, 0, f)[:, None]
        o = int(OFF[i] * SR); vt[o:o + len(c)] += c[:n - o]
    R.writew(f"{V}/voice.wav", vt)
    bed = R.readw(f"{S}/v49/bed.wav"); L = min(len(bed), n); tl = np.arange(L) / SR
    gain = (0.05 * np.clip(tl / 1.0, 0, 1) + 0.06 * np.clip((tl - (EDIT_END - 0.3)) / 0.5, 0, 1)) * np.clip(1 - (tl - (TOTAL - 1.6)) / 1.5, 0, 1)
    sg = np.zeros((n, 2), np.float32); sg[:L] = bed[:L] * gain[:, None]; R.writew(f"{V}/song.wav", sg)
    ev = [(END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
    for a, b, *_r in BIG: ta = out_of(a); ev += [(ta, sfx.whoosh(0.35), 0.22), (ta + 0.26, sfx.click(), 0.6)]
    for a, b, *_r in BADGES: ev += [(out_of(a), sfx.thud(0.35), 0.35), (out_of(a) + 0.05, sfx.click(), 0.7)]
    for t0, *_r in ROW: ev += [(out_of(t0), sfx.click(), 0.45)]
    for a, *_r in ICONS: ev += [(out_of(a), sfx.click(), 0.35)]
    ev += [(out_of(30.8), sfx.siga(), 0.18)]
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=80,acompressor=threshold=0.08:ratio=2.5:attack=8:release=200:makeup=1.6,asplit=2[vox][k2];[2:a]volume=0.8[sf];[3:a]volume=0.95[sg];"
                    "[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][sgd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
