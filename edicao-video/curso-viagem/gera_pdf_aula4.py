S="/tmp/claude-0/-home-user-next-netlify-starter/6cb4edb9-4741-58aa-b5a5-8666ade60fc3/scratchpad"
src=open(f"{S}/viagem2/pdf/aula2.html",encoding="utf8").read()
head=src[:src.index("<body>")+len("<body>")].replace("Aula 2 · No hotel","Aula 4 · A conta e a gorjeta")
def card(e,en,pr,pt): return f'<div class="card"><div class="e">{e}</div><div><div class="en">{en}</div><span class="pron">{pr}</span><div class="pt">{pt}</div></div></div>'
def row(en,pr,pt): return f'<tr><td>{en}<br><span class="pron">{pr}</span></td><td>{pt}</td></tr>'
top='<div class="top"><span class="l">✈️ INGLÊS PARA VIAJAR · AULA 4</span><span class="r">A conta e a gorjeta</span></div>'
def foot(n,extra=""): return f'<div class="foot"><span>Inglês para Viajar · Teacher Eliezio{extra}</span><span>{n}</span></div>'
def sec(n,h,s,mt=""): return f'<div class="sec"{mt}><div class="num">{n}</div><div><h2>{h}</h2><small>{s}</small></div></div>'
MT=' style="margin-top:6mm"'
cover='''<section class="page cover">
  <div class="grid"></div>
  <span class="tag">✈️ INGLÊS PARA VIAJAR · AULA 4 DE 7</span>
  <h1 class="disp" style="font-size:56pt">A CONTA<br><span>E A GORJETA</span></h1>
  <div class="sub">Pedir a conta, pagar, dividir e entender a gorjeta sem passar aperto.</div>
  <div class="av"><img src="avatar.png" alt=""></div>
  <div class="emo">🧾 💳 💵</div>
  <div class="learn"><h3>NESTA AULA VOCÊ VAI APRENDER</h3><ul>
    <li>Pedir a conta (check e bill)</li><li>Pagar com cartão</li>
    <li>Dividir a conta</li><li>Avisar um erro na conta</li>
    <li>Entender a gorjeta nos EUA</li><li>10 frases extras para pagar</li></ul></div>
  <div class="brand"><div><b>Teacher Eliezio</b><br>@teacher.eliezio</div><span class="pill">GUIA DE BOLSO · SALVE NO CELULAR</span></div>
</section>'''
p2=(f'<section class="page">{top}'
 + sec(1,"A CONTA","Nos EUA é check · na Inglaterra é bill")
 + card("🙋","Can I have the check, please?","kén ai rév dâ tchék, plíz","Pode me trazer a conta, por favor?")
 + sec(2,"NA HORA DE PAGAR","Cartão, divisão e erros",MT)
 + '<div class="two">' + card("💳","Can I pay by card?","kén ai pêi bai kárd","Posso pagar com cartão?") + card("➗","Can we split the bill?","kén uí split dâ bil","Podemos dividir a conta?") + '</div>'
 + card("❗","I think there's a mistake.","ai think dérz â mis-têik","Acho que tem um erro.")
 + sec(3,"A GORJETA","Tip, service charge e gratuity",MT)
 + '<div class="two">' + card("❓","Is the tip included?","iz dâ tip in-klú-did","A gorjeta está incluída?") + card("🪙","Keep the change.","kíp dâ tchêindj","Pode ficar com o troco.") + '</div>'
 + '<div class="tip"><div class="i">💡</div><div><b class="t">DICA DE OURO</b>Nos EUA, a gorjeta normalmente não vem na conta e o costume é deixar entre <b>15% e 20%</b>. Antes de pagar, procure <b>“service charge”</b> ou <b>“gratuity”</b>: se estiver escrito, ela já está incluída.</div></div>'
 + foot(2) + '</section>')
more=[("Can I pay in cash?","kén ai pêi in késh","Posso pagar em dinheiro?"),("Do you take credit cards?","du iú têik kré-dit kárdz","Vocês aceitam cartão de crédito?"),
("Can I have the receipt, please?","kén ai rév dâ ri-sít, plíz","Pode me dar o recibo, por favor?"),("We'd like separate checks.","uíd laik sé-pâ-rât tchéks","Queremos contas separadas."),
("I'll get this one.","ail guét dis uân","Essa é por minha conta."),("We didn't order this.","uí dí-dânt ór-dâr dis","Nós não pedimos isso."),
("How much do I owe you?","ráu mâtch du ai ôu iú","Quanto eu te devo?"),("Can I add the tip on the card?","kén ai éd dâ tip ón dâ kárd","Posso colocar a gorjeta no cartão?"),
("The card didn't go through.","dâ kárd dí-dânt gôu thru","O cartão não passou."),("Thank you, everything was delicious!","thénk iú, év-ri-thing uóz di-lí-shâs","Obrigado, estava tudo delicioso!")]
voc=[("🧾","check / bill","conta"),("💵","tip","gorjeta"),("🧮","service charge","taxa de serviço"),("🙏","gratuity","gorjeta (na conta)"),
("💳","credit card","cartão de crédito"),("💴","cash","dinheiro"),("🪙","change","troco"),("📄","receipt","recibo"),
("➗","split","dividir"),("🔢","total","total"),("🏷️","tax","imposto"),("📲","tap","aproximar o cartão"),
("❗","mistake","erro"),("👥","separate checks","contas separadas"),("💯","percent","por cento")]
p3=f'<section class="page">{top}' + sec(4,"MAIS 10 FRASES ÚTEIS","Para pagar, dividir e resolver problemas") + '<table class="more">' + "".join(row(*m) for m in more) + '</table>' + foot(3) + '</section>'
vocs="".join(f'<div><span class="e">{e}</span><p style="margin:0"><b>{a}</b><span>{b}</span></p></div>' for e,a,b in voc)
p4=(f'<section class="page">{top}' + sec(5,"VOCABULÁRIO","Palavras da conta e do pagamento") + f'<div class="voc">{vocs}</div><div style="height:5mm"></div>'
 + sec(6,"SUA VEZ","Escreva o que você diria")
 + '''<div class="two">
    <div class="ex"><div class="q">Como pedir a conta?</div><div class="ln"></div></div>
    <div class="ex"><div class="q">Como perguntar se pode pagar com cartão?</div><div class="ln"></div></div>
    <div class="ex"><div class="q">Como pedir para dividir a conta?</div><div class="ln"></div></div>
    <div class="ex"><div class="q">Conta de US$ 40: quanto de gorjeta (15% a 20%)?</div><div class="ln"></div></div>
  </div>
  <div class="next"><div class="av2"><img src="avatar8.png" alt=""></div><div><b>PRÓXIMA AULA: NA RUA 🗺️</b>Pedir e entender direções sem se perder. Até lá, treine pedir a conta em voz alta!</div></div>'''
 + foot(4) + '</section>')
sim=[("r","How was everything?","Estava tudo bem?"),("v","It was great! Can I have the check, please?","Estava ótimo! Pode me trazer a conta, por favor?"),
("r","Sure, here you go.","Claro, aqui está."),("v","Is the tip included?","A gorjeta está incluída?"),("r","No, it's not included.","Não, não está incluída."),
("v","Can I pay by card?","Posso pagar com cartão?"),("r","Of course. Just tap here.","Claro. É só aproximar aqui."),("v","Thank you!","Obrigado!"),("r","Have a great night!","Tenha uma ótima noite!")]
rows="".join(f'<div class="row {"o" if w=="r" else "y"}"><span class="who">{"WAITER" if w=="r" else "VOCÊ"}</span><div>{en}<small>{pt}</small></div></div>' for w,en,pt in sim)
p5=(f'<section class="page">{top}' + sec(7,"A SIMULAÇÃO COMPLETA","Leia em voz alta. Depois cubra a coluna “Você” e responda sozinho.") + f'<div class="dlg">{rows}</div>'
 + sec(8,"CHECKLIST DA CONTA","Marque o que você já treinou",MT)
 + '''<div class="check">
    <div><i></i>Sei pedir a conta</div><div><i></i>Sei a diferença check / bill</div>
    <div><i></i>Sei pagar com cartão</div><div><i></i>Sei dividir a conta</div>
    <div><i></i>Sei avisar um erro</div><div><i></i>Sei calcular a gorjeta</div>
    <div><i></i>Li a simulação em voz alta</div><div><i></i>Salvei este guia no celular</div>
  </div>''' + foot(5," · @teacher.eliezio") + '</section>')
open(f"{S}/viagem4/pdf/aula4.html","w",encoding="utf8").write(head+"\n"+cover+"\n"+p2+"\n"+p3+"\n"+p4+"\n"+p5+"\n</body></html>")
