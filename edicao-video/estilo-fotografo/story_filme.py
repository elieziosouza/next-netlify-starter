# Story cinematográfico com 1 vídeo (plano-sequência): poucos planos longos em ordem, câmera lenta por interpolação
# de movimento (60 quadros reais), cor de cinema, faixas de cinema, passagens pelo preto, uma rampa de velocidade no
# momento-chave (com obturador e ápice da trilha), título discreto tipo crédito de filme e final no preto com a marca.
#
# Uso: python3 story_filme.py saida.mp4 video.mp4[@início] --texto "Bastidores" --sub "Beth · 70 anos" [--sem-marca]
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
ap.add_argument('saida'); ap.add_argument('video')
ap.add_argument('--texto', default=''); ap.add_argument('--sub', default=''); ap.add_argument('--sem-marca', action='store_true')
ap.add_argument('--som', type=float, default=0.12)
a = ap.parse_args()
TMP = tempfile.mkdtemp(prefix='filme_')
def run(cmd): subprocess.run(cmd, check=True)

p = a.video; ini = 0.2
if '@' in p: p, f = p.rsplit('@', 1); ini = float(f)
j = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-print_format', 'json', '-show_streams', '-show_format', p]))
DUR = float(j['format']['duration']); TEM_SOM = any(s['codec_type'] == 'audio' for s in j['streams'])

# ---------------- planos: (duração na tela, velocidade, modo) ----------------
# velocidade 'rampa' = começa normal e desliza para 0,3x (o momento-chave)
PLANOS = [(4.0, 0.5, 'calma'), (3.5, 0.6, 'calma'), (3.5, 'rampa', 'acao'), (3.0, 0.5, 'calma'), (4.0, 0.5, 'calma')]
CORTE_SECO = {1}            # do 2º para o 3º plano: corte seco (continuidade de ação); os outros passam pelo preto
TOT = sum(d for d, _, _ in PLANOS)

def vel_curva(v, nf):
    u = np.arange(nf) / max(nf - 1, 1)
    return (0.3 + 0.7 * (1 - ease(np.clip(u / 0.7, 0, 1)))) if v == 'rampa' else np.full(nf, float(v))

# análise para escolher o melhor ponto de cada plano dentro da sua fatia do vídeo
sw, sh, af = 96, 160, 10
fr_a = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-i', p, '-vf', f'fps={af},scale={sw}:{sh},format=gray', '-f', 'rawvideo', '-']),
                     np.uint8).reshape(-1, sh, sw).astype(np.float32)
z = lambda v: (v - v.mean()) / (v.std() + 1e-6)
nit = z(np.log1p([cv2.Laplacian(f, cv2.CV_32F).var() for f in fr_a]))
mov = z(np.r_[0, np.abs(np.diff(fr_a, axis=0)).mean((1, 2))])
dsl = np.array([np.zeros(2)] + [np.array(cv2.phaseCorrelate(fr_a[i - 1], fr_a[i])[0]) for i in range(1, len(fr_a))])
trem = z(np.r_[0, np.linalg.norm(np.diff(dsl, axis=0), axis=1)])

srcs = [d * float(np.mean(vel_curva(v, int(d * FPS)))) + 0.15 for d, v, _ in PLANOS]
fim = DUR - 0.2; folga = max(0.0, (fim - ini - sum(srcs)) / len(PLANOS)); cur = ini; esc = []
for (d, v, modo), sr in zip(PLANOS, srcs):
    n = int(sr * af); melhor, t_m = -1e9, cur
    for i in range(int(cur * af), int(min(cur + folga, fim - sr) * af) + 1):
        s = nit[i:i + n].mean() - 0.8 * trem[i:i + n].mean() + (0.6 if modo == 'acao' else -0.3) * mov[i:i + n].mean()
        if s > melhor: melhor, t_m = s, i / af
    esc.append(t_m); cur = t_m + sr
print('planos (início no vídeo):', [round(t, 1) for t in esc], f'total {TOT:.1f}s', flush=True)

# ---------------- preparo de cada plano: estabiliza, interpola para 60 quadros, cor de cinema, escala ----------------
g, ev = cor.mede(cor.amostra(p, ini, DUR - ini)); LUT = cor.cube(os.path.join(TMP, 'filme.cube'), g, ev, estilo='filme')
def prepara(k):
    t0, sr = esc[k], srcs[k] + 0.2; trf = os.path.join(TMP, f'p{k}.trf'); out = os.path.join(TMP, f'p{k}.mp4')
    ss = ['-ss', f'{t0:.3f}', '-t', f'{sr:.3f}', '-i', p]
    run(['ffmpeg', '-v', 'error', '-y', *ss, '-vf', f'vidstabdetect=shakiness=7:accuracy=15:result={trf}', '-f', 'null', '-'])
    vf = (f'hqdn3d=1.5:1.5:5:5,vidstabtransform=input={trf}:smoothing=22:optzoom=1:zoomspeed=0.2:interpol=bicubic,'
          f'minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,lut3d={LUT}:interp=tetrahedral,'
          f'scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},cas=0.4')
    run(['ffmpeg', '-v', 'error', '-y', *ss, '-vf', vf, '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '12', '-pix_fmt', 'yuv420p', out])
    return out
with ThreadPoolExecutor(4) as ex: prontos = list(ex.map(prepara, range(len(PLANOS))))
print('estabilização, câmera lenta e cor prontas', flush=True)

# ---------------- trilha e som ----------------
inicio = np.r_[0, np.cumsum([d for d, _, _ in PLANOS])]
T_CHAVE = inicio[2] + PLANOS[2][0] * 0.55          # o momento mais lento da rampa
trilha = os.path.join(TMP, 'trilha.wav'); run([sys.executable, os.path.join(AQUI, 'trilha_filme.py'), trilha, str(TOT), str(T_CHAVE)])
with wave.open(trilha) as w_: mus = np.frombuffer(w_.readframes(w_.getnframes()), np.int16).reshape(-1, 2).astype(np.float32) / 32768
NS = int(TOT * SR); mix = np.pad(mus[:NS], ((0, max(0, NS - len(mus[:NS]))), (0, 0))).copy()
def soma(sig, t, gn):
    i0 = int(t * SR); i1 = min(NS, i0 + len(sig)); mix[i0:i1] += sig[:i1 - i0] * gn
if TEM_SOM and a.som > 0:
    for k, (d, _, _) in enumerate(PLANOS):
        x = np.frombuffer(subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', f'{esc[k]:.3f}', '-t', f'{d:.3f}', '-i', p, '-ac', '2', '-ar', str(SR),
                                                   '-f', 's16le', '-']), np.int16).reshape(-1, 2).astype(np.float32) / 32768
        if len(x) < SR // 4: continue
        r = int(0.4 * SR); e = np.ones(len(x)); e[:r] = np.linspace(0, 1, r); e[-r:] = np.linspace(1, 0, r)
        soma(x * e[:, None], inicio[k], a.som)
soma(fx.obturador(), T_CHAVE - 0.02, 0.5)
mix = np.tanh(mix * 1.05) * 0.95
wav = os.path.join(TMP, 'mix.wav')
with wave.open(wav, 'wb') as w_: w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((mix * 32767).astype('<i2').tobytes())

# ---------------- gráficos ----------------
def texto_espacado(txt, fonte, tam, esp, alfa=255):
    f = ImageFont.truetype(os.path.join(FONTS, fonte), tam); tmp = ImageDraw.Draw(Image.new('L', (1, 1)))
    larg = [tmp.textlength(ch, font=f) for ch in txt]; tw = sum(larg) + esp * (len(txt) - 1)
    im = Image.new('RGBA', (W, int(tam * 1.6)), (0, 0, 0, 0)); d = ImageDraw.Draw(im); x = (W - tw) / 2
    for ch, lw in zip(txt, larg): d.text((x, tam * 0.2), ch, font=f, fill=(255, 255, 255, alfa)); x += lw + esp
    s = Image.new('RGBA', im.size, (0, 0, 0, 0)); s.paste((0, 0, 0, 120), mask=im.split()[3])
    out = Image.alpha_composite(s.filter(ImageFilter.GaussianBlur(6)), im)
    return np.array(out).astype(np.float32) / 255

def cola(fr, rgba, x, y, alfa=1.0):
    h, w = rgba.shape[:2]; x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0 or alfa <= 0: return
    sub = rgba[y0 - y:y1 - y, x0 - x:x1 - x]; al = sub[..., 3:4] * alfa
    fr[y0:y1, x0:x1] = (fr[y0:y1, x0:x1].astype(np.float32) * (1 - al) + sub[..., :3] * 255 * al).astype(np.uint8)

def icone_ig(size, col):
    s = size * 4; im = Image.new('RGBA', (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); w = max(4, int(s * 0.065))
    d.rounded_rectangle((w, w, s - w, s - w), int(s * 0.28), outline=col, width=w)
    r = s * 0.21; d.ellipse((s / 2 - r, s / 2 - r, s / 2 + r, s / 2 + r), outline=col, width=w)
    q = s * 0.05; d.ellipse((s * 0.73 - q, s * 0.27 - q, s * 0.73 + q, s * 0.27 + q), fill=col)
    return im.resize((size, size), Image.LANCZOS)

def marca(isz, fsz, esp, alfa):
    f = ImageFont.truetype(os.path.join(FONTS, 'Montserrat-Regular.ttf'), fsz); t = 'esouzafotografia'; gap = int(isz * 0.5)
    tmp = ImageDraw.Draw(Image.new('L', (1, 1))); larg = [tmp.textlength(ch, font=f) for ch in t]
    tw = sum(larg) + esp * (len(t) - 1); img = Image.new('RGBA', (int(isz + gap + tw + 40), int(isz + 40)), (0, 0, 0, 0))
    img.alpha_composite(icone_ig(isz, (255, 255, 255, alfa)), (20, 20)); d = ImageDraw.Draw(img); x = 20 + isz + gap
    for ch, lw in zip(t, larg): d.text((x, 20 + (isz - fsz * 1.22) / 2), ch, font=f, fill=(255, 255, 255, alfa)); x += lw + esp
    return np.array(img).astype(np.float32) / 255

FAIXA = 230                                            # faixas de cinema
TIT = texto_espacado(a.texto.upper(), 'Montserrat-Medium.ttf', 46, 24) if a.texto else None
SUB = texto_espacado(a.sub.upper(), 'Montserrat-Regular.ttf', 24, 12, 220) if a.sub else None
WM = None if a.sem_marca else marca(22, 18, 3, 170)    # pequena, dentro da faixa preta de baixo
FIM = marca(50, 36, 6, 235) if not a.sem_marca else (texto_espacado((a.texto or '').upper(), 'Montserrat-Medium.ttf', 46, 24) if a.texto else None)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
VIN = (1 - 0.38 * np.clip(np.sqrt(((xx - W / 2) / (W * 0.7)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2) - 0.4, 0, 1) ** 1.4)[..., None]

# ---------------- composição ----------------
class Leitor:
    def __init__(self, arq):
        self.p = subprocess.Popen(['ffmpeg', '-v', 'quiet', '-i', arq, '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-'], stdout=subprocess.PIPE)
        self.i = -1; self.cur = self.prev = None
    def get(self, x):
        n = int(np.floor(x)); fr = x - n
        while self.i < n + (1 if fr > 0.05 else 0):
            b = self.p.stdout.read(W * H * 3)
            if len(b) == W * H * 3: self.prev, self.cur = self.cur, np.frombuffer(b, np.uint8).reshape(H, W, 3)
            self.i += 1
        if fr > 0.05 and self.prev is not None: return cv2.addWeighted(self.prev, 1 - fr, self.cur, fr, 0)
        return self.cur.copy()
    def fecha(self): self.p.stdout.close(); self.p.wait()

enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-profile:v', 'high',
                        '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', a.saida], stdin=subprocess.PIPE)
gi = 0; NFADE = 9; T_FIM = TOT - 2.8
for k, ((d, v, _), arq) in enumerate(zip(PLANOS, prontos)):
    nf = int(round(inicio[k + 1] * FPS)) - gi; lei = Leitor(arq)
    pos = np.r_[0, np.cumsum(vel_curva(v, nf) * 2)[:-1]]          # fonte em 60 quadros/s
    for i in range(nf):
        t = (gi + i) / FPS; u = i / max(nf - 1, 1)
        fr = lei.get(pos[i])
        zz = 1.0 + 0.06 * ease(u) if k % 2 == 0 else 1.06 - 0.05 * ease(u)
        M = np.float32([[zz, 0, W / 2 * (1 - zz)], [0, zz, H / 2 * (1 - zz)]])
        fr = cv2.warpAffine(fr, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
        fr = fx.cinema(fr, gi + i, grao=3.8, brilho=0.22)
        fr = (fr.astype(np.float32) * VIN).astype(np.uint8)
        # passagens pelo preto (menos no corte seco)
        luz = 1.0
        if k < len(PLANOS) - 1 and k not in CORTE_SECO and i >= nf - NFADE: luz = (nf - 1 - i) / NFADE
        if k > 0 and (k - 1) not in CORTE_SECO and i < NFADE: luz = min(luz, i / NFADE)
        if t < 1.0: luz = min(luz, ease(t / 1.0))
        if t > T_FIM: luz = min(luz, 1 - ease(min(1, (t - T_FIM) / 1.0)))
        if luz < 1: fr = (fr.astype(np.float32) * luz).astype(np.uint8)
        fr[:FAIXA] = 0; fr[H - FAIXA:] = 0
        # título tipo crédito de filme
        if TIT is not None and 0.9 <= t <= 4.3:
            q = ease(min(1, (t - 0.9) / 0.9)) * (1 - ease(min(1, max(0, (t - 3.5) / 0.8))))
            cola(fr, TIT, 0, H - FAIXA - 330 - 8 * (1 - q), q)
            if SUB is not None: cola(fr, SUB, 0, H - FAIXA - 250, q * ease(min(1, max(0, (t - 1.4) / 0.8))))
        # final no preto com a marca
        if FIM is not None and t > T_FIM + 0.8:
            q = ease(min(1, (t - T_FIM - 0.8) / 0.8)); cola(fr, FIM, (W - FIM.shape[1]) / 2, H / 2 - FIM.shape[0] / 2, q)
        elif WM is not None and 1.0 < t < T_FIM + 0.5:
            cola(fr, WM, (W - WM.shape[1]) / 2, H - FAIXA / 2 - WM.shape[0] / 2, 0.85)
        enc.stdin.write(fr.tobytes())
    lei.fecha(); gi += nf
enc.stdin.close(); enc.wait()
print('pronto:', a.saida, f'{TOT:.1f}s')
