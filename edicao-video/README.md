# Kit de edição de vídeo: Eliezio Souza

Padrão visual e técnico dos vídeos verticais do canal (Opinião · Atualidades · Reações).
Tudo aqui foi aprovado em outubro de 2026 e serve de base para os próximos vídeos.
Cada vídeo novo deve seguir este guia e, quando algo for melhorado, o guia é atualizado.

> Vídeos de **corretor de imóveis** usam outro estilo (lettering editorial): veja `estilo-corretor/README.md`. Este guia é do canal de opinião.

## 1. Preferências do Eliezio (prioridade máxima)

- **Redes do canal (15/10/2026):** TikTok, **Kwai** e **X** @elieziosouza78 · **Instagram** e YouTube @eliezio.souza78 (o Instagram mudou de @ezvideos_cortes para @eliezio.souza78 em 17/10/2026). No topo e na tela final ficam só dois grupos: TikTok, Kwai e X com @elieziosouza78; Instagram e YouTube com @eliezio.souza78 (X incluído em 17/10/2026), em `scripts/minitop.py` (`ITEMS`). Incluir o Kwai e o X também nas legendas dos posts.

- **Ele aponta para baixo = ele em cima (15/10/2026):** quando ele aponta o dedo para baixo ao chamar o vídeo, ele sobe para uma janela no topo (400×536, cabeça inteira com folga) e o vídeo de terceiros entra embaixo num cartão 3D inclinado para ele, sobre o fundo escuro desfocado (estilo do react da folga, que passou de 20 mil visualizações). Ver `scripts/render_react_canella.py`.
- **Música "vai dar PT" no final (15/10/2026):** entra baixinha no "dia 25" (com ducking sob a voz), fica cheia quando ele termina de falar, e a letra aparece grande abaixo do rosto com o **"PT" em pílula vermelha**. **Sem a estrela amarela** (ele não gostou). Se ele faz o L no final, a letra fica abaixo da mão.
- **Música com direitos autorais e YouTube (15/10/2026):** o "vai dar PT" foi reivindicado. No YouTube Shorts, vídeo com mais de 1 minuto e reivindicação é bloqueado; com até 59 s fica no ar. Quando usar música de terceiros, entregar também uma **versão YouTube com até 59 s**. Trilha própria no mesmo clima: `scripts/funk_pt.py` (batidão 130 BPM, sem voz) e `scripts/guia_grito.py` (vídeo-guia para ele gravar o grito "Dia 25 está chegando, o povo vai decidir, vai dar PT").
- **Referência da corretora americana: NÃO adotar (16/10/2026).** Ele viu a demonstração e não gostou: nada de ícones em neon, palavra dupla (pequena + grande em degradê), legenda de uma palavra, cantos de visor/transição de foco nem número gigante atrás. Manter a identidade atual e fazer só **ajustes finos**. Zoom: 7 a 9% no máximo.
- **Zoom in / zoom out suave é obrigatório (16/10/2026):** em todo trecho dele em tela cheia, aproximação suave nas falas fortes (3,5 a 7%, rampa de 0,6 s para entrar e para sair), voltando ao normal entre elas, e um leve zoom no final. Centro do zoom na altura do rosto, para o topo da cabeça nunca sair do quadro. Usar `scripts/zoom_suave.py` (`ZOOMS = [(início, fim, quanto)]`); a palavra gigante atrás dele é calculada sobre o quadro já com zoom. Ele reparou que faltou nos vídeos de 15/10.
- **Nada de "vai e volta" visível no final (16/10/2026):** ele reparou que ficou repetindo em loop. Quando faltar imagem para o final com música, usar o próprio vídeo seguindo até o fim, depois um congelamento suave com zoom lento (ou a tela da letra sobre fundo), nunca o mesmo trecho indo e voltando. Pedir a ele para gravar 6 a 8 s a mais no fim (segurando o L ou sorrindo).
- **Destaque de pessoa ou objeto no vídeo de terceiros (16/10/2026):** quando ele cita alguém ou algo da cena, o vídeo **congela**, aproxima no ponto (até 28%, só no vídeo de terceiros), escurece em volta, um **círculo vermelho se desenha** e uma **seta pisca** com um rótulo em pílula vermelha (ex.: "A MALA PRETA"), com batida e clique. Ver `scripts/render_react_lula_chuva.py`.
- **Música do vídeo de terceiros mais presente (16/10/2026):** ele pediu mais alta. Som do vídeo de terceiros a 1,25 com ducking leve (threshold 0,05, ratio 2,5), ficando uns 15 dB abaixo da voz, e não sumindo (antes ficava ~32 dB abaixo).
- **Barra do topo mais alta (16/10/2026):** a linha das redes fica em y ≈ 70 (antes 112), com degradê de 150 px (`make_minitop(..., height=150, cy=70)`). Atenção: no feed do TikTok/Instagram, os botões do app ficam no topo e podem passar por cima dela.
- **Fonte da palavra gigante: Anton (16/10/2026).** Ele comparou e escolheu a Anton (alta e estreita, cara de manchete) só para as palavras gigantes atrás dele, cerca de 1,5× o tamanho que a Montserrat teria, com o centro em y ≈ 262 para não encostar na barra das redes no topo. Legenda, topo, rodapé e capas continuam em Montserrat. Arquivo: `assets/fonts/Anton-Regular.ttf` (licença OFL).
- **Palavras gigantes (18/10/2026, revisado).** Duas formas aprovadas: (1) atrás dele, recortadas pela máscara, só quando o recorte fica limpo (cabeça baixa no quadro, fundo que contrasta com o cabelo); (2) acima da cabeça, entrando pela lateral (alterna direita e esquerda, rastro de movimento, para com clique de mouse) e saindo subindo de leve. Nunca na frente dele, nunca comendo a cabeça, nunca no cabeçalho, nunca cortadas na borda. Sem transparência (ele não gostou). Se a cabeça está alta no quadro, ele fica 12% menor em tela cheia com fundo desfocado nas bordas para abrir espaço. Se o recorte não ficar limpo, avisar o Eliezio antes de entregar.
- **Barra lateral e caixa de manchete (18/10/2026, aprovadas).** Barra na borda esquerda (`scripts/barra_lateral.py`, estilo "canal": azul, marinho e dourado), com brilho, nome do canal na vertical e filete dourado que serve de progresso; entra com som de sino discreto (`sfx.barra`). Em dois momentos troca o nome pela cápsula dourada "SIGA · COMPARTILHE". A caixa de vidro fosco azul-marinho com aba dourada fica fixa do começo até a música: em tela cheia abaixo da legenda, na tela dividida em cima da emenda. Só cores do canal: azul, marinho escuro e dourado. **Área segura do YouTube Shorts:** o YouTube corta até ~100 px de cada lado em celulares compridos (visto em 18/10). A barra fica colada no canto esquerdo (decisão dele em 18/10, mesmo que o YouTube corte um pedaço dela em celulares compridos); caixa, recortes, palavras gigantes e textos ficam na área segura. **Centralização (18/10/2026):** tudo (legendas, caixa, palavras gigantes, recortes, fotos, letra final, cabeçalho e rodapé, painel dele na tela dividida) se centraliza no espaço depois da barra lateral: a barra fica no canto (x 0 a 84) e o resto se centraliza em x = 582 (CX), não no meio do quadro. Largura útil máxima ≈ 680 px. O trecho do L pode ser espelhado quando a mão fica do lado errado (pedido dele).
- **Palavra gigante atrás da pessoa (15/10/2026):** 3 a 5 palavras-chave por vídeo aparecem enormes atrás de quem fala (máscara U2Net, `segment_person.py`), com entrada de pulo curto e **som de clique de mouse** (`sfx.click()`). Nunca cobrir o rosto nem o topo da cabeça; posicionar onde a cabeça é mais estreita para a palavra continuar legível. Ver `scripts/render_professor.py`.
- **"Trilha vai dar PT" = a música original (15/10/2026):** quando ele pedir "nossa trilha vai dar PT", é a música original com a letra ("...vai dar PT, vai dar, vai dar PT") e o PT em vermelho, com o vídeo em até 55 s. A batida própria (`funk_pt.py`) só quando ele pedir trilha sem direitos autorais.
- **Título e hashtags juntos (15/10/2026):** na entrega, dar o título já com as hashtags num bloco só, pronto para copiar e colar.

- **Cores e luz do vídeo dele ficam como ele gravou (12/10/2026):** sem correção de cor, sem vinheta, sem granulação e sem mexer na luz do rosto. A correção de cor só entra nas imagens de terceiros, se ele não pedir o contrário.

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
| Estilo geral | **Minimalista** (pedido do Eliezio em 11/10/2026). Nada grande ocupando a tela |
| Topo | `minitop.make_minitop`: só as redes sociais (ícones dourados de traço fino + @elieziosouza78 (TikTok, Kwai, X) e @eliezio.souza78 (Instagram, YouTube)), Montserrat SemiBold 27, filete dourado fino com pontas esmaecidas e sombra azul suave que some no vídeo. **Sem o nome** |
| Rodapé | `minitop.make_minifooter`: linha fina de progresso (dourada sobre trilho branco a 18%) e "OPINIÃO • ATUALIDADES • REAÇÕES" em 23 px, com ATUALIDADES em dourado |
| Artes antigas | `assets/topo.jpg` e `assets/rodape.jpg` (com nome e botões) ficam guardadas, mas **não são mais usadas** |
| Correção de cor | **Padrão desde 11/10/2026: "Cinema azul e dourado"** (`scripts/grading.py`, função `cinema`): sombras puxadas para o azul-marinho, luzes e pele levemente quentes, fundo menos saturado, verde forte contido, pele protegida por máscara, curva em S com ombro que segura os claros e clareza leve no rosto. Aplicar nas fontes com `grading.Fast(grading.cinema, 'lut_cinema.npy')` (tabela 256³, ~20 ms por quadro). Alternativa para denúncias pesadas: `investig` (documentário). **Desde 12/10/2026 a pele também é corrigida** (`cinema_skin`: menos laranja, brilho da careca contido, sombras do rosto abertas) e os claros da pele são segurados (luz forte de frente). **Não usar `face_light` positivo no vídeo**: o Eliezio achou a luz no rosto forte demais (12/10/2026). Padrão agora: `grading.tame_face(img, 239, 380)` (ombro suave nos claros + exposição 18% menor na região do rosto, uniforme). Não baixar a luz pela máscara de pele: deixa manchas cinzas na testa. Vinheta 24% e granulação suave por cima. |
| Tela final | 3 s: fundo azul, "SIGA PARA MAIS" (ExtraBold 50), filete dourado e a linha das redes. **Sem o nome** |

Exemplos aprovados em `exemplos/`.

## 3. Legendas

- Estilo **karaokê**: Montserrat ExtraBold **56 px** (linha de 78 px), MAIÚSCULAS, branco com contorno azul-marinho. O Eliezio pediu a letra menor em 11/10/2026.
- A palavra falada fica numa **pílula dourada** que desliza para a próxima palavra (0,1 s).
- No máximo 2 linhas, até 5 palavras por bloco, quebra equilibrada.
- Entrada da frase com "pop" curto (escala 86% → 100% em 0,2 s).
- Posição: y ≈ 1450 em tela cheia; y ≈ 1585 (dentro do quadro) na tela dividida.
- Números de dinheiro podem virar dígitos ("20 REAIS", "AGORA SÃO 50").
- Se o vídeo chegar com legenda gravada, ela é apagada quadro a quadro (`capmask.py` + `clean.py`) antes de colocar a nova.

## 4. Layouts

**Tela cheia:** vídeo 1080×1920, topo e rodapé por cima, legenda no peito.

**Tela dividida** (`render_tela_dividida.py`):
- Painel de dados no alto: x 40–1040, começando 30 px abaixo da linha do topo, com 520 px de altura, cantos 26 px, borda dourada fina e sombra suave.
- Quadro do Eliezio embaixo: x 154–926, y 732–1680, escala 1,615, com 125 px de folga acima da cabeça, borda dourada de 2 px e sombra.
- Transição de entrada e saída: 0,7 s com aceleração suave (ease in-out).

**React com dois vídeos e áudio** (`render_react_audio.py`, caso Vorcaro):
- Vídeo de rua num cartão 3D que desce do topo com desfoque de movimento; o Eliezio fica numa janelinha embaixo reagindo (trecho dele em silêncio, em vai e volta).
- Legendas gravadas no vídeo de terceiros são apagadas (detecção por cor + inpaint + vidro fosco suave que não pisca). Fala do protagonista em legenda dourada no lugar da original; fala do repórter numa linha menor com o rótulo "REPÓRTER".
- Áudio vazado vira painel: "ÁUDIO" entra grande e sobe para o topo com data e fonte, fotos dos envolvidos em 3D viradas uma para a outra, borda de quem fala brilha com o volume, onda sonora dourada guiada pelo áudio real e palavras de cobrança com destaque vermelho.
- Cartões de fato entram em camada por cima (manchete real, números com contagem animada), com fonte.
- Conclusão com "OS FATOS": linha do tempo em cartões numerados (negou, o áudio, admitiu).

**React com imagens de ato e números** (`render_react_paulista.py`, Paulista 12/10/2026):
- Imagens de terceiros em cartões 3D empilhados: o primeiro desce do topo, o segundo entra girando por cima e o de baixo recua e escurece. O som dos vídeos de terceiros é cortado (evita direitos autorais) e a trilha sobe.
- **Recorte da pessoa com fundo trocado:** existe (`segment_person.py`), mas o Eliezio **não gostou no vídeo** (12/10/2026). No vídeo, manter o fundo real dele. Na capa pode usar.
- **Cartões de vidro fosco** acima da cabeça (o próprio quadro desfocado atrás), com número animado e fonte. Nunca encostam no rosto.
- **Gesto escrito em luz:** rastreamento da mão por cor de pele (`hand.json`), suavizado; o traço dourado é "escrito" acompanhando a mão (ex.: o L), com ponta brilhante, faíscas e som de marcador.
- A janelinha do react fica parada até o fim das imagens e cresce **uma única vez** até a tela cheia, já com a fala dele (sem imagem dupla e sem transição dobrada).

**Pesquisa eleitoral em gráfico animado** (`render_pesquisa.py`, PoderData 13/10/2026):
- Conferir a pesquisa na fonte antes (instituto, datas de campo, entrevistas, margem, registro no TSE) e mostrar tudo no rodapé do painel.
- A matéria roda num cartão em cima; embaixo, painel de vidro com barras de base zero (proporcionais), foto de cada candidato e o número contando.
- **Mudança entre rodadas (pedido do Eliezio):** selo "ANTERIOR · data" que gira para "NOVA · data", barras andando do valor antigo para o novo com fantasma da rodada anterior, tags −/+ e colchete da diferença encolhendo; no fim, gráfico de linhas desenhado na tela (anterior → nova).
- Carimbo vermelho "EMPATE TÉCNICO" no canto do painel, sem cobrir as barras. Chamada final "COMENTE O QUE VOCÊ ACHA".
- Capa sem rosto pode usar fotos da matéria, mas sem logos de jornal.

**React com o vídeo rolando inteiro e tela dividida** (`render_react_lula_v2.py`, preferido pelo Eliezio em 12/10/2026):
- O vídeo de terceiros **roda inteiro, sem cortes**, com o som original (quando ele quiser). Os momentos do vídeo ficam longos.
- Quando ele fala, a tela **divide**: o vídeo continua rolando em cima (0–840) e ele aparece embaixo, grande, da cabeça ao peito (recorte do próprio quadro em tela cheia, com folga acima da cabeça). Entre as falas, o vídeo ocupa a tela toda.
- **Cortar os trechos em que ele está de cabeça baixa** assistindo. Ele só aparece falando para a câmera.
- Falas encaixadas na cena certa; a última fala fecha em tela cheia, com a divisão se abrindo até ele ocupar tudo (sem imagem dupla).
- Duração alvo: cerca de 50 s.

**React com reação real na janelinha** (`render_react_lula.py`, Lula na Paulista 12/10/2026):
- O trecho em que ele assiste e reage (risada, "olha o pique do véio") vai na janelinha, sincronizado com a cena certa do vídeo de terceiros; a voz dele corre junto.
- **Janelinha maior (pedido de 12/10/2026):** 440×578 px (x 320–760, y 1168–1746). O cartão do vídeo fica com 590 px de largura (cenas largas, 880 px) e a legenda entre os dois.
- Selo com número sobre o cartão (ex.: "80 ANOS · faz 81 no dia 27/10"), entrando com pulo e batida.
- **Gestos (punho etc.):** o Eliezio preferiu **sem efeito** no punho (12/10/2026). Não colocar efeito em gesto sem ele pedir. O L escrito em luz foi pedido por ele, então continua valendo quando ele pedir.
- Som de vídeo de terceiros: se ele quiser manter (ex.: o som da Paulista), entra só nos trechos do vídeo, abaixando quando ele fala, e a nossa trilha sai nesses trechos (`remix_paulista.py`). Quando a música tem direitos autorais, entregar também uma **versão YouTube** sem esse som.

**Notícia na imprensa** (`render_recortes_noticia.py`): mesmo layout dividido, com o recorte de jornal (`cards.py`) no painel "NA IMPRENSA". O recorte traz a manchete real com a fonte embaixo, marca-texto amarelo animado e carimbo vermelho opcional.

## 5. Painéis e animação

- Rótulo pequeno dourado no canto ("A LISTINHA", "OBRA HÍDRICA", "NO SERTÃO", "NA IMPRENSA").
- Textos entram com **desfoque suave**: o texto sai do borrado, sobe 22 px e ganha opacidade em 0,45 s, em cascata.
- Números grandes contam do zero até o valor em 0,5 s.
- Ícones de **traço fino** dourado (família, casa, guindaste, remédio, formatura, moeda, lâmpada, gota, folha, sol).
- Cada item aparece no instante em que é falado.
- "Dados: Governo Federal" ou a fonte da manchete, sempre visível no painel.

**Vídeo com embasamento em notícias** (`render_noticias_embasamento.py`): sequência de painéis encadeados durante a tela dividida:
- número da denúncia ou dado principal;
- linha do tempo do caso, com a etapa citada na fala destacada em dourado;
- manchete real do jornal, com marca-texto e carimbo. O carimbo nunca cobre a manchete nem o crédito da fonte;
- painel "Entenda", que explica o conceito jurídico (ex.: prova anulada não é prova inexistente; anulação não é absolvição).

Em casos contra pessoas, o painel sempre traz a linha "Fulano nega as acusações", quando for o caso.

**Entradas com motion blur:**
- Os painéis entram deslizando da direita com desfoque de movimento horizontal, proporcional à velocidade, e um "whoosh".
- A troca entre painéis é um cruzamento: o novo entra deslizando por cima enquanto o antigo some.
- A abertura do vídeo tem fade do preto, um zoom de 10% que recua em 0,8 s e desfoque vertical que se dissolve.

**Visual minimalista dos gráficos (11/10/2026, pedido do Eliezio)** (`render_graficos_3d_estrela.py`):
- **Sem caixa azul.** Na tela dividida, o fundo é o próprio vídeo dele desfocado e escurecido (26% de brilho), e os gráficos e textos ficam soltos sobre ele.
- **3D:** barras com face frontal, topo mais claro e lateral mais escura, sobre um "piso" sutil, todas na mesma escala para permitir comparação.
- **Camadas:** cartões com duas camadas douradas deslocadas por trás, que dão profundidade.
- **Perspectiva:** os painéis entram girando em profundidade (rotação Y) junto com o deslize e o motion blur.

**Estrela do 13 (vídeos de campanha):** quando ele fala "dia 25", ele fica no quadro embaixo e a estrela vermelha com "13" branco entra em cima, **sempre acima da cabeça, nunca sobre o rosto**:
- **entrada minimalista (aprovada em 11/10/2026):**
  1. contorno branco fino se desenha em 0,65 s;
  2. vermelho chapado (#D6262E) preenche de baixo para cima;
  3. "13" branco sai do desfoque;
  4. "D I A 2 5" em letras espaçadas, com filete dourado que se estende;
  5. um único brilho suave passa pela estrela.
- **Sem raios, sem giro e sem brilhos espalhados;**
- som de "sonho e esperança" (arpejo de sinos subindo, acorde maior suave e eco), em volume discreto.

**Versão TikTok (11/10/2026):** o TikTok marcou o vídeo com a estrela do 13 como violação. Todo vídeo de campanha deve sair em **duas versões**: com a estrela, para o Instagram, e **sem estrela e sem o 13**, para o TikTok. Na versão TikTok, o final volta para a tela cheia só com a legenda da fala.

**Regra eleitoral para lembrar o Eliezio:** eleitor pode postar, mas não pode pagar impulsionamento de propaganda eleitoral.

## 6. Áudio

- Voz: passa-alta 80 Hz, compressão leve, loudnorm em duas passagens com alvo de **-15 LUFS** e pico de -2 dBTP. Sem reverb.
- **Voz dele sempre cheia (21/10/2026):** igualar o volume de todas as frases dele (cada trecho pela mediana do RMS; o começo costuma ser gravado mais baixo), compressão leve na voz e master final em -14 LUFS. Terceiros 3 a 4 dB abaixo, trilha bem baixa (~-41 LUFS no bruto). Medir com ebur128 nos trechos dele, no meio e no começo, antes de entregar.
- **Série "Faltam X dias" (21/10/2026):** `render_contagem.py` (DAY=4,3,2,1) e `capas_contagem.py` (DAY, TEMA="LINHA 1|LINHA 2", FACE_Y0). Abre com a placa do número virando + ele em tela cheia; meio com manchetes conferidas em cartão de papel (veículo e data, "HOJE"/"ONTEM"), trecho de TV e o outro lado; fecha com o contador indo para o próximo número ("AMANHÃ"). Capa: rosto dele inteiro, nunca cortado pelos textos. **Dia 25 (eleição): nada novo** (Lei 9.504, art. 39, § 5º, IV); a série termina no sábado 24.
- **Pesquisas eleitorais:** não colocar números de pesquisa nos vídeos dele (divulgar exige registro, margem, contratante etc.). Usar "disputa apertada, cada voto conta".
- **Caixa fixa sem vãos (22/10/2026):** mesmo estilo do canal (barra dourada do lado, aba dourada com o assunto, vidro azul-marinho com contorno dourado), mas tudo encostado: a barra cola na caixa, a aba nasce da barra e assenta reta na caixa, lado esquerdo da caixa reto. Selos acima dela com respiro (no modo dividido, `cy0 + ch + 30`).
- **Próximos vídeos: novos efeitos combinados (22/10/2026):** zoom de câmera no rosto na frase de impacto; tremida leve na palavra forte; transição de "rasgo de papel" entre recortes de jornal; contador de números subindo (ex.: R$ 10 milhões); linha do tempo animada para explicar casos. Usar um ou dois por vídeo, sem exagero. Conectores sugeridos (ele conecta em claude.ai/customize/connectors e abre sessão nova): vidIQ (assunto, título, capas) e HyperFrames da HeyGen (animações especiais; testar antes de prometer).
- **Proteção jurídica em todo roteiro, legenda, capa e texto de post (21/10/2026):** opinião sim, acusação sem prova não. Antes de entregar, conferir:
  - **Fato x acusação:** o que não tem decisão da Justiça é "acusado", "réu", "investigado", "segundo o MP", "fulano diz". Nunca "assassino", "ladrão", "corrupto", "criminoso" na voz do Eliezio, nem na legenda ou na capa, sem condenação definitiva.
  - **Fala de terceiros:** termo forte dito por campanha, jornal ou político fica atribuído na tela (selo "peça da campanha", "segundo a CNN") e, se preciso, com a ressalva ("o PM é réu; o júri não aconteceu").
  - **Sempre o outro lado:** a resposta ou negativa do citado aparece no vídeo ou na legenda.
  - **Opinião como opinião:** "eu acho", "pra mim", pergunta retórica, crítica à atuação pública. Nada sobre vida íntima, família sem relação com o fato, aparência ou xingamento.
  - **Números e datas** só conferidos em mais de um veículo, com fonte na legenda; sem número na dúvida.
  - **Montagem honesta:** não cortar fala de modo a mudar o sentido; não usar imagem fora de contexto; sem IA imitando voz ou rosto de ninguém.
  - **Crianças e vítimas:** sem foto de vítima menor na capa; tom respeitoso.
  - **Propaganda:** não impulsionar conteúdo eleitoral pago (só candidato, partido ou coligação podem); nada de pesquisa sem registro ou "fake news" sobre urna e votação.
  - **Pessoas comuns:** em print de rede social, desfocar foto e nome de quem comentou (e de qualquer pessoa que não seja figura pública). Placas de carro, endereços e telefones também.
  - **Vídeo de político sem fonte na imprensa:** avisar que só deve ser postado se vier de perfil oficial (risco de montagem ou deepfake).
  - Na dúvida, avisar o Eliezio no começo da resposta e sugerir a versão mais segura.
- **Nunca cortar fala de terceiros no meio (20/10/2026):** repórter, entrevistado ou político só entra e sai em fim de frase. Medir o envelope de áudio nos pontos de corte: começar ~0,1 s antes da primeira sílaba e terminar depois da última, no silêncio. Não cortar lista no meio (nomes, números); se a lista não couber, terminar na frase anterior. Se dois trechos estão a poucos segundos, emendar num só em vez de pular.
- **Sem vermelho nos textos (20/10/2026):** palavras grandes só em dourado claro ou branco, contorno azul-marinho grosso (10 px) e sombra, letras garrafais (o maior tamanho que cabe na faixa livre). Destaque da legenda e selos em azul do canal (14, 62, 120). Vermelho só no "PT" do vai dar PT.
- **Abertura e sons (20/10/2026):** o vídeo começa com ele **grande em tela cheia**; quando entra a matéria, ele encolhe até o card de cima (444×592) e só então o cartão da matéria sobe. A caixa fixa some durante a troca. O som do "siga · compartilhe" é `sfx.siga()` (duas notas suaves e graves), não o sino. Palavra grande entra com sopro + clique + batida leve (`thud`).
- **Palavra grande sempre encaixada (20/10/2026):** a palavra grande é medida de verdade (caixa do texto) e reduzida até caber na faixa livre (na tela dividida: entre a janela dele e o cartão ou o selo do cartão, com 20 px de folga), entra pela lateral e sai só sumindo, sem subir. Títulos e selos também encolhem até caber na largura segura (≈ 660 px). Nunca sobrepor janela, cartão, selo ou cabeçalho.
- **Resumo com compilação (19/10/2026, `render_resumo_debate_v3.py`):** layout do react em que o Flávio fala "Lula" 7x: ele numa janela em cima (384×512, cabeça inteira), palavra grande entre a janela e o cartão, debate num cartão embaixo entrando em 3D, caixa fixa e legenda com folga até o rodapé, tudo centrado em CX. Quando a compilação repete o vídeo em cima e embaixo, usar em cada trecho **a versão melhor** (a de cima é mais aberta e mostra os dois). **Não cortar ninguém**; selos vão na borda de cima do cartão, nunca sobre cabeça.
- **Voz dele x áudio de terceiros (19/10/2026):** a voz do Eliezio fica **3 a 4 dB acima** do trecho do debate/reportagem (medir cada trecho com ebur128). No mesmo nível ele achou a voz baixa, porque o áudio de TV vem muito comprimido.
- Música: trilha própria (`music.py`, 96 BPM, tom menor), com volume 0,30 e **ducking** automático quando a voz entra.
- Efeitos (`sfx.py`): "whoosh" curto na troca de layout e de painel, "tic" em itens de lista, batida grave em carimbo. Todos baixos.
- **Finalização sem cortar o áudio:** a tela final só começa 0,4 s depois da última palavra. Um riser de 2 s (tom subindo com ruído) cresce por baixo das últimas frases, depois vem um whoosh e uma batida grave na entrada da tela final.
- Conferir no final: duração do áudio igual à do vídeo, -15 LUFS, pico abaixo de -1 dBTP.

## 6.1 Assinatura de abertura: glitch (marca registrada, obrigatória)

Pedido do Eliezio em 11/10/2026: **todo vídeo começa com o efeito glitch**. Em 12/10/2026 ele pediu: **o glitch nunca fica em cima da fala inicial**. Por isso a capa e o glitch são feitos juntos, numa etapa só:

```
python3 edicao-video/scripts/embutir_capa.py video_editado.mp4 capa_escolhida.jpg video_final.mp4
```

- A capa aparece sozinha por 0,8 s (com avanço leve de 2%), o vídeo entra com fusão de 0,18 s e a fala começa só depois de 0,62 s.
- O glitch cobre a capa (0 a 0,34 s) e a passagem capa → vídeo. O som do glitch dura 0,32 s, então termina antes da primeira palavra.

- **Som:** cerca de 0,4 s de estalos picotados (tons quadrados, ruído bitcrush, sample-hold) sem zap final (pedido do Eliezio), sempre o mesmo (seed fixa), para virar marca sonora.
- **Imagem:** faixas horizontais deslocadas, separação RGB, linhas de varredura e um flash curto, de forma intermitente, nos primeiros 0,34 s. Um glitch menor repete na passagem capa → vídeo.
- Não desloca nem corta o áudio. O glitch é somado por cima.

## 7. Capa (obrigatória em todo vídeo)

O Eliezio pediu em 11/10/2026: **todo vídeo sai com capa impactante**, de preferência em duas opções. O script é o `scripts/capa.py`.

- **Formato:** 1080×1920. Todo o texto fica dentro da faixa central 3:4 (y 240 a 1680), que é o que aparece na grade do perfil.
- **Foto:** um quadro do próprio vídeo com expressão forte (olhos abertos, fala intensa ou gesto). Rosto grande no alto, contraste reforçado, vinheta e degradê azul-marinho do peito para baixo.
- **Texto:**
  - etiqueta dourada pequena com o tema (ex.: "CASO RACHADINHA");
  - título curto em Montserrat Black, com 2 a 4 palavras de impacto;
  - uma palavra-chave em carimbo vermelho ou em dourado;
  - linha de apoio em ExtraBold e um filete dourado.
- **Sempre três opções (pedido de 12/10/2026):** A e B com o rosto dele, e **C sem o rosto** (só a imagem do assunto, com o mesmo texto forte e carimbo vermelho).
- **Rosto na capa (12/10/2026):** o vídeo do WhatsApp tem só 478 px de largura, então ampliar demais deixa o rosto "duro".
  - Usar pouca ampliação (zoom 1,0), nitidez leve, redução de ruído e a pele corrigida (`grading.cinema_skin` + `face_light`).
  - Escolher o melhor quadro em **todos os vídeos dele**, não só no atual: o quadro mais nítido, com olhos abertos e expressão firme. Os melhores até agora são os do vídeo do Vorcaro (blazer, luz suave).
  - Pode trocar o fundo pela imagem do assunto (recorte da pessoa). Nunca cortar cabeça nem orelha: para tirar algo do fundo, remover pela cor, não pelo formato.
- **Preferida do Eliezio (11/10/2026):** a opção A, com **palavra-chave em carimbo vermelho** (ex.: "PROVA / ANULADA / NÃO É INOCÊNCIA", "EU SOU / BOLSA FAMÍLIA / E MAIS 6 PROGRAMAS", "ZONA AZUL / +150% / DE R$ 20 PARA R$ 50"). O carimbo vermelho é o padrão, mesmo em tema positivo. O dourado (`stamp_gold`) só entra se ele pedir.
- **Duas opções:** uma com o conceito do vídeo (ex.: "PROVA ANULADA NÃO É INOCÊNCIA") e outra com o dado mais forte (ex.: "R$ 2 MILHÕES NA CONTA DO QUEIROZ").
- **O Eliezio escolhe a capa antes de fechar o vídeo (regra fixa).** Primeiro mostre as duas opções e espere a escolha. Só depois embuta a capa e entregue o vídeo final. Nunca embutir por conta própria.
- **Capa embutida:** a capa que ele escolheu entra no início do vídeo. Ela fica parada até 0,42 s e se dissolve em 0,2 s, antes da primeira palavra, então o áudio não é deslocado nem cortado. Isso é feito com overlay do ffmpeg sobre o vídeo final.
- **Entrega:** as duas capas ficam também como arquivos separados na página de download, cada uma com seu botão.
- **Nunca cortar o rosto nem o topo da cabeça** (pedido de 11/10/2026). A cabeça aparece inteira, com folga em cima (`face_y` ≈ 770). O mesmo vale para o quadro dele em react e na tela dividida.
- **Regra de conteúdo:** a capa não afirma o que as fontes não afirmam. Pergunta e conceito podem; acusação sem base não.

## 7.1 Título, legenda e hashtags (obrigatório na entrega)

Toda entrega de vídeo termina com, no chat (título + hashtags num bloco de código pronto para copiar e colar, pedido de 15/10/2026):
- **Primeiro bloco, sempre (pedido de 17/10/2026):** o título já com **4 hashtags** no fim, numa linha só, num bloco de código para copiar e colar de uma vez;
- 3 a 4 opções de **título**, indicando a preferida;
- **legenda do post** para Instagram e TikTok, com fatos com fonte e uma chamada para comentar;
- **hashtags**: uma lista completa e uma versão enxuta com 5 a 6;
- **título para o YouTube Shorts**, com até 100 caracteres.

Em vídeo de campanha, lembrar que o eleitor não pode pagar impulsionamento.

## 8. Como fazer o próximo vídeo

**Começo de sessão nova (16/10/2026):**
1. O "Setup script" do ambiente roda `bash edicao-video/setup.sh` (instala dependências e baixa os modelos de transcrição e de recorte em `~/.cache/edicao-video`). Se não estiver configurado, rode à mão.
2. `bash edicao-video/scripts/prepara_area.sh "$S"` monta a área de trabalho (scripts em `$S/work`, fontes, modelos e a batida própria).
3. Música original "vai dar PT": o repositório é **público**, então ela não fica aqui. Baixar `kit/vai-dar-pt.mp3` da página de entregas (privada) com a ferramenta Artifact e converter para `$S/v15/song_vox.wav` (48 kHz, estéreo).
4. Vídeos do Eliezio: pedir o arquivo original (CapCut ou Google Drive). O WhatsApp reduz para 478×850.

1. O Eliezio exporta do CapCut em 1080p, de preferência **sem** legenda.
   - Para transcrever, use `transcrever.py` (Whisper small + VAD via sherpa-onnx). O Hugging Face é bloqueado na rede da sessão, mas o modelo baixa pelo GitHub:
     - `pip install sherpa-onnx`
     - `github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-small.tar.bz2`
     - `.../asr-models/silero_vad.onnx`
   - Trechos confusos devem ser transcritos de novo com mais contexto, usando o modelo sem int8.
   - Se o vídeo vier com legenda gravada, use `capmask.py` + `segment.py` para ler os tempos e `clean.py` para apagar a legenda.
2. `capmask.py` + `segment.py` extraem os tempos das frases da legenda. Depois é preciso conferir em tiras de imagem com 5 fps, porque falas curtas podem se juntar.
3. Listar os assuntos e pesquisar os números com fonte.
4. Copiar o script de render mais parecido e trocar `SRC`, as legendas (`TXT`/`PHRASES`), `PIP_RANGES`, `ZK` (zooms) e os painéis.
5. Testar quadros soltos (`frames:t1,t2,...`) antes de renderizar o vídeo inteiro.
6. Gerar as duas capas com `capa.py`, mostrar ao Eliezio e **esperar ele escolher**.
7. Render final a 30 fps, com a capa escolhida embutida no início.
8. Aplicar a assinatura glitch (`glitch_intro.py`) como última etapa. Para entregar no celular, gerar cópias de ~13 MB (1080p, duas passagens com ~1,6 Mbps) e publicar numa página privada com botão "Baixar vídeo", porque o app nem sempre salva vídeo direto.

## 9. Histórico

- **10/10/2026:** primeira identidade aplicada (Ubatuba). Depois, versão profissional com tela dividida (Programas do governo, com 7 programas na listinha) e Ubatuba com painel "Na imprensa". O Eliezio aprovou o estilo e pediu para guardar e ir aprimorando.
- **11/10/2026:** vídeo "Rachadinha: provas anuladas". Novidades: transcrição automática com Whisper, painéis com embasamento em notícias (denúncia, linha do tempo, manchete real e "Entenda"), entradas com motion blur e finalização com riser e whoosh sem cortar a fala.
- **11/10/2026:** identidade minimalista aprovada: topo só com as redes, rodapé fino, tela final sem o nome e legenda menor (56 px).
- **11/10/2026:** vídeo do salário mínimo: fundo escurecido no lugar do azul, gráficos 3D, camadas, perspectiva e estrela do 13 acima da cabeça.
- **11/10/2026:** lettering editorial (referência enviada pelo Eliezio) aprovado como estilo **só para corretor de imóveis**, guardado em `estilo-corretor/`. O canal de opinião mantém a identidade.
- **11/10/2026:** capa impactante passa a ser obrigatória em todo vídeo (`capa.py`).
- **11/10/2026:** react Flávio x Vorcaro (negação + áudio): layout de react com áudio, remoção de legenda gravada com vidro fosco, linha do tempo dos fatos. Nova correção de cor "Cinema azul e dourado" vira padrão.
- **12/10/2026:** o Eliezio não gostou do recorte com fundo trocado nem da luz extra no rosto; versão final com o fundo real e a pele com os claros segurados.
- **12/10/2026:** react da Paulista: ele recortado na frente da multidão, cartões de vidro fosco, L escrito em luz acompanhando a mão. Nova abertura `embutir_capa.py`: glitch só sobre a capa, nunca em cima da fala. Reforço do Eliezio: **nunca cortar o rosto dele**.
- **15/10/2026:** react da prisão de Márcio Canella: ele aponta para baixo e sobe para a janela do topo, vídeo em cartão 3D embaixo (`render_react_canella.py`), selo de notícia e de valor conferidos, "vai dar PT" no final sem estrela. O vídeo do Lula às 5h30 foi refeito sem a estrela. React do chinelo de pé gigante (`render_react_chinelo.py`) com legenda gravada em inglês trocada por cartão em português.
- **15/10/2026:** corte do Dia do Professor (57 s, trilha própria): primeiro uso da palavra gigante atrás da pessoa com clique de mouse; capa C com a palavra atrás do professor.
- **16/10/2026:** meme "momento André Janones" (`render_esquete_live.py`): cartão do grupo de WhatsApp com selo AO VIVO piscando e contador de participantes que sobe a cada número falado (clique por degrau, impacto no pico). Palavras Anton atrás dele em azul-marinho quando a parede é clara. Meme leva selo de crédito do áudio. Aprovado pelo Eliezio (capa B).
- **18/10/2026:** pesquisa Vox Brasil (`render_pesquisa_vox_1810.py`): estreia da barra lateral com SIGA · COMPARTILHE e da caixa de manchete fixa; recortes de jornal na tela dividida; palavras gigantes atrás dele com clique. Capa C escolhida.
- **23/10/2026:** pedido do Eliezio para os próximos vídeos: **edição dinâmica para prender a atenção**. Usar motion graphics, ícones e elementos animados (setas, círculos, selos, emojis) quando ajudarem; cortes com zoom de rosto, tremida em palavra forte, transição de papel rasgado, número subindo e linha do tempo animada; e voltar às **palavras gigantes atrás dele** (recorte da pessoa na frente do texto). Primeiro vídeo nesse estilo: tutorial na horizontal (16:9), com mais de 3 minutos, "como pedir para o Claude editar seu vídeo".
