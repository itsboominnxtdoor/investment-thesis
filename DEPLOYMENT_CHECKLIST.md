# Deployment Checklist

## Pre-Deploy Checks

- [ ] All 38 tests passing: `pytest -v`
- [ ] `.env` file has all required variables
- [ ] Git pushed to `origin/main`

## Required Environment Variables

### Backend (Railway)
```
GROQ_API_KEY=gsk_your_key_here
FINANCIAL_DATA_API_KEY=your_fmp_key_here
EDGAR_USER_AGENT=ThesisEngine your@email.com
CORS_ORIGINS=https://investment-thesis-r1ev.vercel.app
LOG_FORMAT=json
DATABASE_URL=(auto-injected by Railway Postgres)
```

### Frontend (Vercel)
```
API_BACKEND_URL=https://your-railway-url.up.railway.app
```

## Deploy Steps

### 1. Push to GitHub
```bash
git add .
git commit -m "Fix Dockerfile and railway.toml"
git push origin main
```

### 2. Railway Backend

1. Go to https://railway.app
2. Select your project (or create new from GitHub)
3. **Root Directory:** `backend`
4. **Start Command:** (handled by `railway.toml`)
5. Add **PostgreSQL** database (Railway → New → Database → PostgreSQL)
6. Add **Redis** (Railway → New → Datastore → Redis)
7. Set environment variables (Railway → Variables)
8. Deploy should trigger automatically on push

**Wait for health check to pass:**
- Visit: `https://your-project.up.railway.app/health`
- Should return: `{"status": "ok"}`

### 3. Vercel Frontend

1. Go to https://vercel.com
2. **Add New → Project**
3. Import `investment-thesis` repository
4. **Root Directory:** `frontend`
5. Set `API_BACKEND_URL` to Railway URL
6. **Deploy**

**Verify:**
- Visit: `https://investment-thesis-r1ev.vercel.app`

### 4. Post-Deploy: Seed Companies

Once backend is healthy, seed the database:

**Option A: Via API**
```bash
curl -X POST https://your-railway-url.up.railway.app/api/v1/companies/bulk-ingest
```

**Option B: Via Railway Shell**
1. Railway → Deployments → New → Shell
2. Run: `python scripts/seed_companies.py`

## Troubleshooting

### Health Check Failing

1. **Check logs:** Railway → Deployments → View Logs
2. **Common issues:**
   - Missing env vars → Add in Railway Variables
   - DB not connected → Check DATABASE_URL is set
   - Migration hanging → Check PostgreSQL addon is active

### Database Errors

```bash
# In Railway Shell
alembic upgrade head
```

### LLM Errors

- Verify `GROQ_API_KEY` is valid: https://console.groq.com
- Check quota remaining

### Frontend Can't Connect

- Verify `API_BACKEND_URL` matches Railway URL
- Check `CORS_ORIGINS` includes Vercel URL

## Health Endpoints

| Endpoint | Purpose |
|----------|---------|
| `/health` | Basic ping (no DB check) |
| `/health/ready` | Checks DB connectivity |
| `/api/v1/companies` | List companies (verifies DB has data) |
| `/docs` | Swagger UI |

## Success Criteria

- [ ] `/health` returns `{"status": "ok"}`
- [ ] `/api/v1/companies` returns company list
- [ ] Frontend loads without errors
- [ ] Can generate business profile for a company
- [ ] Can generate thesis for a company
