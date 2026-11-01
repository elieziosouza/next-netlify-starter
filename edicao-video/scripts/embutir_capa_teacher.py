"""Abertura do canal Teacher Eliezio, feita para o vídeo rodar em loop (pedido de 30/10/2026): capa parada por HOLD s,
sem riser e sem clarão, e o vídeo entra com zoom curto. Nenhum som marca o recomeço, então o fim emenda no começo.
(O riser antigo continua em sfx.riser, se ele pedir de volta.)

Uso: python3 embutir_capa_teacher.py VIDEO.mp4 CAPA.jpg SAIDA.mp4
"""
import sys, subprocess
HOLD, XF = 0.50, 0.20
def main(video, capa, out):
    start = HOLD - XF; nf = int(HOLD * 30) + 1
    fc = (f"[1:v]scale=1080:1920,zoompan=z='1+0.03*on/{nf}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={nf}:s=1080x1920:fps=30,format=yuv420p,setsar=1,trim=duration={HOLD}[c];"
          f"[0:v]fps=30,format=yuv420p,setsar=1[v0];[c][v0]xfade=transition=zoomin:duration={XF}:offset={start:.3f},setpts=PTS-STARTPTS[v];"
          f"[0:a]adelay={int(start * 1000)}|{int(start * 1000)}[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-loop", "1", "-t", str(HOLD + 0.1), "-i", capa,
                    "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-c:a", "pcm_s16le", out], check=True)
    print("ok")
if __name__ == "__main__":
    main(*sys.argv[1:4])
