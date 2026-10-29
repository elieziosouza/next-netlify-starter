"""Abertura do canal Teacher Eliezio: capa sozinha com zoom lento + riser subindo, e no corte do riser o vídeo entra com zoom e
clarão branco. (O canal Eliezio Souza usa o glitch de embutir_capa.py; aqui é outro efeito de propósito, para os canais não se misturarem.)

Uso: python3 embutir_capa_teacher.py VIDEO.mp4 CAPA.jpg SAIDA.mp4
"""
import sys, os, subprocess, tempfile, wave
import numpy as np
HOLD, XF = 1.10, 0.30
def main(video, capa, out):
    here = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, here); tmp = tempfile.mkdtemp()
    import sfx
    start = HOLD - XF; cut = start + XF / 2
    r = sfx.riser(dur=cut, tail=0.7); r = np.concatenate([r, np.zeros((sfx.SR, 2), np.float32)])
    with wave.open(os.path.join(tmp, "riser.wav"), "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sfx.SR); w.writeframes((np.clip(r, -1, 1) * 32000).astype(np.int16).tobytes())
    nf = int(HOLD * 30) + 1
    fc = (f"[1:v]scale=1080:1920,zoompan=z='1+0.06*(on/{nf})^2':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={nf}:s=1080x1920:fps=30,format=yuv420p,setsar=1,trim=duration={HOLD}[c];"
          f"[0:v]fps=30,format=yuv420p,setsar=1[v0];[c][v0]xfade=transition=zoomin:duration={XF}:offset={start:.3f}[x];"
          f"color=white:s=1080x1920:r=30:d=0.5,format=yuva420p,colorchannelmixer=aa=0.85,fade=t=out:st=0:d=0.35:alpha=1[fl];"
          f"[x][fl]overlay=enable='between(t,{cut - 0.02:.3f},{cut + 0.4:.3f})':eof_action=pass,setpts=PTS-STARTPTS[v];"
          f"[0:a]adelay={int(start * 1000)}|{int(start * 1000)}[a0];[2:a]volume=0.25[rs];[a0][rs]amix=inputs=2:normalize=0:duration=first[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-loop", "1", "-t", str(HOLD + 0.1), "-i", capa, "-i", os.path.join(tmp, "riser.wav"),
                    "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-c:a", "pcm_s16le", out], check=True)
    print("ok")
if __name__ == "__main__":
    main(*sys.argv[1:4])
