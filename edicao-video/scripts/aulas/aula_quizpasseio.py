# Quiz relâmpago de 7 palavras: no passeio turístico (18/11/2026). Abertura falada em inglês e em português; fecha com "Follow Teacher Eliezio!".
# Uso: python3 prep_aula.py $S aulas/aula_quizpasseio.py
DIR = "aula_quizpasseio"
GAP = 3.2
PINS = [18.93, 22.02, 24.97, 28.18, 31.46, 34.55, 39.49]
VO_END = 48.10
CAP = [
 ("en", [(0.02, 0.50, "Hello!"), (0.81, 1.26, "Today:"), (1.58, 2.29, "quick quiz!"), (2.63, 4.57, "How do you say these words in English?"), (4.86, 5.96, "On a city tour!"), (6.30, 7.32, "Three seconds each!")]),
 ("pt!", [(7.88, 8.24, "Olá!"), (8.52, 9.02, "Hoje:"), (9.14, 10.03, "quiz relâmpago!"), (10.40, 12.49, "Como se fala estas palavras em inglês?"), (12.87, 14.08, "No passeio turístico!"), (14.43, 15.47, "Três segundos cada!"), (15.71, 16.43, "Você consegue?")]),
 ("en", [(17.00, 17.65, "Number one:"), (18.01, 18.69, "ingresso.")]),
 ("en", [(19.17, 19.72, "Ticket!")]),
 ("en", [(20.26, 20.91, "Number two:"), (21.30, 21.83, "mapa.")]),
 ("en", [(22.21, 22.71, "Map!")]),
 ("en", [(23.26, 23.96, "Number three:"), (24.26, 24.76, "guia.")]),
 ("en", [(25.17, 25.87, "Tour guide!")]),
 ("en", [(26.38, 27.10, "Number four:"), (27.42, 27.97, "museu.")]),
 ("en", [(28.38, 29.03, "Museum!")]),
 ("en", [(29.55, 30.40, "Number five:"), (30.60, 31.28, "lembrança.")]),
 ("en", [(31.63, 32.35, "Souvenir!")]),
 ("en", [(32.87, 33.66, "Number six:"), (33.83, 34.38, "fila.")]),
 ("en", [(34.71, 35.25, "Line!"), (35.55, 36.84, "In the U.K., queue.")]),
 ("en", [(37.37, 38.08, "Number seven:"), (38.35, 39.32, "ponto turístico.")]),
 ("en", [(39.66, 40.35, "Landmark!"), (40.66, 42.21, "Tourist attraction also works.")]),
 ("en", [(42.62, 43.67, "How many did you get?")]),
 ("en", [(44.04, 46.48, "Comment your score, follow and save to review!")]),
 ("en", [(46.82, 48.10, "Follow Teacher Eliezio!")]),
]
# ids 101..112 = sorrindo, bravo, desconfiado, piscando, surpreso, sobrancelha, pensando-lado, piscando-2, bravo-livro, assustado, pensando-queixo, malicioso
EXPR = [(0, 101), (7.88, 108), (15.71, 103), (35.55, 106), (36.95, 101), (40.66, 106), (42.62, 101), (44.04, 104), (46.82, 101)]
THINK_LIST = [111, 107, 112, 102, 109, 103, 106]
REVEAL_LIST = [105, 101, 110, 104, 108, 101, 105]
WHOOSH = (16.85,)
CLICKS = (1.4, 17.00, 20.26, 23.26, 26.38, 29.55, 32.87, 37.37)
CTA_THUD = 42.62
TK = dict(title=0.81, pt0=15.71, q0=17.00, q1=20.26, q2=23.26, q3=26.38, q4=29.55, q5=32.87, q6=37.37, cta=42.62, follow=46.82, save=45.60)
