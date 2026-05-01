# Xcerebro 2.0 — Autonomous Operator Stack

> **Your AI workforce. Self-deployed in under an hour. Runs your business 24/7.**

Welcome to Xcerebro 2.0 — the autonomous business operating system. This repo gives you everything you need to deploy a coordinated AI workforce on your own Railway infrastructure: leadership agents (CEO, COO, CFO, CMO, etc.) that run your day, specialist agents that execute tasks, and pre-built workflows that wire it all into your real tools (CRM, Instagram, Stripe, calendar, Slack).

You self-host on Railway. You own your data. You pay only for the infrastructure ($65–$285/mo) and the LLM API calls you actually use.

---

## What's in this repo

| Folder | Contents |
|---|---|
| `docs/` | Step-by-step deployment guides (start with `01-quick-start.md`) |
| `agents/tier-a/` | 18 leadership agent definitions (CEO, COO, CFO, CMO, etc.) |
| `agents/tier-b/` | 74 specialist agent definitions (marketing, sales, ops, finance, REI, content, support, research, compliance) |
| `agents/tier-c/` | ~99 on-demand presets for Claude Code (engineering, design, specialized) |
| `n8n-workflows/` | Pre-built n8n workflow JSON files (import directly into n8n) |
| `dify-configs/` | Pre-configured Dify apps (knowledge bases, FAQ bots, support bots) |
| `crew/` | The CrewAI agent runtime (FastAPI + Docker) |
| `scripts/` | Helper scripts for setup and verification |
| `docker-compose.yml` | Optional local deployment (for testing) |
| `railway.json` | Railway deployment configuration |
| `.env.example` | Template for your API keys |

---

## Quick start

**Read this first:** [`docs/01-quick-start.md`](docs/01-quick-start.md)

**The 4-step deploy:**

1. Click the Railway templates (n8n, Dify) — 10 minutes
2. Fork this repo and deploy the CrewAI runtime to Railway — 5 minutes
3. Configure environment variables (your API keys) — 15 minutes
4. Activate your first workflow (Daily KPI Brief) — 5 minutes

**Total deployment time:** 30–60 minutes for moderately technical operators.

Non-technical? Skip to **Custom Install (Done-For-You)** — we build, install, and launch the system for you. Starting at $3,000 (1 agent) up to $18,000 (10 agents). DM @qf_xcerebro or email operator@xcerebro.ai to book a discovery call.

---

## What this is NOT

Let's be honest about scope:

- ❌ **Not a hosted SaaS.** You run this on your own Railway instance with your own credentials.
- ❌ **Not zero-tech.** You'll need to be comfortable copy-pasting into a terminal and configuring environment variables.
- ❌ **Not magic.** You set the rules. The agents work within them. They do not autonomously make purchases, send legal communications, or take other high-risk actions without your approval.

This is **infrastructure for operators who want to scale.** Not a replacement for thinking.

---

## What this IS

- ✅ **A real autonomous workforce.** Agents talk to each other, delegate tasks, escalate to you when needed, and run on schedule.
- ✅ **Yours forever.** You own the data, the agents, and the workflows. No vendor lock-in.
- ✅ **Built on production-grade open-source tools** (n8n, Dify, CrewAI, LangGraph, Postiz). All licensed for self-hosted use.
- ✅ **Extensible.** Add your own agents, workflows, integrations as you grow.

---

## License

This curated toolkit is provided to Xcerebro VIP members under our member terms. The underlying open-source tools (n8n, Dify, CrewAI, LangGraph, Postiz) retain their original licenses. See `LICENSES.md` for full attribution.

---

## Support

- **Skool community:** [skool.com/aicheatcodes](https://skool.com/aicheatcodes) — peer support, weekly office hours
- **Done-for-you:** xcerebro.ai/done-for-you — we deploy and maintain it for you
- **Issues:** Submit via the private repo issues tab

Built by Quentin Flores · [xcerebro.ai](https://xcerebro.ai)
