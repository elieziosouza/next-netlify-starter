"""Remix do áudio do react do Lula com o som original do reels nos trechos da Paulista."""
import sys, subprocess, wave, numpy as np
S = sys.argv[1]; V = f"{S}/v11"; OUT = sys.argv[2]
sys.argv = [sys.argv[0], S, "/dev/null", "info"]
exec(open(f"{S}/work/render_lula.py").read().replace("\nmain()\n", "\n"))
SR = 48000
def readw(p):
    w = wave.open(p); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, w.getnchannels()) / 32768
    return a if a.shape[1] == 2 else np.repeat(a, 2, 1)
def writew(p, a):
    with wave.open(p, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(a, -1, 1) * 32000).astype(np.int16).tobytes())
n = int(TOTAL * SR)
clip = readw(f"{V}/lula_vox.wav"); track = np.zeros((n, 2), np.float32); gate = np.zeros(n, np.float32)
for s in segs:
    if s["src"] != "cl": continue
    a0, a1 = int(s["ca"] * SR), int(s["cb"] * SR); t0 = int(s["t0"] * SR); piece = clip[a0:a1].copy()
    f = int(0.08 * SR); env = np.ones(len(piece)); env[:f] = np.linspace(0, 1, f); env[-f:] = np.linspace(1, 0, f)
    track[t0:t0 + len(piece)] += piece * env[:, None]
for s in segs:                                   # trilha nossa sai nos blocos da Paulista (com rampas)
    if s["src"] == "cl": gate[int(s["t0"] * SR):int(s["t1"] * SR)] = 1
k = int(0.35 * SR); gate = np.convolve(gate, np.ones(k) / k, "same")
mus = readw(f"{V}/music.wav")[:n]; mus = np.pad(mus, ((0, n - len(mus)), (0, 0))) * (1 - gate)[:, None]
writew(f"{V}/paulista_snd.wav", track); writew(f"{V}/music_g.wav", mus)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{V}/video.mp4", "-i", f"{V}/voice_edit.wav", "-i", f"{V}/sfx.wav", "-i", f"{V}/music_g.wav", "-i", f"{V}/paulista_snd.wav",
                "-filter_complex",
                "[1:a]apad,asplit=3[vox1][key][key2];[2:a]volume=0.8,apad[sf];[3:a]volume=0.30[mus];[4:a]volume=0.62[pl];"
                "[mus][key]sidechaincompress=threshold=0.02:ratio=7:attack=30:release=600[musd];"
                "[pl][key2]sidechaincompress=threshold=0.02:ratio=5:attack=20:release=450[pld];"
                f"[vox1][sf][musd][pld]amix=inputs=4:normalize=0:duration=longest,atrim=0:{TOTAL:.2f},alimiter=limit=0.79:level=false:asc=1[a]",
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", OUT], check=True)
print("remix ok")
