"""Preparo das aulas do Teacher Eliezio feitas no Remotion: tudo o que não é imagem.
- abre os 2 silêncios do contador na voz (PINS/GAP) e grava vo.wav
- grava timings.json (frases com pedaços cronometrados, quizzes, expressões do avatar, amplitude da voz por quadro) que o Remotion lê
- cria a trilha leve (tom maior, 112 BPM) e o "ding", e mixa voz + efeitos + trilha com ducking em audio.wav
Uso: python3 prep_aula.py $S aula_plural.py   (o arquivo da aula define DIR, PINS, CAP, EXPR, WHOOSH, CLICKS, CTA_THUD e TK; voz em $S/DIR/vo_raw.mp3)"""
import sys, os, json, wave, subprocess, importlib.util
import numpy as np
S = sys.argv[1]; sys.path.insert(0, f"{S}/work")
spec = importlib.util.spec_from_file_location("aula", sys.argv[2]); C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
V = f"{S}/{C.DIR}"
import sfx
SR = 48000; FPS = 30
PINS, GAP, CD = C.PINS, getattr(C, "GAP", 3.4), 3.0
def f(t): return t + GAP * sum(1 for p in PINS if p < t)
QZ = [(f(p) + 0.2, f(p) + 0.2 + CD) for p in PINS]
VO_END = f(C.VO_END); TOTAL = round(VO_END + 0.40, 2)
CAP = C.CAP
def words(chunks):
    out = []
    for a, b, tx in chunks:
        ws = tx.split(); tot = sum(len(w) + 1 for w in ws); acc = 0; a, b = f(a), f(b)
        for w in ws: out.append(dict(w=w, t=round(a + (b - a) * acc / tot, 3))); acc += len(w) + 1
    return out
caps = []
for lg, ch in CAP:
    c = dict(lang=lg, start=round(f(ch[0][0]), 3), end=round(f(ch[-1][1]), 3), words=words(ch))
    if lg == "pt" and caps and caps[-1]["lang"] == "en" and "pt" not in caps[-1]: caps[-1]["pt"] = c
    else: caps.append(c)
for i, c in enumerate(caps): c["until"] = round(caps[i + 1]["start"] - 0.1, 3) if i + 1 < len(caps) else TOTAL
# expressões do avatar: 1 sorrindo, 2 desconfiado, 7 surpreso, 8 piscando, 9 pensando (mão no queixo), 10 bravo, 11 assustado
EXPR = [(f(a), e) for a, e in C.EXPR]
EXPR += [(QZ[0][0] - 0.05, 9), (QZ[0][1], 7), (QZ[1][0] - 0.05, 9), (QZ[1][1], 7)]   # mão no queixo no contador, surpreso na revelação
EXPR = sorted((round(a, 3), e) for a, e in EXPR)
def T(x): return round(f(x), 3)

def readw(p):
    w = wave.open(p); x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768; return x.reshape(-1, w.getnchannels())
def writew(p, x, ch=2):
    w = wave.open(p, "wb"); w.setnchannels(ch); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()

def voz():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{V}/vo_raw.mp3", "-ar", str(SR), "-ac", "2", f"{V}/vo_raw48.wav"], check=True)
    raw = readw(f"{V}/vo_raw48.wav"); parts = []; last = 0
    for p in PINS:
        i = int(p * SR); parts += [raw[last:i], np.zeros((int(GAP * SR), 2), np.float32)]; last = i
    parts.append(raw[last:]); vo = np.concatenate(parts)
    n = int(TOTAL * SR); out = np.zeros((n, 2), np.float32); out[:min(n, len(vo))] = vo[:n]; writew(f"{V}/vo.wav", out); return out

def amplitude(vo):
    m = vo.mean(1); hop = SR // FPS; n = int(TOTAL * FPS); e = np.zeros(n)
    for k in range(n): seg = m[k * hop:(k + 1) * hop]; e[k] = np.sqrt((seg ** 2).mean()) if len(seg) else 0
    e = np.clip(e / (np.percentile(e, 95) + 1e-6), 0, 1.2); sm = np.zeros_like(e); z = 0
    for i, v in enumerate(e): z = max(v, z * 0.72); sm[i] = z
    return [round(float(v), 3) for v in np.clip(sm, 0, 1)]

def trilha(dur):
    """trilha leve e alegre: marimba em I-V-vi-IV (dó maior), baixo redondo, bumbo macio e chocalho, 112 BPM"""
    BPM = 112; beat = 60 / BPM; n = int(dur * SR); out = np.zeros((n, 2), np.float32); rng = np.random.default_rng(4)
    def midi(m): return 440 * 2 ** ((m - 69) / 12)
    def add(i0, sig, pan=0.0, g=1.0):
        if i0 >= n: return
        i1 = min(n, i0 + len(sig)); s = sig[:i1 - i0] * g; out[i0:i1, 0] += s * (1 - pan); out[i0:i1, 1] += s * (1 + pan)
    def marimba(m, d=0.5):
        tt = np.arange(int(d * SR)) / SR; fr = midi(m)
        return (np.sin(2 * np.pi * fr * tt) + 0.35 * np.sin(2 * np.pi * fr * 4 * tt) * np.exp(-tt * 30)) * np.exp(-tt * 7)
    prog = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]; bass = [36, 43, 45, 41]
    patt = [0, 2, 1, 2, 0, 2, 1, 2]
    nb = int(dur / (4 * beat)) + 1
    for b in range(nb):
        ch = prog[b % 4]; t0 = b * 4 * beat
        for k in range(8):
            m = ch[patt[k]] + (12 if k in (3, 7) else 0); add(int((t0 + k * beat / 2) * SR), marimba(m), -0.3 + 0.6 * (k % 2), 0.16)
        tt = np.arange(int(1.6 * beat * SR)) / SR
        for k in (0, 2):
            add(int((t0 + k * beat) * SR), np.sin(2 * np.pi * midi(bass[b % 4]) * tt) * np.exp(-tt * 3.5) * np.clip(tt / 0.01, 0, 1), 0, 0.30)
        for k in range(4):
            tk = np.arange(int(0.25 * SR)) / SR; fk = 55 + 70 * np.exp(-tk * 30)
            add(int((t0 + k * beat) * SR), np.sin(2 * np.pi * np.cumsum(fk) / SR) * np.exp(-tk * 14), 0, 0.30)
        for k in range(8):
            ts = np.arange(int(0.06 * SR)); nz = rng.standard_normal(len(ts)); nz = nz - np.concatenate([[0], nz[:-1]])
            add(int((t0 + k * beat / 2 + beat / 4) * SR), nz * np.exp(-ts / SR * 70), 0.25, 0.035 if k % 2 else 0.05)
    return out / (np.abs(out).max() + 1e-6) * 0.9

def ding(d=1.1):
    tt = np.arange(int(d * SR)) / SR; x = np.zeros_like(tt)
    for fr, g, dec in ((1568, 1, 3.2), (2349, 0.5, 4.5), (3136, 0.35, 6), (4699, 0.15, 9)): x += g * np.sin(2 * np.pi * fr * tt) * np.exp(-tt * dec)
    x *= np.clip(tt / 0.004, 0, 1); x /= np.abs(x).max(); return np.stack([x, x], 1).astype(np.float32)

def mix(vo):
    n = int(TOTAL * SR); bed = trilha(TOTAL + 1)[:n]; tl = np.arange(n) / SR
    gain = 0.09 * np.clip(tl / 0.5, 0, 1) * np.clip(1 - (tl - (TOTAL - 0.8)) / 0.8, 0, 1)
    for a, b in QZ: gain *= 1 - 0.5 * np.clip((tl - a + 0.3) / 0.3, 0, 1) * np.clip((b + 0.4 - tl) / 0.3, 0, 1)
    writew(f"{V}/song.wav", bed * gain[:, None])
    ev = [(T(a) - 0.15, sfx.whoosh(0.4), 0.12) for a in C.WHOOSH]
    ev += [(T(a), sfx.click(seed=i), 0.16) for i, a in enumerate(C.CLICKS)]
    for a, b in QZ: ev += [(a + k, sfx.click(seed=30 + k), 0.3) for k in range(3)] + [(b, ding(), 0.42), (b + 0.02, sfx.paper(0.35), 0.22)]
    ev += [(T(C.CTA_THUD), sfx.thud(0.35), 0.18)]
    sfx.build(ev, TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{V}/vo.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[0:a]highpass=f=70,acompressor=threshold=0.1:ratio=2.2:attack=8:release=200:makeup=1.4,asplit=2[vox][k2];[1:a]volume=0.8[sf];"
                    "[2:a][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][sgd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.89:level=false[a]",
                    "-map", "[a]", "-ar", str(SR), f"{V}/audio.wav"], check=True)

vo = voz()
json.dump(dict(fps=FPS, total=TOTAL, quiz=[dict(start=round(a, 3), reveal=round(b, 3)) for a, b in QZ], caps=caps, expr=EXPR, amp=amplitude(vo),
               t={k: T(v) for k, v in C.TK.items()}), open(f"{V}/timings.json", "w"), ensure_ascii=False, indent=0)
mix(vo); print("total", TOTAL, "quiz", QZ)
