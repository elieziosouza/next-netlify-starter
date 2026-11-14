# Série "Como se fala em inglês" · episódio 1: no aeroporto (14/11/2026). Uso: python3 prep_aula.py $S aulas/aula_aero.py
# Sem quiz (PINS vazio). Cada frase é dita duas vezes: a 2ª é para o aluno repetir junto.
DIR = "aula_aero"
PINS = []
VO_END = 21.28
CAP = [
 ("en", [(0.09, 0.52, "Hello!"), (0.81, 2.14, "How do you say it in English?")]),
 ("en", [(2.49, 3.35, "At the airport.")]),
 ("en", [(3.70, 4.62, "Where is the gate?")]),
 ("en", [(5.05, 6.00, "Where is the gate?")]),
 ("en", [(6.39, 7.80, "My flight was canceled.")]),
 ("en", [(8.16, 9.55, "My flight was canceled.")]),
 ("en", [(9.97, 11.02, "Can I check this bag?")]),
 ("en", [(11.39, 12.52, "Can I check this bag?")]),
 ("en", [(12.91, 14.13, "I lost my luggage.")]),
 ("en", [(14.49, 15.86, "I lost my luggage.")]),
 ("en", [(16.21, 17.70, "Save this for your next trip,"), (17.75, 19.31, "and share with a friend who is traveling!")]),
 ("en", [(19.64, 21.12, "Follow Teacher Eliezio!")]),
]
# 1 sorrindo, 2 desconfiado, 7 surpreso, 8 piscando, 10 bravo, 11 assustado
EXPR = [(0, 1), (3.70, 1), (5.05, 8), (8.16, 1), (9.97, 1), (11.39, 8), (12.91, 11), (14.49, 1), (16.21, 1), (19.64, 8)]
WHOOSH = (3.55, 6.25, 9.85, 12.8, 16.1)
CLICKS = (3.70, 6.39, 9.97, 12.91)
CTA_THUD = 16.21
TK = dict(hook=0, air=2.49, p1=3.70, r1=5.05, p2=6.39, r2=8.16, p3=9.97, r3=11.39, p4=12.91, r4=14.49,
          quiz=16.21, q1=16.21, q2=16.21, cta=16.21, follow=19.64, save=17.75)
