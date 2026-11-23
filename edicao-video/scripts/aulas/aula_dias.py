# Aula "Dias e meses" (s8-a1, 23/11/2026). Abertura falada em inglês e em português. Uso: python3 prep_aula.py $S aulas/aula_dias.py
# Os tempos vêm das pausas da voz (silencedetect, janelas de 58 trechos); dentro de cada trecho, peso por letras.
DIR = "aula_dias"
SP = [(0.0, 0.49), (0.84, 1.28), (1.77, 2.99), (3.31, 5.28), (5.59, 6.11), (6.67, 7.01), (7.35, 7.78), (7.98, 9.08), (9.43, 11.24), (11.53, 12.55),
      (13.13, 14.52), (14.99, 15.55), (15.81, 16.47), (16.71, 20.47), (20.98, 22.2), (22.51, 27.34), (27.89, 28.97), (29.38, 30.9), (31.12, 31.72), (31.94, 32.46),
      (32.68, 33.13), (33.46, 33.97), (34.18, 34.74), (35.12, 36.49), (36.76, 37.41), (37.72, 38.32), (38.55, 39.11), (39.63, 40.9), (41.26, 48.45), (48.76, 50.08),
      (50.7, 51.37), (51.86, 54.84), (55.3, 55.83), (56.27, 56.86), (57.32, 58.03), (58.31, 61.51), (62.07, 62.75), (63.21, 64.48), (65.01, 65.62), (66.02, 66.65),
      (67.17, 67.96), (68.2, 69.42), (69.77, 71.84), (72.43, 73.12), (73.61, 75.76), (76.24, 77.03), (77.29, 78.9), (79.17, 80.47), (81.03, 81.74), (82.28, 83.89),
      (84.19, 85.63), (86.23, 86.96), (87.56, 88.04), (88.53, 90.08), (90.36, 91.51), (92.09, 92.62), (93.18, 96.15), (96.53, 97.95)]
PINS = [85.93, 91.80]   # "Saturday, or Sunday?" termina 85,63 e "Saturday!" começa 86,23; "May, or June?" termina 91,51 e "May!" começa 92,09
VO_END = 97.95
def wt(sp, text, i):
    """instante em que a palavra de índice i (separada por espaço) começa dentro do trecho sp"""
    a, b = SP[sp]; ws = text.split(); tot = sum(len(w) + 1 for w in ws); acc = sum(len(w) + 1 for w in ws[:i]); return round(a + (b - a) * acc / tot, 2)
def ch(sp, text): return (SP[sp][0] + (0.02 if sp == 0 else 0), SP[sp][1], text)
CAP = [
 ("en", [ch(0, "Hello!"), ch(1, "Today:"), ch(2, "days and months."), ch(3, "Small letter, or capital letter?"), ch(4, "Careful!")]),
 ("pt!", [ch(5, "Olá!"), ch(6, "Hoje:"), ch(7, "dias e meses."), ch(8, "Letra minúscula ou maiúscula?"), ch(9, "Cuidado com essa!")]),
 ("en", [ch(10, "First, the days:"), ch(11, "Monday,"), ch(12, "Tuesday,"), ch(13, "Wednesday, Thursday, Friday, Saturday, Sunday.")]),
 ("pt", [ch(14, "Primeiro, os dias:"), ch(15, "segunda, terça, quarta, quinta, sexta, sábado e domingo.")]),
 ("en", [ch(16, "Now, the months:"), ch(17, "January, February,"), ch(18, "March,"), ch(19, "April,"), ch(20, "May,"), ch(21, "June,")]),
 ("en", [ch(22, "July,"), ch(23, "August, September,"), ch(24, "October,"), ch(25, "November,"), ch(26, "December.")]),
 ("pt", [ch(27, "Agora, os meses:"), ch(28, "janeiro, fevereiro, março, abril, maio, junho, julho, agosto, setembro, outubro,"), ch(29, "novembro e dezembro.")]),
 ("en", [ch(30, "Rule one:"), ch(31, "days and months always start with a capital letter."), ch(32, "Monday."), ch(33, "March.")]),
 ("pt", [ch(34, "Regra um:"), ch(35, "dias e meses sempre começam com letra maiúscula.")]),
 ("en", [ch(36, "Rule two:"), ch(37, "watch the pronunciation."), ch(38, "Wednesday."), ch(39, "February.")]),
 ("pt", [ch(40, "Regra dois:"), ch(41, "cuidado com a pronúncia."), ch(42, "Em Wednesday, o D é mudo.")]),
 ("en", [ch(43, "Rule three:"), ch(44, "weekend is Saturday and Sunday.")]),
 ("pt", [ch(45, "Regra três:"), ch(46, "fim de semana, weekend,"), ch(47, "é sábado e domingo.")]),
 ("en", [ch(48, "Quiz time!"), ch(49, "Which one comes after Friday:"), ch(50, "Saturday, or Sunday?")]),
 ("en", [ch(51, "Saturday!")]),
 ("en", [ch(52, "Next one:"), ch(53, "which one comes after April:"), ch(54, "May, or June?")]),
 ("en", [ch(55, "May!")]),
 ("en", [(SP[56][0], 94.6, "Comment if you got it right,"), (94.7, SP[56][1], "follow and save to review!")]),
 ("en", [ch(57, "Follow Teacher Eliezio!")]),
]
# ids 101..112 = sorrindo, bravo, desconfiado, piscando, surpreso, sobrancelha, pensando-lado, piscando-2, bravo-livro, assustado, pensando-queixo, malicioso
EXPR = [(0, 101), (3.31, 103), (5.59, 110), (6.67, 108), (13.13, 101), (27.89, 101), (50.7, 106), (55.3, 101), (62.07, 102), (65.01, 101), (72.43, 106), (81.03, 104), (93.18, 104), (96.53, 101)]
THINK_LIST = [111, 107]
REVEAL_LIST = [105, 101]
WHOOSH = (3.2, 13.0, 27.8, 50.6, 62.0, 72.3, 80.9)
DIAS_EN = [wt(11, "Monday,", 0), wt(12, "Tuesday,", 0)] + [wt(13, "Wednesday, Thursday, Friday, Saturday, Sunday.", i) for i in range(5)]
DIAS_PT = [wt(15, "segunda, terça, quarta, quinta, sexta, sábado e domingo.", i) for i in (0, 1, 2, 3, 4, 5, 7)]
MES_EN = [wt(17, "January, February,", 0), wt(17, "January, February,", 1), SP[18][0], SP[19][0], SP[20][0], SP[21][0], SP[22][0], wt(23, "August, September,", 0), wt(23, "August, September,", 1), SP[24][0], SP[25][0], SP[26][0]]
MES_PT = [wt(28, "janeiro, fevereiro, março, abril, maio, junho, julho, agosto, setembro, outubro,", i) for i in range(10)] + [wt(29, "novembro e dezembro.", 0), wt(29, "novembro e dezembro.", 2)]
CLICKS = tuple(DIAS_EN) + tuple(MES_EN) + (SP[32][0], SP[33][0], SP[38][0], SP[39][0], wt(44, "weekend is Saturday and Sunday.", 2), wt(44, "weekend is Saturday and Sunday.", 4))
CTA_THUD = 93.18
TK = dict(hook=0, tit=1.77, car1=3.31, car2=wt(3, "Small letter, or capital letter?", 2), care=5.59,
          dia=13.13, mes=27.89, r1=50.7, r1h=51.86, r1a=55.3, r1b=56.27, r1p=58.31, r2=62.07, r2h=63.21, r2a=65.01, r2b=66.02, r2p=68.2, r2d=69.77,
          r3=72.43, r3h=73.61, r3a=wt(44, "weekend is Saturday and Sunday.", 2), r3b=wt(44, "weekend is Saturday and Sunday.", 4), r3p=77.29,
          quiz=81.03, q1=82.28, q2=87.56, cta=93.18, follow=96.53, save=wt(56, "Comment if you got it right, follow and save to review!", 6))
TK.update({f"d{i}": t for i, t in enumerate(DIAS_EN)}); TK.update({f"pd{i}": t for i, t in enumerate(DIAS_PT)})
TK.update({f"m{i}": t for i, t in enumerate(MES_EN)}); TK.update({f"pm{i}": t for i, t in enumerate(MES_PT)})
