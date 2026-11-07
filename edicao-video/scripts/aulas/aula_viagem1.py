# Mini curso "Inglês para viajar", Aula 1: No aeroporto (07/11/2026). Horizontal 1920x1080.
# A voz (vo_raw.mp3) é a do professor com a simulação do oficial da imigração (voz Roger) inserida aos 78,70 s (22,65 s de trecho).
# Uso: python3 prep_aula.py $S aulas/aula_viagem1.py
DIR = "viagem1"
D = 22.65                                    # duração da simulação inserida aos 78,70 s
def s(t): return round(t + D, 2) if t >= 78.70 else t
PINS = [s(86.33)]                            # contador entre "Tourism, ou Ten days?" e "Ten days!"
VO_END = s(97.96)
def c(a, b, tx): return (s(a), s(b), tx)
CAP = [
 ("pt", [c(0.03, 3.17, "Você desceu do avião, pegou a fila da imigração..."), c(3.66, 4.11, "e agora?")]),
 ("pt", [c(4.74, 8.76, "Hoje você vai aprender as frases para passar pelo aeroporto sem medo.")]),
 ("pt", [c(9.32, 11.76, "Primeiro, o check-in. Para começar:")]),
 ("en", [c(12.39, 13.48, "I'd like to check in.")]), ("pt", [c(14.00, 15.44, "Eu gostaria de fazer o check-in.")]),
 ("en", [c(17.00, 17.98, "Here is my passport.")]), ("pt", [c(18.51, 19.77, "Aqui está meu passaporte.")]),
 ("pt", [c(20.39, 21.27, "Quer levar a mochila?")]),
 ("en", [c(21.82, 22.92, "Can I take this on board?")]), ("pt", [c(23.40, 24.52, "Posso levar isso a bordo?")]),
 ("en", [c(26.30, 27.40, "Window or aisle?")]), ("pt", [c(27.82, 29.09, "Janela ou corredor?")]),
 ("en", [c(30.67, 31.56, "Window, please.")]),
 ("pt", [c(32.10, 36.04, "Agora, a parte que dá mais frio na barriga: a imigração.")]),
 ("pt", [c(36.50, 39.79, "Fica tranquilo, as perguntas são quase sempre as mesmas.")]),
 ("en", [c(40.33, 41.63, "What's the purpose of your visit?")]), ("pt", [c(42.19, 43.60, "Qual o motivo da sua visita?")]),
 ("en", [c(45.16, 45.66, "Tourism."), c(46.64, 47.71, "I'm here on vacation.")]),
 ("en", [c(48.42, 49.50, "How long are you staying?")]), ("pt", [c(49.94, 51.20, "Quanto tempo você vai ficar?")]),
 ("en", [c(51.74, 52.47, "Ten days.")]), ("pt", [c(52.73, 53.48, "Dez dias.")]),
 ("en", [c(54.00, 54.88, "Where are you staying?")]), ("pt", [c(55.25, 56.15, "Onde você vai ficar?")]),
 ("en", [c(56.66, 57.90, "At a hotel downtown.")]), ("pt", [c(58.34, 59.24, "Em um hotel no centro.")]),
 ("en", [c(60.93, 62.24, "Do you have anything to declare?")]), ("pt", [c(62.63, 63.75, "Você tem algo a declarar?")]),
 ("en", [c(64.24, 65.13, "No, nothing.")]), ("pt", [c(65.56, 66.44, "Não, nada.")]),
 ("pt", [c(67.01, 71.74, "Dica de ouro: na imigração, responda curto, simples e com calma.")]),
 ("pt", [c(72.11, 73.94, "Ninguém quer ouvir sua história de vida.")]),
 ("pt", [c(74.44, 75.36, "Agora vamos treinar."), c(75.78, 78.53, "Escuta o oficial e repara nas respostas.")]),
 ("en", [(79.20, 80.35, "Next, please."), (80.70, 81.90, "Passport, please.")]),
 ("en", [(83.90, 85.70, "What's the purpose of your visit?")]),
 ("en", [(87.70, 89.00, "How long are you staying?")]),
 ("en", [(91.00, 92.20, "Where are you staying?")]),
 ("en", [(94.20, 95.95, "Do you have anything to declare?")]),
 ("en", [(97.95, 101.00, "Welcome to the United States. Enjoy your stay.")]),
 ("pt", [c(78.95, 79.45, "Quiz!"), c(79.92, 80.91, "O oficial pergunta:")]),
 ("en", [c(81.35, 82.39, "How long are you staying?")]),
 ("pt", [c(82.85, 83.81, "O que você responde:"), c(84.18, 86.10, "Tourism, ou Ten days?")]),
 ("en", [c(86.55, 87.22, "Ten days!")]),
 ("pt", [c(87.68, 90.21, "Tourism é para a pergunta do motivo da visita.")]),
 ("pt", [c(90.70, 93.46, "No PDF da aula tem mais frases para o aeroporto."), c(94.00, 96.13, "Nos vemos na próxima aula, no hotel.")]),
 ("en", [c(96.68, 97.96, "Follow Teacher Eliezio!")]),
]
CAP = [x for x in CAP]
# 1 sorrindo, 2 desconfiado, 7 surpreso, 8 piscando, 10 bravo, 11 assustado
EXPR = [(0, 11), (3.66, 2), (4.74, 1), (32.10, 11), (36.50, 1), (67.01, 8), (68.0, 1), (78.70, 2), (s(78.95), 1), (s(96.4), 8), (s(97.4), 1)]
WHOOSH = (9.2, 32.0, 66.9, 78.6, s(78.85), s(90.6))
CLICKS = (12.39, 17.00, 21.82, 26.30, 30.67, 40.33, 45.16, 48.42, 51.74, 54.00, 56.66, 60.93, 64.24)
CTA_THUD = s(96.6)
TK = dict(intro=0, goal=4.74, ci=9.2, c1=12.39, c2=17.00, c3=20.39, c4=26.30, c4a=30.67, imm=32.0, calm=36.50,
          i1=40.33, i1a=45.16, i1b=46.64, i2=48.42, i2a=51.74, i3=54.00, i3a=56.66, i4=60.93, i4a=64.24,
          tip=66.9, train=74.44, sim=78.70, simEnd=101.35, quiz=s(78.85), q1=s(81.35), qopt=s(84.18), after=s(87.68), pdf=s(90.6), cta=s(96.6), end=s(97.96))
