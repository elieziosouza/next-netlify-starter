# Trilha própria para stories de festa (sem direitos autorais): 120 BPM, tom maior, clima alegre.
# Uso: python3 trilha_festa.py saida.wav [duração_s] [estilo]
#   estilo: festa (padrão, batida 4x4) | romantico (sem bateria pesada, para entrada dos noivos, valsa, cerimônia)
import numpy as np, wave, sys
SR = 48000
OUT = sys.argv[1]; DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 64; ESTILO = sys.argv[3] if len(sys.argv) > 3 else 'festa'
BPM = 120 if ESTILO == 'festa' else 84
beat = 60 / BPM; bar = 4 * beat
N = int(DUR * SR); out = np.zeros((N, 2))
rng = np.random.default_rng(3)

def midi(m): return 440 * 2 ** ((m - 69) / 12)
# C - G - Am - F  (I - V - vi - IV)
prog = [(48, [60, 64, 67]), (43, [59, 62, 67]), (45, [60, 64, 69]), (41, [60, 65, 69])]

def add(i0, sig, pan=0.0, g=1.0):
    if i0 >= N: return
    i1 = min(N, i0 + len(sig)); s = sig[:i1 - i0] * g
    out[i0:i1, 0] += s * (1 - pan); out[i0:i1, 1] += s * (1 + pan)

def tone(f, n, harm=6, roll=1.6):
    t = np.arange(n) / SR
    return sum(np.sin(2 * np.pi * f * h * t + h) / h ** roll for h in range(1, harm + 1))

def noise_hp(n, k=1):
    x = rng.normal(0, 1, n)
    for _ in range(k): x = np.diff(x, prepend=0)
    return x / (np.abs(x).max() + 1e-9)

nb = int(DUR / bar) + 1
for b in range(nb):
    root, chord = prog[b % 4]; i0 = int(b * bar * SR); n = int((bar + 0.5) * SR); tt = np.arange(n) / SR
    env = np.clip(tt / 0.4, 0, 1) * np.clip((bar + 0.5 - tt) / 0.5, 0, 1)
    for m in chord:
        for det, pan in [(-0.08, -0.6), (0.08, 0.6)]:
            add(i0, tone(midi(m) * 2 ** (det / 12), n) * env, pan, 0.028)
    # baixo
    step = beat / 2 if ESTILO == 'festa' else beat
    for e in range(int(bar / step)):
        m = int(step * SR); tb = np.arange(m) / SR
        s = np.sin(2 * np.pi * midi(root - 12) * tb) * np.exp(-tb * 4)
        add(i0 + int(e * step * SR), s, 0, 0.20 if (e % 2 == 0 or ESTILO != 'festa') else 0.13)
    # arpejo brilhante (piano/pluck)
    if b >= 1:
        notes = chord + [chord[0] + 12, chord[1] + 12]
        pat = [0, 1, 2, 3, 4, 3, 2, 1] if ESTILO == 'festa' else [0, 2, 4, 2]
        st = bar / len(pat)
        for k, idx in enumerate(pat):
            m = int(0.5 * SR); tp = np.arange(m) / SR
            f = midi(notes[idx] + 12)
            s = (np.sin(2 * np.pi * f * tp) + 0.4 * np.sin(4 * np.pi * f * tp) + 0.15 * np.sin(6 * np.pi * f * tp)) * np.exp(-tp * 9)
            add(i0 + int(k * st * SR), s, 0.3 * (1 if k % 2 else -1), 0.045)
    # bateria
    if ESTILO == 'festa' and b >= 2:
        for q in range(4):
            j0 = i0 + int(q * beat * SR)
            m = int(0.3 * SR); tk = np.arange(m) / SR
            f = 48 + 110 * np.exp(-tk * 35)
            add(j0, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tk * 10), 0, 0.42)
            if q in (1, 3):
                m = int(0.25 * SR); tc = np.arange(m) / SR
                clap = noise_hp(m) * (np.exp(-tc * 25) + 0.5 * np.exp(-np.maximum(tc - 0.012, 0) * 30) * (tc > 0.012))
                add(j0, clap, 0, 0.16)
        for h in range(8):
            m = int(0.06 * SR); th = np.arange(m) / SR
            add(i0 + int((h + 0.5) * beat / 2 * SR) if h % 2 else i0 + int(h * beat / 2 * SR),
                noise_hp(m, 2) * np.exp(-th * 70), 0.25, 0.07 if h % 2 else 0.035)
    elif ESTILO != 'festa' and b >= 2:
        for q in (0, 2):
            m = int(0.4 * SR); tk = np.arange(m) / SR
            f = 45 + 60 * np.exp(-tk * 25)
            add(i0 + int(q * beat * SR), np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tk * 7), 0, 0.18)

# entrada suave e normalização
fade = np.clip(np.arange(N) / (0.3 * SR), 0, 1); out *= fade[:, None]
out = np.tanh(out * 1.3); out /= np.abs(out).max() + 1e-9; out *= 0.89
with wave.open(OUT, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32767).astype('<i2').tobytes())
print(OUT, f'{BPM} BPM', f'{DUR:.0f}s')
