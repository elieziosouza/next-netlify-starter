# Aula "Was e were" (s3-a2, 07/11/2026). Uso: python3 prep_aula.py $S aulas/aula_waswere.py
DIR = "aula_waswere"
PINS = [29.40, 33.12]   # "at the beach." termina 29,23 e "I was!" começa 29,58; "at the party." 32,93 e "They were!" 33,31
VO_END = 35.73
CAP = [
 ("en", [(0.04, 1.37, "Where were you last night?")]),
 ("pt", [(1.87, 3.77, "Hoje: was e were,"), (4.06, 5.36, "o passado do verbo to be.")]),
 ("en", [(5.78, 6.51, "I was,"), (6.76, 7.42, "he was,"), (7.57, 8.32, "she was,"), (8.52, 9.15, "it was.")]),
 ("en", [(9.54, 10.09, "You were,"), (10.44, 10.99, "we were,"), (11.25, 11.75, "they were.")]),
 ("pt", [(12.21, 14.43, "Am e is viram WAS."), (14.78, 16.24, "Are vira WERE.")]),
 ("en", [(16.68, 17.09, "Negative:"), (17.61, 18.18, "wasn't,"), (18.51, 19.01, "weren't.")]),
 ("en", [(19.44, 20.43, "I wasn't at home."), (20.82, 21.95, "They weren't at school.")]),
 ("en", [(22.40, 23.07, "Questions:"), (23.49, 24.22, "Was she happy?"), (24.66, 25.40, "Were you tired?")]),
 ("en", [(25.85, 26.47, "Quiz time!"), (26.91, 28.14, "Yesterday, I..."), (28.49, 29.23, "at the beach.")]),
 ("en", [(29.58, 30.26, "I was!")]),
 ("en", [(30.63, 31.08, "Last one:"), (31.47, 31.94, "They..."), (32.25, 32.93, "at the party.")]),
 ("en", [(33.31, 34.00, "They were!")]),
 ("en", [(34.48, 35.73, "Follow Teacher Eliezio!")]),
]
# 1 sorrindo, 2 desconfiado, 7 surpreso, 8 piscando, 10 bravo, 11 assustado (9 pensando entra sozinho no contador)
EXPR = [(0, 2), (1.87, 1), (12.21, 2), (14.78, 1), (16.68, 10), (19.44, 1), (22.40, 2), (23.49, 1), (26.91, 2), (30.63, 1), (31.47, 2),
        (34.3, 8), (35.3, 1)]
WHOOSH = (5.6, 12.05, 16.5, 22.25, 25.7)
CLICKS = (5.78, 6.76, 7.57, 8.52, 9.54, 10.44, 11.25, 17.61, 18.51, 19.44, 20.82, 23.49, 24.66)
CTA_THUD = 34.4
TK = dict(hook=0, conj=5.6, w1=5.78, w2=6.76, w3=7.57, w4=8.52, r1=9.54, r2=10.44, r3=11.25, rule=12.05, rWas=12.21, rWere=14.78,
          neg=16.5, n1=17.61, n2=18.51, n3=19.44, n4=20.82, q=22.25, q1a=23.49, q2a=24.66,
          quiz=25.7, q1=26.91, q2=30.63, cta=34.3, follow=34.5, save=35.2)
