import numpy as np, sys
M = np.unpackbits(np.load(sys.argv[1]), axis=2)[:, :, :478].astype(bool)
n = len(M); c = M.reshape(n, -1).sum(1)
# dilate-free overlap of consecutive frames
segs = []; cur = None; MIN = 60
for i in range(n):
    if c[i] < MIN:
        if cur: cur["end"] = i; segs.append(cur); cur = None
        continue
    if cur is None:
        cur = dict(start=i, events=[i], peak=i); continue
    prev = M[i - 1]; ov = (prev & M[i]).sum() / max(1, c[i - 1])
    if ov < 0.35:  # replaced
        cur["end"] = i; segs.append(cur); cur = dict(start=i, events=[i], peak=i); continue
    if c[i] > c[cur["peak"]]: cur["peak"] = i
    # word event: notable growth relative to 6 frames ago
    if i - cur["events"][-1] > 8 and c[i] - c[max(cur["start"], i - 6)] > 120 and ov > 0.6:
        cur["events"].append(i)
if cur: cur["end"] = n; segs.append(cur)
segs = [s for s in segs if s["end"] - s["start"] >= 6]
import json
json.dump(segs, open(sys.argv[2], "w"))
for k, s in enumerate(segs):
    print(k, f"{s['start']/60:6.2f}-{s['end']/60:6.2f}", "peak", f"{s['peak']/60:.2f}", "ev", [round(e/60,2) for e in s["events"]])
