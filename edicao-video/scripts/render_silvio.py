"""A história do Silvio Santos, horizontal 16:9 (1920x1080), ~3 min 20 s, narração do ElevenLabs (voz do Eliezio). Gancho, 8 capítulos
e fecho; antes de cada capítulo a voz pausa 1 s para o cartão "CAPÍTULO X". Linha do tempo 1930–2024 embaixo, legenda em 2 linhas,
motion graphics marinho e dourado (sem trechos de TV). Fatos conferidos: Exército e barca, Rádio Nacional 1954, estreia 02/06/1963
na TV Paulista, SBT 1981, candidatura barrada pelo TSE em 1989, sequestro em 2001, banco em 2010, morte em 17/08/2024 aos 93.

Uso: python3 render_silvio.py SCRATCH SAIDA [frames:t1,t2 | one:t | part:i:n | mux | capa:A|B]
"""
import sys, os, math, json, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "frames:5"
sys.path.insert(0, f"{S}/work")
import sfx
V = f"{S}/silvio"; FD = f"{S}/fontdl"; EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H, FPS = 1920, 1080, 30
NAVY = (8, 20, 44); NAVY2 = (16, 38, 78); GOLD = (214, 182, 116); GOLD_L = (245, 226, 176); WHITE = (255, 255, 255); MUTED = (176, 190, 214)
RED = (214, 52, 52); GREEN = (46, 170, 100)
def MF(w, s): return ImageFont.truetype(f"{FD}/Montserrat-{w}.ttf", s)
def ANTON(s): return ImageFont.truetype(f"{FD}/Anton-Regular.ttf", s)
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def eo(x): x = clamp(x); return 1 - (1 - x) ** 3
def eio(x): x = clamp(x); return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2
def bo(x, s=1.7): x = clamp(x) - 1; return 1 + (s + 1) * x ** 3 + s * x ** 2

# ---------------------------------------------------------------- tempo: a voz pausa PAUSE s antes de cada capítulo
CH = [(17.4, "CAPÍTULO 1", "O MENINO DA LAPA", "1930"), (41.0, "CAPÍTULO 2", "A VOZ", "1948"), (66.1, "CAPÍTULO 3", "O BAÚ", "ANOS 50"),
      (85.8, "CAPÍTULO 4", "O DOMINGO", "1963"), (105.5, "CAPÍTULO 5", "A TV", "1981"), (116.95, "CAPÍTULO 6", "QUASE PRESIDENTE", "1989"),
      (138.95, "CAPÍTULO 7", "AS PROVAS", "2001"), (160.55, "CAPÍTULO 8", "O ADEUS", "2024"), (173.55, "", "O QUE FICA", "")]
PAUSE = 1.0; VO_RAW = 190.0
def f(t): return t + PAUSE * sum(1 for c in CH if c[0] <= t)
TOTAL = f(VO_RAW) + 0.4
YEAR_AT = [(0, 1930), (17.4, 1930), (41.0, 1948), (60.1, 1954), (66.1, 1958), (85.8, 1963), (105.5, 1981), (116.95, 1989), (141.2, 2001), (149.3, 2010), (160.55, 2024)]

# ---------------------------------------------------------------- legenda (texto revisado à mão, tempos da fala original)
CAP = [(0.0, 2.94, "Ele começou vendendo na rua, ainda adolescente."), (3.42, 9.34, "Morreu aos 93 anos como dono de uma rede de televisão e de um império com o próprio nome."),
       (9.81, 11.67, "E quase foi presidente do Brasil."), (12.3, 14.6, "Essa é a história de Senor Abravanel."), (15.07, 17.16, "Você conhece como Silvio Santos."),
       (17.62, 22.25, "Senor nasceu em dezembro de 1930, na Lapa, no Rio de Janeiro."), (22.74, 25.46, "Filho de imigrantes judeus, cresceu sem luxo."),
       (25.93, 28.88, "Ainda adolescente, virou camelô nas ruas do centro."), (29.23, 33.6, "As biografias contam que ele vendia capinhas de plástico para título de eleitor,"),
       (33.97, 35.85, "e que tinha um truque: a voz."), (36.16, 39.51, "Enquanto os outros esperavam o cliente, ele chamava."), (39.86, 40.76, "E vendia mais."),
       (41.18, 44.9, "Aos 18 anos, entrou para a escola de paraquedistas do Exército."), (45.39, 48.04, "Nas folgas, trabalhava numa rádio em Niterói."),
       (48.61, 51.47, "Voltando para casa na última barca, teve uma ideia:"), (52.04, 55.16, "por que não colocar música e anúncios durante a travessia?"),
       (55.71, 59.73, "Convenceu a empresa, e a barca virou o primeiro grande negócio dele."), (60.12, 65.73, "Em 1954, assinou contrato como locutor da Rádio Nacional, em São Paulo."),
       (66.29, 71.15, "Lá, trabalhando com o radialista Manoel de Nóbrega, assumiu um negócio que ia mal:"), (71.56, 72.95, "o Baú da Felicidade."),
       (73.31, 78.58, "As pessoas pagavam um carnê todo mês e, no fim, recebiam um baú de presentes."), (79.04, 81.96, "Silvio transformou o carnê numa máquina de vendas."),
       (82.39, 85.63, "E percebeu que, para vender mais, precisava de um palco."), (86.01, 92.64, "Em 2 de junho de 1963, estreou o Programa Silvio Santos, na TV Paulista."),
       (93.19, 96.45, "Ele alugava o horário de domingo e vendia o Baú no ar."), (96.95, 101.28, "Deu tão certo que, durante décadas, o domingo do brasileiro teve dono."),
       (101.68, 105.17, "Mas Silvio queria mais do que um horário. Queria uma emissora."), (105.68, 107.81, "Depois de anos tentando, conseguiu."),
       (108.35, 112.11, "Em 1981, entrou no ar o SBT."), (112.61, 116.75, "O camelô da Lapa agora era dono de uma rede nacional de televisão."),
       (117.08, 122.85, "Em 1989, veio a primeira eleição direta para presidente depois da ditadura."), (123.37, 126.8, "A poucos dias da votação, Silvio se lançou candidato."),
       (127.27, 130.81, "Apareceu forte nas pesquisas e assustou os favoritos."), (131.31, 136.66, "Mas o Tribunal Superior Eleitoral barrou a candidatura, por problemas no registro do partido."),
       (137.16, 138.74, "Ele nunca chegou a disputar."), (139.1, 140.71, "A vida também cobrou caro."), (141.16, 144.2, "Em 2001, a filha Patrícia foi sequestrada."),
       (144.67, 148.72, "Dias depois, o próprio Silvio foi feito refém dentro de casa."), (149.26, 154.62, "Em 2010, um rombo bilionário descoberto no banco do grupo quase levou tudo."),
       (155.12, 160.38, "Silvio colocou o próprio patrimônio como garantia e vendeu o banco para resolver a dívida."), (160.71, 163.6, "Ele comandou o programa por quase sessenta anos."),
       (163.7, 169.37, "Em 17 de agosto de 2024, morreu em São Paulo, aos 93 anos."), (169.76, 173.26, "E o Brasil se despediu do maior comunicador da sua televisão."),
       (173.73, 178.39, "O que fica? Ele não tinha dinheiro, nem sobrenome famoso, nem padrinho."), (178.78, 183.49, "Tinha a voz, a coragem de vender e a teimosia de não desistir."),
       (183.87, 186.51, "E você, qual lembrança tem do Silvio Santos?"), (186.83, 190.0, "Comenta aqui e se inscreve no canal para a próxima história.")]

# ---------------------------------------------------------------- utilidades de desenho
_tx = {}
def txt(t_, fnt, col, stroke=0, scol=NAVY):
    k = (t_, fnt.path, fnt.size, col, stroke)
    if k not in _tx:
        bb = fnt.getbbox(t_); im = Image.new("RGBA", (bb[2] - bb[0] + 20 + 2 * stroke, bb[3] - bb[1] + 20 + 2 * stroke), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10 - bb[0] + stroke, 10 - bb[1] + stroke), t_, font=fnt, fill=col + (255,), stroke_width=stroke, stroke_fill=scol + (255,)); _tx[k] = im
    return _tx[k]
def fade(im, a):
    if a >= 0.999: return im
    im = im.copy(); im.putalpha(im.getchannel("A").point(lambda v: int(v * max(0, a)))); return im
def put(fr, im, x, y, a=1.0, sc=1.0):
    if a <= 0.01: return
    if abs(sc - 1) > 0.004: im = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.BICUBIC)
    fr.alpha_composite(fade(im, a), (int(x - im.width / 2), int(y - im.height / 2)))
_emo = {}
def emoji(ch, size):
    k = (ch, size)
    if k not in _emo:
        fnt = ImageFont.truetype(EMOJI, 109); im = Image.new("RGBA", (180, 160), (0, 0, 0, 0)); ImageDraw.Draw(im).text((8, 8), ch, font=fnt, embedded_color=True)
        bb = im.getbbox(); im = im.crop(bb) if bb else im; sc = size / max(im.size); _emo[k] = im.resize((max(1, int(im.width * sc)), max(1, int(im.height * sc))), Image.LANCZOS)
    return _emo[k]
_ch = {}
def chip(t_, fill, size=40, col=WHITE, outline=None):
    k = (t_, fill, size, col, outline)
    if k not in _ch:
        fnt = MF("ExtraBold", size); w = int(fnt.getlength(t_)) + size * 1.2; h = int(size * 1.75)
        im = Image.new("RGBA", (int(w), h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=fill + (255,), outline=(outline or fill) + (255,), width=3)
        d.text((w / 2, h / 2 + 1), t_, font=fnt, fill=col + (255,), anchor="mm"); _ch[k] = im
    return _ch[k]
def medal(ch, size=220, ring=GOLD):
    """emoji dentro de um círculo marinho com aro dourado"""
    k = ("medal", ch, size, ring)
    if k not in _ch:
        im = Image.new("RGBA", (size + 40, size + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.ellipse((20, 20, size + 20, size + 20), fill=NAVY2 + (255,), outline=ring + (255,), width=6); e = emoji(ch, int(size * 0.55))
        im.alpha_composite(e, (int(20 + size / 2 - e.width / 2), int(20 + size / 2 - e.height / 2))); _ch[k] = im
    return _ch[k]
def stamp(t_, col, size=80, rot=-8):
    fnt = ANTON(size); bb = fnt.getbbox(t_); w, h = bb[2] - bb[0] + 70, bb[3] - bb[1] + 56
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((5, 5, w - 6, h - 6), 14, fill=(255, 255, 255, 235), outline=col + (255,), width=10); d.text((35 - bb[0], 28 - bb[1]), t_, font=fnt, fill=col + (255,))
    return im.rotate(rot, Image.BICUBIC, expand=True)
def env(t, a, b, fi=0.35, fo=0.3): return clamp((t - a) / fi) * clamp((b - t) / fo)
def pop(fr, im, x, y, t, a, b, s=2.0):
    if t < a: return
    put(fr, im, x, y, env(t, a, b), 0.55 + 0.45 * bo((t - a) / 0.4, s))
def T(a): return f(a)

# ---------------------------------------------------------------- fundo
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
BGA = np.array(NAVY, np.float32) + np.array([18, 34, 66], np.float32) * np.clip(1 - np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H * 0.42) / H) ** 2) * 1.5, 0, 1)[..., None]
BGA[::64, :] += 4; BGA[:, ::64] += 4
VIG = (1 - 0.35 * np.clip(np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2) - 0.55, 0, 1) ** 1.5)[..., None].astype(np.float32)
BG = Image.fromarray(np.clip(BGA, 0, 255).astype(np.uint8)).convert("RGBA"); BGD = Image.fromarray(np.clip(BGA * 0.55, 0, 255).astype(np.uint8)).convert("RGBA")
del yy, xx, BGA
BR = json.load(open(f"{S}/v76/br.json"))
def brasil(size=520):
    k = ("br", size)
    if k in _ch: return _ch[k]
    rings = []
    for fe in BR["features"]:
        g = fe["geometry"]; polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for p in polys: rings.append(np.array(p[0], float))
    allp = np.concatenate(rings); x0, x1, y0, y1 = allp[:, 0].min(), allp[:, 0].max(), allp[:, 1].min(), allp[:, 1].max(); sc = size / max(x1 - x0, y1 - y0)
    im = Image.new("RGBA", (size + 20, size + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for r in rings: d.polygon([(10 + (x - x0) * sc, 10 + (y1 - y) * sc) for x, y in r], fill=NAVY2 + (255,), outline=GOLD + (255,))
    _ch[k] = im; return im


# ---------------------------------------------------------------- fotos reais (Wikimedia Commons; domínio público ou CC BY com crédito)
FOT = f"{V}/fotos"
PHOTOS = [  # (início, fim) na fala original, arquivo, legenda, crédito (fotos enviadas pelo Eliezio)
    (12.3, 15.0, "jovem_cor", "Senor Abravanel, jovem", "reprodução"),
    (15.07, 17.3, "sorriso_azul", "Silvio Santos", "reprodução"),
    (18.4, 25.8, "jovem_sorriso", "Silvio jovem", "reprodução"),
    (26.0, 33.6, "doc1950", "Documento de 1950", "reprodução"),
    (41.2, 48.5, "paraquedista1948", "Paraquedista do Exército, 1948", "reprodução"),
    (60.1, 66.0, "radio50", "Começo no rádio", "reprodução"),
    (66.3, 73.2, "anos50", "Os primeiros anos em São Paulo", "reprodução"),
    (82.4, 85.7, "palco70", "Precisava de um palco", "reprodução"),
    (89.4, 96.9, "tv70a", "No comando do programa", "reprodução"),
    (97.0, 101.6, "tv70b", "Anos 70", "reprodução"),
    (112.6, 116.9, "radio70", "Dono da própria emissora", "reprodução"),
    (117.2, 127.2, "colagem70", "O rosto mais conhecido da TV", "reprodução"),
    (149.3, 160.4, "velho_paleto", "Silvio nos anos 2010", "reprodução"),
    (160.7, 166.6, "palco", "No palco do programa", "reprodução"),
    (166.7, 173.5, "sorriso_azul", "Silvio Santos · 1930–2024", "reprodução"),
]
_ph = {}
def photo_img(key):
    if key not in _ph:
        pth = f"{FOT}/{key}.jpg"
        _ph[key] = Image.open(pth).convert("RGB") if os.path.exists(pth) else None
    return _ph[key]
def photo_card(key, t, a, b, cap, cred, maxw=620, maxh=560):
    """porta-retrato com borda clara, leve giro e zoom lento (Ken Burns), legenda e crédito"""
    im = photo_img(key)
    if im is None: return None
    sc = min(maxw / im.width, maxh / im.height); w, h = int(im.width * sc), int(im.height * sc)
    z = 1.0 + 0.06 * clamp((t - a) / max(1, b - a)); cw, ch = im.width / z, im.height / z
    crop = im.crop((int((im.width - cw) / 2), int((im.height - ch) * 0.35), int((im.width + cw) / 2), int((im.height - ch) * 0.35 + ch))).resize((w, h), Image.BICUBIC)
    pad, capH = 16, 92; cwid = max(w + 2 * pad, int(MF("ExtraBold", 28).getlength(cap)) + 50); card = Image.new("RGBA", (cwid, h + pad + capH), (0, 0, 0, 0)); dd = ImageDraw.Draw(card)
    dd.rounded_rectangle((0, 0, card.width - 1, card.height - 1), 10, fill=(246, 242, 232, 255)); card.paste(crop, ((cwid - w) // 2, pad))
    dd.text((card.width / 2, h + pad + 30), cap, font=MF("ExtraBold", 28), fill=(24, 28, 36, 255), anchor="mm")
    dd.text((card.width / 2, h + pad + 66), "Foto: " + cred, font=MF("SemiBold", 18), fill=(110, 116, 128, 255), anchor="mm")
    sh = Image.new("RGBA", (card.width + 80, card.height + 80), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((40, 52, card.width + 40, card.height + 52), 14, fill=(0, 0, 0, 150))
    sh = sh.filter(ImageFilter.GaussianBlur(18)); sh.alpha_composite(card, (40, 40)); return sh
def photo_state(t):
    """(fator 0-1 de quanto a foto está na tela, dados da foto ativa)"""
    for a, b, key, cap, cred in PHOTOS:
        A, B = T(a), T(b)
        if A - 0.01 <= t <= B + 0.45 and photo_img(key) is not None:
            card = max([env(t, f(c0) - PAUSE, f(c0) + 1.3, 0.25, 0.35) for c0, *_ in CH] + [0])
            return clamp((t - A) / 0.5) * clamp((B + 0.45 - t) / 0.45) * (1 - card), (a, b, key, cap, cred)
    return 0.0, None

# ---------------------------------------------------------------- cenas (tempos da fala original via T())
CX, CY = W // 2, 470
def scenes(fr, t):
    d = ImageDraw.Draw(fr)
    # gancho
    k = env(t, 0, T(17.3), 0.2, 0.4)
    if k > 0:
        for i, (em, lab, ta) in enumerate([("🛍️", "CAMELÔ", 0.2), ("🎙️", "LOCUTOR", 3.6), ("📺", "DONO DE TV", 6.0), ("🗳️", "QUASE PRESIDENTE", 9.9)]):
            if t < ta or t > T(12.2): continue
            x = 360 + i * 400; kk = k * clamp((T(12.2) - t) / 0.4); pop(fr, medal(em, 230), x, CY - 20, t, ta, 99); put(fr, txt(lab, MF("ExtraBold", 40), GOLD_L, 3), x, CY + 160, kk * clamp((t - ta - 0.2) / 0.3))
        if t > T(12.3):
            put(fr, txt("SENOR ABRAVANEL", ANTON(130), WHITE, 6), CX, CY - 40, env(t, T(12.3), T(15.0), 0.4, 0.3), 0.9 + 0.1 * eo((t - T(12.3)) / 0.6))
        if t > T(15.0):
            put(fr, txt("SILVIO SANTOS", ANTON(190), GOLD_L, 8), CX, CY - 30, k, 0.8 + 0.2 * bo((t - T(15.0)) / 0.45))
            put(fr, txt("A HISTÓRIA DE", MF("ExtraBold", 40), MUTED, 3), CX, CY - 175, k * clamp((t - T(15.2)) / 0.3))
    # capítulos: cartão durante a pausa + 1,4 s
    for c0, lab, title, yr in CH:
        a = T(c0) - PAUSE * 0 - 1.0 + 1.0   # início da pausa = f(c0) - PAUSE
        a = f(c0) - PAUSE; kk = env(t, a, a + PAUSE + 1.3, 0.25, 0.35)
        if kk <= 0: continue
        fr.alpha_composite(fade(BGD, kk * 0.9))
        if lab: put(fr, txt(lab, MF("ExtraBold", 42), GOLD, 3), CX, CY - 130, kk, 0.9 + 0.1 * eo((t - a) / 0.4))
        put(fr, txt(title, ANTON(150), WHITE, 7), CX, CY, kk, 0.85 + 0.15 * bo((t - a) / 0.45))
        if yr: put(fr, txt(yr, ANTON(80), GOLD_L, 5), CX, CY + 140, kk * clamp((t - a - 0.2) / 0.3))
        w = int(500 * eo((t - a - 0.1) / 0.5)); d.line((CX - w / 2, CY + 85, CX + w / 2, CY + 85), fill=GOLD + (int(255 * kk),), width=4)
    # cap 1 · Lapa
    k = env(t, T(17.6), T(41.0) - PAUSE)
    if k > 0:
        if t < T(25.9):
            pop(fr, txt("1930", ANTON(200), GOLD_L, 8), CX - 330, CY - 20, t, T(18.4), T(25.9)); pop(fr, medal("📍", 200), CX + 250, CY - 60, t, T(19.9), T(25.9))
            put(fr, txt("LAPA · RIO DE JANEIRO", MF("ExtraBold", 40), WHITE, 3), CX + 250, CY + 100, env(t, T(20.3), T(25.9)))
            put(fr, txt("filho de imigrantes judeus", MF("SemiBold", 34), MUTED, 2), CX, CY + 230, env(t, T(22.8), T(25.9)))
        elif t < T(34.0):
            pop(fr, medal("🛍️", 240), CX - 380, CY - 10, t, T(25.9), T(34.0)); pop(fr, txt("CAMELÔ", ANTON(150), WHITE, 7), CX + 160, CY - 70, t, T(26.6), T(34.0))
            if t > T(29.3): put(fr, chip("capinhas para título de eleitor", NAVY2, 36, GOLD_L, GOLD), CX + 160, CY + 70, env(t, T(29.3), T(34.0))); put(fr, txt("segundo as biografias", MF("SemiBold", 28), MUTED, 2), CX + 160, CY + 150, env(t, T(29.6), T(34.0)))
        else:
            pop(fr, medal("📣", 260), CX - 300, CY - 10, t, T(34.0), T(41.0) - PAUSE)
            for i in range(3):
                r = 160 + ((t - T(35.1)) * 220 + i * 80) % 240
                if t > T(35.1): d.arc((CX - 300 - r, CY - 10 - r, CX - 300 + r, CY - 10 + r), -40, 40, fill=GOLD + (int(255 * k * (1 - (r - 160) / 240)),), width=6)
            pop(fr, txt("O TRUQUE: A VOZ", ANTON(110), GOLD_L, 6), CX + 230, CY - 50, t, T(35.1), T(41.0) - PAUSE)
            if t > T(38.8): put(fr, txt("ele chamava o cliente", MF("ExtraBold", 40), WHITE, 3), CX + 230, CY + 70, env(t, T(38.8), T(41.0) - PAUSE))
            if t > T(39.9): put(fr, chip("E VENDIA MAIS", GREEN, 40), CX + 230, CY + 160, env(t, T(39.9), T(41.0) - PAUSE), 0.6 + 0.4 * bo((t - T(39.9)) / 0.3))
    # cap 2 · a voz
    k = env(t, T(41.2), T(66.1) - PAUSE)
    if k > 0:
        if t < T(48.5):
            pop(fr, medal("🪂", 220), CX - 330, CY - 20, t, T(41.3), T(48.5)); put(fr, txt("PARAQUEDISTA · 18 ANOS", MF("ExtraBold", 38), WHITE, 3), CX - 330, CY + 150, env(t, T(42.5), T(48.5)))
            pop(fr, medal("📻", 220), CX + 330, CY - 20, t, T(45.4), T(48.5)); put(fr, txt("RÁDIO EM NITERÓI", MF("ExtraBold", 38), WHITE, 3), CX + 330, CY + 150, env(t, T(45.8), T(48.5)))
        elif t < T(60.0):
            kk = env(t, T(48.6), T(60.0)); y0 = CY + 80
            for i in range(9): d.arc((200 + i * 170, y0 - 20, 370 + i * 170, y0 + 20), 0, 180, fill=(70, 120, 190, int(255 * kk)), width=5)
            put(fr, txt("NITERÓI", MF("ExtraBold", 34), MUTED, 2), 260, y0 + 70, kk); put(fr, txt("RIO", MF("ExtraBold", 34), MUTED, 2), W - 260, y0 + 70, kk)
            bx = 300 + (W - 600) * eio((t - T(48.8)) / 9.0); put(fr, emoji("⛴️", 150), bx, y0 - 60, kk)
            if t > T(52.0):
                for j in range(3):
                    nt = (t * 0.9 + j / 3) % 1; put(fr, emoji("🎵", 60), bx - 40 + j * 40, y0 - 140 - 90 * nt, kk * (1 - nt))
                pop(fr, txt("MÚSICA E ANÚNCIOS NA TRAVESSIA", ANTON(80), GOLD_L, 5), CX, CY - 230, t, T(52.0), T(60.0))
            if t > T(57.1): put(fr, chip("1º GRANDE NEGÓCIO", GREEN, 42), CX, CY - 120, env(t, T(57.1), T(60.0)), 0.6 + 0.4 * bo((t - T(57.1)) / 0.3))
        else:
            pop(fr, txt("1954", ANTON(200), GOLD_L, 8), CX - 330, CY - 20, t, T(60.1), T(66.1) - PAUSE); pop(fr, medal("🎙️", 220), CX + 260, CY - 60, t, T(61.0), T(66.1) - PAUSE)
            put(fr, txt("RÁDIO NACIONAL · SÃO PAULO", MF("ExtraBold", 40), WHITE, 3), CX + 260, CY + 110, env(t, T(62.0), T(66.1) - PAUSE))
    # cap 3 · o Baú
    k = env(t, T(66.3), T(85.8) - PAUSE)
    if k > 0:
        if t < T(73.2):
            pop(fr, chip("com o radialista Manoel de Nóbrega", NAVY2, 40, WHITE, GOLD), CX, CY - 210, t, T(66.8), T(73.2))
            if t > T(69.5): put(fr, txt("um negócio que ia mal…", MF("ExtraBold", 46), MUTED, 3), CX, CY - 90, env(t, T(69.5), T(73.2)))
            if t > T(71.6): pop(fr, txt("BAÚ DA FELICIDADE", ANTON(140), GOLD_L, 7), CX, CY + 60, t, T(71.6), T(73.2)); put(fr, emoji("🎁", 110), CX, CY + 200, env(t, T(71.8), T(73.2)))
        elif t < T(82.3):
            kk = env(t, T(73.3), T(82.3)); put(fr, txt("CARNÊ", ANTON(90), WHITE, 5), CX, CY - 250, kk)
            for i in range(12):
                x = CX - 550 + (i % 6) * 220; y = CY - 120 + (i // 6) * 170; ta = T(73.6) + i * 0.32
                b = Image.new("RGBA", (190, 140), (0, 0, 0, 0)); bd = ImageDraw.Draw(b); bd.rounded_rectangle((0, 0, 189, 139), 18, fill=NAVY2 + (240,), outline=GOLD + (255,), width=3)
                bd.text((95, 34), f"MÊS {i + 1}", font=MF("ExtraBold", 26), fill=MUTED + (255,), anchor="mm")
                if t >= ta: b.alpha_composite(emoji("✅", 56), (67, 62))
                put(fr, b, x, y, kk)
            if t > T(76.8): pop(fr, medal("🎁", 230), CX + 640, CY + 170, t, T(76.8), T(82.3), 2.4)
            if t > T(79.0): put(fr, chip("MÁQUINA DE VENDAS", GREEN, 44), CX, CY + 250, env(t, T(79.0), T(82.3)), 0.6 + 0.4 * bo((t - T(79.0)) / 0.3))
        else:
            pop(fr, medal("🎤", 260), CX - 260, CY - 10, t, T(82.4), T(85.8) - PAUSE); pop(fr, txt("PRECISAVA DE UM PALCO", ANTON(100), GOLD_L, 6), CX + 240, CY - 10, t, T(84.4), T(85.8) - PAUSE)
    # cap 4 · o domingo
    k = env(t, T(86.0), T(105.5) - PAUSE)
    if k > 0:
        if t < T(96.9):
            pop(fr, txt("2 DE JUNHO DE 1963", ANTON(110), GOLD_L, 6), CX, CY - 220, t, T(86.2), T(96.9))
            tv = Image.new("RGBA", (620, 420), (0, 0, 0, 0)); td = ImageDraw.Draw(tv); td.rounded_rectangle((0, 0, 619, 379), 40, fill=(40, 34, 30, 255), outline=GOLD + (255,), width=6)
            glow = clamp((t - T(89.4)) / 0.6); td.rounded_rectangle((40, 40, 470, 340), 30, fill=(int(30 + 200 * glow), int(40 + 180 * glow), int(60 + 120 * glow), 255))
            for i in range(2): td.ellipse((510, 90 + i * 110, 580, 160 + i * 110), fill=(90, 80, 70, 255))
            td.line((200, 380, 160, 420), fill=GOLD + (255,), width=8); td.line((420, 380, 460, 420), fill=GOLD + (255,), width=8)
            if glow > 0.5: td.text((255, 165), "PROGRAMA", font=MF("ExtraBold", 40), fill=NAVY + (255,), anchor="mm"); td.text((255, 225), "SILVIO SANTOS", font=MF("ExtraBold", 40), fill=NAVY + (255,), anchor="mm")
            put(fr, tv, CX - 300, CY + 60, k * clamp((t - T(88.0)) / 0.4))
            if t > T(90.5): put(fr, chip("TV PAULISTA", NAVY2, 40, WHITE, GOLD), CX + 360, CY - 40, env(t, T(90.5), T(96.9)))
            if t > T(93.2): put(fr, txt("alugava o domingo", MF("ExtraBold", 44), WHITE, 3), CX + 360, CY + 70, env(t, T(93.2), T(96.9))); put(fr, txt("e vendia o Baú no ar", MF("ExtraBold", 44), GOLD_L, 3), CX + 360, CY + 140, env(t, T(94.6), T(96.9)))
        else:
            kk = env(t, T(97.0), T(105.5) - PAUSE)
            if t < T(101.6):
                put(fr, txt("DOMINGO", ANTON(90), WHITE, 5), CX, CY - 240, kk)
                for i in range(28):
                    x = CX - 600 + (i % 7) * 200; y = CY - 110 + (i // 7) * 110; on = (i % 7 == 6) and t > T(97.6) + (i // 7) * 0.4
                    d.rounded_rectangle((x - 80, y - 40, x + 80, y + 40), 14, fill=(GOLD if on else NAVY2) + (int(255 * kk),))
                    if on: put(fr, emoji("📺", 50), x, y, kk)
                put(fr, txt("O DOMINGO TEVE DONO", ANTON(80), GOLD_L, 5), CX, CY + 340, env(t, T(99.0), T(101.6)))
            else:
                pop(fr, medal("📡", 260), CX - 260, CY - 10, t, T(101.7), T(105.5) - PAUSE); pop(fr, txt("QUERIA UMA EMISSORA", ANTON(100), GOLD_L, 6), CX + 250, CY - 10, t, T(104.1), T(105.5) - PAUSE)
    # cap 5 · a TV
    k = env(t, T(105.7), T(116.95) - PAUSE)
    if k > 0:
        pop(fr, txt("1981", ANTON(220), GOLD_L, 9), CX - 420, CY - 40, t, T(108.3), T(116.95) - PAUSE)
        if t > T(110.4):
            bx, by = CX + 330, CY - 10; put(fr, brasil(560), bx, by, k)
            for i in range(4):
                r = ((t - T(110.4)) * 260 + i * 110) % 440
                d.ellipse((bx - r, by - r, bx + r, by + r), outline=GOLD_L + (int(200 * k * (1 - r / 440)),), width=4)
            put(fr, chip("SBT NO AR", GOLD, 54, NAVY), bx, by, k, 0.6 + 0.4 * bo((t - T(110.4)) / 0.35, 2.2))
        if t > T(112.6): put(fr, txt("do camelô da Lapa", MF("ExtraBold", 42), WHITE, 3), CX - 420, CY + 130, env(t, T(112.6), T(116.95) - PAUSE)); put(fr, txt("a uma rede nacional", MF("ExtraBold", 42), GOLD_L, 3), CX - 420, CY + 195, env(t, T(113.6), T(116.95) - PAUSE))
    # cap 6 · quase presidente
    k = env(t, T(117.1), T(138.95) - PAUSE)
    if k > 0:
        if t < T(127.2):
            pop(fr, txt("1989", ANTON(200), GOLD_L, 8), CX - 380, CY - 30, t, T(117.2), T(127.2)); pop(fr, medal("🗳️", 230), CX + 300, CY - 60, t, T(119.3), T(127.2))
            put(fr, txt("1ª eleição direta depois da ditadura", MF("ExtraBold", 40), WHITE, 3), CX + 300, CY + 110, env(t, T(120.0), T(127.2)))
            if t > T(125.2): put(fr, chip("SILVIO CANDIDATO", GOLD, 46, NAVY), CX, CY + 250, env(t, T(125.2), T(127.2)), 0.6 + 0.4 * bo((t - T(125.2)) / 0.3))
        else:
            kk = env(t, T(127.3), T(138.95) - PAUSE); g = eo((t - T(127.4)) / 2.5)
            d.rounded_rectangle((CX - 640, CY - 40, CX - 640 + int(700 * g), CY + 40), 40, fill=GOLD + (int(255 * kk),)); put(fr, txt("FORTE NAS PESQUISAS", MF("ExtraBold", 40), WHITE, 3), CX - 400, CY - 100, kk)
            if t > T(131.4): put(fr, stamp("BARRADO PELO TSE", RED, 96, -8), CX + 330, CY + 10, env(t, T(131.4), T(138.95) - PAUSE), 0.6 + 0.4 * bo(clamp((t - T(131.4)) / 0.25), 2.4))
            if t > T(134.8): put(fr, txt("problemas no registro do partido", MF("SemiBold", 36), MUTED, 2), CX + 330, CY + 170, env(t, T(134.8), T(138.95) - PAUSE))
            if t > T(137.2): put(fr, txt("ELE NUNCA DISPUTOU", ANTON(80), WHITE, 5), CX, CY + 290, env(t, T(137.2), T(138.95) - PAUSE))
    # cap 7 · as provas (fundo mais escuro)
    k = env(t, T(139.1), T(160.55) - PAUSE)
    if k > 0:
        fr.alpha_composite(fade(BGD, k * 0.6))
        if t < T(149.2):
            pop(fr, txt("2001", ANTON(200), GOLD_L, 8), CX - 420, CY - 30, t, T(141.2), T(149.2))
            if t > T(142.3): put(fr, txt("SEQUESTRO DA FILHA", ANTON(84), WHITE, 5), CX + 280, CY - 80, env(t, T(142.3), T(149.2)))
            if t > T(145.8): put(fr, txt("Silvio feito refém em casa", MF("ExtraBold", 42), MUTED, 3), CX + 280, CY + 40, env(t, T(145.8), T(149.2)))
        else:
            pop(fr, txt("2010", ANTON(200), GOLD_L, 8), CX - 420, CY - 30, t, T(149.3), T(160.55) - PAUSE)
            if t > T(150.5): put(fr, txt("ROMBO BILIONÁRIO NO BANCO", ANTON(76), WHITE, 5), CX + 300, CY - 100, env(t, T(150.5), T(160.55) - PAUSE))
            if t > T(155.1): put(fr, chip("patrimônio como garantia", NAVY2, 40, GOLD_L, GOLD), CX + 300, CY + 10, env(t, T(155.1), T(160.55) - PAUSE))
            if t > T(158.3): put(fr, chip("vendeu o banco para resolver a dívida", GREEN, 36), CX + 300, CY + 110, env(t, T(158.3), T(160.55) - PAUSE))
    # cap 8 · o adeus
    k = env(t, T(160.7), T(173.55) - PAUSE)
    if k > 0:
        if t < T(163.7):
            pop(fr, txt("QUASE 60 ANOS", ANTON(160), GOLD_L, 8), CX, CY - 40, t, T(160.8), T(163.7)); put(fr, txt("comandando o programa", MF("ExtraBold", 44), WHITE, 3), CX, CY + 100, env(t, T(161.4), T(163.7)))
        else:
            glow = Image.new("RGBA", (900, 900), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse((150, 150, 750, 750), fill=GOLD + (60,)); put(fr, glow.filter(ImageFilter.GaussianBlur(80)), CX, CY, k)
            pop(fr, txt("17 · 08 · 2024", ANTON(120), WHITE, 6), CX, CY - 150, t, T(163.8), T(173.55) - PAUSE)
            if t > T(166.8): put(fr, txt("93 ANOS", ANTON(110), GOLD_L, 6), CX, CY, env(t, T(166.8), T(173.55) - PAUSE))
            if t > T(169.8): put(fr, txt("o maior comunicador da TV brasileira", MF("ExtraBold", 46), WHITE, 3), CX, CY + 140, env(t, T(169.8), T(173.55) - PAUSE))
    # fecho
    k = env(t, T(173.7), TOTAL + 1, 0.35, 0.01)
    if k > 0:
        if t < T(183.8):
            for i, (lab, ta) in enumerate([("DINHEIRO", 174.8), ("SOBRENOME", 176.1), ("PADRINHO", 177.2)]):
                if t > T(ta): x = CX - 520 + i * 520; im_ = txt(lab, ANTON(70), MUTED, 4); put(fr, im_, x - 40, CY - 150, k); put(fr, emoji("❌", 64), x - 40 + im_.width / 2 + 45, CY - 150, k, 0.6 + 0.4 * bo((t - T(ta)) / 0.3))
            for i, (lab, ta) in enumerate([("A VOZ", 178.9), ("CORAGEM DE VENDER", 179.8), ("TEIMOSIA", 181.6)]):
                if t > T(ta): x = CX - 500 + i * 500; put(fr, txt(lab, ANTON(70), GOLD_L, 4), x, CY + 60, k, 0.6 + 0.4 * bo((t - T(ta)) / 0.35)); put(fr, emoji("✅", 70), x, CY + 160, k)
        else:
            put(fr, txt("E VOCÊ?", ANTON(140), WHITE, 7), CX, CY - 170, k, 0.85 + 0.15 * bo((t - T(183.9)) / 0.4))
            put(fr, txt("QUAL LEMBRANÇA TEM DO SILVIO?", ANTON(84), GOLD_L, 5), CX, CY - 20, env(t, T(184.6), 999))
            if t > T(186.8): put(fr, chip("COMENTA AQUI", RED, 50), CX - 260, CY + 140, k, (0.6 + 0.4 * bo((t - T(186.8)) / 0.35, 2.2)) * (1 + 0.03 * math.sin(t * 6)))
            if t > T(187.8): sc_ = 0.6 + 0.4 * bo((t - T(187.8)) / 0.35, 2.2); put(fr, chip("INSCREVA-SE", GOLD, 50, NAVY), CX + 280, CY + 140, k, sc_); put(fr, emoji("🔔", 70), CX + 280 + 210, CY + 140, k, sc_)

def chrome(fr, t):
    """marca do canal, capítulo atual, linha do tempo 1930-2024 e fontes"""
    d = ImageDraw.Draw(fr); a = clamp((t - 0.5) / 0.6)
    put(fr, txt("ELIEZIO SOUZA", MF("ExtraBold", 28), GOLD, 2), 160, 50, a); put(fr, txt("histórias que inspiram", MF("SemiBold", 22), MUTED, 2), 160, 84, a)
    cur = [c for c in CH if f(c[0]) - PAUSE <= t]
    if cur and cur[-1][1]: c_ = chip(f"{cur[-1][1]} · {cur[-1][2]}", NAVY2, 26, GOLD_L, GOLD); put(fr, c_, W - 60 - c_.width / 2, 60, a)
    yr = 1930
    for c0, y in YEAR_AT:
        if t >= T(c0): yr = y
    x0, x1, ty = 260, W - 260, 1038; d.line((x0, ty, x1, ty), fill=(60, 80, 120, int(255 * a)), width=4)
    for y in (1930, 1950, 1970, 1990, 2010, 2024):
        x = x0 + (x1 - x0) * (y - 1930) / 94; d.line((x, ty - 8, x, ty + 8), fill=(90, 110, 150, int(255 * a)), width=3)
        put(fr, txt(str(y), MF("SemiBold", 20), MUTED, 1), x, ty + 24, a * 0.8)
    global _yr_s
    _yr_s = yr if _yr_s is None else _yr_s + (yr - _yr_s) * 0.12
    xm = x0 + (x1 - x0) * (_yr_s - 1930) / 94; d.line((x0, ty, xm, ty), fill=GOLD + (int(255 * a),), width=6); d.ellipse((xm - 12, ty - 12, xm + 12, ty + 12), fill=GOLD_L + (int(255 * a),))
_yr_s = None
def captions(fr, t):
    raw = t
    for c0, *_ in reversed(CH):
        if t >= f(c0): raw = t - PAUSE * sum(1 for c in CH if f(c[0]) <= t); break
    for a, b, s in CAP:
        if a - 0.05 <= raw < b + 0.25:
            fnt = MF("Bold", 44); words = s.split(); lines = [[]]
            for w_ in words:
                if lines[-1] and fnt.getlength(" ".join(lines[-1] + [w_])) > 1500: lines.append([])
                lines[-1].append(w_)
            al = clamp((raw - a + 0.05) / 0.2) * clamp((b + 0.25 - raw) / 0.2)
            for i, ln in enumerate(lines): put(fr, txt(" ".join(ln), fnt, WHITE, 4, (0, 0, 0)), CX, 880 + i * 58 - (len(lines) - 1) * 29, al)
            return
_PR = np.random.default_rng(5); PART = [(_PR.uniform(0, W), _PR.uniform(0, H), _PR.uniform(8, 26), _PR.uniform(1.5, 4.5), _PR.uniform(0, 6.28)) for _ in range(40)]
def particles(fr, t):
    d = ImageDraw.Draw(fr)
    for x0, y0, v, r, ph in PART:
        y = (y0 - v * t) % (H + 40) - 20; x = x0 + 20 * math.sin(t * 0.3 + ph); al = int(70 + 50 * math.sin(t * 1.1 + ph))
        d.ellipse((x - r, y - r, x + r, y + r), fill=GOLD_L + (al,))
def frame_at(t, smooth_year=True, with_captions=True):
    global _yr_s
    if not smooth_year: _yr_s = None
    fr = BG.copy(); particles(fr, t)
    pf, ph = photo_state(t); e = eio(pf)
    if e <= 0.001: scenes(fr, t)
    else:
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); scenes(lay, t)
        sc = 1 - 0.38 * e; lw, lh = int(W * sc), int(H * sc); lay = lay.resize((lw, lh), Image.BICUBIC)
        cx = W / 2 - (W * 0.22) * e; fr.alpha_composite(lay, (int(cx - lw / 2), int(CY - CY * sc)))
        a, b, key, cap, cred = ph; card = photo_card(key, t, T(a), T(b), cap, cred)
        if card is not None:
            ang = -3 + 1.5 * math.sin(t * 0.4); card = card.rotate(ang, Image.BICUBIC, expand=True)
            put(fr, card, W * 0.74 + 120 * (1 - e), CY - 20, pf)
    g = np.zeros((300, W, 4), np.uint8); g[..., :3] = (3, 10, 22); g[..., 3] = np.linspace(0, 200, 300)[:, None].astype(np.uint8); fr.alpha_composite(Image.fromarray(g), (0, H - 300))
    if with_captions: captions(fr, t)
    chrome(fr, t)
    a = np.asarray(fr.convert("RGB")).astype(np.float32) * VIG
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

# ---------------------------------------------------------------- versão 9:16 (TikTok, Instagram, Kwai): vídeo horizontal no meio + fundo com fotos e fatos
VW, VH = 1080, 1920; VY = 660; VHH = int(VW * H / W)   # o horizontal ocupa 1080x608 a partir de y=660
FACTS = [(0, "DE CAMELÔ A DONO DO SBT", "1930–2024"), (17.4, "Nasceu Senor Abravanel, na Lapa (RJ)", "1930"), (41.0, "Paraquedista, locutor e a ideia da barca", "1948"),
         (66.1, "Assume o Baú da Felicidade", "ANOS 50"), (85.8, "Estreia o Programa Silvio Santos", "1963"), (105.5, "Entra no ar o SBT", "1981"),
         (116.95, "Candidatura barrada pelo TSE", "1989"), (138.95, "Sequestro da filha e crise no banco", "2001 · 2010"), (160.55, "Morre aos 93 anos, em São Paulo", "2024"),
         (173.55, "A voz, a coragem e a teimosia", "LEGADO")]
STRIP = [("paraquedista1948", "1948"), ("doc1950", "1950"), ("anos50", "ANOS 50"), ("tv70b", "ANOS 70"), ("sorriso_azul", "2010s")]
_vbg = None
def vbg():
    global _vbg
    if _vbg is not None: return _vbg
    yy, xx = np.mgrid[0:VH, 0:VW].astype(np.float32)
    a = np.array(NAVY, np.float32) + np.array([16, 30, 60], np.float32) * np.clip(1 - np.sqrt(((xx - VW / 2) / VW) ** 2 + ((yy - VH * 0.45) / VH) ** 2) * 1.4, 0, 1)[..., None]
    a[::60, :] += 4; a[:, ::60] += 4; bg = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(bg)
    put(bg, txt("A HISTÓRIA DE", MF("ExtraBold", 40), MUTED, 3), VW / 2, 130); put(bg, txt("SILVIO SANTOS", ANTON(150), GOLD_L, 8), VW / 2, 250)
    x = 40; tw = (VW - 80 - 4 * 16) / 5
    for key, yr in STRIP:   # faixa de fotos de várias épocas
        im = photo_img(key)
        if im is not None:
            th = 250; sc = max(tw / im.width, th / im.height); r = im.resize((int(im.width * sc) + 1, int(im.height * sc) + 1)); cx0 = (r.width - tw) / 2
            r = r.crop((int(cx0), 0, int(cx0 + tw), th)); card = Image.new("RGBA", (int(tw) + 8, th + 48), (246, 242, 232, 255)); card.paste(r, (4, 4))
            ImageDraw.Draw(card).text((card.width / 2, th + 26), yr, font=MF("ExtraBold", 24), fill=(24, 28, 36, 255), anchor="mm"); bg.alpha_composite(card, (int(x), 360))
        x += tw + 16
    d.rounded_rectangle((0, VY - 6, VW - 1, VY + VHH + 6), 0, outline=GOLD + (255,), width=6)
    put(bg, txt("fotos: reprodução", MF("SemiBold", 18), MUTED, 1), VW / 2, VY + VHH + 26)
    _vbg = bg; return bg
def vframe_at(t):
    fr = vbg().copy(); hz = frame_at(t, with_captions=False).resize((VW, VHH), Image.LANCZOS); fr.paste(hz, (0, VY))
    raw = t - PAUSE * sum(1 for c in CH if f(c[0]) <= t)
    fact = [x for x in FACTS if raw >= x[0] - 0.001][-1]; k0 = [f(x[0]) - (PAUSE if x[0] else 0) for x in FACTS if raw >= x[0] - 0.001][-1]
    kk = clamp((t - k0) / 0.5)
    put(fr, txt(fact[2], ANTON(110), GOLD_L, 6), VW / 2, 1400, kk, 0.85 + 0.15 * bo((t - k0) / 0.45))
    put(fr, txt(fact[1], MF("ExtraBold", 40), WHITE, 3), VW / 2, 1500, kk)
    for a, b, s_ in CAP:   # legenda grande
        if a - 0.05 <= raw < b + 0.25:
            fnt = MF("Bold", 46); words = s_.split(); lines = [[]]
            for w_ in words:
                if lines[-1] and fnt.getlength(" ".join(lines[-1] + [w_])) > 940: lines.append([])
                lines[-1].append(w_)
            al = clamp((raw - a + 0.05) / 0.2) * clamp((b + 0.25 - raw) / 0.2)
            for i, ln in enumerate(lines): put(fr, txt(" ".join(ln), fnt, WHITE, 4, (0, 0, 0)), VW / 2, 1660 + i * 60, al)
            break
    put(fr, chip("SIGA @eliezio.souza78", GOLD, 30, NAVY), VW / 2, 1855, clamp((t - 1) / 0.5))
    return fr.convert("RGB")


def cutout(key, target_h):
    """recorte da pessoa (U2Net) com borda suave; volta RGBA na altura pedida"""
    import cv2
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from segment_person import PersonSeg
    im = photo_img(key); rgb = np.asarray(im); m = PersonSeg(os.path.expanduser("~/.cache/edicao-video/seg/u2net_human_seg.onnx"))(rgb)
    m = cv2.GaussianBlur(np.clip((m - 0.35) / 0.3, 0, 1), (0, 0), 2.0)
    rgba = np.dstack([rgb, (m * 255).astype(np.uint8)]); out = Image.fromarray(rgba, "RGBA"); bb = out.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
    out = out.crop(bb); sc = target_h / out.height; return out.resize((int(out.width * sc), int(target_h)), Image.LANCZOS)
def thumbnail(out):
    """miniatura do YouTube 1280x720: jovem (1959, P&B) e maduro (2019, cor), rostos grandes, 4 palavras"""
    TW, TH = 1280, 720; fr = Image.new("RGBA", (TW, TH), NAVY + (255,)); d = ImageDraw.Draw(fr)
    for i in range(24):   # raios dourados atrás
        a0 = i * 15; d.pieslice((TW * 0.62 - 1400, TH * 0.55 - 1400, TW * 0.62 + 1400, TH * 0.55 + 1400), a0, a0 + 6, fill=(30, 52, 96, 255))
    glow = Image.new("RGBA", (TW, TH), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse((TW * 0.62 - 330, TH * 0.55 - 330, TW * 0.62 + 330, TH * 0.55 + 330), fill=GOLD + (120,))
    fr.alpha_composite(glow.filter(ImageFilter.GaussianBlur(90)))
    old = cutout("sorriso_azul", 760)
    yim = photo_img("paraquedista1948").convert("L").convert("RGB"); sc_ = 470 / yim.height; yim = yim.resize((int(yim.width * sc_), 470), Image.LANCZOS)
    young = Image.new("RGBA", (yim.width + 28, yim.height + 28), (246, 242, 232, 255)); young.paste(yim, (14, 14)); young = young.rotate(5, Image.BICUBIC, expand=True)
    def rim(im, col, r=10):
        a = im.getchannel("A").filter(ImageFilter.MaxFilter(r * 2 + 1)); halo = Image.new("RGBA", im.size, col + (0,)); halo.putalpha(a); return halo
    shd = Image.new("RGBA", (young.width + 60, young.height + 60), (0, 0, 0, 0)); shd.paste((0, 0, 0, 170), (30, 40), young.getchannel("A")); fr.alpha_composite(shd.filter(ImageFilter.GaussianBlur(16)), (30, 170))
    fr.alpha_composite(young, (60, 190))
    ox = int(TW * 0.62 - old.width / 2); fr.alpha_composite(rim(old, GOLD_L, 8), (ox, TH - old.height + 40)); fr.alpha_composite(old, (ox, TH - old.height + 40))
    put(fr, txt("DE CAMELÔ", ANTON(118), WHITE, 9, (0, 0, 0)), 300, 95); put(fr, txt("1948", ANTON(70), GOLD_L, 6, (0, 0, 0)), 240, TH - 50)
    put(fr, txt("A DONO DO SBT", ANTON(118), GOLD_L, 9, (0, 0, 0)), TW - 330, 95); dd_ = ImageDraw.Draw(fr); ax, ay = 470, 380; dd_.polygon([(ax - 60, ay - 26), (ax + 20, ay - 26), (ax + 20, ay - 60), (ax + 90, ay), (ax + 20, ay + 60), (ax + 20, ay + 26), (ax - 60, ay + 26)], fill=GOLD + (255,), outline=(0, 0, 0, 255), width=6)
    put(fr, chip("A HISTÓRIA REAL", RED, 40), TW - 230, TH - 70)
    fr.convert("RGB").save(out, quality=95)


def thumbnail2(out, var="1"):
    """miniatura v2: rosto grande à direita, foto de 1948 inclinada, título num bloco só embaixo à esquerda"""
    TW, TH = 1280, 720
    if var == "1":   # vermelho e amarelo, alto contraste
        yy, xx = np.mgrid[0:TH, 0:TW].astype(np.float32); r = np.clip(np.sqrt(((xx - 900) / TW) ** 2 + ((yy - 300) / TH) ** 2) * 1.6, 0, 1)[..., None]
        bgc = np.array([255, 196, 40], np.float32) * (1 - r) + np.array([170, 14, 20], np.float32) * r
        fr = Image.fromarray(bgc.astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(fr)
        for i in range(30): a0 = i * 12; d.pieslice((900 - 1600, 300 - 1600, 900 + 1600, 300 + 1600), a0, a0 + 5, fill=(255, 255, 255, 38))
        rimc, t1c, boxc, t2c = WHITE, WHITE, (255, 214, 40), (20, 10, 10); headline = ("DE CAMELÔ", "A BILIONÁRIO")
    else:            # azul e dourado
        fr = Image.new("RGBA", (TW, TH), NAVY + (255,)); d = ImageDraw.Draw(fr)
        for i in range(24): a0 = i * 15; d.pieslice((900 - 1500, 330 - 1500, 900 + 1500, 330 + 1500), a0, a0 + 6, fill=(30, 54, 100, 255))
        gl = Image.new("RGBA", (TW, TH), (0, 0, 0, 0)); ImageDraw.Draw(gl).ellipse((900 - 360, 330 - 360, 900 + 360, 330 + 360), fill=GOLD + (140,)); fr.alpha_composite(gl.filter(ImageFilter.GaussianBlur(100)))
        rimc, t1c, boxc, t2c = GOLD_L, WHITE, GOLD, NAVY; headline = ("DE CAMELÔ", "A DONO DO SBT")
    old = cutout("sorriso_azul", 900)
    halo = Image.new("RGBA", old.size, rimc + (0,)); halo.putalpha(old.getchannel("A").filter(ImageFilter.MaxFilter(19)))
    ox = TW - old.width + 60; oy = TH - old.height + 230
    sh = Image.new("RGBA", (TW, TH), (0, 0, 0, 0)); sh.paste((0, 0, 0, 140), (ox - 30, oy + 10), old.getchannel("A")); fr.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)))
    fr.alpha_composite(halo, (ox, oy)); fr.alpha_composite(old, (ox, oy))
    yim = photo_img("paraquedista1948").convert("L").convert("RGB"); sc_ = 330 / yim.height; yim = yim.resize((int(yim.width * sc_), 330), Image.LANCZOS)
    young = Image.new("RGBA", (yim.width + 24, yim.height + 64), (246, 242, 232, 255)); young.paste(yim, (12, 12))
    ImageDraw.Draw(young).text((young.width / 2, yim.height + 38), "1948", font=ANTON(40), fill=(24, 24, 24, 255), anchor="mm"); young = young.rotate(-7, Image.BICUBIC, expand=True)
    sh2 = Image.new("RGBA", (young.width + 60, young.height + 60), (0, 0, 0, 0)); sh2.paste((0, 0, 0, 170), (30, 40), young.getchannel("A")); fr.alpha_composite(sh2.filter(ImageFilter.GaussianBlur(14)), (20, 10))
    fr.alpha_composite(young, (40, 20))
    dd = ImageDraw.Draw(fr); ax, ay = 400, 220   # seta da foto antiga para o rosto
    dd.polygon([(ax - 50, ay - 22), (ax + 20, ay - 22), (ax + 20, ay - 52), (ax + 85, ay), (ax + 20, ay + 52), (ax + 20, ay + 22), (ax - 50, ay + 22)], fill=boxc + (255,), outline=(0, 0, 0, 255), width=6)
    l1 = txt(headline[0], ANTON(106), t1c, 9, (0, 0, 0)); fr.alpha_composite(l1, (34, 398))
    f2 = ANTON(104); bb = f2.getbbox(headline[1]); bw, bh = bb[2] - bb[0] + 56, bb[3] - bb[1] + 40
    box = Image.new("RGBA", (bw, bh), boxc + (255,)); ImageDraw.Draw(box).text((28 - bb[0], 20 - bb[1]), headline[1], font=f2, fill=t2c + (255,))
    box = box.rotate(2, Image.BICUBIC, expand=True); fr.alpha_composite(box, (40, 532))
    fr.convert("RGB").save(out, quality=95)

def capa(out, var="A"):
    fr = BG.copy(); global _yr_s
    if var == "A":
        for i, (em, lab) in enumerate([("🛍️", "CAMELÔ"), ("📺", "DONO DE TV")]):
            x = 330 + i * 1260; put(fr, medal(em, 300), x, 470); put(fr, txt(lab, ANTON(70), GOLD_L, 5), x, 680)
        put(fr, txt("➜", ANTON(160), GOLD, 6), CX, 470)
        put(fr, txt("SILVIO SANTOS", ANTON(200), WHITE, 9), CX, 230); put(fr, txt("DE CAMELÔ A DONO DE UMA TV", ANTON(90), GOLD_L, 6), CX, 830)
        put(fr, stamp("A HISTÓRIA COMPLETA", RED, 64, -5), CX, 980)
    else:
        put(fr, txt("ELE VENDIA NA RUA", ANTON(130), WHITE, 7), CX, 250); put(fr, txt("AINDA ADOLESCENTE…", ANTON(130), GOLD_L, 7), CX, 410)
        put(fr, medal("📺", 280), CX - 330, 680); put(fr, txt("DEPOIS COMPROU", ANTON(84), WHITE, 5), CX + 230, 620); put(fr, txt("UMA TV INTEIRA", ANTON(100), GOLD_L, 6), CX + 230, 740)
        put(fr, chip("A HISTÓRIA DE SILVIO SANTOS", RED, 50), CX, 960)
    fr.convert("RGB").save(out, quality=95)

# ---------------------------------------------------------------- áudio: voz com as pausas, trilha abaixando sob a voz, efeitos
def audio(vout):
    SR = 48000; n = int(TOTAL * SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{V}/vo.mp3", "-ar", str(SR), "-ac", "2", f"{V}/vo48.wav"], check=True)
    w = wave.open(f"{V}/vo48.wav"); vo = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, 2) / 32768
    vt = np.zeros((n, 2), np.float32); cuts = [0.0] + [c[0] for c in CH] + [VO_RAW]
    for i in range(len(cuts) - 1):
        a, b = int(cuts[i] * SR), int(cuts[i + 1] * SR); seg = vo[a:b]; o = int(f(cuts[i] + 1e-3) * SR) if i else 0
        vt[o:o + len(seg)] += seg[:max(0, n - o)]
    def writew(p, x):
        ww = wave.open(p, "wb"); ww.setnchannels(2); ww.setsampwidth(2); ww.setframerate(SR); ww.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); ww.close()
    bw = wave.open(f"{S}/v49/bed.wav"); bed = np.frombuffer(bw.readframes(bw.getnframes()), np.int16).astype(np.float32).reshape(-1, bw.getnchannels()) / 32768
    xf = int(1.5 * SR); loop = bed.copy()
    while len(loop) < n:
        r = np.linspace(0, 1, xf)[:, None]; loop[-xf:] = loop[-xf:] * (1 - r) + bed[:xf] * r; loop = np.concatenate([loop, bed[xf:]])
    tl = np.arange(n) / SR; gain = 0.11 * np.clip(tl / 1.0, 0, 1) * np.clip((TOTAL - tl) / 1.5, 0, 1)
    writew(f"{V}/voice.wav", vt); writew(f"{V}/song.wav", loop[:n] * gain[:, None])
    ev = [(f(c[0]) - PAUSE - 0.1, sfx.whoosh(0.6), 0.16) for c in CH] + [(f(c[0]) - PAUSE + 0.25, sfx.thud(0.45), 0.22) for c in CH]
    ev += [(x, sfx.click(seed=i), 0.14) for i, x in enumerate([0.2, 3.6, 6.0, 9.9, T(131.4), T(110.4)])]
    sfx.build(ev, TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/song.wav", "-filter_complex",
                    "[1:a]highpass=f=70,acompressor=threshold=0.1:ratio=2.2:attack=8:release=200:makeup=1.4,asplit=2[vox][k2];[2:a]volume=0.9[sf];[3:a]volume=1.0[sg];"
                    "[sg][k2]sidechaincompress=threshold=0.03:ratio=5:attack=20:release=500[sgd];"
                    f"[vox][sf][sgd]amix=inputs=3:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},loudnorm=I=-14:TP=-1.5:LRA=11[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
def main():
    if MODE == "thumb": thumbnail(OUTFILE); return
    if MODE.startswith("thumb2"): thumbnail2(OUTFILE, MODE.split(":")[1] if ":" in MODE else "1"); return
    if MODE.startswith("capa"): capa(OUTFILE, MODE.split(":")[1] if ":" in MODE else "A"); return
    if MODE.startswith("one:"): frame_at(float(MODE[4:]), False).save(OUTFILE, quality=92); return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]; outs = [frame_at(x, False).resize((640, 360), Image.LANCZOS) for x in ts]
        cols = 3; rows = math.ceil(len(outs) / cols); sh = Image.new("RGB", (640 * cols, 360 * rows))
        [sh.paste(o, ((i % cols) * 640, (i // cols) * 360)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=88); return
    if MODE.startswith("vframes"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]; outs = [vframe_at(x).resize((360, 640), Image.LANCZOS) for x in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=88); return
    NF = int(round(TOTAL * FPS))
    if MODE.startswith("vpart"):
        i, nparts = map(int, MODE.split(":")[1:]); a, b = NF * i // nparts, NF * (i + 1) // nparts
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{VW}x{VH}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", OUTFILE], stdin=subprocess.PIPE)
        for k in range(max(0, a - 60), a): frame_at(k / FPS)
        for k in range(a, b): enc.stdin.write(vframe_at(k / FPS).tobytes())
        enc.stdin.close(); enc.wait(); print("part done", i); return
    if MODE.startswith("part"):
        i, nparts = map(int, MODE.split(":")[1:]); a, b = NF * i // nparts, NF * (i + 1) // nparts
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", OUTFILE], stdin=subprocess.PIPE)
        for k in range(max(0, a - 60), a): frame_at(k / FPS)          # aquece a linha do tempo suavizada
        for k in range(a, b): enc.stdin.write(frame_at(k / FPS).tobytes())
        enc.stdin.close(); enc.wait(); print("part done", i); return
    if MODE == "mux": audio(f"{V}/video.mp4"); print("done"); return
main()
