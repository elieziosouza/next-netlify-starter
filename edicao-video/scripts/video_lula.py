"""Só o vídeo (13/11/2026): vídeo de terceiros em tela cheia com caixa fixa, barra lateral, topo/rodapé e fechamento. Sem a reação dele.
Uso: python3 video_lula.py SAIDA.mp4"""
import sys, math, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw
import video_react3 as R
from video_react3 import BAR, MF, eo, clamp, back_out, NAVY, WHITE, GOLD, CX, W, H, FPS, top, bot, TOPH, HDX
SS, END = 14.0, 24.0
def full_clip(cl_rgb):
    im = cv2.resize(cl_rgb, (1088, 1922), interpolation=cv2.INTER_CUBIC)[1:1921, 4:1084]
    blur = cv2.GaussianBlur(im, (0, 0), 1.6); im = cv2.addWeighted(im, 1.5, blur, -0.5, 0)
    out = Image.fromarray(im).convert("RGBA")
    g = np.zeros((H, W, 4), np.uint8); g[..., 0], g[..., 1], g[..., 2] = 4, 14, 28
    ramp = np.clip((np.arange(H) - 1400) / 520, 0, 1) ** 1.3; g[..., 3] = (ramp * 190).astype(np.uint8)[:, None]
    out.alpha_composite(Image.fromarray(g)); return out
def end_texts(fr, t):
    u = t - 19.6
    if u < 0: return
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); k = eo(u / 0.4)
    d.text((CX, 1722 + 12 * (1 - k)), "COMENTE O QUE VOCÊ ACHA", font=MF("ExtraBold", 50), fill=WHITE + (int(255 * k),), anchor="mm", stroke_width=5, stroke_fill=NAVY + (int(220 * k),))
    lw = int(150 * eo((u - 0.2) / 0.5))
    if lw > 0: d.rectangle((CX - lw, 1764, CX + lw, 1766), fill=GOLD + (255,))
    k2 = eo((u - 0.5) / 0.4)
    if k2 > 0: d.text((CX, 1806 + 10 * (1 - k2)), "SIGA PARA MAIS", font=MF("ExtraBold", 46), fill=WHITE + (int(255 * k2),), anchor="mm", stroke_width=5, stroke_fill=NAVY + (int(220 * k2),))
    fr.alpha_composite(lay)
def compose(cl, t):
    fr = full_clip(cl); kc = eo((t - 0.3) / 0.5)
    if kc > 0: BAR.lower_card(fr, "COP31 · TURQUIA", ["LULA É OVACIONADO E CERCADO", "SEGUNDO A BNEWS (11/11)"], 1565, kc, fs=34)
    ImageDraw.Draw(fr).text((CX, 1489), "Vídeo recebido por WhatsApp", font=MF("SemiBold", 21), fill=(235, 238, 245, 235), anchor="mm", stroke_width=3, stroke_fill=NAVY + (210,))
    end_texts(fr, t)
    if t >= 0.4:
        k = back_out((t - 0.4) / 0.55); fr.alpha_composite(top, (HDX, int(-TOPH * (1 - k)))); fr.alpha_composite(bot, (HDX, int(H - bot.height + bot.height * (1 - k))))
    BAR.draw_bar(fr, clamp(t / END), "canal", eo((t - 0.2) / 0.6), 0.0, 0.5 + 0.5 * math.sin(t * 5))
    return fr.convert("RGB")
def audio(out):
    sys.path.insert(0, R.K + "/scripts"); import sfx
    sfx.build([(0.2, sfx.barra(), 0.12), (19.7, sfx.siga(), 0.10)], END + 1, "sfx_l.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(SS), "-t", str(END), "-i", "ter.mp4", "-i", "sfx_l.wav", "-filter_complex",
        f"[0:a]aresample=48000,highpass=f=70[c];[1:a]aresample=48000[s];[c][s]amix=inputs=2:normalize=0:duration=first,atrim=0:{END:.3f},afade=t=out:st={END-0.4:.3f}:d=0.4[a]", "-map", "[a]", "-c:a", "pcm_s16le", out], check=True)
if __name__ == "__main__":
    a = sys.argv[1]
    if a.startswith("frames:"):
        ims = []
        for ts in a[7:].split(","):
            t = float(ts); cl = R.grab("ter.mp4", SS + t, 480, 848); im = compose(cl, t); im.save(f"lf_{ts}.jpg", quality=88); ims.append(im.resize((360, 640)))
        m = Image.new("RGB", (360 * len(ims), 640)); [m.paste(im, (i * 360, 0)) for i, im in enumerate(ims)]; m.save("lf_sheet.jpg", quality=86); sys.exit()
    audio("mix_l.wav")
    dc = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(SS), "-t", str(END), "-i", "ter.mp4", "-vf", "fps=30", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", "mix_l.wav",
        "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", a], stdin=subprocess.PIPE)
    n = int(END * FPS); last = None
    for i in range(n):
        r = dc.stdout.read(480 * 848 * 3)
        if len(r) == 480 * 848 * 3: last = np.frombuffer(r, np.uint8).reshape(848, 480, 3)
        enc.stdin.write(compose(last, i / FPS).tobytes())
        if i % 150 == 0: print(i, n, flush=True)
    enc.stdin.close(); enc.wait(); print("ok", a, n)
