# Teacher Eliezio no Remotion (teste de 01/11/2026, aula "A, an, the")

Mesma identidade das aulas em Python (marinho, amarelo, avatar 3D, karaokê, quiz com contador e confete), desenhada em React.

## Como rodar
1. `python3 edicao-video/scripts/prep_aula_artigos.py $S` → `$S/aula_artigos/vo.wav`, `audio.wav` (voz + efeitos + trilha mixados, -14 LUFS) e `timings.json`.
2. Copiar esta pasta para o scratchpad, `npm install`, e montar `public/`:
   - `public/fonts/`: Anton-Regular, Montserrat-Bold/ExtraBold/Black (de `assets/fonts`).
   - `public/av/av3d_N.png`: avatar (NÃO fica no repositório, que é público). 1 sorrindo, 2 desconfiado, 7 surpreso, 8 piscando, 9 pensando (mão no queixo), 10 bravo, 11 assustado.
   - `src/timings.json`: copiado do passo 1.
3. Quadros de teste: `node stills.mjs Aula 2.9 14.6 43.0` · capa: `node stills.mjs Capa 0`.
4. Vídeo: `npx remotion render src/index.tsx Aula out/aula_silent.mp4 --browser-executable=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell --gl=swangle --crf=17 --muted`
5. Juntar o áudio (`audio.wav`) e finalizar com `scripts/finaliza_teacher.sh VIDEO CAPA SAIDA`.

O navegador próprio do Remotion não baixa neste servidor: usar o chrome-headless-shell já instalado (passo 4).
