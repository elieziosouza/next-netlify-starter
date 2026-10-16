#!/usr/bin/env bash
# Monta a área de trabalho que os renderizadores esperam (S = 1º argumento dos scripts render_*.py).
# Uso: bash edicao-video/scripts/prepara_area.sh /caminho/da/area
# Depois: python3 $S/work/render_xxx.py $S saida.mp4
set -euo pipefail
S="${1:?informe a pasta da área de trabalho}"; KIT="$(cd "$(dirname "$0")/.." && pwd)"
M="${EDICAO_MODELOS:-$HOME/.cache/edicao-video}"
[ -s "$M/asr/silero_vad.onnx" ] || bash "$KIT/setup.sh"
mkdir -p "$S/work" "$S/musica" "$S/v15"
cp -f "$KIT"/scripts/*.py "$S/work/"
ln -sfn "$M/asr" "$S/asr"; ln -sfn "$M/seg" "$S/seg"; ln -sfn "$KIT/assets/fonts" "$S/fontdl"
[ -s "$S/musica/batidao_pt.wav" ] || ffmpeg -v error -y -i "$KIT/assets/musica/batidao_pt.mp3" -ar 48000 -ac 2 "$S/musica/batidao_pt.wav"
# a música original "vai dar PT" tem dono: não fica no repositório público. Coloque o arquivo em $S/v15/song_vox.wav
# Cópia privada na página de entregas (Artifact https://claude.ai/artifact/7Nf9BW8NJDeozRGdX1DdMS, arquivo kit/vai-dar-pt.mp3):
# Claude baixa com Artifact read (path "kit/vai-dar-pt.mp3") e converte para wav 48 kHz. A letra começa no segundo 0.
[ -s "$S/v15/song_vox.wav" ] || echo "aviso: falta $S/v15/song_vox.wav (música vai dar PT) — baixar kit/vai-dar-pt.mp3 da página de entregas"
echo "área pronta: $S"
