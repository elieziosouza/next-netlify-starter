# Kit de edição de vídeo: Eliezio Souza

Padrão visual e técnico dos vídeos verticais do canal (Opinião · Atualidades · Reações).
Tudo aqui foi aprovado em outubro de 2026 e serve de base para os próximos vídeos.
Cada vídeo novo deve seguir este guia e, quando algo for melhorado, o guia é atualizado.

## 1. Preferências do Eliezio (prioridade máxima)

1. **Nada de cara de amador.** Visual de telejornal: tipografia limpa, linhas finas douradas, números grandes. Sem partículas, sem desenho animado, sem check verde, sem recorte girando.
2. **Não cortar o Eliezio.** Na tela dividida ele aparece inteiro: cabeça completa, folga acima e ombros. Nada fica por cima da cabeça.
3. **Zooms discretos.** No máximo 5 a 7%, com transição suave de 0,6 s, e só em falas fortes. Nunca dar zoom de tranco.
4. **Começar com ele em tela cheia** e ir editando conforme o vídeo avança: tela dividida quando entra um assunto com dado, volta para tela cheia entre os assuntos.
5. **Dados conferidos.** Todo número em painel tem fonte. Se não achar fonte confiável, o painel mostra só a descrição, sem número.
6. **Sem logotipo oficial** de governo ou de jornal. Usa o nome do programa ou a manchete real, com arte própria e a fonte escrita.
7. **Áudio:** sem eco, sem mudança na voz. Só volume padronizado, música baixa e efeitos discretos.

## 2. Identidade visual

| Item | Valor |
|---|---|
| Azul-marinho (painéis) | `#05223A` / `#0A2C4B`, fundo em degradê radial `#0B3458 → #030B18` |
| Dourado | `#D6B674` (destaques), `#F5E2B0` (dourado claro) |
| Texto | Branco `#FFFFFF`; secundário branco a 55% |
| Fonte | Montserrat (ExtraBold nas legendas, Black nos números, Bold/SemiBold no resto), arquivos em `assets/fonts` |
| Topo | `assets/topo.jpg`, com as margens escuras laterais cortadas e esticado de ponta a ponta. Entra deslizando no início, com brilho dourado passando a cada ~13 s |
| Rodapé | `assets/rodape.jpg`, com barra de progresso dourada fina logo acima |
| Correção de cor | Leve curva em S, sombras levemente frias, altas levemente quentes, vinheta 24%, granulação suave |
| Tela final | 3 s: fundo azul, topo ampliado no centro, "SIGA PARA MAIS" e "OPINIÃO • ATUALIDADES • REAÇÕES" |

Exemplos aprovados em `exemplos/`.

## 3. Legendas

- Estilo **karaokê**: Montserrat ExtraBold 66–72 px, MAIÚSCULAS, branco com contorno azul-marinho.
- A palavra falada fica numa **pílula dourada** que desliza para a próxima palavra (0,1 s).
- No máximo 2 linhas, até 5 palavras por bloco, quebra equilibrada.
- Entrada da frase com "pop" curto (escala 86% → 100% em 0,2 s).
- Posição: y ≈ 1450 em tela cheia; y ≈ 1585 (dentro do quadro) na tela dividida.
- Números de dinheiro podem virar dígitos ("20 REAIS", "AGORA SÃO 50").
- Se o vídeo chegar com legenda gravada, ela é apagada quadro a quadro (`capmask.py` + `clean.py`) antes de colocar a nova.

## 4. Layouts

**Tela cheia:** vídeo 1080×1920, topo e rodapé por cima, legenda no peito.

**Tela dividida** (`render_tela_dividida.py`):
- Painel de dados no alto: x 40–1040, y logo abaixo do topo até 772, cantos 26 px, borda dourada fina, sombra suave.
- Quadro do Eliezio embaixo: x 154–926, y 798–1680, escala 1,615, com 125 px de folga acima da cabeça, borda dourada de 2 px e sombra.
- Transição de entrada e saída: 0,7 s com aceleração suave (ease in-out).

**Notícia na imprensa** (`render_recortes_noticia.py`): mesmo layout dividido, com o recorte de jornal (`cards.py`) no painel "NA IMPRENSA". O recorte traz a manchete real com a fonte embaixo, marca-texto amarelo animado e carimbo vermelho opcional.

## 5. Painéis e animação

- Rótulo pequeno dourado no canto ("A LISTINHA", "OBRA HÍDRICA", "NO SERTÃO", "NA IMPRENSA").
- Textos entram com **desfoque suave**: o texto sai do borrado, sobe 22 px e ganha opacidade em 0,45 s, em cascata.
- Números grandes contam do zero até o valor em 0,5 s.
- Ícones de **traço fino** dourado (família, casa, guindaste, remédio, formatura, moeda, lâmpada, gota, folha, sol).
- Cada item aparece no instante em que é falado.
- "Dados: Governo Federal" ou a fonte da manchete, sempre visível no painel.

## 6. Áudio

- Voz: passa-alta 80 Hz, compressão leve, loudnorm em duas passagens com alvo de **-15 LUFS** e pico de -2 dBTP. Sem reverb.
- Música: trilha própria (`music.py`, 96 BPM, tom menor), com volume 0,30 e **ducking** automático quando a voz entra.
- Efeitos (`sfx.py`): "whoosh" curto na troca de layout e de painel, "tic" em itens de lista, batida grave em carimbo. Todos baixos.
- Conferir no final: duração do áudio igual à do vídeo, -15 LUFS, pico abaixo de -1 dBTP.

## 7. Como fazer o próximo vídeo

1. O Eliezio exporta do CapCut em 1080p. O ideal são duas versões: **com** e **sem** legenda automática. A versão com legenda serve para ler o texto e os tempos, porque a transcrição automática fica bloqueada na rede da sessão.
2. `capmask.py` + `segment.py` extraem os tempos das frases da legenda. Depois é preciso conferir em tiras de imagem com 5 fps, porque falas curtas podem se juntar.
3. Listar os assuntos e pesquisar os números com fonte.
4. Copiar o script de render mais parecido e trocar `SRC`, as legendas (`TXT`/`PHRASES`), `PIP_RANGES`, `ZK` (zooms) e os painéis.
5. Testar quadros soltos (`frames:t1,t2,...`) antes de renderizar o vídeo inteiro.
6. Render final a 30 fps. Para entregar no celular, gerar cópias de ~13 MB (1080p, duas passagens com ~1,6 Mbps) e publicar numa página privada com botão "Baixar vídeo", porque o app nem sempre salva vídeo direto.

## 8. Histórico

- **10/10/2026:** primeira identidade aplicada (Ubatuba). Depois, versão profissional com tela dividida (Programas do governo, com 7 programas na listinha) e Ubatuba com painel "Na imprensa". O Eliezio aprovou o estilo e pediu para guardar e ir aprimorando.
