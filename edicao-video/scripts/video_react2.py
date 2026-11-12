"""React em tela dividida (12/11/2026): ele em cima (janela), caixa fixa no meio, vídeo de terceiros embaixo em cartão levemente 3D,
legenda alto padrão, palavras gigantes douradas translúcidas sobre o cartão, barra lateral, topo/rodapé, sons.
Uso: python3 video_react.py frames:t1,t2 | python3 video_react.py SAIDA.mp4"""
import sys, math, subprocess, re, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
K = "/home/user/next-netlify-starter/edicao-video"; sys.path.insert(0, K + "/scripts")
import zoom_suave, sfx
import barra_lateral as BAR
from minitop import make_minitop, make_minifooter, handles_row
import legenda_dinamica as L
import estilo_alto as CAP
FD = K + "/assets/fonts"; BAR.FD = FD
W, H, FPS = 1080, 1920, 30; CX = 582
CAP.CX = CX; CAP.CY = 1712; CAP.MAXW = 640
GOLD = (214, 182, 116); GOLD_L = (245, 226, 176); NAVY = (6, 34, 58); WHITE = (255, 255, 255)
ME_SS = 0.85; ME_DUR = 8.62            # trecho dele (o vídeo original tem 9,47 s; os primeiros 0,85 s são silêncio)
CLIP_SS = 13.0                         # trecho do vídeo de terceiros
END = 13.2
ZOOMS = [(4.4, 7.9, 0.035)]
words = L.words
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def back_out(x, s=1.2): x = clamp(x) - 1; return 1 + (s + 1) * x ** 3 + s * x ** 2
def MF(w, s): return ImageFont.truetype(f"{FD}/Montserrat-{w}.ttf", s)
top, TOPH = make_minitop(W, f"{FD}/Montserrat-SemiBold.ttf"); bot, _ = make_minifooter(W, f"{FD}/Montserrat-SemiBold.ttf")
HROW = handles_row(W, f"{FD}/Montserrat-SemiBold.ttf", size=25, isz=28); HDX = 42
def wt(txt, n=1):
    c = 0
    for w in words:
        if re.sub(r"[^\wÀ-ú]", "", w["w"]).lower() == txt:
            c += 1
            if c == n: return w["s"]
    raise SystemExit("palavra não achada: " + txt)
GIANT = [(wt("presidente"), "PRESIDENTE"), (wt("popstar"), "POPSTAR"), (wt("flavinho", 1), "FLAVINHO"), (wt("volta"), "VOLTA PRO BRASIL"), (wt("chupa"), "CHUPA ESSA")]
GDUR = 1.45
CARD_C = (CX, 1445); CARD_S = 540
WIN_C = (CX, 493); WIN_W, WIN_H = 500, 667

def rounded(im, rad, border=None, bw=5):
    im = im.convert("RGBA"); m = Image.new("L", im.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, im.width - 1, im.height - 1), rad, fill=255); im.putalpha(m)
    if border:
        d = ImageDraw.Draw(im); d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), rad, outline=border + (255,), width=bw)
    return im
def shadowed(im, blur=22, off=16, op=.55):
    sh = Image.new("RGBA", (im.width + 4 * blur, im.height + 4 * blur), (0, 0, 0, 0)); a = Image.new("L", sh.size, 0)
    a.paste(im.getchannel("A").point(lambda v: int(v * op)), (2 * blur, 2 * blur + off)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(blur)))
    sh.alpha_composite(im, (2 * blur, 2 * blur)); return sh
def put(fr, im, cx, cy, a=1.0, sc=1.0):
    if a <= 0.01: return
    if abs(sc - 1) > 0.004: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
    if a < 1: al = im.getchannel("A").point(lambda v: int(v * a)); im = im.copy(); im.putalpha(al)
    fr.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

SEAM = 1100
def top_panel(me_rgb, t):
    z = zoom_suave.nivel(t, ZOOMS); img = zoom_suave.aplica(me_rgb, z, cy_frac=0.30)
    sc = 0.86; sm = cv2.resize(img, (int(W * sc), int(H * sc)), interpolation=cv2.INTER_AREA)        # ele a 86%: cabeça inteira, folga em cima e embaixo
    bgp = cv2.GaussianBlur(cv2.resize(img[40:40 + SEAM], (W // 8, SEAM // 8)), (0, 0), 3); bgp = cv2.resize(bgp, (W, SEAM)).astype(np.float32) * 0.62
    y0 = 13; fg = sm[y0:y0 + SEAM].astype(np.float32); x0 = (W - sm.shape[1]) // 2
    m = np.ones((SEAM, sm.shape[1]), np.float32); f = 40; ramp = np.linspace(0, 1, f); m[:, :f] *= ramp; m[:, -f:] *= ramp[::-1]; m = m[..., None]
    bgp[:, x0:x0 + sm.shape[1]] = bgp[:, x0:x0 + sm.shape[1]] * (1 - m) + fg * m
    return Image.fromarray(np.clip(bgp, 0, 255).astype(np.uint8)).convert("RGBA")
def bottom_panel(cl_rgb):
    ph = H - SEAM; ch = int(480 * ph / W); y0 = 300                                                     # faixa do vídeo de terceiros que ocupa a largura toda
    crop = cl_rgb[y0:y0 + ch, 0:480]; im = cv2.resize(crop, (W, ph), interpolation=cv2.INTER_CUBIC)
    blur = cv2.GaussianBlur(im, (0, 0), 1.6); im = cv2.addWeighted(im, 1.5, blur, -0.5, 0)               # nitidez leve (o original é pequeno)
    out = Image.fromarray(im).convert("RGBA")
    g = np.zeros((ph, W, 4), np.uint8); g[..., 0], g[..., 1], g[..., 2] = 4, 14, 28
    ramp = np.clip((np.arange(ph) - (ph - 400)) / 400, 0, 1) ** 1.4; g[..., 3] = (ramp * 215).astype(np.uint8)[:, None]
    out.alpha_composite(Image.fromarray(g)); return out
gcache = {}
def giant_img(txt):
    if txt in gcache: return gcache[txt]
    s = 250
    while True:
        f = ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s); b = f.getbbox(txt)
        if b[2] - b[0] <= 560 and b[3] - b[1] <= 230: break
        s -= 6
    im = Image.new("RGBA", (b[2] - b[0] + 80, b[3] - b[1] + 80), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((40 - b[0], 40 - b[1]), txt, font=f, fill=GOLD_L + (170,))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0)); sh.putalpha(im.getchannel("A").point(lambda v: int(v * .4)))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0)); out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)), (0, 8)); out.alpha_composite(im)
    gcache[txt] = out; return out
def draw_giant(fr, t):
    for k, (t0, txt) in enumerate(GIANT):
        nxt = GIANT[k + 1][0] if k + 1 < len(GIANT) else 99
        dur = min(GDUR + 0.3, nxt - t0 - 0.12)           # some antes da próxima palavra entrar
        u = t - (t0 - 0.28)
        if u < 0 or u > dur + 0.28: continue
        im = giant_img(txt); side = -1 if k % 2 == 0 else 1
        kin = eo(u / 0.28); x = CARD_C[0] + side * (1 - kin) * 620; a = clamp(u / 0.1) * clamp((dur + 0.28 - u) / 0.2)
        sc = 1.0 + 0.06 * clamp(1 - abs(u - 0.28) / 0.1)
        img = im if sc == 1 else im.resize((int(im.width * sc), int(im.height * sc)), Image.BICUBIC)
        if a < 1: img = img.copy(); img.putalpha(img.getchannel("A").point(lambda v, a=a: int(v * a)))
        fr.alpha_composite(img, (int(x - img.width / 2), int(CARD_C[1] - img.height / 2)))
def end_texts(fr, t):
    u = t - 8.9
    if u < 0: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); k = eo(u / 0.4)
    d.text((CX, 1650 + 14 * (1 - k)), "COMENTE O QUE VOCÊ ACHA", font=MF("ExtraBold", 50), fill=WHITE + (int(255 * k),), anchor="mm", stroke_width=5, stroke_fill=NAVY + (int(220 * k),))
    lw = int(150 * eo((u - 0.2) / 0.5))
    if lw > 0: d.rectangle((CX - lw, 1694, CX + lw, 1696), fill=GOLD + (255,))
    k2 = eo((u - 0.5) / 0.4)
    if k2 > 0: d.text((CX, 1742 + 10 * (1 - k2)), "SIGA PARA MAIS", font=MF("ExtraBold", 46), fill=WHITE + (int(255 * k2),), anchor="mm", stroke_width=5, stroke_fill=NAVY + (int(220 * k2),))
    fr.alpha_composite(lay)
def bg(t):
    # fundo azul-marinho do canal com brilho suave atrás da janela
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32); r = np.sqrt(((xx - CX) / W) ** 2 + ((yy - 560) / H) ** 2)
    c = np.array([2, 8, 18], np.float32) + np.array([9, 40, 72], np.float32) * np.clip(1 - r * 1.8, 0, 1)[..., None]
    return Image.fromarray(np.clip(c, 0, 255).astype(np.uint8)).convert("RGBA")
BG = bg(0)
def compose(me_rgb, cl_rgb, t):
    fr = Image.new("RGBA", (W, H), (4, 14, 28, 255))
    fr.alpha_composite(top_panel(me_rgb, t), (0, 0)); fr.alpha_composite(bottom_panel(cl_rgb), (0, SEAM))
    ImageDraw.Draw(fr).rectangle((0, SEAM - 2, W, SEAM + 2), fill=GOLD + (255,))
    draw_giant(fr, t)
    kc = eo((t - 0.3) / 0.5)
    if kc > 0: BAR.lower_card(fr, "COP31 · TURQUIA", ["LULA É OVACIONADO E CERCADO", "SEGUNDO A BNEWS (11/11)"], SEAM + 30, kc, fs=34)
    ImageDraw.Draw(fr).text((CX, SEAM + 168), "Vídeo recebido por WhatsApp", font=MF("SemiBold", 21), fill=(235, 238, 245, 225), anchor="mm", stroke_width=3, stroke_fill=NAVY + (200,))
    if t < 8.2: fr.alpha_composite(CAP.overlay(t))
    end_texts(fr, t)
    if t >= 0.4:
        k = back_out((t - 0.4) / 0.55); fr.alpha_composite(top, (HDX, int(-TOPH * (1 - k)))); fr.alpha_composite(bot, (HDX, int(H - bot.height + bot.height * (1 - k))))
    BAR.draw_bar(fr, clamp(t / END), "canal", eo((t - 0.2) / 0.6), 0.0, 0.5 + 0.5 * math.sin(t * 5))
    return fr.convert("RGB")
def grab(path, t, w, h):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", path, "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3)
def audio(out):
    ev = [(0.2, sfx.barra(), 0.14)]
    for t0, txt in GIANT: ev += [(t0 - 0.30, sfx.whoosh(0.28), 0.08), (t0 - 0.02, sfx.click(3 + len(txt)), 0.22)]
    ev += [(wt("chupa") - 0.02, sfx.thud(), 0.20), (8.9, sfx.siga(), 0.12)]
    sfx.build(ev, END + 1, "sfx_r.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(ME_SS), "-t", str(ME_DUR), "-i", "me.mp4", "-ss", str(CLIP_SS), "-t", str(END), "-i", "ter.mp4", "-i", "sfx_r.wav", "-filter_complex",
        "[0:a]aresample=48000,highpass=f=80,acompressor=threshold=0.12:ratio=2.5:attack=8:release=120,apad[v];"
        "[v]asplit=2[v1][vk];[1:a]aresample=48000,volume='if(lt(t,8.3),0.16,min(0.9,0.16+(t-8.3)*1.3))':eval=frame[c];"
        "[c][vk]sidechaincompress=threshold=0.03:ratio=5:attack=15:release=300[cd];[2:a]aresample=48000[s];"
        f"[v1][cd][s]amix=inputs=3:normalize=0:duration=longest,atrim=0:{END:.3f},afade=t=out:st={END-0.35:.3f}:d=0.35[a]",
        "-map", "[a]", "-c:a", "pcm_s16le", out], check=True)
if __name__ == "__main__":
    a = sys.argv[1]
    if a.startswith("frames:"):
        ims = []
        for ts in a[7:].split(","):
            t = float(ts); me = grab("me.mp4", min(ME_SS + t, 9.4), 1080, 1920); cl = grab("ter.mp4", CLIP_SS + t, 480, 848)
            im = compose(me, cl, t); im.save(f"rf_{ts}.jpg", quality=88); ims.append(im.resize((360, 640)))
        m = Image.new("RGB", (360 * min(6, len(ims)), 640 * math.ceil(len(ims) / 6)))
        for i, im in enumerate(ims): m.paste(im, ((i % 6) * 360, (i // 6) * 640))
        m.save("rf_sheet.jpg", quality=86); sys.exit()
    audio("mix_r.wav")
    dm = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(ME_SS), "-t", str(ME_DUR), "-i", "me.mp4", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    dc = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(CLIP_SS), "-t", str(END), "-i", "ter.mp4", "-vf", "fps=30", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "mix_r.wav",
        "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", a], stdin=subprocess.PIPE)
    n = int(END * FPS); last_me = None; last_cl = None
    for i in range(n):
        t = i / FPS
        r = dm.stdout.read(W * H * 3)
        if len(r) == W * H * 3: last_me = np.frombuffer(r, np.uint8).reshape(H, W, 3)
        r2 = dc.stdout.read(480 * 848 * 3)
        if len(r2) == 480 * 848 * 3: last_cl = np.frombuffer(r2, np.uint8).reshape(848, 480, 3)
        enc.stdin.write(compose(last_me, last_cl, t).tobytes())
        if i % 100 == 0: print(i, n, flush=True)
    enc.stdin.close(); enc.wait(); print("ok", a, n)
