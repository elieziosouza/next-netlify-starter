"""Legenda dinâmica: palavras pequenas (Montserrat) + palavra-chave gigante (Anton dourado ou pincel), surgindo na hora da fala.
Uso: python3 legenda_dinamica.py SRC.mp4 OUT.mp4 [t_ini t_fim] | frames:t1,t2"""
import sys, json, re, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
FD="/home/user/next-netlify-starter/edicao-video/assets/fonts"
W,H,FPS=1080,1920,30; CX=int(sys.argv[3]) if False else 540; CY=1440
GOLD=(214,182,116); GOLD_L=(245,226,176); WHITE=(255,255,255); NAVY=(5,34,58)
F_SM=ImageFont.truetype(f"{FD}/Montserrat-ExtraBold.ttf",50)
F_BIG=ImageFont.truetype(f"{FD}/Anton-Regular.ttf",168)
F_BRUSH=ImageFont.truetype(f"{FD}/CaveatBrush-Regular.ttf",178)
words=json.load(open("words.json"))
KEY={"bets","stf","errado","rapidinho","setembro","proibiu","provisória","aposta","propaganda","influenciador","empresas","justiça",
"derrubar","proibição","fux","processos","inteiro","decidir","muda","proibida","atenção","prazo","congresso","validade","acabou",
"dinheiro","volta","saldo","parado","sinceramente","proibir","certo","duras","comenta","voltar","governo"}
def clean(w): return re.sub(r"[^\wÀ-ú]","",w).lower()
# agrupa: quebra na pontuação ou a cada 4 palavras
groups=[]; cur=[]
for i,w in enumerate(words):
    cur.append(i)
    if re.search(r"[\.\?\!:,]$",w["w"]) or len(cur)==4:
        groups.append(cur); cur=[]
if cur: groups.append(cur)
# junta grupos de 1 palavra pequena ao seguinte
G=[]
for g in groups:
    if G and len(G[-1])==1 and clean(words[G[-1][0]]["w"]) not in KEY and len(G[-1]+g)<=5: G[-1]=G[-1]+g
    else: G.append(g)
def hero_of(g):
    ks=[i for i in g if clean(words[i]["w"]) in KEY]
    if ks: return max(ks,key=lambda i:len(words[i]["w"]))
    return max(g,key=lambda i:len(clean(words[i]["w"])))
cache={}
def txt_img(text,font,fill,stroke,blur=8,shadow=.55):
    k=(text,id(font),fill)
    if k in cache: return cache[k]
    d=ImageDraw.Draw(Image.new("RGBA",(4,4))); b=d.textbbox((0,0),text,font=font,stroke_width=stroke)
    im=Image.new("RGBA",(b[2]-b[0]+40,b[3]-b[1]+40),(0,0,0,0))
    ImageDraw.Draw(im).text((20-b[0],20-b[1]),text,font=font,fill=fill,stroke_width=stroke,stroke_fill=NAVY+(255,))
    sh=Image.new("RGBA",im.size,(0,0,0,0)); sh.putalpha(im.getchannel("A").point(lambda v:int(v*shadow)))
    sh=sh.filter(ImageFilter.GaussianBlur(blur)); out=Image.new("RGBA",im.size,(0,0,0,0))
    out.alpha_composite(sh,(0,6)); out.alpha_composite(im); cache[k]=out; return out
def pop(t,t0,dur=.16,over=1.12):
    if t<t0: return 0
    x=min(1,(t-t0)/dur)
    return (0.6+ (over-0.6)*x/0.7) if x<0.7 else over-(over-1)*(x-0.7)/0.3
layout={}
for gi,g in enumerate(G):
    h=hero_of(g); brush=(gi%4==2)          # 1 em cada 4 palavras-chave no pincel
    pre=[i for i in g if i<h]; post=[i for i in g if i>h]
    layout[gi]=(pre,h,post,brush)
def render_overlay(t):
    base=Image.new("RGBA",(W,H),(0,0,0,0))
    gi=None
    for k,g in enumerate(G):
        s=words[g[0]]["s"]-0.05; e=(words[G[k+1][0]]["s"]-0.05) if k+1<len(G) else words[g[-1]]["e"]+0.6
        if s<=t<e: gi=k; break
    if gi is None: return base
    pre,h,post,brush=layout[gi]
    def line(ids):
        ims=[(i,txt_img(words[i]["w"].upper().strip(",.:"),F_SM,WHITE,5)) for i in ids]
        return ims
    rows=[]
    if pre: rows.append(("sm",line(pre)))
    hw=words[h]["w"].strip(",.:?!")
    hero=txt_img(hw.upper() if not brush else hw.lower(), F_BRUSH if brush else F_BIG, WHITE if brush else GOLD_L, 3 if brush else 6, 12)
    rows.append(("big",[(h,hero)]))
    if post: rows.append(("sm",line(post)))
    # altura total
    gap=-14
    hs=[max(im.height for _,im in r) for _,r in rows]; tot=sum(hs)+gap*(len(rows)-1); y=CY-tot//2
    for (kind,items),rh in zip(rows,hs):
        wsum=sum(im.width for _,im in items)-14*(len(items)-1); x=CX-wsum//2
        for i,im in items:
            sc=pop(t,words[i]["s"]-0.04, .18 if kind=="big" else .14, 1.14 if kind=="big" else 1.06)
            if sc>0:
                im2=im if abs(sc-1)<.01 else im.resize((max(1,int(im.width*sc)),max(1,int(im.height*sc))),Image.BICUBIC)
                if kind=="big" and brush: im2=im2.rotate(4,resample=Image.BICUBIC,expand=True)
                base.alpha_composite(im2,(int(x+im.width/2-im2.width/2),int(y+rh/2-im2.height/2)))
            x+=im.width-14
        y+=rh+gap
    return base
if __name__=="__main__":
    src,out=sys.argv[1],sys.argv[2]
    if out.startswith("frames:"):
        for ts in out[7:].split(","):
            t=float(ts); fr=subprocess.run(["ffmpeg","-v","error","-ss",ts,"-i",src,"-frames:v","1","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
            im=Image.frombytes("RGB",(W,H),fr).convert("RGBA"); im.alpha_composite(render_overlay(t)); im.convert("RGB").save(f"q_{ts}.jpg",quality=88)
        sys.exit()
    t0=float(sys.argv[3]) if len(sys.argv)>3 else 0; t1=float(sys.argv[4]) if len(sys.argv)>4 else words[-1]["e"]+1.5
    dec=subprocess.Popen(["ffmpeg","-v","error","-ss",str(t0),"-t",str(t1-t0),"-i",src,"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
    enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-ss",str(t0),"-t",str(t1-t0),"-i",src,
        "-map","0:v","-map","1:a","-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart",out],stdin=subprocess.PIPE)
    n=0
    while True:
        fr=dec.stdout.read(W*H*3)
        if len(fr)<W*H*3: break
        t=t0+n/FPS; im=Image.frombytes("RGB",(W,H),fr).convert("RGBA"); im.alpha_composite(render_overlay(t))
        enc.stdin.write(im.convert("RGB").tobytes()); n+=1
    enc.stdin.close(); enc.wait(); print("ok",out,n)
