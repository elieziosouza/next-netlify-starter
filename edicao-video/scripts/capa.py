"""Capa 1080x1920 para Reels/TikTok/Shorts no padrão do canal.

Uso:  python3 capa.py VIDEO SEGUNDO SAIDA.jpg ESTILO
O texto fica dentro da área central 3:4 (y 240–1680), que é o que aparece na grade do perfil.
"""
import sys, subprocess
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

KIT = Path(__file__).resolve().parent.parent
FD = KIT / "assets" / "fonts"
W, H = 1080, 1920
GOLD = (214, 182, 116); WHITE = (255, 255, 255); NAVY = (4, 16, 30); RED = (206, 34, 40)
def MF(w, s): return ImageFont.truetype(str(FD / f"Montserrat-{w}.ttf"), s)

def grab(video, t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", video, "-frames:v", "1",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                            "-of", "csv=p=0", video], capture_output=True, text=True).stdout.strip().split(",")
    w, h = int(probe[0]), int(probe[1])
    return np.frombuffer(raw, np.uint8).reshape(h, w, 3)

def background(frame, face=(239, 360), zoom=1.12, face_y=640):
    h, w = frame.shape[:2]
    sc = W / w * zoom
    M = np.float32([[sc, 0, W / 2 - face[0] * sc], [0, sc, face_y - face[1] * sc]])
    img = cv2.warpAffine(frame, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    blur = cv2.GaussianBlur(img, (0, 0), 2.2)
    img = cv2.addWeighted(img, 1.6, blur, -0.6, 0)                      # sharpen the upscale
    f = img.astype(np.float32) / 255
    f = np.clip((f - 0.5) * 1.12 + 0.5, 0, 1)                           # punchier contrast
    f[..., 2] = np.clip(f[..., 2] * 1.04 + 0.01, 0, 1)                  # cooler shadows
    yy, xx = np.mgrid[0:H, 0:W]
    vig = 1 - 0.45 * np.clip(((xx - W / 2) / (W * 0.7)) ** 2 + ((yy - 700) / (H * 0.55)) ** 2, 0, 1)
    f *= vig[..., None]
    # navy fade from the chest down, where the title sits
    g = np.clip((yy - 860) / 520, 0, 1)[..., None] ** 1.3 * 0.93
    f = f * (1 - g) + np.array(NAVY, np.float32) / 255 * g
    return Image.fromarray((f * 255).astype(np.uint8)).convert("RGBA")

def shadow_text(img, xy, text, font, fill, anchor="mm", blur=10, alpha=170, dy=6):
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((xy[0], xy[1] + dy), text, font=font, fill=(0, 0, 0, alpha), anchor=anchor)
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(img).text(xy, text, font=font, fill=fill, anchor=anchor)

def stamp(text, size=124, rot=-4, color=RED):
    f = MF("Black", size); d0 = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    b = d0.textbbox((0, 0), text, font=f); tw, th = b[2] - b[0], b[3] - b[1]
    pad = 34; im = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((6, 6, im.width - 6, im.height - 6), 18, outline=color + (255,), width=11)
    d.text((pad - b[0], pad - b[1]), text, font=f, fill=color + (255,))
    a = np.array(im); rng = np.random.default_rng(3)
    a[..., 3] = np.where(rng.random(a.shape[:2]) < 0.07, (a[..., 3] * 0.3).astype(np.uint8), a[..., 3])
    return Image.fromarray(a).rotate(rot, Image.BICUBIC, expand=True)

def kicker(img, y, text):
    f = MF("Bold", 30); d = ImageDraw.Draw(img); tw = d.textlength(text, font=f)
    d.rounded_rectangle((W / 2 - tw / 2 - 26, y - 26, W / 2 + tw / 2 + 26, y + 26), 26, outline=GOLD + (255,), width=2, fill=NAVY + (150,))
    d.text((W / 2, y), text, font=f, fill=GOLD + (255,), anchor="mm")

def fit_font(text, weight, size, maxw=960):
    d = ImageDraw.Draw(Image.new("RGBA", (4, 4)))
    while size > 30 and d.textlength(text, font=MF(weight, size)) > maxw: size -= 4
    return MF(weight, size)

def build(frame, kicker_text, lines, face=(239, 360), face_y=600, top=1110):
    """lines: list of (kind, text). kinds: big_white, big_gold, stamp (vermelho, tom negativo), stamp_gold (tom positivo), mid_white, mid_gold, rule"""
    img = background(frame, face=face, face_y=face_y)
    kicker(img, top, kicker_text)
    y = top + 70
    sizes = {"big_white": ("Black", 150, WHITE), "big_gold": ("Black", 132, GOLD),
             "mid_white": ("ExtraBold", 74, WHITE), "mid_gold": ("ExtraBold", 80, GOLD)}
    for kind, text in lines:
        if kind == "rule":
            ImageDraw.Draw(img).rectangle((W / 2 - 120, y + 8, W / 2 + 120, y + 11), fill=GOLD + (255,)); y += 40; continue
        if kind in ("stamp", "stamp_gold"):
            st = stamp(text, 128 if len(text) <= 8 else 104, color=GOLD if kind == "stamp_gold" else RED)
            if st.width > 960: st = st.resize((960, int(st.height * 960 / st.width)), Image.LANCZOS)
            img.alpha_composite(st, (int(W / 2 - st.width / 2), int(y))); y += st.height + 4; continue
        wgt, size, col = sizes[kind]
        f = fit_font(text, wgt, size)
        asc, desc = f.getmetrics(); h = asc + desc
        shadow_text(img, (W / 2, y + h / 2), text, f, col + (255,)); y += int(h * 0.98)
    return img

def cover_prova_anulada(frame):
    return build(frame, "CASO RACHADINHA", [("big_white", "PROVA"), ("stamp", "ANULADA"), ("mid_gold", "NÃO É INOCÊNCIA"), ("rule", "")], face=(239, 355))

def cover_dois_milhoes(frame):
    return build(frame, "CASO RACHADINHA", [("big_gold", "R$ 2 MILHÕES"), ("mid_white", "NA CONTA DO QUEIROZ"), ("rule", ""),
                                            ("mid_white", "E POR QUE ELE NÃO"), ("mid_white", "FOI CONDENADO?")], face=(239, 355))

def clean_frame(frame, masks, fps, t):
    """apaga legenda gravada usando as máscaras do capmask.py"""
    import importlib; sys.path.insert(0, str(Path(__file__).resolve().parent))
    from clean import Cleaner
    return Cleaner(masks).clean(frame.copy(), int(round(t * fps)))

STYLES = {"prova_anulada": cover_prova_anulada, "dois_milhoes": cover_dois_milhoes}

if __name__ == "__main__":
    video, t, out, style = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4]
    STYLES[style](grab(video, t)).convert("RGB").save(out, quality=95)
