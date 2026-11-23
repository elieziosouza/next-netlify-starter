"""Fecha cada versão: áudio tratado (+ efeitos na caprichada), capa embutida, x264 em duas passagens, fMP4 cortado em partes de ~12 MB e prévia leve."""
import sys, os, subprocess, wave, importlib.util
import numpy as np
os.environ["MODO"] = sys.argv[2] if len(sys.argv) > 2 else "sem_id"
spec = importlib.util.spec_from_file_location("montar", "montar.py"); M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
sys.path.insert(0, "/home/user/next-netlify-starter/edicao-video/scripts"); import sfx
nome = sys.argv[1]            # ex.: v5_prem
modo = os.environ["MODO"]; capa = sys.argv[3]; saida = sys.argv[4]
TOTAL = M.TOTAL; D = f"{TOTAL:.2f}"
wav = f"{nome}_a.wav"
filtros = "aresample=48000,highpass=f=70,afftdn=nr=9:nf=-45,acompressor=threshold=0.04:ratio=3.5:attack=10:release=250:makeup=2.4,equalizer=f=3000:t=q:w=1:g=2"
entrada = ["-i", wav]
if modo != "limpo":
    ev = [(max(0.02, t - 0.12), sfx.whoosh(0.4), 0.10) for t in M.FX_AT]
    if modo == "premium":
        B0 = 8.0 + M.OFF
        ev += [(0.2, sfx.thud(0.5), 0.30), (8.2, sfx.click(4), 0.14), (B0 + 0.3, sfx.click(4), 0.14), (B0 + 76.0, sfx.paper(0.5), 0.30), (B0 + 76.05, sfx.thud(0.35), 0.18)]
    sfx.build(ev, TOTAL, f"{nome}_sfx.wav"); entrada += ["-i", f"{nome}_sfx.wav"]
    fc = f"[0:a]{filtros}[v];[v][1:a]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=9,afade=t=out:st={TOTAL-0.6:.2f}:d=0.6[a]"
else:
    fc = f"[0:a]{filtros},loudnorm=I=-14:TP=-1.5:LRA=9,afade=t=out:st={TOTAL-0.6:.2f}:d=0.6[a]"
subprocess.run(["ffmpeg", "-v", "error", "-y"] + entrada + ["-filter_complex", fc, "-map", "[a]", "-ar", "48000", "-c:a", "pcm_s16le", f"{nome}_audio.wav"], check=True)
FC = "[1:v]scale=1080:1920,format=yuva420p,fade=t=out:st=0.45:d=0.32:alpha=1[c];[0:v][c]overlay=0:0:eof_action=pass,format=yuv420p[v]"
v = f"{nome}.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", v, "-loop", "1", "-t", "1", "-framerate", "30", "-i", capa, "-filter_complex", FC, "-map", "[v]", "-c:v", "libx264", "-preset", "slow", "-b:v", "2000k", "-pass", "1", "-passlogfile", f"p_{nome}", "-an", "-f", "null", "/dev/null"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", v, "-loop", "1", "-t", "1", "-framerate", "30", "-i", capa, "-i", f"{nome}_audio.wav", "-filter_complex", FC, "-map", "[v]", "-map", "2:a", "-map_metadata", "-1",
                "-fflags", "+bitexact", "-flags:v", "+bitexact", "-flags:a", "+bitexact", "-c:v", "libx264", "-preset", "slow", "-b:v", "2000k", "-pass", "2", "-passlogfile", f"p_{nome}", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", "-shortest", f"{saida}.mp4"], check=True)
for f in os.listdir("."):
    if f.startswith(f"p_{nome}"): os.remove(f)
# fMP4 + partes de 12 MB (a página junta as partes ao baixar) e prévia leve
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{saida}.mp4", "-c", "copy", "-map_metadata", "-1", "-movflags", "frag_keyframe+empty_moov+default_base_moof", f"{saida}_frag.mp4"], check=True)
os.makedirs(f"parts_{saida}", exist_ok=True)
subprocess.run(["split", "-b", "12000000", "-d", "-a", "1", f"{saida}_frag.mp4", f"parts_{saida}/{saida}-parte-"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{saida}.mp4", "-vf", "scale=540:960", "-c:v", "libx264", "-preset", "slow", "-b:v", "430k", "-c:a", "aac", "-b:a", "56k", "-ac", "1", "-map_metadata", "-1", "-movflags", "+faststart", f"{saida}_previa.mp4"], check=True)
print("pronto", saida, os.path.getsize(f"{saida}.mp4") / 1e6, "MB", sorted(os.listdir(f"parts_{saida}")))
