# Railway Deployment — Detailed Walkthrough

> If `01-quick-start.md` was the highlight reel, this is the director's cut.

This guide assumes you're running the full Xcerebro 2.0 stack on Railway. We'll deploy 4 services that talk to each other through Railway's private network.

---

## The 4 services we're deploying

| Service | Image | Approx. monthly cost | Purpose |
|---|---|---|---|
| **PostgreSQL** | Railway managed | ~$5 | Shared database for all services |
| **Redis** | Railway managed | ~$3 | Job queues for n8n + Dify |
| **n8n** | `docker.n8n.io/n8nio/n8n:latest` | ~$5-10 | Workflow automation |
| **Dify** (10 sub-services) | `langgenius/dify-*` | ~$20-50 | AI app + RAG layer |
| **Agent Runtime (this repo)** | Built from `crew/Dockerfile` | ~$5-10 | CrewAI agents |
| **Postiz** (optional) | `ghcr.io/gitroomhq/postiz-app` | ~$5-10 | Social scheduling |

**Total Railway cost: $43-93/mo at MVP, scaling with usage.**

---

## Recommended deployment order

Deploy in this order to avoid dependency issues:

1. PostgreSQL + Redis (databases first)
2. n8n (uses Postgres)
3. Dify (uses Postgres + Redis)
4. Agent Runtime (uses Postgres + Redis, calls n8n + Dify)
5. Postiz (optional, uses Postgres + Redis)

---

## Step-by-step

### A. Create a new Railway project

1. Sign in to [railway.com](https://railway.com)
2. Click **"+ New Project"**
3. Name it `xcerebro-2.0`
4. Skip initial service selection — we'll add them manually

### B. Add PostgreSQL

1. Click **"+ New" → "Database" → "PostgreSQL"**
2. Wait for the database to spin up (~1 minute)
3. Click on the Postgres service → **"Connect"** tab → save the connection string

This gives you a DATABASE_URL that other services will reference.

### C. Add Redis

1. Click **"+ New" → "Database" → "Redis"**
2. Wait ~30 seconds
3. Note the REDIS_URL from the Connect tab

### D. Deploy n8n

**Option A: Use Railway template (faster)**
1. In a separate tab, go to [Railway n8n template](https://railway.com/deploy/n8n)
2. Click "Deploy Now" → connect to your existing project (drop-down)
3. Railway provisions n8n + auto-connects to Postgres
4. Wait ~2 minutes
5. Generate a public domain (Service → Settings → Networking → Generate Domain)

**Option B: Deploy from Docker image (manual)**
1. In your Railway project, click **"+ New" → "Docker Image"**
2. Image name: `docker.n8n.io/n8nio/n8n`
3. Add environment variables:
   ```
   DB_TYPE=postgresdb
   DB_POSTGRESDB_HOST=${{Postgres.PGHOST}}
   DB_POSTGRESDB_PORT=${{Postgres.PGPORT}}
   DB_POSTGRESDB_DATABASE=n8n
   DB_POSTGRESDB_USER=${{Postgres.PGUSER}}
   DB_POSTGRESDB_PASSWORD=${{Postgres.PGPASSWORD}}
   N8N_PORT=${{PORT}}
   WEBHOOK_URL=https://${{RAILWAY_PUBLIC_DOMAIN}}
   N8N_ENCRYPTION_KEY=<generate with: openssl rand -base64 32>
   GENERIC_TIMEZONE=America/Chicago
   EXECUTIONS_DATA_PRUNE=true
   EXECUTIONS_DATA_MAX_AGE=168
   ```
4. Add a **Volume** mounted at `/home/node/.n8n` (1GB is fine to start)
5. Generate a public domain
6. Wait for deploy → first-load opens the n8n setup wizard

### E. Deploy Dify

**Use the official template** — manual deploy of all 10 services is painful.

1. Open [Railway Dify template](https://railway.com/deploy/dify-ai-workflow) in a new tab
2. Click "Deploy Now" → connect to your project
3. Wait ~5 minutes for all 10 services to come up
4. Open the Nginx service's public domain → first-run wizard
5. Configure your model provider (Anthropic API key)
6. Generate an API key in Account Settings

### F. Deploy the Agent Runtime

1. Fork this repo to your GitHub
2. In Railway: **"+ New" → "GitHub Repo"** → select your fork
3. Railway detects the `Dockerfile` in `crew/`
4. Add environment variables (see `.env.example` for the full list)
5. Connect to Postgres + Redis using Railway reference variables:
   ```
   DATABASE_URL=postgresql://${{Postgres.PGUSER}}:${{Postgres.PGPASSWORD}}@${{Postgres.PGHOST}}:${{Postgres.PGPORT}}/crew
   REDIS_URL=${{Redis.REDIS_URL}}
   ```
6. Generate a public domain
7. Verify with `curl https://your-domain/health`

### G. (Optional) Deploy Postiz

1. **"+ New" → "Docker Image"** → `ghcr.io/gitroomhq/postiz-app:latest`
2. Add Postgres + Redis references
3. Add Postiz-specific env vars (see [Postiz docs](https://docs.postiz.com))
4. Generate domain

---

## Cost monitoring

Railway charges by usage. To prevent surprises:

1. **Set a usage limit** in your account settings — e.g., $100/mo cap
2. **Enable email alerts** at 50%, 75%, 90% of cap
3. **Pause services you're not using** — Railway only bills for active services

---

## Custom domain

To use `crew.yourdomain.com` instead of `crew-production-xxxx.up.railway.app`:

1. Service → Settings → Networking → Custom Domain
2. Add your domain (e.g., `crew.yourdomain.com`)
3. Railway gives you a CNAME target
4. In your DNS provider, create a CNAME record pointing to Railway's target
5. Wait ~5 minutes for SSL provisioning

---

## Updating

When n8n or Dify ships a new version:

```bash
# Just redeploy — Railway pulls the latest image
# (Or pin a specific version in the image name to control upgrades)
```

For the agent runtime: push to your fork's main branch. Railway auto-redeploys.

---

## Common gotchas

- **n8n webhooks return 502:** The container is still booting. Wait 30 more seconds.
- **Dify can't connect to Postgres:** Check that `DB_DATABASE=dify` (not `xcerebro`) — Dify uses its own DB.
- **Agent runtime can't reach n8n:** Use the public Railway URL for `N8N_BASE_URL`, not the internal one. CrewAI tools sometimes need to make external calls.
- **Volume not persisting:** You have to attach the volume *before* first deploy. If you forgot, attach it now and redeploy — first-deploy data will be lost.

See [`docs/08-troubleshooting.md`](08-troubleshooting.md) for more.
