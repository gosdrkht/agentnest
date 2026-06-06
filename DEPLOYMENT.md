# AgentNest Deployment Guide

This guide covers deploying the frontend to Vercel and backend to Railway.

## Frontend Deployment (Vercel)

### Prerequisites
- Vercel account (free at https://vercel.com)
- GitHub account with access to this repository

### Steps

1. **Connect Repository to Vercel**
   - Go to https://vercel.com/new
   - Import your GitHub repository (gosdrkht/agentnest)
   - Select `frontend` as the root directory
   - Click "Deploy"

2. **Set Environment Variables**
   - In Vercel project settings → Environment Variables
   - Add: `REACT_APP_API_URL` = `https://agentnest-api.railway.app` (update with your actual backend URL)

3. **Build Settings**
   - Build Command: `npm run build`
   - Output Directory: `build`
   - Install Command: `npm install`

4. **Deploy**
   - Vercel will automatically deploy when you push to main branch
   - Your frontend URL will be something like: `https://agentnest.vercel.app`

---

## Backend Deployment (Railway)

### Prerequisites
- Railway account (free at https://railway.app)
- GitHub account with access to this repository

### Steps

1. **Create New Project on Railway**
   - Go to https://railway.app
   - Click "New Project" → "Deploy from GitHub"
   - Select your repository

2. **Configure Backend Service**
   - Select `backend` directory as the root
   - Choose Python as the runtime
   - Railway will detect `requirements.txt`

3. **Set Environment Variables**
   - In Railway project settings, add these variables:
   ```
   ENVIRONMENT=production
   DATABASE_URL=postgresql://user:password@host:port/dbname
   REDIS_URL=redis://host:port/0
   SECRET_KEY=your-secret-key-here-change-this
   CORS_ORIGINS=https://agentnest.vercel.app,https://agentnest.io
   API_HOST=0.0.0.0
   API_PORT=8000
   ```

4. **Add Database (PostgreSQL)**
   - In Railway project, click "Add Plugin"
   - Select "PostgreSQL"
   - Railway will automatically set `DATABASE_URL`
   - Use the generated credentials

5. **Add Redis (Optional but recommended)**
   - In Railway project, click "Add Plugin"
   - Select "Redis"
   - Railway will automatically set `REDIS_URL`

6. **Deployment**
   - Push code to main branch
   - Railway automatically deploys
   - Your backend URL will be shown in Railway dashboard (e.g., `https://agentnest-api.railway.app`)

---

## Update Landing Page

After deployment, update `landing/index.html` to point to your deployed frontend:

```html
<!-- Replace in landing/index.html -->
<a href="https://agentnest.vercel.app/login" class="btn btn-outline">Login</a>
<a href="https://agentnest.vercel.app/signup" class="btn btn-primary">Get Started</a>
```

And update backend CORS origins to include your frontend URL.

---

## Troubleshooting

### Frontend 404 on `/signup`
- Ensure `vercel.json` is configured correctly
- Check that `REACT_APP_API_URL` environment variable is set
- Verify backend URL is accessible

### API calls failing
- Check CORS settings in backend `main.py`
- Verify `CORS_ORIGINS` includes your frontend URL
- Check backend logs for errors

### Database connection errors
- Verify `DATABASE_URL` is correct
- Ensure PostgreSQL service is running (Railway plugin)
- Check credentials in environment variables

---

## Local Development

To run locally with Docker:

```bash
docker-compose up
```

Then:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Production Checklist

- [ ] Update `SECRET_KEY` in backend (use strong random string)
- [ ] Set `ENVIRONMENT=production` in backend
- [ ] Enable HTTPS on custom domains
- [ ] Set up proper database backups
- [ ] Configure monitoring/logging
- [ ] Update API documentation with production URL
- [ ] Test authentication flow end-to-end
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Configure rate limiting on backend
