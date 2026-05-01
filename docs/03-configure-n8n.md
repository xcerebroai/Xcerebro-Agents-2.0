# Configuring n8n — Workflow Setup Walkthrough

> n8n is the glue. Every cron, every webhook, every external integration runs through here. This doc walks through importing workflows, configuring credentials, and customizing for your business.

---

## What's already built for you

In `n8n-workflows/` you'll find pre-built JSON workflow files:

| File | What it does | Trigger |
|---|---|---|
| `01-daily-kpi-brief.json` | Morning Slack brief from CFO/CMO/Sales/CEO crew | Daily 6am cron |
| `02-comment-to-dm.json` | Comment keyword → DM lead magnet → CRM contact | Webhook from ManyChat |
| (more workflows ship with the toolkit — see catalog below) | | |

---

## Importing a workflow

1. Open your n8n editor (e.g., `https://n8n-production-xxxx.up.railway.app`)
2. Click **Workflows** (left nav) → **+ Import** (top right) → **From File**
3. Select the JSON file from `n8n-workflows/`
4. Click **Save**

The workflow loads but is **inactive**. You need to:
1. Configure credentials (next section)
2. Set environment variables
3. Toggle the workflow to **Active** (top right)

---

## Setting environment variables in n8n

n8n has its own env var system separate from Railway. Set these in n8n via:

**Settings → Variables** (n8n 1.0+) or by editing the Railway service env vars.

Required variables:

```
AGENT_RUNTIME_URL=https://crew-production-xxxx.up.railway.app
AGENT_RUNTIME_API_KEY=<the random string you generated>
SLACK_NOTIFICATIONS_CHANNEL_ID=C01234ABCDE
SLACK_APPROVAL_CHANNEL_ID=C01234FGHIJ
GHL_BASE_URL=https://services.leadconnectorhq.com
GHL_API_KEY=<from GHL>
GHL_LOCATION_ID=<from GHL>
TIMEZONE=America/Chicago
```

After adding variables, **redeploy n8n** for them to take effect.

---

## Configuring credentials

Some nodes (Slack, Gmail, etc.) need credentials. Configure via:

**n8n Editor → Credentials → + Add Credential**

### Slack credential

1. Type: **Slack API**
2. Authentication: **Access Token**
3. Token: Your `SLACK_BOT_TOKEN` (from your Slack app → OAuth & Permissions)
4. Test the connection
5. Save as **"Slack Bot Token"**

The pre-built workflows reference this credential by name.

### Google Calendar / Gmail credential

1. Type: **Google Calendar OAuth2 API** (or Gmail OAuth2)
2. Click **Sign in with Google**
3. Authorize the requested scopes
4. Save

You may need to set up OAuth credentials in Google Cloud Console first. n8n's docs have a guide:
[https://docs.n8n.io/integrations/builtin/credentials/google/](https://docs.n8n.io/integrations/builtin/credentials/google/)

### GoHighLevel credential

GHL uses Bearer token authentication. The pre-built workflows handle this via env variable, so you don't need to create a credential — just set `GHL_API_KEY` in env vars.

### ManyChat credential (for Instagram comment automation)

ManyChat sends webhooks TO n8n. n8n doesn't call ManyChat. So no credential needed in n8n — just configure the webhook URL in ManyChat:

1. ManyChat → Automation → External Request
2. URL: `https://your-n8n.up.railway.app/webhook/comment-trigger`
3. Method: POST
4. Body: JSON with the comment data

---

## Testing a workflow before going live

For every imported workflow:

1. Open the workflow
2. Click the **first node** (the trigger)
3. Click **Execute Step** → fills in test data
4. Click each subsequent node → **Execute Step**
5. Watch the data flow through
6. Check that the final node outputs what you expect

**Don't activate a workflow until you've test-executed it manually.**

---

## Common modifications

### Change the daily brief time

In `01-daily-kpi-brief.json` after import:
1. Open the **Daily 6am Trigger** node
2. Change the cron expression (e.g., `0 7 * * *` for 7am)
3. Save

### Change the trigger keyword for comment-to-DM

In `02-comment-to-dm.json`:
1. Open the **Check for Trigger Keyword** node
2. Change the right value (currently `"AI"`) to your keyword
3. Save

### Add more keywords

Duplicate the **Check for Trigger Keyword** node, change the keyword, and route to a different DM agent invocation. You can have N keywords → N different lead magnets.

---

## Workflow naming convention

The pre-built workflows are prefixed `01-`, `02-`, etc. **Keep this convention** for your custom workflows. Use:

- `01-` to `09-` for daily/critical flows
- `10-` to `19-` for marketing automations
- `20-` to `29-` for sales automations
- `30-` to `39-` for ops/internal automations
- `40-` to `49-` for finance automations
- `90-` to `99-` for experimental / new flows

This makes the workflow list scannable in n8n's UI.

---

## Webhook URLs

Every webhook trigger in n8n gets two URLs:

- **Test URL** — only fires when you click "Execute" in the editor (use during development)
- **Production URL** — fires whenever called externally (use in your live integrations)

For ManyChat, Stripe webhooks, and other production integrations, **use the Production URL.**

---

## Workflow catalog (full)

These are the workflows that ship with Xcerebro 2.0:

1. **01-daily-kpi-brief** — Morning Slack brief from leadership crew
2. **02-comment-to-dm** — Comment keyword → DM lead magnet → CRM
3. **03-weekly-ceo-summary** — Sunday 6pm strategic review
4. **04-stripe-payment-celebration** — New payment → Slack notification
5. **05-stripe-failed-payment** — Failed payment → CFO triage → ops alert
6. **06-skool-cohort-heartbeat** — Daily Skool engagement check
7. **07-instagram-story-viewer-reactor** — High-intent story replies → DM Agent
8. **08-ads-feedback-loop** — Daily Meta Ads pull → CMO → recommendations
9. **09-meeting-prep-brief** — 30 min before meeting → research brief to Slack

You'll find the JSON for each in `n8n-workflows/`.

Activate them one at a time. Don't activate everything on day 1. Build trust with each before adding the next.
