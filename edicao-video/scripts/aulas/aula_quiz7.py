# Quiz relâmpago de 7 palavras (Teacher Eliezio, 03/11/2026). Uso: python3 prep_aula.py $S aulas/aula_quiz7.py
DIR = "aula_quiz7"
GAP = 3.2   # contador de 3 s + 0,2 s de respiro; a resposta entra logo depois do "ding"
# pausa entre a palavra em português e a resposta em inglês (fim da palavra / começo da resposta)
PINS = [11.02, 14.38, 17.76, 21.15, 24.63, 28.00, 31.26]
VO_END = 40.86
REVEAL_EXPR = 1   # sorrindo em cada resposta (7 surpresas seguidas cansam)
CAP = [
 ("en", [(0.09, 0.55, "Hello!"), (0.79, 2.28, "Today: quick quiz!"), (2.58, 4.55, "How do you say these words in English?"), (4.79, 5.89, "Three seconds each!")]),
 ("pt", [(6.20, 6.95, "Você consegue?"), (7.22, 8.29, "Três segundos cada!")]),
 ("en", [(8.76, 9.32, "Number one:"), (9.78, 10.85, "cachorro-quente.")]),
 ("en", [(11.19, 11.81, "Hot dog!")]),
 ("en", [(12.28, 13.00, "Number two:"), (13.30, 14.21, "geladeira.")]),
 ("en", [(14.55, 15.11, "Fridge!")]),
 ("en", [(15.58, 16.36, "Number three:"), (16.70, 17.61, "guarda-chuva.")]),
 ("en", [(17.91, 18.53, "Umbrella!")]),
 ("en", [(19.03, 19.78, "Number four:"), (20.15, 20.97, "travesseiro.")]),
 ("en", [(21.34, 21.73, "Pillow!")]),
 ("en", [(22.23, 23.11, "Number five:"), (23.38, 24.45, "liquidificador.")]),
 ("en", [(24.82, 25.35, "Blender!")]),
 ("en", [(25.82, 26.60, "Number six:"), (26.85, 27.85, "aniversário.")]),
 ("en", [(28.15, 28.81, "Birthday!")]),
 ("en", [(29.24, 29.99, "Number seven:"), (30.23, 31.11, "sobremesa.")]),
 ("en", [(31.42, 32.13, "Dessert!"), (32.47, 33.77, "Careful: two S."), (34.04, 36.42, "With one S, desert is \"deserto\"!")]),
 ("en", [(36.89, 40.86, "How many did you get? Comment your score, follow and save to review!")]),
]
EXPR = [(0, 1), (8.70, 2), (32.47, 7), (34.04, 1), (39.4, 8), (40.4, 1)]
WHOOSH = (8.60,)
CLICKS = (1.4, 9.78, 13.30, 16.70, 20.15, 23.38, 26.85, 30.23)
CTA_THUD = 36.95
TK = dict(title=0.79, pt0=6.20, q0=8.76, q1=12.28, q2=15.58, q3=19.03, q4=22.23, q5=25.82, q6=29.24, cta=36.89, follow=39.3, save=40.1)
