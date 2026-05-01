#!/usr/bin/env bash
# ============================================================
# Xcerebro 2.0 — Post-Install Verification
# ============================================================
# Runs after Railway deploy. Verifies the agent runtime is healthy,
# n8n is reachable, Dify is reachable, and Slack is configured.
#
# Usage:
#   chmod +x scripts/verify.sh
#   ./scripts/verify.sh
# ============================================================

set -e

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

check_pass() { echo -e "${GREEN}✓${NC} $1"; }
check_fail() { echo -e "${RED}✗${NC} $1"; }
check_warn() { echo -e "${YELLOW}⚠${NC} $1"; }

# Load env
if [ -f ".env" ]; then
    source .env
else
    check_fail "No .env file found. Run install.sh first."
    exit 1
fi

# ============================================================
print_header "1. Agent Runtime Health Check"
# ============================================================

if [ -z "$AGENT_RUNTIME_URL" ]; then
    check_fail "AGENT_RUNTIME_URL not set"
    exit 1
fi

echo "Checking $AGENT_RUNTIME_URL/health ..."
HEALTH=$(curl -s --max-time 10 "$AGENT_RUNTIME_URL/health" || echo "FAILED")

if echo "$HEALTH" | grep -q '"status":"ok"'; then
    check_pass "Agent runtime is healthy"
    AGENTS_LOADED=$(echo "$HEALTH" | grep -o '"agents_loaded":[0-9]*' | cut -d: -f2)
    CREWS_LOADED=$(echo "$HEALTH" | grep -o '"crews_loaded":[0-9]*' | cut -d: -f2)
    echo "  Agents loaded: $AGENTS_LOADED"
    echo "  Crews loaded:  $CREWS_LOADED"

    if [ "$AGENTS_LOADED" -lt 15 ]; then
        check_warn "Fewer agents loaded than expected (expected 18)"
    fi
else
    check_fail "Agent runtime not responding"
    echo "Response: $HEALTH"
    echo "Check Railway logs for the agent runtime container."
fi

# ============================================================
print_header "2. List Loaded Agents"
# ============================================================

if [ -z "$AGENT_RUNTIME_API_KEY" ]; then
    check_warn "AGENT_RUNTIME_API_KEY not set, skipping authenticated checks"
else
    AGENTS=$(curl -s --max-time 10 \
        -H "x-api-key: $AGENT_RUNTIME_API_KEY" \
        "$AGENT_RUNTIME_URL/agents" || echo "FAILED")

    if echo "$AGENTS" | grep -q "tier_a"; then
        check_pass "Agent listing endpoint working"
        # Extract Tier A agent IDs
        echo "$AGENTS" | grep -o '"id":"[^"]*"' | head -5
        echo "  ... (run 'curl -H \"x-api-key: \$AGENT_RUNTIME_API_KEY\" $AGENT_RUNTIME_URL/agents' for full list)"
    else
        check_fail "Agent listing failed"
        echo "Response: $AGENTS"
    fi
fi

# ============================================================
print_header "3. n8n Reachability"
# ============================================================

if [ -z "$N8N_BASE_URL" ]; then
    check_warn "N8N_BASE_URL not set, skipping n8n check"
else
    echo "Checking $N8N_BASE_URL ..."
    N8N_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$N8N_BASE_URL" || echo "FAILED")

    if [ "$N8N_STATUS" = "200" ] || [ "$N8N_STATUS" = "302" ] || [ "$N8N_STATUS" = "401" ]; then
        check_pass "n8n is reachable (HTTP $N8N_STATUS)"
    else
        check_fail "n8n not reachable (HTTP $N8N_STATUS)"
    fi
fi

# ============================================================
print_header "4. Dify Reachability"
# ============================================================

if [ -z "$DIFY_BASE_URL" ]; then
    check_warn "DIFY_BASE_URL not set, skipping Dify check"
else
    echo "Checking $DIFY_BASE_URL ..."
    DIFY_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$DIFY_BASE_URL" || echo "FAILED")

    if [ "$DIFY_STATUS" = "200" ] || [ "$DIFY_STATUS" = "302" ]; then
        check_pass "Dify is reachable (HTTP $DIFY_STATUS)"
    else
        check_fail "Dify not reachable (HTTP $DIFY_STATUS)"
    fi
fi

# ============================================================
print_header "5. Slack Bot Connectivity"
# ============================================================

if [ -z "$SLACK_BOT_TOKEN" ]; then
    check_warn "SLACK_BOT_TOKEN not set"
else
    SLACK_RESPONSE=$(curl -s --max-time 10 \
        -H "Authorization: Bearer $SLACK_BOT_TOKEN" \
        "https://slack.com/api/auth.test" || echo '{"ok":false}')

    if echo "$SLACK_RESPONSE" | grep -q '"ok":true'; then
        BOT_NAME=$(echo "$SLACK_RESPONSE" | grep -o '"user":"[^"]*"' | cut -d'"' -f4)
        TEAM=$(echo "$SLACK_RESPONSE" | grep -o '"team":"[^"]*"' | cut -d'"' -f4)
        check_pass "Slack bot connected as @$BOT_NAME in $TEAM"
    else
        check_fail "Slack bot connection failed"
        echo "Response: $SLACK_RESPONSE"
    fi
fi

# ============================================================
print_header "6. Test Agent Invocation (Optional)"
# ============================================================

if [ -n "$AGENT_RUNTIME_API_KEY" ] && [ "$AGENTS_LOADED" -gt 0 ]; then
    echo "Running a smoke test invocation of auto-ceo..."

    TEST_RESPONSE=$(curl -s --max-time 60 \
        -X POST "$AGENT_RUNTIME_URL/agents/auto-ceo/invoke" \
        -H "x-api-key: $AGENT_RUNTIME_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{
            "task": "Smoke test. Reply with exactly: \"Xcerebro 2.0 is online.\"",
            "context": {},
            "require_approval": false
        }' || echo "FAILED")

    if echo "$TEST_RESPONSE" | grep -q "Xcerebro"; then
        check_pass "Agent invocation works end-to-end!"
    else
        check_warn "Agent invocation returned unexpected response"
        echo "Response (first 200 chars): ${TEST_RESPONSE:0:200}"
    fi
fi

# ============================================================
print_header "Summary"
# ============================================================

cat << 'EOF'
If all checks passed: you're ready to activate workflows in n8n.

If any failed:
  1. Read the error message above
  2. Check Railway logs for the failing service
  3. See docs/08-troubleshooting.md
  4. Ask in Skool VIP if stuck

Next: open n8n and import the workflows from n8n-workflows/.
Activate ONLY 01-daily-kpi-brief first. Watch it run for 7 days.
Then expand from there per docs/09-upgrade-path.md.
EOF

echo ""
