# Quiz relâmpago de 7 palavras: no hotel (14/11/2026). Abertura falada em inglês e em português; fecha com "Follow Teacher Eliezio!".
# Uso: python3 prep_aula.py $S aulas/aula_quizhotel.py
DIR = "aula_quizhotel"
GAP = 3.2
PINS = [17.90, 21.03, 24.10, 27.46, 30.96, 36.06, 39.27]
VO_END = 46.10
CAP = [
 ("en", [(0.09, 0.51, "Hello!"), (0.81, 1.24, "Today:"), (1.61, 2.37, "quick quiz!"), (2.69, 4.58, "How do you say these words in English?"), (4.87, 5.85, "At the hotel!"), (6.22, 7.24, "Three seconds each!")]),
 ("pt!", [(7.72, 8.05, "Olá!"), (8.39, 8.78, "Hoje:"), (8.97, 9.87, "quiz relâmpago!"), (10.19, 12.24, "Como se fala estas palavras em inglês?"), (12.62, 13.21, "No hotel!"), (13.54, 14.59, "Três segundos cada!"), (14.86, 15.55, "Você consegue?")]),
 ("en", [(16.05, 16.72, "Number one:"), (17.21, 17.68, "quarto.")]),
 ("en", [(18.13, 18.66, "Room!")]),
 ("en", [(19.24, 19.92, "Number two:"), (20.21, 20.80, "chave.")]),
 ("en", [(21.27, 21.68, "Key!")]),
 ("en", [(22.29, 22.99, "Number three:"), (23.37, 23.90, "toalha.")]),
 ("en", [(24.29, 24.80, "Towel!")]),
 ("en", [(25.41, 26.13, "Number four:"), (26.46, 27.29, "café da manhã.")]),
 ("en", [(27.63, 28.39, "Breakfast!")]),
 ("en", [(28.97, 29.80, "Number five:"), (30.03, 30.81, "recepção.")]),
 ("en", [(31.12, 31.96, "Front desk!"), (32.29, 33.57, "Reception also works.")]),
 ("en", [(34.10, 34.91, "Number six:"), (35.13, 35.87, "elevador.")]),
 ("en", [(36.26, 36.93, "Elevator!")]),
 ("en", [(37.50, 38.24, "Number seven:"), (38.55, 39.11, "andar.")]),
 ("en", [(39.43, 39.97, "Floor!")]),
 ("en", [(40.53, 41.57, "How many did you get?")]),
 ("en", [(41.82, 44.35, "Comment your score, follow and save to review!")]),
 ("en", [(44.68, 46.10, "Follow Teacher Eliezio!")]),
]
# ids 101..112 = sorrindo, bravo, desconfiado, piscando, surpreso, sobrancelha, pensando-lado, piscando-2, bravo-livro, assustado, pensando-queixo, malicioso
EXPR = [(0, 101), (7.72, 108), (14.86, 103), (32.29, 106), (41.82, 104), (44.68, 101)]
THINK_LIST = [112, 109, 111, 102, 107, 103, 106]
REVEAL_LIST = [101, 105, 110, 104, 108, 101, 105]
WHOOSH = (15.9,)
CLICKS = (1.4, 16.05, 19.24, 22.29, 25.41, 28.97, 34.10, 37.50)
CTA_THUD = 40.53
TK = dict(title=0.81, pt0=14.86, q0=16.05, q1=19.24, q2=22.29, q3=25.41, q4=28.97, q5=34.10, q6=37.50, cta=40.53, follow=44.68, save=43.40)
