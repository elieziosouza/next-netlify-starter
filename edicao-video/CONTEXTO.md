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

## Feito: "Quanto já custou a guerra na Ucrânia" (30/10/2026)
- `scripts/render_ucrania.py`, capa A (mapa), publicado na página do canal (saiu o card "O povo ontem, ep. 2" por causa do limite de 256 MB).
- Voz: 825 créditos. Mapa: `dados/ucrania_ocupacao_aprox.json` (área aproximada, ~19% com as áreas oficiais).

## Feito: "CBS de 11,3%" (31/10/2026)
- Versão própria (roteiro e arte) a partir de um vídeo de referência do explica.ai. `scripts/render_cbs.py`, capa A, publicado (saiu o card "Bora votar"). Voz: 938 créditos.

## PENDENTE: TikTok Shop em lives (2 partes, didático, telas ilustrativas)
- Parte 1 (preparando a conta) com roteiro pronto, 781 créditos, esperando aprovação. Parte 2: sacola, teste e primeira live.
- Melhor ainda se ele gravar a tela do celular fazendo o caminho; senão, telas genéricas com aviso "ilustração".

## EM ANDAMENTO: vídeo horizontal (16:9, ~4 min) "A história do Silvio Santos"
- Roteiro aprovado (gancho + 8 capítulos + fecho), voz gerada e cobrada (2.853 créditos): flow ElevenLabs `zLpIxN8h3GyFGAANn3F1`, sessão `CCy9uiFdJOXbNEFjipdw`. Se a sessão cair, baixar com `creative_get_flow_run_status` (não gerar de novo).
- Visual: motion graphics no estilo do canal (marinho e dourado), sem trechos de TV; capa horizontal com 2 opções para ele escolher.

## Projeto avulso (fora dos canais)
- Comercial Ares do Horto para a corretora Ana Paula: `../projetos-avulsos/ares-do-horto-ana-paula/`, página https://claude.ai/artifact/LGuzdi6rUbFbUE8EgFspe7. Falta só o número do registro da incorporação no rodapé, se ela mandar.

## Ambiente
- Arquivos de trabalho (fontes, avatares, trilhas, vozes) ficam no scratchpad da sessão, que some quando a sessão termina; o kit de modelos é instalado por `setup.sh`. Os scripts de render estão em `scripts/`.
