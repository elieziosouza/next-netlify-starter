# Aula de sala "Simple Past · What did you do last weekend?" (7ª e 8ª série, 06/11/2026), vídeo HORIZONTAL para compartilhar a tela.
# Sem contador, sem respostas e sem música: no fim, duas telas paradas para copiar (EXPLICAÇÃO e LIÇÃO). Uso: python3 prep_aula.py $S aulas/aula_simplepast.py
DIR = "aula_simplepast"
PINS = []
NO_MUSIC = True
VO_END = 93.28 + 8.4          # + as duas telas de cópia (4,2 s cada; ele pausa o tempo que precisar)
CAP = [
 ("en", [(0.09, 0.55, "Hello!"), (0.82, 1.29, "Today:"), (1.62, 2.76, "the Simple Past."), (3.19, 4.65, "What did you do last weekend?")]),
 ("pt", [(5.08, 6.98, "O que você fez no último fim de semana?")]),
 ("en", [(7.54, 9.99, "We use it for finished actions in the past."), (10.36, 11.40, "Look for these words:"), (11.70, 12.42, "yesterday,"), (12.70, 13.51, "last night,"), (13.75, 14.69, "last weekend,"), (14.97, 15.78, "two days ago.")]),
 ("pt", [(16.22, 18.31, "Usamos para ações que já terminaram."), (18.55, 20.61, "Essas palavras avisam que é passado.")]),
 ("en", [(21.05, 21.73, "Rule one:"), (22.14, 23.21, "regular verbs."), (23.51, 24.81, "Add E, D."), (25.30, 26.44, "Play, played."), (26.70, 27.95, "Watch, watched.")]),
 ("en", [(28.34, 29.16, "Ends in E?"), (29.66, 30.47, "Add only D."), (30.87, 32.10, "Like, liked."), (32.54, 33.67, "Consonant plus Y?"), (33.98, 35.69, "Change it to I, E, D."), (35.99, 37.29, "Study, studied.")]),
 ("pt", [(37.69, 40.10, "Nos regulares, coloque E, D no final.")]),
 ("en", [(40.50, 41.22, "Rule two:"), (41.53, 43.14, "irregular verbs change."), (43.61, 44.61, "Go, went."), (44.80, 46.10, "Eat, ate."), (46.33, 47.27, "Have, had."), (47.58, 48.55, "See, saw.")]),
 ("pt", [(48.92, 50.66, "Os irregulares a gente decora.")]),
 ("en", [(51.00, 52.49, "And it's the same for everybody:"), (52.79, 55.05, "I played, she played, they played.")]),
 ("pt", [(55.45, 57.77, "No passado, o verbo é igual para todos.")]),
 ("en", [(58.04, 59.75, "Rule three: the negative."), (60.15, 61.93, "Didn't, plus the normal verb."), (62.42, 63.08, "I didn't go."), (63.51, 65.22, "Never say: I didn't went.")]),
 ("pt", [(65.59, 68.07, "Na negativa: didn't e o verbo normal.")]),
 ("en", [(68.44, 69.09, "Rule four:"), (69.37, 70.09, "questions."), (70.49, 71.97, "Did, plus the normal verb."), (72.41, 73.51, "Did you watch the movie?"), (73.82, 74.63, "Yes, I did."), (74.87, 75.94, "No, I didn't.")]),
 ("pt", [(76.31, 78.69, "Na pergunta: Did e o verbo normal.")]),
 ("en", [(79.03, 80.07, "Now it's your turn!"), (80.50, 84.81, "Copy the explanation and the lesson into your notebook, and answer the five questions."), (85.08, 86.31, "Bring it to the next class!")]),
 ("pt", [(86.62, 87.53, "Agora é com você!"), (88.02, 93.28, "Copie a explicação e a lição no caderno e responda as cinco perguntas. Traga na próxima aula!")]),
]
EXPR = [(0, 1), (7.54, 2), (10.36, 1), (63.51, 10), (65.59, 1), (72.41, 2), (73.82, 1), (85.08, 8), (86.62, 1)]
WHOOSH = (7.4, 20.9, 40.4, 50.9, 57.9, 68.3, 78.9, 93.5, 97.7)
CLICKS = (11.70, 12.70, 13.75, 14.97, 25.30, 26.70, 30.87, 35.99, 43.61, 44.80, 46.33, 47.58, 52.79, 62.42, 63.51, 72.41, 73.82, 74.87)
CTA_THUD = 79.05
TK = dict(intro=0, words=7.54, w1=11.70, w2=12.70, w3=13.75, w4=14.97, reg=21.05, r1=25.30, r2=26.70, rE=28.34, rE1=30.87, rY=32.54, rY1=35.99,
          irr=40.50, i1=43.61, i2=44.80, i3=46.33, i4=47.58, same=51.0, s1=52.79, neg=58.04, n1=62.42, n2=63.51, q=68.44, q1=72.41, q2=73.82, q3=74.87,
          turn=79.03, copy1=93.6, copy2=97.8, cta=999)
