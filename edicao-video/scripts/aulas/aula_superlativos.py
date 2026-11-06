# Aula "Superlativos" (06/11/2026). Uso: python3 prep_aula.py $S aulas/aula_superlativos.py
DIR = "aula_superlativos"
PINS = [36.25, 41.05]   # "mountain in the world." termina 35,98 e "The highest!" começa 36,49; "day of my life!" 40,76 e "The best!" 41,26
VO_END = 43.71
CAP = [
 ("en", [(0.09, 1.66, "Who is the tallest in your family?")]),
 ("pt", [(2.24, 3.97, "Hoje: superlativos,"), (4.30, 6.53, "para dizer quem é o MAIS de todos.")]),
 ("en", [(6.89, 8.06, "Short adjectives:"), (8.41, 10.35, "THE plus EST."), (10.84, 11.30, "Tall,"), (11.61, 12.25, "the tallest.")]),
 ("en", [(12.81, 13.15, "Fast,"), (13.53, 14.27, "the fastest.")]),
 ("en", [(14.72, 15.52, "Ending in Y?"), (15.98, 17.29, "IEST."), (17.73, 18.16, "Happy,"), (18.47, 19.16, "the happiest.")]),
 ("en", [(19.59, 19.97, "Big,"), (20.33, 20.99, "the biggest.")]),
 ("pt", [(21.41, 22.32, "Dobra a consoante.")]),
 ("en", [(22.74, 23.83, "Long adjectives:"), (24.10, 24.70, "THE MOST."), (25.15, 25.77, "Beautiful,"), (26.04, 27.18, "the most beautiful.")]),
 ("en", [(27.62, 28.18, "Irregular:"), (28.64, 28.98, "good,"), (29.32, 29.83, "the best."), (30.42, 30.73, "Bad,"), (31.07, 31.64, "the worst.")]),
 ("en", [(32.10, 32.71, "Quiz time!"), (33.12, 34.69, "Mount Everest is the..."), (34.98, 35.98, "mountain in the world.")]),
 ("en", [(36.49, 37.23, "The highest!")]),
 ("en", [(37.71, 38.20, "Last one:"), (38.58, 39.58, "This is the..."), (39.81, 40.76, "day of my life!")]),
 ("en", [(41.26, 41.91, "The best!")]),
 ("en", [(42.50, 43.71, "Follow Teacher Eliezio!")]),
]
# 1 sorrindo, 2 desconfiado, 7 surpreso, 8 piscando, 10 bravo, 11 assustado (9 pensando entra sozinho no contador)
EXPR = [(0, 2), (2.24, 1), (14.72, 2), (17.73, 1), (22.74, 2), (25.15, 1), (27.62, 11), (28.64, 7), (30.42, 10), (31.07, 1),
        (33.12, 2), (37.71, 1), (38.58, 2), (42.3, 8), (43.3, 1)]
WHOOSH = (6.75, 14.6, 22.6, 27.5, 32.0)
CLICKS = (10.84, 11.61, 12.81, 13.53, 17.73, 18.47, 19.59, 20.33, 25.15, 26.04, 28.64, 29.32, 30.42, 31.07)
CTA_THUD = 42.4
TK = dict(hook=0, short=6.75, est=8.41, s1=10.84, s2=11.61, f1=12.81, f2=13.53, y=14.6, y0=15.98, y1=17.73, y2=18.47,
          b1=19.59, b2=20.33, bPt=21.41, long=22.6, l0=24.10, l1=25.15, l2=26.04, irr=27.5, i1=28.64, i2=29.32, i3=30.42, i4=31.07,
          quiz=32.0, q1=33.12, q2=37.71, cta=42.3, follow=42.6, save=43.3)
