# Operator Dashboard — Setup Guide

> Single HTML file. Drop it anywhere. Points at your runtime URL. Live status of agents, executions, approvals, costs.
>
> Setup time: 2 minutes.

---

## What this dashboard shows

- **Runtime status** — green/red dot + uptime
- **Agents loaded** — total count + Tier A vs Tier B breakdown
- **Executions today** — total + last hour
- **Pending approvals** — what's waiting in Slack for your tap
- **LLM cost today** — estimated daily spend + monthly projection
- **Recent executions table** — last 15, with timestamp, agent, action, status
- **All agents grid** — every agent with active/idle status

Auto-refreshes every 30 seconds. Local-storage remembers your runtime URL.

---

## Setup option 1: Open it locally (easiest, 30 sec)

1. Save `dashboard.html` to your Mac
2. Double-click it — opens in your browser
3. Paste your Railway runtime URL in the input (top right)
4. Click **Connect**
5. Done. Bookmark the local file.

The dashboard runs entirely in your browser. No server needed. Your runtime URL is saved in localStorage for next time.

---

## Setup option 2: Deploy on Vercel (recommended for daily use, 2 min)

If you want to access it from anywhere (phone, other computers):

1. Go to https://vercel.com → **Add New** → **Project**
2. Click **Deploy a static site**
3. Drag-and-drop the `dashboard.html` file (or upload as a single-file repo)
4. Click **Deploy**
5. You get a URL like `xcerebro-dashboard.vercel.app`
6. Bookmark it. Add to your phone home screen.

---

## Setup option 3: Host on your existing xcerebro.ai (advanced)

If your `xcerebro.ai` site is on GitHub Pages or Netlify:

1. Add `dashboard.html` to your site repo at `/operator/dashboard.html`
2. Push
3. Visit `xcerebro.ai/operator/dashboard.html`

Now buyers who deploy can also access this dashboard at a branded URL.

> **Security note:** This dashboard talks directly to the runtime from the browser. It does not store credentials. The runtime URL is per-buyer (their own Railway instance), so there's no cross-buyer data leakage. But: if you host the dashboard on `xcerebro.ai`, anyone who visits and pastes a runtime URL can see that runtime's data. This is fine because the runtime should already be authenticated (basic auth or API key — see CORS note below).

---

## Required runtime endpoints

The dashboard expects these endpoints on your runtime (already defined in `crew/main.py`):

| Endpoint | What it returns | Used by |
|---|---|---|
| `GET /health` | `{ "status": "ok", "uptime": 3600 }` | Status KPI |
| `GET /agents` | List of agents with `id, name, tier, function, last_invoked_at` | Agents KPI + grid |
| `GET /audit?limit=20` | Recent execution log entries | Executions KPI + table |
| `GET /approvals?status=pending` | List of pending approvals | Approvals KPI |

If `/approvals` doesn't exist yet, the dashboard gracefully shows "—" instead of breaking.

---

## CORS configuration

If you deploy the dashboard on a different domain (Vercel, your site), you may hit CORS errors when it tries to call your Railway runtime.

**Fix:** In `crew/main.py`, the FastAPI runtime should already have CORS configured:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:*",
        "https://xcerebro.ai",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)
```

If you opened the file from your Mac (Option 1), CORS isn't an issue — `file://` origin gets a pass on most browsers.

---

## What to watch on this dashboard

**Daily check (10 seconds):**
- Runtime status: green ✓
- Pending approvals: anything > 5? Open Slack.
- Cost today: under your budget?

**Weekly check (2 minutes):**
- Executions today / yesterday — should trend up as you activate more workflows
- Are any agents stuck at "idle" forever? May indicate an unused workflow.
- Cost projection — is monthly going to hit your Railway+LLM budget?

**Red flags to investigate:**
- Runtime status: red 🔴 — runtime is down. Check Railway logs immediately.
- Pending approvals > 20 — you're not keeping up. Open Slack and process them.
- Cost trending way up — an agent might be looping. Check executions table for one agent dominating.

---

## Customization

The dashboard is a single HTML file. Edit it directly:

- **Brand colors:** search/replace `#3B82F6` (electric blue) with your brand color
- **Add KPIs:** copy a `<div class="kpi-card">` block, fetch the data you want, render it
- **Change refresh interval:** find `setInterval(refreshAll, 30000)` and change `30000` (milliseconds)
- **Add charts:** add Chart.js or Recharts via CDN — there's room in the layout

Don't be precious about it. It's yours.

---

## What this saves you

Without the dashboard:
- Buyers ask "is my runtime working?" → you ask "have you checked the Railway dashboard?" → they don't know how
- You can't easily monitor your own deployment without logging into Railway every time
- No central place to see all 9 workflows + 92 agents at once

With the dashboard:
- Buyers bookmark it, check it daily, feel in control of their deployment
- You see your own ops in one glance from your phone
- Onboarding feels professional, not piecemeal

---

## Future enhancements (v2.1+)

- Real-time WebSocket updates (instead of 30s polling)
- Approval action buttons directly in the dashboard (one-tap approve from any device)
- Historical charts (executions per day, cost trend, top agents)
- Per-agent drilldown when you click an agent card
- Export to CSV button on executions table
- Dark/light mode toggle (currently dark only — fits the brand)

These are nice-to-have. Ship the simple version first, see what buyers actually request.

---

## Troubleshooting

**"Cannot reach runtime: TypeError: Failed to fetch"**
- Check the URL is correct (no trailing slash issues — the script handles it but worth checking)
- Check the runtime is actually deployed and healthy in Railway
- If on Vercel/different domain, this is a CORS error — see CORS section above

**Numbers all show "—"**
- Runtime is connected but endpoints aren't returning data
- Check `crew/main.py` — make sure `/agents`, `/audit`, etc. are defined
- Use the dashboard's browser console (F12) to see exact errors

**Dashboard works locally but not on Vercel**
- It's CORS. Update `crew/main.py` to allow your Vercel domain in `allow_origins`.

---

## Files

```
extras/health-dashboard/
├── dashboard.html       ← Single file, no dependencies
└── SETUP.md             ← This file
```

That's it. Open the HTML, paste the URL, get visibility.
