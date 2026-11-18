# Aula "Cores e adjetivos" (s7-a1, 18/11/2026). Abertura falada em inglês e em português. Uso: python3 prep_aula.py $S aulas/aula_cores.py
DIR = "aula_cores"
PINS = [62.43, 68.01]   # "or a red car?" termina 62,19 e "A red car!" começa 62,68; "...two red cars?" termina 67,80 e "Two red cars!" começa 68,22
VO_END = 74.65
CAP = [
 ("en", [(0.02, 0.51, "Hello!"), (0.81, 1.24, "Today:"), (1.68, 3.24, "colors and adjectives."), (3.53, 4.56, "A car red,"), (4.77, 5.97, "or a red car?"), (6.30, 6.93, "Careful!")]),
 ("pt!", [(7.46, 7.80, "Olá!"), (8.10, 8.59, "Hoje:"), (8.76, 10.14, "cores e adjetivos."), (10.39, 11.45, "Cuidado com essa!")]),
 ("en", [(11.96, 12.54, "First,"), (12.67, 13.33, "the colors:"), (13.78, 14.23, "red,"), (14.55, 15.01, "blue,"), (15.29, 15.81, "green,"), (16.09, 16.62, "yellow,"), (16.90, 17.30, "black,"), (17.57, 18.05, "white.")]),
 ("pt", [(18.52, 19.75, "Primeiro, as cores:"), (20.09, 20.71, "vermelho,"), (20.86, 21.39, "azul,"), (21.61, 22.97, "verde, amarelo,"), (23.20, 23.61, "preto"), (23.74, 24.26, "e branco.")]),
 ("en", [(24.78, 25.46, "Rule one:"), (25.91, 28.08, "the adjective comes before the noun."), (28.52, 29.47, "A red car."), (29.84, 30.70, "A blue bag.")]),
 ("pt", [(31.20, 31.88, "Regra um:"), (32.13, 34.39, "o adjetivo vem antes do substantivo.")]),
 ("en", [(34.90, 35.61, "Rule two:"), (36.04, 37.88, "adjectives never take S."), (38.28, 39.57, "Two red cars."), (39.79, 40.68, "Not reds.")]),
 ("pt", [(41.13, 41.88, "Regra dois:"), (42.18, 44.01, "adjetivo não vai para o plural.")]),
 ("en", [(44.53, 45.27, "Rule three:"), (45.75, 48.41, "A or AN depends on the next sound."), (48.75, 49.78, "A big apple."), (50.10, 51.09, "An old car."), (51.42, 52.37, "An orange bag.")]),
 ("pt", [(52.88, 53.67, "Regra três:"), (53.98, 56.96, "A ou AN depende do som da palavra seguinte.")]),
 ("en", [(57.42, 58.08, "Quiz time!"), (58.57, 59.61, "Which one is correct:"), (59.94, 60.81, "a car red,"), (61.06, 62.19, "or a red car?")]),
 ("en", [(62.68, 63.61, "A red car!")]),
 ("en", [(64.13, 64.64, "Next one:"), (65.10, 67.80, "two reds cars, or two red cars?")]),
 ("en", [(68.22, 69.48, "Two red cars!")]),
 ("en", [(69.91, 71.22, "Comment if you got it right,"), (71.36, 72.92, "follow and save to review!")]),
 ("en", [(73.24, 74.65, "Follow Teacher Eliezio!")]),
]
# ids 101..112 = sorrindo, bravo, desconfiado, piscando, surpreso, sobrancelha, pensando-lado, piscando-2, bravo-livro, assustado, pensando-queixo, malicioso
EXPR = [(0, 101), (3.53, 103), (6.30, 110), (7.46, 108), (12.67, 101), (24.78, 106), (28.52, 101), (34.90, 102), (38.28, 101), (44.53, 106), (48.75, 101), (57.42, 104), (69.91, 104), (73.24, 101)]
THINK_LIST = [111, 107]
REVEAL_LIST = [105, 101]
WHOOSH = (3.4, 11.85, 24.65, 34.8, 44.4, 57.3)
CLICKS = (1.68, 13.78, 14.55, 15.29, 16.09, 16.90, 17.57, 28.52, 29.84, 38.28, 39.79, 48.75, 50.10, 51.42)
CTA_THUD = 69.91
TK = dict(hook=0, tit=1.68, car1=3.53, car2=4.77, care=6.30, cor=11.96, c0=13.78, c1=14.55, c2=15.29, c3=16.09, c4=16.90, c5=17.57, cpt=18.52,
          p0=20.09, p1=20.86, p2=21.61, p3=22.30, p4=23.20, p5=23.74,
          r1=24.78, r1h=25.91, r1a=28.52, r1b=29.84, r2=34.90, r2h=36.04, r2a=38.28, r2b=39.79,
          r3=44.53, r3h=45.75, r3a=48.75, r3b=50.10, r3c=51.42, quiz=57.42, q1=58.57, q2=64.13, cta=69.91, follow=73.24, save=71.40)
