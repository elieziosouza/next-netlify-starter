S="/tmp/claude-0/-home-user-next-netlify-starter/6cb4edb9-4741-58aa-b5a5-8666ade60fc3/scratchpad"
src=open(f"{S}/viagem2/pdf/aula2.html",encoding="utf8").read()
head=src[:src.index("<body>")+len("<body>")].replace("Aula 2 · No hotel","Aula 3 · No restaurante")
def card(e,en,pr,pt): return f'<div class="card"><div class="e">{e}</div><div><div class="en">{en}</div><span class="pron">{pr}</span><div class="pt">{pt}</div></div></div>'
def row(en,pr,pt): return f'<tr><td>{en}<br><span class="pron">{pr}</span></td><td>{pt}</td></tr>'
top='<div class="top"><span class="l">✈️ INGLÊS PARA VIAJAR · AULA 3</span><span class="r">No restaurante</span></div>'
def foot(n,extra=""): return f'<div class="foot"><span>Inglês para Viajar · Teacher Eliezio{extra}</span><span>{n}</span></div>'
def sec(n,h,s,mt=""): return f'<div class="sec"{mt}><div class="num">{n}</div><div><h2>{h}</h2><small>{s}</small></div></div>'
MT=' style="margin-top:6mm"'
cover='''<section class="page cover">
  <div class="grid"></div>
  <span class="tag">✈️ INGLÊS PARA VIAJAR · AULA 3 DE 7</span>
  <h1 class="disp" style="font-size:54pt">NO<br><span>RESTAURANTE</span></h1>
  <div class="sub">Mesa, cardápio e o seu pedido: o que dizer da porta até o prato chegar.</div>
  <div class="av"><img src="avatar.png" alt=""></div>
  <div class="emo">🍽️ 🍗 🥤</div>
  <div class="learn"><h3>NESTA AULA VOCÊ VAI APRENDER</h3><ul>
    <li>Pedir uma mesa e o cardápio</li><li>Fazer o seu pedido com educação</li>
    <li>Pedir a bebida</li><li>Perguntar o que o garçom recomenda</li>
    <li>Avisar alergia e restrições</li><li>10 frases extras de restaurante</li></ul></div>
  <div class="brand"><div><b>Teacher Eliezio</b><br>@teacher.eliezio</div><span class="pill">GUIA DE BOLSO · SALVE NO CELULAR</span></div>
</section>'''
p2=(f'<section class="page">{top}'
 + sec(1,"A MESA","Na entrada do restaurante")
 + '<div class="two">' + card("👥","A table for two, please.","â têi-bâl fór tu, plíz","Uma mesa para dois, por favor.") + card("📖","Can I see the menu?","kén ai sí dâ mé-niu","Posso ver o cardápio?") + '</div>'
 + sec(2,"O PEDIDO","Quando o garçom perguntar “Are you ready to order?”",MT)
 + card("🍗","I'd like the chicken, please.","áid laik dâ tchí-kin, plíz","Eu gostaria do frango, por favor.")
 + card("🥤","Can I get a Coke?","kén ai guét â kôuk","Pode me trazer uma Coca?")
 + card("👨‍🍳","What do you recommend?","uót du iú ré-kâ-ménd","O que você recomenda?")
 + sec(3,"RESTRIÇÕES","Alergias e o que você não come",MT)
 + '<div class="two">' + card("🥜","I'm allergic to peanuts.","áim â-lâr-djik tu pí-nâts","Eu tenho alergia a amendoim.") + card("🧅","No onions, please.","nou â-niânz, plíz","Sem cebola, por favor.") + '</div>'
 + '<div class="tip"><div class="i">💡</div><div><b class="t">DICA DE OURO</b><b>“I’d like…”</b> é o jeito mais educado de pedir. Funciona para comida, bebida e qualquer coisa.</div></div>'
 + foot(2) + '</section>')
more=[("Do you have a vegetarian option?","du iú rév â vé-djâ-té-riân óp-shân","Vocês têm opção vegetariana?"),("Is it spicy?","iz it spái-si","É apimentado?"),
("Can I have some water, please?","kén ai rév sâm uó-târ, plíz","Pode me trazer água, por favor?"),("Sparkling or still?","spár-kling ór stil","Com gás ou sem gás?"),
("Medium, please.","mí-diâm, plíz","Ao ponto, por favor. (carne)"),("Can I have it without cheese?","kén ai rév it uí-dáut tchíz","Pode vir sem queijo?"),
("Excuse me, this is not what I ordered.","eks-kiúz mi, dis iz nót uót ai ór-dârd","Com licença, não foi isso que eu pedi."),("Could we have more napkins?","kud uí rév mór nép-kinz","Pode trazer mais guardanapos?"),
("Is the tip included?","iz dâ tip in-klú-did","A gorjeta está incluída?"),("To go, please.","tu gôu, plíz","Para viagem, por favor.")]
voc=[("📖","menu","cardápio"),("🧑‍🍳","waiter / waitress","garçom / garçonete"),("🥗","starter","entrada"),("🍝","main course","prato principal"),
("🍰","dessert","sobremesa"),("🥤","drink","bebida"),("💧","still / sparkling water","água sem / com gás"),("🌶️","spicy","apimentado"),
("🥜","allergy","alergia"),("🍽️","fork / knife / spoon","garfo / faca / colher"),("🧻","napkin","guardanapo"),("🥡","to go","para viagem"),
("🧾","check / bill","conta"),("💵","tip","gorjeta"),("⭐","today's special","prato do dia")]
p3=f'<section class="page">{top}' + sec(4,"MAIS 10 FRASES ÚTEIS","Para pedir, ajustar e resolver problemas") + '<table class="more">' + "".join(row(*m) for m in more) + '</table>' + foot(3) + '</section>'
vocs="".join(f'<div><span class="e">{e}</span><p style="margin:0"><b>{a}</b><span>{b}</span></p></div>' for e,a,b in voc)
p4=(f'<section class="page">{top}' + sec(5,"VOCABULÁRIO","Palavras do cardápio e da mesa") + f'<div class="voc">{vocs}</div><div style="height:5mm"></div>'
 + sec(6,"SUA VEZ","Escreva o SEU pedido")
 + '''<div class="two">
    <div class="ex"><div class="q">How many people?</div><div class="ln"></div></div>
    <div class="ex"><div class="q">Are you ready to order?</div><div class="ln"></div></div>
    <div class="ex"><div class="q">Anything to drink?</div><div class="ln"></div></div>
    <div class="ex"><div class="q">Você tem alguma alergia? Escreva em inglês.</div><div class="ln"></div></div>
  </div>
  <div class="next"><div class="av2"><img src="avatar8.png" alt=""></div><div><b>PRÓXIMA AULA: PAGAR E GORJETA 💳</b>Pedir a conta, dividir e entender a gorjeta. Até lá, treine o seu pedido em voz alta!</div></div>'''
 + foot(4) + '</section>')
sim=[("r","Hi! Welcome. How many people?","Oi! Bem-vindo. Quantas pessoas?"),("v","A table for two, please.","Uma mesa para dois, por favor."),
("r","Follow me, please. Here is the menu. Are you ready to order?","Me acompanhe, por favor. Aqui está o cardápio. Já posso anotar o pedido?"),
("v","I'd like the chicken, please.","Eu gostaria do frango, por favor."),("r","Great choice! Anything to drink?","Ótima escolha! Algo para beber?"),
("v","Can I get a Coke?","Pode me trazer uma Coca?"),("r","Your food will be ready in 15 minutes.","Sua comida fica pronta em 15 minutos."),("v","Thank you!","Obrigado!")]
rows="".join(f'<div class="row {"o" if w=="r" else "y"}"><span class="who">{"WAITER" if w=="r" else "VOCÊ"}</span><div>{en}<small>{pt}</small></div></div>' for w,en,pt in sim)
p5=(f'<section class="page">{top}' + sec(7,"A SIMULAÇÃO COMPLETA","Leia em voz alta. Depois cubra a coluna “Você” e responda sozinho.") + f'<div class="dlg">{rows}</div>'
 + sec(8,"CHECKLIST DO RESTAURANTE","Marque o que você já treinou",MT)
 + '''<div class="check">
    <div><i></i>Sei pedir uma mesa</div><div><i></i>Sei pedir o cardápio</div>
    <div><i></i>Sei fazer o meu pedido</div><div><i></i>Sei pedir a bebida</div>
    <div><i></i>Sei pedir uma recomendação</div><div><i></i>Sei avisar uma alergia</div>
    <div><i></i>Li a simulação em voz alta</div><div><i></i>Salvei este guia no celular</div>
  </div>''' + foot(5," · @teacher.eliezio") + '</section>')
open(f"{S}/viagem3/pdf/aula3.html","w",encoding="utf8").write(head+"\n"+cover+"\n"+p2+"\n"+p3+"\n"+p4+"\n"+p5+"\n</body></html>")
