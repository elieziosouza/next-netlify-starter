# Aula "Plural" (s6-a1, 02/11/2026). Uso: python3 prep_aula.py $S aulas/aula_plural.py
DIR = "aula_plural"
PINS = [52.58, 57.25]   # "two watches?" termina 52,36 e "Two watches!" começa 52,79; "two parties?" 57,06 e "Two parties!" 57,43
VO_END = 61.82
CAP = [
 ("en", [(0.09, 0.55, "Hello!"), (0.86, 1.32, "Today:"), (1.69, 2.79, "plural in English.")]),
 ("en", [(3.10, 3.94, "One child,"), (4.18, 4.97, "two childs?"), (5.30, 5.98, "Careful!")]),
 ("pt", [(6.12, 7.21, "Cuidado com essa!")]),
 ("en", [(7.58, 9.70, "Most words: just add S."), (10.04, 11.72, "One book, two books.")]),
 ("pt", [(11.82, 13.86, "Na maioria, é só colocar S.")]),
 ("en", [(14.17, 17.93, "Words ending in S, SH, CH or X:"), (18.17, 19.21, "add ES."), (19.54, 21.29, "One bus, two buses."), (21.56, 23.27, "One dish, two dishes.")]),
 ("pt", [(23.51, 27.94, "Terminou em S, SH, CH ou X: coloca ES.")]),
 ("en", [(28.28, 29.54, "Consonant plus Y:"), (29.88, 31.91, "change the Y to IES."), (32.22, 32.97, "One baby,"), (33.21, 34.05, "two babies.")]),
 ("pt", [(34.39, 35.69, "Consoante mais Y:"), (36.06, 37.93, "troca o Y por IES.")]),
 ("en", [(38.26, 39.37, "Some are irregular:"), (39.77, 41.41, "one child, two children."), (41.82, 43.24, "One man, two men."), (43.58, 45.19, "One foot, two feet.")]),
 ("pt", [(45.46, 47.62, "Alguns são irregulares: é só decorar.")]),
 ("en", [(48.02, 48.61, "Quiz time!"), (49.02, 50.05, "Which one is correct:"), (50.39, 52.36, "two watchs, or two watches?")]),
 ("en", [(52.79, 53.77, "Two watches!")]),
 ("en", [(54.10, 54.66, "Next one:"), (54.92, 57.06, "two partys, or two parties?")]),
 ("en", [(57.43, 58.57, "Two parties!")]),
 ("en", [(58.90, 61.82, "Comment if you got it right, follow and save to review!")]),
]
# 1 sorrindo, 2 desconfiado, 7 surpreso, 8 piscando, 10 bravo, 11 assustado (9 pensando entra sozinho no contador)
EXPR = [(0, 1), (3.10, 2), (4.18, 10), (6.12, 1), (14.17, 2), (19.54, 1), (28.28, 2), (32.22, 1), (38.26, 11), (39.77, 7), (41.82, 1),
        (50.39, 2), (54.0, 1), (54.92, 2), (58.7, 1), (60.5, 8), (61.4, 1)]
WHOOSH = (2.95, 7.45, 14.05, 28.15, 38.1, 47.9)
CLICKS = (1.69, 10.04, 10.94, 19.54, 20.4, 21.56, 22.71, 32.22, 33.21, 39.77, 40.6, 41.82, 42.5, 43.58, 44.3)
CTA_THUD = 58.95
TK = dict(hook=0, child=2.95, s=7.45, s1=10.04, s2=10.94, es=14.05, es0=18.17, es1=19.54, es2=20.4, es3=21.56, es4=22.71, esPt=23.51,
          y=28.15, y0=29.88, y1=32.22, y2=33.21, yPt=34.39, irr=38.1, irr1=39.77, irr2=41.82, irr3=43.58, irrPt=45.46,
          quiz=47.9, q1=49.02, q2=54.10, cta=58.9, follow=60.3, save=61.0)
