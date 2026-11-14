# Quiz relâmpago de 7 palavras: no restaurante (14/11/2026). Mesmo formato do Quiz7. Usa as 12 expressões da segunda folha do avatar (ids 101..112).
# Uso: python3 prep_aula.py $S aulas/aula_quizrest.py
DIR = "aula_quizrest"
GAP = 3.2
PINS = [11.97, 15.03, 17.97, 21.06, 24.72, 27.89, 33.33]
VO_END = 38.30
CAP = [
 ("en", [(0.09, 0.52, "Hello!"), (0.79, 1.22, "Today:"), (1.54, 2.29, "quick quiz!"), (2.55, 4.52, "How do you say these words in English?"), (4.90, 5.85, "At the restaurant!"), (6.13, 7.17, "Three seconds each!")]),
 ("pt", [(7.49, 8.21, "Você consegue?"), (8.57, 9.63, "Três segundos cada!")]),
 ("en", [(10.13, 10.79, "Number one:"), (11.19, 11.79, "mesa.")]),
 ("en", [(12.14, 12.64, "Table!")]),
 ("en", [(13.12, 13.79, "Number two:"), (14.17, 14.89, "cardápio.")]),
 ("en", [(15.16, 15.66, "Menu!")]),
 ("en", [(16.16, 16.86, "Number three:"), (17.17, 17.82, "garçom.")]),
 ("en", [(18.11, 18.64, "Waiter!")]),
 ("en", [(19.12, 19.86, "Number four:"), (20.14, 20.91, "reserva.")]),
 ("en", [(21.20, 22.00, "Reservation!")]),
 ("en", [(22.48, 23.31, "Number five:"), (23.55, 24.58, "prato principal.")]),
 ("en", [(24.86, 25.72, "Main course!")]),
 ("en", [(26.16, 27.00, "Number six:"), (27.28, 27.76, "conta.")]),
 ("en", [(28.01, 28.46, "Bill!"), (28.82, 31.09, "In the U.S., check also works.")]),
 ("en", [(31.52, 32.23, "Number seven:"), (32.48, 33.18, "gorjeta.")]),
 ("en", [(33.48, 33.86, "Tip!")]),
 ("en", [(34.22, 35.27, "How many did you get?")]),
 ("en", [(35.57, 38.30, "Comment your score, follow and save to review!")]),
]
# ids 101..112 = sorrindo, bravo, desconfiado, piscando, surpreso, sobrancelha, pensando-lado, piscando-2, bravo-livro, assustado, pensando-queixo, malicioso
EXPR = [(0, 101), (7.49, 103), (28.82, 105), (35.57, 104), (36.9, 101)]
THINK_LIST = [111, 107, 106, 103, 102, 109, 112]     # expressão durante o contador de cada pergunta
REVEAL_LIST = [105, 101, 104, 110, 101, 108, 105]    # expressão na revelação de cada resposta
WHOOSH = (10.0,)
CLICKS = (1.4, 10.13, 13.12, 16.16, 19.12, 22.48, 26.16, 31.52)
CTA_THUD = 34.22
TK = dict(title=0.79, pt0=7.49, q0=10.13, q1=13.12, q2=16.16, q3=19.12, q4=22.48, q5=26.16, q6=31.52, cta=34.22, follow=36.80, save=37.50)
