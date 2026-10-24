# Trilha cinematográfica própria (sem direitos autorais): piano e cordas, sem batida de festa.
# Cresce devagar até um ápice (tímpano + cordas abertas) e termina num acorde maior com cauda longa.
# Uso: python3 trilha_filme.py saida.wav duração_s tempo_do_apice_s
import numpy as np, wave, sys
SR = 48000
OUT = sys.argv[1]; DUR = float(sys.argv[2]); APICE = float(sys.argv[3])
BPM = 72; B = 60 / BPM; N = int((DUR + 3) * SR); out = np.zeros((N, 2)); rng = np.random.default_rng(21)

def midi(m): return 440 * 2 ** ((m - 69) / 12)
# Am - F - C - G, um acorde por compasso; termina em C
prog = [[45, 57, 60, 64], [41, 53, 57, 60], [36, 55, 60, 64], [43, 55, 59, 62]]
def add(t, sig, pan=0.0, g=1.0):
    i0 = int(t * SR)
    if i0 >= N: return
    i1 = min(N, i0 + len(sig)); s = sig[:i1 - i0] * g; out[i0:i1, 0] += s * (1 - pan); out[i0:i1, 1] += s * (1 + pan)

def piano(f, dur=3.0, vel=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for h in range(1, 8): s += np.sin(2 * np.pi * f * h * (1 + 0.0004 * h * h) * t) * np.exp(-t * (1.2 + 0.8 * h)) / h ** 1.1
    return s * (1 - np.exp(-t * 300)) * vel

def cordas(t0, dur, notas, g, ataque=1.2):
    n = int(dur * SR); t = np.arange(n) / SR
    env = np.clip(t / ataque, 0, 1) ** 1.5 * np.clip((dur - t) / 1.0, 0, 1)
    vib = 1 + 0.003 * np.sin(2 * np.pi * 5.2 * t)
    for m in notas:
        for det, pan in [(-0.06, -0.6), (0.0, 0.0), (0.06, 0.6)]:
            f = midi(m) * 2 ** (det / 12)
            s = sum(np.sin(2 * np.pi * f * h * np.cumsum(vib) / SR + h) / h ** 1.8 for h in range(1, 9))
            add(t0, s * env, pan, g)

def reverb(x, dur=3.0, mix=0.4):
    n = int(dur * SR); t = np.arange(n) / SR
    ir = rng.normal(0, 1, (n, 2)) * np.exp(-t / (dur / 5))[:, None]; ir[:int(0.015 * SR)] = 0
    F = 1 << int(np.ceil(np.log2(len(x) + n)))
    y = np.stack([np.fft.irfft(np.fft.rfft(x[:, c], F) * np.fft.rfft(ir[:, c], F), F)[:len(x)] for c in range(2)], 1)
    y /= np.abs(y).max() + 1e-9
    return x * (1 - mix) + y * mix * np.abs(x).max()

bar = 4 * B; nb = int(np.ceil(DUR / bar)) + 1
for b in range(nb):
    t0 = b * bar; ch = prog[b % 4] if t0 < DUR - bar else [36, 55, 60, 64]
    crescendo = min(1.0, 0.35 + 0.65 * t0 / max(APICE, 1))
    if t0 > APICE: crescendo = 1.0 if t0 < DUR - 3 else 0.7
    # piano: arpejo lento em colcheias
    notas = ch[1:] + [ch[1] + 12, ch[2] + 12]
    for k in range(8):
        tk = t0 + k * B / 2
        if tk > DUR + 0.5: break
        add(tk, piano(midi(notas[[0, 1, 2, 3, 4, 3, 2, 1][k]] + 12), 2.5, 0.8), 0.3 * (1 if k % 2 else -1), 0.10)
    add(t0, piano(midi(ch[0]), 4.0, 0.9), 0, 0.16)
    # cordas: entram no 2º compasso e crescem até o ápice
    if b >= 1: cordas(t0, bar + 1.0, [ch[0] + 12] + ch[1:], 0.006 + 0.012 * crescendo, ataque=1.5 if t0 < APICE else 0.6)
    if t0 >= APICE - 0.01: cordas(t0, bar + 1.0, [n + 12 for n in ch[1:]], 0.008, ataque=0.4)   # violinos abertos no ápice
# subida antes do ápice (swell) e tímpano no ápice
n = int(2.5 * SR); t = np.arange(n) / SR; p = t / 2.5
sw = rng.normal(0, 1, n); sw = np.convolve(sw, np.ones(40) / 40, 'same') * p ** 2.5
add(APICE - 2.5, sw / (np.abs(sw).max() + 1e-9), 0, 0.12)
m = int(2.5 * SR); ti = np.arange(m) / SR
timp = np.sin(2 * np.pi * np.cumsum(55 + 25 * np.exp(-ti * 6)) / SR) * np.exp(-ti * 1.6) + 0.3 * rng.normal(0, 1, m) * np.exp(-ti * 25)
add(APICE, timp, 0, 0.45)
out = reverb(out, 3.2, 0.42)
fo = int(2.8 * SR); i_fim = int((DUR + 0.2) * SR); out[i_fim:] *= 0.0
out[i_fim - fo:i_fim] *= np.linspace(1, 0, fo)[:, None] ** 1.2
out = np.tanh(out * 1.2); out /= np.abs(out).max() + 1e-9; out *= 0.9
with wave.open(OUT, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out[:int((DUR + 0.5) * SR)] * 32767).astype('<i2').tobytes())
print(OUT, f'{DUR:.1f}s, ápice em {APICE:.1f}s')
