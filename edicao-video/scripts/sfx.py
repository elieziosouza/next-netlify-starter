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

def click(seed=11):
    """clique de mouse: estalo curto de apertar + estalo menor de soltar"""
    rng = np.random.default_rng(seed); n = int(0.11 * SR); out = np.zeros(n)
    for t0, g, f0 in ((0.0, 1.0, 3200), (0.065, 0.55, 2600)):
        i = int(t0 * SR); m = int(0.012 * SR); tt = np.arange(m) / SR
        burst = rng.normal(0, 1, m) * np.exp(-tt / 0.0016) + 0.8 * np.sin(2 * np.pi * f0 * tt) * np.exp(-tt / 0.003)
        out[i:i + m] += g * burst
    out = np.diff(np.concatenate([[0], out])) * 0.6 + out * 0.4
    out /= np.abs(out).max() + 1e-9
    return np.stack([out, out], 1)

def build(events, total, path):
    buf = np.zeros((int(total * SR) + SR, 2))
    for t0, snd, g in events:
        i = int(t0 * SR); buf[i:i + len(snd)] += snd * g
    buf = np.tanh(buf * 1.2) / 1.2
    pcm = (np.clip(buf, -1, 1) * 32000).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

def hope(dur=3.6, seed=5):
    """som de esperança: arpejo de sinos subindo sobre um pad suave, com ecos (usado na estrela do 13 e no punho)"""
    n = int(dur * SR); tt = np.arange(n) / SR; dream = np.zeros(n)
    for i, m in enumerate([60, 64, 67, 71, 74, 76, 79, 83]):
        t0 = i * 0.13; f = 440 * 2 ** ((m + 12 - 69) / 12); idx = tt >= t0; tl = tt[idx] - t0
        dream[idx] += (np.sin(2 * np.pi * f * tl) + 0.35 * np.sin(2 * np.pi * f * 2.76 * tl) * np.exp(-tl * 6)) * np.exp(-tl * 2.2) * 0.22
    env = np.clip(tt / 0.9, 0, 1) * np.clip((dur - tt) / 1.2, 0, 1)
    for m in [48, 55, 60, 64, 67, 71]:
        f = 440 * 2 ** ((m - 69) / 12); dream += (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 1.003 * tt + 1)) * env * 0.07
    nz = np.random.default_rng(seed).normal(0, 1, n); nz = nz - np.convolve(nz, np.ones(8) / 8, "same"); dream += nz * env * 0.03
    out = dream.copy()
    for d, g in [(0.21, 0.45), (0.37, 0.3), (0.55, 0.2)]:
        k = int(d * SR); out[k:] += dream[:-k] * g
    out /= np.abs(out).max() + 1e-9
    return np.stack([out, np.roll(out, 240)], 1)

def circulo(dur=0.5, seed=3):
    """destaque suave: toque de madeira curto + pincelada de ar acompanhando o círculo sendo desenhado"""
    r = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR
    tok = (np.sin(2 * np.pi * 520 * t) + 0.4 * np.sin(2 * np.pi * 1310 * t)) * np.exp(-t / 0.025) * (1 - np.exp(-t * 2000))
    x = r.normal(0, 1, n); bp = onepole_lp(x, np.full(n, 2600.0)); bp = bp - onepole_lp(bp, np.full(n, 700.0))
    p = t / 0.45; brush = bp * np.clip(np.sin(np.pi * np.clip(p, 0, 1)), 0, 1) ** 2 * 0.5
    brush /= np.abs(brush).max() + 1e-9
    out = 0.8 * tok + 0.35 * brush; out /= np.abs(out).max() + 1e-9
    pan = np.clip(p, 0, 1)
    return np.stack([out * (1 - 0.3 * pan), out * (0.7 + 0.3 * pan)], 1)

def barra(dur=1.2, seed=7):
    """entrada da barra lateral: sopro curto subindo e um acorde de sino suave (mi, si, mi) que some devagar"""
    r = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR
    x = r.normal(0, 1, n); p = np.clip(t / 0.35, 0, 1)
    air = onepole_lp(x, 400 + 5000 * p ** 2); air = air - onepole_lp(air, np.full(n, 300.0))
    air *= np.sin(np.pi * p) ** 2 * (t < 0.35); air /= np.abs(air).max() + 1e-9
    bell = np.zeros(n); t1 = np.clip(t - 0.22, 0, None); on = (t >= 0.22)
    for f, g in ((659.3, 1.0), (987.8, 0.7), (1318.5, 0.45), (1975.5, 0.18)):
        bell += g * np.sin(2 * np.pi * f * t1) * np.exp(-t1 / (0.55 if f < 1500 else 0.25))
    bell *= on * (1 - np.exp(-t1 * 400)); bell /= np.abs(bell).max() + 1e-9
    out = 0.35 * air + 0.6 * bell; out /= np.abs(out).max() + 1e-9
    d = int(0.012 * SR); right = np.concatenate([np.zeros(d), out[:-d]])         # leve abertura estéreo
    return np.stack([out, right], 1)


def siga(dur=0.9, seed=9):
    """chamada do "siga · compartilhe": duas notas suaves de marimba (sol, ré), ataque macio e grave, sem brilho"""
    n = int(dur * SR); t = np.arange(n) / SR; out = np.zeros(n)
    for t0, f in ((0.0, 392.0), (0.16, 587.3)):
        tt = np.clip(t - t0, 0, None); on = t >= t0
        tone = np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt / 0.08)
        out += on * tone * (1 - np.exp(-tt * 180)) * np.exp(-tt / 0.32)
    out = onepole_lp(out, np.full(n, 2500.0)); out /= np.abs(out).max() + 1e-9
    d = int(0.010 * SR); right = np.concatenate([np.zeros(d), out[:-d]])
    return np.stack([out, right], 1)

def muu(dur=0.75, seed=13):
    """mugido de vaca de desenho (para tapar palavrão com humor): dente-de-serra grave que sobe e cai, com formantes de 'u'"""
    n = int(dur * SR); t = np.arange(n) / SR
    f0 = 118 + 38 * np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.7 + 3 * np.sin(2 * np.pi * 5.5 * t)
    ph = 2 * np.pi * np.cumsum(f0) / SR; saw = 2 * ((ph / (2 * np.pi)) % 1.0) - 1
    rng = np.random.default_rng(seed); saw += 0.04 * rng.normal(0, 1, n)
    out = onepole_lp(saw, np.full(n, 700.0)) + 0.5 * onepole_lp(saw, np.full(n, 280.0))
    env = np.minimum(1, t / 0.06) * np.minimum(1, (dur - t) / 0.18) ** 1.5
    out = out * env; out /= np.abs(out).max() + 1e-9
    return np.stack([out, out], 1)

def riser(dur=1.8, seed=21):
    """Riser do final (referência que o Eliezio gostou): ruído que abre do grave para o agudo + tom subindo, crescendo até cortar seco
    no começo da tela final. Encaixar terminando exatamente no END_IN (ev: (END_IN - dur, riser(), 0.5)) e somar um thud leve no END_IN."""
    n = int(dur * SR); t = np.arange(n) / SR; u = t / dur
    rng = np.random.default_rng(seed); nz = rng.standard_normal(n).astype(np.float32)
    out = np.zeros(n, np.float32); hop = 512; y_prev = 0.0
    fc = 300 * (14000 / 300) ** (u ** 1.6)                                   # filtro abrindo
    for i in range(0, n, hop):
        a = 1 - np.exp(-2 * np.pi * fc[i] / SR); seg = nz[i:i + hop]; o = np.empty_like(seg)
        for j in range(len(seg)): y_prev = y_prev + a * (seg[j] - y_prev); o[j] = y_prev
        out[i:i + hop] = o
    f0 = 180 * (1400 / 180) ** (u ** 1.3); ph = 2 * np.pi * np.cumsum(f0) / SR
    tone = 0.35 * np.sin(ph) + 0.15 * np.sin(2 * ph)
    env = u ** 2.2; env[-int(0.01 * SR):] *= np.linspace(1, 0, int(0.01 * SR))
    x = (out / (np.abs(out).max() + 1e-6) * 0.7 + tone) * env
    return np.stack([x, x], 1).astype(np.float32)
