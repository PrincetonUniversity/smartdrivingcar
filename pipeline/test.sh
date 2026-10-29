#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
"$PYTHON_BIN" -m ruff check
"$PYTHON_BIN" -m ruff format --check
"$PYTHON_BIN" -m mypy
"$PYTHON_BIN" -m pytest tests/ azure/functions/tests/ -v -p no:cacheprovider
printf 'PASS: lint, format, types and all tests completed\n'
