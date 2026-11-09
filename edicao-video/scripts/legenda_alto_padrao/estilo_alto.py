"""Estilo H 'alto padrão': apoio em Playfair Display fina branca; palavra-chave em Poppins Bold dourado do canal
ou, 1 em cada 3, em Poppins ExtraLight branca grande; filete dourado fino abrindo do centro sob a palavra-chave."""
import sys, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np
import legenda_dinamica as L
FD=L.FD; W,H=1080,1920; CX=540; CY=1500; MAXW=780  # o vídeo final troca CX, CY e MAXW; MAXW=780
WHITE=(250,248,244); GOLD=(222,196,138)
SIGLAS={"STF","PGR","MP"}
def font(n,s): return ImageFont.truetype(f"{FD}/{n}.ttf",s)
cache={}
def word_img(text,fname,size,track,fill):
    k=(text,fname,size,track,fill)
    if k in cache: return cache[k]
    fn=font(fname,size); asc,desc=fn.getmetrics(); ws=[fn.getlength(c) for c in text]
    im=Image.new("RGBA",(int(sum(ws)+track*(len(text)-1))+40,asc+desc+30),(0,0,0,0)); d=ImageDraw.Draw(im); x=20
    for c,wc in zip(text,ws): d.text((x,10),c,font=fn,fill=fill); x+=wc+track
    sh=Image.new("RGBA",im.size,(0,0,0,0)); sh.putalpha(im.getchannel("A").point(lambda v:int(v*.72)))
    out=Image.new("RGBA",im.size,(0,0,0,0)); out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)),(0,5)); out.alpha_composite(im)
    cache[k]=(out,asc); return cache[k]
def clean(i):
    w=L.words[i]["w"].strip(",.:?!"); return w if w.upper() in SIGLAS else w.lower()
def ease(x): x=max(0,min(1,x)); return 1-(1-x)**3
def filete(width,a):
    w=max(2,int(width*a)); x=np.linspace(-1,1,w); al=(np.clip(1-np.abs(x)**3,0,1)*235).astype(np.uint8)
    im=Image.new("RGBA",(w,3),GOLD+(0,)); im.putalpha(Image.fromarray(np.tile(al,(3,1)))); return im
def overlay(t):
    base=Image.new("RGBA",(W,H),(0,0,0,0)); k=None
    for j,g in enumerate(L.G):
        s=L.words[g[0]]["s"]-0.05; e=(L.words[L.G[j+1][0]]["s"]-0.05) if j+1<len(L.G) else L.words[g[-1]]["e"]+0.6
        if s<=t<e: k=j; break
    if k is None: return base
    pre,h,post,_=L.layout[k]; thin=(k%3==1)
    def build(ids,fname,size,track,fill):
        parts=[(i,)+word_img(clean(i),fname,size,track,fill) for i in ids]; sp=size*.24
        return parts,sum(p[1].width-40 for p in parts)+sp*(len(parts)-1),sp
    rows=[]
    if pre:
        s=80
        while True:
            parts,wsum,sp=build(pre,"PlayfairDisplay-Regular",s,0,WHITE)
            if wsum<=MAXW or s<50: break
            s-=4
        rows.append(("pre",parts,wsum,sp,s))
    s=186 if thin else 172
    while True:
        parts,wsum,sp=(build([h],"Poppins-ExtraLight",s,s*.01,WHITE) if thin else build([h],"Poppins-Bold",s,-s*.06,GOLD))
        if wsum<=MAXW+40 or s<90: break
        s-=8
    rows.append(("hero",parts,wsum,sp,s))
    if post:
        s=62
        while True:
            parts,wsum,sp=build(post,"PlayfairDisplay-Regular",s,0,WHITE)
            if wsum<=MAXW or s<40: break
            s-=4
        rows.append(("post",parts,wsum,sp,s))
    lh=[r[4]*(0.95 if r[0]!="hero" else 0.92) for r in rows]; tot=sum(lh)+22; y=CY-tot/2
    for (kind,parts,wsum,sp,s),hh in zip(rows,lh):
        x=CX-wsum/2
        for i,im,asc in parts:
            t0=L.words[i]["s"]-0.04; a=ease((t-t0)/(0.24 if kind=="hero" else 0.16))
            if a>0:
                sc=1+(0.08 if kind=="hero" else 0.0)*(1-a); dy=(1-a)*(14 if kind!="hero" else 6)
                im2=im if sc==1 else im.resize((int(im.width*sc),int(im.height*sc)),Image.BICUBIC)
                if a<1: al=im2.getchannel("A").point(lambda v,a=a:int(v*a)); im2=im2.copy(); im2.putalpha(al)
                base.alpha_composite(im2,(int(x-20-(im2.width-im.width)/2),int(y-10-asc*0.22+dy-(im2.height-im.height)/2)))
            x+=im.width-40+sp
        if kind=="hero":
            t0=L.words[parts[0][0]]["s"]+0.05; a=ease((t-t0)/0.35)
            asc0=parts[0][2]
            if a>0: f=filete(int(wsum*0.62),a); base.alpha_composite(f,(int(CX-f.width/2),int(y-asc0*0.22+asc0+s*0.30)))
            y+=s*0.30
        y+=hh
    return base
if __name__=="__main__":
    ims=[]
    for t in [1.6,3.6,6.6,10.6,12.9,14.9]:
        fr=subprocess.run(["ffmpeg","-v","error","-ss",str(t),"-i","src.mp4","-frames:v","1","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
        im=Image.frombytes("RGB",(W,H),fr).convert("RGBA"); im.alpha_composite(overlay(t)); ims.append(im.convert("RGB").resize((360,640)))
    m=Image.new("RGB",(1080,1280))
    for i,im in enumerate(ims): m.paste(im,((i%3)*360,(i//3)*640))
    m.save("estiloH.jpg",quality=86)
