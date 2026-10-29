#!/bin/zsh
# Disable publishing and revoke just the dedicated GitHub federation.
set -euo pipefail
DRY_RUN=false
case "${1:-}" in
  --dry-run) DRY_RUN=true ;;
  '') ;;
  *) print -u2 'Usage: teardown.zsh [--dry-run]'; exit 2 ;;
esac
: "${NEWSLETTER_AZURE_CLIENT_ID:?Set the dedicated publisher client ID}"
: "${NEWSLETTER_GITHUB_REPOSITORY:?Set owner/repo}"
[[ "$NEWSLETTER_AZURE_CLIENT_ID" =~ '^[a-fA-F0-9-]{36}$' ]] || exit 2
[[ "$NEWSLETTER_GITHUB_REPOSITORY" =~ '^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$' ]] || exit 2
if $DRY_RUN; then
  print 'DRY RUN: disable NEWSLETTER_PIPELINE_ENABLED and delete dedicated publisher federation.'
  print 'DRY RUN: mailbox, retained messages, Pages and unrelated Azure resources remain intact.'
  exit 0
fi
gh variable set NEWSLETTER_PIPELINE_ENABLED --repo "$NEWSLETTER_GITHUB_REPOSITORY" --body false
CREDENTIAL_ID="$(az ad app federated-credential list --id "$NEWSLETTER_AZURE_CLIENT_ID" --query "[?name=='newsletter-mailbox-github'].id | [0]" -o tsv)"
if [[ -n "$CREDENTIAL_ID" ]]; then
  az ad app federated-credential delete --id "$NEWSLETTER_AZURE_CLIENT_ID" --federated-credential-id "$CREDENTIAL_ID"
fi
print 'PASS: publishing disabled and federation revoked. Remove Exchange role assignment using the runbook.'
