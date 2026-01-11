# 🚀 Showcase Deployment Guide (FREE)

Deploy your Crime Safety Platform for **FREE** to share with recruiters, professors, or in your portfolio!

---

## Option 1: Render + Vercel (Recommended - Easiest)

### ⚡ Deploy Backend to Render (5 minutes)

1. **Create Render Account**: https://render.com (Sign up with GitHub)

2. **Push Code to GitHub**:
```powershell
cd e:\nikhil\crime-safety-platform
git init
git add .
git commit -m "Initial commit - Crime Safety Platform"
gh repo create crime-safety-platform --public --source=. --push
# OR manually create repo on GitHub and push
```

3. **Deploy on Render**:
   - Go to https://dashboard.render.com
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repo
   - Settings:
     - **Name**: `crime-safety-backend`
     - **Runtime**: `Python 3`
     - **Build Command**: `pip install -r backend/requirements.txt`
     - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - **Plan**: `Free`
   - Click **"Create Web Service"**

4. **Add Database**:
   - In your service dashboard, go to **"Environment"**
   - Click **"Add Database"** → **PostgreSQL**
   - Free tier: 512MB storage
   - Copy the `DATABASE_URL` environment variable

5. **Your backend is live!** 🎉
   - URL: `https://crime-safety-backend.onrender.com`
   - API Docs: `https://crime-safety-backend.onrender.com/docs`

---

### ⚡ Deploy Frontend to Vercel (3 minutes)

1. **Create Vercel Account**: https://vercel.com (Sign up with GitHub)

2. **Update API URL** in frontend:
```powershell
# Edit frontend/.env
echo "REACT_APP_API_URL=https://crime-safety-backend.onrender.com" > frontend\.env.production
```

3. **Deploy on Vercel**:
   - Go to https://vercel.com/new
   - Import your GitHub repo
   - Settings:
     - **Framework Preset**: `Create React App`
     - **Root Directory**: `frontend`
     - **Build Command**: `npm run build`
     - **Output Directory**: `build`
   - Click **"Deploy"**

4. **Your frontend is live!** 🎉
   - URL: `https://crime-safety-platform.vercel.app`

---

## Option 2: Railway (All-in-One - Even Easier!)

### ⚡ Deploy Everything to Railway (2 minutes)

1. **Create Railway Account**: https://railway.app (Sign up with GitHub)

2. **Deploy**:
   - Click **"New Project"** → **"Deploy from GitHub repo"**
   - Select your repo
   - Railway auto-detects backend and frontend
   - Adds PostgreSQL automatically
   - Gives you 2 URLs (backend + frontend)

3. **Free Tier**: $5 credit/month (enough for showcase)

---

## Option 3: Netlify (Frontend) + Render (Backend)

### Frontend → Netlify:
1. Go to https://netlify.com
2. Drag & drop `frontend/build` folder
3. Done! Live URL instantly

### Backend → Same as Option 1 (Render)

---

## 🎯 Best for Your Use Case

**For Portfolio/Resume**:
- ✅ **Vercel (Frontend)** + **Render (Backend)**
- Professional URLs
- Auto-deploy on GitHub push
- Always free

**For Quick Demo**:
- ✅ **Railway** - Easiest setup
- One platform for everything
- $5/month credit (renews monthly)

**For Interview Presentation**:
- ✅ **Render** - Most reliable free tier
- Won't sleep during demo
- Can upgrade easily if needed

---

## 📝 Update Frontend API URL

Before deploying frontend, update the API endpoint:

**frontend/src/services/api.js**:
```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

**frontend/.env.production**:
```
REACT_APP_API_URL=https://your-backend-url.onrender.com
```

---

## 🔧 Troubleshooting

### Backend sleeping on Render free tier?
- Expected behavior - wakes in 30 seconds
- Solution: Use [UptimeRobot](https://uptimerobot.com/) to ping every 5 minutes (keeps it awake)

### CORS errors?
- Update `backend/app/main.py` CORS origins:
```python
origins = [
    "http://localhost:3000",
    "https://crime-safety-platform.vercel.app",  # Add your Vercel URL
    "https://*.vercel.app",  # All Vercel preview URLs
]
```

### Database not loading?
- Run data ingestion after deploy:
```bash
# In Render shell (Console tab)
python backend/scripts/ingest_data.py
```

---

## 💼 Add to Portfolio

Once deployed, add these to your resume/portfolio:

- **Live Demo**: https://crime-safety-platform.vercel.app
- **API Docs**: https://crime-safety-backend.onrender.com/docs
- **GitHub**: https://github.com/yourusername/crime-safety-platform
- **Tech Stack**: React, FastAPI, PostgreSQL, ML (ARIMA), NLP (DistilBERT)

---

## 📊 Features to Highlight

✅ Real-time crime map with WebSocket updates  
✅ ARIMA-based crime predictions (ML)  
✅ NLP sentiment analysis  
✅ Safe route planning algorithm  
✅ Interactive chatbot  
✅ Community alert system  
✅ Responsive design  

---

## 🎓 Cost Breakdown

| Service | Free Tier | Perfect For |
|---------|-----------|-------------|
| Render | 750 hours/month | Backend API |
| Vercel | Unlimited | Frontend hosting |
| PostgreSQL (Render) | 512MB | Database |
| **Total** | **$0/month** | Showcase project |

**Railway Alternative**: $5 credit/month (use ~$2-3 for showcase)

---

## 🚀 Quick Start Commands

```powershell
# 1. Initialize Git
cd e:\nikhil\crime-safety-platform
git init
git add .
git commit -m "Crime Safety Platform - Ready for deployment"

# 2. Create GitHub repo
gh repo create crime-safety-platform --public --source=. --push

# 3. Go to Render.com → Deploy from GitHub
# 4. Go to Vercel.com → Import GitHub repo
# 5. Done! Share your live URLs
```

---

**Need help?** Each platform has excellent documentation:
- Render: https://render.com/docs
- Vercel: https://vercel.com/docs
- Railway: https://docs.railway.app

**Total Time**: 10-15 minutes from start to live! 🎉
