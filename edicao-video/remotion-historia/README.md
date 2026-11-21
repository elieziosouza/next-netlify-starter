# Vídeos de história (canal EZ Vídeos, @ezvideos2979): documentário animado 2D

Formato novo (21/11/2026): vertical 1080x1920, cerca de 1 min, animação 2D plana com cenários em camadas, mapa real animado (Natural Earth pelo pacote `world-atlas`, fronteiras de hoje, avisar na tela), cartelas de data, números animados e legenda. Narração no ElevenLabs (voz Edmilson, eleven_v4, acelerada 7%).

- Primeiro vídeo: **Guerra do Paraguai em 1 minuto** (`src/GuerraParaguai.tsx`, tempos em `src/gp.json`, gerados por `scripts/historia/gp_timings.py` a partir das pausas da voz).
- Dependências extras no projeto Remotion: `world-atlas@2`, `topojson-client@3`, `d3-geo@3`.
- Render: `npx remotion render src/historia/index.tsx GuerraParaguai out/video.mp4 --gl=swangle --crf=17 --muted` (cerca de 30 min por causa dos mapas; para corrigir um trecho, renderizar só `--frames=A-B` e emendar com ffmpeg).
- Capa: still `GuerraParaguaiCapa`, embutida nos primeiros 0,5 s com dissolve.
- Regras: só fatos conferidos com fonte; mortes são estimativas e variam entre historiadores; nada de violência explícita; fonte na tela.

## Quilombo dos Palmares (22/11/2026)
Segundo vídeo: `src/Palmares.tsx` (tempos em `src/pal.json`, gerados por `scripts/historia/pal_timings.py`). Peças comuns (cartela, mapa, legenda, fumaça, colinas) foram exportadas de `GuerraParaguai.tsx`. Novidade: linha do tempo animada no pé da tela (1590 a 2024). Cuidados: sem violência explícita (só silhuetas); a Dandara ficou de fora porque não aparece nas fontes do século XVII; a exposição da cabeça de Zumbi foi omitida; população de Palmares é estimativa.
