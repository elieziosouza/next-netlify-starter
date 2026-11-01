"""Correção do vídeo do Flamengo (carro, luz do dia): pretos lavados (p1 = 33) e pele da bochecha saturada.
Desce o ponto de preto, um S leve de contraste e tira ~8% da saturação da pele."""
import numpy as np, cv2
x = np.arange(256, dtype=np.float32) / 255
y = np.clip((x - 0.06) / 0.94, 0, 1); y = np.clip(y - 0.02 * np.sin(np.pi * y), 0, 1)        # preto mais fundo, rosto no mesmo brilho da gravação
CURVE = np.repeat((y * 255).astype(np.uint8)[:, None], 3, 1).reshape(256, 1, 3)
def fix(rgb):
    o = cv2.LUT(rgb, CURVE)
    hsv = cv2.cvtColor(o, cv2.COLOR_RGB2HSV).astype(np.float32)
    skin = np.exp(-((hsv[..., 0] - 14) / 8) ** 2) * (hsv[..., 1] > 60)
    hsv[..., 1] *= 1 - 0.16 * skin
    return cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2RGB)
