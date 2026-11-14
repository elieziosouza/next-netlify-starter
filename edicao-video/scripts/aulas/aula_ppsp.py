# Aula "Present Perfect × Simple Past" (14/11/2026, B1). Uso: python3 prep_aula.py $S aulas/aula_ppsp.py
DIR = "aula_ppsp"
PINS = [48.83, 60.00]   # fim da 2ª opção ("or I visited Paris last year" 48,61) e início da resposta (49,05); idem no 2º quiz (59,81 / 60,18)
VO_END = 67.42
CAP = [
 ("en", [(0.09, 0.49, "Hello!"), (0.79, 1.29, "Today:")]),
 ("en", [(1.66, 3.97, "Present Perfect versus Simple Past.")]),
 ("en", [(4.34, 5.93, "\"I have seen him yesterday.\"")]),
 ("en", [(6.30, 7.45, "Many students say this."), (7.65, 8.49, "It's wrong!")]),
 ("pt", [(8.82, 9.99, "Muita gente fala assim."), (10.23, 11.05, "Está errado!")]),
 ("en", [(11.42, 13.64, "Use Simple Past for a finished time:")]),
 ("en", [(14.01, 14.95, "yesterday,"), (15.05, 15.85, "last year,"), (15.95, 16.61, "two days ago.")]),
 ("pt", [(17.05, 19.49, "Simple Past é para um tempo que já acabou:"), (19.86, 22.50, "ontem, ano passado, dois dias atrás.")]),
 ("en", [(22.84, 24.26, "I saw him yesterday.")]),
 ("en", [(24.70, 26.90, "Use Present Perfect when the time is not finished,"), (27.20, 29.06, "or when it still matters now:")]),
 ("en", [(29.56, 30.73, "ever, never,"), (30.97, 32.42, "already, since.")]),
 ("pt", [(32.82, 35.00, "Present Perfect é para quando o tempo não acabou,"), (35.40, 37.13, "ou quando ainda importa agora.")]),
 ("en", [(37.53, 38.89, "I have seen that movie.")]),
 ("en", [(39.22, 41.19, "I have lived here since 2020.")]),
 ("en", [(41.62, 42.25, "Quiz time!"), (42.58, 43.69, "Which one is correct:")]),
 ("en", [(44.02, 46.09, "I have visited Paris last year,")]),
 ("en", [(46.36, 48.61, "or I visited Paris last year?")]),
 ("en", [(49.05, 50.98, "I visited Paris last year!"), (51.29, 52.58, "Last year is finished.")]),
 ("en", [(52.95, 53.45, "Next one!"), (53.85, 54.89, "Which one is correct:")]),
 ("en", [(55.19, 57.22, "I have lived here since 2020,")]),
 ("en", [(57.46, 59.81, "or I lived here since 2020?")]),
 ("en", [(60.18, 62.37, "I have lived here since 2020!")]),
 ("en", [(62.78, 65.64, "Comment if you got it right, follow and save to review!")]),
 ("en", [(65.91, 67.42, "Follow Teacher Eliezio!")]),
]
# 1 sorrindo, 2 desconfiado, 7 surpreso, 8 piscando, 10 bravo, 11 assustado (9 pensando entra sozinho no contador)
EXPR = [(0, 1), (4.34, 11), (6.30, 2), (8.82, 1), (11.42, 1), (22.84, 8), (24.70, 2), (29.56, 1), (37.53, 7), (39.22, 1), (41.62, 1),
        (51.29, 1), (60.18, 1), (62.78, 8), (65.91, 1)]
WHOOSH = (4.2, 11.3, 24.55, 41.4)
CLICKS = (14.01, 15.05, 15.95, 22.84, 29.56, 30.97, 37.53, 39.22)
CTA_THUD = 62.7
TK = dict(hook=0, wrong=4.34, wrongPt=8.82, sp=11.42, sp1=14.01, sp2=15.05, sp3=15.95, spPt=17.05, spEx=22.84,
          pp=24.70, ppE=29.56, ppA=30.97, ppPt=32.82, ppEx1=37.53, ppEx2=39.22,
          quiz=41.55, q1=42.58, q2=52.95, cta=62.70, follow=64.10, save=64.75)
