import numpy as np, wave, sys
SR = 48000; DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 52.5; BPM = 96
beat = 60 / BPM; bar = 4 * beat
N = int(DUR * SR); t = np.arange(N) / SR
rng = np.random.default_rng(7)
out = np.zeros((N, 2))

def midi(m): return 440 * 2 ** ((m - 69) / 12)
# Am - F - C - G  (i - VI - III - VII)
prog = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [55, 60, 64]), (55, [55, 59, 62])]

def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); z = 0.0
    for i in range(len(x)): z = (1 - a) * x[i] + a * z; y[i] = z
    return y

def add(buf, i0, sig, pan=0.0, g=1.0):
    if i0 >= N: return
    i1 = min(N, i0 + len(sig)); sig = sig[:i1 - i0] * g
    buf[i0:i1, 0] += sig * (1 - pan) ; buf[i0:i1, 1] += sig * (1 + pan)

nbars = int(DUR / bar) + 1
for b in range(nbars):
    root, chord = prog[b % 4]
    t0 = b * bar; i0 = int(t0 * SR); n = int(bar * SR) + int(0.4 * SR)
    tt = np.arange(n) / SR
    # pad: detuned soft saw (additive), slow attack
    env = np.clip(tt / 0.6, 0, 1) * np.clip((bar + 0.4 - tt) / 0.5, 0, 1)
    for k, m in enumerate(chord + [chord[0] + 12]):
        f = midi(m)
        for det, pan in [(-0.12, -0.5), (0.12, 0.5)]:
            ff = f * 2 ** (det / 12)
            s = sum(np.sin(2 * np.pi * ff * h * tt + k) / h ** 1.6 for h in range(1, 7))
            add(out, i0, s * env, pan, 0.035)
    # sub bass pulse on 8ths
    for e in range(8):
        j0 = i0 + int(e * beat / 2 * SR); m = int(beat / 2 * SR)
        tb = np.arange(m) / SR
        s = np.sin(2 * np.pi * midi(root - 24) * tb) * np.exp(-tb * 5) * (1 if e % 2 == 0 else 0.6)
        s += 0.3 * np.sin(2 * np.pi * midi(root - 12) * tb) * np.exp(-tb * 9)
        add(out, j0, s, 0, 0.22)
    # pluck arpeggio 16ths (sparse pattern)
    pat = [0, 2, 1, 2, 0, 2, 1, 3, 0, 2, 1, 2, 3, 2, 1, 2]
    if b >= 1:
        for s16, idx in enumerate(pat):
            if (s16 % 4 == 3) and b % 2: continue
            j0 = i0 + int(s16 * beat / 4 * SR); m = int(0.35 * SR)
            tp = np.arange(m) / SR
            note = (chord + [chord[0] + 12])[idx] + 12
            s = (np.sin(2 * np.pi * midi(note) * tp) + 0.3 * np.sin(4 * np.pi * midi(note) * tp)) * np.exp(-tp * 14)
            add(out, j0, s, 0.35 * (1 if s16 % 2 else -1), 0.05)
    # drums from bar 2
    if b >= 2:
        for q in range(4):
            j0 = i0 + int(q * beat * SR)
            if q in (0, 2):
                m = int(0.35 * SR); tk = np.arange(m) / SR
                f = 50 + 90 * np.exp(-tk * 30)
                kick = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tk * 9)
                add(out, j0, kick, 0, 0.35)
            else:
                m = int(0.25 * SR); tc = np.arange(m) / SR
                nz = rng.normal(0, 1, m); nz = nz - lp(nz, 1200)
                add(out, j0, nz * np.exp(-tc * 22), 0, 0.10)
            # off-beat hat
            m = int(0.06 * SR); th = np.arange(m) / SR
            nz = rng.normal(0, 1, m); nz = nz - lp(nz, 7000)
            add(out, j0 + int(beat / 2 * SR), nz * np.exp(-th * 60), 0.2, 0.06)

# master: fade in/out, soft clip, normalize
fade = np.clip(t / 1.5, 0, 1) * np.clip((DUR - t) / 2.5, 0, 1)
out *= fade[:, None]
out = np.tanh(out * 1.5)
out /= np.abs(out).max()
pcm = (out * 0.89 * 32767).astype(np.int16)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
