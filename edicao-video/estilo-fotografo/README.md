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
