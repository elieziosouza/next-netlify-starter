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
