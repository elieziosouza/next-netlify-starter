"""Foto de perfil (1080x1080) e capa (1640x624) do Facebook do Teacher Eliezio: marinho com grade, amarelo de destaque, avatar 3D sorrindo."""
import sys, os, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S = sys.argv[1]; OUT = f"{S}/fb_teacher"; FD = f"{S}/fontdl"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from segment_person import PersonSeg
NAVY = (12, 31, 69); NAVY2 = (22, 48, 98); YEL = (255, 214, 64); WHITE = (255, 255, 255); INK = (20, 24, 34); SKY = (150, 200, 245)
def F(name, s): return ImageFont.truetype(f"{FD}/{name}", s)
def MF(w, s): return F(f"Montserrat-{w}.ttf", s)
def bg(w, h, cx, cy):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32); r = np.sqrt(((xx - cx) / w) ** 2 + ((yy - cy) / h) ** 2)
    a = np.array(NAVY, np.float32) + (np.array(NAVY2, np.float32) - np.array(NAVY, np.float32)) * np.clip(1 - r * 1.5, 0, 1)[..., None]
    g = 48; a[::g, :] += 9; a[:, ::g] += 9
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).convert("RGBA")
def avatar_cut():
    im = Image.open(f"{S}/v77/av3d_1.png").convert("RGBA"); rgb = np.asarray(im.convert("RGB"))
    m = PersonSeg(os.path.expanduser("~/.cache/edicao-video/seg/u2net_human_seg.onnx"))(rgb)
    m = cv2.GaussianBlur(np.clip((m - 0.35) / 0.3, 0, 1), (0, 0), 1.5) * (np.asarray(im)[..., 3] / 255.0)
    out = Image.fromarray(np.dstack([rgb, (m * 255).astype(np.uint8)]), "RGBA"); return out.crop(out.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox())
def shadow(im, r=18, op=140):
    a = im.getchannel("A").filter(ImageFilter.GaussianBlur(r)).point(lambda v: v * op // 255); s = Image.new("RGBA", im.size, (0, 0, 0, 0)); s.putalpha(a); return s
def chip(t, size, fill, col, pad=34):
    f = MF("ExtraBold", size); w = int(f.getlength(t)) + 2 * pad; h = int(size * 1.9)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im); d.rounded_rectangle((0, 0, w - 1, h - 1), h // 2, fill=fill + (255,))
    d.text((w / 2, h / 2 + 1), t, font=f, fill=col + (255,), anchor="mm"); return im
def bubble(t, size):
    f = MF("Black", size); w = int(f.getlength(t)) + 70; h = int(size * 2.0)
    im = Image.new("RGBA", (w + 10, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w, h), 28, fill=WHITE + (255,)); d.polygon([(40, h - 2), (90, h - 2), (30, h + 36)], fill=WHITE + (255,))
    d.text((w / 2, h / 2), t, font=f, fill=INK + (255,), anchor="mm"); return im
def fade_bottom(im, n):
    a = np.asarray(im.getchannel("A")).astype(np.float32); h = a.shape[0]; g = np.ones(h, np.float32); g[h - n:] = np.linspace(1, 0, n) ** 1.3
    out = im.copy(); out.putalpha(Image.fromarray((a * g[:, None]).astype(np.uint8))); return out
def perfil(av):
    N = 1080; fr = bg(N, N, N / 2, N * 0.4); d = ImageDraw.Draw(fr)
    glow = Image.new("RGBA", (N, N), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse((190, 150, 890, 850), fill=YEL + (90,)); fr.alpha_composite(glow.filter(ImageFilter.GaussianBlur(80)))
    sc = 860 / av.height; a = av.resize((int(av.width * sc), 860), Image.LANCZOS); x = (N - a.width) // 2; y = N - a.height - 40
    fr.alpha_composite(shadow(a), (x + 8, y + 14)); fr.alpha_composite(a, (x, y))
    c = chip("TEACHER ELIEZIO", 54, YEL, INK); fr.alpha_composite(c, ((N - c.width) // 2, N - c.height - 70))
    m = Image.new("L", (N, N), 0); ImageDraw.Draw(m).ellipse((0, 0, N - 1, N - 1), fill=255)   # prévia em círculo
    fr.convert("RGB").save(f"{OUT}/teacher_perfil_1080.jpg", quality=95)
    pv = Image.new("RGBA", (N, N), (240, 242, 245, 255)); pv.paste(fr, (0, 0), m); ImageDraw.Draw(pv).ellipse((0, 0, N - 1, N - 1), outline=YEL + (255,), width=14)
    pv.convert("RGB").resize((360, 360), Image.LANCZOS).save(f"{OUT}/prev_perfil_circulo.jpg", quality=90)
def capa(av):
    W, H = 1640, 624; fr = bg(W, H, W * 0.68, H * 0.5); d = ImageDraw.Draw(fr)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glow).ellipse((930, 40, 1450, 620), fill=YEL + (80,)); fr.alpha_composite(glow.filter(ImageFilter.GaussianBlur(70)))
    for (x, y, t, sz) in ((1480, 470, "Let's go!", 34), (1500, 150, "?", 80), (150, 120, "ABC", 44)):
        d.text((x, y), t, font=MF("Black", sz), fill=(52, 80, 136, 255), anchor="mm")
    sc = 580 / av.height; a = av.resize((int(av.width * sc), 580), Image.LANCZOS); a = fade_bottom(a, 130); ax = 1090 - a.width // 2; ay = H - a.height
    fr.alpha_composite(shadow(a), (ax + 8, ay + 12)); fr.alpha_composite(a, (ax, ay))
    b = bubble("Hello!", 42); fr.alpha_composite(b, (1220, 36))
    x0 = 330
    d.text((x0, 150), "ENGLISH CLASS", font=MF("ExtraBold", 34), fill=SKY + (255,), anchor="lm")
    d.text((x0 - 4, 250), "TEACHER", font=F("Anton-Regular.ttf", 118), fill=WHITE + (255,), anchor="lm", stroke_width=0)
    d.text((x0 - 4, 372), "ELIEZIO", font=F("Anton-Regular.ttf", 118), fill=YEL + (255,), anchor="lm")
    d.text((x0, 465), "Inglês fácil, 1 minuto por dia", font=MF("SemiBold", 32), fill=WHITE + (255,), anchor="lm")
    xx = x0
    for t in ("QUIZ", "PRONÚNCIA", "GRAMÁTICA", "VOCABULÁRIO"):
        c = chip(t, 22, (40, 70, 130), WHITE, 22); fr.alpha_composite(c, (xx, 512)); xx += c.width + 12
    fr.convert("RGB").save(f"{OUT}/teacher_capa_facebook_1640x624.jpg", quality=95)
    pv = fr.convert("RGB").copy(); dp = ImageDraw.Draw(pv)   # guia: corte do celular e foto de perfil no PC
    mw = int(H * 16 / 9 * 0.9); mx = (W - mw) // 2
    dp.rectangle((mx, 0, mx + mw, H - 1), outline=(255, 80, 80), width=4); dp.text((mx + 12, 12), "área que aparece no celular", font=MF("Bold", 22), fill=(255, 120, 120))
    dp.ellipse((60, H - 230, 60 + 340, H + 110), outline=(255, 80, 80), width=4); dp.text((90, H - 260), "foto de perfil (PC)", font=MF("Bold", 22), fill=(255, 120, 120))
    pv.resize((820, 312), Image.LANCZOS).save(f"{OUT}/prev_capa_guias.jpg", quality=90)
av = avatar_cut(); perfil(av); capa(av); print("ok")
