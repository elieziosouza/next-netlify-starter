"""Capas do corte "nove dedos" no estilo do canal: rosto dele grande (fundo real, boca fechada), poucas palavras e o Lula do debate como destaque."""
import sys, importlib.util, subprocess
import numpy as np, cv2
from PIL import Image, ImageDraw
S = sys.argv[1]
spec = importlib.util.spec_from_file_location("cx", f"{S}/work/capas_exercito.py"); sys.argv = [sys.argv[0], S]
src = open(f"{S}/work/capas_exercito.py").read().split("scene(\"QUEREM")[0]          # só as funções, sem gerar as capas do exército
ns = {"__name__": "cx"}; exec(compile(src, "capas_exercito", "exec"), ns)
M = ns["M"]; R = ns["R"]; word = ns["word"]; W, H, CX = R.W, R.H, R.CX; YEL = ns["YEL"]; WHITE = ns["WHITE"]; BLUE = ns["BLUE"]; BAR = R.BAR
V = f"{S}/v60"; M.ME = f"{V}/raw.mp4"; M._ch.clear(); M._gr.clear()
p = subprocess.run(["ffmpeg", "-v", "error", "-ss", "16.5", "-i", f"{S}/v59/cl.mp4", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
lula = np.frombuffer(p, np.uint8).reshape(848, 480, 3)[20:520]; lula = cv2.LUT(lula, R.LUT)
def scene(t1, t2, band, bcol, btc, name, emo, tface=16.5):
    img = Image.fromarray(M.NAVY_BG.copy()).convert("RGBA")
    me, idx = M.graded(tface); m = me[190:1600]; top = 860; ph = H - top; fw = int(m.shape[1] * ph / m.shape[0]); fw = min(fw, 2 * (W - CX) - 4)
    fg = cv2.resize(m, (fw, ph), interpolation=cv2.INTER_AREA); x0 = CX - fw // 2
    lay = np.zeros((ph, W, 4), np.uint8); lay[:, x0:x0 + fw, :3] = fg
    al = np.ones((ph, fw), np.float32); al[:200] *= np.linspace(0, 1, 200)[:, None]; al[:, :70] *= np.linspace(0, 1, 70)[None]; al[:, -70:] *= np.linspace(1, 0, 70)[None]
    lay[:, x0:x0 + fw, 3] = (al * 255).astype(np.uint8); img.alpha_composite(Image.fromarray(lay), (0, top))
    c = Image.fromarray(R.rounded(lula, 22, 5)).resize((400, 417), Image.LANCZOS).rotate(-3, resample=Image.BICUBIC, expand=True)
    c = c.resize((int(c.width * 0.9), int(c.height * 0.9)), Image.LANCZOS); R.paste(img, c, CX + 80, 450, 0.8, 26, (10, 26))
    R.pill(img, "LULA NO DEBATE", CX + 80 + c.width / 2, 450 + c.height - 30, 1.0, fill=BLUE, size=28)
    
    word(img, t1, 190, 175, WHITE); word(img, t2, 360, 150, YEL)
    word(img, band, 905, 60, btc, band=bcol, tcol=btc, rot=-2)
    BAR.draw_bar(img, 0.0, "canal"); img.alpha_composite(R.top, (R.HDX, 0)); img.convert("RGB").save(f"{V}/{name}.jpg", quality=95)
scene("“NOVE DEDOS”?", "FALTOU RESPEITO", "FALTA ARGUMENTO, SOBRA OFENSA", (150, 20, 30), WHITE, "capa_A", "😡")
scene("ELE ZOMBOU", "DO TRABALHADOR?", "OLHA A RESPOSTA DO LULA", BLUE, WHITE, "capa_B", "👷")
sheet = Image.new("RGB", (720, 640)); [sheet.paste(Image.open(f"{V}/capa_{k}.jpg").resize((360, 640)), (i * 360, 0)) for i, k in enumerate("AB")]
sheet.save(f"{V}/capas_AB.jpg", quality=90)
