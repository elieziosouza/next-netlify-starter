# Mini curso "Inglês para Viajar com o Teacher Eliezio" (Kiwify)

Combinado em 07/11/2026:
- 7 aulas de 3 a 4 min, horizontal 1920x1080, Remotion (`remotion-teacher/src/Viagem<N>.tsx`) e `scripts/aulas/aula_viagem<N>.py`.
- O que não couber na aula vai para o PDF da aula (HTML em `curso-viagem/aula<N>_pdf.html`, gerado com `node mkpdf.cjs entrada.html saida.pdf`).
- Voz do professor: a dele (njASsAgVyTCHG8OdIeWh). Simulações: pode usar mais de uma voz, uma por personagem.
  - Oficial da imigração: Roger (CwhRBWXzGAHq8TQ4Fs17)
  - Atendentes mulheres (hotel, loja): Jessica (cgSgspJ2msm6clMCkdW9)
  - Atendentes homens jovens (garçom, motorista): Will (bIHbv24MWmeRgasZH58o)
- Simulações com fala das duas pessoas (pedido de 08/11/2026): o atendente/oficial fala com a voz do personagem e a resposta do "VOCÊ" é falada na voz dele (clonada), não fica só na tela. A Aula 1 fica como está.
- Reels de divulgação (pedido de 08/11/2026): sempre entregar um título com 4 hashtags NA MESMA LINHA, com botão de copiar na página do curso. Ex.: "Como pedir comida em inglês sem travar no restaurante 🍽️ #inglesparaviajar #restaurante #frasesemingles #teachereliezio".
- Reels de divulgação (pedido de 08/11/2026): a capa (título + avatar + "link na bio") entra parada nos primeiros 0,5 s do próprio Reel. Montagem: `curso-viagem/reel_divulgacao.py`.
- Sempre roteiro + custo (estimate_only) e esperar o OK antes de gerar voz.
- Ao terminar: cadastro na Kiwify (ele sobe os arquivos; eu preparo os textos).

Aulas:
1. No aeroporto: check-in e imigração (feita 07/11/2026, 1.570 créditos)
2. No hotel (feita 08/11/2026, 1.467 créditos; simulação com recepcionista Jessica + respostas na voz dele)
3. No restaurante: pedir (feita 08/11/2026, 1.234 créditos; garçom Will + respostas na voz dele)
4. No restaurante: pagar e gorjeta (feita 08/11/2026, 1.327 créditos; garçom Will + respostas na voz dele)
5. Na rua: pedir e entender direções (feita 08/11/2026, 1.346 créditos; moça na rua Jessica)
6. Transporte: táxi, Uber e metrô (feita 08/11/2026, 1.191 créditos; motorista Chris)
7. Compras e emergências + encerramento (feita 08/11/2026, 1.337 créditos; vendedora Jessica; PDF com resumo e certificado)

Aulas 5 a 7 geradas com `curso-viagem/gera_aula.py` (voz + config + composição) e `curso-viagem/gera_pdf.py` (PDF).

Reel de vendas (10/11/2026): `video_vendas.py` (+ `capas_venda.py`). 37 s, vertical, formato Teacher, oficial (Roger) + voz dele (550 créditos, 1 tomada). Preço dito na voz ("de cinquenta e nove por vinte e sete, por tempo limitado"): quando a promoção acabar, refazer a voz (516 créditos) ou trocar por versão sem preço. Pré-requisitos na pasta de trabalho: prof.mp3, oficial.mp3, segs.json (transcrever.py), av3d_*.png, pdf-1/pdf-2/cert-7.jpg, amostra-capa.jpg, song.wav (nada disso fica no repositório público). Capa embutida com `finaliza_teacher.sh`. Link na bio do @teacher.eliezio: https://teacher-eliezio.vercel.app/

