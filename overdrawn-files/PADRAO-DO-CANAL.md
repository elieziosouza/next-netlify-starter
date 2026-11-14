# Overdrawn Files — padrão de produção

Canal em inglês, para público americano, sobre como o dinheiro some: escândalos financeiros, falências, golpes e crises.

## Toda pauta sai com

1. **Vídeo principal** de 8 a 10 minutos (acima de 8 libera anúncios no meio).
2. **3 Shorts no mínimo**, já planejados no roteiro (ver abaixo).
3. **3 thumbnails** (1 principal + 2 para o teste A/B do YouTube). Estilo preferido: o mesmo do post (foto escurecida com rosto, etiqueta vermelha com local e data, 2 linhas brancas com o fato e uma pergunta grande em vermelho).
4. Título principal + 2 alternativos, descrição com capítulos e fontes, tags, comentário fixado.
5. Legendas em inglês (.srt).
6. **Post de divulgação** do vídeo principal, feito depois dos cortes: texto em inglês + imagem quadrada 1080×1080 (`POST COMUNIDADE.jpg`), para a aba Posts do YouTube. Publicar 1 a 2 horas depois do vídeo principal.

## Shorts pensados desde o roteiro

Ao escrever o roteiro, marque pelo menos 3 trechos de 45 a 58 segundos que se sustentem sozinhos:

- **Utilidade:** o que a pessoa pode fazer, como um direito, um reembolso ou um alerta de golpe. É o que mais se compartilha e se salva.
- **Notícia:** o fato em si, com o gancho dos primeiros 3 segundos.
- **Número:** a conta, o valor ou a comparação que surpreende.

Regras de cada trecho:
- Começar com uma frase que funcione sem contexto (nada de "this channel" ou "as I said").
- Terminar numa frase que fecha a ideia.
- Ter um número ou uma imagem forte na tela.
- Todo texto que vai para o YouTube (títulos, descrições, tags, posts) é em inglês.

No roteiro, marque assim: `[SHORT 1 começa]` … `[SHORT 1 termina]`.

Formato do Short: 1080×1920, chamada de 3 linhas no topo, vídeo 16:9 no meio, legenda grande de 3 palavras por vez, "FULL STORY ON THE CHANNEL" no rodapé (script `shorts.py`).

## Nomes dos arquivos de entrega

Na pasta `entrega/` de cada vídeo:

```
Overdrawn Files - <Pauta> - VIDEO PRINCIPAL.mp4
Overdrawn Files - <Pauta> - THUMB 1 PRINCIPAL.jpg
Overdrawn Files - <Pauta> - THUMB 2 TESTE AB.jpg
Overdrawn Files - <Pauta> - THUMB 3 TESTE AB.jpg
Overdrawn Files - <Pauta> - LEGENDAS EN.srt
Overdrawn Files - <Pauta> - SHORT 1 <TEMA>.mp4
Overdrawn Files - <Pauta> - POST COMUNIDADE.jpg
```

## Visual

- Fundo: vídeo de banco gratuito (Mixkit), escurecido e levemente desfocado.
- Gráficos: Montserrat Black/ExtraBold, Inter, DM Serif para citações. Vermelho #E1251B, âmbar para "estimativa / não confirmado".
- Em toda cena: logo no canto, barra de progresso vermelha no rodapé e fonte da informação no canto inferior.
- Nada de logo de empresa, recorte de telejornal ou foto de pessoa real sem licença.
- Imagem gerada por IA: no máximo 1 ou 2 por vídeo.

## Narração

- ElevenLabs, voz "Ryan – American Documentary Narrator", modelo multilingual v2.
- O limite é de 5.000 caracteres por geração: divida o texto em partes.
- Gere uma versão só, para economizar crédito.

## Fatos

- Só o que foi confirmado em fonte citada na descrição.
- Acusação é sempre "alleged" (alegada).
- Estimativa vem marcada como estimativa, na fala e na tela.
