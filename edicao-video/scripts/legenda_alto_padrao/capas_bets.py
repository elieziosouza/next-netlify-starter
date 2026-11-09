"""Capas do 'As bets vão voltar?' (09/11/2026): A e B com o rosto dele, C sem o rosto. Só o que as fontes confirmam:
Fux suspendeu as ações contra a proibição até o STF julgar; as bets seguem proibidas."""
import sys, subprocess, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
K="/home/user/next-netlify-starter/edicao-video"; sys.path.insert(0,K+"/scripts"); FD=K+"/assets/fonts"
import barra_lateral as BAR; BAR.FD=FD
from minitop import make_minitop
W,H=1080,1920; CX=582
GOLD=(214,182,116); GOLD_L=(245,226,176); NAVY=(6,34,58); WHITE=(255,255,255); RED=(206,34,40)
def MF(w,s): return ImageFont.truetype(f"{FD}/Montserrat-{w}.ttf",s)
top,_=make_minitop(W,f"{FD}/Montserrat-SemiBold.ttf")
def grab(t):
    raw=subprocess.run(["ffmpeg","-v","error","-ss",str(t),"-i","src.mp4","-frames:v","1","-f","rawvideo","-pix_fmt","rgb24","-"],capture_output=True).stdout
    return np.frombuffer(raw,np.uint8).reshape(H,W,3)
def base_me(t,shift=170,zoom=1.0):
    fr=grab(t); sc=zoom; M=np.float32([[sc,0,CX-540*sc],[0,sc,shift]])
    img=cv2.warpAffine(fr,M,(W,H),flags=cv2.INTER_LANCZOS4,borderMode=cv2.BORDER_REFLECT).astype(np.float32)
    g=np.clip((np.arange(H)-1000)/520,0,1)**1.3; navy=np.array([4,16,30],np.float32)
    img=img*(1-g[:,None,None]*0.92)+navy*(g[:,None,None]*0.92)
    return Image.fromarray(np.clip(img,0,255).astype(np.uint8)).convert("RGBA")
def navy_bg():
    yy,xx=np.mgrid[0:H,0:W]; r=np.sqrt(((xx-CX)/W)**2+((yy-H*0.42)/H)**2)
    c=np.array([2,8,18],np.float32)+np.array([9,40,72],np.float32)*np.clip(1-r*1.9,0,1)[...,None]
    return Image.fromarray(c.astype(np.uint8)).convert("RGBA")
def text(img,txt,cy,font,col=WHITE,stroke=8,maxw=680):
    f=font; size=f.size
    while f.getlength(txt)>maxw: size-=4; f=f.font_variant(size=size)
    lay=Image.new("RGBA",(W,int(size*1.6)),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.text((CX,lay.height/2),txt,font=f,fill=col+(255,),anchor="mm",stroke_width=stroke,stroke_fill=NAVY+(255,))
    sh=lay.copy(); sh.putalpha(sh.getchannel("A").point(lambda v:int(v*.6))); sh=sh.filter(ImageFilter.GaussianBlur(14))
    img.alpha_composite(sh,(0,int(cy-lay.height/2+10))); img.alpha_composite(lay,(0,int(cy-lay.height/2)))
def tag(img,txt,cy):
    f=MF("ExtraBold",34); tw=f.getlength(txt)+60; d=ImageDraw.Draw(img)
    d.rounded_rectangle((CX-tw/2,cy-30,CX+tw/2,cy+30),10,fill=GOLD+(255,)); d.text((CX,cy+1),txt,font=f,fill=NAVY+(255,),anchor="mm")
def stamp(img,txt,cy,size=92,rot=-3,col=RED):
    f=MF("Black",size)
    while f.getlength(txt)>620: size-=4; f=MF("Black",size)
    tw=f.getlength(txt); lay=Image.new("RGBA",(int(tw+90),int(size*1.55)),(0,0,0,0)); d=ImageDraw.Draw(lay)
    d.rounded_rectangle((6,6,lay.width-7,lay.height-7),16,fill=col+(255,),outline=WHITE+(255,),width=6)
    d.text((lay.width/2,lay.height/2+3),txt,font=f,fill=WHITE+(255,),anchor="mm"); lay=lay.rotate(rot,resample=Image.BICUBIC,expand=True)
    sh=Image.new("RGBA",lay.size,(0,0,0,0)); sh.putalpha(lay.getchannel("A").point(lambda v:int(v*.5))); sh=sh.filter(ImageFilter.GaussianBlur(16))
    img.alpha_composite(sh,(int(CX-lay.width/2),int(cy-lay.height/2+14))); img.alpha_composite(lay,(int(CX-lay.width/2),int(cy-lay.height/2)))
def filete(img,cy,w=300):
    d=ImageDraw.Draw(img); d.rectangle((CX-w/2,cy,CX+w/2,cy+3),fill=GOLD+(255,))
def finish(img):
    BAR.draw_bar(img,0.0,"canal"); img.alpha_composite(top,(42,0)); return img.convert("RGB")
A=base_me(1.9); tag(A,"STF  ·  BETS",1170); text(A,"AS BETS",1290,MF("Black",130)); text(A,"VÃO VOLTAR?",1430,MF("Black",130),GOLD_L)
stamp(A,"ENTENDA EM 1 MINUTO",1590,70); finish(A).save("capa_A.jpg",quality=95)
B=base_me(0.9); tag(B,"DECISÃO DO STF",1170); text(B,"BET CONTINUA",1290,MF("Black",118)); stamp(B,"PROIBIDA?",1450,120)
filete(B,1560); text(B,"O QUE MUDA PRA VOCÊ",1620,MF("ExtraBold",58),WHITE,5); finish(B).save("capa_B.jpg",quality=95)
C=navy_bg(); tag(C,"STF  ·  BETS",470); text(C,"AS BETS",640,MF("Black",190)); text(C,"VÃO VOLTAR?",830,MF("Black",150),GOLD_L)
filete(C,960,360); text(C,"FUX SUSPENDEU AS AÇÕES",1060,MF("ExtraBold",60),WHITE,4); text(C,"CONTRA A PROIBIÇÃO",1140,MF("ExtraBold",60),WHITE,4)
stamp(C,"O QUE MUDA?",1330,120); finish(C).save("capa_C.jpg",quality=95)
sheet=Image.new("RGB",(1080,640)); [sheet.paste(Image.open(f"capa_{k}.jpg").resize((360,640)),(i*360,0)) for i,k in enumerate("ABC")]
sheet.save("capas_ABC.jpg",quality=90); print("ok")
