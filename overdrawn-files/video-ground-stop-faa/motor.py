"""Motor de animação do Overdrawn Files: fundo em vídeo + camada de gráficos desenhada quadro a quadro."""
import math, subprocess, os
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1920, 1080, 30
RED = (225, 37, 27)
WHITE = (242, 242, 242)
GREY = (160, 166, 172)
DARK = (11, 13, 16)
AMBER = (242, 183, 5)
KIT = "/home/user/next-netlify-starter/edicao-video/assets/fonts"
INTER = "/usr/share/fonts/opentype/inter"


@lru_cache(None)
def F(name, size):
    p = {
        "black": f"{KIT}/Montserrat-Black.ttf",
        "xbold": f"{KIT}/Montserrat-ExtraBold.ttf",
        "bold": f"{INTER}/Inter-Bold.otf",
        "semi": f"{INTER}/Inter-SemiBold.otf",
        "med": f"{INTER}/Inter-Medium.otf",
        "serif": f"{KIT}/DMSerifDisplay-Regular.ttf",
        "mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    }[name]
    return ImageFont.truetype(p, size)


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def eo(x):  # ease out cubic
    x = clamp(x)
    return 1 - (1 - x) ** 3


def eio(x):
    x = clamp(x)
    return 3 * x * x - 2 * x * x * x


def prog(t, t0, dur=0.5):
    return eo((t - t0) / dur)


def col(c, a):
    return (c[0], c[1], c[2], int(255 * clamp(a)))


def tw(text, font):
    b = font.getbbox(text)
    return b[2] - b[0]


def text(img, s, font, x, y, fill=WHITE, a=1.0, anchor="la"):
    if a <= 0:
        return
    d = ImageDraw.Draw(img)
    d.text((x, y), s, font=font, fill=col(fill, a), anchor=anchor)


def rise(img, s, font, x, y, t, t0, fill=WHITE, anchor="la", dist=34, dur=0.55):
    p = prog(t, t0, dur)
    if p <= 0:
        return
    text(img, s, font, x, y + (1 - p) * dist, fill, p, anchor)


def rect(img, box, fill, a=1.0, r=0):
    if a <= 0 or box[2] < box[0] or box[3] < box[1]:
        return
    d = ImageDraw.Draw(img)
    if r and (box[2] - box[0]) > 2 * r and (box[3] - box[1]) > 2 * r:
        d.rounded_rectangle(box, r, fill=col(fill, a))
    else:
        d.rectangle(box, fill=col(fill, a))


def panel(img, box, a=0.78, r=18):
    rect(img, box, DARK, a, r)


def counter_str(v, fmt):
    return fmt.format(v)


def count(t, t0, dur, target):
    p = eo((t - t0) / dur)
    return target * p


def stamp(img, s, cx, cy, t, t0, color=RED, size=64, angle=-7):
    p = (t - t0) / 0.28
    if p <= 0:
        return
    p = clamp(p)
    scale = 1.7 - 0.7 * eo(p)
    f = F("black", size)
    w_, h_ = tw(s, f) + 60, size + 44
    layer = Image.new("RGBA", (w_ + 20, h_ + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((10, 10, w_ + 10, h_ + 10), 10, outline=col(color, 1), width=8)
    d.text((10 + w_ / 2, 10 + h_ / 2 + 2), s, font=f, fill=col(color, 1), anchor="mm")
    layer = layer.rotate(angle, expand=True, resample=Image.BICUBIC)
    nw, nh = int(layer.width * scale), int(layer.height * scale)
    layer = layer.resize((nw, nh), Image.BICUBIC)
    if p < 1:
        alpha = layer.split()[3].point(lambda v: int(v * p))
        layer.putalpha(alpha)
    img.alpha_composite(layer, (int(cx - nw / 2), int(cy - nh / 2)))


def sweep(img, t, y=0):
    """Linha vermelha que varre a tela no começo de cada cena."""
    p = eio(t / 0.6)
    if p >= 1:
        return
    x = int(-200 + (W + 400) * p)
    rect(img, (x - 260, y + 0, x, y + 6), RED, 1.0)


def bug(img):
    logo(img, 70, 62, 22, a=0.9)
    text(img, "OVERDRAWN FILES", F("xbold", 22), 104, 62, WHITE, 0.85, "lm")


def logo(img, cx, cy, r, a=1.0, width=None):
    d = ImageDraw.Draw(img)
    width = width or max(3, r // 6)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col(WHITE, a), width=width)
    d.rectangle((cx - r * 0.55, cy - width * 0.8, cx + r * 0.55, cy + width * 0.8), fill=col(RED, a))


def progress_bar(img, gt, total):
    rect(img, (0, H - 8, W, H), (40, 40, 40), 0.6)
    rect(img, (0, H - 8, int(W * gt / total), H), RED, 1.0)


def source(img, s, t, t0=0.6):
    p = prog(t, t0, 0.5)
    text(img, s.upper(), F("semi", 22), 70, H - 58, GREY, p * 0.9, "lm")


def kicker(img, s, x, y, t, t0=0.15, color=RED):
    """Etiqueta pequena acima do título."""
    p = prog(t, t0, 0.4)
    if p <= 0:
        return
    f = F("xbold", 26)
    w_ = tw(s, f)
    rect(img, (x, y, x + int((w_ + 32) * p), y + 46), color, 1.0)
    if p > 0.6:
        text(img, s, f, x + 16, y + 23, WHITE, (p - 0.6) / 0.4, "lm")


def bar(img, x, y, w, h, frac, color=RED, bg=(60, 60, 60), a=1.0):
    rect(img, (x, y, x + w, y + h), bg, 0.55 * a)
    rect(img, (x, y, x + int(w * clamp(frac)), y + h), color, a)


def cross(img, cx, cy, s, t, t0, color=RED, width=10):
    p = prog(t, t0, 0.3)
    if p <= 0:
        return
    d = ImageDraw.Draw(img)
    e = s * p
    d.line((cx - s, cy - s, cx - s + 2 * e, cy - s + 2 * e), fill=col(color, 1), width=width)
    if p > 0.5:
        e2 = s * (p - 0.5) * 2
        d.line((cx + s, cy - s, cx + s - 2 * e2, cy - s + 2 * e2), fill=col(color, 1), width=width)


def arrow(img, x1, y, x2, a=1.0, color=GREY, width=5):
    if a <= 0:
        return
    d = ImageDraw.Draw(img)
    d.line((x1, y, x2, y), fill=col(color, a), width=width)
    d.polygon([(x2, y), (x2 - 18, y - 11), (x2 - 18, y + 11)], fill=col(color, a))


def wrap(s, font, maxw):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        nxt = (cur + " " + w_).strip()
        if tw(nxt, font) <= maxw:
            cur = nxt
        else:
            lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def quote(img, s, who, x, y, maxw, t, t0=0.3, size=58):
    f = F("serif", size)
    lines = wrap("“" + s + "”", f, maxw)
    lh = int(size * 1.18)
    for i, ln in enumerate(lines):
        rise(img, ln, f, x, y + i * lh, t, t0 + i * 0.12)
    rise(img, who.upper(), F("bold", 26), x, y + len(lines) * lh + 24, t, t0 + len(lines) * 0.12 + 0.2, GREY)
    pr = prog(t, t0, 0.5)
    rect(img, (x - 34, y + 6, x - 26, y + int((len(lines) * lh) * pr)), RED, 1.0)
    return y + len(lines) * lh + 70


def bg_cmd(path, start, nframes, pan=0):
    vf = (
        "scale=2112:1188:force_original_aspect_ratio=increase,"
        f"crop=1920:1080:x='(iw-1920)*({'n' if pan >= 0 else f'{nframes}-n'})/{max(1, nframes)}':y='(ih-1080)/2',"
        "eq=brightness=-0.10:saturation=0.65:contrast=1.05,gblur=sigma=1.2,vignette=PI/4,format=rgb24"
    )
    return [
        "ffmpeg", "-v", "error", "-stream_loop", "-1", "-ss", f"{start:.2f}", "-i", path,
        "-vf", vf, "-r", str(FPS), "-frames:v", str(nframes), "-f", "rawvideo", "-pix_fmt", "rgb24", "-",
    ]


def render_scene(out, nframes, bgs, draw, gt0, total, dim=0.42):
    """bgs: lista de arquivos de vídeo; o tempo da cena é dividido entre eles."""
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
         "-pix_fmt", "yuv420p", out],
        stdin=subprocess.PIPE,
    )
    shade = Image.new("RGBA", (W, H), (0, 0, 0, int(255 * dim)))
    per = math.ceil(nframes / len(bgs))
    fi = 0
    for k, path in enumerate(bgs):
        n = min(per, nframes - fi)
        if n <= 0:
            break
        dec = subprocess.Popen(bg_cmd(path, 0.5, n, pan=(1 if k % 2 == 0 else -1)), stdout=subprocess.PIPE)
        for _ in range(n):
            raw = dec.stdout.read(W * H * 3)
            if len(raw) < W * H * 3:
                raw = b"\x00" * (W * H * 3)
            frame = Image.frombytes("RGB", (W, H), raw).convert("RGBA")
            frame.alpha_composite(shade)
            t = fi / FPS
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            draw(ov, t, nframes / FPS)
            sweep(ov, t)
            bug(ov)
            progress_bar(ov, gt0 + t, total)
            frame.alpha_composite(ov)
            enc.stdin.write(frame.convert("RGB").tobytes())
            fi += 1
        dec.stdout.close()
        dec.wait()
    enc.stdin.close()
    enc.wait()
