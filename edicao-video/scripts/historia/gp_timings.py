import json,re,wave,numpy as np
spans=[(0.0,3.03),(3.24,6.66),(7.04,10.18),(10.43,14.32),(14.62,22.04),(22.39,26.46),(26.71,32.23),(32.52,36.41),(36.72,45.02),(45.30,51.12),(51.48,58.13)]
sents=["11 de novembro de 1864.","No porto de Assunção, o Paraguai prende um navio brasileiro.","Começava a maior guerra da história da América do Sul.",
"Seis semanas depois, o exército paraguaio invade Mato Grosso.","Em maio de 1865, Brasil, Argentina e Uruguai assinam, em segredo, a Tríplice Aliança.",
"Em junho, a Batalha Naval de Riachuelo destrói a frota paraguaia.","A fortaleza de Humaitá cai em julho de 1868, depois de um longo cerco.","Em janeiro de 1869, Assunção é ocupada.",
"A guerra só termina em primeiro de março de 1870, em Cerro Corá, com a morte do presidente paraguaio, Solano López.","O Brasil enviou cerca de 150 mil homens, e cerca de 50 mil não voltaram.",
"O Paraguai perdeu, segundo estimativas, até 300 mil pessoas, entre combates, doenças e fome."]
w=wave.open('a16.wav'); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
rms=np.sqrt(np.convolve(a**2,np.ones(800)/800,'same'))[::160]
def wt(x): return max(len(re.sub(r'[^\wÀ-ú]','',x)),2)+1.2
words=[]
for si,((s,e),txt) in enumerate(zip(spans,sents)):
    ws=txt.split(); W=[wt(x) for x in ws]; T=sum(W); c=s
    for x,wx in zip(ws,W):
        d=(e-s)*wx/T; words.append(dict(w=x,s=round(c,2),e=round(c+d,2),si=si)); c+=d
# marcas nomeadas
def mark(si,pat):
    for x in words:
        if x['si']==si and re.search(pat,x['w'],re.I): return x['s']
    raise SystemExit(f'sem {si} {pat}')
M=dict(
 d1=0.15, porto=mark(1,'porto'), prende=mark(1,'prende'), maior=mark(2,'maior'), sul=mark(2,'Sul'),
 invade=mark(3,'invade'), mt=mark(3,'Mato'), maio=mark(4,'maio'), brasil=mark(4,'Brasil'), segredo=mark(4,'segredo'), triplice=mark(4,'Tríplice'),
 junho=mark(5,'junho'), riach=mark(5,'Riachuelo'), destroi=mark(5,'destrói'), humaita=mark(6,'Humaitá'), cai=mark(6,'cai'), cerco=mark(6,'cerco'),
 jan=mark(7,'janeiro'), assuncao=mark(7,'Assunção'), ocupada=mark(7,'ocupada'), termina=mark(8,'termina'), marco=mark(8,'março'), cerro=mark(8,'Cerro'),
 morte=mark(8,'morte'), solano=mark(8,'Solano'), brasilN=mark(9,'Brasil'), n150=mark(9,'^150$'), n50=mark(9,'^50$'), parN=mark(10,'Paraguai'), n300=mark(10,'^300$'), fome=mark(10,'fome'))
# legendas: grupos de até 4 palavras, quebra na pontuação
caps=[];cur=[]
for i,x in enumerate(words):
    cur.append(x)
    if re.search(r'[\.,]$',x['w']) or len(cur)==4 or (i+1<len(words) and words[i+1]['si']!=x['si']):
        caps.append(dict(t=cur[0]['s'],e=cur[-1]['e'],text=' '.join(c['w'] for c in cur))); cur=[]
if cur: caps.append(dict(t=cur[0]['s'],e=cur[-1]['e'],text=' '.join(c['w'] for c in cur)))
out=dict(fps=30,total=58.7,spans=spans,M={k:round(v,2) for k,v in M.items()},caps=caps)
json.dump(out,open('timings.json','w'),ensure_ascii=False,indent=0); print(out['M']); print(len(caps))
