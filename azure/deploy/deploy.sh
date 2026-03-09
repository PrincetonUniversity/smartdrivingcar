#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# SmartDrivingCar Azure Newsletter Pipeline — Deploy Script
# ==============================================================================
# Deploys the Azure Function App, API connections, and Logic App for the
# automated newsletter publishing pipeline.
#
# Usage:
#   ./deploy.sh                  # Full deploy (all steps)
#   ./deploy.sh --function-only  # Deploy Function App only
#   ./deploy.sh --connections-only  # Deploy API connections only
#   ./deploy.sh --logic-app-only # Deploy Logic App only
#   ./deploy.sh --help           # Show help
# ==============================================================================

# --- Colors & Symbols --------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

CHECK="${GREEN}✔${NC}"
CROSS="${RED}✖${NC}"
WARN="${YELLOW}⚠${NC}"
INFO="${BLUE}ℹ${NC}"

# --- Helpers ------------------------------------------------------------------
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

print_box() {
    local msg="$1"
    local width=${#msg}
    local border=""
    for ((i = 0; i < width + 4; i++)); do border+="─"; done
    echo -e "${CYAN}┌${border}┐${NC}"
    echo -e "${CYAN}│  ${NC}${msg}${CYAN}  │${NC}"
    echo -e "${CYAN}└${border}┘${NC}"
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
DEPLOY_FUNCTION=true
DEPLOY_CONNECTIONS=true
DEPLOY_LOGIC_APP=true

while [[ $# -gt 0 ]]; do
    case $1 in
        --function-only)
            DEPLOY_CONNECTIONS=false
            DEPLOY_LOGIC_APP=false
            shift
            ;;
        --connections-only)
            DEPLOY_FUNCTION=false
            DEPLOY_LOGIC_APP=false
            shift
            ;;
        --logic-app-only)
            DEPLOY_FUNCTION=false
            DEPLOY_CONNECTIONS=false
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Deploy the Azure newsletter pipeline for SmartDrivingCar."
            echo ""
            echo "Options:"
            echo "  --function-only      Deploy Azure Function App only"
            echo "  --connections-only   Deploy API connections only"
            echo "  --logic-app-only     Deploy Logic App only"
            echo "  --help, -h           Show this help"
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
print_header "SmartDrivingCar Newsletter Pipeline — Azure Deploy"
# ==============================================================================

# --- Step 1: Prerequisites ----------------------------------------------------
STEP=1
if $DEPLOY_FUNCTION || $DEPLOY_CONNECTIONS || $DEPLOY_LOGIC_APP; then
    print_step $STEP "Checking prerequisites"

    # az CLI
    if command -v az &>/dev/null; then
        ok "Azure CLI (az) found: $(az version --query '\"azure-cli\"' -o tsv 2>/dev/null || echo 'unknown')"
    else
        fail "Azure CLI (az) not found. Install: https://aka.ms/install-azure-cli"
    fi

    # func CLI (only for function deploy)
    if $DEPLOY_FUNCTION; then
        if command -v func &>/dev/null; then
            ok "Azure Functions Core Tools (func) found"
        else
            fail "Azure Functions Core Tools (func) not found. Install: https://aka.ms/azure-functions-core-tools"
        fi
    fi

    # python3
    if command -v python3 &>/dev/null; then
        ok "Python 3 found: $(python3 --version 2>&1)"
    else
        fail "Python 3 not found"
    fi

    # az login check
    if az account show &>/dev/null; then
        SUBSCRIPTION=$(az account show --query name -o tsv)
        ok "Logged in to Azure (subscription: ${SUBSCRIPTION})"
    else
        fail "Not logged in to Azure. Run: az login"
    fi

    # scripts exist
    if [[ -f "${SCRIPTS_DIR}/clean_newsletter.py" && -f "${SCRIPTS_DIR}/import_newsletter.py" ]]; then
        ok "Newsletter processing scripts found"
    else
        fail "Missing scripts/clean_newsletter.py or scripts/import_newsletter.py"
    fi

    STEP=$((STEP + 1))
fi

# --- Step 2: Interactive Configuration ---------------------------------------
print_step $STEP "Configuration"
echo ""
info "Press Enter to accept defaults."
echo ""

RANDOM_SUFFIX=$(LC_ALL=C tr -dc 'a-z0-9' </dev/urandom | head -c 4 || true)

prompt_with_default REGION          "Azure region"               "canadacentral"
prompt_with_default RESOURCE_GROUP  "Resource group"             "orfe-dept-azure-alaink-sdc-rg"
prompt_with_default FUNC_APP_NAME   "Function App name"          "orfe-dept-azure-sdc-func"
prompt_with_default STORAGE_ACCOUNT "Storage account name"       "stsdcnewsletter${RANDOM_SUFFIX}"
prompt_with_default LOGIC_APP_NAME  "Logic App name"             "orfe-dept-azure-sdc-logic"
prompt_with_default O365_FOLDER     "O365 mail folder"           "SmartDrivingCars Newsletters for Processing"
prompt_with_default GITHUB_OWNER    "GitHub owner"               "PrincetonUniversity"
prompt_with_default GITHUB_REPO     "GitHub repo"                "smartdrivingcar"
prompt_with_default O365_CONN_NAME  "O365 connection name"       "orfe-dept-azure-sdc-o365"
prompt_with_default GITHUB_CONN_NAME "GitHub connection name"    "orfe-dept-azure-sdc-github"

echo ""
info "Configuration:"
echo "  Region:           ${REGION}"
echo "  Resource Group:   ${RESOURCE_GROUP}"
echo "  Function App:     ${FUNC_APP_NAME}"
echo "  Storage Account:  ${STORAGE_ACCOUNT}"
echo "  Logic App:        ${LOGIC_APP_NAME}"
echo "  O365 Folder:      ${O365_FOLDER}"
echo "  GitHub:           ${GITHUB_OWNER}/${GITHUB_REPO}"
echo ""

read -rp "  Proceed? [Y/n]: " CONFIRM
if [[ "${CONFIRM}" == "n" || "${CONFIRM}" == "N" ]]; then
    echo "Aborted."
    exit 0
fi

STEP=$((STEP + 1))

# --- Step 3: Resource Group ---------------------------------------------------
print_step $STEP "Creating resource group"

az group create \
    --name "${RESOURCE_GROUP}" \
    --location "${REGION}" \
    --output none 2>/dev/null && \
    ok "Resource group '${RESOURCE_GROUP}' ready" || \
    fail "Failed to create resource group"

STEP=$((STEP + 1))

# --- Step 4: Function App ----------------------------------------------------
if $DEPLOY_FUNCTION; then
    print_step $STEP "Deploying Azure Function App"

    # Create storage account
    info "Creating storage account '${STORAGE_ACCOUNT}'..."
    az storage account create \
        --name "${STORAGE_ACCOUNT}" \
        --resource-group "${RESOURCE_GROUP}" \
        --location "${REGION}" \
        --sku Standard_LRS \
        --output none 2>/dev/null && \
        ok "Storage account ready" || \
        fail "Failed to create storage account"

    # Copy scripts to lib/
    info "Copying processing scripts to azure/functions/lib/..."
    mkdir -p "${FUNCTIONS_DIR}/lib"
    cp "${SCRIPTS_DIR}/clean_newsletter.py" "${FUNCTIONS_DIR}/lib/"
    cp "${SCRIPTS_DIR}/import_newsletter.py" "${FUNCTIONS_DIR}/lib/"
    touch "${FUNCTIONS_DIR}/lib/__init__.py"
    ok "Scripts copied to lib/"

    # Create Function App
    info "Creating Function App '${FUNC_APP_NAME}'..."
    az functionapp create \
        --name "${FUNC_APP_NAME}" \
        --resource-group "${RESOURCE_GROUP}" \
        --storage-account "${STORAGE_ACCOUNT}" \
        --consumption-plan-location "${REGION}" \
        --runtime python \
        --runtime-version 3.11 \
        --os-type Linux \
        --functions-version 4 \
        --output none 2>/dev/null && \
        ok "Function App created" || \
        fail "Failed to create Function App"

    # Publish
    info "Publishing Function App (remote build)..."
    (cd "${FUNCTIONS_DIR}" && func azure functionapp publish "${FUNC_APP_NAME}" --python --build remote) && \
        ok "Function App published" || \
        fail "Failed to publish Function App"

    # Retrieve function key
    info "Retrieving function key..."
    FUNCTION_KEY=$(az functionapp function keys list \
        --name "${FUNC_APP_NAME}" \
        --resource-group "${RESOURCE_GROUP}" \
        --function-name "process_newsletter" \
        --query "default" -o tsv 2>/dev/null)

    if [[ -z "${FUNCTION_KEY}" ]]; then
        warn "Could not retrieve function key immediately. Waiting 30s for deployment to propagate..."
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
        fail "Could not retrieve function key. Check Function App deployment status in Azure Portal."
    fi

    # Cleanup lib/ copies
    rm -rf "${FUNCTIONS_DIR}/lib"
    ok "Cleaned up lib/ copies"

    STEP=$((STEP + 1))
fi

# --- Step 5: API Connections --------------------------------------------------
if $DEPLOY_CONNECTIONS; then
    print_step $STEP "Deploying API connections"

    az deployment group create \
        --name "sdc-connections-$(date +%s)" \
        --resource-group "${RESOURCE_GROUP}" \
        --template-file "${LOGIC_APP_DIR}/connections.json" \
        --parameters \
            location="${REGION}" \
            o365ConnectionName="${O365_CONN_NAME}" \
            githubConnectionName="${GITHUB_CONN_NAME}" \
        --output none 2>/dev/null && \
        ok "API connections deployed" || \
        fail "Failed to deploy API connections"

    # Get connection resource IDs
    O365_CONN_ID=$(az resource show \
        --resource-group "${RESOURCE_GROUP}" \
        --resource-type "Microsoft.Web/connections" \
        --name "${O365_CONN_NAME}" \
        --query id -o tsv 2>/dev/null)

    GITHUB_CONN_ID=$(az resource show \
        --resource-group "${RESOURCE_GROUP}" \
        --resource-type "Microsoft.Web/connections" \
        --name "${GITHUB_CONN_NAME}" \
        --query id -o tsv 2>/dev/null)

    ok "Connection IDs retrieved"

    echo ""
    echo -e "${CYAN}┌──────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${CYAN}│                                                              │${NC}"
    echo -e "${CYAN}│  ${BOLD}ACTION REQUIRED: Authorize API Connections${NC}${CYAN}                 │${NC}"
    echo -e "${CYAN}│                                                              │${NC}"
    echo -e "${CYAN}│  Open each URL below in your browser and click 'Authorize'  │${NC}"
    echo -e "${CYAN}│  to complete the OAuth flow.                                │${NC}"
    echo -e "${CYAN}│                                                              │${NC}"
    echo -e "${CYAN}│  1. Office 365 connection:                                  │${NC}"
    echo -e "${CYAN}│     https://portal.azure.com/#resource${O365_CONN_ID}/edit   ${NC}"
    echo -e "${CYAN}│                                                              │${NC}"
    echo -e "${CYAN}│  2. GitHub connection:                                      │${NC}"
    echo -e "${CYAN}│     https://portal.azure.com/#resource${GITHUB_CONN_ID}/edit ${NC}"
    echo -e "${CYAN}│                                                              │${NC}"
    echo -e "${CYAN}└──────────────────────────────────────────────────────────────┘${NC}"
    echo ""

    read -rp "  Press Enter after authorizing both connections..." _

    STEP=$((STEP + 1))
fi

# --- Step 6: Logic App --------------------------------------------------------
if $DEPLOY_LOGIC_APP; then
    print_step $STEP "Deploying Logic App"

    # Ensure we have required variables
    if [[ -z "${FUNCTION_KEY:-}" ]]; then
        info "Function key not set (partial deploy). Enter it manually."
        read -rsp "  Function key: " FUNCTION_KEY
        echo ""
    fi

    if [[ -z "${O365_CONN_ID:-}" ]]; then
        O365_CONN_ID=$(az resource show \
            --resource-group "${RESOURCE_GROUP}" \
            --resource-type "Microsoft.Web/connections" \
            --name "${O365_CONN_NAME}" \
            --query id -o tsv 2>/dev/null)
    fi

    if [[ -z "${GITHUB_CONN_ID:-}" ]]; then
        GITHUB_CONN_ID=$(az resource show \
            --resource-group "${RESOURCE_GROUP}" \
            --resource-type "Microsoft.Web/connections" \
            --name "${GITHUB_CONN_NAME}" \
            --query id -o tsv 2>/dev/null)
    fi

    az deployment group create \
        --name "sdc-logic-app-$(date +%s)" \
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
        ok "Logic App deployed" || \
        fail "Failed to deploy Logic App"

    STEP=$((STEP + 1))
fi

# --- Step 7: Verify ----------------------------------------------------------
print_step $STEP "Verification"

# Test Function App endpoint
if $DEPLOY_FUNCTION; then
    info "Testing Function App endpoint..."
    FUNC_URL="https://${FUNC_APP_NAME}.azurewebsites.net/api/process-newsletter"
    TEST_PAYLOAD='{"body_html":"<html><body><h1>Test</h1><p>Hello</p></body></html>","subject":"Test Newsletter","received_date":"2025-01-01"}'

    HTTP_CODE=$(curl -s -o /tmp/sdc-func-test-response.json -w "%{http_code}" \
        -X POST "${FUNC_URL}" \
        -H "Content-Type: application/json" \
        -H "x-functions-key: ${FUNCTION_KEY}" \
        -d "${TEST_PAYLOAD}" 2>/dev/null || echo "000")

    if [[ "${HTTP_CODE}" == "200" ]]; then
        ok "Function App returned 200 OK"
        RESPONSE_SLUG=$(python3 -c "import json; print(json.load(open('/tmp/sdc-func-test-response.json'))['slug'])" 2>/dev/null || echo "")
        if [[ -n "${RESPONSE_SLUG}" ]]; then
            ok "Response contains valid slug: ${RESPONSE_SLUG}"
        fi
    else
        warn "Function App returned HTTP ${HTTP_CODE} (may need a few minutes to warm up)"
    fi
    rm -f /tmp/sdc-func-test-response.json
fi

# Check Logic App state
if $DEPLOY_LOGIC_APP; then
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

# Check connection statuses
if $DEPLOY_CONNECTIONS; then
    for CONN_NAME in "${O365_CONN_NAME}" "${GITHUB_CONN_NAME}"; do
        CONN_STATUS=$(az resource show \
            --resource-group "${RESOURCE_GROUP}" \
            --resource-type "Microsoft.Web/connections" \
            --name "${CONN_NAME}" \
            --query "properties.statuses[0].status" -o tsv 2>/dev/null || echo "Unknown")
        if [[ "${CONN_STATUS}" == "Connected" ]]; then
            ok "Connection '${CONN_NAME}': Connected"
        else
            warn "Connection '${CONN_NAME}': ${CONN_STATUS} (authorize in Azure Portal if needed)"
        fi
    done
fi

# --- Summary ------------------------------------------------------------------
print_header "Deployment Complete"

echo -e "  ${CHECK} Resource Group:  ${RESOURCE_GROUP}"
$DEPLOY_FUNCTION && echo -e "  ${CHECK} Function App:   ${FUNC_APP_NAME}"
$DEPLOY_CONNECTIONS && echo -e "  ${CHECK} Connections:    ${O365_CONN_NAME}, ${GITHUB_CONN_NAME}"
$DEPLOY_LOGIC_APP && echo -e "  ${CHECK} Logic App:      ${LOGIC_APP_NAME}"
echo ""
echo -e "  ${INFO} Pipeline flow:"
echo "     Email → O365 folder → Logic App (5-min poll)"
echo "     → Azure Function (process) → GitHub Actions (commit)"
echo "     → build.yml (deploy to GitHub Pages)"
echo ""
echo -e "  ${INFO} To monitor: https://portal.azure.com"
echo ""
