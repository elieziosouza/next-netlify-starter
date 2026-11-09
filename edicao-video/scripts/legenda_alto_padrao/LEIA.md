# Legenda "alto padrão" (aprovada em 09/11/2026)

Primeiro vídeo: "As bets vão voltar?" (`video_bets.py`, capas em `capas_bets.py`).

Passo a passo (rodar dentro da pasta de trabalho, com `src.mp4` = vídeo dele):
1. `transcrever.py` → `segs.json`; corrigir o texto em `align.py` (lista FIX, um item por trecho) → `words.json` (tempo de cada palavra).
2. `legenda_dinamica.py` agrupa as palavras (quebra na pontuação ou a cada 4) e escolhe a palavra-chave (lista KEY).
3. `estilo_alto.py` desenha a legenda: apoio em Playfair Display Regular branca; palavra-chave em Poppins Bold no dourado do canal (222,196,138) ou, 1 em cada 3, em Poppins ExtraLight branca grande; filete dourado fino abrindo do centro sob a palavra-chave. Minúsculas (siglas como STF ficam maiúsculas).
4. `sons.py`: clique na palavra-chave (mín. 1,4 s entre cliques), batida grave + clique nas frases de impacto, sopro curto na troca de assunto.
5. `video_bets.py` monta tudo no padrão do canal: ele a 88% com bordas desfocadas, palavras gigantes (Anton, acima da cabeça, entrando pela lateral com clique), barra lateral com SIGA · COMPARTILHE, topo e rodapé, caixa fixa, zooms suaves, "SIGA PARA MAIS" na última frase. Depois `finaliza.sh` com a capa escolhida.
