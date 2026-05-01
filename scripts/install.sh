#!/usr/bin/env bash
# ============================================================
# Xcerebro 2.0 — Install Helper
# ============================================================
# Helps the buyer with local checks before deploying to Railway.
# This does NOT deploy to Railway — Railway deploys are done via
# the Railway dashboard (one-click templates).
#
# Usage:
#   chmod +x scripts/install.sh
#   ./scripts/install.sh
# ============================================================

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "\n${BLUE}===========================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}===========================================${NC}\n"
}

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# ============================================================
print_header "Xcerebro 2.0 Pre-Flight Check"
# ============================================================

echo "Checking your local environment before Railway deploy..."
echo ""

# Check 1: Are we in the right directory?
if [ ! -f "README.md" ] || [ ! -d "agents" ] || [ ! -d "crew" ]; then
    check_fail "Not in xcerebro-2.0 root directory"
    echo "Please cd into the xcerebro-2.0 folder and run again."
    exit 1
fi
check_pass "In xcerebro-2.0 root directory"

# Check 2: .env file
if [ ! -f ".env" ]; then
    check_warn ".env file not found"
    echo "Creating from .env.example..."
    cp .env.example .env
    check_warn "Edit .env with your API keys before deploying"
else
    check_pass ".env file exists"
fi

# Check 3: Required env vars (check that they're not empty/default)
print_header "Checking Critical Environment Variables"

source .env 2>/dev/null || true

CRITICAL_VARS=(
    "ANTHROPIC_API_KEY"
    "AGENT_RUNTIME_API_KEY"
)

ALL_GOOD=true
for var in "${CRITICAL_VARS[@]}"; do
    value="${!var}"
    if [ -z "$value" ] || [ "$value" = "sk-ant-api03-..." ] || [ "$value" = "generate-a-random-string-here" ]; then
        check_fail "$var is not set"
        ALL_GOOD=false
    else
        check_pass "$var is set"
    fi
done

if [ "$ALL_GOOD" = false ]; then
    echo ""
    echo -e "${YELLOW}⚠ Some critical env vars are missing.${NC}"
    echo "Edit .env and fill them in before deploying."
fi

# Check 4: Agent files
print_header "Validating Agent Definitions"

AGENT_COUNT=$(find agents/tier-a -name "*.yaml" 2>/dev/null | wc -l | tr -d ' ')
echo "Tier A agents found: $AGENT_COUNT"

if [ "$AGENT_COUNT" -eq 0 ]; then
    check_fail "No Tier A agents loaded"
elif [ "$AGENT_COUNT" -lt 18 ]; then
    check_warn "Expected 18 Tier A agents, found $AGENT_COUNT"
else
    check_pass "All 18 Tier A agents present"
fi

# Check 5: Workflow files
WORKFLOW_COUNT=$(find n8n-workflows -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
echo "n8n workflows found: $WORKFLOW_COUNT"

if [ "$WORKFLOW_COUNT" -gt 0 ]; then
    check_pass "$WORKFLOW_COUNT pre-built workflows ready to import"
fi

# Check 6: Optional - Docker availability
print_header "Optional: Local Docker Test"

if command -v docker &> /dev/null; then
    check_pass "Docker is installed"

    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        check_pass "Docker Compose is available"
        echo ""
        echo "You can test locally with:"
        echo "  docker compose up -d"
        echo ""
        echo "Or skip straight to Railway deploy (recommended)."
    else
        check_warn "Docker Compose not found (optional for Railway deploy)"
    fi
else
    check_warn "Docker not installed (only needed for local testing)"
    echo "Railway deploy doesn't need Docker locally."
fi

# Check 7: Git status
print_header "Git Repo Status"

if [ -d ".git" ]; then
    check_pass "Git repo initialized"

    if git remote get-url origin &> /dev/null; then
        ORIGIN=$(git remote get-url origin)
        check_pass "Remote 'origin' set: $ORIGIN"
    else
        check_warn "No remote set. You'll need to push to GitHub before Railway deploys."
    fi
else
    check_warn "Not a git repo. Initialize with: git init"
fi

# ============================================================
print_header "Next Steps"
# ============================================================

cat << 'EOF'
1. Edit .env with your real API keys
2. Push this repo to your GitHub (private)
3. Go to railway.com and deploy:
   a. n8n template:  https://railway.com/deploy/n8n
   b. Dify template: https://railway.com/deploy/dify-ai-workflow
   c. This repo as Agent Runtime
4. Configure env vars in Railway (copy from .env)
5. Import n8n workflows from n8n-workflows/
6. Activate the Daily KPI Brief workflow
7. Wait until tomorrow morning — you should get a Slack brief

For detailed walkthrough: docs/01-quick-start.md
For Railway specifics:    docs/02-railway-deploy.md
For troubleshooting:      docs/08-troubleshooting.md

Welcome to autonomy, Operator.
EOF

echo ""
