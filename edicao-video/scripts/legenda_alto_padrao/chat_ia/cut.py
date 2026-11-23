"""Corte limpo + tempo das palavras (conversa com o ChatGPT, 23/11/2026). Gera src.mp4, words.json, cuts.json."""
import wave, json, re, subprocess, numpy as np
N=".."
SEGS=[
(0.15,2.50,[("E","E aí, Chat, beleza? Vamos trocar uma ideia?")]),
(3.65,5.05,[("A","Vamos, claro. Manda.")]),
(5.95,17.45,[("E","Deixa eu te perguntar uma coisa aqui, só para saber mesmo, né? Essa negociação aí dessa guerra na Rússia com a Ucrânia."),("E","Pode dar B.O. pra mim? Eu posso ser chamado para ir para a guerra?")]),
(19.05,20.55,[("A","Vamos ver com calma, já te falo.")]),
(28.65,37.50,[("A","Você não vai ser convocado para lutar na guerra entre Rússia e Ucrânia, só porque o Brasil se envolveu diplomaticamente ou porque o conflito existe.")]),
(47.15,56.25,[("A","Segundo, pela lei do serviço militar, em tempo de paz, a obrigação vai só até 45 anos. Você já tem 47, então está fora do limite normal.")]),
(70.20,78.15,[("E","Poxa, mas aí você me queima. Você vai falar que eu tenho 47 anos, aí você me queima.")]),
(79.95,90.45,[("A","Não tem problema nenhum falar da idade, não muda nada pra você. Pelo contrário, só confirma que você está fora do limite de obrigação normal.")]),
(90.78,95.85,[("E","Não, tipo assim, depois vão ficar me chamando de tiozinho.")]),
(97.26,100.20,[("A","Ah, isso é só brincadeira, não muda nada na vida real.")]),
(104.15,110.85,[("E","E é que você sabe como é, né, Chat? Natal tá chegando aí, a gente quer estar em casa.")]),
(112.15,121.20,[("A","Exatamente, melhor é ficar de boa planejando a festa de fim de ano, nada de preocupação com guerra, tá tudo certo. Quer que a gente fale de um assunto mais leve?")]),
(123.50,135.90,[("E","Eu tenho uma preocupação com isso, né? Venezuela está aqui pertinho, dependendo do Trump vir aqui para o Brasil para invadir, não sei.")]),
(137.60,141.80,[("A","Vamos por partes."),("E","Bem rapidinho. O que você acha disso?")]),
(172.40,191.70,[("A","Sobre o Brasil, a tensão diplomática e o próprio Ministério das Relações Exteriores chegou a alertar para riscos em certos momentos, mas até as informações mais recentes não há confirmação de plano americano de invadir o Brasil."),("E","Mas você acha, Chat, que o Trump vai vir aqui buscar o Lula também?")]),
(193.55,195.10,[("A","Vamos olhar com calma.")]),
(197.27,210.30,[("A","Agora você foi direto ao ponto. Você está perguntando se o Trump poderia fazer com o Lula o que fez com o Maduro, mandando militares e levando à força. Minha resposta é: não há evidências de que Trump esteja planejando fazer isso com o Lula.")]),
(211.37,229.48,[("A","Mas Trump já mostrou que usa força militar, como na operação da Venezuela. Existe tensão entre os governos, mas também notícias falsas circulando, até rolar a expectativa de encontro bilateral no G20. Minha leitura é que não temos elementos para afirmar que os Estados Unidos pretendem capturar o Lula ou invadir o Brasil.")]),
(240.58,244.70,[("E","É isso aí, gente. Eu preciso saber se eu posso comprar o peru para o Natal ou não.")]),
(246.71,256.30,[("A","Pode comprar o peru tranquilo, prepare-se e planeje a confraternização. Não tem cenário realista que exija preocupação com guerra chegando na sua porta. Fica em paz.")]),
(256.68,265.20,[("E","Tá bom, então, Chat. Tá bom então, obrigado aí. Boa noite."),("A","Valeu, uma boa noite."),("E","Agora eu tô bem mais tranquilo.")]),
]
PADS,PADE=0.06,0.10
w=wave.open(f"{N}/a16.wav"); a=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
rms=np.sqrt(np.convolve(a**2,np.ones(480)/480,'same'))[::160]; db=20*np.log10(rms+1e-6); VAD=db>(-55.9+9+3)
def wt(x): return max(len(re.sub(r"[^\wÀ-ú]","",x)),2)+1.2
words=[]; cuts=[]; off=0.0
for s,e,sents in SEGS:
    cs,ce=s-PADS,e+PADE; ce=cs+round((ce-cs)*30)/30; cuts.append((cs,ce,off))
    i0,i1=int(s*100),int(e*100); v=VAD[i0:i1].astype(float); cum=np.concatenate([[0],np.cumsum(v)]); S=cum[-1]
    ws=[]; 
    for spk,txt in sents:
        for x in txt.split(): ws.append((spk,x))
    W=[wt(x) for _,x in ws]; T=sum(W); c=0.0
    for (spk,x),wx in zip(ws,W):
        a0=c/T*S; a1=(c+wx)/T*S; c+=wx
        t0=np.searchsorted(cum,a0+0.001)/100+s; t1=np.searchsorted(cum,a1)/100+s
        t0=max(t0,s); t1=max(t1,t0+0.08)
        words.append(dict(w=x,s=round(t0-cs+off,3),e=round(t1-cs+off,3),spk=spk))
    off+=ce-cs
json.dump(words,open("words.json","w"),ensure_ascii=False); json.dump(cuts,open("cuts.json","w"))
print("duração",round(off,1),"palavras",len(words))
import os
os.makedirs("seg",exist_ok=True); lst=[]
for i,(cs,ce,_) in enumerate(cuts):
    f=f"seg/s{i:02d}.mkv"; d=ce-cs
    subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{cs:.3f}","-t",f"{d:.3f}","-i",f"{N}/img3130.mov","-vf","fps=30","-frames:v",str(round(d*30)),"-af",f"afade=t=in:d=0.02,afade=t=out:st={d-0.03:.3f}:d=0.03,aresample=48000","-c:v","libx264","-preset","fast","-crf","12","-pix_fmt","yuv420p","-c:a","pcm_s16le",f],check=True)
    lst.append(f"file '{f}'")
open("list.txt","w").write("\n".join(lst))
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i","list.txt","-af","highpass=f=70,loudnorm=I=-18:TP=-2:LRA=10","-ar","48000","-c:v","copy","-c:a","aac","-b:a","256k","src.mp4"],check=True)
print("ok")
