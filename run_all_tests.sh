#!/bin/bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

STATUS_UNIT=0
STATUS_INTEGRATION=0
STATUS_UI=0

log_section() {
  echo
  echo "================================================================================"
  echo "$1"
  echo "================================================================================"
}

run_unit_tests() {
  log_section "Ejecutando pruebas unitarias (pytest)"
  if pytest tests/test_models.py tests/test_pokeapi_client.py tests/test_pokemon_service.py tests/test_critical_features.py; then
    echo "✅ Pruebas unitarias completadas."
  else
    echo "❌ Fallaron las pruebas unitarias."
    STATUS_UNIT=1
  fi
}

run_integration_tests() {
  log_section "Ejecutando pruebas de integración (pytest)"
  if pytest tests/test_routes.py tests/test_integration_api.py; then
    echo "✅ Pruebas de integración completadas."
  else
    echo "❌ Fallaron las pruebas de integración."
    STATUS_INTEGRATION=1
  fi
}

start_server() {
  python run.py > /tmp/poke_gui_test_server.log 2>&1 &
  SERVER_PID=$!
  trap 'kill_server' EXIT
}

kill_server() {
  if [[ -n "${SERVER_PID:-}" ]] && ps -p "$SERVER_PID" > /dev/null 2>&1; then
    kill "$SERVER_PID" || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}

wait_for_server() {
  local url=${1:-http://localhost:5000}
  local retries=30
  for _ in $(seq 1 "$retries"); do
    if curl -sSf "$url" > /dev/null; then
      return 0
    fi
    sleep 1
  done
  echo "El servidor Flask no respondió en ${retries}s. Revisa /tmp/poke_gui_test_server.log."
  return 1
}

run_ui_tests() {
  log_section "Ejecutando pruebas de interfaz (Cypress)"
  start_server
  if wait_for_server; then
    if npx cypress run --e2e; then
      echo "✅ Pruebas de interfaz completadas."
    else
      echo "❌ Fallaron las pruebas de interfaz."
      STATUS_UI=1
    fi
  else
    STATUS_UI=1
  fi
  kill_server
  trap - EXIT
}

run_unit_tests
run_integration_tests
run_ui_tests

log_section "Resumen final"
if [[ $STATUS_UNIT -eq 0 && $STATUS_INTEGRATION -eq 0 && $STATUS_UI -eq 0 ]]; then
  echo "✅ Todas las suites de pruebas se ejecutaron correctamente."
  exit 0
fi

[[ $STATUS_UNIT -ne 0 ]] && echo "- Pruebas unitarias: FALLÓ"
[[ $STATUS_INTEGRATION -ne 0 ]] && echo "- Pruebas de integración: FALLÓ"
[[ $STATUS_UI -ne 0 ]] && echo "- Pruebas de interfaz: FALLÓ"

exit 1
