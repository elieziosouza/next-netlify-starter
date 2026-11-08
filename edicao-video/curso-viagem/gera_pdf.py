"""PDF de bolso das aulas 5, 6 e 7 do curso Inglês para Viajar (08/11/2026), no mesmo design das aulas 1 a 4.
A Aula 7 ganha também o certificado de conclusão e o resumo com as 30 frases do curso.
Uso: python3 gera_pdf.py N  → grava $S/viagemN/pdf/aulaN.html (depois: node mkpdf.cjs aulaN.html saida.pdf)"""
import sys, shutil, os
S = "/tmp/claude-0/-home-user-next-netlify-starter/6cb4edb9-4741-58aa-b5a5-8666ade60fc3/scratchpad"
src = open(f"{S}/viagem2/pdf/aula2.html", encoding="utf8").read()
def card(e,en,pr,pt): return f'<div class="card"><div class="e">{e}</div><div><div class="en">{en}</div><span class="pron">{pr}</span><div class="pt">{pt}</div></div></div>'
def row(en,pr,pt): return f'<tr><td>{en}<br><span class="pron">{pr}</span></td><td>{pt}</td></tr>'
def sec(n,h,s,mt=""): return f'<div class="sec"{mt}><div class="num">{n}</div><div><h2>{h}</h2><small>{s}</small></div></div>'
MT = ' style="margin-top:6mm"'
D = {
 5: dict(nome="Na rua", h1="NA<br><span>RUA</span>", sub="Pedir e entender direções: como chegar onde você quer sem se perder.", emo="🗺️ 🧭 🚶",
   learn=["Chamar a atenção com educação","Perguntar como chegar","Entender esquerda, direita e em frente","Entender perto, ao lado e do outro lado","Pedir para repetir devagar","10 frases extras de direção"],
   blocos=[("PERGUNTAR","Comece sempre com “Excuse me”",[("🙋","Excuse me.","eks-kiúz mi","Com licença."),("🏛️","How do I get to the museum?","ráu du ai guét tu dâ miu-zí-âm","Como eu chego ao museu?"),("🚇","Where is the nearest subway station?","uér iz dâ ní-rest sâb-uêi stêi-shân","Onde fica a estação de metrô mais próxima?")]),
           ("ENTENDER A RESPOSTA","As palavras que você vai ouvir",[("⬅️","Turn left.","târn léft","Vire à esquerda."),("➡️","Turn right.","târn ráit","Vire à direita."),("⬆️","Go straight.","gôu strêit","Siga em frente."),("🏦","It's next to the bank.","its nékst tu dâ bénk","Fica ao lado do banco."),("↔️","It's across the street.","its â-krós dâ strít","Fica do outro lado da rua."),("🐢","Could you say that again, more slowly?","kud iú sêi dét â-guén, mór slôu-li","Pode repetir mais devagar?")])],
   dica="Pergunte também se é longe: <b>“Is it far?”</b> Uma resposta comum é <b>“It's a five-minute walk.”</b> (São cinco minutos a pé.)",
   more=[("Is it near here?","iz it nír rír","É perto daqui?"),("Can I walk there?","kén ai uók dér","Dá para ir a pé?"),("Can you show me on the map?","kén iú xôu mi ón dâ mép","Pode me mostrar no mapa?"),("Go past the church.","gôu pést dâ tchârtch","Passe a igreja."),("It's on the corner.","its ón dâ kór-nâr","Fica na esquina."),("At the traffic light, turn right.","ét dâ tré-fik láit, târn ráit","No semáforo, vire à direita."),("It's two blocks away.","its tu blóks â-uêi","Fica a duas quadras."),("I'm lost.","áim lóst","Estou perdido."),("Which way is north?","uítch uêi iz nórth","Para que lado é o norte?"),("Thank you, I'll find it.","thénk iú, ail fáind it","Obrigado, vou achar.")],
   voc=[("⬅️","left","esquerda"),("➡️","right","direita"),("⬆️","straight","em frente"),("🏙️","block","quadra"),("📐","corner","esquina"),("🚦","traffic light","semáforo"),("🛣️","street / avenue","rua / avenida"),("🗺️","map","mapa"),("📍","near / far","perto / longe"),("↔️","across","do outro lado"),("🧭","north / south","norte / sul"),("🚶","walk","caminhar"),("🌉","bridge","ponte"),("🏛️","museum","museu"),("🚇","subway station","estação de metrô")],
   ex=["Como pedir licença para perguntar?","Como perguntar como chegar ao hotel?","O que significa “Turn right”?","Como pedir para repetir devagar?"],
   sim_who="PASSERBY", sim=[("v","Excuse me! How do I get to the museum?","Com licença! Como eu chego ao museu?"),("r","Sure! Go straight for two blocks, then turn left.","Claro! Siga em frente duas quadras e vire à esquerda."),("v","Sorry, could you say that again, more slowly?","Desculpe, pode repetir mais devagar?"),("r","Of course. Go straight, two blocks. Then turn left. It's next to the bank.","Claro. Siga em frente, duas quadras. Depois vire à esquerda. Fica ao lado do banco."),("v","Is it far?","É longe?"),("r","No, it's a five-minute walk.","Não, são cinco minutos a pé."),("v","Thank you so much!","Muito obrigado!"),("r","You're welcome! Have a nice day!","De nada! Tenha um bom dia!")],
   check=["Sei pedir licença","Sei perguntar como chegar","Entendo left e right","Entendo go straight","Sei pedir para repetir","Sei perguntar se é longe","Li a simulação em voz alta","Salvei este guia no celular"],
   prox=("PRÓXIMA AULA: TRANSPORTE 🚕","Táxi, Uber e metrô. Até lá, treine pedir direções em voz alta!")),
 6: dict(nome="Transporte", h1="TRANS-<br><span>PORTE</span>", sub="Táxi, Uber e metrô: como se locomover pela cidade sem medo de errar.", emo="🚕 🚗 🚇",
   learn=["Dar o endereço ao motorista","Perguntar quanto tempo leva","Pedir para parar","Comprar o bilhete do metrô","Achar a linha e o trem certos","Conferir o Uber com segurança"],
   blocos=[("TÁXI OU UBER","Com o motorista",[("📍","Can you take me to this address?","kén iú têik mi tu dis â-drés","Pode me levar para este endereço?"),("⏱️","How long will it take?","ráu lóng uil it têik","Quanto tempo vai levar?"),("✋","Can you stop here, please?","kén iú stóp rír, plíz","Pode parar aqui, por favor?")]),
           ("NO METRÔ","Bilhete, linha e trem",[("🎫","Where can I buy a ticket?","uér kén ai bái â tí-kit","Onde eu compro o bilhete?"),("🏙️","Which line goes downtown?","uítch láin gôuz dáun-táun","Qual linha vai para o centro?"),("🚆","Is this the right train?","iz dis dâ ráit trêin","Este é o trem certo?")])],
   dica="Antes de entrar no Uber, confira a <b>placa</b> no aplicativo e pergunte: <b>“Who are you picking up?”</b> (Quem você veio buscar?). Se o motorista disser o seu nome, é o carro certo.",
   more=[("Can you open the trunk?","kén iú ôu-pân dâ trânk","Pode abrir o porta-malas?"),("How much is it to the airport?","ráu mâtch iz it tu di ér-pórt","Quanto custa até o aeroporto?"),("Can you turn on the AC?","kén iú târn ón di êi-sí","Pode ligar o ar-condicionado?"),("I'm in a hurry.","áim in â râ-ri","Estou com pressa."),("Keep the change.","kíp dâ tchêindj","Pode ficar com o troco."),("A one-way ticket, please.","â uân-uêi tí-kit, plíz","Um bilhete só de ida, por favor."),("A round-trip ticket, please.","â ráund-trip tí-kit, plíz","Um bilhete de ida e volta, por favor."),("Where do I change trains?","uér du ai tchêindj trêinz","Onde eu troco de trem?"),("Which stop is it?","uítch stóp iz it","Qual é a parada?"),("Does this bus go to the beach?","dâz dis bâs gôu tu dâ bítch","Este ônibus vai para a praia?")],
   voc=[("🚕","taxi / cab","táxi"),("🚗","ride","corrida"),("🧑‍✈️","driver","motorista"),("📍","address","endereço"),("🧳","trunk","porta-malas"),("🚇","subway","metrô"),("🎫","ticket","bilhete"),("💳","card / pass","cartão de transporte"),("🔀","line","linha"),("🚏","stop","parada"),("🔁","transfer","baldeação"),("🏙️","downtown","centro"),("➡️","one-way","só ida"),("🔄","round-trip","ida e volta"),("🚌","bus","ônibus")],
   ex=["Como dar o endereço ao motorista?","Como pedir para parar aqui?","Como perguntar onde comprar o bilhete?","Como conferir se é o seu Uber?"],
   sim_who="DRIVER", sim=[("r","Hi there!","Oi!"),("v","Hi! Who are you picking up?","Oi! Quem você veio buscar?"),("r","Silva, to Central Park.","Silva, para o Central Park."),("v","That's me! How long will it take?","Sou eu! Quanto tempo vai levar?"),("r","About twenty minutes with this traffic.","Uns vinte minutos com esse trânsito."),("v","Can you stop here, please?","Pode parar aqui, por favor?"),("r","Sure. Here we are.","Claro. Chegamos."),("v","Thank you!","Obrigado!"),("r","Have a good one!","Tenha um bom dia!")],
   check=["Sei dar o endereço","Sei perguntar o tempo","Sei pedir para parar","Sei comprar o bilhete","Sei perguntar a linha","Sei conferir o Uber","Li a simulação em voz alta","Salvei este guia no celular"],
   prox=("ÚLTIMA AULA: COMPRAS E EMERGÊNCIAS 🛍️","Preço, tamanho e as frases para pedir ajuda. Até lá, treine as frases do Uber!")),
 7: dict(nome="Compras e emergências", h1="COMPRAS E<br><span>EMERGÊNCIAS</span>", sub="Comprar com tranquilidade e saber pedir ajuda se algo der errado.", emo="🛍️ 🏷️ 🚑",
   learn=["Perguntar o preço","Pedir outro tamanho","Experimentar e comprar","Pedir ajuda","Falar com médico e polícia","911 e o consulado"],
   blocos=[("COMPRAS","Na loja",[("🏷️","How much is this?","ráu mâtch iz dis","Quanto custa isso?"),("📏","Do you have this in a smaller size?","du iú rév dis in â smó-lâr sáiz","Tem esse num tamanho menor?"),("👕","Can I try it on?","kén ai trái it ón","Posso experimentar?"),("🛒","I'll take it.","ail têik it","Vou levar.")]),
           ("EMERGÊNCIAS","Espero que você nunca precise",[("🆘","I need help!","ai níd rélp","Eu preciso de ajuda!"),("🛂","I lost my passport.","ai lóst mai péss-port","Eu perdi meu passaporte."),("🩺","I need a doctor.","ai níd â dók-târ","Eu preciso de um médico."),("🚓","Call the police!","kól dâ pâ-lís","Chame a polícia!"),("💊","Where is the nearest pharmacy?","uér iz dâ ní-rest fár-mâ-si","Onde fica a farmácia mais próxima?")])],
   dica="Nos EUA, o número de emergência é <b>911</b>. Antes de viajar, anote o telefone do <b>consulado brasileiro</b> da cidade e guarde uma foto do passaporte no celular.",
   more=[("Do you have this in another color?","du iú rév dis in â-nâ-dâr kâ-lâr","Tem em outra cor?"),("Is this on sale?","iz dis ón sêil","Está em promoção?"),("Where is the fitting room?","uér iz dâ fí-ting rum","Onde fica o provador?"),("Can I return it?","kén ai ri-târn it","Posso devolver?"),("I'm just looking, thanks.","áim djâst lú-king, thénks","Só estou olhando, obrigado."),("Someone stole my wallet.","sâm-uân stôul mai uó-lit","Roubaram minha carteira."),("I don't feel well.","ai dôunt fíl uél","Não estou me sentindo bem."),("I'm allergic to penicillin.","áim â-lâr-djik tu pé-ni-sí-lin","Sou alérgico à penicilina."),("Where is the hospital?","uér iz dâ rós-pi-tâl","Onde fica o hospital?"),("I need to call the Brazilian consulate.","ai níd tu kól dâ brâ-zí-liân kón-sâ-lât","Preciso ligar para o consulado brasileiro.")],
   voc=[("🏷️","price","preço"),("📏","size (S, M, L)","tamanho (P, M, G)"),("👕","fitting room","provador"),("🔥","sale","promoção"),("🧾","receipt","recibo"),("↩️","return","devolução"),("💵","cash","dinheiro"),("🆘","help","ajuda"),("🚓","police","polícia"),("🩺","doctor","médico"),("🏥","hospital","hospital"),("💊","pharmacy","farmácia"),("🛂","passport","passaporte"),("👛","wallet","carteira"),("🇧🇷","consulate","consulado")],
   ex=["Como perguntar o preço?","Como pedir um tamanho maior? (bigger)","Como dizer que perdeu o passaporte?","Qual o número de emergência nos EUA?"],
   sim_who="SHOP", sim=[("r","Hi! Can I help you?","Oi! Posso ajudar?"),("v","Hi! Do you have this in a smaller size?","Oi! Tem esse num tamanho menor?"),("r","Sure, here's a medium.","Claro, aqui está um médio."),("v","Can I try it on?","Posso experimentar?"),("r","Of course. The fitting room is over there.","Claro. O provador é ali."),("v","How much is this?","Quanto custa?"),("r","It's $29.99.","Custa 29,99 dólares."),("v","I'll take it.","Vou levar."),("r","Great! Cash or card?","Ótimo! Dinheiro ou cartão?"),("v","Card, please.","Cartão, por favor."),("r","Here's your receipt. Have a nice day!","Aqui está o recibo. Tenha um bom dia!")],
   check=["Sei perguntar o preço","Sei pedir outro tamanho","Sei pedir para experimentar","Sei pedir ajuda","Sei falar com um médico","Sei o número 911","Li a simulação em voz alta","Salvei este guia no celular"],
   prox=None),
}
RESUMO = [("Aeroporto","I'd like to check in."),("Aeroporto","Here is my passport."),("Aeroporto","Window or aisle? — Window, please."),("Imigração","Tourism. I'm here on vacation."),("Imigração","Ten days."),("Imigração","At a hotel downtown."),("Imigração","No, nothing."),
  ("Hotel","I have a reservation under the name…"),("Hotel","What time is breakfast?"),("Hotel","What's the Wi-Fi password?"),("Hotel","Could I have an extra towel, please?"),("Hotel","I'd like to check out."),
  ("Restaurante","A table for two, please."),("Restaurante","Can I see the menu?"),("Restaurante","I'd like the chicken, please."),("Restaurante","I'm allergic to peanuts."),
  ("Conta","Can I have the check, please?"),("Conta","Can I pay by card?"),("Conta","Can we split the bill?"),("Conta","Is the tip included?"),
  ("Rua","Excuse me. How do I get to…?"),("Rua","Turn left / Turn right / Go straight."),("Rua","Could you say that again, more slowly?"),
  ("Transporte","Can you take me to this address?"),("Transporte","Can you stop here, please?"),("Transporte","Where can I buy a ticket?"),
  ("Compras","How much is this?"),("Compras","Can I try it on?"),("Emergência","I need help! / I need a doctor."),("Emergência","I lost my passport.")]
def main(n):
    d = D[n]; head = src[:src.index("<body>")+len("<body>")].replace("Aula 2 · No hotel", f"Aula {n} · {d['nome']}")
    top = f'<div class="top"><span class="l">✈️ INGLÊS PARA VIAJAR · AULA {n}</span><span class="r">{d["nome"]}</span></div>'
    foot = lambda k, extra="": f'<div class="foot"><span>Inglês para Viajar · Teacher Eliezio{extra}</span><span>{k}</span></div>'
    fs = "56pt" if len(d["h1"]) < 40 else "44pt"
    li = "".join(f"<li>{x}</li>" for x in d["learn"])
    cover = f'''<section class="page cover"><div class="grid"></div>
  <span class="tag">✈️ INGLÊS PARA VIAJAR · AULA {n} DE 7</span>
  <h1 class="disp" style="font-size:{fs}">{d["h1"]}</h1><div class="sub">{d["sub"]}</div>
  <div class="av"><img src="avatar.png" alt=""></div><div class="emo">{d["emo"]}</div>
  <div class="learn"><h3>NESTA AULA VOCÊ VAI APRENDER</h3><ul>{li}</ul></div>
  <div class="brand"><div><b>Teacher Eliezio</b><br>@teacher.eliezio</div><span class="pill">GUIA DE BOLSO · SALVE NO CELULAR</span></div></section>'''
    p2 = f'<section class="page">{top}'
    for i, (h, s, its) in enumerate(d["blocos"]):
        p2 += sec(i+1, h, s, MT if i else "")
        p2 += '<div class="two">' + "".join(card(*x) for x in its) + '</div>'
    p2 += f'<div class="tip"><div class="i">💡</div><div><b class="t">DICA DE OURO</b>{d["dica"]}</div></div>' + foot(2) + '</section>'
    nb = len(d["blocos"])
    p3 = f'<section class="page">{top}' + sec(nb+1, "MAIS 10 FRASES ÚTEIS", "Para ir além do vídeo") + '<table class="more">' + "".join(row(*m) for m in d["more"]) + '</table>' + foot(3) + '</section>'
    vocs = "".join(f'<div><span class="e">{e}</span><p style="margin:0"><b>{a}</b><span>{b}</span></p></div>' for e, a, b in d["voc"])
    exs = "".join(f'<div class="ex"><div class="q">{q}</div><div class="ln"></div></div>' for q in d["ex"])
    prox = f'<div class="next"><div class="av2"><img src="avatar8.png" alt=""></div><div><b>{d["prox"][0]}</b>{d["prox"][1]}</div></div>' if d["prox"] else \
           '<div class="next"><div class="av2"><img src="avatar8.png" alt=""></div><div><b>PARABÉNS! VOCÊ TERMINOU 🎓</b>Nas próximas páginas: o resumo com as 30 frases do curso e o seu certificado.</div></div>'
    p4 = f'<section class="page">{top}' + sec(nb+2, "VOCABULÁRIO", "Palavras que você vai ouvir e ver") + f'<div class="voc">{vocs}</div><div style="height:5mm"></div>' + sec(nb+3, "SUA VEZ", "Escreva a sua resposta") + f'<div class="two">{exs}</div>' + prox + foot(4) + '</section>'
    rows = "".join(f'<div class="row {"o" if w=="r" else "y"}"><span class="who">{d["sim_who"] if w=="r" else "VOCÊ"}</span><div>{en}<small>{pt}</small></div></div>' for w, en, pt in d["sim"])
    chk = "".join(f"<div><i></i>{c}</div>" for c in d["check"])
    p5 = f'<section class="page">{top}' + sec(nb+4, "A SIMULAÇÃO COMPLETA", "Leia em voz alta. Depois cubra a coluna “Você” e responda sozinho.") + f'<div class="dlg">{rows}</div>' + sec(nb+5, "CHECKLIST", "Marque o que você já treinou", MT) + f'<div class="check">{chk}</div>' + foot(5, " · @teacher.eliezio") + '</section>'
    extra = ""
    if n == 7:
        rs = "".join(f'<div style="background:#f4f6fb;border-radius:3mm;padding:1.7mm 3.5mm"><div style="color:#2f6fd6;font-weight:900;font-size:7.5pt;letter-spacing:.1em">{a.upper()}</div><div style="font-weight:800;font-size:10pt;margin-top:.6mm">{b}</div></div>' for a, b in RESUMO)
        extra += f'<section class="page">{top}' + sec("★", "RESUMO DO CURSO", "As 30 frases que mais salvam numa viagem") + f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:1.8mm">{rs}</div>' + foot(6) + '</section>'
        extra += '''<section class="page" style="padding:14mm">
  <div style="position:absolute;inset:10mm;border:3mm solid #0a1a38;border-radius:6mm"></div>
  <div style="position:absolute;inset:15mm;border:1mm solid #ffd640;border-radius:4mm"></div>
  <div style="position:relative;text-align:center;padding-top:30mm;display:grid;gap:7mm;justify-items:center">
    <div style="font-weight:900;letter-spacing:.3em;color:#2f6fd6;font-size:11pt">✈️ INGLÊS PARA VIAJAR</div>
    <div class="disp" style="font-size:48pt;color:#0a1a38;line-height:1">CERTIFICADO<br><span style="color:#d6a800">DE CONCLUSÃO</span></div>
    <div style="font-size:12pt;color:#5d6886;font-weight:600">Certificamos que</div>
    <div style="width:140mm;border-bottom:1.5px solid #0a1a38;height:14mm"></div>
    <div style="font-size:9pt;color:#5d6886">(escreva o seu nome)</div>
    <div style="max-width:140mm;font-size:12pt;line-height:1.55">concluiu o mini curso <b>Inglês para Viajar com o Teacher Eliezio</b>, com 7 aulas: aeroporto, hotel, restaurante, conta e gorjeta, direções, transporte, compras e emergências.</div>
    <div style="width:46mm;height:46mm;border-radius:50%;background:#ffd640;position:relative;margin-top:4mm"><img src="avatar.png" alt="" style="position:absolute;left:3mm;top:3mm;width:40mm;height:40mm"></div>
    <div style="font-family:Anton;font-size:20pt;color:#0a1a38">Teacher Eliezio</div>
    <div style="font-size:10pt;color:#5d6886;font-weight:700">@teacher.eliezio · Boa viagem! 🌎</div>
    <div style="display:flex;gap:30mm;margin-top:6mm;font-size:9pt;color:#5d6886"><div><div style="width:50mm;border-bottom:1px solid #9aa3b8;height:8mm"></div>Data</div><div><div style="width:50mm;border-bottom:1px solid #9aa3b8;height:8mm"></div>Assinatura</div></div>
  </div></section>'''
    os.makedirs(f"{S}/viagem{n}/pdf", exist_ok=True)
    for f in os.listdir(f"{S}/viagem1/pdf"):
        if f.endswith((".ttf", ".png")): shutil.copy(f"{S}/viagem1/pdf/{f}", f"{S}/viagem{n}/pdf/{f}")
    open(f"{S}/viagem{n}/pdf/aula{n}.html", "w", encoding="utf8").write(head + "\n" + cover + p2 + p3 + p4 + p5 + extra + "\n</body></html>")
    print("ok", n)
if __name__ == "__main__":
    for a in sys.argv[1:]: main(int(a))
