# Mini curso "Inglês para viajar", Aula 2: No hotel (08/11/2026). Horizontal 1920x1080.
# Voz = professor + simulação inserida aos 56,90 s (23,90 s): recepcionista (Jessica) e as respostas do aluno na voz dele.
# Uso: python3 prep_aula.py $S aulas/aula_viagem2.py
DIR = "viagem2"
D = 23.90
def s(t): return round(t + D, 2) if t >= 56.90 else t
PINS = [s(67.48)]
VO_END = s(77.51)
def c(a, b, tx): return (s(a), s(b), tx)
SIM = [(57.4, 60.25, "Good evening! Welcome to the Grand Hotel."), (60.7, 62.35, "May I have your name, please?"), (62.8, 65.9, "Hi! I have a reservation under the name Silva."),
       (66.35, 67.9, "May I see your passport?"), (68.35, 69.75, "Here is my passport."), (70.2, 73.0, "Here is your key. You're in room 512."),
       (73.45, 74.9, "What time is breakfast?"), (75.35, 77.5, "Breakfast is from seven to ten."), (77.95, 78.75, "Thank you!"), (79.2, 80.35, "Enjoy your stay!")]
CAP = [
 ("pt", [c(0.05, 2.75, "Você chegou no hotel, cansado da viagem.")]),
 ("pt", [c(3.22, 8.34, "Hoje: as frases para o check-in, para pedir coisas no quarto e para o check-out.")]),
 ("pt", [c(8.97, 10.22, "Primeiro, o check-in.")]),
 ("en", [c(10.63, 13.00, "I have a reservation under the name Silva.")]), ("pt", [c(13.44, 15.41, "Eu tenho uma reserva no nome Silva.")]),
 ("en", [c(15.87, 16.89, "Here is my passport.")]), ("pt", [c(17.41, 18.79, "Aqui está meu passaporte.")]),
 ("en", [c(19.24, 20.40, "What time is breakfast?")]), ("pt", [c(20.86, 22.02, "Que horas é o café da manhã?")]),
 ("pt", [c(22.43, 23.47, "E a senha do Wi-Fi:")]),
 ("en", [c(23.87, 25.33, "What's the Wi-Fi password?")]), ("pt", [c(25.77, 26.88, "Qual a senha do Wi-Fi?")]),
 ("pt", [c(27.36, 28.37, "Agora, no quarto.")]),
 ("en", [c(28.97, 30.72, "Could I have an extra towel, please?")]), ("pt", [c(31.00, 32.36, "Pode me dar mais uma toalha?")]),
 ("en", [c(32.74, 34.50, "The air conditioning isn't working.")]), ("pt", [c(34.85, 36.86, "O ar-condicionado não está funcionando.")]),
 ("pt", [c(37.32, 37.94, "Na saída:")]),
 ("en", [c(38.34, 39.52, "I'd like to check out.")]), ("pt", [c(39.85, 41.44, "Eu gostaria de fazer o check-out.")]),
 ("en", [c(41.82, 43.16, "Can I leave my bags here?")]), ("pt", [c(43.49, 44.92, "Posso deixar minhas malas aqui?")]),
 ("pt", [c(45.33, 52.17, "Dica de ouro: comece os pedidos com Could I ou Can I. É educado e funciona em qualquer lugar.")]),
 ("pt", [c(52.59, 53.55, "Agora vamos treinar."), c(53.94, 56.56, "Escuta a recepcionista e repara nas respostas.")]),
] + [("en", [(a, b, tx)]) for a, b, tx in SIM] + [
 ("pt", [c(57.20, 57.71, "Quiz!"), c(58.12, 59.44, "A recepcionista pergunta:")]),
 ("en", [c(59.86, 61.30, "May I have your name, please?")]),
 ("pt", [c(61.66, 62.68, "O que você responde:"), c(63.10, 64.67, "I'd like to check out, ou"), c(65.03, 67.24, "I have a reservation under the name Silva?")]),
 ("en", [c(67.73, 70.09, "I have a reservation under the name Silva!")]),
 ("pt", [c(70.56, 73.02, "No PDF da aula tem mais frases de hotel."), c(73.36, 75.74, "Nos vemos na próxima aula, no restaurante.")]),
 ("en", [c(76.20, 77.51, "Follow Teacher Eliezio!")]),
]
EXPR = [(0, 2), (3.22, 1), (27.36, 7), (28.97, 1), (32.74, 11), (34.85, 1), (45.33, 8), (46.3, 1), (56.9, 2), (s(57.2), 1), (s(76.0), 8), (s(77.0), 1)]
WHOOSH = (8.85, 27.25, 37.2, 45.2, 56.8, s(57.1), s(70.4))
CLICKS = (10.63, 15.87, 19.24, 23.87, 28.97, 32.74, 38.34, 41.82)
CTA_THUD = s(76.1)
TK = dict(intro=0, goal=3.22, ci=8.85, c1=10.63, c2=15.87, c3=19.24, c4=22.43, room=27.25, r1=28.97, r2=32.74, out=37.2, o1=38.34, o2=41.82,
          tip=45.2, train=52.59, sim=56.90, quiz=s(57.1), q1=s(59.86), qopt=s(63.10), after=s(70.56), pdf=s(70.4), cta=s(76.1), end=s(77.51))
