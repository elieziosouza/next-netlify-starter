# Story de festa com acabamento completo ("edição AAA") do fotógrafo:
# cortes escolhidos na batida, estabilização (vidstab 2 passadas), limpeza de ruído, color grading por clipe
# (cor_fotografo.py), nitidez, aproximação suave em cada cena, transições de zoom com desfoque na batida,
# lettering que entra saindo do desfoque, marca d'água minimalista e tela final com a marca.
#
# Uso:
#   python3 story_aaa.py saida.mp4 clipe1.mp4 [clipe2.mp4 ...] [--dur 16] [--estilo festa|romantico]
#                        [--texto "Os detalhes"] [--sub "24.10.2026"] [--pos alto|baixo] [--som 0.15]
# A ordem dos clipes na linha de comando é a ordem do vídeo.
import sys, os, subprocess, json, argparse, tempfile, wave, numpy as np, cv2
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI); sys.path.insert(0, os.path.join(AQUI, '..', 'scripts'))
import cor_fotografo as cor
FONTS = os.path.join(AQUI, '..', 'assets', 'fonts')
W, H, FPS, SR = 1080, 1920, 30, 48000

ap = argparse.ArgumentParser()
ap.add_argument('saida'); ap.add_argument('clipes', nargs='+')
ap.add_argument('--dur', type=float, default=16); ap.add_argument('--estilo', default='festa')
ap.add_argument('--texto', default=''); ap.add_argument('--sub', default=''); ap.add_argument('--pos', default='alto')
ap.add_argument('--som', type=float, default=0.15); ap.add_argument('--sem-final', action='store_true')
a = ap.parse_args()
BPM = 120 if a.estilo == 'festa' else 84; BEAT = 60 / BPM
TMP = tempfile.mkdtemp(prefix='aaa_')
def run(cmd): subprocess.run(cmd, check=True)

# ---------------- escolha dos trechos ----------------
def probe(p):
    j = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_streams', '-show_format', p]))
    v = next(s for s in j['streams'] if s['codec_type'] == 'video'); w, h = int(v['width']), int(v['height'])
    rot = next((int(sd['rotation']) for sd in v.get('side_data_list', []) if 'rotation' in sd), int(v.get('tags', {}).get('rotate', 0)))
    if abs(rot) % 180 == 90: w, h = h, w
    return float(j['format']['duration']), w, h, any(s['codec_type'] == 'audio' for s in j['streams'])

def analisa(p, has_a):
    """Nota por décimo de segundo: nitidez, movimento da cena (sem chicote), som; tremido conta contra."""
    sw, sh, af = 96, 160, 10
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-vf', f'fps={af},scale={sw}:{sh},format=gray', '-f', 'rawvideo', '-'])
    fr = np.frombuffer(raw, np.uint8).reshape(-1, sh, sw).astype(np.float32); n = len(fr)
    lap = np.array([cv2.Laplacian(f, cv2.CV_32F).var() for f in fr])
    luz = fr.mean((1, 2)); mov = np.r_[0, np.abs(np.diff(fr, axis=0)).mean((1, 2))]
    # tremido: variação rápida do deslocamento global (fase), não o movimento da cena
    desl = [np.zeros(2)] + [np.array(cv2.phaseCorrelate(fr[i - 1], fr[i])[0]) for i in range(1, n)]
    desl = np.array(desl); trem = np.r_[0, np.linalg.norm(np.diff(desl, axis=0), axis=1)]
    if has_a:
        x = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', '8000', '-f', 's16le', '-']), np.int16).astype(np.float32)
        k = 800; m = len(x) // k; rms = np.sqrt((x[:m * k].reshape(m, k) ** 2).mean(1)) if m else np.zeros(1)
        rms = np.interp(np.arange(n), np.arange(len(rms)), rms)
    else: rms = np.zeros(n)
    z = lambda v: (v - v.mean()) / (v.std() + 1e-6)
    nota = z(np.log1p(lap)) + 0.3 * z(np.minimum(mov, np.percentile(mov, 85))) + 0.3 * z(rms) - 0.6 * z(trem)
    nota -= 2.0 * (luz < 25)
    return nota, af

def escolhe(clipes, alvo):
    L = 4 * BEAT; tot_disp = sum(c['dur'] for c in clipes); out = []
    for c in clipes:
        nseg = max(1, int(round(max(L, alvo * c['dur'] / tot_disp) / L)))
        if c['dur'] <= L * 1.2: out.append([c, 0.15, min(L, c['dur'] - 0.2)]); continue
        # um trecho contínuo por clipe (panorâmica não leva salto no meio do movimento)
        nseg = min(nseg, max(1, int((c['dur'] - 0.4) / L)))
        nota, af = c['nota'], c['af']; n = int(nseg * L * af); mg = int(0.3 * af)
        s, i = max((nota[i:i + n].mean(), i) for i in range(mg, max(mg + 1, len(nota) - n - mg + 1)))
        out.append([c, i / af, nseg * L])
    while sum(d for _, _, d in out) > alvo + 0.01 and len(out) > 1:
        exc = sum(d for _, _, d in out) - alvo
        if out[-1][2] - exc >= 2 * BEAT: out[-1][2] -= exc; break
        out.pop()
    for s in out:   # duração em batidas inteiras
        s[2] = min(max(2, round(s[2] / BEAT)) * BEAT, s[0]['dur'] - s[1] - 0.05)
    return out

clipes = []
for p in a.clipes:
    dur, w, h, ha = probe(p); c = dict(p=p, dur=dur, w=w, h=h, a=ha); c['nota'], c['af'] = analisa(p, ha); clipes.append(c)
segs = escolhe(clipes, a.dur)
TOT = sum(d for _, _, d in segs)
print('trechos:', [(os.path.basename(c['p'])[-10:], round(t0, 2), round(d, 2)) for c, t0, d in segs], f'total {TOT:.2f}s', flush=True)

# ---------------- estabilização + limpeza + cor + escala (em paralelo) ----------------
def prepara(k):
    c, t0, d = segs[k]; trf = os.path.join(TMP, f's{k}.trf'); lut = os.path.join(TMP, f's{k}.cube'); out = os.path.join(TMP, f's{k}.mp4')
    g, ev = cor.mede(cor.amostra(c['p'], t0, d)); cor.cube(lut, g, ev)
    ss = ['-ss', f'{t0:.3f}', '-t', f'{d:.3f}', '-i', c['p']]
    run(['ffmpeg', '-v', 'error', '-y', *ss, '-vf', f'vidstabdetect=shakiness=7:accuracy=15:result={trf}', '-f', 'null', '-'])
    base = (f'hqdn3d=1.5:1.5:5:5,vidstabtransform=input={trf}:smoothing=18:optzoom=1:zoomspeed=0.2:interpol=bicubic,'
            f'lut3d={lut}:interp=tetrahedral')
    if c['h'] / c['w'] >= 1.3:
        vf = f'{base},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},cas=0.45,fps={FPS}'
    else:
        vf = (f'{base},fps={FPS},split[a][b];[a]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,boxblur=12:2,'
              f'scale={W}:{H},eq=brightness=-0.08[bg];[b]scale={W}:-2:flags=lanczos,cas=0.45[fg];[bg][fg]overlay=0:(H-h)/2')
    run(['ffmpeg', '-v', 'error', '-y', *ss, '-filter_complex', vf, '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '11',
         '-pix_fmt', 'yuv420p', out])
    return out

with ThreadPoolExecutor(3) as ex: prontos = list(ex.map(prepara, range(len(segs))))
print('estabilização e cor prontas', flush=True)

# ---------------- elementos gráficos ----------------
def icone_ig(size, col):
    s = size * 4; im = Image.new('RGBA', (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); w = max(4, int(s * 0.065))
    d.rounded_rectangle((w, w, s - w, s - w), int(s * 0.28), outline=col, width=w)
    r = s * 0.21; d.ellipse((s / 2 - r, s / 2 - r, s / 2 + r, s / 2 + r), outline=col, width=w)
    q = s * 0.05; d.ellipse((s * 0.73 - q, s * 0.27 - q, s * 0.73 + q, s * 0.27 + q), fill=col)
    return im.resize((size, size), Image.LANCZOS)

def marca(isz, fsz, esp, alfa, sombra=110):
    """Ícone fino do Instagram + esouzafotografia espaçado. Devolve RGBA recortado."""
    f = ImageFont.truetype(os.path.join(FONTS, 'Montserrat-Regular.ttf'), fsz); t = 'esouzafotografia'; gap = int(isz * 0.5)
    tmp = ImageDraw.Draw(Image.new('L', (1, 1))); larg = [tmp.textlength(ch, font=f) for ch in t]
    tw = sum(larg) + esp * (len(t) - 1); Wm, Hm = int(isz + gap + tw + 40), int(isz + 40)
    def desenha(cam, col, dy):
        cam.alpha_composite(icone_ig(isz, col), (20, 20 + dy)); d = ImageDraw.Draw(cam); x = 20 + isz + gap
        yt = 20 + (isz - fsz * 1.22) / 2 + dy
        for ch, lw in zip(t, larg): d.text((x, yt), ch, font=f, fill=col); x += lw + esp
    s = Image.new('RGBA', (Wm, Hm), (0, 0, 0, 0)); desenha(s, (0, 0, 0, sombra), 1)
    img = s.filter(ImageFilter.GaussianBlur(4)); desenha(img, (255, 255, 255, alfa), 0)
    return np.array(img).astype(np.float32) / 255

def lettering():
    if not (a.texto or a.sub): return None
    img = Image.new('RGBA', (W, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(img); y = 40
    if a.texto:
        tam = 124; ff = lambda t: ImageFont.truetype(os.path.join(FONTS, 'DMSerifDisplay-Regular.ttf'), t)
        while d.textlength(a.texto, font=ff(tam)) > W - 140 and tam > 60: tam -= 4
        f = ff(tam); tw = d.textlength(a.texto, font=f)
        s = Image.new('RGBA', img.size, (0, 0, 0, 0)); ImageDraw.Draw(s).text(((W - tw) / 2, y + 4), a.texto, font=f, fill=(0, 0, 0, 120))
        img = Image.alpha_composite(img, s.filter(ImageFilter.GaussianBlur(12))); d = ImageDraw.Draw(img)
        d.text(((W - tw) / 2, y), a.texto, font=f, fill=(255, 255, 255, 255)); y += int(tam * 1.28)
    if a.sub:
        fs = ImageFont.truetype(os.path.join(FONTS, 'Montserrat-Medium.ttf'), 30); txt = ' '.join(a.sub.upper()); tw = d.textlength(txt, font=fs)
        for x0, x1 in [((W - tw) / 2 - 84, (W - tw) / 2 - 24), ((W + tw) / 2 + 24, (W + tw) / 2 + 84)]:
            d.line([(x0, y + 19), (x1, y + 19)], fill=(255, 255, 255, 170), width=2)
        d.text(((W - tw) / 2, y), txt, font=fs, fill=(255, 255, 255, 235))
    return np.array(img).astype(np.float32) / 255

def cola(fr, rgba, x, y, alfa=1.0):
    h, w = rgba.shape[:2]; x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0 or alfa <= 0: return
    sub = rgba[y0 - y:y1 - y, x0 - x:x1 - x]; al = sub[..., 3:4] * alfa
    reg = fr[y0:y1, x0:x1].astype(np.float32)
    fr[y0:y1, x0:x1] = (reg * (1 - al) + sub[..., :3] * 255 * al).astype(np.uint8)

LET = lettering(); WM = marca(28, 24, 3.2, 190); FIM = marca(54, 40, 6, 240, 0)
y_let = 330 if a.pos == 'alto' else 1150
let_blur = [cv2.GaussianBlur(LET, (0, 0), s) if s > 0 else LET for s in np.linspace(9, 0, 12)] if LET is not None else None
T_IN, T_OUT = 0.35, min(TOT * 0.42, 4.2)
FINAL = 0 if a.sem_final else 1.9

# ---------------- transições: zoom com desfoque radial nos cortes alternados ----------------
TRANS = set(range(0, len(segs) - 1, 2))   # corte k -> k+1 com transição; os outros são corte seco na batida
NA, NB = 4, 5                             # quadros antes / depois do corte

def zoom(fr, z, cx=W / 2, cy=H / 2):
    M = np.float32([[z, 0, cx * (1 - z)], [0, z, cy * (1 - z)]])
    return cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)

def zoom_blur(fr, amt):
    if amt <= 0.002: return fr
    acc = np.zeros(fr.shape, np.float32); n = 7
    for i in range(n): acc += zoom(fr, 1 + amt * i / (n - 1))
    return (acc / n).astype(np.uint8)

ease = lambda u: u * u * (3 - 2 * u)

# ---------------- áudio ----------------
trilha = os.path.join(TMP, 'trilha.wav')
run([sys.executable, os.path.join(AQUI, 'trilha_festa.py'), trilha, str(TOT + 12), a.estilo])
with wave.open(trilha) as w_: mus = np.frombuffer(w_.readframes(w_.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768
off = int((8 * BEAT if a.estilo == 'festa' else 4 * BEAT) * SR); NS = int(TOT * SR)
mix = mus[off:off + NS].copy() * 0.85
amb = []
for c, t0, d in segs:
    n = int(round(d * SR))
    if c['a'] and a.som > 0:
        x = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', f'{t0:.3f}', '-t', f'{d:.3f}', '-i', c['p'], '-ac', '2', '-ar', str(SR), '-f', 's16le', '-']), np.int16)
        x = x.reshape(-1, 2).astype(np.float32) / 32768; x = np.pad(x, ((0, max(0, n - len(x))), (0, 0)))[:n]
        r = int(0.03 * SR); x[:r] *= np.linspace(0, 1, r)[:, None]; x[-r:] *= np.linspace(1, 0, r)[:, None]
    else: x = np.zeros((n, 2), np.float32)
    amb.append(x)
amb = np.concatenate(amb)[:NS]; mix[:len(amb)] += amb * a.som
try:
    import sfx
    wh = sfx.whoosh(0.45) * 0.10; t_acc = 0
    for k, (_, _, d) in enumerate(segs[:-1]):
        t_acc += d
        if k in TRANS:
            i0 = int((t_acc - 0.30) * SR); i1 = min(NS, i0 + len(wh)); mix[i0:i1] += wh[:i1 - i0]
except Exception as e: print('sem whoosh:', e)
fo = int(1.6 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.5
mix[:int(0.1 * SR)] *= np.linspace(0, 1, int(0.1 * SR))[:, None]
mix = np.tanh(mix * 1.1) * 0.93
wav = os.path.join(TMP, 'mix.wav')
with wave.open(wav, 'wb') as w_:
    w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((mix * 32767).astype('<i2').tobytes())

# ---------------- composição quadro a quadro ----------------
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-profile:v', 'high',
                        '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', a.saida], stdin=subprocess.PIPE)
NTOT = int(round(TOT * FPS)); gi = 0
for k, ((c, t0, d), arq) in enumerate(zip(segs, prontos)):
    nf = int(round((sum(s[2] for s in segs[:k + 1])) * FPS)) - gi
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', arq, '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
    ult = None; z0, z1 = (1.0, 1.05) if k % 2 == 0 else (1.05, 1.0)   # aproximação / afastamento alternados
    for i in range(nf):
        b = dec.stdout.read(W * H * 3)
        fr = np.frombuffer(b, np.uint8).reshape(H, W, 3).copy() if len(b) == W * H * 3 else ult.copy()
        ult = fr; u = i / max(nf - 1, 1); t = (gi + i) / FPS
        z = z0 + (z1 - z0) * ease(u)
        extra = 0.0; blur = 0.0
        if k in TRANS and i >= nf - NA: p = (i - (nf - NA) + 1) / NA; extra, blur = 0.10 * p * p, 0.12 * p
        if (k - 1) in TRANS and i < NB: p = 1 - i / NB; extra, blur = -0.0, 0.12 * p * p; z *= 1 + 0.08 * p * p
        fr = zoom(fr, z * (1 + extra))
        fr = zoom_blur(fr, blur)
        if blur > 0.06: fr = cv2.addWeighted(fr, 1.0, np.full_like(fr, 255), 0.10 * (blur / 0.12), 0)   # brilho leve no corte
        # lettering saindo do desfoque
        if LET is not None and T_IN <= t <= T_OUT + 0.6:
            if t < T_IN + 0.7:
                p = (t - T_IN) / 0.7; idx = min(11, int(ease(p) * 11)); cola(fr, let_blur[idx], 0, y_let + 18 * (1 - ease(p)), ease(p))
            elif t > T_OUT:
                p = (t - T_OUT) / 0.6; idx = max(0, 11 - int(p * 11)); cola(fr, let_blur[idx], 0, y_let - 10 * p, 1 - ease(p))
            else: cola(fr, LET, 0, y_let)
        # tela final: escurece e desfoca o último plano, marca no centro
        tf = t - (TOT - FINAL)
        if FINAL and tf >= 0:
            p = ease(min(1, tf / 0.6)); bl = cv2.GaussianBlur(fr, (0, 0), 1 + 14 * p)
            fr = cv2.addWeighted(bl, 1 - 0.55 * p, np.zeros_like(bl), 0, 0)
            q = ease(min(1, max(0, (tf - 0.25) / 0.6)))
            cola(fr, FIM, (W - FIM.shape[1]) / 2, H / 2 - FIM.shape[0] / 2 + 14 * (1 - q), q)
        else:
            cola(fr, WM, (W - WM.shape[1]) / 2, H - 330 + 26)
        if t < 0.25: fr = (fr * (t / 0.25)).astype(np.uint8)
        enc.stdin.write(fr.tobytes())
    dec.stdout.close(); dec.wait(); gi += nf
enc.stdin.close(); enc.wait()
print('pronto:', a.saida, f'{TOT:.1f}s')
