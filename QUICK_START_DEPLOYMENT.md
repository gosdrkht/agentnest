# Quick Start Guide

## Deploy Frontend to Vercel

### Option A: Deploy via GitHub (Recommended)

1. **Go to https://vercel.com/new**
2. **Connect GitHub**
   - Click "Continue with GitHub"
   - Authorize Vercel to access your repositories

3. **Import Project**
   - Select `gosdrkht/agentnest`
   - Click "Import"

4. **Configure Project**
   - **Framework**: React
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

5. **Environment Variables**
   - Click "Environment Variables"
   - Add new variable:
     - **Name**: `REACT_APP_API_URL`
     - **Value**: `https://agentnest-api.railway.app` (update after backend deployment)

6. **Deploy**
   - Click "Deploy"
   - Wait for build to complete (~2-3 minutes)
   - Your frontend URL: `https://agentnest-XXXXX.vercel.app`

---

## Deploy Backend to Railway

### Prerequisites
- Railway account (free at https://railway.app)

### Steps

1. **Create New Project**
   - Go to https://railway.app/dashboard
   - Click "New Project"
   - Select "Deploy from GitHub"
   - Select `gosdrkht/agentnest` repository

2. **Configure Backend Service**
   - Click "Configure"
   - Select `backend` as root directory
   - Railway will auto-detect Python runtime

3. **Add Services**

   **a) PostgreSQL Database**
   - Click "Add Plugin"
   - Select "PostgreSQL"
   - Railway creates automatically with `DATABASE_URL` env var

   **b) Redis Cache**
   - Click "Add Plugin"
   - Select "Redis"
   - Railway creates automatically with `REDIS_URL` env var

4. **Set Environment Variables**
   - In backend service settings, add:
   ```
   ENVIRONMENT=production
   SECRET_KEY=generate-a-strong-random-string-here
   CORS_ORIGINS=https://agentnest-XXXXX.vercel.app,https://agentnest.io
   ```
   - Replace `agentnest-XXXXX.vercel.app` with your actual Vercel URL

5. **Deploy**
   - Railway auto-deploys when you push to main
   - Your backend URL will be shown in Railway dashboard
   - Example: `https://agentnest-api-production.railway.app`

---

## Update Vercel Environment Variables

After backend is deployed:

1. Go to Vercel project settings
2. Update `REACT_APP_API_URL` to your Railway backend URL
3. Redeploy (it should auto-redeploy when env vars change)

---

## Update Landing Page

Once both are deployed:

Edit `landing/index.html` and replace all:
- `https://app.agentnest.io/login` → `https://agentnest-XXXXX.vercel.app/login`
- `https://app.agentnest.io/signup` → `https://agentnest-XXXXX.vercel.app/signup`

Then redeploy landing page to Vercel.

---

## Test Deployment

1. Visit: `https://agentnest-XXXXX.vercel.app`
2. Click "Get Started" → should go to `/signup`
3. Try signing up → should connect to backend
4. Check backend logs in Railway for any errors

---

## Troubleshooting

### 404 on /signup
- [ ] Vercel project root is set to `frontend` directory
- [ ] `vercel.json` exists with correct routing rules
- [ ] Build completed successfully

### API connection errors
- [ ] `REACT_APP_API_URL` is set correctly
- [ ] Backend `CORS_ORIGINS` includes your frontend URL
- [ ] Backend service is running (check Railway logs)

### Database errors
- [ ] PostgreSQL plugin is added in Railway
- [ ] `DATABASE_URL` is automatically set by Railway
- [ ] Backend service dependencies exist

---

## Next Steps

After deployment:
- [ ] Set up custom domain pointing to Vercel frontend
- [ ] Configure email service for notifications
- [ ] Set up monitoring/error tracking
- [ ] Enable analytics on frontend
- [ ] Configure automated backups for PostgreSQL
