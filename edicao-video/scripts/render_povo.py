"""Série "O povo ontem": ele apresenta (noite, carro) e entram dois vídeos de gente reagindo ao Flávio na TV (bandeja na TV, @lourrizy;
"vai pedir desculpa"), cada um num card com ele no círculo. Áudio original dos vídeos; trecho do palavrão fica de fora."""

import sys, math, subprocess, importlib.util, os
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
S = sys.argv[1]; OUTFILE = sys.argv[2]; MODE = sys.argv[3] if len(sys.argv) > 3 else "full"
spec = importlib.util.spec_from_file_location("ra", f"{S}/work/render_atrop.py"); sys.argv = [sys.argv[0], S, "/dev/null", "lib"]
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
sys.path.insert(0, f"{S}/work")
import cor_fla, sfx
W, H, FPS, CX = R.W, R.H, R.FPS, R.CX; clamp = R.clamp; eo = R.ease_out; eio = R.ease_io; bo = R.back_out
V = f"{S}/v64"; FD = f"{S}/fontdl"
_f = {}
def I(w, s):
    if (w, s) not in _f: _f[(w, s)] = ImageFont.truetype(f"{FD}/Inter-{w}.ttf", s)
    return _f[(w, s)]
WH = (245, 246, 248); MUT = (170, 178, 190); YEL = (255, 214, 92)
PARTS = [("me", 4.40, 8.15, "intro"), ("c1", 2.0, 16.5, "clip"), ("c2", 0.0, 18.2, "clip")]
segs = []; acc = 0.0
for s_, a, b, m in PARTS: segs.append(dict(src=s_, a=a, b=b, mode=m, t0=acc, t1=acc + b - a)); acc += b - a
EDIT_END = acc; END_IN = EDIT_END + 0.05; TOTAL = END_IN + 3.0
R.FIN_IN = EDIT_END; R.END_IN = END_IN; R.EDIT_END = EDIT_END; R.MUS_IN = 0.0
CREDIT = {"c1": "Vídeo: @lourrizy", "c2": "Vídeo: redes sociais"}
def seg_at(t):
    for s in segs:
        if t < s["t1"]: return s
    return segs[-1]
_cache = {}
def frames(name, path, w, h, vf=""):
    if name not in _cache:
        p = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps=30,scale={w}:{h}{vf}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        n = len(p) // (w * h * 3); _cache[name] = np.frombuffer(p[:n * w * h * 3], np.uint8).reshape(n, h, w, 3)
    return _cache[name]
def me(x): a = frames("me", f"{V}/me.mp4", W, H); return a[int(clamp(x * FPS, 0, len(a) - 1))]
CW, CHh, CY0 = 760, 1351, 250
def cl(x, src="c1"):
    a = frames(src, f"{V}/{src}.mp4", CW, CHh); return a[int(clamp(x * FPS, 0, len(a) - 1))]
def zoom(img, z, cy=760):
    if abs(z - 1) < 1e-3: return img
    M = np.float32([[z, 0, CX * (1 - z)], [0, z, cy * (1 - z)]]); return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
CAPS = [(4.54, 5.70, ["E", "aí,", "vai", "mais", "uma"]), (5.70, 6.85, ["da", "série", "“O", "povo", "ontem”,"]), (6.85, 8.10, ["assistindo", "o", "debate", "na", "Globo."])]
HOTW = {"“O", "povo", "ontem”,", "Globo."}
def caption(fr, x, y=1420):
    for a, b, ws in CAPS:
        if not (a <= x < b): continue
        f1, f2 = I(600, 64), I(800, 64); sp = f1.getlength(" "); ff = lambda w: f2 if w in HOTW else f1
        tot = sum(ff(w).getlength(w) for w in ws) + sp * (len(ws) - 1); xx = CX - tot / 2; n = sum(len(w) + 1 for w in ws); k = 0
        lay = Image.new("RGBA", fr.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        for w in ws:
            t0 = a + (b - a - 0.15) * k / n; k += len(w) + 1; al = clamp((x - t0 + 0.05) / 0.12); col = YEL if w in HOTW else WH
            d.text((xx + 3, y + 3 + 10 * (1 - al)), w, font=ff(w), fill=(0, 0, 0, int(150 * al)), anchor="lm")
            d.text((xx, y + 10 * (1 - al)), w, font=ff(w), fill=col + (int(255 * al),), anchor="lm"); xx += ff(w).getlength(w) + sp
        fr.alpha_composite(lay)
def eyebrow(fr, s, y, a=1.0, col=MUT, size=26, track=5):
    f = I(600, size); w = sum(f.getlength(c) + track for c in s) - track; x = CX - w / 2; d = ImageDraw.Draw(fr)
    for c in s: d.text((x, y), c, font=f, fill=col + (int(255 * a),), anchor="lm"); x += f.getlength(c) + track
def circle(fr, x, k):
    L_ = 1.4; p_ = (x * 0.5) % (2 * L_); img = me(1.2 + (p_ if p_ < L_ else 2 * L_ - p_)); pw = 290
    pc = cv2.resize(img[260:1340, 0:1080], (pw, pw), interpolation=cv2.INTER_AREA); m = np.zeros((pw, pw), np.uint8); cv2.circle(m, (pw // 2, pw // 2), pw // 2 - 2, 255, -1)
    pim = Image.fromarray(pc).convert("RGBA"); pim.putalpha(Image.fromarray(m))
    ring = Image.new("RGBA", (pw + 10, pw + 10), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((0, 0, pw + 9, pw + 9), fill=(255, 255, 255, 230)); ring.alpha_composite(pim, (5, 5))
    rs = ring.resize((max(1, int(ring.width * k)), max(1, int(ring.height * k))))
    R.paste(fr, rs, CX + 300 - rs.width / 2, CY0 + CHh - 40 - rs.height / 2, 0.6, 16, (6, 14))
def frame_at(t):
    tt = min(t, EDIT_END - 1e-3); s = seg_at(tt); u = tt - s["t0"]; x = s["a"] + u
    if s["mode"] == "clip":
        bg = me(2.0); base = cv2.resize(cv2.GaussianBlur(cv2.resize(bg, (108, 192)), (0, 0), 3), (W, H)).astype(np.float32) * 0.3
        fr = Image.fromarray(base.astype(np.uint8)).convert("RGBA"); kin = eo(u / 0.4)
        card = cl(x, s["src"]); zc = 1.0 + 0.025 * (0.5 - 0.5 * math.cos(2 * math.pi * u / 6.0))
        card = cv2.warpAffine(card, np.float32([[zc, 0, CW / 2 * (1 - zc)], [0, zc, CHh * 0.45 * (1 - zc)]]), (CW, CHh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        ci = Image.fromarray(R.rounded(card, 28, 0)); R.paste(fr, R.fade(ci, kin), CX - CW / 2, CY0 + 160 * (1 - kin), 0.6, 24, (10, 26))
        eyebrow(fr, "SÉRIE  ·  O POVO ONTEM", 200, kin)
        d = ImageDraw.Draw(fr); d.text((CX - CW / 2 + 4, CY0 + CHh + 30), CREDIT[s["src"]], font=I(400, 22), fill=MUT + (int(200 * kin),), anchor="lm")
        circle(fr, u, bo(clamp((tt - segs[1]["t0"] - 0.4) / 0.35), 1.8))
    else:
        z = 1.0 + 0.03 * (0.5 - 0.5 * math.cos(2 * math.pi * tt / 7.0))
        fr = Image.fromarray(zoom(me(x), z)).convert("RGBA")
        g = np.zeros((420, W, 4), np.uint8); g[..., 3] = (np.sin(np.linspace(0, np.pi, 420)) * 130).astype(np.uint8)[:, None]; fr.alpha_composite(Image.fromarray(g), (0, 1210))
        if s["mode"] == "intro": caption(fr, x)
    cta = clamp((t - (segs[2]["t1"] - 6)) / 0.4) if t > segs[2]["t1"] - 6 else 0.0
    R.BAR.draw_bar(fr, clamp(t / END_IN), "canal", eo((t - 0.2) / 0.6), cta, 0.5 + 0.5 * math.sin(t * 5))
    R.draw_banners(fr, t)
    for sg in segs[1:]:
        if abs(t - sg["t0"]) < 0.07: fr = Image.blend(fr, Image.new("RGBA", fr.size, (255, 255, 255, 255)), (1 - abs(t - sg["t0"]) / 0.07) * 0.3)
    if t >= END_IN: fr.alpha_composite(R.fade(R.end_card(t), clamp((t - END_IN) / 0.35)))
    return fr.convert("RGB")
def capa(out):
    base = cv2.resize(cv2.GaussianBlur(cv2.resize(me(2.0), (108, 192)), (0, 0), 3), (W, H)).astype(np.float32) * 0.3
    fr = Image.fromarray(base.astype(np.uint8)).convert("RGBA")
    c = cl(11.0, "c1")[90:1130]; ci = Image.fromarray(R.rounded(c, 28, 0)).resize((700, int(700 * c.shape[0] / CW)), Image.LANCZOS); R.paste(fr, ci, CX - 350, 560, 0.6, 24, (10, 26))
    d = ImageDraw.Draw(fr); eyebrow(fr, "SÉRIE", 170, 1.0, MUT, 28, 8)
    d.text((CX, 280), "O povo ontem", font=I(800, 104), fill=YEL, anchor="mm"); d.text((CX, 395), "no debate da Globo", font=I(300, 76), fill=WH, anchor="mm")
    k = 1.0; circle(fr, 0.9, 1.15)
    R.BAR.draw_bar(fr, 0.0, "canal"); fr.alpha_composite(R.top, (R.HDX, 0)); fr.convert("RGB").save(out, quality=95)
def main():
    if MODE == "lib": return
    if MODE == "capa": capa(OUTFILE); return
    if MODE.startswith("frames"):
        ts = [float(v) for v in MODE.split(":")[1].split(",")]
        outs = [frame_at(x).resize((360, 640), Image.LANCZOS) for x in ts]
        sh = Image.new("RGB", (360 * len(outs), 640)); [sh.paste(o, (i * 360, 0)) for i, o in enumerate(outs)]; sh.save(OUTFILE, quality=90); return
    vout = f"{V}/video.mp4"
    if not (os.environ.get("REUSE") and os.path.exists(vout)):
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", vout], stdin=subprocess.PIPE)
        for k in range(int(round(TOTAL * FPS))): enc.stdin.write(frame_at(k / FPS).tobytes())
        enc.stdin.close(); enc.wait()
    SR = 48000; n = int(TOTAL * SR)
    for nm in ("me", "c1", "c2"): subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{V}/{nm}.mp4", "-ar", "48000", "-ac", "2", f"{V}/{nm}48.wav"], check=True)
    src = {k: R.readw(f"{V}/{k}48.wav") for k in ("me", "c1", "c2")}
    def rms(c): v = c[np.abs(c).max(1) > 0.01]; return float(np.sqrt((v ** 2).mean())) if len(v) else 1e-6
    ref = rms(src["me"][int(4.5 * SR):int(8.1 * SR)])
    for s_ in segs[1:]: src[s_["src"]] = src[s_["src"]] * (ref / rms(src[s_["src"]][int(s_["a"] * SR):int(s_["b"] * SR)])) * 10 ** (-1.0 / 20)
    vt = np.zeros((n, 2), np.float32)
    for s in segs:
        cc = src[s["src"]][int(s["a"] * SR):int(s["b"] * SR)].copy(); fl = int(0.03 * SR); cc[:fl] *= np.linspace(0, 1, fl)[:, None]; cc[-fl:] *= np.linspace(1, 0, fl)[:, None]
        o = int(s["t0"] * SR); vt[o:o + len(cc)] += cc[:n - o]
    R.writew(f"{V}/voice.wav", vt)
    ev = [(segs[1]["t0"] - 0.12, sfx.whoosh(0.45), 0.25), (segs[2]["t0"] - 0.12, sfx.whoosh(0.45), 0.25), (END_IN - 0.3, sfx.whoosh(0.6), 0.22)]
    sfx.build(ev, TOTAL, f"{V}/sfx.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vout, "-i", f"{V}/voice.wav", "-i", f"{V}/sfx.wav", "-filter_complex",
                    f"[1:a]highpass=f=70[v];[v][2:a]amix=inputs=2:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.8:level=false[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUTFILE], check=True)
    print("done")
main()
