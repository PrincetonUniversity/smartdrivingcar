#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# SmartDrivingCar Azure Newsletter Pipeline — Update Script
# ==============================================================================
# Updates deployed Azure resources without a full redeploy. Republishes Function
# App code, updates Logic App workflow, or reconfigures connections.
#
# Usage:
#   ./update.sh                  # Update everything (function + logic app)
#   ./update.sh --function-only  # Republish Function App code only
#   ./update.sh --logic-app-only # Redeploy Logic App workflow only
#   ./update.sh --help           # Show help
# ==============================================================================

# --- Colors & Symbols --------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

CHECK="${GREEN}✔${NC}"
CROSS="${RED}✖${NC}"
WARN="${YELLOW}⚠${NC}"
INFO="${BLUE}ℹ${NC}"

print_header() {
    echo ""
    echo -e "${MAGENTA}${BOLD}══════════════════════════════════════════════════${NC}"
    echo -e "${MAGENTA}${BOLD}  $1${NC}"
    echo -e "${MAGENTA}${BOLD}══════════════════════════════════════════════════${NC}"
    echo ""
}

print_step() {
    echo -e "${CYAN}${BOLD}── Step $1: $2 ──${NC}"
}

ok()   { echo -e "  ${CHECK} $1"; }
fail() { echo -e "  ${CROSS} $1"; exit 1; }
warn() { echo -e "  ${WARN} $1"; }
info() { echo -e "  ${INFO} $1"; }

prompt_with_default() {
    local varname="$1"
    local prompt_text="$2"
    local default_val="$3"
    local input
    read -rp "  $(echo -e "${BOLD}")${prompt_text}$(echo -e "${NC}") [${default_val}]: " input
    eval "$varname='${input:-$default_val}'"
}

# --- Parse Arguments ----------------------------------------------------------
UPDATE_FUNCTION=true
UPDATE_LOGIC_APP=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --function-only)
            UPDATE_LOGIC_APP=false
            shift
            ;;
        --logic-app-only)
            UPDATE_FUNCTION=false
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Update the deployed Azure newsletter pipeline."
            echo ""
            echo "Options:"
            echo "  --function-only    Republish Function App code only"
            echo "  --logic-app-only   Redeploy Logic App workflow only"
            echo "  --help, -h         Show this help"
            echo ""
            echo "This script does NOT recreate resource groups, storage accounts,"
            echo "or API connections. Use deploy.sh for initial setup."
            exit 0
            ;;
        *)
            fail "Unknown option: $1. Use --help for usage."
            ;;
    esac
done

# --- Resolve paths ------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
FUNCTIONS_DIR="${REPO_ROOT}/azure/functions"
LOGIC_APP_DIR="${REPO_ROOT}/azure/logic-app"
SCRIPTS_DIR="${REPO_ROOT}/scripts"

# ==============================================================================
print_header "SmartDrivingCar Newsletter Pipeline — Update"
# ==============================================================================

# --- Prerequisites ------------------------------------------------------------
print_step 1 "Checking prerequisites"

if ! command -v az &>/dev/null; then
    fail "Azure CLI (az) not found"
fi

if $UPDATE_FUNCTION && ! command -v func &>/dev/null; then
    fail "Azure Functions Core Tools (func) not found"
fi

if ! az account show &>/dev/null; then
    fail "Not logged in to Azure. Run: az login"
fi

SUBSCRIPTION=$(az account show --query name -o tsv)
ok "Logged in to Azure (subscription: ${SUBSCRIPTION})"

if [[ -f "${SCRIPTS_DIR}/clean_newsletter.py" && -f "${SCRIPTS_DIR}/import_newsletter.py" ]]; then
    ok "Newsletter processing scripts found"
else
    fail "Missing scripts/clean_newsletter.py or scripts/import_newsletter.py"
fi

# --- Configuration ------------------------------------------------------------
print_step 2 "Configuration"
echo ""
info "Enter existing deployment details (must match what was used in deploy.sh)."
echo ""

prompt_with_default RESOURCE_GROUP  "Resource group"        "orfe-dept-azure-alaink-sdc-rg"
prompt_with_default FUNC_APP_NAME   "Function App name"     "orfe-dept-azure-sdc-func"

if $UPDATE_LOGIC_APP; then
    prompt_with_default LOGIC_APP_NAME  "Logic App name"        "orfe-dept-azure-sdc-logic"
    prompt_with_default REGION          "Azure region"          "canadacentral"
    prompt_with_default O365_FOLDER     "O365 mail folder"      "SmartDrivingCars Newsletters for Processing"
    prompt_with_default GITHUB_OWNER    "GitHub owner"          "PrincetonUniversity"
    prompt_with_default GITHUB_REPO     "GitHub repo"           "smartdrivingcar"
    prompt_with_default O365_CONN_NAME  "O365 connection name"  "orfe-dept-azure-sdc-o365"
    prompt_with_default GITHUB_CONN_NAME "GitHub connection name" "orfe-dept-azure-sdc-github"
fi

echo ""

# --- Update Function App -----------------------------------------------------
if $UPDATE_FUNCTION; then
    print_step 3 "Updating Function App"

    # Verify Function App exists
    if ! az functionapp show --name "${FUNC_APP_NAME}" --resource-group "${RESOURCE_GROUP}" &>/dev/null; then
        fail "Function App '${FUNC_APP_NAME}' not found in '${RESOURCE_GROUP}'. Run deploy.sh first."
    fi

    # Copy scripts to lib/
    info "Copying processing scripts to azure/functions/lib/..."
    mkdir -p "${FUNCTIONS_DIR}/lib"
    cp "${SCRIPTS_DIR}/clean_newsletter.py" "${FUNCTIONS_DIR}/lib/"
    cp "${SCRIPTS_DIR}/import_newsletter.py" "${FUNCTIONS_DIR}/lib/"
    touch "${FUNCTIONS_DIR}/lib/__init__.py"
    ok "Scripts copied to lib/"

    # Publish
    info "Publishing updated Function App (remote build)..."
    (cd "${FUNCTIONS_DIR}" && func azure functionapp publish "${FUNC_APP_NAME}" --python --build remote) && \
        ok "Function App updated" || \
        fail "Failed to publish Function App"

    # Retrieve function key (needed if updating Logic App too)
    if $UPDATE_LOGIC_APP; then
        info "Retrieving function key..."
        FUNCTION_KEY=$(az functionapp function keys list \
            --name "${FUNC_APP_NAME}" \
            --resource-group "${RESOURCE_GROUP}" \
            --function-name "process_newsletter" \
            --query "default" -o tsv 2>/dev/null)

        if [[ -z "${FUNCTION_KEY}" ]]; then
            warn "Waiting 30s for deployment to propagate..."
            sleep 30
            FUNCTION_KEY=$(az functionapp function keys list \
                --name "${FUNC_APP_NAME}" \
                --resource-group "${RESOURCE_GROUP}" \
                --function-name "process_newsletter" \
                --query "default" -o tsv 2>/dev/null)
        fi

        if [[ -n "${FUNCTION_KEY}" ]]; then
            ok "Function key retrieved"
        else
            fail "Could not retrieve function key"
        fi
    fi

    # Cleanup lib/ copies
    rm -rf "${FUNCTIONS_DIR}/lib"
    ok "Cleaned up lib/ copies"
fi

# --- Update Logic App ---------------------------------------------------------
if $UPDATE_LOGIC_APP; then
    STEP=$($UPDATE_FUNCTION && echo 4 || echo 3)
    print_step $STEP "Updating Logic App"

    # Get function key if we didn't just deploy the function
    if [[ -z "${FUNCTION_KEY:-}" ]]; then
        info "Retrieving current function key..."
        FUNCTION_KEY=$(az functionapp function keys list \
            --name "${FUNC_APP_NAME}" \
            --resource-group "${RESOURCE_GROUP}" \
            --function-name "process_newsletter" \
            --query "default" -o tsv 2>/dev/null)

        if [[ -z "${FUNCTION_KEY}" ]]; then
            fail "Could not retrieve function key. Is the Function App deployed?"
        fi
        ok "Function key retrieved"
    fi

    # Get connection IDs
    O365_CONN_ID=$(az resource show \
        --resource-group "${RESOURCE_GROUP}" \
        --resource-type "Microsoft.Web/connections" \
        --name "${O365_CONN_NAME}" \
        --query id -o tsv 2>/dev/null) || fail "O365 connection '${O365_CONN_NAME}' not found"

    GITHUB_CONN_ID=$(az resource show \
        --resource-group "${RESOURCE_GROUP}" \
        --resource-type "Microsoft.Web/connections" \
        --name "${GITHUB_CONN_NAME}" \
        --query id -o tsv 2>/dev/null) || fail "GitHub connection '${GITHUB_CONN_NAME}' not found"

    ok "Connection IDs retrieved"

    az deployment group create \
        --name "sdc-logic-app-update-$(date +%s)" \
        --resource-group "${RESOURCE_GROUP}" \
        --template-file "${LOGIC_APP_DIR}/workflow.json" \
        --parameters \
            logicAppName="${LOGIC_APP_NAME}" \
            location="${REGION}" \
            functionAppName="${FUNC_APP_NAME}" \
            functionAppResourceGroup="${RESOURCE_GROUP}" \
            functionKey="${FUNCTION_KEY}" \
            o365FolderPath="${O365_FOLDER}" \
            githubOwner="${GITHUB_OWNER}" \
            githubRepo="${GITHUB_REPO}" \
            o365ConnectionId="${O365_CONN_ID}" \
            githubConnectionId="${GITHUB_CONN_ID}" \
        --output none 2>/dev/null && \
        ok "Logic App updated" || \
        fail "Failed to update Logic App"
fi

# --- Verify -------------------------------------------------------------------
VERIFY_STEP=$(($(($UPDATE_FUNCTION && echo 1 || echo 0) + $($UPDATE_LOGIC_APP && echo 1 || echo 0)) + 3))
print_step $VERIFY_STEP "Verification"

if $UPDATE_FUNCTION; then
    info "Testing Function App endpoint..."
    FUNC_URL="https://${FUNC_APP_NAME}.azurewebsites.net/api/process-newsletter"

    # Retrieve key if not already set
    if [[ -z "${FUNCTION_KEY:-}" ]]; then
        FUNCTION_KEY=$(az functionapp function keys list \
            --name "${FUNC_APP_NAME}" \
            --resource-group "${RESOURCE_GROUP}" \
            --function-name "process_newsletter" \
            --query "default" -o tsv 2>/dev/null)
    fi

    TEST_PAYLOAD='{"body_html":"<html><body><h1>Test</h1><p>Hello</p></body></html>","subject":"Test Newsletter","received_date":"2025-01-01"}'

    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST "${FUNC_URL}" \
        -H "Content-Type: application/json" \
        -H "x-functions-key: ${FUNCTION_KEY}" \
        -d "${TEST_PAYLOAD}" 2>/dev/null || echo "000")

    if [[ "${HTTP_CODE}" == "200" ]]; then
        ok "Function App returned 200 OK"
    else
        warn "Function App returned HTTP ${HTTP_CODE} (may need a few minutes to warm up)"
    fi
fi

if $UPDATE_LOGIC_APP; then
    LOGIC_STATE=$(az logic workflow show \
        --name "${LOGIC_APP_NAME}" \
        --resource-group "${RESOURCE_GROUP}" \
        --query "state" -o tsv 2>/dev/null || echo "Unknown")
    if [[ "${LOGIC_STATE}" == "Enabled" ]]; then
        ok "Logic App is Enabled"
    else
        warn "Logic App state: ${LOGIC_STATE}"
    fi
fi

# --- Summary ------------------------------------------------------------------
print_header "Update Complete"

$UPDATE_FUNCTION && echo -e "  ${CHECK} Function App '${FUNC_APP_NAME}' republished"
$UPDATE_LOGIC_APP && echo -e "  ${CHECK} Logic App '${LOGIC_APP_NAME}' redeployed"
echo ""
