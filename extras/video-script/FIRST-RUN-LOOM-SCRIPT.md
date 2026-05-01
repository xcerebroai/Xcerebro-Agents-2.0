# Xcerebro 2.0 — First Run Walkthrough Loom Script

> 10-minute walkthrough script for Quentin to record. Buyers watch this immediately after purchase. Cuts deployment confusion in half.
>
> Record this once after first successful deploy. Update only when v2.1 ships breaking changes.

---

## Pre-recording setup

**On your screen, have these tabs open in this order:**
1. The unzipped `xcerebro-2.0/` folder in Finder
2. VS Code (or terminal) open to that folder
3. Browser tab on https://railway.app
4. Browser tab on https://console.anthropic.com (or OpenAI)
5. Slack (your workspace)

**Recording tool:** Loom (free tier is fine for the first cut)

**Camera on or off:** Camera ON for first 30 sec to introduce yourself, then off — let the screen do the work. People trust faces but learn from screens.

**Microphone:** External or AirPods, not laptop mic.

---

## SCRIPT — read aloud while screen recording

### [0:00–0:30] Intro (camera on)

"Hey — Quentin here from Xcerebro. You just bought 2.0, you're staring at a folder full of files, and you're wondering 'what now?'

I'm going to walk you through the entire deployment in under 10 minutes. By the end of this video, you'll have an autonomous workforce running on Railway that's about to send you a Slack message tomorrow at 6am with your business KPIs.

Let's go."

### [0:30–1:30] Tour the folder (camera off, screen on)

[Screen: open the unzipped xcerebro-2.0/ folder]

"First — what you bought. This folder. 151 files. Don't be intimidated.

[Click into agents/tier-a/]
"18 leadership agent definitions — your CEO, COO, CFO, etc. These are YAML files. You don't need to touch them to deploy."

[Click into agents/tier-b/]
"74 specialist agents — same deal. YAML files. Pre-configured."

[Click back, then into n8n-workflows/]
"9 ready-to-import workflow files. We'll import these into n8n in a few minutes."

[Click back, then into docs/]
"9 documentation guides. Read these later. The one you need NOW is `01-quick-start.md`. That's our roadmap for this video."

[Click back to root, point at .env.example]
"The most important file. We'll fill this in next."

### [1:30–3:30] Configure .env file

[Open .env.example in VS Code]

"Copy this file to a new file called `.env`. Drop the `.example`."

[Demonstrate: cp .env.example .env, open .env]

"Now we fill in the real values. You don't need every single variable — only the ones for the integrations you actually use.

The MUST-FILL section:

- ANTHROPIC_API_KEY — get this from console.anthropic.com. Five seconds. [Show getting it]
- DATABASE_URL — Railway will auto-provision this when we deploy
- SLACK_WEBHOOK_URL — for the Daily KPI Brief. Create one at api.slack.com/apps. [Show the workspace]

The NICE-TO-HAVE section:
- GHL_API_KEY — only if you're using GoHighLevel for CRM
- INSTAGRAM_BUSINESS_ACCOUNT_ID — only if you want comment-to-DM working
- STRIPE_API_KEY — only if you want payment celebration / failed payment workflows

Everything else can stay blank or default. Save the file.

**CRITICAL:** Never commit .env to GitHub. The .gitignore already excludes it. But just be aware."

### [3:30–5:30] Deploy to Railway

[Open https://railway.app, log in]

"Railway is your hosting. Five-minute deploy.

Click 'New Project' → 'Deploy from GitHub repo' → select Xcerebro-Agents-2.0 [your repo].

[Show the deploy starting]

While that's deploying, click 'New' → 'Database' → 'Add PostgreSQL'. Railway gives you the DATABASE_URL automatically.

[Wait for deploy to complete]

Once your service is live, click on it → Variables tab. Paste in everything from your .env file here, EXCEPT DATABASE_URL — Railway already set that one.

[Show pasting variables]

Click 'Deploy' to apply changes. Wait 60 seconds.

[Show successful deploy]

You now have a running agent runtime at something like xcerebro-2-0-production-ab1c.up.railway.app. Save that URL — we'll use it next."

### [5:30–7:00] Deploy n8n on Railway

[Back to Railway]

"Now n8n. Same Railway project. Click 'New' → 'Template' → search 'n8n' → deploy the official one.

[Show deployment]

Once n8n is live, you get a URL like xcerebro-n8n.up.railway.app. Open it.

[Open n8n]

Set up your account. Strong password.

Now we import the 9 workflows. In n8n, click the menu → 'Import from File' → select `n8n-workflows/01-daily-kpi-brief.json` from your folder.

[Demonstrate import]

It loads. You'll see red error icons on some nodes — that's because credentials aren't set. Click each red node and authenticate (Slack, your runtime URL, etc.).

[Demonstrate authenticating one node]

Repeat for all 9 workflows. Takes about 10 minutes the first time. Way faster after."

### [7:00–8:30] Test the first workflow

[In n8n, open the Daily KPI Brief workflow]

"Let's prove it works. Open `01-daily-kpi-brief`. Click 'Execute Workflow' in the top right.

[Demonstrate execute]

Watch the nodes light up green. Within 60 seconds, check Slack.

[Switch to Slack]

There it is. Your CEO agent just briefed you. The CFO weighed in on cash position. The CMO commented on content performance. The Sales Manager noted pipeline health.

This is what 'autonomous' actually looks like. You didn't write any of those words. The agents did, drawing on whatever data you connected.

Now go back to n8n. Top right corner — toggle the workflow from 'Inactive' to 'Active'. Tomorrow at 6am, this fires automatically. Forever. Until you turn it off."

### [8:30–9:30] Approval system intro

[Open Slack again]

"One more thing. Some agents — Sales Rep, DM Agent, Compliance — require approval before they fire. By default, EVERY action requires approval for the first 30 days. This is intentional. You build trust.

When an agent wants to send a DM or schedule something, you'll see a Slack message like this — [if you have one to show, show it; otherwise describe]. Two buttons: Approve or Reject. One tap.

After 30 days of approving, you can graduate categories to auto-fire. Read `docs/06-approval-system.md` for how to do that. Don't rush it. Trust is earned."

### [9:30–10:00] Close (camera on)

[Camera back on]

"That's it. You're live. Tomorrow morning, Slack will ping you with your first autonomous brief.

If anything broke, three places to go:
1. Open a GitHub issue on the repo
2. Post in the AI Cheat Codes Skool — VIP channel
3. DM me on Instagram @qf_xcerebro for urgent stuff

The full deep-dive guides are in /docs. Read `06-approval-system.md` first — that's where most operators have questions.

Welcome to autonomy, Operator. Now go run your business while it runs itself.

— Q"

[End recording]

---

## Post-recording checklist

- [ ] Trim dead air at start and end
- [ ] Add a thumbnail (your face + "Xcerebro 2.0 — First Run" text)
- [ ] Add Loom chapters at: Intro / Folder tour / .env / Railway / n8n / First test / Approvals / Close
- [ ] Upload to a private Loom — share the link in the README + welcome email
- [ ] Add the link to: WHAT-YOU-JUST-BOUGHT.md, README.md, the Stripe success page, and the GitHub release description

---

## Why this matters

The biggest source of failed deployments is buyers getting stuck on something a 30-second video clarifies. This single Loom cuts your support load by ~70% based on similar product launches.

Don't skip it. Don't outsource it. Your face. Your voice. Five takes max — done is better than perfect.
