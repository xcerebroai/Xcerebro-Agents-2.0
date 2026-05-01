# LICENSES.md

This document explains the licensing for Xcerebro 2.0 and the open-source tools it relies on. Read this carefully if you plan to redistribute or modify the toolkit.

---

## Xcerebro 2.0 Curated Toolkit

The contents of this repo — the agent YAMLs, the FastAPI runtime code, the n8n workflow JSON files, the Dify configurations, the documentation — are provided to Xcerebro members under the **Xcerebro Member License**.

**You may:**
- Deploy this toolkit on your own infrastructure for your own business use
- Modify the agent definitions, workflows, and configurations to fit your needs
- Reference the runtime code as part of your own internal projects

**You may not:**
- Resell this toolkit as-is to other parties
- Sell hosted access to this toolkit as a SaaS service
- Redistribute the curated configurations to non-members

For commercial redistribution rights, contact xcerebro.ai/license.

---

## Underlying Open-Source Tools

This toolkit relies on five open-source projects. Each has its own license, which YOU as the deployer must comply with.

---

### CrewAI — MIT License

**License:** [MIT](https://github.com/crewAIInc/crewAI/blob/main/LICENSE)

**What you can do:** Almost anything. Use, modify, redistribute, sell. Just keep the MIT notice in any copies of CrewAI source code.

**Source:** https://github.com/crewAIInc/crewAI

---

### LangGraph (LangChain) — MIT License

**License:** [MIT](https://github.com/langchain-ai/langgraph/blob/main/LICENSE)

**What you can do:** Same as CrewAI — full freedom under MIT terms.

**Source:** https://github.com/langchain-ai/langgraph

---

### Dify — Apache 2.0 License (Modified)

**License:** [Modified Apache 2.0](https://github.com/langgenius/dify/blob/main/LICENSE)

**Restriction:** Dify's modified Apache 2.0 license includes a **multi-tenant SaaS clause**. You cannot run Dify as a multi-tenant SaaS that competes with Dify Cloud without a commercial license from langgenius.

**What you can do:**
- Self-host Dify for your own business use ✅
- Modify Dify's source code for your own deployment ✅
- Run a single-tenant Dify instance for your team ✅

**What you cannot do:**
- Sell hosted multi-tenant Dify-as-a-service ❌

For Xcerebro 2.0: **You're fine.** Each buyer self-hosts their own single-tenant instance. We're not running multi-tenant SaaS.

**Source:** https://github.com/langgenius/dify

---

### n8n — Sustainable Use License (fair-code)

**License:** [Sustainable Use License](https://github.com/n8n-io/n8n/blob/master/LICENSE.md)

**What it means:** n8n uses a "fair-code" license. Free for:
- Internal business use ✅
- Self-hosting on your own servers ✅
- Modifying for your own use ✅

Restrictions on:
- Hosting n8n as a competitive service to n8n Cloud ❌
- Selling modifications of n8n itself ❌

**For Xcerebro 2.0:** We sell GUIDES + WORKFLOW TEMPLATES that USE n8n. We do NOT sell n8n itself. Buyers self-host their own n8n instance. We're clean.

**Source:** https://github.com/n8n-io/n8n

---

### Postiz — AGPL-3.0 License

**License:** [AGPL-3.0](https://github.com/gitroomhq/postiz-app/blob/main/LICENSE.txt)

**What it means:** AGPL is a strong copyleft license. If you modify Postiz and host it for users to access over a network, you must share your modifications.

**For Xcerebro 2.0:**
- We don't modify Postiz source ✅
- Each buyer self-hosts their own Postiz on their Railway instance ✅
- We don't run a hosted Postiz service for users ✅

If you modify Postiz for your deployment, you must publish your modifications. Most buyers won't modify Postiz, so this isn't a concern.

**Source:** https://github.com/gitroomhq/postiz-app

---

## Summary Table

| Tool | License | Buyer's restriction |
|---|---|---|
| CrewAI | MIT | None |
| LangGraph | MIT | None |
| Dify | Apache 2.0 (modified) | No multi-tenant SaaS |
| n8n | Sustainable Use | No competitive hosting |
| Postiz | AGPL-3.0 | Publish modifications if hosted for users |

For 99% of Xcerebro buyers (single-business operators self-hosting on Railway), all licenses are clean. You're not redistributing, you're not running multi-tenant SaaS, and you're not modifying the source of these tools.

---

## Disclaimer

This document is informational. We are not lawyers. If you plan to do anything beyond standard self-hosted use (e.g., redistributing the toolkit, building a competing product, running multi-tenant SaaS), consult an attorney to review the licenses for your specific use case.

---

## Attribution

Xcerebro 2.0 stands on the shoulders of giants. Thank you to:

- The **CrewAI team** for the agent orchestration framework
- The **LangChain team** for LangGraph and the broader ecosystem
- The **Dify team (langgenius)** for the LLM application platform
- The **n8n team** for the workflow automation engine
- The **Postiz team (Gitroom)** for the social media scheduling platform
- The **Anthropic team** for the foundational LLMs that power agent reasoning

Without the open-source community, none of this would be possible.
