# Comercial Ares do Horto (corretora Ana Paula)

Projeto avulso, separado dos canais Eliezio Souza e Teacher Eliezio. Não usar as regras nem as identidades desses canais aqui.

- Cliente: Ana Paula, corretora de imóveis, CRECI-SP 201.926, WhatsApp (11) 97246-9161.
- Empreendimento: Ares do Horto, Plano&Plano, Horto do Ipê, Zona Sul de São Paulo.
- Formato: vertical 1080x1920, 30 s, minimalista (off-white #f4f1ea, verde #264a3a, DM Serif Display + Inter), trilha própria gerada no script.
- Cenas: fachada (0-4,4 s), localização (4,4-8,2), planta oficial em 3D em camadas, com laje, piso e paredes extrudadas a partir da cor das paredes (8,2-16,4), lazer com fotos (16,4-23,4), cartão da corretora com foto (23,4-30).
- Dados usados só onde as fontes batem: 2 dormitórios, opções com e sem varanda, piscinas, academia, playground, pet place, churrasqueira. Metragem, preço e entrega ficaram de fora (os portais divergem).
- Pendente: número do registro da incorporação no rodapé (obrigatório em anúncio de imóvel na planta).
- Imagens (plantas e perspectivas da incorporadora, foto da corretora) ficam em `assets/` fora do repositório.
- Página de download: https://claude.ai/artifact/LGuzdi6rUbFbUE8EgFspe7

Uso: `python3 render_ares.py SAIDA part:i:n` em paralelo, concat em `video.mp4`, depois `python3 render_ares.py FINAL.mp4 mux`.
