# Adriatic Claim Co - Deployment Guide

## Free Hosting Options

### Option 1: Google Cloud Run (Recommended)

- **Backend**: Free tier with 2 million requests/month
- **Frontend**: Cloud Storage + Cloud CDN (5GB storage, 1GB network egress/month)
- **Database**: Cloud SQL PostgreSQL (30GB storage free tier) or use SQLite with persistent volume

**Pros**: Most generous free tier, production-ready, scales automatically  
**Cons**: Requires credit card, more complex setup

### Option 2: Render.com (Easiest)

- **Backend**: Free tier with auto-sleep after 15 min inactivity, 750 hours/month
- **Frontend**: Free static site hosting with global CDN
- **Database**: Free PostgreSQL 90-day trial (then $7/month or use external DB)

**Pros**: Zero config deployment, GitHub integration, free SSL  
**Cons**: Backend sleeps after inactivity (15-30s cold start), limited hours

### Option 3: Railway.app

- **Backend & Frontend**: $5 free credit/month (~500 hours)
- **Database**: Included PostgreSQL with persistent storage

**Pros**: Simple dashboard, no sleep on free tier  
**Cons**: Credit runs out quickly with 24/7 uptime

---

## Deployment Instructions

### Prerequisites

1. **Backend**: Push code to GitHub repository
2. **Frontend**: Update `.env.production` with your backend URL after deployment
3. **Database**: Create PostgreSQL database on hosting platform (or use external like ElephantSQL)

---

## Option A: Deploy to Render.com (Recommended for Beginners)

### Backend Deployment

1. **Create Render Account**: Go to [render.com](https://render.com) and sign up with GitHub

2. **Create Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `Adriatic-Claim-Co`
   - Select the repository

3. **Configure Service**:
   - **Name**: `adriatic-backend` (or your choice)
   - **Region**: Choose closest to your location
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

4. **Add Environment Variables**:
   - Click "Environment" tab
   - Add these variables:
     ```
     DATABASE_URL=(provided by Render PostgreSQL or external DB)
     FLASK_ENV=production
     SECRET_KEY=your_random_secret_key_here_replace_this
     PORT=10000
     ```
   - Generate SECRET_KEY with: `python -c 'import secrets; print(secrets.token_hex(32))'`

5. **Create PostgreSQL Database** (Optional - skip if using SQLite):
   - Click "New +" → "PostgreSQL"
   - Name: `adriatic-db`
   - Copy the "Internal Database URL"
   - Paste it as `DATABASE_URL` in backend environment variables

6. **Deploy**: Click "Create Web Service" - wait 5-10 minutes for build

7. **Note Your Backend URL**: Copy the URL (e.g., `https://adriatic-backend.onrender.com`)

### Frontend Deployment

1. **Update Environment Variable Locally**:
   - Open `frontend/.env.production`
   - Replace with your backend URL:
     ```
     REACT_APP_API_URL=https://adriatic-backend.onrender.com
     ```
   - Commit and push: `git add . && git commit -m "Update production API URL" && git push`

2. **Create Static Site on Render**:
   - Click "New +" → "Static Site"
   - Connect same GitHub repository
   - **Name**: `adriatic-frontend`
   - **Branch**: `main`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install --legacy-peer-deps && npm run build`
   - **Publish Directory**: `build`

3. **Deploy**: Click "Create Static Site" - wait 5-10 minutes

4. **Access Your App**: Use the frontend URL (e.g., `https://adriatic-frontend.onrender.com`)

---

## Option B: Deploy to Google Cloud Run

### Backend Deployment

1. **Install Google Cloud CLI**:

   ```bash
   # macOS
   brew install --cask google-cloud-sdk

   # Or download from: https://cloud.google.com/sdk/docs/install
   ```

2. **Initialize and Login**:

   ```bash
   gcloud init
   gcloud auth login
   ```

3. **Create Project** (if needed):

   ```bash
   gcloud projects create adriatic-claims --name="Adriatic Claim Co"
   gcloud config set project adriatic-claims
   ```

4. **Enable Required APIs**:

   ```bash
   gcloud services enable run.googleapis.com
   gcloud services enable sqladmin.googleapis.com
   gcloud services enable cloudbuild.googleapis.com
   ```

5. **Create PostgreSQL Database** (Optional):

   ```bash
   gcloud sql instances create adriatic-db \
     --database-version=POSTGRES_14 \
     --tier=db-f1-micro \
     --region=us-central1

   gcloud sql databases create adriatic_claims --instance=adriatic-db
   gcloud sql users set-password postgres --instance=adriatic-db --password=YOUR_PASSWORD
   ```

6. **Build and Deploy Backend**:

   ```bash
   cd backend

   # Build container
   gcloud builds submit --tag gcr.io/adriatic-claims/backend

   # Deploy to Cloud Run
   gcloud run deploy adriatic-backend \
     --image gcr.io/adriatic-claims/backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars "FLASK_ENV=production,SECRET_KEY=your_secret_key_here"
   ```

7. **Note the Backend URL** shown in the output

### Frontend Deployment

1. **Build Frontend Locally**:

   ```bash
   cd ../frontend

   # Update .env.production with Cloud Run backend URL
   echo "REACT_APP_API_URL=https://adriatic-backend-xxxxx-uc.a.run.app" > .env.production

   # Build
   npm install --legacy-peer-deps
   npm run build
   ```

2. **Deploy to Cloud Storage**:

   ```bash
   # Create bucket
   gsutil mb gs://adriatic-claims-frontend

   # Upload files
   gsutil -m cp -r build/* gs://adriatic-claims-frontend/

   # Make public
   gsutil iam ch allUsers:objectViewer gs://adriatic-claims-frontend

   # Set index/error pages
   gsutil web set -m index.html -e index.html gs://adriatic-claims-frontend
   ```

3. **Access at**: `https://storage.googleapis.com/adriatic-claims-frontend/index.html`

---

## Option C: Deploy to Railway.app

### One-Click Deploy

1. **Create Railway Account**: Go to [railway.app](https://railway.app)

2. **Deploy Backend**:
   - Click "New Project" → "Deploy from GitHub repo"
   - Select `Adriatic-Claim-Co` repository
   - Railway auto-detects Python and deploys
   - Add environment variables in Settings:
     ```
     FLASK_ENV=production
     SECRET_KEY=your_secret_key
     ```

3. **Add PostgreSQL**:
   - Click "+ New" → "Database" → "Add PostgreSQL"
   - Railway automatically connects DATABASE_URL

4. **Deploy Frontend**:
   - Add new service from same repo
   - Railway detects Node.js
   - Set build command: `npm install --legacy-peer-deps && npm run build`
   - Set start command: `npx serve -s build -l $PORT`
   - Update `.env.production` with backend Railway URL

---

## Environment Variables Reference

### Backend (.env)

```bash
# Database - auto-provided by Render/Railway, or use external
DATABASE_URL=postgresql://user:password@host:5432/database
# Or for SQLite (development/testing)
# DATABASE_URL=sqlite:///instance/adriatic.db

# Flask configuration
FLASK_ENV=production
SECRET_KEY=your_random_secret_key_generate_with_secrets_module

# Port (auto-set by most platforms)
PORT=5000
```

### Frontend (.env.production)

```bash
# Backend API URL - update after backend deployment
REACT_APP_API_URL=https://your-backend-url.onrender.com
# or
# REACT_APP_API_URL=https://your-backend-url.run.app
# or
# REACT_APP_API_URL=https://your-backend.railway.app
```

---

## Testing Deployment

### Backend Health Check

```bash
curl https://your-backend-url.onrender.com/health
# Should return: {"status": "healthy"}

curl https://your-backend-url.onrender.com/
# Should return: {"message": "Adriatic Claim Co API", "version": "1.0"}
```

### Frontend API Connection

1. Open your frontend URL in browser
2. Open Developer Tools → Console
3. Fill out the Owner Claim Intake form
4. Submit and check for success message
5. Verify in Network tab that API calls reach backend

---

## Troubleshooting

### Backend Issues

**502 Bad Gateway / App won't start**:

- Check logs in hosting dashboard
- Verify `requirements.txt` has all dependencies
- Ensure `Procfile` command is correct: `web: gunicorn app:app`
- Check DATABASE_URL format (should be `postgresql://`, not `postgres://`)

**Database connection errors**:

- Verify DATABASE_URL is set correctly
- For Render: Use "Internal Database URL" from PostgreSQL dashboard
- Check database is in same region as backend

**CORS errors**:

- Verify frontend URL is in `CORS(app, origins=[...])` in `app.py`
- Add your frontend domain to allowed origins

### Frontend Issues

**Can't connect to backend**:

- Check `.env.production` has correct `REACT_APP_API_URL`
- Ensure backend URL doesn't have trailing slash
- Verify backend is running and accessible

**Blank page after deployment**:

- Check browser console for errors
- Verify build completed successfully
- Check `public/index.html` exists

**Environment variables not working**:

- Ensure variables start with `REACT_APP_`
- Rebuild after changing `.env.production`
- Variables are embedded at build time, not runtime

---

## Cost Optimization

### Stay Within Free Tiers

**Render.com**:

- Backend sleeps after 15 min inactivity (acceptable for low-traffic apps)
- Use external free PostgreSQL (ElephantSQL, Supabase) after 90-day trial
- Static frontend is always free

**Google Cloud**:

- Cloud Run: 2M requests/month free
- Cloud Storage: 5GB storage free
- Use Cloud SQL free tier or SQLite with persistent disk

**Railway**:

- $5 credit = ~500 hours of uptime
- Good for low-traffic or development staging

### External Free Databases

If hosting database becomes expensive:

- **ElephantSQL**: 20MB PostgreSQL free forever
- **Supabase**: 500MB PostgreSQL + API + auth free
- **PlanetScale**: 5GB MySQL free tier

Update `DATABASE_URL` environment variable with external database connection string.

---

## Next Steps

After successful deployment:

1. ✅ **Test all form functionality**
2. ✅ **Set up custom domain** (optional, Render/Railway support this)
3. ✅ **Enable HTTPS** (automatic on all platforms)
4. ✅ **Configure monitoring** (use platform dashboards)
5. ⬜ **Set up CI/CD** (auto-deploy on git push - see below)
6. ⬜ **Add authentication** (JWT tokens, OAuth)
7. ⬜ **Implement file uploads** (claims documentation)

---

## Continuous Deployment (Auto-Deploy on Git Push)

### Render.com

- ✅ Already enabled by default
- Every push to `main` branch automatically deploys

### Google Cloud Run

Add to `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Cloud SDK
        uses: google-github-actions/setup-gcloud@v0
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: adriatic-claims

      - name: Build and Deploy
        run: |
          cd backend
          gcloud builds submit --tag gcr.io/adriatic-claims/backend
          gcloud run deploy adriatic-backend --image gcr.io/adriatic-claims/backend
```

### Railway

- ✅ Auto-deploy enabled by default on git push

---

## Support

If you encounter issues:

1. Check platform-specific documentation:
   - Render: https://render.com/docs
   - Google Cloud: https://cloud.google.com/run/docs
   - Railway: https://docs.railway.app

2. Review application logs in platform dashboard

3. Test locally first:

   ```bash
   # Backend
   cd backend
   python app.py

   # Frontend
   cd frontend
   npm start
   ```
