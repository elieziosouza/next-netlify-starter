import numpy as np, cv2
Y0 = 520
K = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
class Cleaner:
    def __init__(self, mask_path):
        self.M = np.load(mask_path)
    def __call__(self, frame_rgb, idx):
        return self.clean(frame_rgb, idx)
    def clean(self, frame_rgb, idx):
        if idx >= len(self.M): return frame_rgb
        m = np.unpackbits(self.M[idx], axis=1)[:, :478]
        cnt = int(m.sum())
        if cnt < 30 or cnt > 25000: return frame_rgb
        full = np.zeros(frame_rgb.shape[:2], np.uint8)
        full[Y0:Y0 + m.shape[0]] = m * 255
        strong = cv2.dilate(full, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
        a = frame_rgb.astype(np.int16); mn = a.min(2); mx = a.max(2)
        weak = ((mn > 85) & (mx - mn < 40)).astype(np.uint8) * 255
        full = cv2.bitwise_or(full, cv2.bitwise_and(weak, strong))
        full = cv2.dilate(full, K, iterations=1)
        return cv2.inpaint(np.ascontiguousarray(frame_rgb), full, 4, cv2.INPAINT_TELEA)
