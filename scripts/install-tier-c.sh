#!/usr/bin/env bash
# ============================================================
# Xcerebro 2.0 — Tier C Installer
# ============================================================
# Installs the existing 199 Xcerebro markdown agent presets
# from the public xcerebroai/Xcerebro-Agents repo into the
# buyer's Claude Code agent directory.
#
# Tier C agents are NOT autonomous. They install as Claude Code
# personality presets and respond when invoked by name.
#
# Usage:
#   ./scripts/install-tier-c.sh
# ============================================================

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

CLAUDE_AGENTS_DIR="$HOME/.claude/agents"
TIER_C_REPO="https://github.com/xcerebroai/Xcerebro-Agents.git"
TEMP_DIR="/tmp/xcerebro-tier-c-$$"

echo -e "${BLUE}===========================================${NC}"
echo -e "${BLUE}  Xcerebro Tier C Agents — Installer${NC}"
echo -e "${BLUE}===========================================${NC}\n"

# Check 1: Claude Code is installed
if [ ! -d "$HOME/.claude" ]; then
    echo -e "${YELLOW}⚠${NC} ~/.claude directory not found"
    echo "Claude Code may not be installed yet."
    echo ""
    echo "Install Claude Code first:"
    echo "  https://docs.claude.com/en/docs/claude-code"
    echo ""
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create agents directory if it doesn't exist
mkdir -p "$CLAUDE_AGENTS_DIR"
echo -e "${GREEN}✓${NC} Target directory: $CLAUDE_AGENTS_DIR"

# Check 2: git is available
if ! command -v git &> /dev/null; then
    echo -e "${RED}✗${NC} git is not installed."
    echo "Install git: https://git-scm.com/downloads"
    exit 1
fi

# Clone the Tier C repo to a temp location
echo ""
echo "Cloning Tier C agents from public repo..."
echo "  Repo: $TIER_C_REPO"

if [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

git clone --depth 1 "$TIER_C_REPO" "$TEMP_DIR" 2>&1 | tail -3

# Verify the clone worked and has agent files
if [ ! -d "$TEMP_DIR" ]; then
    echo -e "${RED}✗${NC} Clone failed."
    echo ""
    echo "Possible causes:"
    echo "  - Repo is private (you need to be a member)"
    echo "  - Network issue"
    echo "  - Repo URL changed"
    echo ""
    echo "If you're a paying Xcerebro member, contact support@xcerebro.ai"
    exit 1
fi

# Find the agents folder inside the clone
AGENTS_SOURCE=""
for candidate in "$TEMP_DIR/agents" "$TEMP_DIR/.claude/agents" "$TEMP_DIR"; do
    if [ -d "$candidate" ] && [ "$(find "$candidate" -name '*.md' -maxdepth 2 | head -1)" ]; then
        AGENTS_SOURCE="$candidate"
        break
    fi
done

if [ -z "$AGENTS_SOURCE" ]; then
    echo -e "${RED}✗${NC} No agent .md files found in cloned repo."
    rm -rf "$TEMP_DIR"
    exit 1
fi

echo -e "${GREEN}✓${NC} Found agents at: $AGENTS_SOURCE"

# Count files before copy
EXISTING_COUNT=$(find "$CLAUDE_AGENTS_DIR" -name '*.md' 2>/dev/null | wc -l | tr -d ' ')
INCOMING_COUNT=$(find "$AGENTS_SOURCE" -name '*.md' 2>/dev/null | wc -l | tr -d ' ')

echo ""
echo "Existing agents in ~/.claude/agents/: $EXISTING_COUNT"
echo "Incoming Tier C agents:               $INCOMING_COUNT"
echo ""

if [ "$EXISTING_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠${NC} You have $EXISTING_COUNT existing agent files."
    read -p "Overwrite existing agents with Tier C versions? [y/N] " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Skipping copy. Tier C agents NOT installed."
        rm -rf "$TEMP_DIR"
        exit 0
    fi
fi

# Copy all .md files preserving directory structure
echo "Copying Tier C agents..."
cp -r "$AGENTS_SOURCE"/. "$CLAUDE_AGENTS_DIR"/

FINAL_COUNT=$(find "$CLAUDE_AGENTS_DIR" -name '*.md' 2>/dev/null | wc -l | tr -d ' ')

echo -e "${GREEN}✓${NC} Tier C install complete."
echo "  Total agents now in ~/.claude/agents/: $FINAL_COUNT"
echo ""

# Cleanup
rm -rf "$TEMP_DIR"

echo -e "${BLUE}===========================================${NC}"
echo -e "${BLUE}  Next steps${NC}"
echo -e "${BLUE}===========================================${NC}"
echo ""
echo "1. Open Claude Code in your terminal"
echo "2. Try: 'Use the Backend Architect to design a schema for X'"
echo "3. Claude Code will activate the matching Tier C agent"
echo ""
echo "Tier C is for ON-DEMAND specialist work."
echo "For autonomous workflows, see Tier A + Tier B (deployed via Railway)."
echo ""
echo "Welcome to the Xcerebro workforce, Operator."
