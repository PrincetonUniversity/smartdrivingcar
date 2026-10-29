#!/bin/zsh
# Provision only a dedicated Entra identity and its GitHub OIDC trust.
set -euo pipefail
DRY_RUN=false
case "${1:-}" in
  --dry-run) DRY_RUN=true ;;
  '') ;;
  *) print -u2 'Usage: deploy.zsh [--dry-run]'; exit 2 ;;
esac
: "${NEWSLETTER_APP_NAME:?Set NEWSLETTER_APP_NAME to a dedicated unique app name}"
: "${NEWSLETTER_GITHUB_REPOSITORY:?Set NEWSLETTER_GITHUB_REPOSITORY to owner/repo}"
: "${NEWSLETTER_AZURE_TENANT_ID:?Set NEWSLETTER_AZURE_TENANT_ID}"
[[ "$NEWSLETTER_APP_NAME" =~ '^[A-Za-z0-9-]{3,80}$' ]] || { print -u2 'Invalid app name'; exit 2; }
[[ "$NEWSLETTER_GITHUB_REPOSITORY" =~ '^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$' ]] || { print -u2 'Invalid repository'; exit 2; }
[[ "$NEWSLETTER_AZURE_TENANT_ID" =~ '^[a-fA-F0-9-]{36}$' ]] || { print -u2 'Invalid tenant ID'; exit 2; }
if $DRY_RUN; then
  print 'DRY RUN: find or create dedicated Entra app and service principal.'
  print "DRY RUN: reconcile OIDC subject repo:${NEWSLETTER_GITHUB_REPOSITORY}:environment:newsletter-mailbox."
  print 'DRY RUN: no Graph tenant-wide permissions, Azure subscription roles or passwords will be granted.'
  exit 0
fi
command -v az >/dev/null
[[ "$(az account show --query tenantId -o tsv)" == "$NEWSLETTER_AZURE_TENANT_ID" ]] || { print -u2 'Azure CLI is using a different tenant'; exit 1; }
APP_IDS="$(az ad app list --filter "displayName eq '$NEWSLETTER_APP_NAME'" --query '[].appId' -o tsv)"
[[ "$APP_IDS" != *$'\n'* ]] || { print -u2 'App name is not unique; choose a unique name'; exit 1; }
if [[ -z "$APP_IDS" ]]; then
  APP_IDS="$(az ad app create --display-name "$NEWSLETTER_APP_NAME" --query appId -o tsv)"
fi
SP_ID="$(az ad sp list --filter "appId eq '$APP_IDS'" --query '[0].id' -o tsv)"
if [[ -z "$SP_ID" ]]; then
  SP_ID="$(az ad sp create --id "$APP_IDS" --query id -o tsv)"
fi
SCRIPT_DIR="${0:A:h}"
REPO_ROOT="${SCRIPT_DIR:h:h}"
PYTHON_BIN="${PYTHON_BIN:-$REPO_ROOT/.venv/bin/python}"
CREDENTIAL_FILE="$(mktemp)"
trap 'rm -f "$CREDENTIAL_FILE"' EXIT
export NEWSLETTER_FEDERATION_OUTPUT="$CREDENTIAL_FILE"
"$PYTHON_BIN" - <<'PY'
import json, os
from pathlib import Path
Path(os.environ['NEWSLETTER_FEDERATION_OUTPUT']).write_text(json.dumps({
    'name': 'newsletter-mailbox-github',
    'issuer': 'https://token.actions.githubusercontent.com',
    'subject': 'repo:' + os.environ['NEWSLETTER_GITHUB_REPOSITORY'] + ':environment:newsletter-mailbox',
    'audiences': ['api://AzureADTokenExchange']}))
PY
EXISTING_ID="$(az ad app federated-credential list --id "$APP_IDS" --query "[?name=='newsletter-mailbox-github'].id | [0]" -o tsv)"
if [[ -z "$EXISTING_ID" ]]; then
  az ad app federated-credential create --id "$APP_IDS" --parameters "@$CREDENTIAL_FILE" --output none
else
  az ad app federated-credential update --id "$APP_IDS" --federated-credential-id "$EXISTING_ID" --parameters "@$CREDENTIAL_FILE" --output none
fi
print "PASS: identity and federation ready. Client ID: $APP_IDS"
print "Enterprise service principal object ID for Exchange: $SP_ID"
print 'Next: administrator applies configure-mailbox.ps1 and verifies mailbox isolation.'
