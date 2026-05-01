# What This Will Actually Cost You

> Real numbers, no surprises. Here's everything you'll pay monthly to run Xcerebro 2.0.

---

## The honest answer: $65 to $285 per month

Plus your one-time purchase of Xcerebro 2.0. Everything else is your direct cost to the underlying infrastructure and LLM providers — Xcerebro doesn't take a cut.

---

## Cost breakdown

### 1. Railway infrastructure: $43–$93/mo

| Service | Cost |
|---|---|
| PostgreSQL (managed) | ~$5 |
| Redis (managed) | ~$3 |
| n8n | ~$5–$10 |
| Dify (10 sub-services) | ~$20–$50 |
| Agent Runtime (this repo) | ~$5–$10 |
| Postiz (optional, social scheduling) | ~$5–$10 |

### 2. LLM API costs: $20–$200/mo (highly variable)

This is the biggest variable. Depends on:
- How many agents you run autonomously
- How often they fire (cron schedules)
- How chatty they are (token consumption)
- Which model you use (Sonnet vs. Haiku vs. GPT-4 vs. GPT-4o-mini)

**Rough usage estimates:**

| Usage profile | Estimated monthly LLM cost |
|---|---|
| Solo coach, 5 daily flows, light DM volume | $20–$50 |
| Active operator, 10 daily flows, moderate volume | $50–$120 |
| Agency / high-volume creator | $120–$300 |
| Heavy DM/comment automation, full crew schedule | $200–$500 |

### 3. Optional: Tool-specific API costs

Some tools you integrate have their own costs:

- **GoHighLevel:** Already paying — uses your existing GHL plan
- **ManyChat:** Free up to 1,000 contacts, then $15+/mo
- **Stripe:** Free (just transaction fees as normal)
- **Skool:** Already paying — uses your group's existing plan
- **Meta Ads / Google Ads APIs:** Free (just your existing ad spend)

---

## Cost controls (built in)

The agent runtime has hard caps in the `.env`:

```
MAX_TOKENS_PER_TASK=4000      # Per LLM call
MAX_TASKS_PER_HOUR=120        # Rate limit
MAX_DAILY_LLM_SPEND_USD=50    # Emergency brake — runtime stops at this
```

**Recommended starting points:**
- New buyer / cautious: $25/day cap → ~$750/mo max
- Comfortable / running for 30+ days: $50/day cap
- Aggressive / scaled / agency: $100+/day cap

---

## How to reduce costs

If your bill is too high:

1. **Use Haiku/Mini for routine work.** Cheaper, faster, plenty good enough for triage and simple summaries.
   - Edit agent YAML: `llm_model: claude-haiku-4-5` instead of `claude-sonnet-4-5`
2. **Reduce cron frequency.** A daily KPI brief at 6am is plenty — don't run it every hour.
3. **Cap context window.** Set `max_tokens_per_task` to a smaller number for verbose agents.
4. **Audit `/audit` regularly.** Look for runaway agents calling the LLM repeatedly. Fix the underlying loop.
5. **Pause agents you're not using.** Just remove their schedules. They stay loaded but don't fire.

---

## Compare to alternatives

A typical "AI assistant" SaaS costs $97–$497/mo per user.

If you have 1 user (just you) and pay average prices: **$200/mo to a SaaS company.**

Xcerebro 2.0 self-hosted: **$65–$285/mo total** — includes ~100 autonomous agents, full data ownership, no per-seat pricing.

The math gets dramatically better as you add team members. Most SaaS charges per-seat. Self-hosted Xcerebro doesn't care how many users you add.

---

## Watch-outs

**Things that surprise buyers:**

1. **Embedding costs at scale.** Loading 10,000 documents into Dify costs ~$10-30 in embedding fees. One-time, but real.
2. **Verbose agent outputs.** A CMO that writes 2000-token responses costs more than one that writes 500. Tune `expected_output` in the YAML.
3. **Agent loops.** A misconfigured agent that calls itself or another agent recursively can rack up $20-50 in an hour. Hard caps catch this, but watch the audit log first week.
4. **Railway sleep mode.** If your Dify services idle, Railway charges full price during runtime. Set autoscale to scale-to-zero if you can.

---

## The bottom line

For most operators, expect **$80-$150/mo** in steady state.

If you're closing even ONE additional deal per quarter from the automation, you're net positive.

If the autonomous workforce saves you 5+ hours/week of manual work (which it will), you're net positive on time alone.

Still — watch the bill the first 30 days. Adjust caps. Tune agents. By month 2, costs will stabilize.
