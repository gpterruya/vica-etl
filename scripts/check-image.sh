#!/usr/bin/env bash
# Confere uma imagem do ETL sem executá-lo (sem rede):
#  - /app não pode conter dados (CSV, JSONL, PDF, planilhas, arquivos compactados)
#  - as bibliotecas instaladas têm que ser exatamente as do requirements.txt
set -euo pipefail

IMAGE="$1"

echo "Arquivos em /app:"
files=$(docker run --rm --network none --entrypoint sh "$IMAGE" \
  -c 'cd /app && find . -type f ! -path "*/__pycache__/*" | sort')
echo "$files"

if grep -Eiq '\.(csv|jsonl|json|pdf|xlsx|xls|tgz|tar|gz|zip|yaml|yml|env)$' <<< "$files"; then
  echo "::error::A imagem contém arquivos de dados ou configuração local em /app."
  exit 1
fi

expected=$(grep -Ev '^[[:space:]]*(#|$)' requirements.txt | tr -d '\r' | sort -f)
installed=$(docker run --rm --network none --entrypoint pip "$IMAGE" freeze 2>/dev/null | sort -f)

if ! diff <(echo "$expected") <(echo "$installed"); then
  echo "::error::As bibliotecas da imagem diferem do requirements.txt."
  exit 1
fi

echo "Imagem OK: sem dados em /app e bibliotecas iguais ao requirements.txt."
