"""Reel 9:16 do Ares do Horto Cajueiro (Plano&Plano) a partir de um render estático (08/11/2026).
Movimento de câmera feito aqui (sem IA de vídeo): descida pelas torres, aproximação da entrada e deslize até a placa.
Estilo corretor: palavra serifada grande + kicker pequeno, destaque itálico, transição com desfoque e tela final com contatos.
Sempre com "Imagem ilustrativa" (render da construtora). Uso: python3 reel_render_ares.py IMAGEM SAIDA.mp4 [frame_t]"""
import sys, subprocess
from pathlib import Path
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
KIT = Path(__file__).resolve().parent.parent
FD = str(KIT / "assets" / "fonts"); W, H, FPS = 1080, 1920, 30; DUR = 15.0
LIME = (206, 222, 70)                                     # tom do logo
def F(n, s): return ImageFont.truetype(f"{FD}/{n}.ttf", s)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def smooth(x): x = clamp(x); return x * x * (3 - 2 * x)
def ease(x): x = clamp(x); return 1 - (1 - x) ** 3

SRC = cv2.cvtColor(cv2.imread(sys.argv[1]), cv2.COLOR_BGR2RGB).astype(np.float32)
SH, SW = SRC.shape[:2]                                    # 1504 x 2000

# câmera: (centro x, centro y, altura da janela) em pixels da imagem, por trecho
SHOTS = [
    (0.0, 4.0, (1000, 550, 1100), (1000, 954, 1100)),     # desce das torres até a portaria
    (4.0, 8.0, (1130, 1000, 1500), (1150, 1120, 1000)),   # aproxima do casal na entrada
    (8.0, 12.0, (1250, 1130, 980), (1690, 1170, 860)),    # desliza até a placa do empreendimento
    (12.0, 15.0, (1000, 752, 1504), (1000, 752, 1400)),   # tela final (fundo desfocado)
]
def cam(t):
    for a, b, p, q in SHOTS:
        if a <= t < b or (b == DUR and t >= a):
            k = smooth((t - a) / (b - a)); return [p[i] + (q[i] - p[i]) * k for i in range(3)]
def frame_img(t):
    cx, cy, h = cam(t); w = h * W / H
    cx = clamp(cx, w / 2, SW - w / 2); cy = clamp(cy, h / 2, SH - h / 2); s = W / w
    M = np.float32([[s, 0, W / 2 - s * cx], [0, s, H / 2 - s * cy]])
    return cv2.warpAffine(SRC, M, (W, H), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)

def text_layer(text, font, fill, shadow=0.45, blur=10):
    d = ImageDraw.Draw(Image.new("RGBA", (4, 4))); b = d.textbbox((0, 0), text, font=font)
    im = Image.new("RGBA", (b[2] - b[0] + 60, b[3] - b[1] + 60), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((30 - b[0], 30 - b[1]), text, font=font, fill=fill)
    blk = Image.new("RGBA", im.size, (0, 0, 0, 255)); blk.putalpha(im.getchannel("A").point(lambda v: int(v * shadow)))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0)); out.alpha_composite(blk.filter(ImageFilter.GaussianBlur(blur))); out.alpha_composite(im); return out
def put(base, lay, cx, y, alpha=1.0, scale=1.0, blur=0.0, anchor="c"):
    if alpha <= 0: return
    if scale != 1.0: lay = lay.resize((max(1, int(lay.width * scale)), max(1, int(lay.height * scale))), Image.LANCZOS)
    if blur > 0.3: lay = lay.filter(ImageFilter.GaussianBlur(blur))
    if alpha < 1: a = lay.getchannel("A").point(lambda v: int(v * alpha)); lay = lay.copy(); lay.putalpha(a)
    x = int(cx - lay.width / 2) if anchor == "c" else int(cx)
    base.alpha_composite(lay, (x, int(y)))
def appear(t, a, b, fade=0.45):                            # entra saindo do desfoque, sai em fade
    if t < a or t > b: return 0, 0
    k = ease((t - a) / fade); out = clamp((b - t) / 0.35); return k * out, (1 - k) * 14

L = {
 "k1": text_layer("lançamento na planta", F("Montserrat-Regular", 46), (255, 255, 255, 255)),
 "b1": text_layer("Ares", F("DMSerifDisplay-Regular", 240), (255, 255, 255, 255), 0.5, 14),
 "b1b": text_layer("do Horto", F("DMSerifDisplay-Regular", 150), (255, 255, 255, 255), 0.5, 14),
 "k2": text_layer("para viver o seu", F("Montserrat-Regular", 42), (255, 255, 255, 255)),
 "b2": text_layer("novo lar", F("DMSerifDisplay-Regular", 210), (255, 255, 255, 255), 0.5, 14),
 "acc": text_layer("AGENDE SUA", F("Montserrat-ExtraBoldItalic", 112), LIME + (255,), 0.6, 12),
 "acc2": text_layer("VISITA", F("Montserrat-ExtraBoldItalic", 150), LIME + (255,), 0.6, 12),
 "ilus": text_layer("Imagem ilustrativa", F("Montserrat-Medium", 26), (255, 255, 255, 220), 0.6, 6),
 "e1": text_layer("Fale comigo", F("DMSerifDisplay-Regular", 150), (255, 255, 255, 255), 0.5, 12),
 "e2": text_layer("WhatsApp (11) 97111-8620", F("Montserrat-SemiBold", 54), (255, 255, 255, 255)),
 "e3": text_layer("@eliezio.corretordeimoveis", F("Montserrat-SemiBold", 46), LIME + (255,)),
 "e4": text_layer("eliezioimoveis.com.br  ·  @ezbrokers", F("Montserrat-Regular", 36), (230, 234, 240, 255)),
 "e5": text_layer("Eliezio Souza · Corretor de Imóveis", F("Montserrat-Regular", 34), (230, 234, 240, 255)),
}
def render(t):
    img = frame_img(t)
    # transição com desfoque nas trocas de cena
    bl = max([clamp(1 - abs(t - c) / 0.28) for c in (4.0, 8.0, 12.0)] + [0])
    if t >= 12.0: bl = max(bl, smooth((t - 12.0) / 0.5))
    if bl > 0.01: img = cv2.GaussianBlur(img, (0, 0), 1 + 22 * bl)
    if t >= 12.0: img = img * (1 - 0.45 * smooth((t - 12.0) / 0.5))
    base = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
    grad = np.zeros((H, W, 4), np.uint8); g = np.linspace(0, 1, 520) ** 1.6
    grad[:520, :, 3] = (150 * g[::-1])[:, None]; grad[-420:, :, 3] = (150 * np.linspace(0, 1, 420) ** 1.6)[:, None]
    base.alpha_composite(Image.fromarray(grad))
    a, b_ = appear(t, 0.35, 3.85)
    put(base, L["k1"], 160, 205, a, blur=b_, anchor="l"); put(base, L["b1"], W / 2, 290, a, 1 + 0.04 * (t / 4), b_); put(base, L["b1b"], W / 2, 570, a, 1 + 0.04 * (t / 4), b_)
    a, b_ = appear(t, 4.35, 7.85)
    put(base, L["k2"], 175, 265, a, blur=b_, anchor="l"); put(base, L["b2"], W / 2, 330, a, 1 + 0.04 * ((t - 4) / 4), b_)
    a, b_ = appear(t, 8.4, 11.85)
    put(base, L["acc"], W / 2, 300, a, blur=b_); put(base, L["acc2"], W / 2, 440, a, blur=b_)
    if t < 12.0: put(base, L["ilus"], W / 2, H - 150, 0.9)
    for i, (k, y) in enumerate([("e1", 560), ("e2", 830), ("e3", 940), ("e4", 1040), ("e5", 1110)]):
        a, b_ = appear(t, 12.3 + i * 0.25, DUR + 1)
        put(base, L[k], W / 2, y, a, blur=b_)
    return base.convert("RGB")

if __name__ == "__main__":
    OUT = sys.argv[2]
    if len(sys.argv) > 3:
        for ts in sys.argv[3:]: render(float(ts)).save(f"{OUT}_{ts}.jpg", quality=90)
        sys.exit()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", OUT], stdin=subprocess.PIPE)
    for f in range(int(DUR * FPS)): p.stdin.write(np.asarray(render(f / FPS)).tobytes())
    p.stdin.close(); p.wait(); print("ok", OUT)
