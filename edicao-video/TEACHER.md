# Canal Teacher Eliezio: padrão das aulas

Canal de inglês para o Ensino Fundamental e o Médio. Não misturar com o canal de opinião (Eliezio Souza): outra cor, outro avatar,
outra abertura.

## Formato
- Vertical 1080x1920, de 40 s a 1 min (aulas de sala podem passar de 2 min).
- Avatar 3D do professor embaixo (`v77/av3d_1..8.png`), reagindo: 1 sorrindo, 2 desconfiado/pensando, 7 surpreso, 8 piscando.
- Fundo azul-marinho com grade, cabeçalho "ENGLISH CLASS · Teacher Eliezio", amarelo (255, 214, 64) como destaque.
- Legenda karaokê: inglês em branco com a palavra falada em amarelo, português embaixo em amarelo-claro.
- **Feito para rodar em loop (30/10/2026):** sem riser e sem som de abertura. A capa fica parada e muda por 0,5 s e entra com zoom curto (`scripts/finaliza_teacher.sh`). As chamadas (SALVA, SIGA, COMENTA) entram durante a última frase, depois da última resposta, e o vídeo acaba 0,35 s depois da voz, sem tela parada no fim. Assim o fim emenda no começo e a pessoa assiste de novo. Nunca o glitch do canal de opinião.
- A capa vai SEMPRE fixada no início de todo vídeo, inclusive nos virais de 10 s.

## Roteiro (ElevenLabs, voz do Eliezio, modelo Eleven v4)
1. Abertura fixa: "Hello! Today: <tema>." e, logo depois, o gancho (uma pergunta ou um erro comum).
2. Nada de ligar um vídeo ao outro: sem "resposta do último desafio" e sem pergunta para o próximo vídeo.
3. Regra e exemplos: inglês primeiro, depois português. Números escritos por extenso em inglês.
4. Quiz com contador: pergunta, silêncio de 3 a 5 s aberto na edição (círculo, 3-2-1, tique-taque, música abaixa),
   "ding" e a resposta certa em verde com ✅, a errada apagada com ❌, com explosão de confete saindo da alternativa certa
   (por trás dos cartões, para não cobrir o texto) e som leve de papel junto com o "ding" (pedido de 30/10/2026).
5. Toda pergunta é respondida no próprio vídeo, no formato quiz com contador (pode ter 2 quizzes). Opções na mesma cor até a
   revelação, e nenhum emoji ou cor na legenda que entregue a resposta. Conferir ouvindo onde a pergunta termina e a resposta começa.
6. Pedido falado para comentar se acertou, seguir e salvar; na tela "COMENTA SE VOCÊ ACERTOU", "SIGA @teachereliezio" e "SALVA PRA REVISAR".

## Entrega
- Primeiro bloco: título com 4 hashtags na mesma linha, pronto para copiar. As 4 hashtags são do assunto do vídeo (ex.: #verbtobe #isorare #gramaticainglesa #quizdeingles), nada genérico.
- Depois: descrição e hashtags, cada um no seu bloco.
- Marcar a aula como feita no controle: https://claude.ai/artifact/1S2ouhHbcGgVcEsuUpJwq4
- Publicar o vídeo e a capa na página de vídeos do canal (novo no topo, com título + hashtags para copiar): https://claude.ai/artifact/Br8ebANZH1TaR4wNAv7RwE

## Scripts
- `render_short_present_continuous.py` (Short com exercício e CTAs), `render_short_comparative.py`, `render_aula_datas_vo.py` (quiz com
  contador e silêncio aberto na fala: `PINS` e `GAP`).
