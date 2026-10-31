"""CBS de 11,3% (cálculo do TCU para 2027), 9:16, ~63 s, narração do ElevenLabs, versão própria do Eliezio (roteiro e arte próprios).
Hook com o 11,3%, o que a CBS substitui (PIS e Cofins), nota fiscal com a CBS separada (exemplo com itens fora da cesta básica), fim da
cascata, por que 11,3% e não 9,2%, quem paga menos (cesta básica 0%, saúde e educação −60%), cashback do CadÚnico, serviços podem
subir, Senado até 15/12. Sem opinião. Formato loop. Fontes: TCU, CNN Brasil, Poder360, LC 214/2025."""
import sys, math, subprocess, importlib.util, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("rex", f"{S}/work/render_exercito.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M); R = M.R
import sfx
BAR = R.BAR; W, H, FPS = R.W, R.H, R.FPS; CX = R.CX; clamp = R.clamp; eo = R.ease_out; ei = R.ease_in; eio = R.ease_io; bo = R.back_out
V = f"{S}/cbs"; FD = f"{S}/fontdl"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
EDIT_END = 62.75; TOTAL = EDIT_END; END_IN = TOTAL + 99   # loop: nenhuma tela final
R.FIN_IN = EDIT_END + 99; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
GOLD = R.GOLD; GOLD_L = R.GOLD_L; NAVY = R.NAVY; WHITE = (255, 255, 255); RED = (226, 52, 52); GREEN_BR = (40, 150, 90); YEL = (255, 214, 64); INK = (20, 24, 34)
def ANTON(s): return ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s)
MF = R.MF
# ---------------------------------------------------------------- legenda (texto revisado à mão)
CAPTXT = [(0.05, 2.19, "O Tribunal de Contas da União calculou:"), (2.6, 8.71, "a CBS, o imposto novo que começa em janeiro, terá alíquota de 11,3%."),
          (9.17, 12.89, "Mas isso não quer dizer que tudo vai ficar 11% mais caro."), (13.24, 13.89, "Eu te explico."),
          (14.3, 20.91, "A CBS substitui o PIS e a Cofins, dois impostos que já estão escondidos no preço de quase tudo."),
          (21.31, 24.27, "A diferença é que ela vem separada na nota fiscal."), (24.63, 25.96, "Você vai ver quanto paga."),
          (26.33, 28.34, "E acaba o imposto sobre imposto:"), (28.7, 31.81, "cada empresa desconta o que já pagou na etapa anterior."),
          (32.26, 33.13, "Por que tão alta?"), (33.51, 35.85, "O governo estimava 9,2."), (36.17, 38.43, "Mas a lei manda arrecadar o mesmo de hoje,"),
          (38.73, 40.53, "e muita coisa vai pagar menos:"), (40.84, 42.84, "a cesta básica tem alíquota zero,"), (43.09, 46.34, "saúde e educação têm 60% de desconto."),
          (46.72, 52.09, "Quem está no Cadastro Único recebe de volta a CBS do gás de cozinha, da luz e da água."), (52.47, 54.96, "Para muitos serviços, a conta pode subir."),
          (55.36, 58.66, "O Senado tem até 15 de dezembro para confirmar o número."), (59.04, 60.44, "Você acha que vai pagar mais?"), (60.78, 62.4, "Comenta aqui e me segue.")]
HOT = {"CALCULOU:", "CBS,", "11,3%.", "11%", "CARO.", "PIS", "COFINS,", "ESCONDIDOS", "SEPARADA", "NOTA", "PAGA.", "IMPOSTO:", "DESCONTA", "ALTA?", "9,2.", "MESMO",
       "MENOS:", "ZERO,", "60%", "DESCONTO.", "CADASTRO", "ÚNICO", "VOLTA", "SUBIR.", "SENADO", "15", "DEZEMBRO", "MAIS?", "AQUI", "SEGUE."}
CAPS = []
for a, b, txt_ in CAPTXT:
    ws = txt_.upper().split(); n = len(ws); k = max(1, math.ceil(n / 4)); per = math.ceil(n / k); chunks = [ws[i:i + per] for i in range(0, n, per)]
    tot = sum(len(w) + 2 for w in ws); acc = 0
    for ch in chunks:
        c0 = a + (b - a) * acc / tot; ts = []
        for w in ch: ts.append(a + (b - a - 0.06) * acc / tot); acc += len(w) + 2
        CAPS.append(dict(words=ch, ts=ts, start=c0, end=a + (b - a) * acc / tot + (0.25 if ch is chunks[-1] else 0.0), src="au" if any(w in HOT for w in ch) else "me"))
for i in range(len(CAPS) - 1): CAPS[i]["end"] = min(CAPS[i]["end"], CAPS[i + 1]["start"])
R.CAPS = CAPS; R.HOT = HOT; R._capcache.clear()
CARDS = [(0.4, 13.9, "REFORMA TRIBUTÁRIA", ["CBS: 11,3%", "CÁLCULO DO TCU"]), (13.9, 32.2, "O QUE MUDA", ["SUBSTITUI PIS E COFINS", "SEPARADA NA NOTA"]),
         (32.2, 46.6, "POR QUE 11,3%?", ["ARRECADAR O MESMO", "MUITA COISA PAGA MENOS"]), (46.6, 55.2, "NO SEU BOLSO", ["CASHBACK NO CADÚNICO", "SERVIÇOS PODEM SUBIR"]),
         (55.2, EDIT_END + 0.3, "PRÓXIMO PASSO", ["SENADO DECIDE ATÉ 15/12"])]
CAP_Y, CARD_Y = 1430, 1712
yy_, xx_ = np.mgrid[0:H, 0:W].astype(np.float32)
OCEAN = (np.array([6, 22, 44], np.float32) + np.array([10, 30, 56], np.float32) * np.clip(1 - np.sqrt(((xx_ - W / 2) / W) ** 2 + ((yy_ - 700) / H) ** 2) * 1.6, 0, 1)[..., None])
OCEAN[::60, :] += 5; OCEAN[:, ::60] += 5
OCEAN = np.clip(OCEAN, 0, 255).astype(np.uint8); del yy_, xx_
GREY = (120, 132, 156)
# ---------------------------------------------------------------- elementos
_emo = {}
def emoji(ch, size):
    key = (ch, size)
    if key not in _emo:
        f = ImageFont.truetype(EMOJI, 109); im = Image.new("RGBA", (180, 160), (0, 0, 0, 0)); ImageDraw.Draw(im).text((8, 8), ch, font=f, embedded_color=True)
        bb = im.getbbox(); im = im.crop(bb) if bb else im; sc = size / max(im.size); _emo[key] = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    return _emo[key]
_tx = {}
def txt(t_, f, col, stroke=0, scol=(0, 0, 0)):
    key = (t_, f.path, f.size, col, stroke)
    if key not in _tx:
        bb = f.getbbox(t_); im = Image.new("RGBA", (bb[2] - bb[0] + 16 + 2 * stroke, bb[3] - bb[1] + 16 + 2 * stroke), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((8 - bb[0] + stroke, 8 - bb[1] + stroke), t_, font=f, fill=col + (255,), stroke_width=stroke, stroke_fill=scol + (255,)); _tx[key] = im
    return _tx[key]
def put(fr, im, cx, cy, al=1.0, sc=1.0, rot=0):
    if al <= 0.01: return
    if abs(sc - 1) > 0.004: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
    if rot: im = im.rotate(rot, Image.BICUBIC, expand=True)
    fr.alpha_composite(R.fade(im, al), (int(cx - im.width / 2), int(cy - im.height / 2)))
def env(t, a, b, fi=0.3, fo=0.25): return clamp((t - a) / fi) * clamp((b - t) / fo)
def dashed(d, pts, col, w, dash=22, gap=14):
    acc = 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        L = math.hypot(x1 - x0, y1 - y0)
        if L < 1e-3: continue
        p = 0.0
        while p < L:
            on = (acc + p) % (dash + gap) < dash; q = min(L, p + 4)
            if on: d.line((x0 + (x1 - x0) * p / L, y0 + (y1 - y0) * p / L, x0 + (x1 - x0) * q / L, y0 + (y1 - y0) * q / L), fill=col, width=w)
            p = q
        acc += L
def path(a, b, g, bend=0.18, n=40):
    a, b = np.array(a), np.array(b); m = (a + b) / 2; nrm = np.array([-(b - a)[1], (b - a)[0]]) * bend
    pts = [tuple((1 - u) ** 2 * a + 2 * (1 - u) * u * (m + nrm) + u * u * b) for u in np.linspace(0, 1, n)]
    k = max(2, int(n * clamp(g))); return pts[:k]
def pin(fr, x, y, label, col, al, sub=None, dy=-52):
    if al <= 0: return
    d = ImageDraw.Draw(fr); a = int(255 * al)
    d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=col + (a,), outline=WHITE + (a,), width=4)
    put(fr, chipimg(label, col, 30), x, y + dy, al)
    if sub: put(fr, txt(sub, MF("SemiBold", 24), WHITE, 3), x, y + 40, al)
_ch = {}
def chipimg(t_, fill, size=30, col=WHITE):
    key = (t_, fill, size, col)
    if key not in _ch:
        f = MF("ExtraBold", size); w = int(f.getlength(t_)) + 36; h = int(size * 1.7)
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=fill + (255,), outline=WHITE + (255,), width=3)
        d.text((w / 2, h / 2 + 1), t_, font=f, fill=col + (255,), anchor="mm"); _ch[key] = im
    return _ch[key]
def stamp(t_, col, size=70, rot=-10):
    f = ANTON(size); bb = f.getbbox(t_); w, h = bb[2] - bb[0] + 60, bb[3] - bb[1] + 50
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((4, 4, w - 5, h - 5), 12, fill=(255, 255, 255, 230), outline=col + (255,), width=9); d.text((30 - bb[0], 25 - bb[1]), t_, font=f, fill=col + (255,))
    return im.rotate(rot, Image.BICUBIC, expand=True)
def title(fr, t, a, b, s, sub=None, y=360):
    k = env(t, a, b)
    if k <= 0: return 0
    put(fr, txt(s, ANTON(92), WHITE, 6, NAVY), CX, y, k, 0.85 + 0.15 * bo((t - a) / 0.4))
    if sub: put(fr, txt(sub, MF("SemiBold", 28), (200, 210, 230), 3), CX, y + 78, k)
    return k
def hbar(fr, t, ta, y, lab, val, vmax, col, vtxt, al=1.0, L=560, x0=190):
    if t < ta: return
    g = eo((t - ta) / 0.9); kk = al * clamp((t - ta) / 0.25); d = ImageDraw.Draw(fr)
    li = txt(lab, MF("ExtraBold", 34), WHITE, 3); put(fr, li, x0 + li.width / 2, y - 52, kk)
    w = max(24, int(L * val / vmax * g)); d.rounded_rectangle((x0, y - 28, x0 + w, y + 28), 28, fill=col + (int(255 * kk),))
    im = txt(vtxt, ANTON(52), WHITE, 5, NAVY); put(fr, im, x0 + w + 20 + im.width / 2, y, kk)
# ---------------------------------------------------------------- cenas
PAPER = (250, 248, 240); INKP = (24, 28, 36)
def receipt(t, t_cbs, t_hi):
    """nota fiscal de exemplo (itens fora da cesta básica); a linha da CBS entra em t_cbs"""
    w, h = 560, 600; im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    zig = [(x, h - 18 + (9 if (x // 18) % 2 else 0)) for x in range(0, w + 1, 18)]
    d.polygon([(0, 0), (w, 0)] + [(w, h - 18)] + zig[::-1] + [(0, h - 18)], fill=PAPER + (255,))
    f = MF("ExtraBold", 30); fs = MF("SemiBold", 26); y = 40
    d.text((w / 2, y), "NOTA FISCAL", font=MF("ExtraBold", 36), fill=INKP + (255,), anchor="mm"); y += 40
    d.text((w / 2, y), "exemplo · a partir de 2027", font=fs, fill=(110, 116, 128, 255), anchor="mm"); y += 40
    for x in range(30, w - 30, 16): d.line((x, y, x + 8, y), fill=(170, 170, 170, 255), width=2)
    y += 30
    for a, b in (("SABÃO EM PÓ", "R$ 20,00"), ("CHOCOLATE", "R$ 10,00")): d.text((36, y), a, font=f, fill=INKP + (255,)); d.text((w - 36, y), b, font=f, fill=INKP + (255,), anchor="ra"); y += 52
    d.text((36, y), "SUBTOTAL", font=fs, fill=(110, 116, 128, 255)); d.text((w - 36, y), "R$ 30,00", font=fs, fill=(110, 116, 128, 255), anchor="ra"); y += 56
    if t >= t_cbs:
        g = eo((t - t_cbs) / 0.35); hl = t >= t_hi
        d.rounded_rectangle((24, y - 10, w - 24, y + 50), 12, fill=(GOLD if hl else (230, 226, 214)) + (int(255 * g),))
        d.text((40, y), "CBS 11,3%", font=f, fill=INKP + (int(255 * g),)); d.text((w - 40, y), "R$ 3,39", font=f, fill=INKP + (int(255 * g),), anchor="ra")
    y += 80
    d.text((36, y), "TOTAL", font=MF("ExtraBold", 38), fill=INKP + (255,)); d.text((w - 36, y), "R$ 33,39" if t >= t_cbs else "R$ 30,00", font=MF("ExtraBold", 38), fill=INKP + (255,), anchor="ra")
    return im
def box(lab, sub, col, w=200, h=150):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.rounded_rectangle((0, 0, w - 1, h - 1), 22, fill=(12, 30, 60, 240), outline=col + (255,), width=4)
    d.text((w / 2, 52), lab, font=MF("ExtraBold", 30), fill=WHITE + (255,), anchor="mm"); d.text((w / 2, 104), sub, font=MF("SemiBold", 22), fill=(200, 210, 230, 255), anchor="mm"); return im
def counter_txt(fr, t, ta, tb, v1, fmt, cy, col, size=130, x=None):
    if t < ta: return
    v = v1 * eio((t - ta) / max(0.01, tb - ta)); put(fr, txt(fmt(v), ANTON(size), col, 8, NAVY), CX if x is None else x, cy, 1, 1 + 0.04 * (1 - eo((t - ta) / 0.3)))
def overlays(fr, t):
    # 0-13.9: abertura
    k = env(t, 0.0, 14.0, 0.2)
    if k > 0:
        put(fr, chipimg("REFORMA TRIBUTÁRIA", GOLD, 36, NAVY), CX, 290, k, 0.8 + 0.2 * bo(t / 0.4))
        put(fr, txt("CBS", ANTON(120), WHITE, 7, NAVY), CX, 420, k, 0.85 + 0.15 * bo((t - 0.2) / 0.4))
        counter_txt(fr, t, 5.6, 7.6, 11.3, lambda v: f"{v:.1f}%".replace(".", ","), 620, GOLD_L, 230)
        if t < 5.6: put(fr, txt("?", ANTON(230), GOLD_L, 8, NAVY), CX, 620, k)
        if t > 0.6: put(fr, stamp("CÁLCULO DO TCU", RED, 52, -6), CX, 830, env(t, 0.6, 14.0), 0.6 + 0.4 * bo(clamp((t - 0.6) / 0.25), 2.2))
        if t > 9.2:
            put(fr, txt("NÃO É TUDO 11%", ANTON(80), WHITE, 6, NAVY), CX, 980, env(t, 9.2, 14.0), 0.8 + 0.2 * bo((t - 9.2) / 0.35))
            put(fr, txt("MAIS CARO", ANTON(80), WHITE, 6, NAVY), CX, 1075, env(t, 9.4, 14.0))
        if t > 13.2: put(fr, chipimg("EU TE EXPLICO", NAVY, 40), CX, 1200, env(t, 13.2, 14.0), 0.7 + 0.3 * bo((t - 13.2) / 0.3))
    # 14.0-21.3: substitui PIS e Cofins
    k = env(t, 14.0, 21.35)
    if k > 0:
        put(fr, txt("O QUE ELA SUBSTITUI", ANTON(84), WHITE, 6, NAVY), CX, 300, k, 0.85 + 0.15 * bo((t - 14.0) / 0.4))
        for i, (lab, ta) in enumerate([("PIS", 15.5), ("COFINS", 16.3)]):
            if t > ta: put(fr, chipimg(lab, (80, 92, 120), 60), CX + (i * 2 - 1) * 170, 520, env(t, ta, 21.35), 0.6 + 0.4 * bo((t - ta) / 0.35, 2))
        if t > 17.6: put(fr, emoji("🙈", 120), CX, 700, env(t, 17.6, 21.35), 0.6 + 0.4 * bo((t - 17.6) / 0.35)); put(fr, txt("escondidos no preço de quase tudo", MF("SemiBold", 30), (200, 210, 230), 3), CX, 820, env(t, 18.2, 21.35))
        if t > 19.3:
            put(fr, txt("↓", ANTON(120), GOLD_L, 6, NAVY), CX, 960, env(t, 19.3, 21.35)); put(fr, chipimg("CBS", GOLD, 70, NAVY), CX, 1110, env(t, 19.5, 21.35), 0.6 + 0.4 * bo((t - 19.5) / 0.35, 2))
    # 21.3-26.3: nota fiscal
    k = env(t, 21.35, 26.35)
    if k > 0:
        put(fr, txt("SEPARADA NA NOTA", ANTON(88), WHITE, 6, NAVY), CX, 300, k, 0.85 + 0.15 * bo((t - 21.35) / 0.4))
        put(fr, receipt(t, 22.4, 24.6), CX, 720, k, 0.9 + 0.1 * eo((t - 21.35) / 0.4), -2)
        if t > 24.6: put(fr, chipimg("VOCÊ VÊ QUANTO PAGA", (40, 150, 90), 40), CX, 1100, env(t, 24.6, 26.35), 0.7 + 0.3 * bo((t - 24.6) / 0.3))
    # 26.3-32.2: fim da cascata
    k = env(t, 26.35, 32.25)
    if k > 0:
        put(fr, txt("FIM DO IMPOSTO", ANTON(90), WHITE, 6, NAVY), CX, 300, k, 0.85 + 0.15 * bo((t - 26.35) / 0.4)); put(fr, txt("SOBRE IMPOSTO", ANTON(90), GOLD_L, 6, NAVY), CX, 410, k)
        for i, (lab, sub, ta) in enumerate([("FARINHA", "moinho", 28.7), ("PÃO", "padaria", 29.6), ("VOCÊ", "consumidor", 30.5)]):
            if t < ta: continue
            x = CX - 230 + i * 230; put(fr, box(lab, sub, GOLD), x, 640, env(t, ta, 32.25), 0.6 + 0.4 * bo((t - ta) / 0.35, 2))
            if i < 2 and t > ta + 0.4: put(fr, txt("→", ANTON(70), GOLD_L, 4, NAVY), x + 115, 640, env(t, ta + 0.4, 32.25))
        if t > 29.6: put(fr, chipimg("DESCONTA O QUE JÁ FOI PAGO", (40, 150, 90), 36), CX, 820, env(t, 29.6, 32.25), 0.7 + 0.3 * bo((t - 29.6) / 0.3))
        if t > 30.5: put(fr, txt("cada etapa paga só sobre o que acrescentou", MF("SemiBold", 28), (200, 210, 230), 3), CX, 910, env(t, 30.5, 32.25))
    # 32.2-38.7: por que tão alta
    k = env(t, 32.25, 38.75)
    if k > 0:
        put(fr, txt("POR QUE TÃO ALTA?", ANTON(96), WHITE, 7, NAVY), CX, 300, k, 0.85 + 0.15 * bo((t - 32.25) / 0.4))
        for i, (lab, v, col, ta) in enumerate([("GOVERNO ESTIMAVA", 9.2, GREY, 33.5), ("CÁLCULO DO TCU", 11.3, GOLD, 34.6)]):
            if t < ta: continue
            y = 500 + i * 170; g = eo((t - ta) / 0.7); d = ImageDraw.Draw(fr); x0 = CX - 300; L = int(460 * v / 11.3 * g) + 20
            put(fr, txt(lab, MF("ExtraBold", 32), WHITE, 3), x0 + txt(lab, MF("ExtraBold", 32), WHITE, 3).width / 2, y - 55, env(t, ta, 38.75))
            d.rounded_rectangle((x0, y - 28, x0 + L, y + 28), 28, fill=col + (int(255 * k),)); put(fr, txt(f"{v:.1f}%".replace(".", ","), ANTON(60), WHITE, 5, NAVY), x0 + L + 80, y, env(t, ta, 38.75))
        if t > 36.2: put(fr, emoji("⚖️", 110), CX, 900, env(t, 36.2, 38.75), 0.6 + 0.4 * bo((t - 36.2) / 0.35)); put(fr, chipimg("A LEI: ARRECADAR O MESMO DE HOJE", NAVY, 34), CX, 1030, env(t, 36.3, 38.75))
    # 38.7-46.7: quem paga menos
    k = env(t, 38.75, 46.7)
    if k > 0:
        put(fr, txt("MUITA COISA", ANTON(96), WHITE, 7, NAVY), CX, 300, k, 0.85 + 0.15 * bo((t - 38.75) / 0.4)); put(fr, txt("PAGA MENOS", ANTON(96), (60, 200, 120), 7, NAVY), CX, 410, k)
        for i, (em, lab, val, ta) in enumerate([("🛒", "CESTA BÁSICA", "0%", 40.84), ("🩺", "SAÚDE E EDUCAÇÃO", "−60%", 43.09)]):
            if t < ta: continue
            y = 620 + i * 230; kk = env(t, ta, 46.7); sc = 0.6 + 0.4 * bo((t - ta) / 0.35, 2)
            b = Image.new("RGBA", (660, 190), (0, 0, 0, 0)); dd = ImageDraw.Draw(b); dd.rounded_rectangle((0, 0, 659, 189), 28, fill=(12, 30, 60, 240), outline=(60, 200, 120, 255), width=3)
            b.alpha_composite(emoji(em, 90), (30, 50)); dd.text((140, 95), lab, font=MF("ExtraBold", 30), fill=WHITE + (255,), anchor="lm"); put(fr, b, CX, y, kk, sc)
            put(fr, txt(val, ANTON(72), (60, 200, 120), 6, NAVY), CX + 245, y, kk, sc)
        if t > 43.5: put(fr, txt("a conta fica com quem não tem desconto", MF("SemiBold", 28), (200, 210, 230), 3), CX, 1100, env(t, 43.5, 46.7))
    # 46.7-52.4: cashback
    k = env(t, 46.7, 52.45)
    if k > 0:
        put(fr, chipimg("CADASTRO ÚNICO", GOLD, 44, NAVY), CX, 300, k, 0.7 + 0.3 * bo((t - 46.7) / 0.35))
        put(fr, txt("DINHEIRO DE VOLTA", ANTON(92), (60, 200, 120), 7, NAVY), CX, 420, k)
        for i, (em, lab, ta) in enumerate([("🔥", "GÁS", 49.4), ("💡", "LUZ", 50.6), ("💧", "ÁGUA", 51.3)]):
            if t < ta: continue
            x = CX - 220 + i * 220; kk = env(t, ta, 52.45); put(fr, emoji(em, 120), x, 640, kk, 0.5 + 0.5 * bo((t - ta) / 0.35, 2.2)); put(fr, txt(lab, ANTON(64), WHITE, 5, NAVY), x, 780, kk)
        if t > 47.6: put(fr, txt("a CBS paga nessas contas volta para a família", MF("SemiBold", 28), (200, 210, 230), 3), CX, 900, env(t, 47.6, 52.45))
    # 52.4-55.3: serviços
    k = env(t, 52.45, 55.3)
    if k > 0:
        put(fr, txt("SERVIÇOS", ANTON(120), WHITE, 7, NAVY), CX, 360, k, 0.85 + 0.15 * bo((t - 52.45) / 0.4))
        put(fr, emoji("📈", 170), CX, 600, k, 0.6 + 0.4 * bo((t - 52.6) / 0.4)); put(fr, stamp("PODE SUBIR", RED, 70, -6), CX, 830, k, 0.6 + 0.4 * bo(clamp((t - 53.2) / 0.25), 2.2))
        put(fr, txt("compram pouco, então têm pouco para descontar", MF("SemiBold", 28), (200, 210, 230), 3), CX, 960, env(t, 53.4, 55.3))
    # 55.3-59.0: Senado
    k = env(t, 55.3, 59.05)
    if k > 0:
        put(fr, emoji("🏛️", 150), CX, 380, k, 0.6 + 0.4 * bo((t - 55.4) / 0.4)); put(fr, txt("SENADO DECIDE", ANTON(100), WHITE, 7, NAVY), CX, 560, k)
        put(fr, txt("ATÉ 15/12", ANTON(140), GOLD_L, 8, NAVY), CX, 720, k, 0.8 + 0.2 * bo((t - 56.5) / 0.35) if t > 56.5 else 0.8)
        put(fr, txt("se não votar, vale o cálculo do TCU", MF("SemiBold", 28), (200, 210, 230), 3), CX, 850, env(t, 57.2, 59.05))
    # 59.0-fim: pergunta + CTA (sem tela final)
    k = env(t, 59.05, EDIT_END + 1, 0.3, 0.01)
    if k > 0:
        put(fr, txt("VOCÊ VAI", ANTON(120), WHITE, 7, NAVY), CX, 460, k, 0.85 + 0.15 * bo((t - 59.05) / 0.4)); put(fr, txt("PAGAR MAIS?", ANTON(130), GOLD_L, 7, NAVY), CX, 620, k)
        if t > 60.7: put(fr, chipimg("COMENTA AQUI", RED, 50), CX, 820, k, (0.6 + 0.4 * bo((t - 60.7) / 0.35, 2.2)) * (1 + 0.03 * math.sin(t * 6)))
        if t > 61.5: put(fr, chipimg("SIGA PARA MAIS", GOLD, 46, NAVY), CX, 950, k, 0.6 + 0.4 * bo((t - 61.5) / 0.35, 2.2))
    if 0.5 < t < EDIT_END: R.credit(fr, "Fontes: TCU, CNN Brasil, Poder360, LC 214/2025", W - 30, 168, clamp((t - 0.5) / 0.4))
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); fr = Image.fromarray(OCEAN).convert("RGBA")
    overlays(fr, tt)
    g = np.zeros((520, W, 4), np.uint8); g[..., :3] = (3, 10, 22); g[..., 3] = np.linspace(0, 210, 520)[:, None].astype(np.uint8); fr.alpha_composite(Image.fromarray(g), (0, H - 520))
    M.caption(fr, tt, CAP_Y, 54)
    for a_, b_, kick, lines in CARDS:
        kc = clamp((tt - a_) / 0.4) * (1 - clamp((tt - (b_ - 0.3)) / 0.3))
        if kc > 0: BAR.lower_card(fr, kick, lines, CARD_Y, kc, fs=40)
    cta = clamp((t - 60.7) / 0.4) if t > 60.7 else 0.0
    BAR.draw_bar(fr, clamp(t / TOTAL), "canal", eo((t - 0.2) / 0.6), cta, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(fr, t)
    return fr.convert("RGB")
def capa(out, var="A"):
    fr = Image.fromarray(OCEAN).convert("RGBA")
    if var == "A":
        put(fr, chipimg("REFORMA TRIBUTÁRIA", GOLD, 40, NAVY), CX, 250)
        put(fr, txt("CBS DE 11,3%", ANTON(130), GOLD_L, 8, NAVY), CX, 400); put(fr, txt("O QUE MUDA NO", ANTON(90), WHITE, 6, NAVY), CX, 540); put(fr, txt("SEU BOLSO", ANTON(110), WHITE, 7, NAVY), CX, 650)
        put(fr, receipt(99, 0, 0), CX, 1030, 1, 0.85, -4); put(fr, chipimg("COMEÇA EM JANEIRO", RED, 40), CX, 1360)
    else:
        put(fr, txt("11,3%", ANTON(300), GOLD_L, 10, NAVY), CX, 430); put(fr, chipimg("IMPOSTO NOVO · CBS", GOLD, 44, NAVY), CX, 640)
        put(fr, txt("VAI FICAR TUDO", ANTON(110), WHITE, 7, NAVY), CX, 820); put(fr, txt("MAIS CARO?", ANTON(140), RED, 8, NAVY), CX, 980)
        put(fr, chipimg("EU TE EXPLICO EM 1 MINUTO", NAVY, 40), CX, 1180)
    BAR.draw_bar(fr, 0.0, "canal"); fr.alpha_composite(R.top, (R.HDX, 0)); fr.convert("RGB").save(out, quality=95)
def audio(vout):
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{V}/vo.mp3", "-ar", "48000", "-ac", "2", f"{V}/vo48.wav"], check=True)
    vo = R.readw(f"{V}/vo48.wav"); vt = np.zeros((n, 2), np.float32); vt[:min(len(vo), n)] = vo[:n]
    bed = R.readw(f"{S}/v49/bed.wav"); xf = int(1.5 * SR); loop = bed.copy()
    while len(loop) < n:
        r = np.linspace(0, 1, xf)[:, None]; loop[-xf:] = loop[-xf:] * (1 - r) + bed[:xf] * r; loop = np.concatenate([loop, bed[xf:]])
    tl = np.arange(n) / SR; gain = 0.09 * np.clip(tl / 0.3, 0, 1) * np.clip((TOTAL - tl) / 0.5, 0, 1)
    R.writew(f"{V}/voice.wav", vt); R.writew(f"{V}/song.wav", loop[:n] * gain[:, None])
    def pop():
        tt = np.arange(int(0.12 * SR)) / SR; y = np.sin(2 * np.pi * (500 + 900 * tt / 0.12) * tt) * np.exp(-tt / 0.03); return np.stack([y, y], 1)
    ev = [(a - 0.15, sfx.whoosh(0.5), 0.15) for a in (14.0, 21.35, 26.35, 32.25, 38.75, 46.7, 52.45, 55.3, 59.05)]
    ev += [(x, pop(), 0.3) for x in (9.2, 13.2, 15.5, 16.3, 19.5, 22.4, 24.6, 28.7, 29.6, 30.5, 33.5, 34.6, 40.84, 43.09, 49.4, 50.6, 51.3, 60.7, 61.5)]
    ev += [(x, sfx.thud(0.4), 0.28) for x in (0.6, 7.6, 53.2)]
    sfx.build(ev, TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=70,acompressor=threshold=0.1:ratio=2.2:attack=8:release=200:makeup=1.4,asplit=2[vox][k2];[2:a]volume=0.9[sf];[3:a]volume=1.0[sg];"
                    "[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=400[sgd];"
                    f"[vox][sf][sgd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
def main():
    if MODE == "lib": return
    if MODE.startswith("capa"): capa(OUTFILE, MODE.split(":")[1] if ":" in MODE else "A"); return
    if MODE.startswith("one:"): frame_at(float(MODE[4:])).save(OUTFILE, quality=92); return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(x).resize((360, 640), Image.LANCZOS) for x in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    NF = int(round(TOTAL * FPS))
    if MODE.startswith("part"):
        i, nparts = map(int, MODE.split(":")[1:]); a, b = NF * i // nparts, NF * (i + 1) // nparts
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", OUTFILE], stdin=subprocess.PIPE)
        for k in range(a, b): enc.stdin.write(frame_at(k / FPS).tobytes())
        enc.stdin.close(); enc.wait(); print("part done", i); return
    if MODE == "mux": audio(f"{V}/video.mp4"); print("done"); return
main()
