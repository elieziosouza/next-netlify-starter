import numpy as np, json, wave
SR = 48000
AUD, TAIL = 537.03, 2.0
N = int((AUD + TAIL) * SR)
t = np.arange(N) / SR
rng = np.random.default_rng(7)

def lowpass(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    from scipy.signal import lfilter
    return lfilter([1 - a], [1, -a], x)

# --- pad: Am F C G, 8 s cada, notas suaves com harmônicos
def hz(m): return 440 * 2 ** ((m - 69) / 12)
chords = [[45, 57, 60, 64], [41, 53, 57, 60], [48, 55, 60, 64], [43, 55, 59, 62]]
pad = np.zeros(N)
L = 8.0
for k in range(int(np.ceil(N / SR / L))):
    st, en = int(k * L * SR), min(N, int((k + 1) * L * SR + 2 * SR))
    if st >= N: break
    tt = np.arange(en - st) / SR
    env = np.minimum(1, tt / 2.5) * np.minimum(1, np.maximum(0, (L + 2 - tt) / 2.5))
    for m in chords[k % 4]:
        f = hz(m)
        for h, amp in [(1, 1), (2, 0.35), (3, 0.15)]:
            pad[st:en] += amp * env * np.sin(2 * np.pi * f * h * tt + rng.uniform(0, 6)) * (1 + 0.003 * np.sin(2 * np.pi * 0.2 * tt))
pad = lowpass(pad, 900)
# pulso grave a cada 2 s (tensão)
pulse = np.zeros(N)
for s0 in np.arange(0, N / SR, 2.0):
    i = int(s0 * SR); n = int(0.5 * SR)
    if i + n > N: break
    tt = np.arange(n) / SR
    pulse[i:i + n] += np.sin(2 * np.pi * 55 * tt) * np.exp(-tt * 9)
music = pad / np.abs(pad).max() * 0.6 + pulse * 0.35
music *= np.minimum(1, t / 3) * np.minimum(1, (AUD + TAIL - t) / 4)

# --- efeitos
sfx = np.zeros(N)
def whoosh(at, dur=0.55, g=0.25):
    i = int(at * SR); n = int(dur * SR)
    if i + n > N or i < 0: return
    tt = np.arange(n) / SR
    noise = rng.standard_normal(n)
    fc = 300 + 5000 * np.sin(np.pi * tt / dur) ** 2
    out = np.zeros(n); y = 0
    for j in range(n):
        a = np.exp(-2 * np.pi * fc[j] / SR); y = (1 - a) * noise[j] + a * y; out[j] = y
    sfx[i:i + n] += g * out / (np.abs(out).max() + 1e-9) * np.sin(np.pi * tt / dur)
def hit(at, g=0.55):
    i = int(at * SR); n = int(0.9 * SR)
    if i + n > N: return
    tt = np.arange(n) / SR
    body = np.sin(2 * np.pi * (90 * np.exp(-tt * 6) + 40) * tt) * np.exp(-tt * 5)
    click = rng.standard_normal(n) * np.exp(-tt * 60) * 0.5
    sfx[i:i + n] += g * (body + click)

T = [x['t'] for x in json.load(open('audio/tempos.json'))]
starts = [0.0] + [max(0, x - 0.25) for x in T[1:]]
ends = starts[1:] + [AUD + TAIL]
for s0 in starts[1:]:
    whoosh(s0 - 0.15)
names = [x['anchor'] for x in json.load(open('audio/tempos.json'))]
def at(anchor, rel=None, frac=None):
    k = names.index(anchor); d = ends[k] - starts[k]
    return starts[k] + (rel if rel is not None else d * frac)
for s0 in [at("On Friday, November 13th", 4.6), at("Bloomberg reported", frac=0.4),
           at("So far, officials say no", frac=0.8), at("Friday was not an ordinary day", frac=0.55),
           at("Here's the honest answer", 0.6)]:
    hit(s0)

# --- narração + ducking simples
w = wave.open('audio/narracao.wav'); nar = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, w.getnchannels()).mean(1) / 32768
nar = np.pad(nar, (0, max(0, N - len(nar))))[:N]
envn = lowpass(np.abs(nar), 3)
duck = 1 - 0.55 * np.clip(envn / 0.05, 0, 1)
mix = nar * 1.0 + music * 0.11 * duck + sfx * 0.5
mix = mix / max(1.0, np.abs(mix).max() / 0.95)
out = (np.repeat(mix[:, None], 2, 1) * 32767).astype(np.int16)
ww = wave.open('audio/mix.wav', 'w'); ww.setnchannels(2); ww.setsampwidth(2); ww.setframerate(SR); ww.writeframes(out.tobytes()); ww.close()
print('ok', len(mix) / SR)
