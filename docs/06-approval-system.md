# The Approval System — Stay in Control

> Autonomous agents that act without oversight are a liability. The Xcerebro 2.0 approval system gives you fine-grained control over what your agents can do without asking permission first.

---

## The principle

Every agent action falls into one of three categories:

1. **Auto-fire** — safe to execute without approval (logging, reading data, internal updates)
2. **Approval required** — voice-sensitive or money-sensitive (DMs, posts, refunds, payments)
3. **Always blocked** — never allowed regardless of approval (legal advice, contracts, sensitive PII without explicit handling)

You configure which actions fall in which bucket. Defaults are conservative.

---

## Default approval requirements

Out of the box, these require approval:

| Category | Default | Configure with |
|---|---|---|
| Send DM | ✅ Required | `APPROVAL_REQUIRED_FOR_DM` |
| Send email broadcast | ✅ Required | `APPROVAL_REQUIRED_FOR_EMAIL` |
| Post publicly (IG, X, etc.) | ✅ Required | `APPROVAL_REQUIRED_FOR_PUBLIC_POST` |
| Process refund | ✅ Required | `APPROVAL_REQUIRED_FOR_REFUND` |
| Make payment / charge card | ✅ Required | `APPROVAL_REQUIRED_FOR_PAYMENT` |
| Update CRM contact | ❌ Auto | `APPROVAL_REQUIRED_FOR_CRM_UPDATE` |
| Book calendar appointment | ❌ Auto | `APPROVAL_REQUIRED_FOR_CALENDAR_BOOKING` |

Change any of these in your `.env` — set to `true` or `false`.

---

## How approvals flow

When an agent tries to do something requiring approval:

```
1. Agent generates the action (e.g., "Send DM to @username with this message")
2. Runtime checks approval policy → "Yes, DMs require approval"
3. Runtime PAUSES execution
4. Runtime calls ApprovalManager.request()
5. ApprovalManager:
   - Writes request to Postgres
   - Posts a Slack message to your approval channel
   - Returns approval_id (UUID)
6. Runtime returns 202 to caller with status="awaiting_approval"
7. You see the Slack message:
   ┌────────────────────────────────────────┐
   │ 🔔 Approve DM Agent action             │
   │                                        │
   │ Description:                           │
   │ Send DM to @rei_pro_dallas:            │
   │ "Hey — saw you grabbed the AI          │
   │ Workforce guide. What part of your     │
   │ business are you trying to take off    │
   │ your plate first?"                     │
   │                                        │
   │ Approval ID: abc-123-uuid              │
   │                                        │
   │ [✅ Approve]    [❌ Reject]            │
   └────────────────────────────────────────┘
8. You tap [Approve]
9. Slack posts to /approvals/{id} with decision="approve"
10. Runtime resumes the agent → action executes → result logged
```

---

## Graduating to auto-fire

After 1-2 weeks of running with full approvals, you'll have a sense of which categories are reliably safe. Examples of common graduations:

- **First-DM lead magnet delivery** — safe to auto-fire after 50+ approved instances
- **Recurring weekly content drafts** — safe once your CMO agent's voice is dialed in
- **CRM tag updates from comments** — safe immediately (low risk)

To graduate a category to auto-fire:

1. Edit `.env`: set the variable to `false`
2. Restart the runtime
3. Watch the audit log for unexpected behavior
4. Reverse if needed (set to `true` again)

**Never** graduate these without specific careful review:
- Public posts to your main account
- Refund processing
- Email broadcasts to lists > 100 people
- Anything involving signed agreements or legal commitments

---

## Per-agent overrides

You can override approval policy per-agent in YAML:

```yaml
# This specific agent ALWAYS requires approval, regardless of global settings
permissions:
  always_require_approval: true
```

```yaml
# This specific agent NEVER requires approval (use only for read-only, low-risk agents)
permissions:
  always_require_approval: false
```

---

## Slack interactive buttons setup

For the buttons in Slack messages to work, your Slack app needs:

1. **OAuth scopes:**
   - `chat:write` (post messages)
   - `chat:write.public` (post in channels you're not in)
   - `commands` (handle interactive components)

2. **Interactive Components configured:**
   - Settings → Interactivity & Shortcuts → On
   - Request URL: `https://crew.yourdomain.com/slack/interactive`
   - (This endpoint receives Slack button clicks and forwards to `/approvals/{id}`)

3. **Event Subscriptions** (optional, for richer Slack interactions):
   - Subscribe to `message.channels`, `app_mention` if you want to chat with agents in Slack

---

## Manual approval via API (no Slack)

If you don't have Slack set up, you can approve manually via cURL:

```bash
# List pending approvals
curl -H "x-api-key: $KEY" https://crew.yourdomain.com/audit?event_type=agent.approval.requested&limit=10

# Approve a specific one
curl -X POST https://crew.yourdomain.com/approvals/abc-123-uuid \
  -H "x-api-key: $KEY" \
  -H "Content-Type: application/json" \
  -d '{"decision": "approve", "approver": "quentin@xcerebro.ai"}'

# Reject
curl -X POST https://crew.yourdomain.com/approvals/abc-123-uuid \
  -H "x-api-key: $KEY" \
  -H "Content-Type: application/json" \
  -d '{"decision": "reject", "approver": "quentin@xcerebro.ai", "note": "Tone is too aggressive"}'
```

---

## Audit trail

Every approval is logged. Query history:

```bash
curl -H "x-api-key: $KEY" "https://crew.yourdomain.com/audit?event_type=approval.approve&limit=50"
```

You can review:
- What agent requested the action
- What the action was
- Who approved/rejected
- When
- Any notes

This audit trail is critical for debugging agent behavior and for satisfying compliance / legal requirements.

---

## Bottom line

Start conservative. Graduate gradually. Trust is built one approved action at a time.
