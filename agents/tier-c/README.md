# Tier C — On-Demand Specialist Presets

> The existing 199 Xcerebro agents. These do NOT run autonomously. They install as Claude Code presets and respond when called by name.

---

## What's in this tier

The original 199 markdown agents organized into 13 divisions:

| Division | Count | Examples |
|---|---|---|
| Engineering | ~50 | Frontend Dev, Backend Architect, DevOps Engineer, Mobile Dev |
| Product | ~12 | Product Manager, Product Designer, UX Researcher |
| Design | ~15 | Brand Designer, UI/UX, Motion Design, Illustration |
| Marketing | ~20 | (overlaps with Tier B autonomous) |
| Specialized | ~25 | Data Scientist, ML Engineer, Game Dev, Spatial Computing |
| Sales | ~10 | (overlaps with Tier B autonomous) |
| Paid Media | ~8 | (overlaps with Tier B autonomous) |
| Finance | ~6 | (overlaps with Tier A CFO) |
| Support & Ops | ~12 | (overlaps with Tier A) |
| Real Estate (REI) | ~15 | Wholesale Specialist, Acquisitions Lead |
| Project Mgmt | ~8 | (overlaps with Tier A Project Manager) |
| Testing & QA | ~10 | QA Engineer, Test Automation, Security Auditor |
| Academic Research | ~8 | Research Writer, Peer Review, Citation Specialist |

**Total: ~199 agents.** (Some overlap with Tier A/B autonomous agents — that's by design. The autonomous version handles ongoing work; the Markdown preset handles ad-hoc requests.)

---

## How buyers install Tier C

These ship as the original Markdown files in this folder. Buyers install via:

```bash
# Inside Claude Code
./scripts/install.sh --tool claude-code
```

This copies all .md files from `agents/tier-c/` to the buyer's `~/.claude/agents/` folder.

After install, the buyer can invoke any of them in Claude Code by name:

```
> Use the Backend Architect to design the schema for the new feature.
```

Claude Code activates that personality preset and responds in that role.

---

## What Tier C does NOT do

- ❌ Run on a schedule
- ❌ Talk to other agents
- ❌ Call external APIs autonomously
- ❌ Delegate to Tier A or B agents
- ❌ Hit approval gates

They are **prompts**, not **autonomous software.** They make Claude Code responses better in specialized domains. That's their job.

---

## Why we keep them

Two reasons:

1. **They have real value.** When a buyer needs to design a database schema, write a marketing campaign, debug a complex piece of code, or research a real estate deal, having a specialized agent that brings that expertise on demand is genuinely useful.

2. **Continuity for existing buyers.** Operators who already use the 199 don't lose anything. Xcerebro 2.0 layers on top — the autonomous workforce is additive, not replacement.

---

## Files in this folder

The actual 199 markdown files are not included in this repo by default to keep file size manageable. They install separately:

```bash
# After running the main setup, run:
./scripts/install.sh --tool claude-code

# This pulls the latest 199 from the public Xcerebro Agents repo
# (xcerebro.ai/agents.html) and copies them to your local Claude Code.
```

If you need them included in this repo for your build, fork the public agents repo and add the symlink.

---

## Summary

- Tier A (18) = leadership orchestrators, autonomous
- Tier B (~80) = operational specialists, autonomous, delegated to by Tier A
- **Tier C (~99) = on-demand presets, NOT autonomous, install separately**

When you bought Xcerebro 2.0, you got all three tiers. They serve different jobs.
