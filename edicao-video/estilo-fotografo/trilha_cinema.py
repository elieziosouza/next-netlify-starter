# Trilha própria com arco emocional para o story_cinema.py (sem direitos autorais):
# piano emocionante -> subida (riser, caixa acelerando, meio tempo de silêncio) -> explosão (batida cheia + impacto)
# -> final com piano e cauda de reverb.
# Uso: python3 trilha_cinema.py saida.wav intro_tempos subida_tempos explosao_tempos final_tempos [bpm]
import numpy as np, wave, sys
SR = 48000
OUT = sys.argv[1]; IB, BB, DB, OB = (int(x) for x in sys.argv[2:6]); BPM = float(sys.argv[6]) if len(sys.argv) > 6 else 120
B = 60 / BPM; TOT_B = IB + BB + DB + OB; N = int((TOT_B * B + 3.0) * SR)
out = np.zeros((N, 2)); rng = np.random.default_rng(11)
t_sub, t_drop, t_fim = IB * B, (IB + BB) * B, (IB + BB + DB) * B

def midi(m): return 440 * 2 ** ((m - 69) / 12)
prog = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [55, 60, 64]), (55, [55, 59, 62])]   # Am F C G
def acorde(tb): return prog[int(tb // 4) % 4]

def add(t, sig, pan=0.0, g=1.0):
    i0 = int(t * SR)
    if i0 >= N or i0 < 0: return
    i1 = min(N, i0 + len(sig)); s = sig[:i1 - i0] * g
    out[i0:i1, 0] += s * (1 - pan); out[i0:i1, 1] += s * (1 + pan)

def piano(f, dur=2.5, vel=1.0):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for h in range(1, 8):
        fh = f * h * (1 + 0.0004 * h * h)
        s += np.sin(2 * np.pi * fh * t) * np.exp(-t * (1.6 + 0.9 * h)) / h ** 1.1
    s *= (1 - np.exp(-t * 400)) * vel
    return s

def ruido(n, k=1):
    x = rng.normal(0, 1, n)
    for _ in range(k): x = np.diff(x, prepend=0)
    return x / (np.abs(x).max() + 1e-9)

def reverb(x, dur=2.2, mix=0.35):
    n = int(dur * SR); t = np.arange(n) / SR
    ir = rng.normal(0, 1, (n, 2)) * np.exp(-t / (dur / 5))[:, None]; ir[:int(0.012 * SR)] = 0
    m = len(x) + n; F = 1 << int(np.ceil(np.log2(m)))
    y = np.stack([np.fft.irfft(np.fft.rfft(x[:, c], F) * np.fft.rfft(ir[:, c], F), F)[:len(x)] for c in range(2)], 1)
    y /= np.abs(y).max() + 1e-9
    return x * (1 - mix) + y * mix * np.abs(x).max()

# ---------------- piano (abertura, subida e final) ----------------
pn = np.zeros((N, 2)); buf = out; out = pn
for tb in np.arange(0, IB + BB, 1):
    root, ch = acorde(tb); notas = ch + [ch[0] + 12]
    if tb % 4 == 0: add(tb * B, piano(midi(root - 12), 3.0, 0.8), 0, 0.30)
    add(tb * B, piano(midi(notas[int(tb) % 4] + 12), 2.0, 0.9), 0.25 * (1 if tb % 2 else -1), 0.22)
    if tb % 2 == 1: add((tb + 0.5) * B, piano(midi(notas[(int(tb) + 2) % 4] + 12), 1.6, 0.6), -0.2, 0.15)
# melodia simples por cima na abertura
mel = [76, 74, 72, 74, 76, 79, 77, 76]
for k, m in enumerate(mel[:IB]): add(k * B + 0.02, piano(midi(m), 2.2, 1.0), 0.1, 0.20)
for tb in np.arange(IB + BB + DB, TOT_B + 1, 1):     # final
    root, ch = (48, [55, 60, 64]) if tb >= TOT_B - 2 else acorde(tb)
    if (tb - (IB + BB + DB)) % 2 == 0:
        add(tb * B, piano(midi(root - 12), 4.0, 0.8), 0, 0.30)
        for j, m in enumerate(ch): add(tb * B + j * 0.06, piano(midi(m + 12), 4.0, 0.7), 0.3 * (j - 1), 0.16)
tt_ = np.arange(N) / SR; gpn = np.where(tt_ < t_drop, 0.5, 0.75)[:, None]   # piano mais baixo: a explosão contrasta
out = buf; out += reverb(pn, 2.6, 0.45) * gpn

# ---------------- pad suave ----------------
def pad(t0, dur, notas, g):
    n = int(dur * SR); t = np.arange(n) / SR; env = np.clip(t / 0.8, 0, 1) * np.clip((dur - t) / 0.8, 0, 1)
    for m in notas:
        for det, pan in [(-0.07, -0.5), (0.07, 0.5)]:
            f = midi(m) * 2 ** (det / 12); s = sum(np.sin(2 * np.pi * f * h * t + h) / h ** 2 for h in range(1, 6))
            add(t0, s * env, pan, g)
for tb in range(0, TOT_B, 4):
    root, ch = acorde(tb); g = 0.010 if tb < IB + BB else 0.018
    if tb >= IB + BB + DB: g = 0.012
    pad(tb * B, 4 * B + 0.8, ch, g)

# ---------------- subida: riser, caixa acelerando, meio tempo de silêncio ----------------
dur_sub = BB * B; n = int(dur_sub * SR); tt = np.arange(n) / SR; p = tt / dur_sub
x = ruido(n); lp = np.zeros(n); z = 0
fc = 400 + 9000 * p ** 2; a_ = np.exp(-2 * np.pi * fc / SR)
for i in range(n): z = (1 - a_[i]) * x[i] + a_[i] * z; lp[i] = z
riser = lp / (np.abs(lp).max() + 1e-9) * p ** 1.5
riser += 0.25 * np.sin(2 * np.pi * np.cumsum(180 + 700 * p ** 2) / SR) * p ** 2
corte = int(max(0, dur_sub - 0.5 * B) * SR); riser[corte:] = 0            # silêncio antes da explosão
add(t_sub, riser, 0, 0.30)
k = 0.0
while k < BB - 0.5:
    passo = 0.5 if k < BB * 0.4 else (0.25 if k < BB * 0.75 else 0.125)
    m = int(0.09 * SR); tc = np.arange(m) / SR
    add(t_sub + k * B, ruido(m) * np.exp(-tc * 35), 0, 0.10 + 0.25 * k / BB)
    k += passo

# ---------------- explosão ----------------
m = int(1.6 * SR); ti = np.arange(m) / SR
boom = np.sin(2 * np.pi * np.cumsum(35 + 90 * np.exp(-ti * 9)) / SR) * np.exp(-ti * 2.2)
crash = ruido(m, 2) * np.exp(-ti * 2.5) * 0.5
add(t_drop, boom + crash, 0, 0.55)
for tb in np.arange(IB + BB, IB + BB + DB):
    t = tb * B; root, ch = acorde(tb - (IB + BB))
    mk = int(0.32 * SR); tk = np.arange(mk) / SR
    add(t, np.sin(2 * np.pi * np.cumsum(48 + 120 * np.exp(-tk * 32)) / SR) * np.exp(-tk * 9), 0, 0.50)
    if int(tb) % 2 == 1:
        mc = int(0.25 * SR); tc = np.arange(mc) / SR
        add(t, ruido(mc) * (np.exp(-tc * 22) + 0.6 * np.exp(-np.maximum(tc - 0.011, 0) * 28) * (tc > 0.011)), 0, 0.20)
    mh = int(0.09 * SR); th = np.arange(mh) / SR
    add(t + B / 2, ruido(mh, 2) * np.exp(-th * 30), 0.3, 0.09)
    add(t + B / 4, ruido(int(0.04 * SR), 2) * np.exp(-np.arange(int(0.04 * SR)) / SR * 90), -0.3, 0.035)
    for e in range(2):   # baixo em colcheias
        mb = int(B / 2 * SR); tb_ = np.arange(mb) / SR
        add(t + e * B / 2, np.sin(2 * np.pi * midi(root - 12) * tb_) * np.exp(-tb_ * 5) * (1 - np.exp(-tb_ * 300)), 0, 0.26)
    ms = int(B * 0.45 * SR); ts = np.arange(ms) / SR       # acorde de serra no contratempo
    st = sum(sum(np.sin(2 * np.pi * midi(mm + 12) * 2 ** (dd / 12) * h * ts) / h for h in range(1, 7)) for mm in ch for dd in (-0.1, 0.1))
    add(t + B / 2, st * np.exp(-ts * 7), 0.15, 0.022)
    if int(tb - (IB + BB)) % 2 == 0:                        # piano junto, para não perder a emoção
        add(t, piano(midi(ch[int(tb) % 3] + 24), 1.2, 0.8), -0.2, 0.10)

out = np.tanh(out * 1.15); out /= np.abs(out).max() + 1e-9; out *= 0.9
fo = int(2.5 * SR); out[-fo:] *= np.linspace(1, 0, fo)[:, None]
with wave.open(OUT, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype('<i2').tobytes())
print(OUT, f'{BPM:.0f} BPM', f'explosão em {t_drop:.2f}s', f'final em {t_fim:.2f}s')
