#!/bin/zsh
set -euo pipefail
# Reconcile the same named identity and credential. Safe to re-run.
exec "${0:A:h}/deploy.zsh" "$@"
