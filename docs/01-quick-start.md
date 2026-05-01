# Quick Start — Xcerebro 2.0 in 30-60 Minutes

> The minimum-viable deploy. Get your first autonomous workflow running today.

This guide walks you through the fastest path from "I just bought Xcerebro 2.0" to "my AI workforce is sending me a Slack brief tomorrow morning."

**Time required:** 30-60 minutes for moderately technical operators.
**Skills required:** Comfortable copy-pasting into a terminal, configuring environment variables, and clicking buttons in cloud dashboards.

If that doesn't sound like you, **skip ahead to Custom Install (Done-For-You)**. We deploy the whole stack for you. Starting at $3,000 (1 agent) up to $18,000 (10 agents). Contact: operator@xcerebro.ai.

---

## Step 0 — Before you start (5 minutes)

Make sure you have:

- [ ] A **Railway account** — sign up at [railway.com](https://railway.com) (free, $5 trial credit)
- [ ] A **GitHub account** — to fork this repo
- [ ] An **Anthropic API key** OR **OpenAI API key** — your LLM provider
  - Anthropic: [console.anthropic.com](https://console.anthropic.com) (recommended)
  - OpenAI: [platform.openai.com](https://platform.openai.com)
- [ ] A **Slack workspace** with admin rights (for the approval inbox)

**Optional but recommended for full functionality:**
- GoHighLevel account (for CRM integration)
- ManyChat or Instagram Business API access (for comment automation)
- Stripe account (for revenue tracking)

---

## Step 1 — Deploy n8n (5-10 minutes)

n8n is the workflow automation backbone.

1. Go to [Railway's n8n template](https://railway.com/deploy/n8n)
2. Click **"Deploy Now"**
3. Sign in with GitHub (or your Railway account)
4. Wait ~2 minutes for the deploy to complete
5. Click **"Generate Domain"** in the n8n service settings → Networking
6. Open the generated domain (e.g., `n8n-production-xxxx.up.railway.app`)
7. Create your admin account on first load
8. Go to **Settings → API → Create API Key** — save this key for Step 4

**Save these for later:**
- Your n8n public URL: `https://n8n-production-xxxx.up.railway.app`
- Your n8n API key

---

## Step 2 — Deploy Dify (5-10 minutes)

Dify is the AI app + RAG layer. It hosts your knowledge bases.

1. Go to [Railway's Dify template](https://railway.com/deploy/dify-ai-workflow)
2. Click **"Deploy Now"**
3. Wait ~5 minutes for all 10 services to deploy and become healthy
4. Open the public Nginx domain → first-run setup wizard
5. Create your admin account
6. Go to **Settings → Model Providers** → add your Anthropic or OpenAI API key
7. Go to **Account Settings → API Access** → create an API key

**Save these for later:**
- Your Dify public URL
- Your Dify API key

---

## Step 3 — Deploy the Agent Runtime (5 minutes)

This is the CrewAI service that actually runs the agents.

1. Fork this repo to your GitHub account
2. In Railway, click **"New Project" → "Deploy from GitHub repo"**
3. Select your fork
4. Railway auto-detects the Dockerfile in `crew/`
5. Add a **PostgreSQL** plugin (Railway → Add Service → Database → PostgreSQL)
6. Add a **Redis** plugin (same path)
7. Wait ~3 minutes for the build + deploy
8. Click **"Generate Domain"** → save this URL as your `AGENT_RUNTIME_URL`

---

## Step 4 — Configure Environment Variables (10-15 minutes)

In Railway, open your **Agent Runtime service** → **Variables** tab. Paste in the following (with your real values):

```
ANTHROPIC_API_KEY=sk-ant-api03-...
DEFAULT_LLM_MODEL=claude-sonnet-4-5
DEFAULT_LLM_PROVIDER=anthropic

N8N_BASE_URL=https://n8n-production-xxxx.up.railway.app
N8N_API_KEY=<paste from step 1>
N8N_WEBHOOK_URL=https://n8n-production-xxxx.up.railway.app/webhook

DIFY_BASE_URL=<paste from step 2>
DIFY_API_KEY=<paste from step 2>

AGENT_RUNTIME_API_KEY=<generate a random 32-char string>

SLACK_BOT_TOKEN=xoxb-...
SLACK_NOTIFICATIONS_CHANNEL_ID=C01234ABCDE
SLACK_APPROVAL_CHANNEL_ID=C01234FGHIJ
```

**For Slack:**
1. Go to [api.slack.com/apps](https://api.slack.com/apps) → Create New App → From Scratch
2. Add OAuth scopes: `chat:write`, `channels:read`, `chat:write.public`
3. Install to your workspace
4. Copy the Bot User OAuth Token → that's your `SLACK_BOT_TOKEN`
5. In your Slack workspace, create channels `#xcerebro-brief` and `#xcerebro-approvals`
6. Right-click each channel → View channel details → copy the Channel ID at the bottom

**Generate a random API key:**
```bash
openssl rand -base64 32
```

After saving variables, **redeploy the runtime** (Railway → Settings → Redeploy).

---

## Step 5 — Import Workflows into n8n (5 minutes)

1. Open your n8n editor
2. Click **Workflows → Import from File**
3. Upload `n8n-workflows/01-daily-kpi-brief.json`
4. In the imported workflow, set up your Slack credential (gear icon → New)
5. Add environment variables in n8n: `AGENT_RUNTIME_URL`, `AGENT_RUNTIME_API_KEY`, `SLACK_NOTIFICATIONS_CHANNEL_ID`
6. **Activate** the workflow (toggle in top-right)

---

## Step 6 — Verify everything works (5 minutes)

**Test 1: Agent Runtime is alive**

```bash
curl https://crew-production-xxxx.up.railway.app/health
```

Expected response:
```json
{
  "status": "ok",
  "service": "xcerebro-2.0-agent-runtime",
  "agents_loaded": 3,
  "crews_loaded": 1
}
```

**Test 2: List loaded agents**

```bash
curl -H "x-api-key: <your-key>" \
  https://crew-production-xxxx.up.railway.app/agents
```

You should see `auto-ceo`, `auto-cmo`, `auto-dm-agent` in Tier A.

**Test 3: Trigger the daily brief manually**

In n8n, open the Daily KPI Brief workflow and click **"Execute Workflow"**.

Within 60-120 seconds, you should see a brief land in your `#xcerebro-brief` Slack channel.

If it doesn't work:
- Check Railway logs for the agent runtime
- Check n8n execution log
- See [`docs/08-troubleshooting.md`](08-troubleshooting.md)

---

## What's next?

**Tomorrow at 6am**, the Daily KPI Brief will fire automatically and post to your Slack.

Once you've confirmed it works, expand:

1. **Activate more workflows** — see `n8n-workflows/` for the catalog
2. **Build your knowledge bases in Dify** — see [`docs/04-configure-dify.md`](04-configure-dify.md)
3. **Add more agents** — see `agents/tier-a/` for examples, drop new YAMLs in
4. **Connect more tools** — GHL, Stripe, Instagram, etc. via env vars

---

## Support

- **Skool community:** [skool.com/aicheatcodes](https://skool.com/aicheatcodes) — peer help
- **Done-for-you upgrade:** [xcerebro.ai/done-for-you](https://xcerebro.ai/done-for-you)
- **Bug reports:** Repo Issues tab

Welcome to autonomy, Operator.
