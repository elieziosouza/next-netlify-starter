# Teacher Eliezio no Remotion (desde 01/11/2026: "A, an, the" e "Plural")

Mesma identidade das aulas em Python (marinho, amarelo, avatar 3D, karaokê, quiz com contador e confete), desenhada em React.

## Como rodar
Estrutura: `src/kit.tsx` (fundo, avatar, legenda karaokê, quiz com contador e confete, chamada final, `<Licao>` e `<CapaBase>`), um arquivo por aula
(`src/Artigos.tsx`, `src/Plural.tsx`) com as cenas próprias e a capa, e `src/index.tsx` com uma composição por aula.

**Aula nova:** copiar `scripts/aulas/aula_plural.py` (tempos das frases tirados da transcrição, PINS onde o contador abre, expressões, cliques,
whooshes e as chaves `TK` usadas nas cenas) e copiar `src/Plural.tsx` trocando as cenas.

1. `python3 edicao-video/scripts/prep_aula.py $S edicao-video/scripts/aulas/aula_X.py` → `$S/aula_X/vo.wav`, `audio.wav` (voz + efeitos + trilha mixados, -14 LUFS) e `timings.json` (voz original em `$S/aula_X/vo_raw.mp3`).
2. Copiar esta pasta para o scratchpad, `npm install`, e montar `public/`:
   - `public/fonts/`: Anton-Regular, Montserrat-Bold/ExtraBold/Black (de `assets/fonts`).
   - `public/av/av3d_N.png`: avatar (NÃO fica no repositório, que é público). 1 sorrindo, 2 desconfiado, 7 surpreso, 8 piscando, 9 pensando (mão no queixo), 10 bravo, 11 assustado.
   - `src/timings/X.json`: copiado do passo 1.
3. Quadros de teste: `node stills.mjs Plural 2.9 14.6 43.0` · capa: `node stills.mjs PluralCapa 0`.
4. Vídeo: `npx remotion render src/index.tsx Plural out/plural_silent.mp4 --browser-executable=/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell --gl=swangle --crf=17 --muted`
5. Juntar o áudio (`audio.wav`) e finalizar com `scripts/finaliza_teacher.sh VIDEO CAPA SAIDA`.

O navegador próprio do Remotion não baixa neste servidor: usar o chrome-headless-shell já instalado (passo 4).
