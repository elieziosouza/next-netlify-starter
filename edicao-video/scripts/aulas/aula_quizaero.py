# Quiz relâmpago de 7 palavras: no aeroporto (14/11/2026). Mesmo formato do Quiz7. Uso: python3 prep_aula.py $S aulas/aula_quizaero.py
DIR = "aula_quizaero"
GAP = 3.2   # contador de 3 s + 0,2 s de respiro
# meio da pausa entre a palavra em português e a resposta em inglês
PINS = [12.06, 15.33, 18.48, 21.45, 25.16, 28.66, 31.82]
VO_END = 40.05
CAP = [
 ("en", [(0.09, 0.51, "Hello!"), (0.80, 1.22, "Today:"), (1.53, 2.23, "quick quiz!"), (2.60, 4.51, "How do you say these words in English?"), (4.78, 5.79, "At the airport!"), (6.03, 7.11, "Three seconds each!")]),
 ("pt", [(7.40, 8.11, "Você consegue?"), (8.49, 9.55, "Três segundos cada!")]),
 ("en", [(10.02, 10.60, "Number one:"), (11.04, 11.86, "passaporte.")]),
 ("en", [(12.25, 12.97, "Passport!")]),
 ("en", [(13.44, 14.07, "Number two:"), (14.45, 15.12, "bagagem.")]),
 ("en", [(15.54, 16.23, "Luggage!")]),
 ("en", [(16.68, 17.32, "Number three:"), (17.69, 18.26, "portão.")]),
 ("en", [(18.71, 19.22, "Gate!")]),
 ("en", [(19.68, 20.39, "Number four:"), (20.77, 21.26, "voo.")]),
 ("en", [(21.65, 22.31, "Flight!")]),
 ("en", [(22.79, 23.57, "Number five:"), (23.87, 24.96, "cartão de embarque.")]),
 ("en", [(25.37, 26.27, "Boarding pass!")]),
 ("en", [(26.72, 27.50, "Number six:"), (27.80, 28.47, "atraso.")]),
 ("en", [(28.86, 29.40, "Delay!")]),
 ("en", [(29.91, 30.60, "Number seven:"), (30.90, 31.66, "alfândega.")]),
 ("en", [(31.99, 32.74, "Customs!"), (33.04, 33.45, "Careful:"), (33.71, 35.69, "customs always ends with S.")]),
 ("en", [(36.11, 37.08, "How many did you get?")]),
 ("en", [(37.35, 40.05, "Comment your score, follow and save to review!")]),
]
EXPR = [(0, 1), (7.40, 2), (33.04, 7), (33.71, 1), (37.35, 8), (39.6, 1)]
REVEAL_EXPR = 1
WHOOSH = (9.9,)
CLICKS = (1.4, 10.02, 13.44, 16.68, 19.68, 22.79, 26.72, 29.91)
CTA_THUD = 36.11
TK = dict(title=0.80, pt0=7.40, q0=10.02, q1=13.44, q2=16.68, q3=19.68, q4=22.79, q5=26.72, q6=29.91, cta=36.11, follow=38.60, save=39.30)
