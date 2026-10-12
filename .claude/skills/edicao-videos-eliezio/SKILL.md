---
name: edicao-videos-eliezio
description: Padrão de edição dos vídeos verticais do Eliezio Souza (canal Opinião · Atualidades · Reações). Use sempre que ele mandar um vídeo para editar, pedir legendas, motion graphics, tela dividida, recortes de notícia, música ou ajustes de áudio.
---

# Edição de vídeos do Eliezio

Antes de editar qualquer vídeo, leia `edicao-video/README.md` na raiz deste repositório. Ele tem o guia de estilo aprovado, as preferências do Eliezio e o passo a passo.

Regras que nunca mudam sem ele pedir:
- Visual profissional de telejornal, nunca amador.
- Não cortar o Eliezio: na tela dividida ele aparece inteiro, com folga acima da cabeça.
- Zooms de no máximo 7%, sempre suaves.
- Começar em tela cheia e editar conforme o vídeo avança.
- Todo número em painel precisa de fonte conferida.
- Nada de logotipo oficial de governo ou de jornal.

Material pronto:
- Topo, rodapé e fontes em `edicao-video/assets/`.
- Scripts em `edicao-video/scripts/`: `render_tela_dividida.py` (painéis de dados), `render_recortes_noticia.py` (recortes de jornal), `clean.py` (apaga legenda gravada), `capmask.py`/`segment.py` (lê tempos da legenda), `sfx.py`, `music.py` e `cards.py`.
- Exemplos aprovados em `edicao-video/exemplos/`.

Todo vídeo sai com duas opções de capa impactante (`edicao-video/scripts/capa.py`, seção 7 do README). Antes de fechar o vídeo, mostre as duas e espere o Eliezio escolher qual vai embutida no início.

Todo vídeo começa com a capa escolhida e a assinatura glitch, numa etapa só: `edicao-video/scripts/embutir_capa.py VIDEO CAPA SAIDA`. O glitch fica só sobre a capa e nunca em cima da fala inicial.

Nunca cortar o rosto nem o topo da cabeça do Eliezio (vídeo, janelinha, capa, transições). Conferir em quadros soltos antes do render.

Ao entregar cada vídeo, termine sempre com título (opções), legenda do post, hashtags e título para Shorts (seção 7.1 do README).

Quando o Eliezio aprovar uma melhoria, atualize o README (seções 1 a 6 e o histórico) e faça commit.
