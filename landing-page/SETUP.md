# Landing Page — Setup Guide

> Single-file landing page for xcerebro.ai. Drop-in replacement.
>
> Setup time: 2 minutes (push to your hosting)

---

## What's here

`index.html` — the complete v2.0 landing page

**Structure:**
- Sticky nav with scroll-to anchors
- Hero with terminal animation showing autonomous activity
- "What changed in 2.0" comparison vs v1.0
- "What's inside" 9-feature grid
- **Two-track section:**
  - Track 1: VIP Membership ($97/mo or $500/yr) → routes to Skool
  - Track 2: Custom Install ($3K-$18K+) → routes to DM/email contact
- FAQ — 10 honest answers
- Final CTA + footer

**No Stripe links to configure.** VIP goes through Skool. Custom Install goes through DM/email + manual invoicing.

---

## Setup steps

### 1. Verify the Skool link (30 sec)

In `index.html`, the VIP CTA links to `https://skool.com/aicheatcodes`. Confirm that's correct and that subscribing through there is what you want.

### 2. Update contact info if needed (30 sec)

The Custom Install section directs people to:
- DM @Quentin Flores in Skool
- Email operator@xcerebro.ai

Change either if you want different contact methods.

### 3. Deploy

**Option A: GitHub Pages (your current setup)**
1. Replace your existing `index.html` on the `xcerebroai/xcerebroai.github.io` repo (or wherever xcerebro.ai is currently hosted)
2. Commit and push
3. Wait 30 seconds for GitHub Pages to rebuild
4. Visit xcerebro.ai

**Option B: Netlify / Vercel**
1. Drag-and-drop the file
2. Set custom domain xcerebro.ai
3. Done

---

## What to keep from your existing site

If `xcerebro.ai/agents.html` (the v1.0 directory of 199 markdown agents) is still serving v1.0 buyers — keep it. The new `index.html` is just the landing/sales page.

Recommended structure:

```
xcerebro.ai/
├── index.html             ← New landing page (sales + tracks)
├── agents.html            ← Existing v1.0 agent directory (keep)
└── operator/
    └── dashboard.html     ← Optional: operator dashboard from extras/
```

---

## What to update over time

**Within first 30 days:**
- Add the Loom URL (when recorded) to the First-Run Walkthrough feature card
- Add 1-3 testimonials below the tracks section
- Add "X operators deployed" social proof in the hero

**At month 1:**
- Replace the terminal animation with real screenshots or testimonial quotes
- Add a /case-studies page showing real operator results

---

## Performance

- Single HTML file: ~35 KB
- Inline CSS: no extra requests
- Google Fonts: 1 request, ~80ms
- Total page load: <500ms on broadband
- Mobile responsive

---

## Maintenance

This page is intentionally low-maintenance:
- No build step
- No JS dependencies
- No CMS
- Edits are: open file, edit text, save, push

---

If anything in the copy doesn't sound right for your voice, edit it. The technical structure is what matters; the words can flex.
