"""Série diária "IA no seu bolso": vinheta de abertura (1,6 s) e capa padrão (título + número do episódio + rosto dele), no estilo do canal.
Uso: python3 serie_ia.py S vinheta | python3 serie_ia.py S capa EP "LINHA 1|LINHA 2" "EMOJI" ME.mp4 T_ROSTO SAIDA.jpg"""
import sys, math, subprocess, importlib.util, io
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
S = sys.argv[1]; CMD = sys.argv[2]; ARGS = sys.argv[3:]
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
import sfx
W, H, CX, FPS = R.W, R.H, R.CX, R.FPS; YEL = (255, 214, 0); WHITE = (255, 255, 255); BAR = R.BAR; clamp = R.clamp; ease_out = R.ease_out
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"; OUT = f"{S}/serie_ia"
def emoji(ch, size):
    f = ImageFont.truetype(EMOJI, 109); im = Image.new("RGBA", (160, 160), (0, 0, 0, 0)); ImageDraw.Draw(im).text((8, 8), ch, font=f, embedded_color=True)
    im = im.crop(im.getbbox()); sc = size / max(im.size); return im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
def logo(k=1.0):
    """selo da série: 'IA' grande dourado num anel, 'NO SEU BOLSO' embaixo"""
    lay = Image.new("RGBA", (900, 700), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); cx, cy = 450, 290
    r = 230 * ease_out(clamp(k / 0.5))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=R.GOLD + (255,), width=14)
    d.ellipse((cx - r * 0.86, cy - r * 0.86, cx + r * 0.86, cy + r * 0.86), fill=(8, 30, 56, 255))
    if k > 0.25:
        f = R.BIGF(int(230 * ease_out(clamp((k - 0.25) / 0.35)) + 1)); d.text((cx, cy + 6), "IA", font=f, fill=R.GOLD_L + (255,), anchor="mm", stroke_width=4, stroke_fill=R.NAVY + (255,))
    if k > 0.5:
        a = clamp((k - 0.5) / 0.3); f2 = R.BIGF(96); txt = "NO SEU BOLSO"
        t = Image.new("RGBA", (900, 140), (0, 0, 0, 0)); ImageDraw.Draw(t).text((450, 70), txt, font=f2, fill=WHITE + (255,), anchor="mm", stroke_width=6, stroke_fill=R.NAVY + (255,))
        lay.alpha_composite(R.fade(t, a), (int(-120 * (1 - a)), 540))
    return lay
def vinheta():
    T = 1.6; n = int(T * FPS); bg = np.clip(R.NAVYBG, 0, 255).astype(np.uint8)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", f"{OUT}/vinheta_v.mp4"], stdin=subprocess.PIPE)
    for i in range(n):
        t = i / FPS; k = t / 1.1; fr = Image.fromarray(bg).convert("RGBA")
        for j in range(18):                                            # raios dourados girando devagar
            a = j / 18 * 2 * math.pi + t * 0.6; L = 1400
            ray = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(ray)
            dr.polygon([(CX, 900), (CX + L * math.cos(a - 0.03), 900 + L * math.sin(a - 0.03)), (CX + L * math.cos(a + 0.03), 900 + L * math.sin(a + 0.03))], fill=R.GOLD + (int(26 * clamp(t / 0.4)),))
            fr.alpha_composite(ray)
        lg = logo(k); fr.alpha_composite(lg, (CX - 450, 900 - 290))
        if t > 0.75:
            e = emoji("🤖", int(170 * R.back_out(clamp((t - 0.75) / 0.3), 2.2)) + 1); fr.alpha_composite(e, (CX + 200, 560))
        if t > 0.9:
            a = clamp((t - 0.9) / 0.3); f = R.MF("ExtraBold", 40); tl = Image.new("RGBA", (W, 80), (0, 0, 0, 0))
            ImageDraw.Draw(tl).text((CX, 40), "com Eliezio Souza", font=f, fill=R.GOLD_L + (255,), anchor="mm"); fr.alpha_composite(R.fade(tl, a), (0, 1520))
        if t > T - 0.15: fr = Image.blend(fr, Image.new("RGBA", fr.size, (255, 255, 255, 255)), (t - (T - 0.15)) / 0.15 * 0.8)
        BAR.draw_bar(fr, 0.0, "canal")
        enc.stdin.write(fr.convert("RGB").tobytes())
    enc.stdin.close(); enc.wait()
    sfx.build([(0.0, sfx.whoosh(0.6), 0.35), (0.3, sfx.thud(0.4), 0.4), (0.8, sfx.click(), 0.6), (T - 0.2, sfx.whoosh(0.4), 0.25)], T, f"{OUT}/vinheta_a.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{OUT}/vinheta_v.mp4", "-i", f"{OUT}/vinheta_a.wav", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", f"{OUT}/vinheta_ia_no_seu_bolso.mp4"], check=True)
def capa(ep, lines, emo, me, t_face, out):
    img = Image.fromarray(np.clip(R.NAVYBG, 0, 255).astype(np.uint8)).convert("RGBA")
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t_face), "-i", me, "-frames:v", "1", "-vf", "scale=1080:1920", "-f", "image2pipe", "-vcodec", "png", "-"], capture_output=True).stdout
    m = np.asarray(Image.open(io.BytesIO(p)).convert("RGB"))[260:1620]; top = 880; ph = H - top; fw = min(int(m.shape[1] * ph / m.shape[0]), 2 * (W - CX) - 4)
    fg = cv2.resize(m, (fw, ph), interpolation=cv2.INTER_AREA); x0 = CX - fw // 2
    lay = np.zeros((ph, W, 4), np.uint8); lay[:, x0:x0 + fw, :3] = fg
    al = np.ones((ph, fw), np.float32); al[:200] *= np.linspace(0, 1, 200)[:, None]; al[:, :70] *= np.linspace(0, 1, 70)[None]; al[:, -70:] *= np.linspace(1, 0, 70)[None]
    lay[:, x0:x0 + fw, 3] = (al * 255).astype(np.uint8); img.alpha_composite(Image.fromarray(lay), (0, top))
    lg = logo(1.0).resize((360, 280), Image.LANCZOS); img.alpha_composite(lg, (CX - 180, 640))
    chip = Image.new("RGBA", (190, 70), (0, 0, 0, 0)); dc = ImageDraw.Draw(chip); dc.rounded_rectangle((0, 0, 189, 69), 16, fill=R.GOLD + (255,))
    dc.text((95, 36), f"EP. {int(ep):02d}", font=R.BIGF(48), fill=R.NAVY + (255,), anchor="mm"); R.paste(img, chip.rotate(-4, expand=True, resample=Image.BICUBIC), CX + 250, 660, 0.5, 10, (4, 8))
    e = emoji(emo, 190); img.alpha_composite(e, (CX - 430, 660))
    ys = (210, 380)
    for li, (txt, col) in enumerate(zip(lines[:2], (WHITE, YEL))):
        size = 170; f = R.BIGF(size)
        while f.getlength(txt) > 860: size -= 4; f = R.BIGF(size)
        t = Image.new("RGBA", (W, int(size * 1.3)), (0, 0, 0, 0)); ImageDraw.Draw(t).text((CX, t.height / 2), txt, font=f, fill=col + (255,), anchor="mm", stroke_width=12, stroke_fill=(0, 0, 0, 255))
        R.paste(img, t, 0, ys[li] - t.height / 2, 0.8, 18, (6, 14))
    BAR.draw_bar(img, 0.0, "canal"); img.alpha_composite(R.top, (R.HDX, 0)); img.convert("RGB").save(out, quality=95)
if CMD == "vinheta": vinheta()
else: capa(ARGS[0], ARGS[1].split("|"), ARGS[2], ARGS[3], float(ARGS[4]), ARGS[5])
