"""Abertura padrão desde 30/10/2026: capa parada e muda, feita para o vídeo rodar em loop (o fim emenda no começo sem som de abertura).

Uso: python3 embutir_capa.py VIDEO.mp4 CAPA.jpg SAIDA.mp4
- A capa aparece sozinha por HOLD s (0,5), com um leve avanço de 2%.
- O vídeo entra com fusão de XF s; a fala começa depois de HOLD - XF (0,35 s).
- GLITCH=1 no ambiente volta à abertura antiga (capa de 0,8 s + glitch_intro.py com som), só se ele pedir.
"""
import sys, subprocess, os, tempfile
GLITCH = os.environ.get("GLITCH") == "1"
HOLD, XF = (0.80, 0.18) if GLITCH else (0.50, 0.15)
def main(video, capa, out):
    here = os.path.dirname(os.path.abspath(__file__)); tmp = tempfile.mkdtemp(); mid = os.path.join(tmp, "capa.mp4")
    start = HOLD - XF
    fc = (f"[1:v]scale=1080:1920,zoompan=z='1+0.02*on/({HOLD}*30)':d={int(HOLD * 30) + 1}:s=1080x1920:fps=30,format=yuv420p,setsar=1,trim=duration={HOLD}[c];"
          f"[0:v]fps=30,format=yuv420p,setsar=1[v0];[c][v0]xfade=transition=fade:duration={XF}:offset={start:.3f}[v];"
          f"[0:a]adelay={int(start * 1000)}|{int(start * 1000)}[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-loop", "1", "-t", str(HOLD + 0.1), "-i", capa, "-filter_complex", fc,
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-c:a", "pcm_s16le", mid if GLITCH else out], check=True)
    if GLITCH: subprocess.run([sys.executable, os.path.join(here, "glitch_intro.py"), mid, out, f"{start + XF / 2:.3f}"], check=True)
if __name__ == "__main__":
    main(*sys.argv[1:4])
