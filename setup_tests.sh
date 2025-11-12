#!/bin/bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$PROJECT_ROOT"

mkdir -p tests cypress/e2e

pip install -r requirements.txt

if command -v npm >/dev/null 2>&1; then
  npm install
else
  echo "npm no está disponible en el entorno. Instálalo para preparar las pruebas de interfaz." >&2
fi

echo "Test environment ready."
