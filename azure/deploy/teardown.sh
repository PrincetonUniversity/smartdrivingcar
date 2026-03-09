#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# SmartDrivingCar Azure Newsletter Pipeline — Teardown Script
# ==============================================================================
# Removes all Azure resources created by the deploy script.
#
# Usage:
#   ./teardown.sh                     # Interactive teardown (prompts for confirmation)
#   ./teardown.sh --resource-group rg-smartdrivingcar  # Specify resource group
#   ./teardown.sh --yes               # Skip confirmation prompt
#   ./teardown.sh --help              # Show help
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

ok()   { echo -e "  ${CHECK} $1"; }
fail() { echo -e "  ${CROSS} $1"; exit 1; }
warn() { echo -e "  ${WARN} $1"; }
info() { echo -e "  ${INFO} $1"; }

# --- Parse Arguments ----------------------------------------------------------
RESOURCE_GROUP=""
AUTO_YES=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --resource-group|-g)
            RESOURCE_GROUP="$2"
            shift 2
            ;;
        --yes|-y)
            AUTO_YES=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Tear down the Azure newsletter pipeline resources."
            echo ""
            echo "Options:"
            echo "  --resource-group, -g NAME   Resource group to delete (default: rg-smartdrivingcar)"
            echo "  --yes, -y                   Skip confirmation prompt"
            echo "  --help, -h                  Show this help"
            exit 0
            ;;
        *)
            fail "Unknown option: $1. Use --help for usage."
            ;;
    esac
done

# --- Prerequisites ------------------------------------------------------------
print_header "SmartDrivingCar Newsletter Pipeline — Teardown"

if ! command -v az &>/dev/null; then
    fail "Azure CLI (az) not found. Install: https://aka.ms/install-azure-cli"
fi

if ! az account show &>/dev/null; then
    fail "Not logged in to Azure. Run: az login"
fi

SUBSCRIPTION=$(az account show --query name -o tsv)
ok "Logged in to Azure (subscription: ${SUBSCRIPTION})"

# --- Determine Resource Group -------------------------------------------------
if [[ -z "${RESOURCE_GROUP}" ]]; then
    read -rp "  $(echo -e "${BOLD}")Resource group to delete$(echo -e "${NC}") [rg-smartdrivingcar]: " RESOURCE_GROUP
    RESOURCE_GROUP="${RESOURCE_GROUP:-rg-smartdrivingcar}"
fi

# Check if resource group exists
if ! az group show --name "${RESOURCE_GROUP}" &>/dev/null; then
    warn "Resource group '${RESOURCE_GROUP}' does not exist. Nothing to tear down."
    exit 0
fi

# --- List Resources -----------------------------------------------------------
echo ""
info "Resources in '${RESOURCE_GROUP}':"
echo ""
az resource list \
    --resource-group "${RESOURCE_GROUP}" \
    --query "[].{Name:name, Type:type}" \
    --output table 2>/dev/null || true
echo ""

# --- Confirm ------------------------------------------------------------------
if ! $AUTO_YES; then
    echo -e "${RED}${BOLD}  WARNING: This will permanently delete ALL resources in '${RESOURCE_GROUP}'.${NC}"
    echo -e "${RED}${BOLD}  This action cannot be undone.${NC}"
    echo ""
    read -rp "  Type the resource group name to confirm: " CONFIRM
    if [[ "${CONFIRM}" != "${RESOURCE_GROUP}" ]]; then
        echo "  Aborted. Names did not match."
        exit 1
    fi
fi

# --- Delete Resources Individually (for visibility) --------------------------
print_header "Deleting Resources"

# Delete Logic App
LOGIC_APPS=$(az logic workflow list --resource-group "${RESOURCE_GROUP}" --query "[].name" -o tsv 2>/dev/null || true)
for LA in ${LOGIC_APPS}; do
    info "Deleting Logic App: ${LA}..."
    az logic workflow delete --name "${LA}" --resource-group "${RESOURCE_GROUP}" --yes --output none 2>/dev/null && \
        ok "Logic App '${LA}' deleted" || \
        warn "Could not delete Logic App '${LA}'"
done

# Delete API connections
CONNECTIONS=$(az resource list --resource-group "${RESOURCE_GROUP}" --resource-type "Microsoft.Web/connections" --query "[].name" -o tsv 2>/dev/null || true)
for CONN in ${CONNECTIONS}; do
    info "Deleting API connection: ${CONN}..."
    az resource delete --resource-group "${RESOURCE_GROUP}" --resource-type "Microsoft.Web/connections" --name "${CONN}" --output none 2>/dev/null && \
        ok "Connection '${CONN}' deleted" || \
        warn "Could not delete connection '${CONN}'"
done

# Delete Function App
FUNC_APPS=$(az functionapp list --resource-group "${RESOURCE_GROUP}" --query "[].name" -o tsv 2>/dev/null || true)
for FA in ${FUNC_APPS}; do
    info "Deleting Function App: ${FA}..."
    az functionapp delete --name "${FA}" --resource-group "${RESOURCE_GROUP}" --output none 2>/dev/null && \
        ok "Function App '${FA}' deleted" || \
        warn "Could not delete Function App '${FA}'"
done

# Delete App Service Plans (created automatically with Function Apps)
APP_PLANS=$(az appservice plan list --resource-group "${RESOURCE_GROUP}" --query "[].name" -o tsv 2>/dev/null || true)
for AP in ${APP_PLANS}; do
    info "Deleting App Service Plan: ${AP}..."
    az appservice plan delete --name "${AP}" --resource-group "${RESOURCE_GROUP}" --yes --output none 2>/dev/null && \
        ok "App Service Plan '${AP}' deleted" || \
        warn "Could not delete App Service Plan '${AP}'"
done

# Delete Storage Accounts
STORAGE_ACCOUNTS=$(az storage account list --resource-group "${RESOURCE_GROUP}" --query "[].name" -o tsv 2>/dev/null || true)
for SA in ${STORAGE_ACCOUNTS}; do
    info "Deleting Storage Account: ${SA}..."
    az storage account delete --name "${SA}" --resource-group "${RESOURCE_GROUP}" --yes --output none 2>/dev/null && \
        ok "Storage Account '${SA}' deleted" || \
        warn "Could not delete Storage Account '${SA}'"
done

# Delete Application Insights (may have been created automatically)
APP_INSIGHTS=$(az resource list --resource-group "${RESOURCE_GROUP}" --resource-type "Microsoft.Insights/components" --query "[].name" -o tsv 2>/dev/null || true)
for AI in ${APP_INSIGHTS}; do
    info "Deleting Application Insights: ${AI}..."
    az resource delete --resource-group "${RESOURCE_GROUP}" --resource-type "Microsoft.Insights/components" --name "${AI}" --output none 2>/dev/null && \
        ok "Application Insights '${AI}' deleted" || \
        warn "Could not delete Application Insights '${AI}'"
done

# --- Delete Resource Group ----------------------------------------------------
info "Deleting resource group '${RESOURCE_GROUP}'..."
az group delete --name "${RESOURCE_GROUP}" --yes --no-wait --output none 2>/dev/null && \
    ok "Resource group '${RESOURCE_GROUP}' deletion initiated (runs in background)" || \
    warn "Could not delete resource group"

# --- Summary ------------------------------------------------------------------
print_header "Teardown Complete"

echo -e "  ${CHECK} All resources in '${RESOURCE_GROUP}' have been deleted or deletion is in progress."
echo ""
echo -e "  ${INFO} Resource group deletion runs asynchronously."
echo "     Check status: az group show --name ${RESOURCE_GROUP}"
echo ""
echo -e "  ${INFO} The GitHub Actions workflow (.github/workflows/receive-newsletter.yml)"
echo "     remains in the repo but will be inert without the Azure pipeline."
echo ""
