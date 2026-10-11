"""Assinatura de abertura do canal: glitch sonoro + glitch visual nos primeiros quadros.

Uso: python3 glitch_intro.py ENTRADA.mp4 SAIDA.mp4
Aplicar como última etapa, depois de embutir a capa. Não desloca nem corta o áudio.
"""
import sys, subprocess, wave, tempfile, os
import numpy as np

SR = 48000

def glitch_sound(seed=7):
    """~0.3 s: stutter de tons quadrados, ruído bitcrush e sample-hold (sem o zap final, pedido do Eliezio)"""
    rng = np.random.default_rng(seed)
    n = int(0.32 * SR); out = np.zeros(n)
    t = 0
    while t < int(0.30 * SR):                      # stutter blocks
        L = int(rng.uniform(0.012, 0.035) * SR)
        tt = np.arange(L) / SR
        kind = rng.integers(0, 3)
        if kind == 0:
            f = rng.choice([180, 330, 660, 1320, 2600])
            blk = np.sign(np.sin(2 * np.pi * f * tt)) * 0.55
        elif kind == 1:
            blk = rng.normal(0, 0.6, L)
            q = rng.choice([4, 6, 8]); blk = np.round(blk * q) / q     # bitcrush
        else:
            hold = rng.integers(20, 80); v = rng.normal(0, 0.7, L // hold + 1)
            blk = np.repeat(v, hold)[:L]                                # sample & hold
        if rng.random() < 0.25: blk *= 0                                # gaps
        env = np.ones(L); env[:30] = np.linspace(0, 1, 30); env[-30:] = np.linspace(1, 0, 30)
        e = min(n, t + L); out[t:e] += (blk * env)[:e - t]
        t += L
    out = np.tanh(out * 1.4); out /= np.abs(out).max() + 1e-9
    return np.stack([out, np.roll(out, 90)], 1)

def glitch_frame(img, k, rng):
    """k: intensidade 0..1"""
    if k <= 0.01: return img
    h, w = img.shape[:2]; out = img.copy()
    # deslocamento de faixas horizontais
    for _ in range(int(6 + 10 * k)):
        y0 = rng.integers(0, h - 10); hh = int(rng.integers(8, 70) * (0.5 + k))
        dx = int(rng.integers(-60, 60) * k)
        out[y0:y0 + hh] = np.roll(out[y0:y0 + hh], dx, axis=1)
    # separação RGB
    sh = int(14 * k)
    if sh:
        out[..., 0] = np.roll(out[..., 0], sh, axis=1); out[..., 2] = np.roll(out[..., 2], -sh, axis=1)
    # linhas de varredura e ruído leve
    if rng.random() < 0.6 * k:
        out[::3] = (out[::3].astype(np.int16) * 0.75).astype(np.uint8)
    if rng.random() < 0.25 * k:                                         # flash curto
        out = np.clip(out.astype(np.int16) + 60, 0, 255).astype(np.uint8)
    return out

def intensity(t):
    if t < 0.34: return 1.0 - 0.6 * (t / 0.34)          # abertura
    if 0.40 <= t < 0.50: return 0.55                     # passagem capa → vídeo
    return 0.0

def main(src, dst):
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                            "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip().split(",")
    w, h = int(probe[0]), int(probe[1]); num, den = probe[2].split("/"); fps = float(num) / float(den)
    tmp = tempfile.mkdtemp()
    vout = os.path.join(tmp, "v.mp4"); aout = os.path.join(tmp, "g.wav")
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", f"{fps}",
                            "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
    rng = np.random.default_rng(3); fb = w * h * 3; i = 0
    while True:
        raw = dec.stdout.read(fb)
        if len(raw) < fb: break
        t = i / fps; k = intensity(t)
        if k > 0 and t < 0.34 and rng.random() < 0.3: k = 0      # falha intermitente, mais natural
        if k > 0:
            img = np.frombuffer(raw, np.uint8).reshape(h, w, 3)
            raw = glitch_frame(img, k, rng).tobytes()
        enc.stdin.write(raw); i += 1
    enc.stdin.close(); enc.wait()
    g = glitch_sound(); pcm = (np.clip(g, -1, 1) * 32000).astype(np.int16)
    with wave.open(aout, "wb") as wv:
        wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes(pcm.tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", src, "-i", aout, "-filter_complex",
                    "[2:a]volume=0.45,apad[g];[1:a][g]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.89:level=false[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                    "-movflags", "+faststart", dst], check=True)
    print("ok", i)

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
