import json, subprocess, sys
sys.path.insert(0, '.')
from motor import F, RED, WHITE, GREY, logo, tw
from PIL import Image, ImageDraw

SRC = 'entrega/Overdrawn Files - Ground Stop EUA - VIDEO PRINCIPAL.mp4'
SHORTS = [
    ('1', 'REEMBOLSO', 320.55, 376.3, ['FLIGHT CANCELED?', '!THE AIRLINE OWES', '!YOU CASH']),
    ('2', 'TODOS OS VOOS PARADOS', 0.0, 48.3, ['EVERY U.S.', 'FLIGHT', '!JUST STOPPED']),
    ('3', 'QUANTO CUSTA', 214.55, 272.2, ['WHAT DOES ONE', 'DAY OF THIS', '!REALLY COST?']),
]
segs = json.load(open('audio/segs.json'))
fixes = {'cruise.': 'crews.', 'Plains': 'Planes', 'can safely': "can't safely", 'networked': 'network',
         'Mark Wayne Mullen': 'Markwayne Mullin', 'significantly change means': 'significantly changed means', 'or cancel.': 'or canceled.', 'Microsoft Outage': 'Microsoft outage'}

def ass_time(x):
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def make_ass(t0, t1, path):
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Montserrat ExtraBold,104,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,9,0,8,60,60,1320,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    for s in segs:
        if s['end'] <= t0 or s['start'] >= t1:
            continue
        txt = s['text']
        for a, b in fixes.items():
            txt = txt.replace(a, b)
        words = txt.split()
        a, b = max(s['start'], t0) - t0, min(s['end'], t1) - t0
        chunks = [words[i:i + 3] for i in range(0, len(words), 3)]
        for k, ch in enumerate(chunks):
            cs = a + (b - a) * k / len(chunks); ce = a + (b - a) * (k + 1) / len(chunks)
            line = ' '.join(ch).upper()
            ev.append(f"Dialogue: 0,{ass_time(cs)},{ass_time(ce)},Cap,,0,0,0,,{{\\fad(40,0)}}{line}")
    open(path, 'w').write(head + '\n'.join(ev) + '\n')

def make_top(lines, path):
    im = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    logo(im, 90, 150, 26, 1.0, 5)
    d.text((132, 150), 'OVERDRAWN FILES', font=F('xbold', 32), fill=WHITE, anchor='lm')
    f = F('black', 96)
    y = 250
    for ln in lines:
        c = RED if ln.startswith('!') else WHITE
        s = ln.lstrip('!')
        size = 96
        while tw(s, F('black', size)) > 960:
            size -= 4
        d.text((540, y), s, font=F('black', size), fill=c, anchor='ma', stroke_width=6, stroke_fill=(0, 0, 0))
        y += int(size * 1.12)
    d.text((540, 1760), 'FULL STORY ON THE CHANNEL', font=F('xbold', 34), fill=GREY, anchor='mm')
    im.save(path)

for n, name, t0, t1, lines in SHORTS:
    top = f'clips/short{n}_top.png'; ass = f'clips/short{n}.ass'
    make_top(lines, top); make_ass(t0, t1, ass)
    out = f'entrega/Overdrawn Files - Ground Stop EUA - SHORT {n} {name}.mp4'
    fc = ("[0:v]split[a][b];"
          "[a]scale=-2:1920,crop=1080:1920,gblur=sigma=30,eq=brightness=-0.25[bg];"
          "[b]scale=1080:-2[fg];"
          "[bg][fg]overlay=0:640[v1];[v1][1:v]overlay=0:0[v2];"
          f"[v2]subtitles={ass}:fontsdir=/home/user/next-netlify-starter/edicao-video/assets/fonts,"
          f"fade=t=in:st=0:d=0.3,fade=t=out:st={t1 - t0 - 0.4:.2f}:d=0.4[v];"
          f"[0:a]afade=t=in:st=0:d=0.15,afade=t=out:st={t1 - t0 - 0.4:.2f}:d=0.4[aud]")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t0}', '-to', f'{t1}', '-i', SRC, '-i', top,
                    '-filter_complex', fc, '-map', '[v]', '-map', '[aud]', '-c:v', 'libx264', '-preset', 'medium',
                    '-crf', '20', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-b:a', '192k',
                    '-movflags', '+faststart', out], check=True)
    print('ok', out)
