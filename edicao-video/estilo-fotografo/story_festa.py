# Story de festa em tempo real (fotógrafo): escolhe os melhores trechos, corta no tempo da trilha,
# põe trilha própria, lettering opcional e a assinatura @esouzafotografia. Saída 1080x1920, pronta para postar.
#
# Uso:
#   python3 story_festa.py saida.mp4 clipe1.mp4 [clipe2.mov ...] [opções]
# Opções:
#   --dur 15              duração alvo em segundos (story = 15; até 60)
#   --estilo festa        festa (120 BPM) | romantico (84 BPM: entrada, valsa, cerimônia)
#   --texto "Ana & Pedro" lettering principal (serifado). Vazio = sem lettering
#   --sub "24.10.2026"    linha menor embaixo do lettering
#   --pos alto|baixo      onde fica o lettering (alto = terço de cima, padrão)
#   --som 0.15            volume do som original do vídeo por baixo da trilha (0 = só trilha)
#   --inteiro             usa os clipes inteiros, sem escolher trechos
#   --sem-assinatura      tira o @esouzafotografia
import sys, os, subprocess, json, argparse, tempfile, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(AQUI, '..', 'assets', 'fonts')
W, H, FPS = 1080, 1920, 30

ap = argparse.ArgumentParser()
ap.add_argument('saida'); ap.add_argument('clipes', nargs='+')
ap.add_argument('--dur', type=float, default=15); ap.add_argument('--estilo', default='festa')
ap.add_argument('--texto', default=''); ap.add_argument('--sub', default=''); ap.add_argument('--pos', default='alto')
ap.add_argument('--som', type=float, default=0.15); ap.add_argument('--inteiro', action='store_true')
ap.add_argument('--sem-assinatura', action='store_true'); ap.add_argument('--trilha', default='')
a = ap.parse_args()

BPM = 120 if a.estilo == 'festa' else 84
BEAT = 60 / BPM
TMP = tempfile.mkdtemp(prefix='story_')

def run(cmd): subprocess.run(cmd, check=True)

def probe(p):
    j = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_streams', '-show_format', p]))
    v = next(s for s in j['streams'] if s['codec_type'] == 'video')
    w, h = int(v['width']), int(v['height'])
    rot = 0
    for sd in v.get('side_data_list', []):
        if 'rotation' in sd: rot = int(sd['rotation'])
    if 'rotate' in v.get('tags', {}): rot = int(v['tags']['rotate'])
    if abs(rot) % 180 == 90: w, h = h, w
    has_a = any(s['codec_type'] == 'audio' for s in j['streams'])
    return float(j['format']['duration']), w, h, has_a

def analisa(p, dur, has_a):
    """Nota por décimo de segundo: nitidez, movimento da cena (sem tremido forte) e energia do som."""
    sw, sh, af = 96, 160, 10
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-vf', f'fps={af},scale={sw}:{sh}:force_original_aspect_ratio=disable,format=gray',
                                   '-f', 'rawvideo', '-'])
    fr = np.frombuffer(raw, np.uint8).reshape(-1, sh, sw).astype(np.float32)
    n = len(fr)
    lap = np.array([np.var(f[1:-1, 1:-1] * 4 - f[:-2, 1:-1] - f[2:, 1:-1] - f[1:-1, :-2] - f[1:-1, 2:]) for f in fr])
    luz = fr.mean((1, 2))
    mov = np.r_[0, np.abs(np.diff(fr, axis=0)).mean((1, 2))]
    if has_a:
        pcm = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-ac', '1', '-ar', '8000', '-f', 's16le', '-'])
        x = np.frombuffer(pcm, np.int16).astype(np.float32)
        k = 800; m = len(x) // k
        rms = np.sqrt((x[:m * k].reshape(m, k) ** 2).mean(1)) if m else np.zeros(1)
        rms = np.interp(np.arange(n), np.arange(len(rms)), rms)
    else:
        rms = np.zeros(n)
    z = lambda v: (v - v.mean()) / (v.std() + 1e-6)
    nota = 1.0 * z(np.log1p(lap)) + 0.4 * z(np.minimum(mov, np.percentile(mov, 85))) + 0.4 * z(rms)
    nota -= 1.5 * (mov > np.percentile(mov, 95)) * (mov > 12)   # chicote / tremido forte
    nota -= 2.0 * (luz < 25)                                    # escuro demais
    return nota, af

def escolhe(clipes, alvo):
    """Distribui a duração entre os clipes e escolhe as janelas de maior nota, em múltiplos de compasso."""
    seg_len = 4 * BEAT   # um compasso: 2 s na festa, ~2,9 s no romântico
    total_disp = sum(min(c['dur'], 9e9) for c in clipes)
    out = []
    for c in clipes:
        cota = max(seg_len, alvo * c['dur'] / total_disp)
        nseg = max(1, int(round(cota / seg_len)))
        if a.inteiro or c['dur'] <= seg_len * 1.2:
            out.append((c, 0.0, c['dur'])); continue
        nota, af = c['nota'], c['af']
        L = int(seg_len * af); margem = int(0.3 * af)
        cand = [(nota[i:i + L].mean(), i) for i in range(margem, max(margem + 1, len(nota) - L - margem), 2)]
        cand.sort(reverse=True); pegos = []
        for s, i in cand:
            if all(abs(i - j) >= L for j in pegos): pegos.append(i)
            if len(pegos) == nseg: break
        for i in sorted(pegos): out.append((c, i / af, min(seg_len, c['dur'] - i / af)))
    # ajusta ao alvo: corta janelas menos importantes ou encurta a última
    tot = sum(d for _, _, d in out)
    while tot > alvo + 0.01 and len(out) > 1:
        excesso = tot - alvo
        c, t0, d = out[-1]
        if d - excesso >= 2 * BEAT: out[-1] = (c, t0, d - excesso); break
        out.pop(); tot = sum(d for _, _, d in out)
    # cortes caindo na batida
    q = []
    for c, t0, d in out:
        db = max(2, round(d / BEAT)) * BEAT
        q.append((c, t0, min(db, c['dur'] - t0)))
    return q

def lettering_png(caminho):
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    y = 360 if a.pos == 'alto' else 1180
    if a.texto:
        tam = 118
        f = ImageFont.truetype(os.path.join(FONTS, 'DMSerifDisplay-Regular.ttf'), tam)
        while d.textlength(a.texto, font=f) > W - 140 and tam > 60:
            tam -= 4; f = ImageFont.truetype(os.path.join(FONTS, 'DMSerifDisplay-Regular.ttf'), tam)
        tw = d.textlength(a.texto, font=f)
        sombra = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sombra)
        ds.text(((W - tw) / 2, y + 4), a.texto, font=f, fill=(0, 0, 0, 150))
        img = Image.alpha_composite(img, sombra.filter(ImageFilter.GaussianBlur(10)))
        d = ImageDraw.Draw(img)
        d.text(((W - tw) / 2, y), a.texto, font=f, fill=(255, 255, 255, 255))
        y += int(tam * 1.25)
    if a.sub:
        fs = ImageFont.truetype(os.path.join(FONTS, 'Montserrat-Medium.ttf'), 32)
        txt = ' '.join(a.sub.upper())  # espaçamento entre letras
        tw = d.textlength(txt, font=fs)
        linha = 60
        d.line([((W - tw) / 2 - linha - 24, y + 20), ((W - tw) / 2 - 24, y + 20)], fill=(255, 255, 255, 170), width=2)
        d.line([((W + tw) / 2 + 24, y + 20), ((W + tw) / 2 + linha + 24, y + 20)], fill=(255, 255, 255, 170), width=2)
        sombra = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sombra).text(((W - tw) / 2, y + 2), txt, font=fs, fill=(0, 0, 0, 160))
        img = Image.alpha_composite(img, sombra.filter(ImageFilter.GaussianBlur(6))); d = ImageDraw.Draw(img)
        d.text(((W - tw) / 2, y), txt, font=fs, fill=(255, 255, 255, 235))
    img.save(caminho)

def assinatura_png(caminho):
    img = Image.new('RGBA', (W, 120), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f = ImageFont.truetype(os.path.join(FONTS, 'Montserrat-Medium.ttf'), 28)
    t = '@esouzafotografia'; tw = d.textlength(t, font=f)
    s = Image.new('RGBA', (W, 120), (0, 0, 0, 0)); ImageDraw.Draw(s).text(((W - tw) / 2, 42), t, font=f, fill=(0, 0, 0, 140))
    img = Image.alpha_composite(img, s.filter(ImageFilter.GaussianBlur(5))); d = ImageDraw.Draw(img)
    d.text(((W - tw) / 2, 40), t, font=f, fill=(255, 255, 255, 200))
    img.save(caminho)

# ---------- análise ----------
clipes = []
for p in a.clipes:
    dur, w, h, has_a = probe(p)
    c = dict(p=p, dur=dur, w=w, h=h, a=has_a)
    if not a.inteiro: c['nota'], c['af'] = analisa(p, dur, has_a)
    clipes.append(c)
segs = escolhe(clipes, a.dur)
TOT = sum(d for _, _, d in segs)
print('trechos:', [(os.path.basename(c['p']), round(t0, 2), round(d, 2)) for c, t0, d in segs], f'total {TOT:.2f}s')

# ---------- trilha ----------
trilha = a.trilha or os.path.join(TMP, 'trilha.wav')
if not a.trilha:
    run([sys.executable, os.path.join(AQUI, 'trilha_festa.py'), trilha, str(max(TOT + 2, 20)), a.estilo])
inicio_trilha = 2 * 4 * BEAT if a.estilo == 'festa' else 4 * BEAT   # entra já com a batida

# ---------- montagem ----------
args = ['ffmpeg', '-v', 'error', '-y']
fc = []
for k, (c, t0, d) in enumerate(segs):
    args += ['-ss', f'{t0:.3f}', '-t', f'{d:.3f}', '-i', c['p']]
nseg = len(segs)
args += ['-ss', f'{inicio_trilha:.3f}', '-i', trilha]; i_tri = nseg
extras = []
if a.texto or a.sub:
    lettering_png(os.path.join(TMP, 'lettering.png')); args += ['-loop', '1', '-t', f'{TOT:.3f}', '-i', os.path.join(TMP, 'lettering.png')]; i_let = nseg + 1
if not a.sem_assinatura:
    assinatura_png(os.path.join(TMP, 'ass.png')); args += ['-loop', '1', '-t', f'{TOT:.3f}', '-i', os.path.join(TMP, 'ass.png')]
    i_ass = nseg + 1 + (1 if (a.texto or a.sub) else 0)

cor = 'eq=contrast=1.04:saturation=1.07:gamma=1.01'   # leve, só para dar vida; não muda pele
for k, (c, t0, d) in enumerate(segs):
    vert = c['h'] / c['w'] >= 1.3
    if vert:
        fc.append(f'[{k}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},{cor},fps={FPS},setsar=1,format=yuv420p[v{k}]')
    else:   # horizontal: vídeo inteiro no meio, fundo com o próprio vídeo desfocado
        fc.append(f'[{k}:v]{cor},fps={FPS},split[a{k}][b{k}];'
                  f'[a{k}]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,boxblur=12:2,scale={W}:{H},eq=brightness=-0.08[bg{k}];'
                  f'[b{k}]scale={W}:-2[fg{k}];[bg{k}][fg{k}]overlay=0:(H-h)/2,setsar=1,format=yuv420p[v{k}]')
    if c['a'] and a.som > 0:
        fc.append(f'[{k}:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{d:.3f},volume={a.som}[s{k}]')
    else:
        fc.append(f'anullsrc=r=48000:cl=stereo,atrim=0:{d:.3f}[s{k}]')
fc.append(''.join(f'[v{k}][s{k}]' for k in range(nseg)) + f'concat=n={nseg}:v=1:a=1[vc][ac]')
ult = 'vc'
if a.texto or a.sub:
    t_in, t_out = 0.4, min(TOT - 0.3, max(3.5, TOT * 0.45))
    fc.append(f'[{i_let}:v]format=rgba,fade=in:st={t_in}:d=0.6:alpha=1,fade=out:st={t_out}:d=0.6:alpha=1[let]')
    fc.append(f'[{ult}][let]overlay=0:0[vl]'); ult = 'vl'
if not a.sem_assinatura:
    fc.append(f'[{ult}][{i_ass}:v]overlay=0:{H - 330}[va]'); ult = 'va'
fc.append(f'[{ult}]fade=in:st=0:d=0.25,fade=out:st={TOT - 0.45:.3f}:d=0.45[vout]')
fc.append(f'[{i_tri}:a]atrim=0:{TOT:.3f},afade=in:st=0:d=0.15,afade=out:st={TOT - 1.2:.3f}:d=1.2,volume=0.85[m];'
          f'[ac][m]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.95[aout]')
args += ['-filter_complex', ';'.join(fc), '-map', '[vout]', '-map', '[aout]', '-t', f'{TOT:.3f}',
         '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
         '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', a.saida]
run(args)
print('pronto:', a.saida, f'{TOT:.1f}s')
