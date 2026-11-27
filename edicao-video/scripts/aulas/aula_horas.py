# Aula "As horas" (s9-a1, 26/11/2026). Abertura falada em inglês e em português. Uso: python3 prep_aula.py $S aulas/aula_horas.py
# Tempos vêm das pausas da voz (silencedetect, 52 trechos); dentro de cada trecho, peso por letras.
DIR = "aula_horas"
SP = [(0.0, 0.5), (0.9, 1.37), (1.8, 2.71), (3.16, 4.0), (4.4, 4.77), (5.09, 5.52), (5.82, 6.51), (6.84, 7.46), (7.89, 9.39), (9.76, 10.62), (10.97, 12.2), (12.56, 13.39), (13.79, 14.54), (14.9, 15.49), (15.85, 16.67), (17.02, 17.62), (17.94, 19.0), (19.21, 19.8), (20.17, 20.91), (21.24, 22.02), (22.43, 23.2), (23.54, 24.43), (24.79, 25.83), (26.18, 26.99), (27.19, 29.24), (29.53, 30.25), (30.55, 31.6), (32.03, 32.82), (33.16, 35.03), (35.4, 36.51), (36.87, 37.79), (38.12, 38.95), (39.19, 40.87), (41.05, 42.38), (42.64, 43.46), (43.75, 44.97), (45.18, 46.46), (46.81, 47.44), (47.74, 48.8), (49.13, 49.98), (50.3, 51.07), (51.45, 52.21), (52.45, 53.56), (53.89, 54.58), (54.96, 56.96), (57.17, 58.23), (58.64, 59.6), (60.0, 60.53), (60.79, 63.39), (63.75, 64.95), (65.28, 68.23), (68.53, 70.08)]
PINS = [58.43, 63.57]   # "or half past eight?" termina 58,23 e "Half past seven!" começa 58,64; "...quarter to five?" termina 63,39 e "Quarter to five!" começa 63,75
VO_END = 70.08
def wt(sp, text, i):
    a, b = SP[sp]; ws = text.split(); tot = sum(len(w) + 1 for w in ws); acc = sum(len(w) + 1 for w in ws[:i]); return round(a + (b - a) * acc / tot, 2)
def ch(sp, text): return (SP[sp][0] + (0.02 if sp == 0 else 0), SP[sp][1], text)
CTA_TXT = "Comment if you got it right, follow and save to review!"
CAP = [
 ("en", [ch(0, "Hello!"), ch(1, "Today:"), ch(2, "telling the time."), ch(3, "What time is it?")]),
 ("pt!", [ch(4, "Olá!"), ch(5, "Hoje:"), ch(6, "as horas."), ch(7, "Que horas são?")]),
 ("en", [ch(8, "To ask the time, say:"), ch(9, "What time is it?")]),
 ("pt", [ch(10, "Para perguntar as horas:"), ch(11, "What time is it?")]),
 ("en", [ch(12, "Rule one:"), ch(13, "o'clock."), ch(14, "Three o'clock.")]),
 ("pt", [ch(15, "Regra um:"), ch(16, "hora exata é"), ch(17, "o'clock."), ch(18, "Três horas:"), ch(19, "three o'clock.")]),
 ("en", [ch(20, "Rule two:"), ch(21, "half past."), ch(22, "Half past three.")]),
 ("pt", [ch(23, "Regra dois:"), ch(24, "meia hora é half past."), ch(25, "Três e meia:"), ch(26, "half past three.")]),
 ("en", [ch(27, "Rule three:"), ch(28, "quarter past, and quarter to."), ch(29, "Quarter past three."), ch(30, "Quarter to four.")]),
 ("pt", [ch(31, "Regra três:"), ch(32, "quarter é quinze minutos."), ch(33, "Past é depois:"), ch(34, "três e quinze."), ch(35, "To é antes:"), ch(36, "quinze para as quatro.")]),
 ("en", [ch(37, "Easy way:"), ch(38, "just say the numbers."), ch(39, "Three fifteen."), ch(40, "Three thirty.")]),
 ("pt", [ch(41, "Jeito fácil:"), ch(42, "fale só os números.")]),
 ("en", [ch(43, "Quiz time!"), ch(44, "What time is it: half past seven,"), ch(45, "or half past eight?")]),
 ("en", [ch(46, "Half past seven!")]),
 ("en", [ch(47, "Next one:"), ch(48, "quarter past five, or quarter to five?")]),
 ("en", [ch(49, "Quarter to five!")]),
 ("en", [(SP[50][0], wt(50, CTA_TXT, 6) - 0.05, "Comment if you got it right,"), (wt(50, CTA_TXT, 6), SP[50][1], "follow and save to review!")]),
 ("en", [ch(51, "Follow Teacher Eliezio!")]),
]
# ids 101..112 = sorrindo, bravo, desconfiado, piscando, surpreso, sobrancelha, pensando-lado, piscando-2, bravo-livro, assustado, pensando-queixo, malicioso
EXPR = [(0, 101), (3.16, 103), (4.4, 108), (7.89, 101), (12.56, 106), (20.17, 101), (22.43, 104), (27.19, 106), (32.03, 103), (38.12, 101), (46.81, 108), (53.89, 105), (65.28, 104), (68.53, 101)]
THINK_LIST = [111, 107]
REVEAL_LIST = [105, 101]
WHOOSH = (7.8, 12.5, 22.4, 32.0, 46.7, 53.8)
CLICKS = (SP[13][0], SP[14][0], SP[21][0], SP[22][0], SP[29][0], SP[30][0], SP[39][0], SP[40][0])
CTA_THUD = SP[50][0]
TK = dict(hook=0, tit=SP[2][0], ask=SP[3][0], pt=SP[4][0], perg=SP[8][0], perg2=SP[9][0], pergpt=SP[10][0],
          r1=SP[12][0], r1a=SP[13][0], r1b=SP[14][0], r1p=SP[16][0], r2=SP[20][0], r2a=SP[21][0], r2b=SP[22][0], r2p=SP[24][0],
          r3=SP[27][0], r3a=SP[29][0], r3b=SP[30][0], r3q=SP[32][0], r3p=SP[33][0], r3t=SP[35][0],
          ez=SP[37][0], ez1=SP[39][0], ez2=SP[40][0], quiz=SP[43][0], q1=SP[44][0], q2=SP[47][0], cta=SP[50][0], follow=SP[51][0],
          save=wt(50, CTA_TXT, 7))
