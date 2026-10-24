# Story com roteiro de filme de evento (edição avançada do fotógrafo), em 4 atos:
#   1. ABERTURA emocional: sai do preto, faixas de cinema, câmera lenta, piano, título (atrás da pessoa se houver)
#   2. SUBIDA: cortes acelerando (1, 1, 1/2, 1/2, 1/4...), zoom crescendo, riser e meio tempo de silêncio
#   3. EXPLOSÃO: flash + impacto + tremor, faixas abrem, corte em toda batida com pulso, chicote, tela em 3,
#      stutter e rampas de velocidade
#   4. FINAL emocional: faixas voltam, câmera lenta, clique da foto e marca
# O primeiro clipe abre o vídeo e o último fecha. "clipe.mp4@1.5" força o trecho da abertura/final a começar em 1,5 s.
#
# Uso: python3 story_cinema.py saida.mp4 abertura.mp4 meio1.mp4 ... final.mp4 --texto "Bastidores" --sub "Beth · 70 anos"
#      [--musica faixa.mp3] [--sem-marca] [--som 0.25]
import sys, os, subprocess, json, argparse, tempfile, wave, numpy as np, cv2
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont, ImageFilter

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI); sys.path.insert(0, os.path.join(AQUI, '..', 'scripts'))
import cor_fotografo as cor, efeitos as fx
FONTS = os.path.join(AQUI, '..', 'assets', 'fonts')
W, H, FPS, SR = 1080, 1920, 30, 48000
ease = lambda u: u * u * (3 - 2 * u)

ap = argparse.ArgumentParser()
ap.add_argument('saida'); ap.add_argument('clipes', nargs='+')
ap.add_argument('--texto', default=''); ap.add_argument('--sub', default='')
ap.add_argument('--musica', default=''); ap.add_argument('--sem-marca', action='store_true'); ap.add_argument('--som', type=float, default=0.25)
a = ap.parse_args()
TMP = tempfile.mkdtemp(prefix='cine_')
def run(cmd): subprocess.run(cmd, check=True)

# ---------------- roteiro em tempos de batida ----------------
IB, BB, DB, OB = 8, 4, 16, 6
SUBIDA = [1, 1, 0.5, 0.5, 0.25, 0.25, 0.25, 0.25]
EXPLOSAO = [(2, 'rampa'), (1, ''), (1, ''), (1, ''), (1, ''), (2, 'tres'), (1, ''), (1, ''), (2, 'rampa'), (1, ''), (1, ''), (1, 'stutter'), (1, '')]
CORTES_EXP = ['chicote', 'seco', 'zoom', 'seco', 'chicote', 'seco', 'luz', 'seco', 'chicote', 'seco', 'zoom', 'seco']
BPM = 120.0
if a.musica:
    import musica; INFO = musica.analisa(a.musica); BPM = INFO['bpm']
B = 60 / BPM
T_SUB, T_DROP, T_FIM = IB * B, (IB + BB) * B, (IB + BB + DB) * B; TOT = (IB + BB + DB + OB) * B
print(f'roteiro: abertura 0-{T_SUB:.1f}s, subida até {T_DROP:.1f}s, explosão até {T_FIM:.1f}s, final até {TOT:.1f}s ({BPM:.1f} BPM)', flush=True)

# ---------------- análise dos clipes ----------------
def probe(p):
    j = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_streams', '-show_format', p]))
    v = next(s for s in j['streams'] if s['codec_type'] == 'video'); w, h = int(v['width']), int(v['height'])
    rot = next((int(sd['rotation']) for sd in v.get('side_data_list', []) if 'rotation' in sd), int(v.get('tags', {}).get('rotate', 0)))
    if abs(rot) % 180 == 90: w, h = h, w
    return float(j['format']['duration']), w, h, any(s['codec_type'] == 'audio' for s in j['streams'])

def analisa(p):
    sw, sh, af = 96, 160, 10
    fr = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-vf', f'fps={af},scale={sw}:{sh},format=gray', '-f', 'rawvideo', '-']),
                       np.uint8).reshape(-1, sh, sw).astype(np.float32)
    lap = np.log1p([cv2.Laplacian(f, cv2.CV_32F).var() for f in fr])
    mov = np.r_[0, np.abs(np.diff(fr, axis=0)).mean((1, 2))]
    d = np.array([np.zeros(2)] + [np.array(cv2.phaseCorrelate(fr[i - 1], fr[i])[0]) for i in range(1, len(fr))])
    trem = np.r_[0, np.linalg.norm(np.diff(d, axis=0), axis=1)]
    z = lambda v: (v - v.mean()) / (v.std() + 1e-6)
    return dict(nitidez=z(lap), mov=z(np.minimum(mov, np.percentile(mov, 90))), trem=z(trem), escuro=fr.mean((1, 2)) < 25, af=af)

clipes = []
for p in a.clipes:
    fix = None
    if '@' in p: p, f = p.rsplit('@', 1); fix = float(f)
    dur, w, h, ha = probe(p); clipes.append(dict(p=p, dur=dur, w=w, h=h, a=ha, fix=fix, an=analisa(p), usado=[]))

def janela(c, dur_src, modo, ini=None):
    """Melhor início para `dur_src` segundos: 'calma' (nítida, pouco tremor) ou 'acao' (movimento, nítida)."""
    an = c['an']; af = an['af']; n = max(1, int(dur_src * af)); L = len(an['nitidez'])
    if ini is not None: return min(ini, max(0, c['dur'] - dur_src - 0.05))
    if c['dur'] <= dur_src + 0.3: return max(0.0, (c['dur'] - dur_src) / 2)
    melhor, t_m = -1e9, 0.15
    for i in range(int(0.15 * af), max(int(0.15 * af) + 1, L - n - 1)):
        t0 = i / af
        if any(t0 < u1 and t0 + dur_src > u0 for u0, u1 in c['usado']): continue
        s = an['nitidez'][i:i + n].mean() - 0.7 * an['trem'][i:i + n].mean() - 3 * an['escuro'][i:i + n].mean()
        s += (0.8 * an['mov'][i:i + n].mean()) if modo == 'acao' else (-0.4 * an['mov'][i:i + n].mean())
        if s > melhor: melhor, t_m = s, t0
    if melhor == -1e9:   # clipe já todo usado: repete o melhor trecho
        c['usado'] = []; return janela(c, dur_src, modo)
    return t_m

# ---------------- plano de planos ----------------
planos = []   # dict(c, t0, beats, tipo, vel)
def plano(c, beats, tipo='', modo='acao', ini=None):
    dur_out = beats * B
    vel = {'lenta': 0.6, 'rampa': 1.15, 'stutter': 1 / 3, 'final': 0.7}.get(tipo, 1.0)
    src = dur_out * vel + 0.1; t0 = janela(c, src, modo, ini)
    c['usado'].append((t0, t0 + src)); return dict(c=c, t0=t0, beats=beats, tipo=tipo, src=src)

abre, fecha = clipes[0], clipes[-1]
SEQ = len(clipes) <= 2   # 1 ou 2 vídeos: conta a história em ordem cronológica dentro do vídeo principal

def janela_entre(c, src, lo, hi, modo):
    """Melhor início entre lo e hi (o trecho cabe inteiro antes do fim do clipe)."""
    an = c['an']; af = an['af']; n = max(1, int(src * af)); hi = min(hi, c['dur'] - src - 0.05)
    if hi <= lo: return max(0.0, min(lo, c['dur'] - src - 0.05))
    melhor, t_m = -1e9, lo
    for i in range(int(lo * af), int(hi * af) + 1):
        s = an['nitidez'][i:i + n].mean() - 0.7 * an['trem'][i:i + n].mean() - 3 * an['escuro'][i:i + n].mean()
        s += (0.8 * an['mov'][i:i + n].mean()) if modo == 'acao' else (-0.4 * an['mov'][i:i + n].mean())
        if s > melhor: melhor, t_m = s, i / af
    return t_m

if SEQ:
    prin = max(clipes, key=lambda c: c['dur'])
    vel = {'lenta': 0.6, 'rampa': 1.15, 'stutter': 1 / 3, 'final': 0.7}
    specs = [(4, 'lenta', 'calma')] + [(bt, '', 'acao') for bt in SUBIDA]
    for bt, tipo in EXPLOSAO: specs += [(bt, tipo, 'acao')] + ([(bt, 'extra', 'acao')] * 2 if tipo == 'tres' else [])
    p1 = plano(abre, 4, 'lenta', 'calma', abre['fix'])
    ini = p1['t0'] + p1['src'] if abre is prin else 0.2
    fim_prin = prin['dur'] - 0.2
    if fecha is prin and len(clipes) == 1: fim_prin -= OB * B * 0.7 + 0.3
    srcs = [bt * B * vel.get(tp, 1.0) + 0.1 for bt, tp, _ in specs]
    folga = max(0.0, (fim_prin - ini - sum(srcs)) / len(specs)); cur = ini; seq = []
    for (bt, tp, md), sr in zip(specs, srcs):
        t0 = janela_entre(prin, sr, cur, cur + folga, md); cur = t0 + sr
        seq.append(dict(c=prin, t0=t0, beats=bt, tipo='' if tp == 'extra' else tp, src=sr))
    planos.append(p1)
    for q in seq:
        if q['tipo'] == '' and planos and planos[-1]['tipo'] == 'tres' and len(planos[-1].setdefault('extra', [])) < 2:
            planos[-1]['extra'].append(q)
        else: planos.append(q)
    if fecha is prin and len(clipes) == 1:
        sr = OB * B * 0.7 + 0.1; planos.append(dict(c=prin, t0=prin['dur'] - sr - 0.1, beats=OB, tipo='final', src=sr))
    else: planos.append(plano(fecha, OB, 'final', 'acao', fecha['fix']))
else:
    meio = clipes[1:-1] if len(clipes) > 2 else clipes
    planos.append(plano(abre, 4, 'lenta', 'calma', abre['fix'] if abre['fix'] is not None else None))
    segundo = max(meio, key=lambda c: c['an']['nitidez'].max() - c['an']['trem'].mean())
    planos.append(plano(segundo, 4, 'lenta', 'calma'))
    rr = [0]
    def proximo():
        c = meio[rr[0] % len(meio)]; rr[0] += 1; return c
    for bt in SUBIDA: planos.append(plano(proximo(), bt))
    for bt, tipo in EXPLOSAO:
        if tipo == 'tres':
            p = plano(proximo(), bt, 'tres'); p['extra'] = [plano(proximo(), bt), plano(proximo(), bt)]; planos.append(p)
        else: planos.append(plano(proximo(), bt, tipo))
    planos.append(plano(fecha, OB, 'final', 'acao', fecha['fix']))
print('planos:', [(os.path.basename(p['c']['p'])[-6:-4], round(p['t0'], 1), p['beats'], p['tipo'] or '-') for p in planos], flush=True)

# tipo de cada corte k -> k+1
NP = len(planos); CORTE = {}; i_sub = 2; i_exp = 2 + len(SUBIDA); i_fim = NP - 1
CORTE[0] = 'luz'; CORTE[1] = 'seco'
for k in range(i_sub, i_exp - 1): CORTE[k] = 'seco'
CORTE[i_exp - 1] = 'flash'
for j, k in enumerate(range(i_exp, i_fim - 1)): CORTE[k] = CORTES_EXP[j % len(CORTES_EXP)]
CORTE[i_fim - 1] = 'luz'
inicio = np.r_[0, np.cumsum([p['beats'] * B for p in planos])]
CUTS = inicio[1:-1]

# ---------------- preparo: estabiliza, limpa, cor, escala (o clipe inteiro, uma vez) ----------------
def prepara(c):
    k = clipes.index(c); trf = os.path.join(TMP, f'c{k}.trf'); lut = os.path.join(TMP, f'c{k}.cube'); out = os.path.join(TMP, f'c{k}.mp4')
    g, ev = cor.mede(cor.amostra(c['p'], 0, c['dur'])); cor.cube(lut, g, ev)
    run(['ffmpeg', '-v', 'error', '-y', '-i', c['p'], '-vf', f'vidstabdetect=shakiness=7:accuracy=15:result={trf}', '-f', 'null', '-'])
    base = f'hqdn3d=1.5:1.5:5:5,vidstabtransform=input={trf}:smoothing=18:optzoom=1:zoomspeed=0.2:interpol=bicubic,lut3d={lut}:interp=tetrahedral'
    if c['h'] / c['w'] >= 1.3: vf = f'{base},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},cas=0.45,fps={FPS}'
    else: vf = (f'{base},fps={FPS},split[a][b];[a]scale=270:480:force_original_aspect_ratio=increase,crop=270:480,boxblur=12:2,'
                f'scale={W}:{H},eq=brightness=-0.08[bg];[b]scale={W}:-2:flags=lanczos,cas=0.45[fg];[bg][fg]overlay=0:(H-h)/2')
    run(['ffmpeg', '-v', 'error', '-y', '-i', c['p'], '-filter_complex', vf, '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '12',
         '-g', '6', '-pix_fmt', 'yuv420p', out])
    c['prep'] = out
usados = [c for c in clipes if any(p['c'] is c or any(e['c'] is c for e in p.get('extra', [])) for p in planos)]
with ThreadPoolExecutor(3) as ex: list(ex.map(prepara, usados))
print('estabilização e cor prontas', flush=True)

def quadros(p):
    raw = subprocess.check_output(['ffmpeg', '-v', 'quiet', '-ss', f"{p['t0']:.3f}", '-t', f"{p['src'] + 0.1:.3f}", '-i', p['c']['prep'],
                                   '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'])
    f = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    return f if len(f) else np.zeros((1, H, W, 3), np.uint8)

def indices(p, nf):
    """Índice (fracionário) do quadro da fonte para cada quadro de saída, conforme o tipo do plano."""
    u = np.arange(nf) / max(nf - 1, 1)
    if p['tipo'] == 'lenta': v = np.full(nf, 0.6)
    elif p['tipo'] == 'final': v = np.full(nf, 0.7)
    elif p['tipo'] == 'rampa': v = 0.45 + 2.6 * u ** 3          # lento e acelera para dentro do corte
    elif p['tipo'] == 'stutter':
        terc = max(1, nf // 3); return np.array([i % terc for i in range(nf)], np.float64)
    else: v = np.ones(nf)
    return np.r_[0, np.cumsum(v)[:-1]]

def pega(f, x):
    n = int(np.floor(x)); fr = x - n; n = min(n, len(f) - 1)
    if fr > 0.05 and n + 1 < len(f): return cv2.addWeighted(f[n], 1 - fr, f[n + 1], fr, 0)
    return f[n].copy()

# ---------------- gráficos ----------------
def icone_ig(size, col):
    s = size * 4; im = Image.new('RGBA', (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); w = max(4, int(s * 0.065))
    d.rounded_rectangle((w, w, s - w, s - w), int(s * 0.28), outline=col, width=w)
    r = s * 0.21; d.ellipse((s / 2 - r, s / 2 - r, s / 2 + r, s / 2 + r), outline=col, width=w)
    q = s * 0.05; d.ellipse((s * 0.73 - q, s * 0.27 - q, s * 0.73 + q, s * 0.27 + q), fill=col)
    return im.resize((size, size), Image.LANCZOS)

def marca(isz, fsz, esp, alfa, sombra=110):
    f = ImageFont.truetype(os.path.join(FONTS, 'Montserrat-Regular.ttf'), fsz); t = 'esouzafotografia'; gap = int(isz * 0.5)
    tmp = ImageDraw.Draw(Image.new('L', (1, 1))); larg = [tmp.textlength(ch, font=f) for ch in t]
    tw = sum(larg) + esp * (len(t) - 1); Wm, Hm = int(isz + gap + tw + 40), int(isz + 40)
    def desenha(cam, col, dy):
        cam.alpha_composite(icone_ig(isz, col), (20, 20 + dy)); d = ImageDraw.Draw(cam); x = 20 + isz + gap; yt = 20 + (isz - fsz * 1.22) / 2 + dy
        for ch, lw in zip(t, larg): d.text((x, yt), ch, font=f, fill=col); x += lw + esp
    s = Image.new('RGBA', (Wm, Hm), (0, 0, 0, 0)); desenha(s, (0, 0, 0, sombra), 1)
    img = s.filter(ImageFilter.GaussianBlur(4)); desenha(img, (255, 255, 255, alfa), 0)
    return np.array(img).astype(np.float32) / 255

def cola(fr, rgba, x, y, alfa=1.0):
    h, w = rgba.shape[:2]; x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0 or alfa <= 0: return
    sub = rgba[y0 - y:y1 - y, x0 - x:x1 - x]; al = sub[..., 3:4] * alfa
    fr[y0:y1, x0:x1] = (fr[y0:y1, x0:x1].astype(np.float32) * (1 - al) + sub[..., :3] * 255 * al).astype(np.uint8)

WM = None if a.sem_marca else marca(28, 24, 3.2, 190)
F_TIT = os.path.join(FONTS, 'DMSerifDisplay-Regular.ttf'); F_SUB = os.path.join(FONTS, 'Montserrat-SemiBold.ttf')
if a.sem_marca:   # tela final do organizador: o próprio título
    FIM = None
else: FIM = marca(54, 40, 6, 240, 0)
VIN = None
def vinheta():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); r = np.sqrt(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.7)) ** 2)
    return (1 - 0.28 * np.clip(r - 0.45, 0, 1) ** 1.5)[..., None].astype(np.float32)
VIN = vinheta()

MODELO = os.path.join(os.environ.get('EDICAO_MODELOS', os.path.expanduser('~/.cache/edicao-video')), 'seg', 'u2net_human_seg.onnx')
PESSOA = fx.Pessoa(MODELO) if (a.texto and os.path.exists(MODELO)) else None
TIT = SUB = None; Y_TIT = Y_SUB = 0; ATRAS = False; T_IN = 0.6; T_SUB_TXT = 1.4; T_OUT = T_SUB + 0.6
def monta_lettering(primeiro):
    global TIT, SUB, Y_TIT, Y_SUB, ATRAS, T_SUB_TXT
    if a.texto:
        if PESSOA is not None:
            m = PESSOA(primeiro)
            if m.mean() > 0.05:
                sp, hb, _ = fx.letras(a.texto, F_TIT, 320, largura_max=W - 60, espaco=2)
                y = fx.faixa_atras(m, hb, letras=fx.linhas_letras(sp))
                if y is not None: TIT, Y_TIT, ATRAS = (sp, hb), y, True
        if TIT is None:
            sp, hb, _ = fx.letras(a.texto, F_TIT, 176 if len(a.texto) <= 10 else 124); TIT, Y_TIT = (sp, hb), 560
    if a.sub:
        sp, hb, _ = fx.letras(a.sub.upper(), F_SUB, 36, espaco=9); SUB = (sp, hb)
        Y_SUB = (H - 640) if ATRAS else Y_TIT + TIT[1] - 34
    T_SUB_TXT = T_IN + 0.35 + (len(TIT[0]) * 0.06 if TIT else 0)
    print('lettering:', 'atrás da pessoa' if ATRAS else 'na frente', flush=True)
def sombra_texto(fr, y, hb, alfa):
    y0, y1 = max(0, y - 40), min(H, y + hb + 40)
    if y1 <= y0 or alfa <= 0: return fr
    yy, xx = np.mgrid[y0:y1, 0:W].astype(np.float32)
    g = np.exp(-(((xx - W / 2) / (W * 0.38)) ** 2 + ((yy - (y + hb / 2)) / (hb * 0.75)) ** 2)) * 0.38 * alfa
    fr[y0:y1] = (fr[y0:y1].astype(np.float32) * (1 - g[..., None])).astype(np.uint8); return fr

# ---------------- efeitos de câmera ----------------
def warp(fr, z, dx=0.0, dy=0.0):
    M = np.float32([[z, 0, W / 2 * (1 - z) + dx], [0, z, H / 2 * (1 - z) + dy]])
    return cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
def zoom_blur(fr, amt):
    if amt <= 0.002: return fr
    acc = np.zeros(fr.shape, np.float32)
    for i in range(6): acc += warp(fr, 1 + amt * i / 5)
    return (acc / 6).astype(np.uint8)
def chicote(fr, p, dirx):
    """Movimento de chicote: desloca e borra na horizontal (p 0..1 = força)."""
    if p <= 0.01: return fr
    k = int(8 + 170 * p); fr = cv2.blur(fr, (k, 1))
    return warp(fr, 1.0 + 0.04 * p, dirx * W * 0.35 * p, 0)
def faixas_cinema(fr, h):
    h = int(h)
    if h > 0: fr[:h] = 0; fr[H - h:] = 0
    return fr
def tres_paineis(fs, ts, t_rel, dur):
    """Tela em 3 colunas com divisória branca fina; cada coluna sobe na sua vez (1/3 de batida de atraso)."""
    out = np.zeros((H, W, 3), np.uint8); col = (W - 2 * 10) // 3
    for j in range(3):
        u = ease(min(1, max(0, (t_rel - j * B / 3) / (B * 0.5))))
        fr = fs[j]; x0 = j * (col + 10); cx = (W - col) // 2
        painel = fr[:, cx:cx + col]
        dy = int((1 - u) * H * (1 if j % 2 == 0 else -1))
        y0, y1 = max(0, dy), min(H, H + dy)
        if y1 > y0: out[y0:y1, x0:x0 + col] = painel[y0 - dy:y1 - dy]
    for j in (1, 2): out[:, j * (col + 10) - 10:j * (col + 10)] = 245
    return out

# tremor de câmera (impacto na explosão e leve em cada compasso da explosão)
rng = np.random.default_rng(3); TREMOR = rng.normal(0, 1, (int(TOT * FPS) + 10, 2))
def tremor(t):
    a1 = 22 * np.exp(-(t - T_DROP) / 0.25) if t >= T_DROP else 0
    if T_DROP <= t < T_FIM:
        tb = (t - T_DROP) % (4 * B); a1 += 6 * np.exp(-tb / 0.12)
    return a1

def batida_pulso(t):
    if not (T_DROP <= t < T_FIM): return 0.0
    tb = (t - T_DROP) % B; return float(np.exp(-tb / 0.09))

def altura_faixas(t):
    hb = 210
    if t < T_SUB: return hb
    if t < T_DROP: return hb + 40 * ease((t - T_SUB) / (T_DROP - T_SUB))
    if t < T_FIM: return (hb + 40) * (1 - ease(min(1, (t - T_DROP) / 0.12)))
    return hb * ease(min(1, (t - T_FIM) / 0.6))

# ---------------- áudio ----------------
NS = int(TOT * SR)
if a.musica:
    mus = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', a.musica, '-ac', '2', '-ar', str(SR), '-f', 's16le', '-']), np.int16)
    mus = mus.reshape(-1, 2).astype(np.float32) / 32768
    bt, eb = INFO['beats'], INFO['energia']; pre = IB + BB; melhor, kd = -1e9, pre
    for k in range(pre, len(bt) - (DB + OB)):    # explosão = maior subida de energia da faixa
        s_ = eb[k:k + 8].mean() - eb[k - 8:k].mean()
        if s_ > melhor and (k - INFO['um']) % 4 == 0: melhor, kd = s_, k
    off = int(round(bt[kd - pre] * SR)); print(f'música: explosão da faixa em {bt[kd]:.2f}s', flush=True)
    mix = np.pad(mus[off:off + NS], ((0, max(0, NS - len(mus[off:off + NS]))), (0, 0))).copy()
    mix *= 0.20 / (np.sqrt((mix ** 2).mean()) + 1e-6)
else:
    tw_ = os.path.join(TMP, 'trilha.wav'); run([sys.executable, os.path.join(AQUI, 'trilha_cinema.py'), tw_, str(IB), str(BB), str(DB), str(OB), str(BPM)])
    with wave.open(tw_) as w_: mus = np.frombuffer(w_.readframes(w_.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768
    mix = np.pad(mus[:NS], ((0, max(0, NS - len(mus[:NS]))), (0, 0))).copy() * 0.95
def soma(sig, t, g):
    i0 = int(t * SR)
    if i0 < 0: sig = sig[-i0:]; i0 = 0
    i1 = min(NS, i0 + len(sig)); mix[i0:i1] += sig[:i1 - i0] * g
# som ambiente só na abertura e no final (emoção: o som real da festa sob o piano)
for k in (0, 1, NP - 1):
    p = planos[k]
    if not p['c']['a'] or a.som <= 0: continue
    d = p['beats'] * B; x = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', f"{p['t0']:.3f}", '-t', f'{d:.3f}', '-i', p['c']['p'],
                                                                  '-ac', '2', '-ar', str(SR), '-f', 's16le', '-']), np.int16).reshape(-1, 2).astype(np.float32) / 32768
    if len(x) < 100: continue
    r = int(0.3 * SR); env = np.ones(len(x)); env[:r] = np.linspace(0, 1, r); env[-r:] = np.linspace(1, 0, r)
    soma(x * env[:, None], inicio[k], a.som)
import sfx
wh, sw, ob = sfx.whoosh(0.4), fx.swish(0.55), fx.obturador()
for k, v in CORTE.items():
    if v == 'chicote': soma(wh, CUTS[k] - 0.22, 0.12)
    if v == 'luz': soma(sw, CUTS[k] - 0.3, 0.10)
    if v == 'zoom': soma(wh, CUTS[k] - 0.3, 0.08)
T_FOTO = TOT - 2.4; soma(ob, T_FOTO, 0.6)
if a.musica:   # impacto na explosão quando a música não tem
    m = int(1.2 * SR); ti = np.arange(m) / SR
    soma(np.stack([np.sin(2 * np.pi * np.cumsum(35 + 90 * np.exp(-ti * 9)) / SR) * np.exp(-ti * 2.5)] * 2, 1), T_DROP, 0.35)
fo = int(1.4 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None] ** 1.3
mix = np.tanh(mix * 1.1) * 0.93
wav = os.path.join(TMP, 'mix.wav')
with wave.open(wav, 'wb') as w_: w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((mix * 32767).astype('<i2').tobytes())

# ---------------- composição ----------------
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-profile:v', 'high',
                        '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', a.saida], stdin=subprocess.PIPE)
gi = 0; mask = None; NA = NB = 3; congelado = None; dir_ch = 1
for k, p in enumerate(planos):
    nf = int(round(inicio[k + 1] * FPS)) - gi
    f = quadros(p); idx = indices(p, nf)
    extras = [(quadros(e), indices(e, nf)) for e in p.get('extra', [])]
    z0, z1 = (1.0, 1.05) if k % 2 == 0 else (1.05, 1.0)
    for i in range(nf):
        t = (gi + i) / FPS; u = i / max(nf - 1, 1)
        fr = pega(f, idx[i])
        if k == 0 and i == 0 and (a.texto or a.sub): monta_lettering(fr)
        if p['tipo'] == 'tres':
            fr = tres_paineis([fr] + [pega(ef, ei[i]) for ef, ei in extras], None, i / FPS, nf / FPS)
        # câmera: empurrão lento, zoom crescendo na subida, pulso na batida, tremor
        z = z0 + (z1 - z0) * ease(u)
        if T_SUB <= t < T_DROP: z *= 1 + 0.10 * ease((t - T_SUB) / (T_DROP - T_SUB))
        z *= 1 + 0.06 * batida_pulso(t)
        am = tremor(t); g = min(len(TREMOR) - 1, gi + i)
        fr = warp(fr, z + am / 900, TREMOR[g, 0] * am, TREMOR[g, 1] * am)
        # transições
        c_out, c_in = CORTE.get(k), CORTE.get(k - 1)
        if c_out == 'zoom' and i >= nf - NA: q = (i - (nf - NA) + 1) / NA; fr = zoom_blur(warp(fr, 1 + 0.1 * q * q), 0.12 * q)
        if c_in == 'zoom' and i < NB: q = 1 - i / NB; fr = zoom_blur(warp(fr, 1 + 0.08 * q * q), 0.12 * q * q)
        if c_out == 'chicote' and i >= nf - NA: fr = chicote(fr, ((i - (nf - NA) + 1) / NA) ** 1.5, -dir_ch)
        if c_in == 'chicote' and i < NB: fr = chicote(fr, (1 - i / NB) ** 1.5, dir_ch)
        for kk in (k - 1, k):
            if CORTE.get(kk) == 'luz':
                q = (t - (CUTS[kk] - 0.25)) / 0.7
                if 0 <= q <= 1: fr = fx.vazamento(fr, q, semente=kk)
        if c_in == 'flash' and i < 5: fr = cv2.addWeighted(fr, 1 - 0.8 * (1 - i / 5), np.full_like(fr, 255), 0.8 * (1 - i / 5), 0)
        fr = fx.pulso(fr, batida_pulso(t) * 0.8)
        # final: clique da foto e tela da marca por cima
        if k == NP - 1 and t >= T_FOTO:
            if congelado is None: congelado = fr.copy()
            fr = fx.foto(congelado, min(1, (t - T_FOTO) / 0.8), angulo=-3.5)
        fr = fx.cinema(fr, gi + i)
        fr = (fr.astype(np.float32) * VIN).astype(np.uint8)
        fr = faixas_cinema(fr, altura_faixas(t))
        # título da abertura
        if (TIT or SUB) and T_IN <= t <= T_OUT + 0.5:
            sai = 1 - ease(min(1, max(0, (t - T_OUT) / 0.5)))
            if ATRAS and (i % 2 == 0 or mask is None): mask = PESSOA(fr)
            if TIT:
                faixa = fx.camada_letras(TIT[0], TIT[1], t, T_IN, passo=0.06, dur=0.6, subida=40)
                if not ATRAS: fr = sombra_texto(fr, Y_TIT, TIT[1], ease(min(1, (t - T_IN) / 0.6)) * sai)
                fr = fx.aplica_faixa(fr, faixa, Y_TIT - int(14 * (1 - sai)), sai, mask if ATRAS else None)
            if SUB and t >= T_SUB_TXT:
                fr = sombra_texto(fr, Y_SUB, SUB[1], ease(min(1, (t - T_SUB_TXT) / 0.4)) * sai * 0.8)
                fr = fx.aplica_faixa(fr, fx.camada_letras(SUB[0], SUB[1], t, T_SUB_TXT, passo=0.025, dur=0.35, subida=14), Y_SUB, sai)
        # tela final
        tf = t - (TOT - 1.6)
        if tf >= 0:
            q = ease(min(1, max(0, tf / 0.6)))
            fr = cv2.addWeighted(cv2.GaussianBlur(fr, (0, 0), 1 + 12 * q), 1 - 0.5 * q, np.zeros_like(fr), 0, 0)
            if FIM is not None: cola(fr, FIM, (W - FIM.shape[1]) / 2, H / 2 - FIM.shape[0] / 2 + 14 * (1 - q), q)
            elif TIT:
                fr = fx.aplica_faixa(fr, fx.camada_letras(TIT[0], TIT[1], tf + 10, 10), H // 2 - TIT[1] // 2 - 30, q)
                if SUB: fr = fx.aplica_faixa(fr, fx.camada_letras(SUB[0], SUB[1], tf + 10, 10), H // 2 + TIT[1] // 2 - 40, q)
        elif WM is not None and t > 1.0:
            cola(fr, WM, (W - WM.shape[1]) / 2, H - 330 + 26 - max(0, int(altura_faixas(t)) - 200))
        if t < 0.6: fr = (fr.astype(np.float32) * ease(t / 0.6)).astype(np.uint8)   # sai do preto
        enc.stdin.write(fr.tobytes())
    if CORTE.get(k) == 'chicote': dir_ch = -dir_ch
    gi += nf
enc.stdin.close(); enc.wait()
print('pronto:', a.saida, f'{TOT:.1f}s')
