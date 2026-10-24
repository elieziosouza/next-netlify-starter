# Estilo fotógrafo: stories de festa em tempo real

Para o @esouzafotografia postar durante a festa (casamento, aniversário, evento). Ele manda os vídeos
conforme grava e recebe de volta o story pronto em poucos minutos.

## Como roda

```bash
python3 edicao-video/estilo-fotografo/story_festa.py saida.mp4 clipe1.mp4 clipe2.mov \
  --texto "Ana & Pedro" --sub "24.10.2026"
```

- **Cortes:** o script dá nota a cada décimo de segundo (nitidez, movimento da cena, energia do som) e descarta
  tremido forte e trecho escuro. Escolhe as melhores janelas de um compasso (2 s na festa) e corta na batida.
- **Trilha:** própria, sem direitos autorais (`trilha_festa.py`). `--estilo festa` (120 BPM, batida 4x4) ou
  `--estilo romantico` (84 BPM, para entrada dos noivos, valsa, cerimônia). O som original fica por baixo a 15% (`--som`).
- **Lettering:** só quando faz sentido (nome dos noivos, aniversariante, momento: "A entrada", "Primeira dança").
  DM Serif Display branco com sombra suave no terço de cima, linha menor espaçada em Montserrat. Entra aos 0,4 s e sai
  antes da metade do vídeo para não esconder a festa.
- **Marca d'água (24/10/2026, pedido dele: tudo minimalista):** ícone do Instagram em traço fino + `esouzafotografia`
  em Montserrat Regular 24 com letras espaçadas, branco translúcido e sombra quase invisível. Centralizada embaixo,
  acima da área de resposta do Instagram, o vídeo todo. Sem logo colorido, sem caixa, sem fundo.
- **Formato:** 1080x1920, 30 fps, H.264. Vídeo vertical preenche a tela; horizontal fica inteiro no meio com fundo
  desfocado do próprio vídeo.
- **Cor:** só um toque leve de contraste e saturação. Pele não é mexida.

Padrão: 15 s por story (`--dur`). Para Reels, até 60 s.

## Acabamento completo ("edição AAA", 24/10/2026): `story_aaa.py`

Padrão quando ele pede "edição AAA" ou capricho. Leva ~1min20 para 16 s (o modo rápido `story_festa.py` leva ~20 s).

```bash
python3 edicao-video/estilo-fotografo/story_aaa.py saida.mp4 clipe1.mp4 clipe2.mp4 ... --dur 16 --texto "Os detalhes"
```

- **Ordem:** a dos clipes na linha de comando (abrir com detalhe bonito, fechar com o plano geral).
- **Cortes:** um trecho contínuo por clipe (panorâmica nunca leva salto no meio), escolhido por nitidez, movimento e
  pouco tremido; duração em batidas inteiras.
- **Estabilização:** vidstab em 2 passadas (smoothing 18, optzoom). Celular com estabilizador já chega firme: o ganho
  medido foi de 15 a 25% nos detalhes; smoothing maior (30 a 45) não melhorou a panorâmica.
- **Limpeza e nitidez:** hqdn3d leve antes, escala Lanczos e `cas=0.45` depois (compensa a compressão do WhatsApp).
- **Cor (`cor_fotografo.py`, "luz natural"):** por clipe, branco corrigido pelos tons neutros (parede, toalha, prato)
  a 70% e exposição para meio-tom luminoso (nunca escurece o clipe). Look único: ombro suave nos claros, curva em S
  delicada, preto levemente aberto, vibração que protege o que já é saturado (rosas, morango), verde da folhagem
  puxado para oliva e calor leve nos claros.
- **Movimento:** aproximação e afastamento suaves alternados (5%) em cada cena.
- **Transições:** a cada dois cortes, zoom com desfoque radial e brilho leve, com whoosh baixinho; os demais são corte
  seco na batida.
- **Lettering:** sai do desfoque subindo 18 px, sai antes da metade.
- **Tela final (1,9 s):** último plano desfoca e escurece, ícone + esouzafotografia maior no centro. A marca d'água
  pequena some nessa hora.

## Versão para cliente / organizador (24/10/2026)

`--sem-marca`: tira a marca d'água e, na tela final, mostra o lettering (ex.: "Beth · 70 anos") no lugar da marca.
Na festa, entregar sempre as duas: `..._esouza.mp4` (com marca, para o Instagram dele) e `..._organizador.mp4`.

Lettering de abertura no estilo storymaker de evento: nome curto em DM Serif 176 px, linha "70 ANOS" em Montserrat
SemiBold 36 espaçado com filetes, e uma sombra difusa (sem bordas) atrás do texto para ler sobre flores e decoração.

## Bastidores e música livre (24/10/2026)

- **Bastidores ("eu fotografando"):** abrir com ele já em ação (andando visto por trás, fotografando), **não** com ele
  parado olhando para a câmera (ele tirou essa abertura em 24/10/2026), e fechar com ele saindo de cena andando com a câmera. Lettering `--pos baixo` (no peito) para nunca cobrir o rosto: no alto, a sombra do texto
  escureceu a testa dele. Versão só dele (com marca); não precisa da versão do organizador.
- **Fixar um trecho:** `clipe.mp4@0.1+3` começa em 0,1 s e dura ~3 s (arredondado na batida).
- **Música livre:** `--musica faixa.mp3` (ver `musica.py`). Faixas do Kevin MacLeod no Wikimedia Commons, licença
  CC BY 3.0, exigem crédito na legenda: `Música: "Nome da faixa", Kevin MacLeod (incompetech.com), CC BY 3.0`.
  O upload.wikimedia.org limita IP compartilhado (429, retry-after 600): baixar uma faixa por vez, com intervalo.
  Epidemic Sound e Pixabay estão bloqueados na rede da sessão; ele baixa e manda o arquivo.

## Recursos de storymaker (24/10/2026, "a edição está genérica e com poucos recursos")

Ligados por padrão no `story_aaa.py` (`--simples` volta ao básico). Código em `efeitos.py`.

- **Texto atrás da pessoa:** se a abertura tem gente, o título entra gigante (DM Serif, largura da tela) atrás dela
  (U2Net). A cabeça cobre a metade de baixo das letras: dá profundidade e ainda se lê. A linha de baixo
  ("BETH · 70 ANOS") fica na frente, no peito. Sem pessoa, o título fica na frente com sombra difusa.
- **Letras animadas:** cada letra sobe e aparece, uma depois da outra (45 ms).
- **Clique da foto:** 1 por story (2 acima de 14 s), no meio: congela no fim do trecho, flash, som de obturador
  sintetizado e o quadro vira foto com borda branca (mais larga embaixo), inclinada, com sombra, sobre o próprio
  quadro desfocado. Corte seco depois.
- **Rampa de velocidade:** até 2 trechos com sobra de clipe: começa ~2x e assenta em ~0,75x (mistura de quadros).
- **Cortes alternados:** zoom com desfoque (whoosh) · vazamento de luz quente (swish) · seco na batida.
- **Pulso:** no tempo 3 de cada compasso, zoom de 3% e brilho rápido, longe dos cortes.
- **Cinema:** brilho suave nos claros e granulação fina, em todos os quadros.
- Tempo: ~3 min para 18 s (a máscara da pessoa roda a cada 2 quadros só enquanto o título está na tela).

## Modo cinema / roteiro (24/10/2026, "edição avançadíssima, dinamismo e emoção"): `story_cinema.py`

Padrão a partir de agora. Inspirado em filme de casamento/evento: o vídeo conta uma história em 4 atos, e trilha,
imagem e efeitos seguem o mesmo arco (17 s a 120 BPM).

1. **Abertura (8 tempos):** sai do preto, faixas de cinema (letterbox 210 px), 2 planos em câmera lenta (0,6x),
   vazamento de luz entre eles, piano + som real da festa por baixo, título com letras subindo (atrás da pessoa).
2. **Subida (4 tempos):** cortes acelerando 1, 1, ½, ½, ¼, ¼, ¼, ¼ tempo; zoom crescendo 10%; faixas apertam;
   riser, caixa acelerando e meio tempo de silêncio.
3. **Explosão (16 tempos):** flash branco, impacto e tremor de câmera; faixas abrem em 0,12 s; corte em toda batida
   com pulso de zoom e brilho; cortes chicote (desfoque horizontal, direção alternada), zoom e luz; tela em 3 colunas
   com divisória branca entrando uma a uma; stutter (repete 1/3 de tempo); rampas (lento e acelera para o corte).
4. **Final (6 tempos):** faixas voltam, câmera lenta 0,7x, clique da foto e tela da marca (ou do título, na versão
   do organizador).

- Ordem: o 1º clipe abre e o último fecha (`clipe.mp4@0.2` fixa o início); os do meio entram em rodízio.
- Trilha própria `trilha_cinema.py` (piano Am F C G, riser, explosão com impacto). Com `--musica`, a explosão é
  colocada na maior subida de energia da faixa.
- Vinheta leve, brilho de cinema e grão em tudo. Tempo: ~5 min para 17 s.
- **Com 1 ou 2 vídeos (24/10/2026, pedido dele):** se ele manda (ou escolhemos) um plano-sequência longo, o
  `story_cinema.py` conta a história em ordem cronológica dentro do vídeo principal (o mais longo): os trechos de
  subida e explosão são distribuídos do começo ao fim dele, cada um no melhor ponto da sua fatia. O 2º vídeo fecha.
  Nos bastidores da Beth (30 s seguindo ele + 4 s saindo de cena) ficou melhor que misturar 7 vídeos curtos:
  história contínua em vez de pulos de lugar. Para mesa/decoração, vários clipes curtos continuam fazendo sentido.

## Cinematográfico com 1 vídeo (24/10/2026, "queria cinematográfico, faça com apenas 1 vídeo"): `story_filme.py`

Quando ele pede **cinematográfico**, é linguagem de filme, não de storymaker de festa: menos efeito, mais clima.

```bash
python3 edicao-video/estilo-fotografo/story_filme.py saida.mp4 "video.mp4@4.0" --texto "Bastidores" --sub "Beth · 70 anos"
```

- **5 planos longos em ordem** dentro do mesmo vídeo (4 · 3,5 · 3,5 · 3 · 4 s = 18 s), cada um no melhor ponto
  (nítido, pouco tremor) da sua fatia. `@4.0` pula o começo (ele não quer abrir parado olhando para a câmera).
- **Câmera lenta de verdade:** `minterpolate` (mci, 60 quadros) só nos trechos usados, em paralelo (~11 s de
  processamento por segundo de fonte, por processo). Planos a 0,5x/0,6x; o 3º é **rampa** de 1x para 0,3x no
  momento-chave, com **obturador** e o **ápice da trilha** (tímpano + violinos) caindo juntos.
- **Cor de cinema** (`cor_fotografo.look_filme`): luz natural + saturação 82%, S mais firme, preto aveludado,
  sombras levemente frias, claros e pele quentes.
- **Faixas de cinema** de 230 px o vídeo todo; passagens pelo preto entre planos (corte seco do 2º para o 3º, para
  manter a ação); empurrão lento alternado (6%); brilho nos claros, grão e vinheta mais marcada.
- **Título tipo crédito:** Montserrat Medium 46 em caixa alta bem espaçada + linha menor, acima da faixa de baixo.
- **Marca:** pequena dentro da faixa preta de baixo; no fim, tudo vai ao preto e a marca aparece no centro.
- **Trilha** `trilha_filme.py`: 72 BPM, piano em arpejo + cordas crescendo, ápice, acorde maior com cauda longa.
- Tempo: ~3 min para 18 s.
