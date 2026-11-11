# Sourced by the azure/deploy scripts. Stops them before they change anything
# unless the Azure CLI is on the newsletter's subscription, which is recorded
# once, in azure/connector/production.json. A fresh `az login` picks whatever
# default subscription the account has, which is often a different one.
# Checks only: never changes the CLI's default subscription.

require_newsletter_subscription() {
    local here config expected current
    here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    config="${here}/../connector/production.json"
    expected="$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["subscription"])' "$config")" || {
        echo "Cannot read the subscription from ${config}" >&2
        return 1
    }
    current="$(az account show --query id -o tsv)" || {
        echo "Not logged in to Azure. Run: az login" >&2
        return 1
    }
    if [[ "$current" != "$expected" ]]; then
        echo "Azure CLI is on subscription ${current}, but the newsletter resources are in ${expected}." >&2
        echo "Run: az account set --subscription ${expected}" >&2
        return 1
    fi
}
