#!/bin/zsh
set -euo pipefail
REPO_ROOT="${0:A:h:h:h}"
exec "${PYTHON_BIN:-$REPO_ROOT/.venv/bin/python}" "$REPO_ROOT/scripts/azure_connector_admin.py" deploy "$@"
