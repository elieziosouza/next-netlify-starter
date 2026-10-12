import numpy as np, cv2, subprocess, json
A, B = 21.6, 24.1
p = subprocess.run(["ffmpeg","-v","error","-ss",str(A),"-t",str(B-A),"-i","me.mp4","-vf","fps=30","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
fr = np.frombuffer(p, np.uint8).reshape(-1, 850, 478, 3)
out = []
for i, f in enumerate(fr):
    ycc = cv2.cvtColor(f, cv2.COLOR_RGB2YCrCb)
    sk = ((ycc[..., 1] > 135) & (ycc[..., 1] < 180) & (ycc[..., 2] > 85) & (ycc[..., 2] < 135) & (ycc[..., 0] > 60)).astype(np.uint8)
    sk = cv2.morphologyEx(sk, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)); sk = cv2.morphologyEx(sk, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    sk[:, 238:] = 0                                   # mão fica do lado esquerdo do quadro
    face = np.zeros_like(sk); cv2.ellipse(face, (245, 400), (125, 175), 0, 0, 360, 1, -1); sk[face > 0] = 0
    n, lab, st, cen = cv2.connectedComponentsWithStats(sk)
    best = None
    for k in range(1, n):
        x, y, w, h, a = st[k]
        if a > 1500 and (best is None or a > st[best][4]): best = k
    if best is None: out.append(None); continue
    ys, xs = np.where(lab == best); top = ys.min(); bot = ys.max(); hgt = bot - top
    tip = (float(np.median(xs[ys < top + 8])), float(top))
    low = ys > top + hgt * 0.55
    j = np.argmax(xs[low]); thumb = (float(xs[low][j]), float(ys[low][j]))
    finger_x = float(np.percentile(xs[ys < top + hgt * 0.35], 50))
    corner = (finger_x, thumb[1])
    out.append(dict(t=A + i / 30, tip=tip, corner=corner, thumb=thumb, area=int(st[best][4])))
json.dump(out, open("hand.json", "w"))
sel = [8, 12, 14, 18, 24, 30, 40, 50, 60, 70]
ims = []
for i in sel:
    f = fr[i].copy(); o = out[i]
    if o:
        P = lambda q: (int(q[0]), int(q[1]))
        cv2.line(f, P(o["tip"]), P(o["corner"]), (255, 215, 0), 4); cv2.line(f, P(o["corner"]), P(o["thumb"]), (255, 215, 0), 4)
    ims.append(cv2.resize(f, (239, 425)))
cv2.imwrite("hand_track.jpg", cv2.cvtColor(np.hstack(ims), cv2.COLOR_RGB2BGR))
print([ (round(o["t"],2), [round(v) for v in o["tip"]], [round(v) for v in o["thumb"]]) if o else None for o in out[::6]])
