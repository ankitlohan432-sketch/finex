# 🚀 Finex Deployment Guide — 100% Free
### GitHub → Render (Backend + DB) → Vercel (Frontend)

---

## STEP 1 — Push to GitHub

1. Go to **github.com** → click **"New repository"**
2. Name it: `finex`
3. Set to **Private** → click **Create repository**
4. Open terminal/cmd in your project folder and run:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/finex.git
git push -u origin main
```

---

## STEP 2 — Deploy Database on Render (Free PostgreSQL)

1. Go to **render.com** → Sign up with GitHub
2. Click **"New +"** → **PostgreSQL**
3. Fill in:
   - Name: `finex-db`
   - Region: Singapore (closest to India)
   - Plan: **Free**
4. Click **Create Database**
5. Wait ~1 min → copy the **"Internal Database URL"** — you'll need it next

---

## STEP 3 — Deploy Backend on Render

1. Click **"New +"** → **Web Service**
2. Connect your GitHub → select `finex` repo
3. Fill in:
   - Name: `finex-backend`
   - Root Directory: `backend`
   - Runtime: **Python 3**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Plan: **Free**
4. Click **"Advanced"** → **Add Environment Variables**:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | (paste the Internal Database URL from Step 2) |
| `SECRET_KEY` | `finex-super-secret-key-2026-change-me` |
| `SENDGRID_API_KEY` | `YOUR_SENDGRID_API_KEY` |
| `STOCK_API_KEY` | `4b49de0121444553852e9e591654f2c8` |
| `ENVIRONMENT` | `production` |

5. Click **Create Web Service**
6. Wait ~3 mins for deploy → copy your backend URL:
   `https://finex-backend.onrender.com`

---

## STEP 4 — Deploy Frontend on Vercel

1. Go to **vercel.com** → Sign up with GitHub
2. Click **"Add New Project"** → Import `finex` repo
3. Fill in:
   - Framework Preset: **Vite**
   - Root Directory: `frontend`
4. Click **"Environment Variables"** → Add:

| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://finex-backend.onrender.com` |

5. Click **Deploy**
6. Wait ~2 mins → your frontend is live at:
   `https://finex.vercel.app`

---

## STEP 5 — Update Frontend API URL

In `frontend/src/services/api.js`, make sure the base URL uses the env var:

```js
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'
```

Push to GitHub — Vercel auto-redeploys.

---

## STEP 6 — Verify SendGrid (So OTP emails work)

1. Go to **sendgrid.com** → Login
2. Settings → Sender Authentication → verify `noreply@finex.app`
   OR use a free domain from Render's built-in domain.
3. OTP emails will now reach real inboxes ✅

---

## ✅ Final URLs

| Service | URL |
|---------|-----|
| Frontend | `https://finex.vercel.app` |
| Backend API | `https://finex-backend.onrender.com` |
| API Docs | `https://finex-backend.onrender.com/docs` |
| Admin Panel | `https://finex-backend.onrender.com/admin/dashboard?email=ankitlohan432@gmail.com&username=rohan&password=finex_admin_secret_2024` |

---

## ⚠️ Important Notes

- **Render free tier sleeps** after 15 min of inactivity — first request takes ~30 sec to wake up. Upgrade to $7/mo to avoid this.
- **Never push `.env` to GitHub** — it's in `.gitignore` already.
- Every `git push` to `main` → Render + Vercel auto-redeploy.
