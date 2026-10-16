"""Demo do lettering editorial: palavra-chave serifada atrás da pessoa, legenda de uma palavra, destaque itálico e desfoque."""
import sys, math, subprocess
from pathlib import Path
KIT = Path(__file__).resolve().parent.parent   # pasta edicao-video
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUT = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
sys.path.insert(0, str(KIT / "scripts"))
from segment_person import PersonSeg
from minitop import make_minitop, make_minifooter
SRC = "/root/.claude/uploads/698dd744-d40f-5d96-b9e9-72023ae79dbf/356534d2-VID-20261011-WA0001.mp4"
FD = str(KIT / "assets" / "fonts"); W, H, FPS = 1080, 1920, 30; DUR = 12.4
GOLD = (214, 182, 116)
def F(name, s): return ImageFont.truetype(f"{FD}/{name}.ttf", s)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)

# palavras com tempo (distribuídas nas frases transcritas)
PHR = [("Então agora vamos falar de salário mínimo, o que cada governo fez, o que cada governo está prometendo fazer.", 0.89, 6.24),
       ("Bom, no governo Bolsonaro pai, o salário mínimo foi reajustado de acordo com a inflação. Não teve nenhum aumento real.", 6.46, 12.16)]
WORDS = []
for txt, st, en in PHR:
    ws = txt.split(); tot = sum(len(w) + 2 for w in ws); acc = 0
    for w in ws:
        a = st + (en - st) * acc / tot; acc += len(w) + 2; b = st + (en - st) * acc / tot
        WORDS.append((w.strip(",."), a, b))
# grandes palavras serifadas atrás da cabeça (kicker pequeno + palavra)
BIG = [("vamos falar de", "salário", 1.6, 4.6), ("de acordo com a", "inflação", 9.0, 11.0)]
ACCENT = [("SEM AUMENTO", 11.0, 12.3)]    # destaque em itálico caixa alta, dourado
BLUR_AT = [6.35]                           # transição com desfoque

seg = PersonSeg(f"{S}/seg/u2net_human_seg.onnx")   # baixar: github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.onnx
x_ = np.arange(256) / 255.0
s_curve = np.clip(x_ + 0.16 * (x_ - 0.5) * (1 - abs(2 * x_ - 1)), 0, 1)
LUT = np.stack([np.clip((s_curve - 0.010 * (1 - x_) ** 2.2 + 0.022 * x_ ** 2.2) * 255, 0, 255),
                np.clip((s_curve + 0.003 * (1 - x_) ** 2.2 + 0.010 * x_ ** 2.2) * 255, 0, 255),
                np.clip((s_curve + 0.026 * (1 - x_) ** 2.2 - 0.015 * x_ ** 2.2) * 255, 0, 255)], 1).astype(np.uint8)[:, None, :]
top, TOPH = make_minitop(W, f"{FD}/Montserrat-SemiBold.ttf"); bot, FL = make_minifooter(W, f"{FD}/Montserrat-SemiBold.ttf")

def person_mask(src_rgb):
    m = seg(src_rgb); b = (m > 0.5).astype(np.uint8)
    b = cv2.erode(b, np.ones((7, 7), np.uint8))
    n, lab = cv2.connectedComponents(b)
    keep = lab == lab[380, 239] if lab[380, 239] else b.astype(bool)
    keep = cv2.dilate(keep.astype(np.uint8), np.ones((7, 7), np.uint8)).astype(np.float32)
    xs = np.arange(m.shape[1])[None, :]
    ys = np.arange(m.shape[0])[:, None]
    head = np.clip(1.15 - np.sqrt(((xs - 239) / 112.0) ** 2 + ((ys - 330) / 175.0) ** 2), 0, 1) * 4   # elipse da cabeça
    body = (ys > 420) * np.clip((230 - np.abs(xs - 239)) / 20, 0, 1)
    keep = keep * np.clip(np.maximum(head, body), 0, 1)
    return np.clip(cv2.GaussianBlur(m * keep, (0, 0), 1.2), 0, 1)

def text_layer(text, font, fill, shadow=0.35):
    d = ImageDraw.Draw(Image.new("RGBA", (4, 4))); b = d.textbbox((0, 0), text, font=font)
    im = Image.new("RGBA", (b[2] - b[0] + 60, b[3] - b[1] + 60), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((30 - b[0], 30 - b[1]), text, font=font, fill=fill)
    if shadow:
        blk = Image.new("RGBA", im.size, (0, 0, 0, 255)); blk.putalpha(im.getchannel("A").point(lambda v: int(v * shadow)))
        sh = blk.filter(ImageFilter.GaussianBlur(10)); out = Image.new("RGBA", im.size, (0, 0, 0, 0))
        out.alpha_composite(sh, (0, 6)); out.alpha_composite(im); return out
    return im

def reveal(img, k, blur=10, rise=26):
    k = clamp(k)
    if k >= 1: return img, 0
    im = img.filter(ImageFilter.GaussianBlur((1 - k) * blur)); im.putalpha(im.getchannel("A").point(lambda v: int(v * k)))
    return im, int(rise * (1 - ease_out(k)))

def frame_at(src, t):
    sc = W / 478 * 1.02
    M = np.float32([[sc, 0, W / 2 - 239 * sc], [0, sc, 0]])
    base = cv2.LUT(cv2.warpAffine(src, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT), LUT)
    # desfoque de transição
    for tb in BLUR_AT:
        k = 1 - abs(t - tb) / 0.28
        if k > 0: base = cv2.GaussianBlur(base, (0, 0), 1 + 22 * smooth(k))
    frame = Image.fromarray(base).convert("RGBA")
    # palavra grande atrás da pessoa
    for kick, word, a, b in BIG:
        if not (a <= t < b): continue
        u = t - a; kin = ease_out(u / 0.5); kout = smooth((t - (b - 0.35)) / 0.35)
        al = kin * (1 - kout)
        big = text_layer(word, F("DMSerifDisplay-Regular", 215), (255, 255, 255, 255), 0.25)
        scale = 1.0 + 0.04 * (u / (b - a))                        # leve zoom contínuo
        big = big.resize((int(big.width * scale), int(big.height * scale)), Image.BICUBIC)
        big, _ = reveal(big, al, 14, 0)
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        y = 300
        lay.alpha_composite(big, (int(W / 2 - big.width / 2), y))
        ks = text_layer(kick, F("Montserrat-Regular", 40), (255, 255, 255, 235), 0.3)
        ks, dy = reveal(ks, (u - 0.1) / 0.45 * (1 - kout), 6, 10)
        lay.alpha_composite(ks, (int(W / 2 - big.width / 2 + 40), y + 18 + dy))
        frame.alpha_composite(lay)
        # a pessoa volta por cima da palavra
        m = person_mask(src)
        mf = cv2.warpAffine(m, M, (W, H), flags=cv2.INTER_LINEAR)
        person = Image.fromarray(base).convert("RGBA"); person.putalpha(Image.fromarray((mf * 255).astype(np.uint8)))
        clip = Image.new("L", (W, H), 0); ImageDraw.Draw(clip).rectangle((0, y - 60, W, y + big.height + 40), fill=255)
        pa = np.minimum(np.asarray(person.getchannel("A")), np.asarray(clip)); person.putalpha(Image.fromarray(pa))
        frame.alpha_composite(person)
    # legenda de uma palavra por vez (some durante a palavra grande correspondente)
    for w, a, b in WORDS:
        if a <= t < b:
            if any(a2 <= t < b2 and w.lower() == wd.lower() for _, wd, a2, b2 in BIG): break
            if any(a2 <= t < b2 for _, a2, b2 in ACCENT): break
            lay = text_layer(w, F("Montserrat-SemiBold", 62), (255, 255, 255, 255), 0.5)
            lay, dy = reveal(lay, (t - a) / 0.12, 6, 8)
            frame.alpha_composite(lay, (int(W / 2 - lay.width / 2), 1390 + dy))
            break
    # destaque itálico caixa alta, dourado
    for txt, a, b in ACCENT:
        if a <= t < b:
            u = t - a; k = ease_out(u / 0.25)
            lay = text_layer(txt, F("Montserrat-ExtraBoldItalic", 120), GOLD + (255,), 0.45)
            sc = 1.25 - 0.25 * k
            lay = lay.resize((int(lay.width * sc), int(lay.height * sc)), Image.BICUBIC)
            lay, _ = reveal(lay, k, 8, 0)
            frame.alpha_composite(lay, (int(W / 2 - lay.width / 2), 1340))
    frame.alpha_composite(top, (0, 0)); frame.alpha_composite(bot, (0, H - bot.height))
    return frame

def main():
    p = subprocess.run(["ffmpeg", "-v", "error", "-t", str(DUR), "-i", SRC, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    frames = np.frombuffer(p, np.uint8).reshape(-1, 850, 478, 3)
    if MODE.startswith("frames"):
        ts = [float(x) for x in MODE.split(":")[1].split(",")]
        outs = [frame_at(frames[int(t * FPS)], t).convert("RGB").resize((360, 640), Image.LANCZOS) for t in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUT, quality=90); return
    vout = OUT + ".v.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
    for i in range(min(len(frames), int(DUR * FPS))):
        enc.stdin.write(frame_at(frames[i], i / FPS).convert("RGB").tobytes())
    enc.stdin.close(); enc.wait()
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-t", str(DUR), "-i", f"{S}/v7/vox.wav", "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT], check=True)

main()
