# What You Just Bought — Xcerebro 2.0 Orientation

> Welcome, Operator. Read this first. It'll save you 30 minutes of confusion.

---

## The 10-second pitch

You bought a **complete, self-deployable autonomous workforce** for your business.

**~100 autonomous agents** + **~99 on-demand presets** + **9 pre-built workflows** + **5 best-in-class open-source tools** + **9 documentation guides**.

You self-host on Railway. You own your data. You pay $65–$285/month in infrastructure (no per-seat SaaS fees, no vendor lock-in).

Setup time: **30–60 minutes** for moderately technical operators.

---

## The 3 tiers of agents — explained simply

```
┌─────────────────────────────────────────────────────┐
│   TIER A — Leadership Orchestrators (18 agents)     │
│   Strategic. Run on schedule. Delegate downward.    │
│   CEO, COO, CFO, CMO, Sales Manager, etc.           │
│   → Run autonomously on your Railway                │
└─────────────────────────────────────────────────────┘
                         ↓ delegates to
┌─────────────────────────────────────────────────────┐
│   TIER B — Operational Specialists (74 agents)      │
│   Tactical. Hook Writer, Copy Chief, Image Director │
│   Trend Spotter, Sales Rep, Lead Magnet Designer    │
│   → Run autonomously on your Railway                │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│   TIER C — On-Demand Presets (~99 agents)           │
│   Reactive. Engineering, Design, REI specialized.   │
│   Backend Architect, UX Researcher, Wholesaler...   │
│   → Run inside Claude Code (your laptop)            │
└─────────────────────────────────────────────────────┘
```

**Key insight:** Tier A + B are autonomous and run on your cloud. Tier C is reactive and runs in Claude Code. Different jobs, different deployment paths, both come with your purchase.

---

## What's in each folder

```
xcerebro-2.0/
│
├── README.md                      ← Start here
├── WHAT-YOU-JUST-BOUGHT.md        ← This file
├── docs/                          ← 9 step-by-step guides
│   └── 01-quick-start.md          ← The 30-min deploy guide
│
├── agents/
│   ├── tier-a/                    ← 18 leadership orchestrators (autonomous)
│   ├── tier-b/                    ← 74 specialists (autonomous, 9 pods)
│   └── tier-c/                    ← The 199 install separately via script
│
├── crew/                          ← The autonomous agent runtime
│   ├── main.py                    ← FastAPI server
│   ├── crews/                     ← 3 pre-built coordinated crews
│   └── tools/                     ← Audit log, Slack approvals
│
├── n8n-workflows/                 ← 9 ready-to-import workflows
│   ├── 01-daily-kpi-brief.json    ← Activate this FIRST
│   └── ... (8 more)
│
├── dify-configs/                  ← Knowledge base templates
│
├── scripts/
│   ├── install.sh                 ← Pre-flight checks
│   ├── install-tier-c.sh          ← Install the 199 markdown agents
│   └── verify.sh                  ← Post-deploy health check
│
├── docker-compose.yml             ← Optional local testing
├── railway.json                   ← Railway deployment config
└── .env.example                   ← Copy to .env, fill in your keys
```

---

## Your next 60 minutes (in order)

### Minute 0–5: Pre-flight
```bash
cd xcerebro-2.0
cp .env.example .env
./scripts/install.sh
```
The install script will check your environment and tell you what's missing.

### Minute 5–35: Open `docs/01-quick-start.md` and follow it

Don't skip steps. Don't try to be clever. The order matters:
1. Deploy n8n on Railway (one-click template)
2. Deploy Dify on Railway (one-click template)
3. Deploy this repo as the Agent Runtime (Railway from GitHub)
4. Configure environment variables in Railway
5. Import workflows into n8n

### Minute 35–45: Verify
```bash
./scripts/verify.sh
```
This will hit every endpoint and tell you what's working.

### Minute 45–60: First flow live
1. In n8n, activate **only** `01-daily-kpi-brief`
2. Click "Execute Workflow" once to test
3. You should see a Slack message land within 60 seconds
4. Activate the schedule (toggle in top-right)

**Tomorrow at 6am, you'll wake up to an autonomous Slack brief.** That's proof of life.

---

## The mental model

Think of Xcerebro 2.0 as a **company you own**:

- **n8n** is your **dispatch center** — it routes events (cron, webhooks) to the right department
- **CrewAI runtime** is your **leadership office** — agents reason, delegate, and respond
- **Dify** is your **knowledge library** — SOPs, scripts, FAQs that agents reference
- **Postgres** is your **filing cabinet** — every action audit-logged
- **Slack** is your **approval inbox** — sensitive actions require your tap before firing
- **Postiz** is your **publishing department** — social media calendar (optional)

You're the founder. They run the day-to-day.

---

## What you DO NOT need to do

❌ You DO NOT need to build agents from scratch — 18 leadership + 74 specialists are pre-defined
❌ You DO NOT need to write Python code — it's all built and Dockerized
❌ You DO NOT need to manage servers — Railway handles infrastructure
❌ You DO NOT need to keep the workforce running — once deployed, it self-runs on schedule
❌ You DO NOT need to approve every action forever — graduate categories to auto-fire over time

---

## What you DO need to do (be honest with yourself)

✅ Configure your `.env` with real API keys
✅ Read at least `docs/01-quick-start.md` end-to-end before starting
✅ Watch the audit log for the first 7 days to build trust
✅ Approve agent actions in Slack the first 50–100 times before graduating to auto-fire
✅ Update knowledge bases in Dify when your business changes (new offers, new pricing, etc.)
✅ Pay your Railway bill ($65–$285/mo) and your LLM bill (Anthropic or OpenAI)

If you're not willing to do these things, **upgrade to Custom Install (Done-For-You)**. We build, install, and launch the system for you. Starting at $3,000. DM @qf_xcerebro or email operator@xcerebro.ai.

---

## What success looks like in 30 days

- Daily KPI Brief lands in Slack at 6am every morning
- Comment-to-DM pipeline converts at >40% (lead magnet delivery)
- Stripe payment celebrations create dopamine in your team
- Failed payments get triaged to CFO before becoming churn
- You've reviewed and approved ~200 agent actions
- You've graduated 1–2 categories to auto-fire
- Your knowledge bases have ~10–20 docs uploaded
- You've added 1 custom agent specific to your business

This is the **floor** of success. The ceiling is much higher as you build trust and scale.

---

## What success looks like in 90 days

- 5–10 workflows running autonomously
- Multiple categories on auto-fire (you trust the agents)
- Custom agents for YOUR specific business workflows
- Audit log shows >5,000 logged actions
- Visible time savings: 5–15 hours/week of manual work eliminated
- Visible revenue impact: faster lead response, faster content production
- You forget what your life was like before this

---

## Where to get help

| Issue | Where to go |
|---|---|
| Bug in the toolkit | GitHub Issues (private repo, members only) |
| "How do I..." question | Skool VIP community: skool.com/aicheatcodes |
| Custom build / done-for-you | xcerebro.ai/done-for-you |
| Urgent issue affecting business | DM @qf_xcerebro on Instagram |

---

## What this is NOT

Let me be honest about scope:

❌ Not a hosted SaaS — you run it on Railway
❌ Not zero-tech — you'll use a terminal
❌ Not magic — agents work within rules YOU set
❌ Not a replacement for thinking — it's leverage for thinkers

---

## What this IS

✅ A real autonomous workforce
✅ Your data on your infrastructure forever
✅ Built on production-grade open-source tools
✅ Extensible and customizable
✅ Designed for operators who want to scale without hiring

---

## Final thought

This is infrastructure for operators, not a toy.

If you've been doing the same manual work for 18 months and you're sick of it — Xcerebro 2.0 is the off-ramp.

If you're looking for a magic button that prints money — close this folder, save the receipt, and go shop somewhere else. We won't waste each other's time.

You bought it. Now deploy it.

Welcome to autonomy, Operator.
— **Quentin & the Xcerebro team**

---

**Next step:** Open `docs/01-quick-start.md`.
