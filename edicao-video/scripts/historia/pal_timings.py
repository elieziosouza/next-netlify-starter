import json,re,wave,numpy as np
spans=[(0.0,6.48),(6.69,9.05),(9.29,17.41),(17.59,20.2),(20.51,26.75),(27.18,28.17),(28.43,31.51),(31.78,37.39),(37.55,43.28),(43.64,47.88),(48.11,52.51),(52.75,54.49)]
sents=["No fim do século dezesseis, em Pernambuco, escravizados que fugiam dos engenhos se refugiam na Serra da Barriga.","Nascia o Quilombo dos Palmares.",
"No auge, historiadores estimam entre 11 mil e 20 mil pessoas: africanos, indígenas e colonos marginalizados.","Era o maior quilombo da história do Brasil.",
"Entre 1680 e 1686, ao menos seis expedições tentam destruí-lo.","Todas fracassam.","Zumbi se torna a principal liderança da resistência.",
"Em 1694, uma grande ofensiva, com artilharia, destrói Palmares.","Zumbi resiste até 20 de novembro de 1695, quando é morto numa emboscada.",
"Em 1995, Zumbi é reconhecido como herói nacional.","E desde 2024, o 20 de novembro é feriado em todo o país:","o Dia da Consciência Negra."]
def wt(x): return max(len(re.sub(r'[^\wÀ-ú]','',x)),2)+1.2
words=[]
for si,((s,e),txt) in enumerate(zip(spans,sents)):
    ws=txt.split(); W=[wt(x) for x in ws]; T=sum(W); c=s
    for x,wx in zip(ws,W):
        d=(e-s)*wx/T; words.append(dict(w=x,s=round(c,2),e=round(c+d,2),si=si)); c+=d
def mark(si,pat,nth=1):
    n=0
    for x in words:
        if x['si']==si and re.search(pat,x['w'],re.I):
            n+=1
            if n==nth: return x['s']
    raise SystemExit(f'sem {si} {pat}')
M=dict(seculo=mark(0,'século'),pern=mark(0,'Pernambuco'),engenhos=mark(0,'engenhos'),serra=mark(0,'Serra'),barriga=mark(0,'Barriga'),
 quilombo=mark(1,'Quilombo'),palmares=mark(1,'Palmares'),auge=mark(2,'auge'),n11=mark(2,'^11$'),n20=mark(2,'^20$'),afric=mark(2,'africanos'),indig=mark(2,'indígenas'),colonos=mark(2,'colonos'),
 maior=mark(3,'maior'),a1680=mark(4,'1680'),a1686=mark(4,'1686'),seis=mark(4,'seis'),exped=mark(4,'expedições'),fracas=mark(5,'fracassam'),zumbi1=mark(6,'Zumbi'),lider=mark(6,'liderança'),
 a1694=mark(7,'1694'),artil=mark(7,'artilharia'),destroi=mark(7,'destrói'),zumbi2=mark(8,'Zumbi'),n20n=mark(8,'^20$'),a1695=mark(8,'1695'),embosc=mark(8,'emboscada'),
 a1995=mark(9,'1995'),heroi=mark(9,'herói'),a2024=mark(10,'2024'),feriado=mark(10,'feriado'),pais=mark(10,'país'),consc=mark(11,'Consciência'))
caps=[];cur=[]
for i,x in enumerate(words):
    cur.append(x)
    if re.search(r'[\.,:]$',x['w']) or len(cur)==4 or (i+1<len(words) and words[i+1]['si']!=x['si']):
        caps.append(dict(t=cur[0]['s'],e=cur[-1]['e'],text=' '.join(c['w'] for c in cur))); cur=[]
if cur: caps.append(dict(t=cur[0]['s'],e=cur[-1]['e'],text=' '.join(c['w'] for c in cur)))
out=dict(fps=30,total=55.0,spans=spans,M={k:round(v,2) for k,v in M.items()},caps=caps)
json.dump(out,open('timings.json','w'),ensure_ascii=False,indent=0); print(out['M'])
