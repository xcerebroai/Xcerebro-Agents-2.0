# Configuring Dify — Knowledge Bases & AI Apps

> Dify is your knowledge layer. It hosts your SOPs, scripts, product info, FAQs, and any reference docs your agents need to do their jobs.

---

## What Dify is for in Xcerebro 2.0

Three primary uses:

1. **Knowledge bases (RAG)** — Upload your SOPs, scripts, product info, and FAQs. Agents query these for context.
2. **FAQ bot** — A self-service support bot for your members/customers, embedded on your site or Skool.
3. **Internal assistant** — A chat interface where your agents (and you) can pull answers from your knowledge corpus.

---

## First-time setup (after deploying via Railway template)

### Step 1: Open Dify

Open the public Nginx domain Railway gave you. You'll land on `/install` — the first-run wizard.

### Step 2: Create your admin account

- Email + password
- This is YOUR account (the operator). You can add team members later.

### Step 3: Configure your model provider

1. Click your avatar (top right) → **Settings** → **Model Providers**
2. Find **Anthropic** (or **OpenAI**) → **Setup**
3. Paste your API key
4. Click **Save**

You should see model availability light up (Claude Sonnet, Claude Haiku, etc.).

### Step 4: Create your first knowledge base

1. **Knowledge** (left nav) → **+ Create Knowledge**
2. Choose **Import from a file** or **Sync from Notion** (recommended)
3. Upload your SOP docs, product info, FAQs
4. Set **Indexing Method**: High Quality (uses embeddings — better recall)
5. Embedding model: `text-embedding-3-large` (OpenAI) or your provider's equivalent
6. Click **Save and Process** — wait 1-3 minutes for indexing

### Step 5: Create your first app (FAQ bot)

1. **Studio** → **+ Create App** → **Chatbot**
2. Name: "Customer FAQ Bot"
3. Click **Create**
4. In the configuration:
   - **Instructions:** "You are a helpful customer support bot for [your business]. Use the knowledge base to answer questions accurately. If you don't know, say so and offer to escalate to human support."
   - **Knowledge:** Add the knowledge base you created in Step 4
5. Test the bot in the right-side preview
6. Click **Publish**
7. Copy the **API key** from Settings → API Access → save for your `.env`

---

## Recommended knowledge base structure

For Xcerebro 2.0, organize your knowledge bases into these folders:

```
1. Product Info
   - Xcerebro features
   - Pricing tiers
   - Member benefits
   - Refund policy

2. Sales Scripts & Templates
   - Discovery call framework
   - Objection responses
   - Pricing presentation
   - Follow-up cadence

3. Marketing Reference
   - Brand voice guide
   - Audience profiles
   - Top-performing hooks (last 6 months)
   - Banned phrases / brand no-go zone

4. Real Estate Operations (REI)
   - State-specific contract templates
   - Title issue playbooks
   - Probate / heirship checklists
   - Subject-to / wraps reference

5. Support FAQs
   - Common install issues
   - Account / billing FAQ
   - Skool VIP access guide

6. Compliance Reference
   - TCPA quick guide
   - CAN-SPAM checklist
   - Platform TOS (Meta, X, TikTok, LinkedIn)
   - 10DLC SMS rules
```

Each agent in `agents/tier-a/` references which knowledge bases it can read in its `data_sources` field.

---

## Sharing knowledge bases across agents

When you create an agent (CrewAI YAML), reference the Dify knowledge base by API:

```yaml
# In agents/tier-a/auto-customer-support.yaml
permissions:
  can_call_tools:
    - dify.knowledge_base.read
data_sources:
  - dify_kb.support_faqs
  - dify_kb.product_info
```

The runtime will route the agent's queries to the right Dify knowledge base via API.

---

## Adding new knowledge over time

This is the part most operators get wrong. Knowledge bases need MAINTENANCE.

**Set a weekly cadence:**

- **Mondays:** Add any new SOPs you wrote that week
- **End of month:** Review the FAQ bot's logs — what questions did it fail to answer? Add those answers.
- **Quarterly:** Audit the whole corpus. Delete outdated info. Refresh stale pricing/features.

The Customer Support agent has a built-in pattern for this. It logs every "I don't know" and surfaces them weekly for you to add to the knowledge base.

---

## Embedding the FAQ bot on your website

After publishing your FAQ chatbot in Dify:

1. **Overview** → **Embed**
2. Choose **Iframe** or **Script tag**
3. Copy the snippet
4. Paste into your website (xcerebro.ai, your Skool group, etc.)

The bot will appear as a chat widget. It pulls from the knowledge base you connected.

---

## API access for agents

Every Dify app exposes an API. The Xcerebro 2.0 agent runtime calls these APIs to query knowledge bases.

To get an API key:
1. Open the app in Dify Studio
2. **API Access** (left side panel)
3. **+ Create New Secret Key**
4. Save to your runtime's `.env` as `DIFY_API_KEY`

The runtime's `dify.knowledge_base.read` tool uses this to query.

---

## Cost notes

Dify itself is free (open-source). Your costs:

- Railway infrastructure: ~$20-50/mo for the 10-service Dify stack
- LLM API calls: charged by your provider (Anthropic / OpenAI), based on usage
- Embedding costs: ~$0.0001 per 1000 tokens for text-embedding-3-large

**Budget tip:** Use embeddings only for knowledge that's queried often. Don't embed your entire archive of Slack messages. Embed the SOPs and references that agents actually need.

---

## Common gotchas

- **Knowledge base not retrieving?** Check the indexing status. High Quality mode takes 1-3 mins per doc.
- **Bot returns "I don't have that information" for things you uploaded?** Lower the **Top K** retrieval setting (try 5 → 3) and **Score Threshold** (try 0.5 → 0.3).
- **Bot answers wrong?** Add an explicit instruction: "Only answer using the knowledge base. If unsure, say 'I don't have that information yet — let me get a human.'"
- **Want a more personal tone?** Edit the Instructions to specify voice. "Casual, peer-to-peer, no corporate-speak."

---

That's Dify. The 80/20 here is: **build 1 knowledge base, get the FAQ bot working, then expand.** Don't try to upload your entire library on day 1.
