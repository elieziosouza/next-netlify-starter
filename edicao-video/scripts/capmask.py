import subprocess, numpy as np, sys
SRC = sys.argv[1]; OUT = sys.argv[2]
W, H = 478, 850; Y0, Y1 = 520, 800
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
masks = []; fb = W * H * 3
while True:
    raw = p.stdout.read(fb)
    if len(raw) < fb: break
    a = np.frombuffer(raw, np.uint8).reshape(H, W, 3)[Y0:Y1].astype(np.int16)
    mn = a.min(2); mx = a.max(2)
    m = (mn > 170) & (mx - mn < 45)
    masks.append(np.packbits(m, axis=1))
np.save(OUT, np.stack(masks))
print(len(masks))
