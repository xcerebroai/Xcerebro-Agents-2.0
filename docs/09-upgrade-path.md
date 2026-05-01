# Upgrade Path — Adding More Agents Over Time

> Don't try to activate everything on day 1. This is the recommended ramp-up.

---

## Week 1: Foundation

**Goal:** Prove the system works. Build trust with one autonomous flow.

- ✅ Deploy the stack (Railway)
- ✅ Configure environment variables
- ✅ Activate **only** the Daily KPI Brief workflow
- ✅ Watch it run for 7 days. Verify outputs land in Slack.
- ✅ Tune the agents' instructions if the brief is too long, too short, or off-tone

**Week 1 success criteria:** You wake up to a useful Slack brief every morning. You trust the data.

---

## Week 2: First Real Automation

**Goal:** Add ONE customer-touching workflow with approval gates.

- ✅ Activate **02-comment-to-dm**
- ✅ Set up ManyChat to webhook into n8n
- ✅ Test with a real comment
- ✅ Approve the first 10 DMs manually in Slack
- ✅ Watch for tone, accuracy, conversion rate

**Week 2 success criteria:** DMs are sending. Quality is high. You're approving them in <30 seconds each.

---

## Week 3: Expand to More Workflows

**Goal:** Activate 3-5 more workflows.

Recommended next:

- **03-weekly-ceo-summary** (Sunday 6pm — strategic review for the week ahead)
- **04-stripe-payment-celebration** (Slack pings on every new sale)
- **05-stripe-failed-payment** (CFO triages failed payments)
- **08-ads-feedback-loop** (Daily Meta Ads recommendations from CMO)

---

## Week 4: Graduate Auto-Fire

**Goal:** Stop manually approving every action. Promote categories you trust.

After 100+ approved DM lead-magnet deliveries with consistent quality:
```
APPROVAL_REQUIRED_FOR_DM=false  # Only for lead-magnet DMs (use whitelist)
```

After 50+ approved Slack notifications:
```
# Internal notifications already auto-fire — no change needed
```

Keep these requiring approval indefinitely:
```
APPROVAL_REQUIRED_FOR_PUBLIC_POST=true
APPROVAL_REQUIRED_FOR_REFUND=true
APPROVAL_REQUIRED_FOR_PAYMENT=true
APPROVAL_REQUIRED_FOR_EMAIL=true
```

---

## Month 2: Specialist Tier B Agents

**Goal:** Add specialist agents for tasks the leadership crew delegates.

In `agents/tier-b/`:
- Hook Writer
- Copy Chief
- Image Director
- Trend Spotter
- Lead Magnet Designer

Each has a YAML file. Drop in, restart runtime, they're loaded.

The Tier A leadership agents (CMO, etc.) will start delegating to them automatically based on the `delegation_rules` in their YAML.

---

## Month 3: Custom Agents

**Goal:** Build agents specific to YOUR business.

Examples we've seen operators add:

- **REI Cold Caller QA Agent** — listens to call recordings, flags the bad ones
- **Skool Cohort Engagement Agent** — daily check on member activity, flags at-risk members
- **Property Owner Outreach Agent** — drafts personalized outreach for absentee owners

Process:
1. Copy `agents/tier-a/auto-cmo.yaml` as a template
2. Rename, update the role/goal/backstory for your use case
3. Define what tools it can call
4. Set approval requirements
5. Add to the registry (auto-loaded on next runtime restart)

---

## Quarter 2: Multi-Crew Coordination

**Goal:** Build crews that span departments.

Example: **Cohort Launch Crew**
- Members: CMO, Content Strategist, Hook Writer, Copy Chief, Sales Manager, Customer Support
- Triggered: 2 weeks before cohort start date
- Tasks: Build content arc, write sales emails, prep onboarding docs, schedule support coverage

This is where Xcerebro 2.0 starts to feel like a real workforce — multiple agents collaborating on a shared goal.

---

## Quarter 3: Custom Tools

**Goal:** Extend agents with your own Python tools.

Add to `crew/tools/`:

```python
from crewai.tools import tool

@tool
def lookup_property_in_propstream(address: str) -> dict:
    """Look up a property in PropStream by address."""
    # Your implementation
    return result
```

Reference in agent YAML:
```yaml
permissions:
  can_call_tools:
    - lookup_property_in_propstream
```

The agent can now call your custom tool autonomously.

---

## Year 1+: Compound

The real win is when ~30 days of audit logs reveal patterns you didn't expect:

- "The DM Agent converts 4x better in the morning vs evening"
- "Posts that mention 'Hormozi' get 2x engagement"
- "Tax-delinquent leads close 3x more often than probate leads"

These insights, fed back into the agent prompts, create a compounding flywheel. Each month, the agents get sharper because YOU got sharper.

---

## What NOT to do

- ❌ Don't activate everything on day 1
- ❌ Don't graduate categories to auto-fire without 30+ approved instances
- ❌ Don't build custom agents until the off-the-shelf ones are running clean
- ❌ Don't expand to Tier B specialists before Tier A leadership is solid
- ❌ Don't add new tool integrations weekly — pick 1, get it working, then next

The system rewards patience. Operators who try to use everything in week 1 burn out. Operators who add one new thing every 1-2 weeks compound.

---

## Need help expanding?

- **Skool VIP:** post your custom agent YAMLs for community feedback
- **Custom Install (Done-For-You):** pay us to expand the system for you ($3K for 1 agent, $5K for 2, $10K for 5, $18K for 10, custom quote for 10+)
- **Custom development:** if you want a brand new tool integration, reach out via xcerebro.ai/contact

But for most operators, the catalog of 18 leadership + 80 specialist agents is more than enough. Start there.
