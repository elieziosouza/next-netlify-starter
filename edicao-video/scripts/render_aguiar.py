"""Corte de notícia (sem gravação dele): deputado estadual Marcelo Aguiar (PL-SP) foi ao ato do Flávio na Paulista (18/10) e, horas depois,
foi detido após disparo numa balada no Itaim Bibi; o tiro pegou de raspão no pé do Fred Bruno; liberado por imunidade.
Só fatos de imprensa (Metrópoles, SBT, Terra); sem "usa drogas" nem "atirou contra" (não confirmados); o outro lado em cartão próprio.
Linha do tempo animada feita no vidIQ (motion graphics) e encaixada no meio."""
import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
import sfx
BLUE = (14, 62, 120); PAPER = (247, 244, 236); INK = (22, 26, 34)
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; ease_out = R.ease_out; ease_in = R.ease_in
V = f"{S}/v50"; CL = f"{V}/cl.mp4"; MG = f"{V}/mg2.mp4"
# (tipo, duração, dados)
PARTS = [("hook", 5.6, 12.6), ("head", 3.6, "h1"), ("head", 3.6, "h2"), ("mg", 7.0, None), ("head", 3.4, "h3"), ("lado", 4.8, None), ("fim", 3.2, None)]
segs = []; acc = 0.0
for k, d, data in PARTS: segs.append(dict(kind=k, t0=acc, t1=acc + d, data=data)); acc += d
EDIT_END = acc; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = EDIT_END; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
def seg_at(t):
    for s in segs:
        if t < s["t1"]: return s
    return segs[-1]
FULL = MODE == "full" or MODE.startswith("frames")
ARR = R.decode(CL, 12.0, 19.0, 288, 430, "crop=288:430:0:0") if FULL else None          # o deputado sendo levado (metade de cima, sem o texto da página)
_p = subprocess.run(["ffmpeg", "-v", "error", "-ss", "20", "-i", CL, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
FR = np.frombuffer(_p, np.uint8).reshape(1024, 576, 3); FRED = FR[0:280, 288:576].copy()   # Fred Bruno
MGF = R.decode(MG, 0, 7.0, 1080, 1920, "") if FULL else None
def fr_of(arr, x): return arr[int(clamp(x * FPS, 0, len(arr) - 1))]
def wrap(txt, font, maxw):
    lines, cur = [], ""
    for w in txt.split():
        t = (cur + " " + w).strip()
        if font.getlength(t) <= maxw: cur = t
        else: lines.append(cur); cur = w
    return lines + [cur]
HEADS = {"h1": ("METRÓPOLES · 19/10", "Antes de atirar em balada, deputado do PL foi a ato de Flávio na Paulista"),
         "h2": ("METRÓPOLES · 19/10", "Fred Bruno foi atingido “de raspão” por tiro de deputado em balada de SP"),
         "h3": ("METRÓPOLES · 19/10", "Deputado do PL que atirou em balada não foi preso por imunidade")}
_hc = {}
def head_card(key):
    if key in _hc: return _hc[key]
    w = 900; im = Image.new("RGB", (w, 700), PAPER); d = ImageDraw.Draw(im); src, txt = HEADS[key]
    d.rectangle((0, 0, w, 10), fill=BLUE); d.text((44, 52), src, font=R.MF("ExtraBold", 28), fill=BLUE, anchor="lm")
    d.line((44, 84, w - 44, 84), fill=(205, 200, 190), width=2)
    for sz in range(68, 30, -2):
        f = R.SERIF(sz); ls = wrap(txt, f, w - 88)
        if len(ls) * sz * 1.18 <= 340: break
    y = 110
    for l in ls: d.text((44, y), l, font=f, fill=INK); y += sz * 1.18
    _hc[key] = np.asarray(im)[:int(y + 40) // 2 * 2]; return _hc[key]
def lado_card():
    w = 900; im = Image.new("RGB", (w, 760), BLUE); d = ImageDraw.Draw(im)
    d.text((w / 2, 70), "O OUTRO LADO", font=R.BIGF(80), fill=R.GOLD_L, anchor="mm")
    f = R.MF("SemiBold", 40); y = 150
    for par in ["O deputado diz que houve uma discussão e que os fatos serão esclarecidos.",
                "O gabinete nega que ele tenha sido preso e fala em reação a um remédio forte.",
                "A polícia investiga se o disparo foi acidental."]:
        for l in wrap(par, f, w - 100): d.text((50, y), l, font=f, fill=(255, 255, 255)); y += 52
        y += 26
    return np.asarray(im)[:int(y + 20) // 2 * 2]
LADO = lado_card()
CARD = ("ITAIM BIBI, SP", ["DEPUTADO DO PL", "DETIDO APÓS TIRO"])
def big(frame, word, cy, size, col, t_in, t, shake=False):
    u = t - t_in
    if u < 0: return
    f = R.BIGF(size)
    while f.getlength(word) > 700: size -= 4; f = R.BIGF(size)
    k = ease_out(u / 0.28); lay = Image.new("RGBA", (W, int(size * 1.4)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.text((W / 2 + 5, lay.height / 2 + 7), word, font=f, fill=(0, 0, 0, 120), anchor="mm", stroke_width=10, stroke_fill=(0, 0, 0, 120))
    d.text((W / 2, lay.height / 2), word, font=f, fill=col + (255,), anchor="mm", stroke_width=10, stroke_fill=R.NAVY + (255,))
    dx = W * 0.9 * (1 - k); dy = 0
    if shake and 0.28 < u < 1.0:                                    # tremida curta na palavra forte
        a = 9 * (1 - (u - 0.28) / 0.72); dx += a * math.sin(u * 95); dy = a * 0.6 * math.cos(u * 77)
    frame.alpha_composite(lay, (int(CX - W / 2 + dx), int(cy - lay.height / 2 + dy)))
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); s = seg_at(tt); u = tt - s["t0"]
    bgsrc = fr_of(ARR, 0.5 + (tt % 6.5))
    if s["kind"] == "mg":
        frame = Image.fromarray(fr_of(MGF, u)).convert("RGBA")
    else:
        frame = Image.fromarray(np.clip(R.blur_bg(bgsrc, 0.28), 0, 255).astype(np.uint8)).convert("RGBA")
    if s["kind"] == "hook":
        x = s["data"] + u; im = fr_of(ARR, x - 12.0); cw = 600
        card = cv2.resize(cv2.LUT(im, R.LUT), (cw, int(cw * im.shape[0] / im.shape[1])), interpolation=cv2.INTER_CUBIC)
        z = 1.0 + 0.05 * u / 5.6; zc = cv2.resize(card, (int(cw * z), int(card.shape[0] * z)))
        oy, ox = (zc.shape[0] - card.shape[0]) // 2, (zc.shape[1] - cw) // 2; card = zc[oy:oy + card.shape[0], ox:ox + cw]
        R.paste(frame, Image.fromarray(R.rounded(card, 26, 4)), CX - cw / 2, 430, 0.6, 22, (10, 26))
        R.credit(frame, "Imagens: reprodução redes sociais", CX, 1772, 1.0, anchor="mm")
        big(frame, "DEPUTADO DO PL", 200, 130, R.WHITE, 0.15, tt, shake=True); big(frame, "DETIDO", 330, 150, R.GOLD_L, 0.45, tt, shake=True)
        R.pill(frame, "MADRUGADA DE 19/10 · ITAIM BIBI, SP", CX, 430 + card.shape[0] + 40, clamp((u - 0.8) / 0.3), fill=R.NAVY, size=30)
    elif s["kind"] == "head":
        card = head_card(s["data"]); kin = ease_out(u / 0.4); rot = -1.4 if s["data"] != "h2" else 1.3
        ci = Image.fromarray(R.rounded(card, 22, 4)).rotate(rot, resample=Image.BICUBIC, expand=True)
        R.paste(frame, R.fade(ci, kin), CX - ci.width / 2, 380 + 300 * (1 - kin), 0.6, 22, (10, 26))
        py = 380 + ci.height + 30
        if s["data"] == "h2":
            fw = 380; fi = cv2.resize(cv2.LUT(FRED, R.LUT), (fw, int(fw * FRED.shape[0] / FRED.shape[1])), interpolation=cv2.INTER_CUBIC)
            kp = ease_out((u - 0.3) / 0.4); R.paste(frame, R.fade(Image.fromarray(R.rounded(fi, 20, 4)), kp), CX - fw / 2, py + 120 * (1 - kp), 0.6, 22, (10, 26))
            R.pill(frame, "FRED BRUNO REGISTROU QUEIXA", CX, py + fi.shape[0] + 50, clamp((u - 0.8) / 0.3), fill=BLUE, size=30)
        if s["data"] == "h1": big(frame, "HORAS DEPOIS", py + 140, 130, R.GOLD_L, s["t0"] + 0.5, tt)
        if s["data"] == "h3": big(frame, "IMUNIDADE", py + 140, 150, R.WHITE, s["t0"] + 0.5, tt)
        R.credit(frame, "Manchete: Metrópoles" + (" · Imagem: reprodução" if s["data"] == "h2" else ""), CX, 1772, kin, anchor="mm")
    elif s["kind"] == "lado":
        kin = ease_out(u / 0.4); R.paste(frame, R.fade(Image.fromarray(R.rounded(LADO, 22, 4)), kin), CX - LADO.shape[1] / 2, 520 + 200 * (1 - kin), 0.6, 22, (10, 26))
        R.credit(frame, "Fontes: Metrópoles, SBT News, Terra", CX, 1772, kin, anchor="mm")
    elif s["kind"] == "fim":
        big(frame, "DIA 25,", 700, 180, R.WHITE, s["t0"] + 0.1, tt); big(frame, "PENSA NISSO.", 900, 170, R.GOLD_L, s["t0"] + 0.5, tt, shake=True)
    if s["kind"] not in ("mg",):
        kc = clamp((tt - 0.8) / 0.4) * (1 - clamp((tt - (END_IN - 0.35)) / 0.35))
        if s["kind"] in ("hook", "fim") and kc > 0: BAR.lower_card(frame, CARD[0], CARD[1], 1620, kc, fs=40)
    BAR.draw_bar(frame, clamp(t / END_IN), "canal", ease_out((t - 0.2) / 0.6), 0.0, 0.5 + 0.5 * math.sin(t * 5))
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
    if MODE == "info": print("TOTAL", round(TOTAL, 2), [(s["kind"], round(s["t0"], 2)) for s in segs]); return
    vout = f"{V}/video.mp4"
    if not (os.environ.get("REUSE") and os.path.exists(vout)):
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
        for i in range(int(round(TOTAL * FPS))): enc.stdin.write(frame_at(i / FPS).tobytes())
        enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", CL, "-ar", "48000", "-ac", "2", f"{V}/cl48.wav"], check=True)
    cl = R.readw(f"{V}/cl48.wav"); vt = np.zeros((n, 2), np.float32)
    s0 = segs[0]; c = cl[int(s0["data"] * SR):int((s0["data"] + 5.6) * SR)].copy() * 0.9      # o áudio da abordagem no gancho
    c *= np.clip(np.linspace(0, 5.6, len(c)) / 0.1, 0, 1)[:, None] * np.clip((5.6 - np.linspace(0, 5.6, len(c))) / 0.6, 0, 1)[:, None]
    vt[:len(c)] += c; R.writew(f"{V}/voice.wav", vt)
    bed = R.readw(f"{V}/bed.wav"); L = min(len(bed), n); tl = np.arange(L) / SR
    gain = 0.16 * np.where(tl < segs[1]["t0"], 0.45, 1.0) * np.clip(1 - (tl - (TOTAL - 1.6)) / 1.5, 0, 1)
    sg = np.zeros((n, 2), np.float32); sg[:L] = bed[:L] * gain[:, None]; R.writew(f"{V}/song.wav", sg)
    ev = [(0.0, sfx.whoosh(0.4), 0.2), (0.15 + 0.26, sfx.thud(0.4), 0.3), (0.45 + 0.26, sfx.click(), 0.8), (END_IN - 0.3, sfx.whoosh(0.6), 0.25)]
    ev += [(s["t0"] - 0.1, sfx.paper(), 0.5) for s in segs if s["kind"] == "head"] + [(s["t0"] - 0.12, sfx.whoosh(0.45), 0.22) for s in segs[1:]]
    ev += [(segs[-1]["t0"] + 0.5 + 0.26, sfx.thud(0.4), 0.3)]
    sfx.build([e for e in ev if 0 <= e[0] < TOTAL - 0.9], TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    f"[1:a][2:a][3:a]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
