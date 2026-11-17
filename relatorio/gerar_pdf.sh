#!/usr/bin/env bash
# Gera relatorio/relatorio_final.pdf a partir de relatorio_final.md.
# Requisitos: pandoc e Google Chrome (ou Chromium) instalados.
set -euo pipefail
cd "$(dirname "$0")"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
pandoc relatorio_final.md --standalone --mathml --css estilo.css --metadata title-prefix="" \
  -o relatorio_final.html
PERFIL="$(mktemp -d)"; trap 'rm -rf "$PERFIL"' EXIT
"$CHROME" --headless=new --user-data-dir="$PERFIL" --disable-gpu --no-pdf-header-footer --allow-file-access-from-files \
  --print-to-pdf=relatorio_final.pdf "file://$PWD/relatorio_final.html"
rm relatorio_final.html
echo "Gerado: relatorio/relatorio_final.pdf"
