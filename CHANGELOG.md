# Changelog

All notable changes to Xcerebro 2.0 are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [2.0.0] — Initial Release

The first release of Xcerebro 2.0 — the autonomous workforce upgrade.

### Added

**Core architecture:**
- FastAPI-based agent runtime (CrewAI + LangGraph)
- PostgreSQL audit log
- Redis-backed job queues
- Slack-based human approval system
- Cost controls (max tokens, max tasks, daily spend cap)

**Tier A — 18 leadership orchestrators:**
- `auto-ceo` — Strategic direction + delegation
- `auto-coo` — Operations + project tracking
- `auto-cfo` — Financial visibility + reporting
- `auto-cmo` — Marketing growth engine
- `auto-sales-manager` — Pipeline management
- `auto-appointment-setter` — Lead-to-call conversion
- `auto-dm-agent` — Conversational front line
- `auto-social-media-manager` — Publishing + scheduling
- `auto-content-strategist` — Content calendar + theme arcs
- `auto-lead-manager` — CRM hygiene + lead routing
- `auto-customer-support` — Support ticket triage
- `auto-project-manager` — Task breakdown + tracking
- `auto-deal-analyst` — Real estate deal analysis
- `auto-title-specialist` — Title review + curative checklists
- `auto-data-research` — Online research + competitive intel
- `auto-automation-engineer` — n8n workflow building + maintenance
- `auto-compliance` — Compliance review (TCPA, CAN-SPAM, FTC)
- `auto-executive-assistant` — Calendar + inbox management

**Tier B — 74 operational specialists across 7 functional pods:**

*Marketing pod (16):* hook-writer, copy-chief, image-director, lead-magnet-designer, trend-spotter, ads-strategist, video-script-writer, email-copywriter, seo-strategist, seo-content-writer, youtube-strategist, instagram-strategist, tiktok-strategist, linkedin-strategist, twitter-strategist, podcast-strategist

*Sales pod (6):* high-ticket-sales-rep, sales-script-writer, sales-call-analyst, crm-cleaner, renewal-specialist, partnership-developer

*Operations pod (8):* sop-writer, workflow-optimizer, vendor-manager, hiring-screener, documentation-curator, internal-newsletter-writer, calendar-defender, inbox-zero-agent

*Finance pod (5):* revenue-analyst, expense-auditor, invoice-manager, forecast-modeler, tax-prep-specialist

*Content production pod (8):* video-editor, thumbnail-designer, captions-writer, repurposing-specialist, podcast-producer, blog-writer, course-content-writer, brand-voice-keeper

*Customer experience pod (6):* onboarding-specialist, retention-specialist, community-manager, event-coordinator, survey-runner, review-collector

*Data and research pod (6):* competitive-analyst, trends-analyst, market-researcher, survey-data-analyst, metrics-dashboard-builder, pricing-researcher

*REI pod (10):* wholesale-acquisitions-specialist, disposition-specialist, subject-to-specialist, creative-finance-strategist, rei-cold-caller-qa, market-comp-analyst, rehab-estimator, foreclosure-tracker, title-research-specialist, rei-marketing-specialist

*Compliance and risk pod (4):* contract-reviewer, privacy-compliance-agent, ip-defender, dispute-handler

*Cross-functional (5):* knowledge-base-curator, integrations-specialist, ai-cost-monitor, integration-tester, documentation-writer

**Tier C — Existing 199 markdown presets:**
- Continue to install via existing Claude Code mechanism
- Stay as on-demand specialists, NOT autonomous
- Documented in `agents/tier-c/README.md`

**Pre-built crews:**
- `daily-kpi-brief` — CFO + CMO + Sales Manager + CEO synthesize daily brief
- `weekly-content-production` — CMO directs Trend Spotter + Hook Writer + Copy Chief + Image Director + Social Media Manager
- `comment-to-dm-pipeline` — DM Agent + Compliance + Lead Manager coordinate

**Pre-built n8n workflows (9):**
- `01-daily-kpi-brief.json` — Daily 6am Slack brief
- `02-comment-to-dm.json` — Comment trigger → DM lead magnet
- `03-weekly-ceo-summary.json` — Sunday 6pm strategic review
- `04-stripe-payment-celebration.json` — New payment Slack notification
- `05-stripe-failed-payment.json` — Failed payment CFO triage
- `06-skool-cohort-heartbeat.json` — Daily Skool engagement check
- `07-story-viewer-reactor.json` — Instagram story reply intent classifier
- `08-ads-feedback-loop.json` — Daily Meta/Google Ads brief
- `09-meeting-prep-brief.json` — 30-min-before-meeting brief

**Documentation (9 docs):**
- `01-quick-start.md` — 30-60 minute deploy guide
- `02-railway-deploy.md` — Detailed Railway walkthrough
- `03-configure-n8n.md` — n8n workflow setup
- `04-configure-dify.md` — Dify knowledge bases
- `05-agent-runtime.md` — CrewAI runtime explained
- `06-approval-system.md` — Human approval flow
- `07-buyer-cost-guide.md` — Real cost expectations
- `08-troubleshooting.md` — Common issues + fixes
- `09-upgrade-path.md` — Recommended ramp-up

**Deployment:**
- `docker-compose.yml` — Full local 11-service stack
- `railway.json` — Railway deployment config
- `.env.example` — Exhaustive environment variable template
- `scripts/install.sh` — Pre-flight check helper
- `scripts/verify.sh` — Post-deploy health check
- `scripts/init-multiple-databases.sh` — Postgres multi-DB init

### Architecture

- **5 foundation repos** (n8n, Dify, CrewAI, LangGraph, Postiz)
- **Railway-first deployment** with one-click templates for n8n + Dify
- **Self-hosted, single-tenant** — buyer owns all data and credentials
- **License-clean** across MIT, Apache 2.0, AGPL, and Sustainable Use

### Cost

Buyer's monthly cost: **$65–$285/mo** (Railway infrastructure + LLM API calls)

---

## Roadmap

### [2.1.0] — Planned

- Additional Tier B agents based on operator feedback
- More n8n workflows (15+ total in catalog)
- Dify pre-configured knowledge base imports
- Slack interactive button approval handler
- Cost dashboard widget for the operator

### [2.2.0] — Planned

- White-glove deployment service ("Tier 3")
- Custom integrations (industry-specific)
- Multi-replica scaling for high-volume operators
- Webhook signing + verification for production hardening

---

## License

This curated toolkit is provided to Xcerebro members under the Xcerebro Member License. See `LICENSES.md` for details on the underlying open-source components.
