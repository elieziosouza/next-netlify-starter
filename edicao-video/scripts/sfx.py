import numpy as np, wave, sys
SR = 48000
rng = np.random.default_rng(1)

def onepole_lp(x, fc):
    y = np.zeros_like(x); z = 0.0
    a = np.exp(-2 * np.pi * fc / SR)
    for i in range(len(x)):
        z = (1 - a[i]) * x[i] + a[i] * z; y[i] = z
    return y

def whoosh(dur=0.5, up=True):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.normal(0, 1, n)
    p = t / dur
    fc = 300 + 5000 * (np.sin(np.pi * p) ** 2)
    lp = onepole_lp(x, fc)
    hp = lp - onepole_lp(lp, np.full(n, 180.0))
    env = np.sin(np.pi * np.clip(p if up else p, 0, 1)) ** 1.6
    env *= (p ** 0.6) if up else 1
    pan = np.clip(p, 0, 1)
    out = hp * env
    out /= np.abs(out).max() + 1e-9
    return np.stack([out * (1 - 0.5 * pan), out * (0.5 + 0.5 * pan)], 1)

def paper(dur=0.35):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.normal(0, 1, n)
    hp = x - onepole_lp(x, np.full(n, 1800.0))
    crackle = (rng.random(n) < 0.004) * rng.normal(0, 3, n)
    env = np.exp(-t * 9) * (1 - np.exp(-t * 300))
    out = (hp * 0.6 + crackle) * env
    out /= np.abs(out).max() + 1e-9
    return np.stack([out, out], 1)

def thud(dur=0.45):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 95 * np.exp(-t * 6) + 45
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11)
    click = rng.normal(0, 1, n) * np.exp(-t * 120)
    out = body + 0.35 * click
    out /= np.abs(out).max() + 1e-9
    return np.stack([out, out], 1)

def marker(dur=0.7):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.normal(0, 1, n)
    bp = onepole_lp(x, np.full(n, 3500.0)); bp = bp - onepole_lp(bp, np.full(n, 1200.0))
    env = np.clip(t / 0.05, 0, 1) * np.clip((dur - t) / 0.08, 0, 1) * (0.7 + 0.3 * np.sin(2 * np.pi * 7 * t))
    out = bp * env; out /= np.abs(out).max() + 1e-9
    return np.stack([out, out], 1)

def build(events, total, path):
    buf = np.zeros((int(total * SR) + SR, 2))
    for t0, snd, g in events:
        i = int(t0 * SR); buf[i:i + len(snd)] += snd * g
    buf = np.tanh(buf * 1.2) / 1.2
    pcm = (np.clip(buf, -1, 1) * 32000).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
