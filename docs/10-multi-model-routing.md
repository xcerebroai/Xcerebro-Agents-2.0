# Multi-Model Routing — v2.1 Feature Guide

> **Status:** Infrastructure built and shipped in v2.0 codebase. Disabled by default. Flip `ROUTING_ENABLED=true` in your `.env` to turn it on.
>
> **What it does:** Routes agent tasks to the cheapest model that can handle them. Cuts LLM costs 70-90% for typical workloads.

---

## The 30-second pitch

Your CEO agent doesn't need a $15-per-million-tokens model to write a daily Slack briefing. DeepSeek can do it for $0.27 per million — **55x cheaper.**

But your Compliance agent reviewing a contract? **Use Claude Opus.** That's not where you cheap out.

Multi-model routing automates this decision per task. The cheap model handles the bulk of the work. The expensive model only fires when escalation is needed.

---

## How the three tiers work

### Tier 1: Economy
- **Default model:** DeepSeek Flash
- **Fallback:** None — accepts failures
- **Best for:** High-volume, low-stakes (CRM cleaning, data tagging, basic replies)
- **Typical cost:** ~$3-15/month for active workforce

### Tier 2: Balanced (DEFAULT)
- **Default model:** DeepSeek v4 Pro
- **Fallback:** Claude Sonnet 4 (on retry/keyword/category trigger)
- **Best for:** Most agents (copy writing, research, summaries, hooks)
- **Typical cost:** ~$25-75/month for active workforce

### Tier 3: Premium
- **Default model:** Claude Opus 4
- **Fallback:** None — already at premium
- **Best for:** High-stakes agents (Compliance, Title Specialist, CFO, anything customer-facing or legal/financial)
- **Typical cost:** ~$200-500/month for active workforce

---

## Per-agent configuration

Each agent's YAML file can set its own routing preference:

```yaml
# agents/tier-b/copy-writer.yaml
name: copy-writer
role: Copy Writer
tier: B
pod: marketing
goal: Write punchy hooks and copy

# NEW in v2.1 — routing config
model_routing:
  tier: balanced  # economy | balanced | premium
  # Optional overrides:
  primary: deepseek-v4-pro
  fallback: claude-sonnet-4-6
  premium: claude-opus-4-7
  escalate_on_retry_count: 2
  escalate_on_keywords:
    - legal
    - compliance
    - contract
  force_premium: false
```

**If you don't add `model_routing` to an agent's YAML, it inherits the default tier from your `.env` (`ROUTING_DEFAULT_TIER`).**

---

## Recommended tier per agent type

The defaults below are sensible starting points. Adjust based on your business risk tolerance.

### Premium tier (high stakes — DON'T cheap out)

- Compliance Officer
- Title Specialist
- CFO
- Legal Researcher
- Customer Dispute Handler
- Anything that drafts contracts, refund decisions, or regulatory communications

### Balanced tier (most agents)

- CEO Orchestrator
- COO Orchestrator
- CMO Orchestrator
- Sales Manager
- DM Agent
- Hook Writer
- Copy Chief
- Email Copywriter
- Most Tier B specialists

### Economy tier (high volume, low stakes)

- CRM Cleaner
- Data Tagger
- Lead Sorter
- Initial DM Triage (before human review)
- Comment-to-DM Triage
- Daily Activity Logger
- Internal Reporting Generator

---

## Auto-escalation triggers

Even when routed to a cheap model, the system will auto-escalate to the premium model if:

1. **Retry count exceeds threshold** — cheap model retried 2x and failed → escalate
2. **Keywords detected** — task mentions "legal", "compliance", "contract", "lawsuit", "refund", "fraud", "medical" → escalate
3. **Category matches** — task category is "compliance", "finance_critical", "customer_facing_dispute" → escalate
4. **Force premium flag** — agent or task explicitly requests premium

You can customize these triggers per agent in the YAML.

---

## Real cost example

Here's a buyer running a typical workforce: 200 agent tasks/day across 9 workflows.

### Without routing (v2.0 default — all Claude)

| Agent | Tasks/day | Model | Daily cost | Monthly |
|---|---|---|---|---|
| All agents | 200 | Claude Opus | ~$15 | **~$450** |

### With routing — Balanced tier

| Agent type | Tasks/day | Routed to | Daily cost | Monthly |
|---|---|---|---|---|
| Routine (CRM, tagging) | 80 | DeepSeek Flash | ~$0.10 | $3 |
| Standard (copy, hooks) | 100 | DeepSeek v4 Pro | ~$1.20 | $36 |
| Escalated (compliance) | 15 | Claude Sonnet | ~$0.60 | $18 |
| High-stakes (Compliance, CFO) | 5 | Claude Opus | ~$0.40 | $12 |
| **Total** | 200 | — | **~$2.30** | **~$69** |

**Savings: $381/month (85% off)**

---

## How to enable routing

### Step 1: Get API keys for the models you want

- **DeepSeek** (essential for cost savings): https://platform.deepseek.com
- **Anthropic** (for fallback/premium): https://console.anthropic.com
- **OpenAI** (optional alternative): https://platform.openai.com
- **Groq** (optional, ultra-fast Llama): https://console.groq.com

### Step 2: Add keys to your `.env`

```bash
ANTHROPIC_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...

# Enable routing
ROUTING_ENABLED=true
ROUTING_DEFAULT_TIER=balanced
ROUTING_MAX_RETRIES=2
```

### Step 3: Restart the runtime

```bash
docker compose restart agent-runtime
# or in Railway, just push the env var change
```

### Step 4: Verify

Check the `/health` endpoint for available providers:

```bash
curl https://your-runtime.up.railway.app/health
# Should show: configured_providers: ["anthropic", "deepseek"]
```

### Step 5: Watch the dashboard

The operator dashboard now shows per-model spend. After a day of running, you'll see the breakdown — and the savings.

---

## Programmatic usage (for custom workflows)

If you're writing custom code that uses the routing layer:

```python
from crew.routing import (
    RoutingExecutor,
    RoutingPolicy,
    RoutingTier,
    TIER_POLICIES,
)

executor = RoutingExecutor()

# Use a pre-defined tier policy
policy = TIER_POLICIES[RoutingTier.BALANCED]

response = executor.execute(
    agent_id="copy-writer",
    policy=policy,
    messages=[
        {"role": "user", "content": "Write me 3 hook variations for a TikTok about subject-to deals"},
    ],
    system="You are a punchy copywriter for real estate investors.",
    category="content",  # used for category-based escalation rules
    max_tokens=2000,
)

print(response.content)
print(f"Cost: ~${(response.input_tokens/1000 * 0.00027) + (response.output_tokens/1000 * 0.0011):.4f}")
print(f"Model used: {response.model_id}")
```

---

## Loading routing from agent YAML

When parsing agent definitions, use `load_policy_from_yaml`:

```python
import yaml
from crew.routing import load_policy_from_yaml, RoutingExecutor

with open("agents/tier-b/copy-writer.yaml") as f:
    agent_data = yaml.safe_load(f)

policy = load_policy_from_yaml(agent_data)

executor = RoutingExecutor()
response = executor.execute(
    agent_id=agent_data["name"],
    policy=policy,
    messages=[{"role": "user", "content": task}],
)
```

---

## Monitoring spend

The router logs every call. Get a spend summary:

```python
executor = RoutingExecutor()
summary = executor.get_spend_summary(hours=24)

# Returns:
# {
#   "period_hours": 24,
#   "total_calls": 187,
#   "total_cost_usd": 2.31,
#   "by_model": {
#     "deepseek-v4-pro": {"calls": 142, "cost": 1.21, "tokens": 184000},
#     "claude-sonnet-4-6": {"calls": 35, "cost": 0.65, "tokens": 28000},
#     "claude-opus-4-7": {"calls": 10, "cost": 0.45, "tokens": 4500},
#   }
# }
```

This data also flows into the operator dashboard for visual tracking.

---

## Troubleshooting

### "Provider deepseek not configured"
- Check `DEEPSEEK_API_KEY` is set in `.env`
- Verify the key works: `curl -H "Authorization: Bearer $DEEPSEEK_API_KEY" https://api.deepseek.com/v1/models`

### "All retries failed"
- Increase `ROUTING_MAX_RETRIES` to 3 or 4
- Check that your fallback provider (Claude) is also configured
- Look at runtime logs for the actual error

### "Claude is being called too much" (still expensive)
- Check your agent YAMLs — too many set to `tier: premium`?
- Check escalation keywords — "money" might be triggering too many escalations
- Add `force_premium: false` to agents that don't truly need it

### "DeepSeek output quality is bad for [task]"
- Move that specific agent to `tier: balanced` (gets Sonnet fallback)
- Or override its `primary: claude-haiku-4-5` (still cheap, better quality than DeepSeek for some tasks)

---

## What this enables for buyers

**Before routing:** Buyer pays $300-500/month in LLM costs running Xcerebro at scale. That's a wall — they hesitate to add more agents.

**After routing:** Same workforce runs for $30-75/month. They're encouraged to add more agents because the marginal cost is tiny.

**The Custom Install upsell pitch:**
> "Standard install runs ~$50/month in LLM costs with smart routing. Without routing, the same workload would cost $400+/month. We configure the routing per agent so you get Claude-quality decisions where it matters and DeepSeek economics everywhere else."

That's a real value lever you can charge for.

---

## Future enhancements (v2.2+)

- **Confidence-based escalation:** Use the cheap model's stated confidence (when it says "I'm not sure...") to auto-escalate without retry
- **Per-buyer cost caps:** Hard daily/monthly LLM spend limit per Custom Install client
- **Quality scoring:** Track output quality per model per task type, auto-tune routing over time
- **Local models via Ollama:** Run Llama 3.3 locally for $0/call (privacy-sensitive buyers)
- **Smart batching:** Group similar small tasks into single calls to save tokens
