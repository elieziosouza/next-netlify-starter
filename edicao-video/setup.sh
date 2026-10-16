#!/usr/bin/env bash
# Instala o que o kit de edição precisa numa sessão nova (cole no "Setup script" do ambiente).
# Modelos ficam em ~/.cache/edicao-video (fora do repositório, que é público).
set -euo pipefail
M="${EDICAO_MODELOS:-$HOME/.cache/edicao-video}"
mkdir -p "$M/asr" "$M/seg"
command -v ffmpeg >/dev/null || { (apt-get update -qq && apt-get install -y -qq ffmpeg) || sudo apt-get install -y -qq ffmpeg; }
python3 -m pip install -q --disable-pip-version-check numpy pillow opencv-python-headless onnxruntime sherpa-onnx
baixa() { if [ ! -s "$2" ]; then curl -fsSL --retry 4 -o "$2.part" "$1" && mv -f "$2.part" "$2"; fi; }
# transcrição (Whisper small em português) e detector de fala
if [ ! -s "$M/asr/sherpa-onnx-whisper-small/small-encoder.int8.onnx" ]; then
  curl -fsSL --retry 4 https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-small.tar.bz2 | tar -xj -C "$M/asr"
  rm -f "$M/asr/sherpa-onnx-whisper-small/"small-*coder.onnx            # fica só a versão int8, mais leve
fi
baixa https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/silero_vad.onnx "$M/asr/silero_vad.onnx"
# recorte da pessoa (palavra gigante atrás, capas)
baixa https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.onnx "$M/seg/u2net_human_seg.onnx"
echo "kit de edição pronto em $M"
