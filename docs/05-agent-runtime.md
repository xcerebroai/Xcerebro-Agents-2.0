# The Agent Runtime — How It Works

> The CrewAI service is the heart of your autonomous workforce. This doc explains what it does, how it talks to other services, and how to extend it.

---

## What it is

A FastAPI service running in a Docker container on Railway. It loads agent definitions from YAML files in `agents/tier-a/` and `agents/tier-b/`, then exposes HTTP endpoints that n8n (and other services) can call to invoke them.

When n8n triggers a workflow, it makes an HTTP POST to the agent runtime. The runtime spins up the right CrewAI agent (or coordinated crew), runs the task, applies human approval gates if needed, and returns the result.

---

## Endpoints

### `GET /health`
Health check used by Railway and Docker. Returns service status + counts.

### `POST /agents/{agent_id}/invoke`
Invoke a single agent for a task.

```bash
curl -X POST https://crew.yourdomain.com/agents/auto-cmo/invoke \
  -H "x-api-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Plan content for next week. Audience: AI/operator. Goal: drive cohort signups.",
    "context": {
      "current_offers": ["Skool VIP $97/mo", "Operator Cohort $1497"]
    }
  }'
```

### `POST /crews/{crew_id}/run`
Run a coordinated multi-agent crew. Use this for orchestrated flows like the Daily KPI Brief.

```bash
curl -X POST https://crew.yourdomain.com/crews/daily-kpi-brief/run \
  -H "x-api-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"inputs": {"date": "2026-04-30"}}'
```

### `POST /workflows/trigger`
Generic webhook entrypoint that n8n calls. Routes to the right crew based on workflow name.

```bash
curl -X POST https://crew.yourdomain.com/workflows/trigger \
  -H "x-api-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_name": "daily-kpi-brief",
    "source": "schedule",
    "payload": {"date": "2026-04-30"}
  }'
```

### `GET /agents`
List all loaded agents.

### `GET /crews`
List all loaded crews.

### `POST /approvals/{approval_id}`
Receive a human approval decision (called from Slack interactive buttons or admin UI).

```bash
curl -X POST https://crew.yourdomain.com/approvals/abc-123-uuid \
  -H "x-api-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "approve",
    "approver": "quentin@xcerebro.ai"
  }'
```

### `GET /audit`
Recent agent activity log. Filter by `agent_id` query param.

---

## The data flow

```
[n8n cron triggers] → POST /workflows/trigger → CrewRegistry.run_crew()
                                                       │
                          ┌────────────────────────────┴─┐
                          ↓                              │
                 Build CrewAI agents                     │
                 Build CrewAI tasks                      │
                          │                              │
                          ↓                              │
                 crew.kickoff(inputs)                    │
                          │                              │
            ┌─────────────┴────────────────┐             │
            ↓                              ↓             │
   Tier A agent calls                  Tool call         │
   Tier B specialists      ←→     (n8n, Dify, GHL)       │
            │                              │             │
            ↓                              ↓             │
   AuditLogger writes events to Postgres   │             │
                                           ↓             │
                              Sensitive action?          │
                                  ↓ YES                  │
                  ApprovalManager.request() → Slack ─────┘
                                  ↓
                          Human taps approve
                                  ↓
                        Resume agent, complete
```

---

## Adding a new agent

1. Create a new YAML file in `agents/tier-a/` or `agents/tier-b/`
2. Follow the format from `agents/tier-a/auto-ceo.yaml` (use that as a template)
3. Required fields: `id`, `name`, `tier`, `role`, `goal`, `backstory`, `permissions`
4. Restart the agent runtime (Railway: Settings → Redeploy)
5. Verify with `GET /agents`

---

## Adding a new crew

1. Create a new YAML file in `crew/crews/`
2. Define `members` (list of agent IDs to participate)
3. Define `tasks` (sequential or hierarchical workflow)
4. Set `triggers_for_workflows` (n8n workflow names that map to this crew)
5. Restart the runtime
6. Verify with `GET /crews`

---

## Approval gates explained

Sensitive actions (DMs, public posts, refunds, payments) hit an approval gate. By default, the approval manager:

1. Writes the request to Postgres
2. Sends a Slack message to your approval channel with **Approve** and **Reject** buttons
3. Pauses execution
4. When you click a button, Slack POSTs to `/approvals/{id}`
5. The runtime resumes the agent or aborts

To **disable approvals for a category** (after building trust):
- Edit `.env`: set `APPROVAL_REQUIRED_FOR_DM=false`
- Or in agent YAML: `permissions.always_require_approval: false`

To **always require approval for a specific agent** (override defaults):
- In YAML: `permissions.always_require_approval: true`

---

## Cost controls

The runtime enforces hard caps:

- `MAX_TOKENS_PER_TASK` — caps each LLM call
- `MAX_TASKS_PER_HOUR` — rate-limits agent invocations
- `MAX_DAILY_LLM_SPEND_USD` — emergency brake (the runtime refuses new tasks past this)

Set these in your `.env`. Recommended starting points are conservative — raise them as you build confidence.

---

## Logs + observability

```bash
# Recent agent activity
curl -H "x-api-key: $KEY" https://crew.yourdomain.com/audit?limit=50

# Filter by specific agent
curl -H "x-api-key: $KEY" https://crew.yourdomain.com/audit?agent_id=auto-dm-agent
```

Railway also gives you raw logs in the service dashboard.

---

## Extending with custom tools

CrewAI agents can call custom Python tools. Add a new tool in `crew/tools/`:

```python
from crewai.tools import tool

@tool
def lookup_lead_in_ghl(email: str) -> dict:
    """Look up a lead by email in GoHighLevel CRM."""
    # ... implementation
    return result
```

Then reference it in an agent YAML:
```yaml
permissions:
  can_call_tools:
    - lookup_lead_in_ghl
```

---

## What this runtime does NOT do

- ❌ It does not run LLMs locally. All inference goes to Anthropic / OpenAI.
- ❌ It does not store sensitive data. Everything goes through your DB.
- ❌ It does not act without your env config. No secrets, no hardcoded API keys.
- ❌ It does not auto-fire on sensitive actions (DM, post, payment) without explicit approval setting.

This is intentional. The runtime is designed to be auditable, predictable, and stoppable.
