"""Gera, a partir de uma especificação, tudo o que uma aula do curso Inglês para Viajar precisa antes do render (08/11/2026):
trilha de voz com a simulação a duas vozes (vo_raw.mp3), config do prep_aula (aulas/aula_viagemN.py) e a composição Remotion (ViagemN.tsx).
Uso: python3 gera_aula.py N   (as especificações das aulas 5, 6 e 7 estão em SPECS)."""
import sys, json, subprocess
import numpy as np
S = "/tmp/claude-0/-home-user-next-netlify-starter/6cb4edb9-4741-58aa-b5a5-8666ade60fc3/scratchpad"
REPO = "/home/user/next-netlify-starter/edicao-video"
SR = 48000
SPECS = {
 5: dict(dir="viagem5", titulo="NA RUA", sub="Pedir e entender direções", emo=["🗺️", "🧭", "🚶"], cut=55.60, pin=62.03, vo_end=74.72, resp_nome="PASSERBY", resp_emo="👩",
   sim_pill="SIMULAÇÃO · NA RUA 🗺️", sim_files=("rua.mp3", "voce.mp3"),
   sim=[("v",0.0,2.55,"Excuse me! How do I get to the museum?"),("r",0.0,3.35,"Sure! Go straight for two blocks, then turn left."),("v",2.70,5.45,"Sorry, could you say that again, more slowly?"),
        ("r",3.45,8.65,"Of course. Go straight, two blocks. Then turn left. It's next to the bank."),("v",5.55,6.55,"Is it far?"),("r",8.75,10.75,"No, it's a five-minute walk."),
        ("v",6.70,8.16,"Thank you so much!"),("r",10.90,12.96,"You're welcome! Have a nice day!")],
   caps=[("pt",[(0.05,2.66,"Você saiu do hotel e quer chegar a um lugar.")]),("pt",[(3.17,6.47,"Hoje: como pedir e entender direções.")]),("pt",[(6.91,9.69,"Para começar, chame a atenção com educação:")]),
     ("en",[(10.09,10.78,"Excuse me.")]),("pt",[(11.21,11.90,"Com licença.")]),("pt",[(12.30,13.28,"Depois pergunte:")]),
     ("en",[(13.67,15.12,"How do I get to the museum?")]),("pt",[(15.48,16.54,"Como eu chego ao museu?")]),("pt",[(16.90,17.23,"Ou:")]),
     ("en",[(17.57,19.42,"Where is the nearest subway station?")]),("pt",[(19.76,21.97,"Onde fica a estação de metrô mais próxima?")]),("pt",[(22.39,24.23,"Agora, entender a resposta.")]),
     ("en",[(24.60,25.16,"Turn left.")]),("pt",[(25.68,26.60,"Vire à esquerda.")]),("en",[(26.94,27.70,"Turn right.")]),("pt",[(27.98,28.87,"Vire à direita.")]),
     ("en",[(29.22,30.11,"Go straight.")]),("pt",[(30.35,31.30,"Siga em frente.")]),("en",[(31.66,32.69,"It's next to the bank.")]),("pt",[(33.18,34.40,"Fica ao lado do banco.")]),
     ("en",[(34.72,35.94,"It's across the street.")]),("pt",[(36.28,37.77,"Fica do outro lado da rua.")]),("pt",[(38.15,38.84,"Não entendeu?")]),
     ("en",[(39.19,40.99,"Could you say that again, more slowly?")]),("pt",[(41.30,42.65,"Pode repetir mais devagar?")]),
     ("pt",[(43.04,45.76,"Dica de ouro: pergunte também se é longe.")]),("en",[(46.09,46.82,"Is it far?")]),("pt",[(47.14,47.68,"É longe?")]),
     ("en",[(47.99,49.13,"It's a five-minute walk.")]),("pt",[(49.52,50.85,"São cinco minutos a pé.")]),
     ("pt",[(51.20,52.26,"Agora vamos treinar."),(52.58,55.43,"Escuta a moça na rua e repara nas respostas.")]),
     "SIM",
     ("pt",[(55.72,56.24,"Quiz!"),(56.59,57.53,"A pessoa diz:")]),("en",[(57.76,58.26,"Turn left.")]),("pt",[(58.82,61.80,"Para onde você vira: para a direita ou para a esquerda?")]),
     ("pt",[(62.17,62.98,"Para a esquerda!")]),("pt",[(63.32,66.29,"Left é esquerda, right é direita.")]),
     ("pt",[(66.64,69.35,"No PDF da aula tem mais frases de direção."),(69.60,73.03,"Nos vemos na próxima aula: táxi, Uber e metrô.")]),("en",[(73.44,74.72,"Follow Teacher Eliezio!")])],
   blocos=[("1 · PERGUNTAR 🙋", "C_AN", 6.80, [("🙋","Excuse me.","Com licença.",10.09),("🏛️","How do I get to the museum?","Como eu chego ao museu?",13.67),("🚇","Where is the nearest subway station?","Onde fica a estação de metrô mais próxima?",17.57)]),
           ("2 · ENTENDER A RESPOSTA 🧭", "C_A", 22.30, [("⬅️","Turn left.","Vire à esquerda.",24.60),("➡️","Turn right.","Vire à direita.",26.94),("⬆️","Go straight.","Siga em frente.",29.22),("🏦","It's next to the bank.","Fica ao lado do banco.",31.66),("↔️","It's across the street.","Fica do outro lado da rua.",34.72)]),
           ("3 · NÃO ENTENDEU? 🐢", "C_THE", 38.05, [("🐢","Could you say that again, more slowly?","Pode repetir mais devagar?",39.19)])],
   dica=("Pergunte também se é longe:", [("Is it far?", 46.09), ("It's a five-minute walk.", 47.99)], None),
   quiz=("⬅️", "A pessoa diz: “Turn left.”", [("Para a direita ➡️", False), ("Para a esquerda ⬅️", True)], "Left = esquerda · Right = direita"), quiz_after=63.32,
   proxima="PRÓXIMA AULA: 🚕 TRANSPORTE", pdf_sub="mais frases de direção + vocabulário",
   capa=("NA RUA", "Pedir e entender direções", "NA<br />RUA", "Pedir e entender<br />direções")),
 6: dict(dir="viagem6", titulo="TRANSPORTE", sub="Táxi, Uber e metrô", emo=["🚕", "🚗", "🚇"], cut=42.90, pin=50.05, vo_end=61.75, resp_nome="DRIVER", resp_emo="🧑‍✈️",
   sim_pill="SIMULAÇÃO · UBER 🚗", sim_files=("motorista.mp3", "voce.mp3"),
   sim=[("r",0.0,0.70,"Hi there!"),("v",0.0,1.80,"Hi! Who are you picking up?"),("r",0.80,2.75,"Silva, to Central Park."),("v",1.85,4.30,"That's me! How long will it take?"),
        ("r",2.90,4.98,"About twenty minutes with this traffic."),("v",4.35,5.88,"Can you stop here, please?"),("r",5.05,6.60,"Sure. Here we are."),("v",5.95,6.80,"Thank you!"),("r",6.65,7.68,"Have a good one!")],
   caps=[("pt",[(0.06,2.64,"Agora você precisa se locomover pela cidade.")]),("pt",[(3.14,5.60,"Hoje: táxi, Uber e metrô.")]),("pt",[(6.17,7.42,"No táxi ou no Uber:")]),
     ("en",[(7.89,9.42,"Can you take me to this address?")]),("pt",[(9.78,11.28,"Pode me levar para este endereço?")]),
     ("en",[(11.68,12.67,"How long will it take?")]),("pt",[(13.15,14.13,"Quanto tempo vai levar?")]),
     ("en",[(14.52,15.80,"Can you stop here, please?")]),("pt",[(16.10,17.39,"Pode parar aqui, por favor?")]),("pt",[(17.84,18.36,"No metrô:")]),
     ("en",[(18.74,20.02,"Where can I buy a ticket?")]),("pt",[(20.33,21.39,"Onde eu compro o bilhete?")]),
     ("en",[(21.74,23.25,"Which line goes downtown?")]),("pt",[(23.63,24.75,"Qual linha vai para o centro?")]),
     ("en",[(25.26,26.46,"Is this the right train?")]),("pt",[(26.81,27.62,"Este é o trem certo?")]),
     ("pt",[(28.18,32.80,"Dica de ouro: antes de entrar no Uber, confira a placa no aplicativo e pergunte:")]),("en",[(33.15,34.05,"Who are you picking up?")]),("pt",[(34.50,35.50,"Quem você veio buscar?")]),
     ("pt",[(35.83,38.41,"Se o motorista disser o seu nome, é o carro certo.")]),("pt",[(38.92,39.93,"Agora vamos treinar."),(40.24,42.74,"Escuta o motorista e repara nas respostas.")]),
     "SIM",
     ("pt",[(43.05,43.53,"Quiz!"),(43.84,46.22,"Você quer descer do carro. O que você fala:")]),("pt",[(46.51,49.88,"Can you stop here, please, ou Where can I buy a ticket?")]),
     ("en",[(50.23,51.57,"Can you stop here, please!")]),("pt",[(51.89,53.94,"Where can I buy a ticket é no metrô.")]),
     ("pt",[(54.29,56.98,"No PDF da aula tem mais frases de transporte."),(57.21,60.17,"Nos vemos na última aula: compras e emergências.")]),("en",[(60.49,61.75,"Follow Teacher Eliezio!")])],
   blocos=[("1 · TÁXI OU UBER 🚕", "C_AN", 6.05, [("📍","Can you take me to this address?","Pode me levar para este endereço?",7.89),("⏱️","How long will it take?","Quanto tempo vai levar?",11.68),("✋","Can you stop here, please?","Pode parar aqui, por favor?",14.52)]),
           ("2 · NO METRÔ 🚇", "C_A", 17.75, [("🎫","Where can I buy a ticket?","Onde eu compro o bilhete?",18.74),("🏙️","Which line goes downtown?","Qual linha vai para o centro?",21.74),("🚆","Is this the right train?","Este é o trem certo?",25.26)])],
   dica=("Antes de entrar no Uber, confira a placa e pergunte:", [("Who are you picking up?", 33.15)], (35.83, "Se o motorista disser o seu nome, é o carro certo.")),
   quiz=("🚗", "Você quer descer do carro…", [("Where can I buy a ticket?", False), ("Can you stop here, please?", True)], "Where can I buy a ticket → é no metrô"), quiz_after=51.89,
   proxima="ÚLTIMA AULA: 🛍️ COMPRAS E EMERGÊNCIAS", pdf_sub="mais frases de transporte + vocabulário",
   capa=("TRANSPORTE", "Táxi, Uber e metrô", "TRANS-<br />PORTE", "Táxi, Uber<br />e metrô")),
 7: dict(dir="viagem7", titulo="COMPRAS E EMERGÊNCIAS", sub="Comprar com tranquilidade e pedir ajuda", emo=["🛍️", "🏷️", "🚑"], cut=48.89, pin=55.00, vo_end=69.31, resp_nome="SHOP", resp_emo="👩‍💼",
   sim_pill="SIMULAÇÃO · NA LOJA 🛍️", sim_files=("loja.mp3", "voce.mp3"),
   sim=[("r",0.0,1.45,"Hi! Can I help you?"),("v",0.0,2.75,"Hi! Do you have this in a smaller size?"),("r",1.55,3.20,"Sure, here's a medium."),("v",2.80,3.95,"Can I try it on?"),
        ("r",3.25,5.55,"Of course. The fitting room is over there."),("v",4.00,5.15,"How much is this?"),("r",5.60,7.35,"It's $29.99."),("v",5.20,6.05,"I'll take it."),
        ("r",7.40,9.25,"Great! Cash or card?"),("v",6.10,7.12,"Card, please."),("r",9.35,11.36,"Here's your receipt. Have a nice day!")],
   caps=[("pt",[(0.05,1.66,"Chegamos à última aula!")]),("pt",[(2.03,4.36,"Hoje: compras e emergências.")]),("pt",[(4.72,5.52,"Nas compras:")]),
     ("en",[(5.84,6.78,"How much is this?")]),("pt",[(7.12,8.03,"Quanto custa isso?")]),("en",[(8.41,10.19,"Do you have this in a smaller size?")]),("pt",[(10.46,11.74,"Tem esse num tamanho menor?")]),
     ("en",[(12.18,13.06,"Can I try it on?")]),("pt",[(13.36,14.23,"Posso experimentar?")]),("en",[(14.63,15.16,"I'll take it.")]),("pt",[(15.52,16.00,"Vou levar.")]),
     ("pt",[(16.51,21.23,"Agora, as emergências. Espero que você nunca precise, mas é importante saber.")]),
     ("en",[(21.68,22.36,"I need help!")]),("pt",[(22.79,24.05,"Eu preciso de ajuda!")]),("en",[(24.41,25.61,"I lost my passport.")]),("pt",[(26.00,27.25,"Eu perdi meu passaporte.")]),
     ("en",[(27.61,28.49,"I need a doctor.")]),("pt",[(28.79,30.01,"Eu preciso de um médico.")]),("en",[(30.32,31.33,"Call the police!")]),("pt",[(31.49,32.41,"Chame a polícia!")]),
     ("en",[(32.73,34.07,"Where is the nearest pharmacy?")]),("pt",[(34.40,36.05,"Onde fica a farmácia mais próxima?")]),
     ("pt",[(36.38,41.01,"Dica de ouro: nos Estados Unidos, o número de emergência é 911."),(41.31,44.48,"E antes de viajar, anote o telefone do consulado brasileiro.")]),
     ("pt",[(44.93,45.82,"Agora vamos treinar."),(46.21,48.75,"Escuta a vendedora e repara nas respostas.")]),
     "SIM",
     ("pt",[(49.03,49.55,"Quiz!"),(49.87,52.27,"Você quer saber o preço. O que você fala:")]),("pt",[(52.49,54.79,"How much is this, ou I need a doctor?")]),
     ("en",[(55.18,56.16,"How much is this!")]),("pt",[(56.49,58.44,"I need a doctor é para emergência.")]),
     ("pt",[(58.84,61.94,"Parabéns! Você terminou o curso Inglês para Viajar."),(62.24,66.65,"No PDF tem o seu certificado e um resumo com as frases mais importantes.")]),
     ("pt",[(66.90,67.66,"Boa viagem!")]),("en",[(68.02,69.31,"Follow Teacher Eliezio!")])],
   blocos=[("1 · COMPRAS 🛍️", "C_AN", 4.62, [("🏷️","How much is this?","Quanto custa isso?",5.84),("📏","Do you have this in a smaller size?","Tem esse num tamanho menor?",8.41),("👕","Can I try it on?","Posso experimentar?",12.18),("🛒","I'll take it.","Vou levar.",14.63)]),
           ("2 · EMERGÊNCIAS 🚑", "RED", 16.40, [("🆘","I need help!","Eu preciso de ajuda!",21.68),("🛂","I lost my passport.","Eu perdi meu passaporte.",24.41),("🩺","I need a doctor.","Eu preciso de um médico.",27.61),("🚓","Call the police!","Chame a polícia!",30.32),("💊","Where is the nearest pharmacy?","Onde fica a farmácia mais próxima?",32.73)])],
   dica=("Nos EUA, o número de emergência é:", [("911", 38.5)], (41.31, "Antes de viajar, anote o telefone do consulado brasileiro.")),
   quiz=("🏷️", "Você quer saber o preço…", [("I need a doctor.", False), ("How much is this?", True)], "I need a doctor → é para emergência"), quiz_after=56.49,
   proxima="🎓 PARABÉNS! CURSO CONCLUÍDO", pdf_sub="certificado + resumo com as frases do curso",
   capa=("COMPRAS E EMERGÊNCIAS", "Comprar e pedir ajuda em inglês", "COMPRAS E<br />EMERGÊNCIAS", "Comprar e pedir<br />ajuda em inglês")),
}
def load(p): return np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",p,"-ar",str(SR),"-ac","1","-f","s16le","-"],capture_output=True).stdout,np.int16).astype(np.float32)/32768
def main(n):
    sp = SPECS[n]; D = f"{S}/{sp['dir']}"
    t = load(f"{D}/vo_prof.mp3"); r = load(f"{D}/{sp['sim_files'][0]}"); v = load(f"{D}/{sp['sim_files'][1]}")
    CUT = sp["cut"]; seg = [np.zeros(int(0.5*SR), np.float32)]; tl = 0.5; sim = []
    for who, a, b, txt in sp["sim"]:
        src = r if who == "r" else v; piece = src[int(a*SR):int(b*SR)]
        sim.append([round(CUT+tl, 2), round(CUT+tl+len(piece)/SR, 2), who, txt]); seg.append(piece); tl += len(piece)/SR
        seg.append(np.zeros(int(0.45*SR), np.float32)); tl += 0.45
    out = np.concatenate([t[:int(CUT*SR)]] + seg + [t[int(CUT*SR):]])
    subprocess.run(["ffmpeg","-v","error","-y","-f","s16le","-ar",str(SR),"-ac","1","-i","-","-b:a","192k",f"{D}/vo_raw.mp3"],input=(np.clip(out,-1,1)*32767).astype(np.int16).tobytes(),check=True)
    DL = round(tl, 2); sh = lambda x: round(x + DL, 2) if x >= CUT else x
    # ---- config do prep_aula
    caps = []
    for c in sp["caps"]:
        if c == "SIM": caps += [("en", [(a, b, tx)]) for a, b, w, tx in sim]
        else: caps.append((c[0], [(sh(a), sh(b), tx) for a, b, tx in c[1]]))
    blocos = sp["blocos"]; first_frase = blocos[0][3][0][3]
    clicks = [it[3] for bl in blocos for it in bl[3]]
    tk = dict(intro=0, goal=sp["caps"][1][1][0][0], tip=[c for c in sp["caps"] if c != "SIM" and c[1][0][2].startswith("Dica")][0][1][0][0] - 0.1,
              sim=CUT, quiz=sh(CUT + 0.1), cta=sh(sp["vo_end"] - 1.4), end=sh(sp["vo_end"]))
    for i, bl in enumerate(blocos): tk[f"b{i}"] = bl[2]
    trein = [c for c in sp["caps"] if c != "SIM" and c[1][0][2].startswith("Agora vamos treinar")][0][1][0][0]; tk["train"] = trein
    qcaps = [c for c in sp["caps"] if c != "SIM" and c[1][0][0] > CUT]
    tk["q1"] = sh(qcaps[0][1][-1][0]); tk["qopt"] = sh(qcaps[1][1][0][0]); tk["after"] = sh(sp["quiz_after"])
    pdfcap = [c for c in qcaps if "PDF" in c[1][0][2] or "Parabéns" in c[1][0][2]][0]; tk["pdf"] = sh(pdfcap[1][0][0] - 0.1)
    expr = [(0, 1), (blocos[0][2], 2), (first_frase, 1), (tk["tip"], 8), (tk["tip"] + 1.0, 1), (CUT, 2), (sh(CUT + 0.15), 1), (sh(sp["vo_end"] - 1.6), 8), (sh(sp["vo_end"] - 0.6), 1)]
    whoosh = [bl[2] for bl in blocos] + [tk["tip"], CUT - 0.1, sh(CUT + 0.05), tk["pdf"]]
    cfg = f'''# Mini curso "Inglês para viajar", Aula {n}: {sp["titulo"].title()} (08/11/2026). Gerado por curso-viagem/gera_aula.py.
DIR = "{sp["dir"]}"
PINS = [{sh(sp["pin"])}]
VO_END = {sh(sp["vo_end"])}
CAP = {caps!r}
EXPR = {sorted(expr)!r}
WHOOSH = {tuple(whoosh)!r}
CLICKS = {tuple(clicks)!r}
CTA_THUD = {tk["cta"]}
TK = {tk!r}
'''
    open(f"{REPO}/scripts/aulas/aula_viagem{n}.py", "w", encoding="utf8").write(cfg)
    # ---- composição Remotion (a partir da Aula 4)
    s = open(f"{S}/remotion/src/Viagem4.tsx", encoding="utf8").read()
    s = s.replace('import TM from "./timings/viagem4.json";', f'import TM from "./timings/viagem{n}.json";').replace("Aula 4: Pagar a conta e a gorjeta (08/11/2026)", f"Aula {n}: {sp['titulo'].title()} (08/11/2026, gerada por curso-viagem/gera_aula.py)").replace("viagem4.json (scripts/prep_aula.py + aulas/aula_viagem4.py)", f"viagem{n}.json (scripts/prep_aula.py + aulas/aula_viagem{n}.py)")
    a = s.index("const Intro = () =>"); b = s.index("const Simulacao = () =>")
    e = sp["emo"]; nb = len(blocos)
    sc = f'''const Intro = () => (
  <Scene a={{0}} b={{T.b0}}>
    <In at={{0.1}}><Pill bg={{C_A}} size={{34}}>✈️ INGLÊS PARA VIAJAR · MINI CURSO</Pill></In>
    <In at={{0.6}}><div style={{{{ display: "flex", gap: 50 }}}}>{"".join(f'<Emoji e="{x}" size={{120}} />' for x in e)}</div></In>
    <In at={{1.2}}><Title size={{{100 if len(sp["titulo"]) > 12 else 120}}} color={{YEL}}>AULA {n} · {sp["titulo"]}</Title></In>
    <In at={{T.goal}}><div style={{{{ font: F(700, 40), color: PT, textAlign: "center" }}}}>{sp["sub"]}</div></In>
  </Scene>
);
'''
    for i, (pill, cor, at, its) in enumerate(blocos):
        end = f"T.b{i+1}" if i + 1 < nb else "T.tip"
        size = 62 if len(its) <= 2 else (54 if len(its) <= 3 else 44); gap = 26 if len(its) <= 3 else 14
        grid = len(its) > 4; w = 660 if grid else 1000; size = 44 if grid else size
        items = "".join(f'\n      <Frase at={{{t0}}} w={{{w}}} e="{em}" en="{en}" pt="{pt}" size={{{size}}}{" border={RED}" if cor == "RED" else ""} />' for em, en, pt, t0 in its)
        lay = 'display: "grid", gridTemplateColumns: "1fr 1fr", columnGap: 34, rowGap: 22' if grid else f'display: "flex", flexDirection: "column", gap: {gap}'
        sc += f'''const Bloco{i} = () => (
  <Scene a={{T.b{i}}} b={{{end}}} gap={{18}}>
    <In at={{T.b{i}}}><Pill bg={{{cor}}} size={{44}}>{pill}</Pill></In>
    <div style={{{{ {lay}, marginTop: 6 }}}}>{items}
    </div>
  </Scene>
);
'''
    dt, pills, extra = sp["dica"]
    pill_html = "".join(f'<In at={{{t0}}}><Pill bg={{{["C_A","C_AN","C_THE"][k % 3]}}} size={{{90 if len(txt) <= 4 else 54}}}>{txt}</Pill></In>' for k, (txt, t0) in enumerate(pills))
    extra_html = f'\n    <In at={{{extra[0]}}}><div style={{{{ font: F(700, 38), color: PT }}}}>{extra[1]}</div></In>' if extra else ""
    sc += f'''const Dica = () => (
  <Scene a={{T.tip}} b={{T.sim}}>
    <In at={{T.tip}}><Title size={{110}} color={{YEL}}>💡 DICA DE OURO</Title></In>
    <In at={{T.tip + 1.2}}><div style={{{{ font: F(700, 40), color: PT }}}}>{dt}</div></In>
    <div style={{{{ display: "flex", gap: 30, flexWrap: "wrap", justifyContent: "center" }}}}>{pill_html}</div>{extra_html}
    <In at={{T.train}}><Pill bg={{YEL}} color={{INK}} size={{40}}>AGORA VAMOS TREINAR</Pill></In>
  </Scene>
);
const SIM: [number, number, "r" | "v", string][] = {json.dumps(sim, ensure_ascii=False)};
'''
    s = s[:a] + sc + s[b:]
    s = s.replace("SIMULAÇÃO · A CONTA 🧾", sp["sim_pill"]).replace('<Emoji e="🧑‍🍳" size={150}', f'<Emoji e="{sp["resp_emo"]}" size={{150}}').replace(">WAITER<", f">{sp['resp_nome']}<")
    qe, qt, qo, qa = sp["quiz"]
    s = s.replace('<Emoji e="➗" size={100} /><Card border={C_A}><span style={{ font: `400 72px Anton`, color: "#fff" }}>Você quer dividir a conta…</span>', f'<Emoji e="{qe}" size={{100}} /><Card border={{C_A}}><span style={{{{ font: `400 66px Anton`, color: "#fff" }}}}>{qt}</span>')
    s = s.replace('{opt("Keep the change.", false, 0)}{opt("Can we split the bill?", true, 1)}', f'{{opt("{qo[0][0]}", {str(qo[0][1]).lower()}, 0)}}{{opt("{qo[1][0]}", {str(qo[1][1]).lower()}, 1)}}')
    s = s.replace('Keep the change → é para <b style={{ color: YEL }}>deixar o troco</b>', qa)
    s = s.replace("mais frases para pagar + vocabulário", sp["pdf_sub"]).replace("PRÓXIMA AULA: 🗺️ NA RUA", sp["proxima"])
    s = s.replace("export const Viagem4: React.FC", f"export const Viagem{n}: React.FC").replace(">AULA 4 de 7<", f">AULA {n} de 7<").replace("<Intro /><Conta /><Pagar /><Gorjeta /><Dica />", "<Intro />" + "".join(f"<Bloco{i} />" for i in range(nb)) + "<Dica />")
    s = s.replace("export const Viagem4Capa: React.FC", f"export const Viagem{n}Capa: React.FC").replace("export const Viagem4Capa916: React.FC", f"export const Viagem{n}Capa916: React.FC")
    s = s.replace("INGLÊS PARA VIAJAR · AULA 4</Pill>", f"INGLÊS PARA VIAJAR · AULA {n}</Pill>").replace(">AULA 4 DE 7<", f">AULA {n} DE 7<")
    for sz in (130, 140): s = s.replace(f'<Emoji e="🧾" size={{{sz}}} /><Emoji e="💳" size={{{sz}}} /><Emoji e="💵" size={{{sz}}} />', "".join(f'<Emoji e="{x}" size={{{sz}}} />' for x in e))
    c1, c2, c3, c4 = sp["capa"]
    s = s.replace('<Title size={150} color={YEL}>A CONTA E A GORJETA</Title>\n    <Title size={70}>Pedir a conta, pagar e dar gorjeta</Title>', f'<Title size={{{150 if len(c1) <= 12 else 120}}} color={{YEL}}>{c1}</Title>\n    <Title size={{70}}>{c2}</Title>')
    s = s.replace('<Title size={170} color={YEL}>A CONTA<br />E A GORJETA</Title>\n    <Title size={76}>Pedir a conta, pagar<br />e dar gorjeta</Title>', f'<Title size={{{170 if len(c3) <= 16 else 130}}} color={{YEL}}>{c3}</Title>\n    <Title size={{76}}>{c4}</Title>')
    for k in ["Conta", "Pagar", "Gorjeta", "check", "gorjeta"]:
        if k in s.split("const Simulacao")[0].split("const Intro")[1]: print("ATENÇÃO sobra:", k)
    open(f"{S}/remotion/src/Viagem{n}.tsx", "w", encoding="utf8").write(s)
    idx = f"{S}/remotion/src/index.tsx"; ix = open(idx, encoding="utf8").read()
    if f'from "./Viagem{n}"' not in ix:
        ix = ix.replace('import TV4 from "./timings/viagem4.json";', f'import TV4 from "./timings/viagem4.json";\nimport {{ Viagem{n}, Viagem{n}Capa, Viagem{n}Capa916 }} from "./Viagem{n}";\nimport TV{n} from "./timings/viagem{n}.json";')
        ix = ix.replace("  </>\n);", f'''    <Composition id="Viagem{n}" component={{Viagem{n}}} width={{1920}} height={{1080}} fps={{TV{n}.fps}} durationInFrames={{Math.round(TV{n}.total * TV{n}.fps)}} />
    <Still id="Viagem{n}Capa" component={{Viagem{n}Capa}} width={{1920}} height={{1080}} />
    <Still id="Viagem{n}Capa916" component={{Viagem{n}Capa916}} width={{1080}} height={{1920}} />
  </>
);''')
        open(idx, "w", encoding="utf8").write(ix)
    json.dump(dict(cut=CUT, sim_len=DL, sim=sim), open(f"{D}/sim.json", "w"), indent=1, ensure_ascii=False)
    print("ok aula", n, "sim", DL)
if __name__ == "__main__":
    for a in sys.argv[1:]: main(int(a))
