# Aula "For × Since" (14/11/2026, B1). Uso: python3 prep_aula.py $S aulas/aula_forsince.py
# Tempos tirados da transcrição (Whisper) + pausas da voz (vo_raw.mp3, 49,7 s).
DIR = "aula_forsince"
PINS = [33.95, 41.85]   # fim da pergunta (33,73 / 41,70) e início da resposta (34,14 / 42,02)
VO_END = 49.70
CAP = [
 ("en", [(0.09, 0.50, "Hello!"), (0.86, 1.29, "Today:")]),
 ("en", [(1.69, 3.44, "for versus since.")]),
 ("en", [(3.79, 5.50, "Both go with the Present Perfect,"), (5.70, 7.34, "and people mix them up all the time.")]),
 ("en", [(7.96, 9.19, "FOR is how long.")]),
 ("en", [(9.69, 10.75, "For two years."), (10.85, 11.67, "For ten minutes."), (11.88, 12.92, "For a long time.")]),
 ("en", [(13.43, 15.08, "SINCE is when it started.")]),
 ("en", [(15.48, 16.48, "Since 2020."), (16.76, 17.50, "Since Monday."), (17.82, 18.80, "Since I was a kid.")]),
 ("en", [(19.24, 22.39, "I have lived here for five years,")]),
 ("en", [(22.72, 24.50, "or I have lived here since 2020.")]),
 ("en", [(24.86, 26.60, "Same idea, two ways.")]),
 ("en", [(26.97, 27.56, "Quiz time!"), (27.96, 29.06, "Which one is correct:")]),
 ("en", [(29.37, 31.45, "I have worked here for three years,")]),
 ("en", [(31.60, 33.73, "or I have worked here since three years?")]),
 ("en", [(34.14, 34.60, "For!"), (34.82, 36.25, "Three years is how long.")]),
 ("en", [(36.70, 37.17, "Next one!")]),
 ("en", [(37.57, 39.55, "I have studied English for 2023,")]),
 ("en", [(39.85, 41.65, "or since 2023?")]),
 ("en", [(42.02, 42.67, "Since!"), (42.88, 44.87, "2023 is when it started.")]),
 ("en", [(45.30, 48.01, "Comment if you got it right, follow and save to review!")]),
 ("en", [(48.34, 49.70, "Follow Teacher Eliezio!")]),
]
# 1 sorrindo, 2 desconfiado, 7 surpreso, 8 piscando, 10 bravo, 11 assustado (9 pensando entra sozinho no contador)
EXPR = [(0, 1), (7.96, 1), (13.43, 8), (19.24, 1), (24.86, 8), (26.97, 1), (34.14, 1), (36.70, 1), (42.02, 1), (45.30, 8), (48.34, 1)]
WHOOSH = (3.7, 7.85, 13.3, 19.1, 26.85)
CLICKS = (9.69, 10.85, 11.88, 15.48, 16.76, 17.82, 19.24, 22.72)
CTA_THUD = 45.3
TK = dict(hook=0, pp=3.79, fo=7.96, fo1=9.69, fo2=10.85, fo3=11.88, si=13.43, si1=15.48, si2=16.76, si3=17.82,
          cmp=19.24, cmp2=22.72, cmpPt=24.86,
          quiz=26.90, q1=27.96, q2=36.70, cta=45.30, follow=46.70, save=47.30)
