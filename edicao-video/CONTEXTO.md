# Ponto de partida para uma conversa nova

Peça ao Claude: **"Leia edicao-video/CONTEXTO.md, README.md e TEACHER.md e continue de onde paramos."**
Resumo salvo em 30/10/2026 para não carregar o histórico longo (economia de tokens).

## Quem é e regras gerais
- Eliezio Souza: corretor de imóveis, fotógrafo e professor de inglês. Português sem jargão de IA.
- Dois canais que **nunca se misturam**:
  - **Eliezio Souza** (opinião · atualidades · reações): marinho e dourado, barra lateral, caixa de manchete, legenda karaokê. Regras em `README.md` e na skill `.claude/skills/edicao-videos-eliezio`.
  - **Teacher Eliezio** (aulas de inglês): marinho e amarelo, avatar 3D, quiz com contador. Regras em `TEACHER.md`.
- Entrega: primeiro bloco = título + 4 hashtags do assunto na mesma linha; depois descrição e hashtags, cada um num bloco para copiar.
- Opinião: só quando ele pedir. Proteção jurídica: fato conferido em mais de uma fonte, nada de acusação sem decisão, citar fonte.
- Voz: conector ElevenLabs, modelo `eleven_v4`, voz do Eliezio `njASsAgVyTCHG8OdIeWh`, sempre 1 take. **Antes de gerar, mostrar roteiro e custo (`estimate_only`) e esperar aprovação.** Custo ≈ 1 crédito por caractere.
- Números por extenso no texto da voz. Para lacunas use "blank", nunca "___".

## Formato loop (desde 30/10/2026, os dois canais)
- Capa muda por 0,5 s no início, sem riser e sem glitch (`scripts/finaliza.sh` para o canal de opinião, `scripts/finaliza_teacher.sh` para o Teacher). `GLITCH=1` volta o glitch antigo só se ele pedir.
- Sem tela final parada: SIGA/COMENTA entram por cima da última frase e o vídeo acaba 0,3–0,5 s depois da voz.
- Canal de opinião: **ele escolhe a capa (2 opções) antes de fechar o vídeo**.

## Teacher Eliezio
- Abertura "Hello! Today: ...", inglês primeiro e depois português, quiz respondido no próprio vídeo, cores das opções iguais até a revelação, conferir no áudio que a resposta vem depois do relógio, **confete saindo da alternativa certa** (novo padrão).
- Controle das aulas (marcar feita): https://claude.ai/artifact/1S2ouhHbcGgVcEsuUpJwq4 (coleção `aulas`, doc `s{semana}-{a1|a2|b1|b2}` = `{done, doneAt}`).
- Página de vídeos do canal (novo no topo): https://claude.ai/artifact/Br8ebANZH1TaR4wNAv7RwE
- Feitas: s1-a1, s1-a2, s1-b1, s1-b2, s2-a1, s2-a2, s3-a1, s9-a2, **s4-a1 (Numbers 1–100, `scripts/render_short_numeros.py`)**.
- Próximas na fila: A, an, the (A1) · Was e were (A2) · Plural (A1) · Present Perfect × Simple Past (B1).
- Série viral (`scripts/render_viral.py`, variável `VIRAL`): basico, very, brasileiro, obrigado, isare — já refeitos no formato loop.

## Eliezio Souza (opinião)
- Página de vídeos: https://claude.ai/artifact/7wTF12GuP8AE3v9AcPqEq7 (limite de 256 MB: ao publicar novo, tirar os cards mais antigos).
- O vídeo "Região por região" (mapa) foi muito bem: 20,7 mil views, público 55+. Ele quer mais vídeos explicativos com dados nesse estilo.
- Feito em 30/10: **O novo Congresso** (`scripts/render_congresso.py`, capa A, publicado). Título: "O novo Congresso: quem ganhou e quem perdeu cadeiras #novocongresso #eleicoes2026 #camaradosdeputados #senadofederal".
- Lista de temas sugeridos: (1) capital por capital, (2) abstenção por estado, (3) Congresso — feito, (4) isenção do IR até R$ 5 mil, (5) quanto cada região paga de imposto e recebe.

## PENDENTE: vídeo "Quanto já custou a guerra na Ucrânia"
- Roteiro aprovado (completo) e **voz já gerada e cobrada (825 créditos)**: flow ElevenLabs `3UXY7F6tJQskU0nc9wGt`, sessão `SIEJsgwZSY3ZhRAiX8GY`. Na conversa nova: chamar `creative_get_flow_run_status` com esses ids e baixar o `content_url` (não gerar de novo).
- Roteiro: 4 anos e 8 meses de guerra · Rússia ocupa quase 1/5 da Ucrânia com a Crimeia, mais que Pernambuco inteiro · CSIS: Rússia ~1,4 milhão de mortos, feridos ou desaparecidos; Ucrânia 525 a 625 mil · ONU: mais de 17 mil civis mortos (contagem verificada, abaixo do real) · Europa ~€70 bi em ajuda militar (Instituto Kiel) · EUA US$ 133 bi em ajuda total · Banco Mundial: reconstrução US$ 588 bi (dano direto US$ 195 bi; setores: transporte, energia, moradia) · pergunta "acaba em 2027?".
- Mapa: `dados/ucrania_ocupacao_aprox.json` tem o contorno da Ucrânia e a área ocupada aproximada (linha de frente desenhada pela geografia conhecida; com as áreas oficiais das regiões dá ~116 mil km², ~19%). Marcar na tela "área aproximada". Contorno original: geoBoundaries UKR ADM1 (media.githubusercontent.com). Pernambuco: `br.json` usado em `scripts/render_mapa.py`.
- Montar no estilo de `scripts/render_congresso.py` / `render_mapa.py` (formato loop), mostrar 2 capas, ele escolhe, publicar na página do canal.

## Projeto avulso (fora dos canais)
- Comercial Ares do Horto para a corretora Ana Paula: `../projetos-avulsos/ares-do-horto-ana-paula/`, página https://claude.ai/artifact/LGuzdi6rUbFbUE8EgFspe7. Falta só o número do registro da incorporação no rodapé, se ela mandar.

## Ambiente
- Arquivos de trabalho (fontes, avatares, trilhas, vozes) ficam no scratchpad da sessão, que some quando a sessão termina; o kit de modelos é instalado por `setup.sh`. Os scripts de render estão em `scripts/`.
