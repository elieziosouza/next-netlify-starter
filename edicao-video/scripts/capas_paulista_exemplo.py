import sys; sys.path.insert(0, "/home/user/next-netlify-starter/edicao-video/scripts"); sys.path.insert(0, "/tmp/claude-0/-home-user-next-netlify-starter/698dd744-d40f-5d96-b9e9-72023ae79dbf/scratchpad/work")
import capa
from capa import *
from segment_person import PersonSeg
import grading
G = grading.Fast(grading.cinema_skin, "/tmp/claude-0/-home-user-next-netlify-starter/698dd744-d40f-5d96-b9e9-72023ae79dbf/scratchpad/grade/lut_cinema_pele.npy", 0.06, 6)
seg = PersonSeg("/tmp/claude-0/-home-user-next-netlify-starter/698dd744-d40f-5d96-b9e9-72023ae79dbf/scratchpad/seg/u2net_human_seg.onnx")
U = "/root/.claude/uploads/698dd744-d40f-5d96-b9e9-72023ae79dbf"
ME = f"{U}/e159f5ad-VID-20261011-WA0008.mp4"; A = "/tmp/claude-0/-home-user-next-netlify-starter/698dd744-d40f-5d96-b9e9-72023ae79dbf/scratchpad/v10/aereo.mp4"; O = "/home/user/next-netlify-starter/capas"

def soft_background(img, face, face_y, zoom=1.0):
    """rosto com menos ampliação, sem nitidez agressiva (o vídeo do WhatsApp é 478 px)"""
    sc = W / img.shape[1] * zoom
    M = np.float32([[sc, 0, W / 2 - face[0] * sc], [0, sc, face_y - face[1] * sc]])
    out = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    bl = cv2.GaussianBlur(out, (0, 0), 1.6); out = cv2.addWeighted(out, 1.25, bl, -0.25, 0)
    f = out.astype(np.float32) / 255
    yy, xx = np.mgrid[0:H, 0:W]
    vig = 1 - 0.38 * np.clip(((xx - W / 2) / (W * 0.72)) ** 2 + ((yy - 640) / (H * 0.55)) ** 2, 0, 1)
    f *= vig[..., None]
    g = np.clip((yy - 900) / 520, 0, 1)[..., None] ** 1.3 * 0.93
    f = f * (1 - g) + np.array(NAVY, np.float32) / 255 * g
    return Image.fromarray((np.clip(f, 0, 1) * 255).astype(np.uint8)).convert("RGBA")

def me_on_paulista(t, ta):
    raw = grab(ME, t).copy(); me = grading.face_light(G(raw), 245, 390, gain=0.05)
    me = cv2.fastNlMeansDenoisingColored(me, None, 3, 3, 5, 15)
    m = seg(raw).astype(np.float32); m = np.clip((m - 0.5) * 3.2 + 0.5, 0, 1)
    n, lab = cv2.connectedComponents((m > 0.5).astype(np.uint8))
    r_, g_, b_ = [raw[..., i].astype(np.int16) for i in range(3)]
    blue = ((b_ - r_ > 25) & (b_ > 90)).astype(np.uint8)                      # quadro dos golfinhos (azul), nunca pele
    blue = cv2.dilate(blue, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))); blue[430:] = 0
    m = m * (1 - cv2.GaussianBlur(blue.astype(np.float32), (0, 0), 2.0))
    n, lab = cv2.connectedComponents((m > 0.5).astype(np.uint8))
    if lab[400, 240]: m = m * cv2.dilate((lab == lab[400, 240]).astype(np.uint8), np.ones((5, 5), np.uint8))
    m = cv2.GaussianBlur(cv2.erode(m, np.ones((3, 3), np.uint8)), (0, 0), 1.4)[..., None]
    ae = G(grab(A, ta)[230:840, 655:1265]); sc = 850 / 610; ae = cv2.resize(ae, (int(610 * sc) + 1, 850)); x0 = (ae.shape[1] - 478) // 2
    bg = cv2.GaussianBlur(ae[:, x0:x0 + 478], (0, 0), 2.4).astype(np.float32) * 0.68
    return np.clip(me * m + bg * (1 - m), 0, 255).astype(np.uint8)

def crowd_only(ta):
    ae = G(grab(A, ta)[0:840, 655:1265]); ae = cv2.fastNlMeansDenoisingColored(ae, None, 3, 3, 5, 15)
    return ae

capa.background = lambda frame, face=(245, 390), zoom=1.0, face_y=700: soft_background(frame, face, face_y, 1.0)
build(me_on_paulista(12.0, 12.0), "PAULISTA ONTEM", [("mid_white", "CONTANDO VITÓRIA"), ("big_white", "ANTES DO TEMPO?"), ("stamp", "OLHA A PAULISTA"), ("rule", "")], face=(245, 390), face_y=700).convert("RGB").save(f"{O}/paulista_capa_A_olha_a_paulista.jpg", quality=95)
build(me_on_paulista(8.5, 20.0), "2º TURNO", [("big_gold", "33 MILHÕES"), ("mid_white", "NÃO VOTARAM NO 1º TURNO"), ("stamp", "DIA 25 VAI SER HISTÓRICO"), ("rule", "")], face=(245, 390), face_y=700).convert("RGB").save(f"{O}/paulista_capa_B_33_milhoes.jpg", quality=95)
# C: sem rosto, só a multidão
def crowd_bg(img, face=None, face_y=None, zoom=None):
    sc = max(W / img.shape[1], 1500 / img.shape[0]); big = cv2.resize(img, (int(img.shape[1] * sc) + 1, int(img.shape[0] * sc) + 1), interpolation=cv2.INTER_CUBIC)
    x0 = (big.shape[1] - W) // 2; canvas = np.zeros((H, W, 3), np.uint8); canvas[:min(H, big.shape[0])] = big[:H, x0:x0 + W]
    f = canvas.astype(np.float32) / 255; yy, xx = np.mgrid[0:H, 0:W]
    g = np.clip((yy - 760) / 600, 0, 1)[..., None] ** 1.2 * 0.95
    f = f * (1 - g) + np.array(NAVY, np.float32) / 255 * g
    f *= (1 - 0.3 * np.clip(((xx - W / 2) / (W * 0.8)) ** 2 + ((yy - 600) / (H * 0.6)) ** 2, 0, 1))[..., None]
    return Image.fromarray((np.clip(f, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
capa.background = crowd_bg
build(crowd_only(12.0), "AV. PAULISTA · 11/10", [("mid_white", "TEM BOLSONARISTA"), ("big_white", "CONTANDO"), ("big_gold", "VITÓRIA"), ("stamp", "ANTES DO TEMPO"), ("rule", "")], top=1020).convert("RGB").save(f"{O}/paulista_capa_C_sem_rosto.jpg", quality=95)
