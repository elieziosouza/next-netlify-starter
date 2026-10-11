# Estilo do corretor de imóveis: lettering editorial

Estilo separado, **só para os vídeos de corretor de imóveis** do Eliezio (Eliezio Imóveis / EZ Brokers).
O canal de opinião (Opinião · Atualidades · Reações) **continua com a identidade azul-marinho e dourado** do `README.md` principal.
Não misturar os dois estilos.

Referência: um reel de corretora americana enviado pelo Eliezio em 11/10/2026, com lettering editorial de revista.

## Contatos do corretor (para tela final e legenda)

- WhatsApp: (11) 97111-8620
- Sites: eliezioimoveis.com.br e ezbrokers.com.br
- Instagram: @eliezio.corretordeimoveis e @ezbrokers

## Elementos do estilo

1. **Palavra-chave gigante em serifa** (DM Serif Display, cerca de 215 px, branca, sombra suave) **atrás da pessoa**: a cabeça passa na frente das letras.
   - Junto vai uma palavra pequena em Montserrat Regular 40, sobreposta no canto superior esquerdo (ex.: "vamos falar de / **salário**").
   - A palavra entra saindo do desfoque e cresce devagar (4% durante a exibição).
   - Em vídeo de enquadramento fechado, a palavra fica no alto e cruza o topo da cabeça. Em plano aberto (até a cintura), pode ficar mais baixa, na altura da cabeça.
2. **Legenda de uma palavra por vez:** Montserrat SemiBold 62, branca, sem caixa, com sombra, na altura do peito, entrando com um leve desfoque.
3. **Destaque de impacto:** Montserrat ExtraBold Italic, 120 px, caixa alta. Usar uma cor de destaque por vídeo (na referência, verde; na demo, dourado).
4. **Transição com desfoque:** a imagem desfoca e volta em cerca de 0,5 s, na troca de assunto ou de cena.
5. **B-roll em cartões** (fotos do imóvel aparecendo em volta do corretor), como na referência. Ideal para mostrar os imóveis.

## Como funciona o "texto atrás da cabeça"

- `scripts/segment_person.py` recorta a pessoa com o modelo U2Net Human Seg (onnxruntime). O modelo baixa pelo GitHub:
  - `github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.onnx`
  - instalar com `pip install onnxruntime`
- A máscara é limitada ao componente ligado ao rosto e a uma elipse da cabeça mais o corpo, para não confundir quadros e paredes claras com a pessoa.
- Ordem das camadas: vídeo → palavra grande → pessoa recortada por cima, só na faixa da palavra → legendas.

## Dicas de gravação para o efeito ficar perfeito

- Gravar em **plano mais aberto** (até a cintura ou corpo inteiro), com espaço acima da cabeça.
- Fundo que contraste com a pessoa. Áreas externas e imóveis funcionam muito bem.
- Gravar takes de b-roll do imóvel (fachada, sala, cozinha, área de lazer) para os cartões e as transições.

## Script

`lettering_editorial.py` é a demo (12 s) feita sobre um vídeo do canal. Para um vídeo novo, troque:
- `SRC`;
- `PHR` (frases com tempo, vindas da transcrição com `scripts/transcrever.py`);
- `BIG` (palavras grandes);
- `ACCENT` (destaques);
- `BLUR_AT` (transições).

Capa, glitch e as demais regras de entrega do kit continuam valendo, adaptados à identidade de corretor quando o Eliezio definir.
