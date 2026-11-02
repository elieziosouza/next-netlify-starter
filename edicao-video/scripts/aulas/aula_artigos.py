# Aula "A, an, the" (s5-a1, 01/11/2026). Uso: python3 prep_aula.py $S aulas/aula_artigos.py
DIR = "aula_artigos"
PINS = [44.70, 49.12]   # "an orange?" termina 44,55 e "An orange!" começa 44,86; "an uniform?" 48,93 e "A uniform!" 49,30
VO_END = 53.50
CAP = [
 ("en", [(0.09, 0.58, "Hello!"), (0.89, 1.35, "Today:"), (1.59, 3.37, "a, an, and the.")]),
 ("en", [(3.70, 6.47, "A university, or an university?"), (6.78, 8.58, "Many Brazilians get this one wrong.")]),
 ("pt", [(8.86, 10.50, "Muita gente erra essa!")]),
 ("en", [(10.78, 13.10, "Use \"a\" before a consonant sound:"), (13.25, 14.73, "a dog, a car.")]),
 ("pt", [(15.13, 17.13, "\"A\" antes de som de consoante.")]),
 ("en", [(17.43, 19.56, "Use \"an\" before a vowel sound:"), (19.99, 21.38, "an apple, an egg.")]),
 ("pt", [(21.69, 23.43, "\"An\" antes de som de vogal.")]),
 ("en", [(23.70, 24.20, "But listen:"), (24.47, 26.31, "it's the sound, not the letter."), (26.62, 27.72, "A university,"), (27.96, 28.55, "an hour.")]),
 ("pt", [(28.95, 30.57, "Vale o som, não a letra.")]),
 ("en", [(30.90, 31.56, "And \"the\"?"), (31.83, 33.25, "Use it for something specific:"), (33.66, 34.18, "the sun,"), (34.40, 35.53, "the book on the table.")]),
 ("pt", [(35.86, 38.44, "\"The\" é o, a, os, as:"), (38.68, 39.94, "uma coisa específica.")]),
 ("en", [(40.25, 40.90, "Quiz time!"), (41.27, 42.28, "Which one is correct:"), (42.58, 44.55, "a orange, or an orange?")]),
 ("en", [(44.86, 45.70, "An orange!")]),
 ("en", [(45.98, 46.50, "Next one:"), (46.81, 48.93, "a uniform, or an uniform?")]),
 ("en", [(49.30, 50.15, "A uniform!")]),
 ("en", [(50.55, 53.50, "Comment if you got it right, follow and save to review!")]),
]
EXPR = [(0, 1), (3.70, 10), (6.78, 2), (8.86, 1), (23.70, 11), (26.62, 1), (42.58, 2), (45.9, 1), (46.81, 2), (50.4, 1), (52.2, 8), (53.1, 1)]
WHOOSH = (3.6, 10.7, 17.3, 23.6, 30.8, 40.1)
CLICKS = (1.62, 2.1, 2.75, 13.25, 14.05, 19.99, 20.75, 26.62, 27.96, 33.66, 34.40)
CTA_THUD = 50.6
TK = dict(hook=0, uni=3.6, a=10.7, a1=13.25, a2=14.05, an=17.3, an1=19.99, an2=20.75, som=23.6, som1=24.47, som2=26.62,
          som3=27.96, the=30.8, the1=33.66, the2=34.40, thept=35.86, quiz=40.1, q1=41.27, q2=45.98, cta=50.55, follow=52.0, save=52.8)
