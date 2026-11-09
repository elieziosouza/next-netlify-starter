"""Vídeo 'As bets vão voltar?' (09/11/2026): ele em tela cheia (88% com bordas desfocadas para abrir espaço acima da cabeça),
legenda H (alto padrão), palavras gigantes acima da cabeça, barra lateral, topo, caixa fixa, zooms suaves, sons.
Uso: python3 video_bets.py SAIDA.mp4 | frames:t1,t2"""
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
words=L.words; LAST=words[-1]["e"]; END=LAST+0.42
def wt(txt,n=1):  # tempo da n-ésima ocorrência da palavra
    c=0
    for w in words:
        if re.sub(r"[^\wÀ-ú]","",w["w"]).lower()==txt:
            c+=1
            if c==n: return w["s"]
    raise SystemExit("palavra não achada: "+txt)
def clamp(x,a=0.0,b=1.0): return max(a,min(b,x))
def eo(x): x=clamp(x); return 1-(1-x)**3
def back_out(x,s=1.2): x=clamp(x)-1; return 1+(s+1)*x**3+s*x**2
ZOOMS=[(0.6,5.4,0.05),(11.0,15.4,0.05),(20.3,24.6,0.05),(30.1,33.3,0.06),(42.8,46.1,0.06),(51.5,56.0,0.05),(56.4,END,0.03)]
FIT=0.88
GIANT=[(wt("stf"),"STF",GOLD_L),(wt("proibiu"),"PROIBIU",WHITE),(wt("parar"),"PARAR",GOLD_L),(wt("muda"),"NADA MUDA",WHITE),
       (wt("prazo"),"PRAZO",GOLD_L),(wt("volta"),"NÃO VOLTA",WHITE)]
GDUR=2.1
CTA=[(16.0,19.2),(46.4,50.4)]
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
    # dourado com transparência e sem contorno (pedidos de 09/11/2026): preenchimento a 78%, sombra leve
    ImageDraw.Draw(im).text((40-b[0],40-b[1]),txt,font=f,fill=GOLD_L+(200,))
    sh=Image.new("RGBA",im.size,(0,0,0,0)); sh.putalpha(im.getchannel("A").point(lambda v:int(v*.35)))
    out=Image.new("RGBA",im.size,(0,0,0,0)); out.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)),(0,8)); out.alpha_composite(im)
    gcache[txt]=out; return out
def draw_giant(frame,t):
    for k,(t0,txt,col) in enumerate(GIANT):
        u=t-(t0-0.30)
        if u<0 or u>GDUR+0.35: continue
        im=giant_img(txt,col); side=-1 if k%2==0 else 1
        kin=eo(u/0.30); x=CX+side*(1-kin)*700; a=clamp(u/0.12)*clamp((GDUR+0.35-u)/0.35)
        sc=1.0+0.06*clamp(1-abs(u-0.30)/0.12)          # pulinho quando para (junto do clique)
        y=330-(1-clamp((GDUR+0.35-u)/0.35))*18
        img=im if sc==1 else im.resize((int(im.width*sc),int(im.height*sc)),Image.BICUBIC)
        if kin<1:                                         # rastro de movimento
            tr=img.copy(); tr.putalpha(tr.getchannel("A").point(lambda v:int(v*.25*a)))
            frame.alpha_composite(tr,(int(x-side*60-img.width/2),int(y-img.height/2)))
        if a<1: img=img.copy(); img.putalpha(img.getchannel("A").point(lambda v,a=a:int(v*a)))
        frame.alpha_composite(img,(int(x-img.width/2),int(y-img.height/2)))
def me_frame(src,t):
    z=zoom_suave.nivel(t,ZOOMS); img=zoom_suave.aplica(src,z,cy_frac=0.30)
    bg=cv2.resize(img,(W//8,H//8)); bg=cv2.GaussianBlur(bg,(0,0),4); bg=cv2.resize(bg,(W,H))
    bg=(bg.astype(np.float32)*0.72).astype(np.uint8)
    sw,sh=int(W*FIT),int(H*FIT); sm=cv2.resize(img,(sw,sh),interpolation=cv2.INTER_AREA)
    x0=CX-sw//2; y0=H-sh; out=bg.copy()
    # borda suave entre ele e o fundo
    m=np.ones((sh,sw),np.float32); f=40
    ramp=np.linspace(0,1,f); m[:,:f]*=ramp; m[:,-f:]*=ramp[::-1]; m[:f,:]*=ramp[:,None]
    reg=out[y0:y0+sh,max(0,x0):x0+sw]; xs=max(0,-x0)
    mm=m[:,xs:xs+reg.shape[1],None]; reg[:]=(sm[:,xs:xs+reg.shape[1]]*mm+reg*(1-mm)).astype(np.uint8)
    return Image.fromarray(out).convert("RGBA")
def cta_level(t): return max([clamp((t-a)/0.4)*clamp((b-t)/0.4) for a,b in CTA]+[0.0])
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
    fr.alpha_composite(CAP.overlay(t))
    kc=eo((t-1.0)/0.5)*(1 if t<LAST-1.6 else clamp((LAST-1.3-t)/0.3))
    if kc>0: BAR.lower_card(fr,"STF · BETS",["FUX SUSPENDE AÇÕES CONTRA","A PROIBIÇÃO DAS BETS"],1640,kc,fs=40)
    if t>=0.4:
        k=back_out((t-0.4)/0.55); fr.alpha_composite(top,(HDX,int(-TOPH*(1-k)))); fr.alpha_composite(bot,(HDX,int(H-bot.height+bot.height*(1-k))))
    end_overlay(fr,t)
    BAR.draw_bar(fr,clamp(t/END),"canal",eo((t-0.2)/0.6),cta_level(t),0.5+0.5*math.sin(t*5))
    return fr.convert("RGB")
def grab(t):
    raw=subprocess.run(["ffmpeg","-v","error","-ss",str(t),"-i","src.mp4","-frames:v","1","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
    return np.frombuffer(raw,np.uint8).reshape(H,W,3)
def audio(out):
    ev=[(0.2,sfx.barra(),0.16)]
    import sons
    ev+=sons.eventos(0,99)
    for t0,txt,col in GIANT: ev+=[(t0-0.32,sfx.whoosh(0.3),0.10),(t0,sfx.click(3),0.24),(t0+0.01,sfx.thud(),0.16)]
    for a,b in CTA: ev.append((a+0.05,sfx.siga(),0.14))
    ev.append((LAST-1.45,sfx.siga(),0.12))
    sfx.build(ev,END+1,"sfx_full.wav")
    subprocess.run([sys.executable,K+"/scripts/music.py","mus.wav",str(END+1)],check=True,capture_output=True)
    subprocess.run(["ffmpeg","-v","error","-y","-i","src.mp4","-i","sfx_full.wav","-i","mus.wav","-filter_complex",
      "[0:a]aresample=48000,highpass=f=80,acompressor=threshold=0.12:ratio=2.5:attack=8:release=120,asplit=2[v][vk];"
      "[2:a]volume=0.30[m];[m][vk]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=400[md];"
      f"[v][1:a][md]amix=inputs=3:normalize=0:duration=first,atrim=0:{END:.3f},afade=t=out:st={END-0.4:.3f}:d=0.4[a]",
      "-map","[a]","-c:a","pcm_s16le",out],check=True)
if __name__=="__main__":
    arg=sys.argv[1]
    if arg.startswith("frames:"):
        for ts in arg[7:].split(","):
            compose(grab(float(ts)),float(ts)).save(f"fq_{ts}.jpg",quality=88)
        sys.exit()
    audio("mix.wav")
    dec=subprocess.Popen(["ffmpeg","-v","error","-i","src.mp4","-t",f"{END:.3f}","-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
    enc=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-i","mix.wav",
        "-map","0:v","-map","1:a","-c:v","libx264","-preset","medium","-crf","17","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",arg],stdin=subprocess.PIPE)
    n=0
    while True:
        raw=dec.stdout.read(W*H*3)
        if len(raw)<W*H*3: break
        src=np.frombuffer(raw,np.uint8).reshape(H,W,3); enc.stdin.write(compose(src,n/FPS).tobytes()); n+=1
        if n%300==0: print(n,flush=True)
    enc.stdin.close(); enc.wait(); print("ok",arg,n)
