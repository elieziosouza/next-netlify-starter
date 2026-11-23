"""Vídeo 'Conversa com o ChatGPT: posso ser chamado pra guerra?' (23/11/2026), padrão do canal (ele em tela cheia a 88%, legenda alto padrão, palavras gigantes
acima da cabeça, barra lateral, topo, caixa fixa, zooms suaves, sons). Respostas da IA levam a etiqueta CHATGPT.
Uso: python3 video_chat.py SAIDA.mp4 | frames:t1,t2"""
import sys, math, subprocess, re, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
K="/home/user/next-netlify-starter/edicao-video"; sys.path.insert(0,K+"/scripts")
import zoom_suave, sfx
import barra_lateral as BAR
from minitop import make_minitop, make_minifooter, handles_row
import legenda_dinamica as L
import estilo_alto as CAP
FD=K+"/assets/fonts"; BAR.FD=FD
W,H,FPS=1080,1920,30; CX=582
CAP.CX=CX; CAP.CY=1340; CAP.MAXW=660
GOLD=(214,182,116); GOLD_L=(245,226,176); NAVY=(6,34,58); WHITE=(255,255,255)
words=L.words; LAST=170.72; END=171.17   # fim real da voz, medido em src.mp4
cuts=json.load(open("cuts.json"))
def clean(x): return re.sub(r"[^\wÀ-ú]","",x).lower()
def wt(txt,n=1):
    c=0
    for w in words:
        if clean(w["w"])==txt:
            c+=1
            if c==n: return w["s"]
    raise SystemExit("palavra não achada: "+txt)
def clamp(x,a=0.0,b=1.0): return max(a,min(b,x))
def eo(x): x=clamp(x); return 1-(1-x)**3
def back_out(x,s=1.2): x=clamp(x)-1; return 1+(s+1)*x**3+s*x**2
# zooms: falas dele (E) a 5%; respostas longas da IA a 3% bem lento
runs=[]; cur=None
for w in words:
    if cur and cur["spk"]==w["spk"] and w["s"]-cur["e"]<0.9: cur["e"]=w["e"]
    else:
        if cur: runs.append(cur)
        cur=dict(spk=w["spk"],s=w["s"],e=w["e"])
runs.append(cur)
ZOOMS=[]
for r in runs:
    d=r["e"]-r["s"]
    if r["spk"]=="E" and d>=2.2: ZOOMS.append((r["s"]-0.1,r["e"]+0.1,0.05))
    elif r["spk"]=="A" and d>=6: ZOOMS.append((r["s"]+0.5,r["e"],0.03))
FIT=0.88; IMG_CX=530; ZCX=0.70
GIANT=[(wt("bo"),"B.O.?",GOLD_L),(wt("convocado"),"CONVOCADO",WHITE),(wt("47",2),"47 ANOS",GOLD_L),(wt("tiozinho"),"TIOZINHO",WHITE),(wt("natal"),"NATAL",GOLD_L),
       (wt("venezuela"),"VENEZUELA",WHITE),(wt("lula"),"LULA?",GOLD_L),(wt("evidências"),"SEM EVIDÊNCIAS",WHITE),(wt("peru"),"PERU?",GOLD_L)]
GDUR=2.1
CTA=[(62.0,65.5),(118.0,121.5)]
ASS=[cuts[i][2] for i in (12,14,16,19)]
top,TOPH=make_minitop(W,f"{FD}/Montserrat-SemiBold.ttf"); bot,_=make_minifooter(W,f"{FD}/Montserrat-SemiBold.ttf")
HROW=handles_row(W,f"{FD}/Montserrat-SemiBold.ttf",size=25,isz=28)
HDX=42
def MF(w,s): return ImageFont.truetype(f"{FD}/Montserrat-{w}.ttf",s)
gcache={}
def giant_img(txt,col):
    if txt in gcache: return gcache[txt]
    s=260
    while True:
        f=ImageFont.truetype(f"{FD}/Anton-Regular.ttf",s); b=f.getbbox(txt)
        if b[2]-b[0]<=640 and b[3]-b[1]<=250: break
        s-=8
    im=Image.new("RGBA",(b[2]-b[0]+80,b[3]-b[1]+80),(0,0,0,0))
    ImageDraw.Draw(im).text((40-b[0],40-b[1]),txt,font=f,fill=GOLD_L+(155,))
    sh=Image.new("RGBA",im.size,(0,0,0,0)); sh.putalpha(im.getchannel("A").point(lambda v:int(v*.55)))
    out=Image.new("RGBA",im.size,(0,0,0,0)); out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)),(0,8)); out.alpha_composite(im)
    gcache[txt]=out; return out
def draw_giant(frame,t):
    for k,(t0,txt,col) in enumerate(GIANT):
        u=t-(t0-0.30)
        if u<0 or u>GDUR+0.35: continue
        im=giant_img(txt,col); side=-1 if k%2==0 else 1
        kin=eo(u/0.30); x=CX+side*(1-kin)*700; a=clamp(u/0.12)*clamp((GDUR+0.35-u)/0.35)
        sc=1.0+0.06*clamp(1-abs(u-0.30)/0.12)
        y=330-(1-clamp((GDUR+0.35-u)/0.35))*18
        img=im if sc==1 else im.resize((int(im.width*sc),int(im.height*sc)),Image.BICUBIC)
        if kin<1:
            tr=img.copy(); tr.putalpha(tr.getchannel("A").point(lambda v:int(v*.25*a)))
            frame.alpha_composite(tr,(int(x-side*60-img.width/2),int(y-img.height/2)))
        if a<1: img=img.copy(); img.putalpha(img.getchannel("A").point(lambda v,a=a:int(v*a)))
        frame.alpha_composite(img,(int(x-img.width/2),int(y-img.height/2)))
def zaplica(img,z,cy_frac=0.30):
    if z<=0.0005: return img
    h,w=img.shape[:2]; sc=1+z; cx,cy=w*ZCX,h*cy_frac
    M=np.float32([[sc,0,cx-cx*sc],[0,sc,cy-cy*sc]])
    return cv2.warpAffine(img,M,(w,h),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
def me_frame(src,t):
    z=zoom_suave.nivel(t,ZOOMS); img=zaplica(src,z)
    bg=cv2.resize(img,(W//8,H//8)); bg=cv2.GaussianBlur(bg,(0,0),4); bg=cv2.resize(bg,(W,H))
    bg=(bg.astype(np.float32)*0.72).astype(np.uint8)
    sw,sh=int(W*FIT),int(H*FIT); sm=cv2.resize(img,(sw,sh),interpolation=cv2.INTER_AREA)
    x0=IMG_CX-sw//2; y0=H-sh; out=bg.copy()
    m=np.ones((sh,sw),np.float32); f=40
    ramp=np.linspace(0,1,f); m[:,:f]*=ramp; m[:,-f:]*=ramp[::-1]; m[:f,:]*=ramp[:,None]
    reg=out[y0:y0+sh,max(0,x0):x0+sw]; xs=max(0,-x0)
    mm=m[:,xs:xs+reg.shape[1],None]; reg[:]=(sm[:,xs:xs+reg.shape[1]]*mm+reg*(1-mm)).astype(np.uint8)
    return Image.fromarray(out).convert("RGBA")
def cta_level(t): return max([clamp((t-a)/0.4)*clamp((b-t)/0.4) for a,b in CTA]+[0.0])
def tag_chat(frame,t):
    """etiqueta CHATGPT sobre a legenda quando a fala é da IA"""
    k=None
    for j,g in enumerate(L.G):
        s=words[g[0]]["s"]-0.05; e=(words[L.G[j+1][0]]["s"]-0.05) if j+1<len(L.G) else words[g[-1]]["e"]+0.6
        if s<=t<e: k=(j,s); break
    if k is None or words[L.G[k[0]][0]]["spk"]!="A": return
    a=eo((t-k[1])/0.2)
    f=MF("ExtraBold",29); txt="CHATGPT"; tw=int(f.getlength(" ".join(txt)))+56; hh=50
    lay=Image.new("RGBA",(tw+4,hh+4),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.rounded_rectangle((2,2,tw+1,hh+1),hh//2,fill=NAVY+(205,),outline=GOLD+(255,),width=2)
    d.text(((tw+4)/2,(hh+4)/2+1)," ".join(txt),font=f,fill=GOLD_L+(255,),anchor="mm")
    lay.putalpha(lay.getchannel("A").point(lambda v:int(v*a)))
    frame.alpha_composite(lay,(int(CX-lay.width/2),int(1140+(1-a)*10)))
def end_overlay(frame,t):
    u=t-(LAST-1.45)
    if u<0: return
    d=ImageDraw.Draw(frame); cy=330
    k1=eo(u/0.45)
    if k1>0:
        lay=Image.new("RGBA",(W,H),(0,0,0,0)); dd=ImageDraw.Draw(lay)
        dd.text((CX,cy-60+14*(1-k1)),"SIGA PARA MAIS",font=MF("ExtraBold",50),fill=WHITE+(int(255*k1),),anchor="mm",stroke_width=4,stroke_fill=NAVY+(int(200*k1),))
        lw=int(140*eo((u-0.2)/0.5))
        if lw>0: dd.rectangle((CX-lw,cy-14,CX+lw,cy-12),fill=GOLD+(255,))
        frame.alpha_composite(lay)
    k2=eo((u-0.35)/0.45)
    if k2>0:
        hr=HROW.copy(); hr.putalpha(hr.getchannel("A").point(lambda v:int(v*k2))); frame.alpha_composite(hr,(int(CX-hr.width/2),cy+6))
def compose(src,t):
    fr=me_frame(src,t)
    draw_giant(fr,t)
    fr.alpha_composite(CAP.overlay(t)); tag_chat(fr,t)
    kc=eo((t-1.0)/0.5)*(1 if t<LAST-1.6 else clamp((LAST-1.3-t)/0.3))
    if kc>0: BAR.lower_card(fr,"CONVERSA COM O CHATGPT",["POSSO IR PRA GUERRA?","RESPOSTAS DA IA"],1640,kc,fs=40)
    if t>=0.4:
        k=back_out((t-0.4)/0.55); fr.alpha_composite(top,(HDX,int(-TOPH*(1-k)))); fr.alpha_composite(bot,(HDX,int(H-bot.height+bot.height*(1-k))))
    end_overlay(fr,t)
    BAR.draw_bar(fr,clamp(t/END),"canal",eo((t-0.2)/0.6),cta_level(t),0.5+0.5*math.sin(t*5))
    return fr.convert("RGB")
def grab(t):
    raw=subprocess.run(["ffmpeg","-v","error","-ss",str(t),"-i","src.mp4","-frames:v","1","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
    return np.frombuffer(raw,np.uint8).reshape(H,W,3)
def audio(out):
    import sons
    sons.ASSUNTO=ASS
    ev=[(0.2,sfx.barra(),0.16)]
    ev+=sons.eventos(0,999)
    for t0,txt,col in GIANT: ev+=[(max(0.03,t0-0.32),sfx.whoosh(0.3),0.10),(max(0.05,t0),sfx.click(3),0.24),(max(0.06,t0+0.01),sfx.thud(),0.16)]
    for a,b in CTA: ev.append((a+0.05,sfx.siga(),0.14))
    ev.append((LAST-1.45,sfx.siga(),0.12))
    ev=[(max(0.02,t),sg,g) for t,sg,g in ev]
    sfx.build(ev,END+1,"sfx_full.wav")
    subprocess.run([sys.executable,K+"/scripts/music.py","mus.wav",str(END+1)],check=True,capture_output=True)
    subprocess.run(["ffmpeg","-v","error","-y","-i","src.mp4","-i","sfx_full.wav","-i","mus.wav","-filter_complex",
      "[0:a]aresample=48000,asplit=2[v][vk];"
      "[2:a]volume=0.22[m];[m][vk]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[md];"
      f"[v][1:a][md]amix=inputs=3:normalize=0:duration=longest,atrim=0:{END:.3f},afade=t=out:st={END-0.4:.3f}:d=0.4[a]",
      "-map","[a]","-c:a","pcm_s16le",out],check=True)
if __name__=="__main__":
    arg=sys.argv[1]
    if arg.startswith("frames:"):
        for ts in arg[7:].split(","):
            compose(grab(float(ts)),float(ts)).save(f"fq_{ts}.jpg",quality=88)
        sys.exit()
    T0=float(sys.argv[2]) if len(sys.argv)>2 else 0.0
    if T0==0: audio("mix.wav")
    dec=subprocess.Popen(["ffmpeg","-v","error","-ss",str(T0),"-i","src.mp4","-t",f"{END-T0:.3f}","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
    enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-"]+
        (["-an"] if T0 else ["-i","mix.wav","-map","0:v","-map","1:a","-c:a","aac","-b:a","192k","-shortest"])+
        ["-c:v","libx264","-preset","medium","-crf","17","-pix_fmt","yuv420p","-movflags","+faststart",arg],stdin=subprocess.PIPE)
    n=0
    while True:
        raw=dec.stdout.read(W*H*3)
        if len(raw)<W*H*3: break
        src=np.frombuffer(raw,np.uint8).reshape(H,W,3); enc.stdin.write(compose(src,T0+n/FPS).tobytes()); n+=1
        if n%300==0: print(n,flush=True)
    enc.stdin.close(); enc.wait(); print("ok",arg,n)
