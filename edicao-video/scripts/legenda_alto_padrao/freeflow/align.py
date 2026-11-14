import json, wave, numpy as np, re
segs=json.load(open("segs.json"))
# texto corrigido pelo roteiro, um por segmento VAD
FIX=["Atenção, motorista: o prazo para pagar o free flow atrasado, sem multa, acaba nessa segunda-feira, dia 16.",
"O free flow é o pedágio sem cancela.",
"Câmeras e sensores leem a sua placa e registram a cobrança.",
"Você não é multado por passar, a multa vem se você não pagar. E quanto custa deixar para pagar depois? Não pagar é evasão de pedágio, infração grave, multa de R$ 195,23",
"e cinco pontos na carteira.",
"Segundo o Ministério dos Transportes, até 29 de outubro, mais de 724 mil motoristas ainda não tinham pago. Quem passou pelos pórticos até 17 de outubro tem até segunda-feira para quitar sem multa.",
"E quem pagar até lá ainda pode ter retirados da CNH os pontos das infrações que ficaram suspensas.",
"Como consultar? Abre o aplicativo da CNH do Brasil,",
"toque em veículos, escolha seu carro e depois em pedágio eletrônico.",
"Ali aparecem as passagens e o caminho para o canal oficial de pagamento da concessionária.",
"Minha dica: o governo está avisando por WhatsApp, mas não clique em link solto.",
"Entre no aplicativo e confira lá. E se você já pagou multa por isso, dá para pedir reembolso pelo gov.br no site da ANTT. Você já conferiu o seu carro?",
"Me conta aqui nos comentários."]
assert len(FIX)==len(segs)
w=wave.open("a16.wav"); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
hop=160; rms=np.sqrt(np.convolve(a**2,np.ones(800)/800,'same'))[::hop]  # 10 ms
def t2i(t): return int(t*100)
def wt(wd):
    v=len(re.sub(r"[^\wÀ-ú]","",wd)); return max(v,2)+1.5
words=[]
for s,txt in zip(segs,FIX):
    st,en=s["start"],s["end"]
    sents=[x for x in re.split(r"(?<=[\.\?\!:,])\s+",txt) if x]
    # peso por sentença, depois ajusta fronteiras para o vale de energia mais próximo
    ws=[sum(wt(x) for x in se.split()) for se in sents]; tot=sum(ws)
    bounds=[st]; acc=0
    for k in range(len(sents)-1):
        acc+=ws[k]; est=st+(en-st)*acc/tot
        lo,hi=t2i(max(st+.2,est-.6)),t2i(min(en-.2,est+.6))
        if hi>lo: est=(lo+int(np.argmin(rms[lo:hi])))/100
        bounds.append(est)
    bounds.append(en)
    for k,se in enumerate(sents):
        a0,a1=bounds[k],bounds[k+1]; ww=se.split(); W=[wt(x) for x in ww]; T=sum(W); c=a0
        for x,wx in zip(ww,W):
            d=(a1-a0)*wx/T; words.append(dict(w=x,s=round(c,3),e=round(c+d,3))); c+=d
json.dump(words,open("words.json","w"),ensure_ascii=False,indent=0)
print(len(words)); print(" ".join(f"{x['w']}@{x['s']:.1f}" for x in words[:40]))
