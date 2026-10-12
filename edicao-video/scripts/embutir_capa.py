"""Abertura padrão: capa sozinha + glitch, e só depois o vídeo começa (o glitch nunca fica em cima da fala).

Uso: python3 embutir_capa.py VIDEO.mp4 CAPA.jpg SAIDA.mp4
- A capa aparece sozinha por HOLD s, com um leve avanço de 2%.
- O vídeo entra com fusão de XF s; a fala começa depois de HOLD - XF (0,62 s).
- O glitch (glitch_intro.py) cobre só a capa e a passagem; o som do glitch dura 0,32 s.
"""
import sys, subprocess, os, tempfile
HOLD, XF = 0.80, 0.18
def main(video, capa, out):
    here = os.path.dirname(os.path.abspath(__file__)); tmp = tempfile.mkdtemp(); mid = os.path.join(tmp, "capa.mp4")
    start = HOLD - XF
    fc = (f"[1:v]scale=1080:1920,zoompan=z='1+0.02*on/({HOLD}*30)':d={int(HOLD * 30) + 1}:s=1080x1920:fps=30,format=yuv420p,setsar=1,trim=duration={HOLD}[c];"
          f"[0:v]fps=30,format=yuv420p,setsar=1[v0];[c][v0]xfade=transition=fade:duration={XF}:offset={start:.3f}[v];"
          f"[0:a]adelay={int(start * 1000)}|{int(start * 1000)}[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-loop", "1", "-t", str(HOLD + 0.1), "-i", capa, "-filter_complex", fc,
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-c:a", "pcm_s16le", mid], check=True)
    subprocess.run([sys.executable, os.path.join(here, "glitch_intro.py"), mid, out, f"{start + XF / 2:.3f}"], check=True)
if __name__ == "__main__":
    main(*sys.argv[1:4])
