import json, wave, numpy as np, re
segs=json.load(open("segs.json"))
# texto corrigido pelo roteiro, um por segmento VAD
FIX=["As bets vão voltar ou não? Hoje saiu uma decisão do STF que muita gente entendeu errado.",
"Vou te explicar rapidinho.",
"Em setembro, o governo proibiu as bets com uma medida provisória. Acabou a aposta, acabou a propaganda, inclusive de influenciador.",
"Só que várias empresas foram para a Justiça tentar derrubar essa proibição.",
"E hoje o ministro Luiz Fux mandou parar todos esses processos no Brasil inteiro,",
"até o próprio STF decidir de uma vez se a proibição vale ou não.",
"Ou seja,",
"por enquanto nada muda. Bet continua proibida.",
"Mas presta atenção numa coisa: a medida provisória tem prazo. Se o Congresso não aprovar a tempo, ela perde a validade. Então essa história ainda não acabou.",
"E o dinheiro que você perdeu apostando?",
"Esse não volta.",
"A proibição só devolveu o saldo que estava parado na conta. Agora me fala sinceramente:",
"você acha que proibir foi certo ou deveria só ter regras mais duras?",
"Comenta aqui embaixo, por favor."]
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
