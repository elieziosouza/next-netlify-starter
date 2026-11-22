# Tempos do vídeo "Canudos" (22/11/2026): pausas da voz (silencedetect) + peso por letras dentro de cada frase.
# Uso: python3 can_timings.py  → escreve can.json (copiar para remotion-historia/src/)
import json,re
spans=[(0.0,1.06),(1.23,3.11),(3.53,11.65),(11.98,13.7),(13.88,21.35),(21.64,26.15),(26.37,30.29),(30.58,32.24),(32.59,39.07),(39.57,43.35),(43.55,48.6),(48.86,55.0)]
sents=["Sertão da Bahia,","1893.","O líder religioso Antônio Conselheiro funda o arraial de Belo Monte, às margens do rio Vaza-Barris, perto da antiga fazenda de Canudos.",
"A comunidade cresce depressa.","Estima-se que chegou a ter entre 25 mil e 30 mil moradores: sertanejos pobres e muitos ex-escravizados.",
"A jovem República suspeita de uma conspiração monarquista e envia tropas.","A primeira expedição parte em novembro de 1896.","As três primeiras fracassam.",
"A quarta, com perto de 10 mil homens, cerca o arraial por meses e o bombardeia com artilharia pesada.","Canudos cai em 5 de outubro de 1897.",
"A guerra matou, segundo estimativas, entre 15 mil e 30 mil pessoas.","O episódio inspirou Os Sertões, de Euclides da Cunha, um dos livros fundamentais da literatura brasileira."]
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
M=dict(sertao=mark(0,'Sertão'),a1893=mark(1,'1893'),lider=mark(2,'líder'),consel=mark(2,'Conselheiro'),belo=mark(2,'Belo'),rio=mark(2,'rio'),canudos=mark(2,'Canudos'),
 cresce=mark(3,'cresce'),n25=mark(4,'^25$'),n30=mark(4,'^30$'),sertanejos=mark(4,'sertanejos'),exesc=mark(4,'ex-'),
 repub=mark(5,'República'),monarq=mark(5,'monarquista'),tropas=mark(5,'tropas'),primeira=mark(6,'primeira'),nov=mark(6,'novembro'),a1896=mark(6,'1896'),tres=mark(7,'três'),fracas=mark(7,'fracassam'),
 quarta=mark(8,'quarta'),n10=mark(8,'^10$'),cerca=mark(8,'cerca'),meses=mark(8,'meses'),bomb=mark(8,'bombardeia'),artil=mark(8,'artilharia'),
 cai=mark(9,'cai'),a1897=mark(9,'1897'),out=mark(9,'outubro'),guerra=mark(10,'guerra'),n15=mark(10,'^15$'),n30b=mark(10,'^30$'),sertoes=mark(11,'Sertões'),eucl=mark(11,'Euclides'),livros=mark(11,'livros'))
caps=[];cur=[]
for i,x in enumerate(words):
    cur.append(x)
    if re.search(r'[\.,:]$',x['w']) or len(cur)==4 or (i+1<len(words) and words[i+1]['si']!=x['si']):
        caps.append(dict(t=cur[0]['s'],e=cur[-1]['e'],words=[dict(w=c['w'],s=c['s'],e=c['e']) for c in cur])); cur=[]
if cur: caps.append(dict(t=cur[0]['s'],e=cur[-1]['e'],words=[dict(w=c['w'],s=c['s'],e=c['e']) for c in cur]))
out=dict(fps=30,total=56.0,spans=spans,M={k:round(v,2) for k,v in M.items()},caps=caps)
json.dump(out,open('can.json','w'),ensure_ascii=False,indent=0); print(out['M'])
