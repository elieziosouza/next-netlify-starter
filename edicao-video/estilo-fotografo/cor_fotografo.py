# Color grading do fotógrafo ("luz natural"): corrige branco e exposição de cada clipe e aplica um look único,
# limpo e luminoso, com pele e rosas naturais. Gera uma LUT .cube por clipe para o ffmpeg (lut3d).
import numpy as np, subprocess

def amostra(p, t0, d, n=6, w=144, h=256):
    """Alguns quadros do trecho, em RGB 0..1 (já com a rotação do celular aplicada)."""
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', f'{t0:.3f}', '-t', f'{d:.3f}', '-i', p,
                                   '-vf', f'fps={n / max(d, 0.1):.4f},scale={w}:{h}', '-frames:v', str(n),
                                   '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3).astype(np.float32) / 255

def lin(x): return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)
def srgb(x): x = np.clip(x, 0, None); return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)

def mede(fr):
    """Ganhos de branco (pelos tons neutros claros: parede, toalha, prato) e de exposição."""
    px = fr.reshape(-1, 3); L = px @ [0.2126, 0.7152, 0.0722]
    mx, mn = px.max(1), px.min(1); sat = (mx - mn) / (mx + 1e-4)
    neutro = (sat < 0.18) & (L > 0.35) & (L < 0.95)
    base = px[neutro] if neutro.sum() > 200 else px[(L > np.percentile(L, 60))]
    m = lin(base).mean(0); g = m.mean() / (m + 1e-6)
    g = 1 + 0.7 * (g - 1)                       # corrige 70%: tira a dominante sem deixar frio
    g = np.clip(g, 0.85, 1.18)
    med = np.median(lin(px * 1.0) @ [0.2126, 0.7152, 0.0722])
    ev = np.clip(0.20 / (med + 1e-4), 0.97, 1.5)  # meio-tom alvo ~0,49 em sRGB: luminoso, sem estourar
    return g, ev

def look(rgb, g, ev):
    x = lin(rgb) * g * ev
    # ombro suave nos claros (não estoura toalha e prato)
    x = x / (1 + 0.18 * x)
    x *= 1.18
    y = srgb(x)
    # curva em S delicada + preto levemente aberto (aspecto de foto, não de vídeo)
    s = y * y * (3 - 2 * y)
    y = y + 0.22 * (s - y)
    y = 0.018 + y * (0.985 - 0.018)
    # vibração: aumenta mais o que está pouco saturado, protege o que já é forte (rosas, morango)
    L = (y @ [0.2126, 0.7152, 0.0722])[..., None]
    sat = (y.max(-1, keepdims=True) - y.min(-1, keepdims=True))
    y = L + (y - L) * (1 + 0.28 * (1 - np.clip(sat * 1.6, 0, 1)))
    # verde da folhagem um pouco mais oliva, para não brigar com o rosa
    r, gg, b = y[..., 0], y[..., 1], y[..., 2]
    verde = np.clip((gg - np.maximum(r, b)) * 4, 0, 1)
    y[..., 1] -= 0.03 * verde; y[..., 0] += 0.012 * verde
    # calor leve nos claros
    w = np.clip((L[..., 0] - 0.55) / 0.45, 0, 1)
    y[..., 0] += 0.012 * w; y[..., 2] -= 0.012 * w
    return np.clip(y, 0, 1)

def cube(caminho, g, ev, n=33):
    v = np.linspace(0, 1, n)
    b, gg, r = np.meshgrid(v, v, v, indexing='ij')   # .cube: R varia mais rápido
    rgb = np.stack([r, gg, b], -1).reshape(-1, 3)
    out = look(rgb, g, ev)
    with open(caminho, 'w') as f:
        f.write(f'LUT_3D_SIZE {n}\n')
        f.write('\n'.join(f'{a:.5f} {c:.5f} {d:.5f}' for a, c, d in out))
    return caminho
