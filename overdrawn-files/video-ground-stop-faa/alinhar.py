import json, re, difflib, sys
sys.path.insert(0, '.')
from cenas import CENAS
segs = json.load(open('audio/segs.json'))
norm = lambda s: re.sub(r'[^a-z0-9 ]', '', s.lower().replace('-', ' '))
words = []  # (palavra, tempo estimado)
for s in segs:
    ws = norm(s['text']).split()
    for i, w in enumerate(ws):
        words.append((w, s['start'] + (s['end'] - s['start']) * i / max(1, len(ws))))
seq = [w for w, _ in words]
out, pos = [], 0
for anchor, _, _ in CENAS:
    a = norm(anchor).split()
    best, bi = 0, None
    for i in range(pos, min(len(seq), pos + 400)):
        r = difflib.SequenceMatcher(None, a, seq[i:i + len(a)]).ratio()
        if r > best + 1e-9:
            best, bi = r, i
        if r >= 0.99:
            break
    t = words[bi][1]
    # se a palavra é a primeira de um segmento, usa o início exato do segmento
    out.append(dict(anchor=anchor, t=round(t, 2), score=round(best, 2)))
    pos = bi + 1
    print(f"{t:7.2f}  {best:.2f}  {anchor}  ->  {' '.join(seq[bi:bi+len(a)])}")
json.dump(out, open('audio/tempos.json', 'w'), indent=1)
