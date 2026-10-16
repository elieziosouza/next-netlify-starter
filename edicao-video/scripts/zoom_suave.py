"""Zoom in / zoom out suave nas falas fortes do Eliezio (padrão do canal: no máximo 7%, rampa de 0,6 s).

ZOOMS = [(início, fim, quanto)] em segundos da fonte. Entre os trechos a imagem volta ao normal.
O centro do zoom fica na altura do rosto, então o topo da cabeça nunca sai do quadro.
"""
import numpy as np, cv2

def _io(x):
    x = min(1.0, max(0.0, x)); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2

def nivel(t, zooms, ramp=0.6):
    z = 0.0
    for a, b, amt in zooms:
        k = _io((t - a) / ramp) * (1 - _io((t - b) / ramp))
        z = max(z, min(0.07, amt) * k)
    return z

def aplica(img, z, cy_frac=0.42):
    if z <= 0.0005: return img
    h, w = img.shape[:2]; sc = 1 + z; cx, cy = w / 2, h * cy_frac
    M = np.float32([[sc, 0, cx - cx * sc], [0, sc, cy - cy * sc]])
    return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
