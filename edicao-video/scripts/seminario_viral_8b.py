"""Edição viral do seminário de inglês do 8º ano B (23/11/2026): 90 s, vertical 1080x1920, a partir do original 4K 60 fps.
Estrutura: A) abertura nervosa (0:01) · B) "vamos cantar" (5:05) · C) contagem "3, 4, vai!" (5:30) · D, E, F) a música, com cortes entre plano aberto e fechados (cantora, percussão, colega) · final com os aplausos.
Uso: python3 montar.py SAIDA.mp4 [t_ini t_fim]   (t em segundos do vídeo final, para testar um trecho)"""
import sys, subprocess, json, math, wave
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ORIG = "/tmp/claude-0/-home-user/6cb4edb9-4741-58aa-b5a5-8666ade60fc3/scratchpad/seminario/orig/seminario.mp4"
FD = "/home/user/next-netlify-starter/edicao-video/assets/fonts"
W, H, FPS = 1080, 1920, 30
SW, SH = 3840, 2160
GOLD = (255, 214, 64); WHITE = (255, 255, 255); INK = (16, 22, 36); RED = (236, 84, 84)

# ---------------------------------------------------------------- planos
# kind: wide4 (4 alunas em pé), wide (cena da música, 3 alunas), sing (cantora), perc (percussão), left (aluna da esquerda)
CROPS = {"wide4": (880, 0, 2500, 2160), "wide": (0, 0, 3300, 2160), "sing": (1344, 386, 972, 1728), "perc": (2314, 432, 972, 1728), "left": (0, 100, 972, 1728)}
SHOTS = []   # (src_ini, dur, kind, zoom_ini, zoom_fim)
def add(src, dur, kind, z0=1.0, z1=1.05): SHOTS.append((src, dur, kind, z0, z1))
# A: abertura (4 alunas em pé, 'I'm nervous...' e palmas)
add(1.0, 8.0, "wide4", 1.0, 1.08)
# B: "vamos cantar" (5:05)
add(305.0, 6.0, "wide", 1.0, 1.06)
# C: contagem "3, 4, vai!" (5:30)
add(330.0, 6.0, "wide", 1.06, 1.0)
# D: 5:36 a 5:58
t = 336.0
for dur, k in [(3.0, "wide"), (3.5, "sing"), (3.0, "perc"), (3.0, "sing"), (2.5, "wide"), (2.0, "left"), (3.0, "sing"), (2.0, "perc")]:
    add(t, dur, k); t += dur
# E: 6:08 a 6:28
t = 368.0
for dur, k in [(3.0, "sing"), (2.0, "wide"), (3.5, "perc"), (3.5, "sing"), (2.0, "left"), (2.0, "wide"), (4.0, "sing")]:
    add(t, dur, k); t += dur
# F: 7:02 a 7:30 (final com aplausos)
t = 422.0
for dur, k in [(2.5, "sing"), (3.0, "perc"), (3.0, "sing"), (3.0, "wide"), (3.5, "sing"), (3.0, "perc"), (2.5, "sing"), (7.5, "wide")]:
    add(t, dur, k); t += dur
TOTAL = sum(s[1] for s in SHOTS)
BLOCKS = [0, 8.0, 14.0, 20.0, 42.0, 62.0]   # início de cada bloco no vídeo final

# ---------------------------------------------------------------- áudio
def audio():
    """junta os trechos do áudio original (48 kHz estéreo), com fusão curta nas emendas dos blocos"""
    w = wave.open("/tmp/claude-0/-home-user/6cb4edb9-4741-58aa-b5a5-8666ade60fc3/scratchpad/seminario/a48.wav")
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, 2) / 32768; sr = 48000
    parts = []; t = 0.0
    for src, dur, *_ in SHOTS: parts.append((t, a[int(src * sr):int((src + dur) * sr)])); t += dur
    out = np.zeros((int(TOTAL * sr), 2), np.float32)
    for t0, seg in parts:
        i0 = int(t0 * sr); out[i0:i0 + len(seg)] = seg[:len(out) - i0]
    # fusão de 40 ms nas emendas entre blocos
    f = int(0.04 * sr)
    for b in BLOCKS[1:]:
        i = int(b * sr); out[i - f:i] *= np.linspace(1, 0.2, f)[:, None]; out[i:i + f] *= np.linspace(0.2, 1, f)[:, None]
    return out

# ---------------------------------------------------------------- textos
def F(name, size): return ImageFont.truetype(f"{FD}/{name}", size)
def texto(txt, font, fill=WHITE, stroke=INK, sw=10, pad=30, maxw=960, bg=None, line=1.12):
    d0 = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    words = txt.split(" "); lines = []; cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if d0.textlength(t, font=font) <= maxw - 2 * pad or not cur: cur = t
        else: lines.append(cur); cur = w
    lines.append(cur)
    lh = int(font.size * line); wmax = int(max(d0.textlength(l, font=font) for l in lines)) + 2 * pad; h = lh * len(lines) + 2 * pad
    im = Image.new("RGBA", (wmax, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if bg: d.rounded_rectangle((0, 0, wmax - 1, h - 1), radius=int(font.size * 0.45), fill=bg)
    for k, l in enumerate(lines):
        x = (wmax - d.textlength(l, font=font)) / 2; d.text((x, pad + k * lh), l, font=font, fill=fill, stroke_width=sw if not bg else 0, stroke_fill=stroke)
    return im
def pill(txt, size=34, bg=(16, 22, 36, 215), fill=WHITE):
    return texto(txt, F("Montserrat-Bold.ttf", size), fill=fill, sw=0, pad=int(size * 0.5), bg=bg, maxw=1000)
ANTON = lambda s: F("Anton-Regular.ttf", s)
# (t0, t1, imagem, y do topo, tipo) — tipo: "pop" entra com um pulinho; "fade" só esmaece
OV = []
def ov(t0, t1, im, y, kind="pop"): OV.append((t0, t1, im, y, kind))
BADGE = pill("SEMINÁRIO DE INGLÊS · 8º ANO B", 30)
ov(0.0, TOTAL, BADGE, 205, "fade")
ov(0.2, 3.4, texto("ELAS NÃO SÓ APRESENTARAM…", ANTON(80), GOLD, maxw=1060, pad=20), 340)
ov(1.6, 4.0, texto("ELAS CANTARAM!", ANTON(150), WHITE, maxw=1000), 430)
ov(4.2, 7.9, pill("Nervosas, mas prontas", 44), 1385)
ov(8.4, 13.8, pill("E aí veio a surpresa…", 46), 1385)
ov(14.3, 19.8, texto("3… 4… VAI!", ANTON(150), GOLD, maxw=1000), 340)
ov(20.2, 24.5, pill("AO VIVO", 38, bg=(236, 84, 84, 235)), 1385)
ov(42.3, 46.0, texto("QUE ENERGIA!", ANTON(120), GOLD, maxw=1000), 340)
ov(62.4, 66.5, pill("Cada vez mais forte", 44), 1385)
ov(82.4, 87.0, texto("E A SALA APLAUDIU", ANTON(112), GOLD, maxw=1000), 340)
ov(86.6, 90.0, texto("PARABÉNS, 8º ANO B!", ANTON(120), WHITE, maxw=1000), 340)

# ---------------------------------------------------------------- composição
def blend(frame, im, x, y, a):
    ia = np.asarray(im); h, w = ia.shape[:2]
    y0, x0 = max(y, 0), max(x, 0); y1, x1 = min(y + h, frame.shape[0]), min(x + w, frame.shape[1])
    if y1 <= y0 or x1 <= x0: return
    sub = ia[y0 - y:y1 - y, x0 - x:x1 - x]; al = (sub[:, :, 3:4].astype(np.float32) / 255) * a
    frame[y0:y1, x0:x1] = frame[y0:y1, x0:x1] * (1 - al) + sub[:, :, :3] * al
def overlays(frame, t):
    for t0, t1, im, y, kind in OV:
        if t < t0 or t > t1: continue
        a = min(1, (t - t0) / 0.25) * min(1, (t1 - t) / 0.3)
        if kind == "pop":
            k = 0.85 + 0.15 * (1 - (1 - min(1, (t - t0) / 0.3)) ** 3)
            im2 = im.resize((int(im.width * k), int(im.height * k)), Image.BILINEAR) if k < 0.999 else im
        else: im2 = im
        blend(frame, im2, (W - im2.width) // 2, int(y + (im.height - im2.height) / 2), a)
def barras(frame, audio_seg, y0=1230, n=28, alt=64):
    """equalizador discreto, ligado ao som do próprio vídeo"""
    x = audio_seg.mean(1) if audio_seg.ndim > 1 else audio_seg
    if len(x) < 512: return
    sp = np.abs(np.fft.rfft(x[:2048] * np.hanning(min(len(x), 2048)))); sp = sp[2:300]
    edges = np.unique(np.geomspace(2, 298, n + 1).astype(int)); m = len(edges) - 1
    v = np.array([sp[edges[i]:edges[i + 1]].mean() if edges[i + 1] > edges[i] else 0 for i in range(m)]); v = np.clip(np.log10(v + 1e-4) + 2.2, 0, 3.2) / 3.2
    bw = 22; gap = 10; tot = m * (bw + gap) - gap; x0 = (W - tot) // 2
    for i in range(m):
        h = int(10 + alt * v[i]); xx = x0 + i * (bw + gap)
        cv2.rectangle(frame, (xx, y0 - h // 2), (xx + bw, y0 + h // 2), (255, 214, 64), -1, cv2.LINE_AA)
def blur_bg(fg):
    h, w = fg.shape[:2]; cw = int(w * h / H * W / W * 0 + (h * W / H))   # largura da fatia com a proporção 9:16
    x0 = (w - cw) // 2; sl = fg[:, x0:x0 + cw]
    sm = cv2.resize(sl, (W // 12, H // 12), interpolation=cv2.INTER_AREA); sm = cv2.GaussianBlur(sm, (0, 0), 3)
    bg = cv2.resize(sm, (W, H), interpolation=cv2.INTER_LINEAR).astype(np.float32)
    gray = bg.mean(2, keepdims=True); bg = (gray + (bg - gray) * 1.35) * 0.62      # mais cor e mais claro
    vig = 1 - 0.35 * (np.linspace(-1, 1, H)[:, None, None] ** 2)
    return bg * vig

def frames_do_plano(src, dur, kind, z0, z1):
    x0, y0, cw, chh = CROPS[kind]
    if kind in ("wide4", "wide"):
        fw, fh = W, int(round(chh * W / cw)); fh -= fh % 2
        vf = f"crop={cw}:{chh}:{x0}:{y0},scale={fw}:{fh}:flags=lanczos,fps={FPS}"
    else:
        fw, fh = W, H; vf = f"crop={cw}:{chh}:{x0}:{y0},scale={W}:{H}:flags=lanczos,fps={FPS}"
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{src:.3f}", "-t", f"{dur:.3f}", "-i", ORIG, "-an", "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=fw * fh * 3 * 4); n = int(round(dur * FPS)); k = 0
    while k < n:
        buf = p.stdout.read(fw * fh * 3)
        if len(buf) < fw * fh * 3: break
        fr = np.frombuffer(buf, np.uint8).reshape(fh, fw, 3); u = k / max(1, n - 1); z = z0 + (z1 - z0) * (u * u * (3 - 2 * u))
        if kind in ("wide4", "wide"):
            if z > 1.001:   # zoom suave no plano aberto
                cw2, ch2 = int(fw / z), int(fh / z); xx, yy = (fw - cw2) // 2, (fh - ch2) // 2
                fr = cv2.resize(fr[yy:yy + ch2, xx:xx + cw2], (fw, fh), interpolation=cv2.INTER_LINEAR)
            canvas = blur_bg(fr); y = (H - fh) // 2 - 40
            canvas[y:y + fh] = fr; yield canvas, "wide"
        else:
            if z > 1.001:
                cw2, ch2 = int(W / z), int(H / z); xx, yy = (W - cw2) // 2, int((H - ch2) * 0.42)
                fr = cv2.resize(fr[yy:yy + ch2, xx:xx + cw2], (W, H), interpolation=cv2.INTER_LINEAR)
            yield fr.astype(np.float32), "close"
        k += 1
    while k < n:   # se faltar quadro no fim, repete o último
        yield canvas if kind in ("wide4", "wide") else fr.astype(np.float32), kind; k += 1
    p.stdout.close(); p.wait()

import os
MODO = os.environ.get("MODO", "sem_id")   # sem_id: textos sem nenhuma identificação do professor · limpo: nenhum texto nem equalizador
if MODO == "limpo": OV.clear()
def main():
    out = sys.argv[1]; t_ini = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0; t_fim = float(sys.argv[3]) if len(sys.argv) > 3 else TOTAL
    au = audio(); sr = 48000
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    t = 0.0; gi = 0
    for src, dur, kind, z0, z1 in SHOTS:
        if t + dur <= t_ini or t >= t_fim: t += dur; continue
        kind_atual = kind
        for i, (fr, mode) in enumerate(frames_do_plano(src, dur, kind, z0, z1)):
            tt = t + i / FPS
            if tt < t_ini or tt >= t_fim: continue
            frame = np.clip(fr, 0, 255).astype(np.float32) if fr.dtype != np.float32 else fr.copy()
            # faixa escura embaixo para a legibilidade em plano fechado
            if mode == "close" and MODO != "limpo":
                g = np.linspace(0, 0.6, 640)[:, None, None]; frame[H - 640:H] *= (1 - g)
            if MODO == "limpo": pass
            elif mode == "close": barras(frame, au[int(tt * sr):int(tt * sr) + 2048], y0=1365)
            elif kind_atual == "wide": barras(frame, au[int(tt * sr):int(tt * sr) + 2048], y0=(H - 707) // 2 - 40 + 707 + 50)
            overlays(frame, tt)
            enc.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())
        t += dur
    enc.stdin.close(); enc.wait()
    sf = int(t_ini * sr); ef = int(min(t_fim, TOTAL) * sr)
    wavp = out.replace(".mp4", "_a.wav"); w = wave.open(wavp, "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((np.clip(au[sf:ef], -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
    print("total", TOTAL, "ok")
if __name__ == "__main__": main()
