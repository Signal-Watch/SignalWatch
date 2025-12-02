# 🚀 SignalWatch Deployment Guide

## 📋 Overview
- **Backend**: Render.com (Python Flask API)
- **Frontend**: Your Domain Hosting (Static Files)
- **Repository**: https://github.com/Signal-Watch/SignalWatchUK-Private.git

---

## Part 1: Push to GitHub

### 1. Initialize Git (if not already done)
```powershell
cd D:\signalwatch
git init
git remote add origin https://github.com/Signal-Watch/SignalWatchUK-Private.git
```

### 2. Commit and Push
```powershell
# Check what's being committed (.env should NOT appear)
git status

# Stage all files
git add .

# Commit
git commit -m "Initial commit - SignalWatch backend ready for deployment"

# Push to GitHub
git push -u origin main
```

### ✅ Verify: Check GitHub repo - `.env` should NOT be visible (it's in .gitignore)

---

## Part 2: Deploy Backend to Render

### 1. Connect GitHub to Render
1. Go to https://dashboard.render.com/
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account
4. Select repository: `Signal-Watch/SignalWatchUK-Private`
5. Click **"Connect"**

### 2. Configure Render Service
**Settings:**
- **Name**: `signalwatch-backend` (or any name)
- **Region**: Oregon (closest to UK) or Frankfurt
- **Branch**: `main`
- **Root Directory**: Leave blank (uses repo root)
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
- **Plan**: Free (or paid for better performance)

### 3. Add Environment Variables in Render Dashboard
Go to **Environment** tab and add:

**Required:**
```
GITHUB_TOKEN = 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
```

**Optional (users will provide via UI):**
```
FLASK_SECRET_KEY = <generate random string>
FLASK_DEBUG = False
FLASK_HOST = 0.0.0.0
FLASK_PORT = 10000
```

**Do NOT add these (users provide their own):**
- ❌ COMPANIES_HOUSE_API_KEY
- ❌ XAI_API_KEY

### 4. Deploy
- Click **"Create Web Service"**
- Wait 5-10 minutes for build
- You'll get a URL like: `https://signalwatch-backend.onrender.com`

### ✅ Test Backend
Open: `https://signalwatch-backend.onrender.com/`
Should see the scan form.

---

## Part 3: Create Frontend Dist Folder for Your Hosting

### What Goes in Dist Folder?
Your domain hosting needs ONLY the frontend (HTML/CSS/JS) that points to Render backend API.

### Option A: Use Render as Full Stack (Easiest)
Just use the Render URL directly:
- `https://signalwatch-backend.onrender.com` → This serves both frontend AND backend
- Point your domain DNS to Render
- Done! ✅

### Option B: Separate Frontend on Your Hosting (Custom Domain)

#### 1. Create Dist Folder
```powershell
# Create dist folder
New-Item -ItemType Directory -Path "D:\signalwatch\dist"

# Copy frontend files
Copy-Item -Path "D:\signalwatch\templates" -Destination "D:\signalwatch\dist\templates" -Recurse
Copy-Item -Path "D:\signalwatch\static" -Destination "D:\signalwatch\dist\static" -Recurse
```

#### 2. Update API Endpoints in Frontend
You need to change all `/api/scan` calls to point to Render:

**File**: `dist/static/js/main.js`
```javascript
// Change this:
const API_BASE = '/api';

// To this:
const API_BASE = 'https://signalwatch-backend.onrender.com/api';
```

#### 3. Upload to Your Domain Hosting
1. Login to your hosting cPanel/FTP
2. Upload entire `dist` folder contents to `public_html` or your domain root
3. Set index file to `index.html`

#### 4. Configure CORS on Backend
Since frontend is now on different domain, update `app.py`:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['https://yourdomain.com'])
```

---

## Part 4: Post-Deployment Checklist

### Backend (Render)
- ✅ Service is running (green status)
- ✅ Logs show no errors: `gunicorn` started successfully
- ✅ Test API: `https://your-render-url.onrender.com/api/scan`
- ✅ Environment variables set (GITHUB_TOKEN)
- ✅ Auto-deploy enabled (deploys on git push)

### Frontend (Your Domain)
- ✅ Files uploaded to hosting
- ✅ Domain resolves to correct server
- ✅ SSL certificate active (HTTPS)
- ✅ API calls reach Render backend
- ✅ Test full scan workflow

### Security
- ✅ No `.env` file on GitHub
- ✅ No API keys in code
- ✅ Users must provide their own Companies House key
- ✅ CORS configured correctly
- ✅ Rate limiting working

---

## 🐛 Troubleshooting

### Render Build Fails
**Error**: `ModuleNotFoundError`
- **Fix**: Check `requirements.txt` has all dependencies
- Run locally: `pip install -r requirements.txt`

### CORS Error in Browser
**Error**: `Access-Control-Allow-Origin`
- **Fix**: Add `flask-cors` to requirements.txt
- Update app.py with CORS configuration

### API Calls Not Working
**Error**: 404 on API endpoints
- **Fix**: Check Render URL is correct in frontend
- Verify Render service is running (not sleeping)

### Free Tier Limitations
- Render free tier sleeps after 15 min inactivity
- First request takes 30-60 seconds (cold start)
- **Solution**: Upgrade to paid tier ($7/month) or use cron job to ping every 10 min

---

## 📊 Monitoring

### Render Dashboard
- View logs: Real-time application logs
- Metrics: CPU, Memory, Request count
- Events: Deploy history

### Analytics
- Track scan volume
- Monitor GitHub cache hit rate
- Watch for API errors

---

## 🔄 Update Workflow

### Update Code
```powershell
# Make changes
git add .
git commit -m "Your update message"
git push origin main
```

Render auto-deploys on push! 🚀

### Update Frontend Only
Upload new files to your hosting via FTP/cPanel.

---

## 💡 Recommended Architecture

**Best Setup:**
```
User Browser
    ↓
Your Domain (Frontend)
yourdomain.com
    ↓
Render Backend API
signalwatch.onrender.com
    ↓
Companies House API
(user's own key)
```

**Benefits:**
- Custom domain for branding
- Backend can scale independently
- Easy to update either part separately
- GitHub caching reduces API costs

---

## 🎯 Next Steps

1. ✅ Push to GitHub (now)
2. ✅ Deploy to Render (5 min)
3. ✅ Test backend URL
4. ✅ Create dist folder if needed
5. ✅ Upload to your hosting
6. ✅ Test full workflow
7. ✅ Monitor logs for first few scans

---

**Need Help?**
- Render Docs: https://render.com/docs
- Flask Deployment: https://flask.palletsprojects.com/en/3.0.x/deploying/

**Your Backend Will Be Live At:**
`https://signalwatch-backend.onrender.com`
