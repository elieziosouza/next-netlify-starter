#!/bin/bash
# finaliza_teacher.sh VIDEO_EDITADO CAPA SAIDA: capa+riser (canal Teacher Eliezio), loudnorm -14 LUFS e x264 em duas passagens
set -e
IN=$1; CAPA=$2; OUT=$3; T=$(mktemp -d)
python3 /home/user/next-netlify-starter/edicao-video/scripts/embutir_capa_teacher.py "$IN" "$CAPA" $T/cc.mp4
J=$(ffmpeg -hide_banner -i $T/cc.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g(){ echo "$J" | python3 -c "import json,sys;print(json.load(sys.stdin)['$1'])"; }
AF="loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true"
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 $T/cc.mp4)
VB=$(python3 -c "print(int(min(9000, 13.8*8*1024*1024/$D/1000 - 200)))")
cd $T; ffmpeg -v error -y -i cc.mp4 -c:v libx264 -preset slow -b:v ${VB}k -pass 1 -an -f null /dev/null
ffmpeg -v error -y -i cc.mp4 -c:v libx264 -preset slow -b:v ${VB}k -pass 2 -pix_fmt yuv420p -af "$AF" -c:a aac -b:a 160k -ar 48000 -movflags +faststart "$OUT"
rm -rf $T; ls -la "$OUT"
