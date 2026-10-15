"""Trilha original no clima de funk/batidão (130 BPM) para o final dos vídeos, sem direitos de terceiros."""
import sys, wave
import numpy as np
SR = 48000; BPM = 130; STEP = 60 / BPM / 4; BAR = STEP * 16
rng = np.random.default_rng(7)
def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / d)
def kick(): n = int(0.35 * SR); t = np.arange(n) / SR; f = 45 + 110 * np.exp(-t / 0.03); ph = 2 * np.pi * np.cumsum(f) / SR; return np.tanh(2.2 * np.sin(ph) * env(n, 0.001, 0.16))
def clap():
    n = int(0.25 * SR); x = rng.normal(0, 1, n); e = np.zeros(n)
    for o in (0, 0.011, 0.022): k = int(o * SR); e[k:] += env(n - k, 0.0005, 0.012 if o < 0.02 else 0.09)
    x = x * e; x = np.convolve(x, [1, -0.9], "same"); return 0.7 * x / np.abs(x).max()
def hat(open_=False): n = int((0.12 if open_ else 0.04) * SR); x = rng.normal(0, 1, n); x = np.diff(np.concatenate([[0], x])); return 0.25 * x * env(n, 0.0005, 0.05 if open_ else 0.012)
def tom(f0=180): n = int(0.22 * SR); t = np.arange(n) / SR; f = f0 * (1 + 0.6 * np.exp(-t / 0.02)); return 0.6 * np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.08)
def bass808(freq, dur): n = int(dur * SR); t = np.arange(n) / SR; f = freq * (1 + 0.5 * np.exp(-t / 0.02)); return np.tanh(1.6 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * env(n, 0.003, dur * 0.7)
def stab(freqs, dur=0.16):
    n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for f in freqs:
        for det in (-0.006, 0, 0.006): x += ((2 * ((t * f * (1 + det)) % 1) - 1))
    x /= len(freqs) * 3; x = np.convolve(x, np.ones(6) / 6, "same"); return 0.5 * x * env(n, 0.004, 0.09)
def whistle(dur=0.5):
    n = int(dur * SR); t = np.arange(n) / SR; f = 2900 + 120 * np.sign(np.sin(2 * np.pi * 22 * t))
    return 0.18 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.03)
N = lambda m: 440 * 2 ** ((m - 69) / 12)
def render(bars=10, intro=2):
    L = int((bars * BAR + 1.0) * SR); mix = np.zeros(L)
    def put(x, t, g=1.0):
        i = int(t * SR); j = min(L, i + len(x)); mix[i:j] += g * x[:j - i]
    K, C, T = kick(), clap(), tom()
    hook = [(0, [69, 72, 76]), (3, [69, 72, 76]), (6, [67, 71, 74]), (10, [69, 72, 76]), (12, [72, 76, 79]), (14, [71, 74, 79])]
    bassline = [(0, 33), (3, 33), (6, 31), (10, 33), (12, 36), (14, 35)]
    for b in range(bars):
        t0 = b * BAR; full = b >= intro
        for s, ch in hook: put(stab([N(m) for m in ch]), t0 + s * STEP, 0.55 if full else 0.35)
        for s in range(16): put(hat(s % 4 == 2), t0 + s * STEP, 0.5 if full else 0.3)
        if full:
            for s in (0, 3, 7, 10): put(K, t0 + s * STEP, 0.9)
            for s in (4, 12): put(C, t0 + s * STEP, 0.8)
            for s, f0 in ((2, 200), (6, 160), (9, 220), (14, 180)): put(tom(f0), t0 + s * STEP, 0.5)
            for i, (s, m) in enumerate(bassline):
                nxt = bassline[i + 1][0] if i + 1 < len(bassline) else 16
                put(bass808(N(m), (nxt - s) * STEP), t0 + s * STEP, 0.55)
        if b == intro - 1: put(whistle(0.45), t0 + 12 * STEP, 1.0)
        if b in (intro + 3, intro + 7): put(whistle(0.3), t0 + 13 * STEP, 0.8)
    mix = np.tanh(mix * 1.3) * 0.85
    st = np.stack([mix, np.roll(mix, int(0.0007 * SR))], 1)
    return st
if __name__ == "__main__":
    st = render(int(sys.argv[2]) if len(sys.argv) > 2 else 10)
    with wave.open(sys.argv[1], "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(st, -1, 1) * 30000).astype(np.int16).tobytes())
