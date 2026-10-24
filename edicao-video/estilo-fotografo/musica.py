# Análise de música para encaixar os cortes: andamento (BPM), batidas, início de compasso e o melhor trecho
# da faixa para a duração do story (o refrão/parte mais cheia, começando num tempo 1).
# Uso direto: python3 musica.py faixa.mp3 [duração_s]
import numpy as np, subprocess, sys

SR = 22050; HOP = 512; NFFT = 2048

def carrega(p, sr=SR):
    x = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', str(sr), '-f', 's16le', '-']), np.int16)
    return x.astype(np.float32) / 32768

def analisa(p):
    x = carrega(p); n = 1 + (len(x) - NFFT) // HOP
    idx = np.arange(NFFT)[None, :] + HOP * np.arange(n)[:, None]
    S = np.abs(np.fft.rfft(x[idx] * np.hanning(NFFT), axis=1))
    L = np.log1p(100 * S)
    flux = np.maximum(0, np.diff(L, axis=0)).sum(1); flux = np.r_[0, flux]
    flux -= np.convolve(flux, np.ones(16) / 16, 'same'); flux = np.maximum(flux, 0)
    fps = SR / HOP
    # andamento: autocorrelação do envelope de ataques, com preferência suave por ~115 BPM
    ac = np.correlate(flux, flux, 'full')[len(flux) - 1:]
    bpms = np.arange(70, 181, 0.25); lags = 60 * fps / bpms
    val = np.interp(lags, np.arange(len(ac)), ac)
    val2 = np.interp(lags * 2, np.arange(len(ac)), ac)       # reforço pelo dobro do período
    peso = np.exp(-0.5 * (np.log2(bpms / 115) / 0.9) ** 2)
    bpm = bpms[np.argmax((val + 0.5 * val2) * peso)]
    # ajuste fino: andamento e fase que mais caem em cima dos ataques ao longo da faixa inteira
    fr = np.arange(len(flux)); melhor = (-1, bpm, 0)
    for b in np.arange(bpm - 1.2, bpm + 1.2001, 0.05):
        P = 60 * fps / b
        for f in np.arange(0, P, 0.5):
            v = np.interp(np.arange(f, len(flux) - 1, P), fr, flux).mean()
            if v > melhor[0]: melhor = (v, b, f)
    _, bpm, f0 = melhor; P = 60 * fps / bpm
    beats = np.arange(f0, len(flux) - 1, P) / fps + NFFT / 2 / SR   # centro da janela de análise
    # tempo 1 do compasso: onde o grave (bumbo/baixo) é mais forte, de 4 em 4
    grave = L[:, 1:int(150 / (SR / NFFT))].sum(1)
    bf = (beats - NFFT / 2 / SR) * fps
    gb = np.interp(bf, np.arange(len(grave)), grave)
    um = int(np.argmax([gb[k::4].mean() for k in range(4)]))
    # energia por batida
    rms = np.sqrt(np.convolve(x ** 2, np.ones(HOP) / HOP, 'same')[::HOP])
    eb = np.interp(beats * fps, np.arange(len(rms)), rms)
    return dict(bpm=float(bpm), beats=beats, um=um, energia=eb, dur=len(x) / SR)

def melhor_trecho(info, dur, estilo='festa'):
    """Início (s) do trecho de `dur` segundos com mais energia, começando num tempo 1 e longe do fim."""
    beats, eb = info['beats'], info['energia']; nb = int(np.ceil(dur / (60 / info['bpm'])))
    cand = [k for k in range(info['um'], len(beats) - nb, 4) if beats[k] > 1.0 and beats[k] + dur < info['dur'] - 2]
    if not cand: return float(beats[info['um']]) if len(beats) else 0.0
    nota = []
    for k in cand:
        e = eb[k:k + nb]
        s = e.mean() + 0.3 * e[:4].mean()       # começa já cheio (sem introdução morna)
        if estilo == 'romantico': s = e.mean() - 0.5 * e.std()   # trecho mais constante, sem explosão
        nota.append(s)
    return float(beats[cand[int(np.argmax(nota))]])

if __name__ == '__main__':
    info = analisa(sys.argv[1]); d = float(sys.argv[2]) if len(sys.argv) > 2 else 16
    print(f"{info['bpm']:.1f} BPM, {info['dur']:.0f}s, melhor trecho começa em {melhor_trecho(info, d):.2f}s")
