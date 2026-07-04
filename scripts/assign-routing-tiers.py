"""
Assign model_routing tiers to agent YAMLs (one-time migration for v2.1 routing).

Rules (id + role text keywords):
  premium  — money/legal/customer-facing-risk agents (Claude Opus only)
  economy  — bulk/low-stakes housekeeping agents (DeepSeek, no fallback)
  balanced — everyone else (DeepSeek primary, Claude Sonnet fallback) [default]

Appends a model_routing block to each YAML (text append preserves comments).
Idempotent: skips files that already have model_routing.
"""

import re
from pathlib import Path
import yaml

AGENTS_DIR = Path(__file__).resolve().parent.parent / "agents"

PREMIUM_KEYWORDS = (
    "cfo", "finance", "legal", "compliance", "contract", "dispute", "tax",
    "invoice", "refund", "attorney", "privacy", "ip-defender", "high-ticket",
    "closer", "acquisition", "disposition", "title",
)
ECONOMY_KEYWORDS = (
    "cleaner", "tracker", "monitor", "collector", "scraper", "repurpos",
    "curator", "transcri", "tagger", "formatter",
)


def pick_tier(agent_id: str, role: str) -> str:
    # Classify on the agent id only — role prose is full of false positives
    # ("optimizes titles" -> title, "repurposing" in the CMO role). The id is
    # the curated signal. Economy first: a bulk monitor/tracker stays cheap
    # even if its id also mentions a money domain (foreclosure-tracker).
    text = agent_id.lower()
    if any(k in text for k in ECONOMY_KEYWORDS):
        return "economy"
    if any(k in text for k in PREMIUM_KEYWORDS):
        return "premium"
    return "balanced"


def main() -> None:
    counts = {"premium": 0, "economy": 0, "balanced": 0, "skipped": 0}
    for tier_dir in ("tier-a", "tier-b"):
        for path in sorted((AGENTS_DIR / tier_dir).glob("*.yaml")):
            raw = path.read_text(encoding="utf-8")
            data = yaml.safe_load(raw)
            if "model_routing" in data:
                counts["skipped"] += 1
                continue
            tier = pick_tier(data.get("id", path.stem), data.get("role", ""))
            block = f"\nmodel_routing:\n  tier: {tier}\n"
            path.write_text(raw.rstrip("\n") + "\n" + block, encoding="utf-8")
            counts[tier] += 1
            print(f"{tier:8s}  {path.stem}")
    print(f"\nDone: {counts}")


if __name__ == "__main__":
    main()
