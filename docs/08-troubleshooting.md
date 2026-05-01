# Troubleshooting — Common Issues & Fixes

> When something breaks, look here first. Most issues fall into 5 categories.

---

## Quick diagnosis flow

1. **Is the agent runtime alive?** → `curl https://crew.yourdomain.com/health`
2. **Are agents loaded?** → `curl -H "x-api-key: KEY" https://crew.yourdomain.com/agents`
3. **Are crews loaded?** → `curl -H "x-api-key: KEY" https://crew.yourdomain.com/crews`
4. **What does the audit log say?** → `curl -H "x-api-key: KEY" https://crew.yourdomain.com/audit?limit=50`

If any of these fail, start with the troubleshooting steps below.

---

## Category 1: Agent Runtime won't start

### Symptom: `/health` returns 502 / connection refused

**Causes:**
- Container is still booting (wait 60s)
- Build failed — check Railway logs
- Missing required environment variable

**Fixes:**
```bash
# Check Railway logs
# Railway → Service → Deployments → Click latest → View logs

# Common errors:
# - "ImportError: No module named X" → check requirements.txt
# - "OperationalError: could not connect to server" → check DATABASE_URL
# - "ValueError: ANTHROPIC_API_KEY required" → set the env var
```

### Symptom: Container starts but `/agents` returns empty

**Cause:** Agent YAML files aren't being loaded.

**Fix:**
- Ensure `agents/` is mounted at `/app/agents` (Docker compose) or copied into the image (Railway deploy)
- Check YAML syntax: invalid YAML silently fails to load
- Look for "Failed to load agent" warnings in the logs

---

## Category 2: n8n workflows aren't firing

### Symptom: Cron-triggered workflow never runs

**Causes:**
- Workflow is **inactive** (toggle the switch in top-right)
- Cron expression is wrong timezone
- n8n hasn't been restarted since cron change

**Fix:**
1. Open the workflow in n8n editor
2. Verify Active toggle is on
3. Check **Executions** tab — does it show scheduled runs?
4. Set timezone in workflow settings (top right of editor → Settings)

### Symptom: Webhook returns 404

**Causes:**
- Workflow is inactive (production webhooks only work when active)
- Wrong webhook path
- n8n is using test URL instead of production URL

**Fix:**
- Activate the workflow
- Check the webhook node — there's a "Test URL" and a "Production URL"
- Use the **Production URL** in your external service (ManyChat, Stripe, etc.)

### Symptom: Workflow fires but HTTP node fails

**Causes:**
- `AGENT_RUNTIME_URL` env var not set in n8n
- Agent runtime is down
- Wrong API key

**Fix:**
- Check Railway: is the agent runtime container healthy?
- Test directly: `curl -H "x-api-key: $KEY" https://crew.../health`
- Verify env vars in n8n match the agent runtime's `AGENT_RUNTIME_API_KEY`

---

## Category 3: Agents return errors or weird outputs

### Symptom: Agent returns "I cannot complete this task"

**Causes:**
- LLM doesn't have enough context
- Task is ambiguous
- Agent's role doesn't match the task

**Fix:**
- Add more context in the `context` payload
- Rewrite the task description to be more specific
- Check if a different agent is better suited

### Symptom: Agent output is too long / too verbose

**Cause:** `expected_output` field doesn't constrain length.

**Fix:** Edit the agent YAML:
```yaml
expected_output: >
  A concise summary in 3-4 bullet points. Total under 200 words.
```

### Symptom: Agent hallucinates / makes up data

**Causes:**
- Agent doesn't have access to the Dify knowledge base
- Knowledge base doesn't contain the relevant info
- Agent's prompt allows speculation

**Fix:**
- Add Dify knowledge base to agent's `data_sources`
- Upload the missing reference doc to the relevant knowledge base
- Add to backstory: "If you don't know, say so. Never make up data."

---

## Category 4: Slack approvals not working

### Symptom: Slack doesn't receive approval messages

**Causes:**
- `SLACK_BOT_TOKEN` not set or invalid
- Bot not added to the approval channel
- Wrong channel ID

**Fix:**
1. Test Slack connection:
   ```bash
   curl -X POST https://slack.com/api/auth.test \
     -H "Authorization: Bearer $SLACK_BOT_TOKEN"
   # Expected: {"ok":true,"user":"xcerebro-bot",...}
   ```
2. Add the bot to your approval channel: `/invite @xcerebro-bot`
3. Get the channel ID: right-click channel → View channel details → copy ID at bottom

### Symptom: Approval buttons don't work

**Causes:**
- Slack app's "Interactivity" not configured
- Request URL doesn't match agent runtime's domain

**Fix:**
1. Slack app settings → **Interactivity & Shortcuts** → On
2. Request URL: `https://crew.yourdomain.com/slack/interactive`
3. Make sure the runtime exposes that endpoint (or use manual cURL approval as a workaround)

---

## Category 5: Costs/Performance issues

### Symptom: LLM bill is too high

**Causes:**
- Too many cron schedules running simultaneously
- An agent is in an infinite loop
- Using Sonnet/GPT-4 for everything when Haiku/Mini would suffice

**Fix:**
1. Audit the `/audit` log — look for repeated agent invocations within minutes
2. Lower cron frequency (daily instead of hourly)
3. Switch low-stakes agents to cheaper models
4. Set `MAX_DAILY_LLM_SPEND_USD` lower as a hard brake

### Symptom: Railway bill is higher than expected

**Causes:**
- Dify's 10-service stack is always-on
- Too many services running idle

**Fix:**
- Pause services you're not using (Railway → Service → Settings → Pause)
- Enable scale-to-zero if your usage is bursty
- Consider downgrading Dify if you're not using it (some users only need n8n + CrewAI)

---

## Category 6: Database / Data persistence

### Symptom: Workflows / data disappear after redeploy

**Causes:**
- Postgres volume not attached
- Wrong DATABASE_URL after redeploy

**Fix:**
- Verify Postgres has a persistent volume
- Don't switch DATABASE_URL between deploys without migration

### Symptom: "duplicate key" errors in audit log

**Cause:** Multiple agent runtime instances sharing one DB without unique IDs.

**Fix:** Run a single replica of the agent runtime in Railway. Horizontal scaling needs migration to Celery workers (Phase 5+).

---

## When all else fails

1. **Check Railway logs.** They contain the answer 80% of the time.
2. **Check n8n execution log.** For workflow issues.
3. **Check `/audit`.** For agent-level issues.
4. **Ask in Skool VIP.** Other operators have hit the same wall.
5. **Open a repo issue.** For bugs in the curated toolkit.

---

## Reset everything (nuclear option)

If your install is broken beyond repair:

```bash
# 1. In Railway, delete all services in the project
# 2. Re-run the deployment guide from scratch
# 3. You'll lose: workflow execution history, agent audit log
# 4. You'll keep: nothing — this is a clean slate
```

Don't do this unless you've tried everything else. Most issues have a simpler fix.
