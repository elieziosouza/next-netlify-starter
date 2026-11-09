import sys, re, json, numpy as np
sys.path.insert(0,"/home/user/next-netlify-starter/edicao-video/scripts")
import sfx
import legenda_dinamica as L
IMPACTO={"muda","proibida","volta","errado","validade","acabou"}
ASSUNTO=[7.15,15.6,29.15,33.45,42.75,51.5]   # trocas de assunto (início de frase)
def eventos(t0=0,t1=99):
    ev=[]; last=-9
    for k,g in enumerate(L.G):
        pre,h,post,_=L.layout[k]; w=re.sub(r"[^\wÀ-ú]","",L.words[h]["w"]).lower(); ts=L.words[h]["s"]-0.04
        if w in IMPACTO: ev.append((ts,sfx.thud(),0.22)); ev.append((ts,sfx.click(5),0.20)); last=ts
        elif w in L.KEY and ts-last>=1.4: ev.append((ts,sfx.click(11+k%3),0.20)); last=ts
    for a in ASSUNTO: ev.append((a-0.22,sfx.whoosh(0.32),0.10))
    return [(t-t0,s,g) for t,s,g in ev if t0<=t<t1]
if __name__=="__main__":
    t0,t1,out=float(sys.argv[1]),float(sys.argv[2]),sys.argv[3]
    ev=eventos(t0,t1); sfx.build(ev,t1-t0,out); print(len(ev),"sons")
