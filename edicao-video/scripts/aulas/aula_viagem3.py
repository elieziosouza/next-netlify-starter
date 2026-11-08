# Mini curso "Inglês para viajar", Aula 3: No restaurante, pedir (08/11/2026). Horizontal 1920x1080.
# Voz = professor + simulação inserida aos 47,80 s (20,75 s): garçom (Will) e as respostas do aluno na voz dele.
DIR = "viagem3"
D = 20.75
def s(t): return round(t + D, 2) if t >= 47.80 else t
PINS = [s(56.62)]
VO_END = s(69.36)
def c(a, b, tx): return (s(a), s(b), tx)
SIM = [(48.3, 50.8, "Hi! Welcome. How many people?"), (51.25, 52.95, "A table for two, please."), (53.4, 57.4, "Follow me, please. Here is the menu. Are you ready to order?"),
       (57.85, 59.6, "I'd like the chicken, please."), (60.05, 62.35, "Great choice! Anything to drink?"), (62.8, 64.05, "Can I get a Coke?"),
       (64.5, 66.9, "Your food will be ready in 15 minutes."), (67.35, 68.1, "Thank you!")]
CAP = [
 ("pt", [c(0.04, 2.35, "Você entrou no restaurante, com fome.")]),
 ("pt", [c(2.90, 6.46, "Hoje: como pedir mesa, cardápio e o seu prato.")]),
 ("pt", [c(6.99, 8.12, "Primeiro, a mesa.")]),
 ("en", [c(8.78, 10.17, "A table for two, please.")]), ("pt", [c(10.58, 12.08, "Uma mesa para dois, por favor.")]),
 ("en", [c(12.73, 13.67, "Can I see the menu?")]), ("pt", [c(14.10, 15.12, "Posso ver o cardápio?")]),
 ("pt", [c(15.71, 16.86, "Agora, o pedido.")]),
 ("en", [c(17.41, 18.81, "I'd like the chicken, please.")]), ("pt", [c(19.17, 20.69, "Eu gostaria do frango, por favor.")]),
 ("en", [c(21.37, 22.11, "Can I get a Coke?")]), ("pt", [c(22.66, 23.82, "Pode me trazer uma Coca?")]),
 ("en", [c(24.41, 25.33, "What do you recommend?")]), ("pt", [c(25.82, 26.85, "O que você recomenda?")]),
 ("pt", [c(27.32, 28.35, "Tem alguma restrição?")]),
 ("en", [c(28.96, 30.43, "I'm allergic to peanuts.")]), ("pt", [c(30.79, 32.36, "Eu tenho alergia a amendoim.")]),
 ("en", [c(32.86, 34.02, "No onions, please.")]), ("pt", [c(34.35, 35.53, "Sem cebola, por favor.")]),
 ("pt", [c(36.18, 43.24, "Dica de ouro: I'd like é o jeito mais educado de pedir. Funciona para comida, bebida e qualquer coisa.")]),
 ("pt", [c(43.75, 44.71, "Agora vamos treinar."), c(45.08, 47.54, "Escuta o garçom e repara nas respostas.")]),
] + [("en", [(a, b, tx)]) for a, b, tx in SIM] + [
 ("pt", [c(47.97, 48.48, "Quiz!"), c(48.97, 49.92, "O garçom pergunta:")]),
 ("en", [c(50.39, 51.36, "Are you ready to order?")]),
 ("pt", [c(51.89, 52.86, "O que você responde:"), c(53.26, 54.71, "A table for two, ou"), c(55.02, 56.35, "I'd like the chicken, please?")]),
 ("en", [c(56.89, 58.26, "I'd like the chicken, please!")]),
 ("pt", [c(58.82, 60.65, "A table for two é na entrada.")]),
 ("pt", [c(61.22, 63.92, "No PDF da aula tem mais frases de restaurante."), c(64.29, 67.58, "Nos vemos na próxima aula: pagar a conta e a gorjeta.")]),
 ("en", [c(68.07, 69.36, "Follow Teacher Eliezio!")]),
]
EXPR = [(0, 1), (6.99, 2), (8.78, 1), (27.32, 2), (28.96, 11), (32.86, 1), (36.18, 8), (37.2, 1), (47.8, 2), (s(47.97), 1), (s(67.9), 8), (s(68.9), 1)]
WHOOSH = (6.9, 15.6, 27.2, 36.1, 47.7, s(47.9), s(61.1))
CLICKS = (8.78, 12.73, 17.41, 21.37, 24.41, 28.96, 32.86)
CTA_THUD = s(68.0)
TK = dict(intro=0, goal=2.90, mesa=6.9, m1=8.78, m2=12.73, ped=15.6, p1=17.41, p2=21.37, p3=24.41, res=27.2, r1=28.96, r2=32.86,
          tip=36.1, train=43.75, sim=47.80, quiz=s(47.9), q1=s(50.39), qopt=s(53.26), after=s(58.82), pdf=s(61.1), cta=s(68.0), end=s(69.36))
