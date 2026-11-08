# Mini curso "Inglês para viajar", Aula 4: Pagar a conta e a gorjeta (08/11/2026). Horizontal 1920x1080.
# Voz = professor + simulação inserida aos 57,75 s (18,57 s): garçom (Will) e as respostas do aluno na voz dele.
DIR = "viagem4"
D = 18.57
def s(t): return round(t + D, 2) if t >= 57.75 else t
PINS = [s(64.63)]
VO_END = s(77.12)
def c(a, b, tx): return (s(a), s(b), tx)
SIM = [(58.25, 59.4, "How was everything?"), (59.85, 62.65, "It was great! Can I have the check, please?"), (63.1, 64.55, "Sure, here you go."),
       (65.0, 66.4, "Is the tip included?"), (66.85, 68.8, "No, it's not included."), (69.25, 70.7, "Can I pay by card?"),
       (71.15, 73.05, "Of course. Just tap here."), (73.5, 74.29, "Thank you!"), (74.74, 75.87, "Have a great night!")]
CAP = [
 ("pt", [c(0.10, 3.32, "A comida estava ótima. Agora é hora de pagar.")]),
 ("pt", [c(3.87, 7.83, "Hoje: pedir a conta, pagar e entender a gorjeta.")]),
 ("pt", [c(8.27, 9.32, "Para pedir a conta:")]),
 ("en", [c(9.72, 11.07, "Can I have the check, please?")]), ("pt", [c(11.42, 12.99, "Pode me trazer a conta, por favor?")]),
 ("pt", [c(13.39, 16.64, "Nos Estados Unidos é check. Na Inglaterra, bill.")]),
 ("pt", [c(17.08, 18.01, "Na hora de pagar:")]),
 ("en", [c(18.46, 19.56, "Can I pay by card?")]), ("pt", [c(19.99, 21.14, "Posso pagar com cartão?")]),
 ("en", [c(21.55, 22.61, "Can we split the bill?")]), ("pt", [c(22.97, 24.18, "Podemos dividir a conta?")]),
 ("pt", [c(24.60, 25.82, "E se vier algo errado:")]),
 ("en", [c(26.25, 27.47, "I think there's a mistake.")]), ("pt", [c(28.05, 28.98, "Acho que tem um erro.")]),
 ("pt", [c(29.41, 30.73, "Agora, a gorjeta.")]),
 ("en", [c(31.13, 32.22, "Is the tip included?")]), ("pt", [c(32.65, 33.88, "A gorjeta está incluída?")]),
 ("pt", [c(34.29, 40.81, "Nos Estados Unidos, a gorjeta normalmente não vem na conta, e o costume é deixar entre 15 e 20%.")]),
 ("en", [c(41.33, 42.08, "Keep the change.")]), ("pt", [c(42.46, 43.41, "Pode ficar com o troco.")]),
 ("pt", [c(43.94, 49.92, "Dica de ouro: antes de pagar, procure na conta as palavras service charge ou gratuity."), c(50.31, 53.20, "Se estiver escrito, a gorjeta já está incluída.")]),
 ("pt", [c(53.63, 54.64, "Agora vamos treinar."), c(55.01, 57.54, "Escuta o garçom e repara nas respostas.")]),
] + [("en", [(a, b, tx)]) for a, b, tx in SIM] + [
 ("pt", [c(57.88, 58.39, "Quiz!"), c(58.81, 60.29, "Você quer dividir a conta."), c(60.64, 61.45, "O que você fala:")]),
 ("pt", [c(61.86, 64.41, "Can we split the bill, ou Keep the change?")]),
 ("en", [c(64.86, 65.82, "Can we split the bill!")]),
 ("pt", [c(66.24, 68.26, "Keep the change é para deixar o troco.")]),
 ("pt", [c(68.80, 71.45, "No PDF da aula tem mais frases para pagar."), c(71.84, 75.33, "Nos vemos na próxima aula: na rua, pedindo direções.")]),
 ("en", [c(75.78, 77.12, "Follow Teacher Eliezio!")]),
]
EXPR = [(0, 1), (8.27, 2), (9.72, 1), (24.60, 11), (26.25, 2), (29.41, 1), (34.29, 7), (37.0, 1), (43.94, 8), (45.0, 1), (57.75, 2), (s(57.88), 1), (s(75.6), 8), (s(76.6), 1)]
WHOOSH = (8.15, 16.95, 29.3, 43.8, 57.65, s(57.8), s(68.7))
CLICKS = (9.72, 18.46, 21.55, 26.25, 31.13, 41.33)
CTA_THUD = s(75.7)
TK = dict(intro=0, goal=3.87, conta=8.15, c1=9.72, cb=13.39, pag=16.95, p1=18.46, p2=21.55, e1=26.25, gor=29.3, g1=31.13, gc=34.29, g2=41.33,
          tip=43.8, train=53.63, sim=57.75, quiz=s(57.8), q1=s(58.81), qopt=s(61.86), after=s(66.24), pdf=s(68.7), cta=s(75.7), end=s(77.12))
