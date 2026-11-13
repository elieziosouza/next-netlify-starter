import json, sys, os, subprocess
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from motor import *
from cenas import CENAS, BR

AUD = 537.03
TAIL = 2.0
T = [x['t'] for x in json.load(open('audio/tempos.json'))]
starts = [0.0] + [max(0, t - 0.25) for t in T[1:]]
ends = starts[1:] + [AUD + TAIL]
TOTAL = AUD + TAIL
os.makedirs('clips', exist_ok=True)

def frames(i):
    return int(round(ends[i] * FPS)) - int(round(starts[i] * FPS))

def job(i):
    out = f'clips/{i:02d}.mp4'
    _, bgs, fn = CENAS[i]
    render_scene(out, frames(i), [BR[b] for b in bgs], fn, starts[i], TOTAL)
    return out

def still(i, frac):
    _, bgs, fn = CENAS[i]
    d = frames(i) / FPS
    t = d * frac
    raw = subprocess.run(bg_cmd(BR[bgs[0]], 0.5 + t % 5, 1), capture_output=True).stdout
    fr = Image.frombytes('RGB', (W, H), raw).convert('RGBA')
    fr.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(255 * 0.42))))
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    fn(ov, t, d); sweep(ov, t); bug(ov); progress_bar(ov, starts[i] + t, TOTAL)
    fr.alpha_composite(ov)
    return fr.convert('RGB')

if __name__ == '__main__':
    if sys.argv[1] == 'stills':
        ids = [int(x) for x in sys.argv[2].split(',')]
        ims = [still(i, 0.85).resize((960, 540)) for i in ids]
        cols = 2; rows = (len(ims) + 1) // 2
        sheet = Image.new('RGB', (960 * cols, 540 * rows))
        for k, im in enumerate(ims):
            sheet.paste(im, ((k % cols) * 960, (k // cols) * 540))
        sheet.save(sys.argv[3], quality=88)
    else:
        ids = range(len(CENAS)) if len(sys.argv) < 3 else [int(x) for x in sys.argv[2].split(',')]
        with Pool(4) as p:
            for o in p.imap_unordered(job, ids):
                print('ok', o, flush=True)
