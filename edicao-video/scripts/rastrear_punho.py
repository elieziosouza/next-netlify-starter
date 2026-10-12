import numpy as np, cv2, subprocess, json
A, B = 33.0, 36.8
p = subprocess.run(["ffmpeg","-v","error","-ss",str(A),"-t",str(B-A),"-i","me.mp4","-vf","fps=30","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
fr = np.frombuffer(p, np.uint8).reshape(-1, 850, 478, 3)
out = []
for i, f in enumerate(fr):
    ycc = cv2.cvtColor(f, cv2.COLOR_RGB2YCrCb)
    sk = ((ycc[..., 1] > 135) & (ycc[..., 1] < 180) & (ycc[..., 2] > 85) & (ycc[..., 2] < 135) & (ycc[..., 0] > 60)).astype(np.uint8)
    sk = cv2.morphologyEx(sk, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8)); sk = cv2.morphologyEx(sk, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    sk[:, 175:] = 0; sk[:200] = 0
    face = np.zeros_like(sk); cv2.ellipse(face, (250, 400), (115, 165), 0, 0, 360, 1, -1); sk[face > 0] = 0
    n, lab, st, cen = cv2.connectedComponentsWithStats(sk)
    best = max(range(1, n), key=lambda k: st[k][4], default=None)
    if best is None or st[best][4] < 1200: out.append(None); continue
    ys, xs = np.where(lab == best)
    top = ys.min(); sel = ys < top + 90                    # parte de cima = o punho
    out.append(dict(t=A + i / 30, c=[float(xs[sel].mean()), float(ys[sel].mean())], area=int(st[best][4])))
json.dump(out, open("fist.json", "w"))
print([(round(o["t"], 2), [round(v) for v in o["c"]]) if o else None for o in out[::5]])
sel = [6, 12, 18, 24, 40, 60, 80, 100]
ims = []
for i in sel:
    f = fr[i].copy(); o = out[i]
    if o: cv2.circle(f, (int(o["c"][0]), int(o["c"][1])), 30, (255, 215, 0), 3)
    ims.append(cv2.resize(f, (159, 283)))
cv2.imwrite("fist_track.jpg", cv2.cvtColor(np.hstack(ims), cv2.COLOR_RGB2BGR))
