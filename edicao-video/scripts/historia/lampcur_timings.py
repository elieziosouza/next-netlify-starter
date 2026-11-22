# Tempos do Short "Lampião: herói ou bandido?" (22/11/2026, vertical, Instagram/TikTok): silencedetect da voz (atempo 1.08) + peso por letras.
import json,re
spans=[(0.0,0.63),(0.93,2.2),(2.68,8.9),(9.11,11.97),(12.18,13.72),(13.94,19.18),(19.36,29.49),(29.75,34.7),(35.04,43.31),(43.55,45.3),(45.46,47.26),(47.46,49.83),(50.36,52.97),(53.34,55.46),(55.86,56.36),(56.55,57.14)]
sents=["Lampião:","herói ou bandido?","Virgulino Ferreira da Silva nasceu em Pernambuco, entre 1897 e 1900.","Uma briga com um vizinho tirou a família do sítio,","e ele entrou no cangaço.",
"Em 1922, assumiu o comando do bando e virou o Rei do Cangaço.","Foram cerca de dezesseis anos, em sete estados do Nordeste, com mais de duzentos confrontos com as volantes. Estima-se que o bando tenha matado mais de mil pessoas.",
"Em 1930, conheceu Maria Bonita, a primeira mulher a entrar no bando.","No dia 28 de julho de 1938, a volante do tenente João Bezerra o surpreendeu na Grota do Angico, em Sergipe.",
"Em cerca de vinte minutos,","onze cangaceiros estavam mortos,","entre eles Lampião e Maria Bonita.","Para as autoridades, ele era a brutalidade.","Para parte dos sertanejos, bravura.","E você,","o que acha?"]
assert len(spans)==len(sents)==16
def wt(x): return max(len(re.sub(r'[^\wÀ-ú]','',x)),2)+1.2
words=[]
for si,((s,e),txt) in enumerate(zip(spans,sents)):
    ws=txt.split(); W=[wt(x) for x in ws]; T=sum(W); c=s
    for x,wx in zip(ws,W):
        d=(e-s)*wx/T; words.append(dict(w=x,s=round(c,2),e=round(c+d,2),si=si)); c+=d
def mark(si,pat):
    for x in words:
        if x['si']==si and re.search(pat,x['w'],re.I): return x['s']
    raise SystemExit(f'sem {si} {pat}')
MK=dict(a1897=(2,'1897'),pern=(2,'Pernambuco'),briga=(3,'briga'),cangaco=(4,'cangaço'),a1922=(5,'1922'),rei=(5,'Rei'),dezesseis=(6,'dezesseis'),sete=(6,'sete'),duzentos=(6,'duzentos'),mil=(6,r'^mil$'),a1930=(7,'1930'),primeira=(7,'primeira'),
 a1938=(8,'1938'),surp=(8,'surpreendeu'),grota=(8,'Grota'),sergipe=(8,'Sergipe'),vinte=(9,'vinte'),onze=(10,'onze'),eles=(11,'entre'),auto=(12,'autoridades'),brut=(12,'brutalidade'),sert=(13,'sertanejos'),bravura=(13,'bravura'),voce=(14,'você'))
M={k:round(mark(*v),2) for k,v in MK.items()}
caps=[];cur=[]
for i,x in enumerate(words):
    cur.append(x)
    if re.search(r'[\.,:?]$',x['w']) or len(cur)==4 or (i+1<len(words) and words[i+1]['si']!=x['si']):
        caps.append(dict(t=cur[0]['s'],e=cur[-1]['e'],words=[dict(w=c['w'],s=c['s'],e=c['e']) for c in cur])); cur=[]
if cur: caps.append(dict(t=cur[0]['s'],e=cur[-1]['e'],words=[dict(w=c['w'],s=c['s'],e=c['e']) for c in cur]))
out=dict(fps=30,total=58.6,spans=spans,M=M,caps=caps)
json.dump(out,open('lampcur.json','w'),ensure_ascii=False,indent=0); print(M)
