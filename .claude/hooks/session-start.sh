#!/bin/bash
# Prepara o kit de edição de vídeo do Eliezio em toda sessão nova na nuvem:
# dependências Python e modelos de transcrição/recorte (ver edicao-video/setup.sh).
set -euo pipefail
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi
cd "${CLAUDE_PROJECT_DIR:-.}"
bash edicao-video/setup.sh
echo 'export EDICAO_MODELOS="$HOME/.cache/edicao-video"' >> "${CLAUDE_ENV_FILE:-/dev/null}"
