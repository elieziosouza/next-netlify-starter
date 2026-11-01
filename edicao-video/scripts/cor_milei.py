"""Correção do vídeo gravado no carro (Milei): sombras puxando magenta (camisa preta roxa), pele laranja e um pouco saturada.
Neutraliza as sombras (tira vermelho/azul, põe um tico de verde só no escuro), abre um pouco os médios e tira ~10% de saturação da pele."""
import numpy as np, cv2
x = np.arange(256, dtype=np.float32) / 255
sh = np.clip(1 - x / 0.35, 0, 1) ** 1.5                                # peso só nas sombras
mid = np.clip(x + 0.06 * np.sin(np.pi * x), 0, 1)                      # abre os médios sem estourar
R_ = np.clip(mid - 0.020 * sh, 0, 1); G_ = np.clip(mid + 0.012 * sh, 0, 1); B_ = np.clip(mid - 0.028 * sh, 0, 1)
CURVE = np.stack([R_, G_, B_], 1)[:, None, :] * 255; CURVE = CURVE.astype(np.uint8).reshape(256, 1, 3)
def fix(rgb):
    o = cv2.LUT(rgb, CURVE)
    hsv = cv2.cvtColor(o, cv2.COLOR_RGB2HSV).astype(np.float32)
    skin = np.exp(-((hsv[..., 0] - 14) / 8) ** 2) * (hsv[..., 1] > 60)   # tons de pele (H do OpenCV 0..180)
    hsv[..., 1] *= 1 - 0.06 * skin             # menos saturada e um tico menos laranja
    return cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2RGB)
