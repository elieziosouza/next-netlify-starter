# Tempos do vídeo "Lampião" (22/11/2026, horizontal 1920x1080): pausas da voz (silencedetect, voz sem aceleração) + peso por letras.
# Uso: python3 lamp_timings.py → escreve lamp.json (copiar para remotion-historia/src/)
import json,re
spans=[(0.0,2.34),(2.53,4.59),(4.82,8.43),(8.86,11.08),(12.05,18.7),(18.93,21.13),(21.36,32.53),(32.85,40.73),(40.91,41.78),(42.06,46.33),(46.53,50.48),(50.67,57.01),(57.7,65.65),(65.98,68.04),(68.33,73.79),(74.11,81.94),(82.17,86.96),(87.25,93.8),(93.99,99.59),(99.88,106.83),(107.38,115.51),(115.83,120.96),(121.24,122.93),(123.13,126.26),(126.85,133.31),(133.69,137.19),(137.64,141.55),(141.73,142.85),(143.36,147.73),(148.01,151.54),(152.06,153.59),(153.83,159.59),(159.87,166.73),(167.05,168.83),(169.3,173.7),(174.03,178.37),(178.62,180.43),(180.69,183.91),(184.27,186.8),(187.28,190.03),(190.44,195.6),(195.94,201.65),(202.17,205.75),(206.0,208.21),(208.59,211.5),(211.81,214.09),(214.5,221.71),(221.98,229.82),(230.43,233.37),(233.82,236.3),(236.84,238.67),(238.96,240.08),(240.26,241.36),(241.9,242.43),(242.73,243.72)]
sents=["Ele foi chamado de Rei do Cangaço.","Para a polícia, era um criminoso.","Para parte do povo do sertão, era símbolo de coragem.","Esta é a história de Lampião.",
"Virgulino Ferreira da Silva nasceu entre 1897 e 1900, em Vila Bela,","hoje Serra Talhada, em Pernambuco.",
"Era o terceiro filho de uma família de agricultores. Trabalhou como vaqueiro no sítio do pai, aprendeu a ler sem nunca ter frequentado escola e tocava sanfona nas festas da vizinhança.",
"Por volta de 1917, uma briga com o vizinho José Saturnino, que começou com acusações de roubo de animais,","mudou tudo.",
"A família vendeu o sítio e se mudou, primeiro dentro de Pernambuco,","depois para Alagoas, mas a inimizade seguiu os irmãos.",
"Eles se juntaram a cangaceiros, e foi nessa época que Virgulino passou a ser chamado de Lampião.","Entre 1920 e 1921, o pai, José Ferreira, foi morto pela volante do coronel José Lucena.","A mãe também morreu nesse período.",
"Lampião entrou no bando de Sinhô Pereira, um dos cangaceiros mais conhecidos da região.","Em 1922, quando Sinhô deixou o cangaço, aconselhado pelo Padre Cícero, Lampião assumiu o comando.",
"Foram cerca de dezesseis anos de atuação, em sete estados do Nordeste.","As volantes, polícias móveis criadas para persegui-lo, enfrentaram o bando mais de duzentas vezes.",
"Estima-se que o bando tenha matado mais de mil pessoas, além de saques e sequestros.","Os cangaceiros andavam a cavalo, vestidos de couro, e contavam com os coiteiros, que davam abrigo e comida.",
"Em março de 1926, em Juazeiro do Norte, no Ceará, Lampião recebeu do Padre Cícero a patente de capitão.","Em junho de 1927, atacou Mossoró, no Rio Grande do Norte.","A cidade estava preparada,","e ali ele sofreu a maior derrota da sua carreira.",
"Em 1930, na Bahia, Lampião conheceu Maria Gomes de Oliveira, casada com um sapateiro.","Ela fugiu com ele e foi a primeira mulher a entrar no bando.","O apelido Maria Bonita só se espalhou depois da morte dela,","por obra da imprensa.",
"Em 1932 nasceu a filha do casal, Expedita,","criada por outra família, como mandavam as regras do cangaço.","Mas o cerco se fechava.","O governo de Getúlio Vargas, no Estado Novo, decidiu acabar com os bandos que não se rendessem.",
"Na noite de 27 de julho de 1938, o bando acampou na Grota do Angico, em Sergipe,","lugar que Lampião achava seguro.","Chovia, e a volante do tenente João Bezerra chegou sem fazer barulho.","Por volta das cinco da manhã, abriu fogo com metralhadoras portáteis.",
"Em cerca de vinte minutos,","onze dos trinta e quatro cangaceiros estavam mortos.","Entre eles, Lampião e Maria Bonita.","Até hoje não se sabe ao certo quem os traiu.",
"As cabeças dos mortos foram exibidas em cidades do Nordeste e levadas para Salvador.","Só foram enterradas em 1969, mais de trinta anos depois.","Sem o líder, os outros chefes de bando acabaram se entregando,","e o cangaço terminou nos anos seguintes.",
"Surgiram teorias de que Lampião teria sobrevivido,","mas a filha, Expedita, as nega.","Ele virou tema de cordel, de filmes, como O Cangaceiro, de 1953, e até de samba-enredo:","em 2023, a Imperatriz Leopoldinense foi campeã do carnaval do Rio com um desfile inspirado em cordéis sobre ele.",
"Para as autoridades, Lampião era a brutalidade.","Para parte dos sertanejos, era bravura.","A história guarda os dois lados:","os crimes do bando","e o mito que ficou.","E você,","como se lembra dele?"]
assert len(spans)==len(sents)==55
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
MK=dict(terceiro=(6,'terceiro'),vaqueiro=(6,'vaqueiro'),sanfona=(6,'sanfona'),saturnino=(7,'Saturnino'),alagoas=(10,'Alagoas'),pai=(12,'pai'),mae=(13,'mãe'),sinho=(14,'Sinhô'),a1922=(15,'1922'),cicero=(15,'Cícero'),assumiu=(15,'assumiu'),
 dezesseis=(16,'dezesseis'),estados=(16,'estados'),volantes=(17,'volantes'),duzentas=(17,'duzentas'),mil=(18,'mil'),couro=(19,'couro'),coiteiros=(19,'coiteiros'),a1926=(20,'1926'),capitao=(20,'capitão'),a1927=(21,'1927'),
 derrota=(23,'derrota'),a1930=(24,'1930'),primeira=(25,'primeira'),bonita=(26,'Bonita'),expedita=(28,'Expedita'),cerco=(30,'cerco'),vargas=(31,'Vargas'),a1938=(32,'1938'),angico=(32,'Angico'),chovia=(34,'Chovia'),cinco=(35,'cinco'),
 vinte=(36,'vinte'),onze=(37,'onze'),trinta=(37,'trinta'),lampiao_mb=(38,'Lampião'),traiu=(39,'traiu'),cabecas=(40,'cabeças'),a1969=(41,'1969'),entregando=(42,'entregando'),teorias=(44,'teorias'),filha=(45,'filha'),
 cordel=(46,'cordel'),a1953=(46,'1953'),samba=(46,'samba'),a2023=(47,'2023'),imperatriz=(47,'Imperatriz'),autoridades=(48,'autoridades'),sertanejos=(49,'sertanejos'),bravura=(49,'bravura'),lados=(50,'lados'),crimes=(51,'crimes'),mito=(52,'mito'),voce=(53,'você'))
M={k:round(mark(*v),2) for k,v in MK.items()}
caps=[];cur=[]
for i,x in enumerate(words):
    cur.append(x)
    if re.search(r'[\.,:?]$',x['w']) or len(cur)==6 or (i+1<len(words) and words[i+1]['si']!=x['si']):
        caps.append(dict(t=cur[0]['s'],e=cur[-1]['e'],words=[dict(w=c['w'],s=c['s'],e=c['e']) for c in cur])); cur=[]
if cur: caps.append(dict(t=cur[0]['s'],e=cur[-1]['e'],words=[dict(w=c['w'],s=c['s'],e=c['e']) for c in cur]))
out=dict(fps=30,total=247.0,spans=spans,M=M,caps=caps)
json.dump(out,open('lamp.json','w'),ensure_ascii=False,indent=0); print(M)
