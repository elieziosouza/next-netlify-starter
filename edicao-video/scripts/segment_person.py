"""Máscara de pessoa com U2Net (human seg) via onnxruntime."""
import numpy as np, cv2, onnxruntime as ort
class PersonSeg:
    def __init__(self, path):
        o = ort.SessionOptions(); o.intra_op_num_threads = 4
        self.s = ort.InferenceSession(path, o, providers=["CPUExecutionProvider"]); self.inp = self.s.get_inputs()[0].name
    def __call__(self, rgb):
        h, w = rgb.shape[:2]
        x = cv2.resize(rgb, (320, 320), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
        x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
        x = x.transpose(2, 0, 1)[None].astype(np.float32)
        m = self.s.run(None, {self.inp: x})[0][0, 0]
        m = (m - m.min()) / (m.max() - m.min() + 1e-6)
        return cv2.resize(m, (w, h), interpolation=cv2.INTER_LINEAR)
