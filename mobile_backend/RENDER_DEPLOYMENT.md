# Deploying Mobile Backend to Render

## 🚀 Quick Deployment Guide

### Prerequisites
- GitHub account with this repository pushed
- Render account (free tier available at https://render.com)
- Supabase database already configured

---

## Step-by-Step Deployment

### 1. Prepare Your Repository

**Ensure these files exist in `/mobile_backend`:**
- ✅ `main.py` - Main FastAPI application
- ✅ `requirements.txt` - Python dependencies
- ✅ `runtime.txt` - Python version (optional)
- ✅ `render.yaml` - Render configuration (optional)

**Check requirements.txt includes:**
```txt
fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
pydantic
python-multipart
```

### 2. Push to GitHub

```bash
cd /Users/dakshrathore/Desktop/Code_on_track
git add .
git commit -m "Prepare mobile backend for Render deployment"
git push origin daksh
```

### 3. Create New Web Service on Render

1. **Go to Render Dashboard**
   - Visit: https://dashboard.render.com
   - Click "New +" → "Web Service"

2. **Connect Repository**
   - Select "Connect a repository"
   - Authorize GitHub if needed
   - Choose repository: `DEMACARTI/Code_on_track`
   - Click "Connect"

3. **Configure Service**

   **Basic Settings:**
   - **Name:** `railchinh-mobile-backend` (or your choice)
   - **Region:** Select closest to your users
   - **Branch:** `daksh`
   - **Root Directory:** `mobile_backend`
   - **Runtime:** `Python 3`

   **Build & Deploy:**
   - **Build Command:** 
     ```bash
     pip install -r requirements.txt
     ```
   
   - **Start Command:**
     ```bash
     uvicorn main:app --host 0.0.0.0 --port $PORT
     ```

   **Instance Type:**
   - Select `Free` (or paid tier for better performance)

4. **Environment Variables**

   Click "Advanced" → "Add Environment Variable"

   **Required Variables:**
   ```
   DATABASE_URL=postgresql://postgres.aktfgilmfoprdkwkzybd:Alqawwiy%40123@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres
   PYTHON_VERSION=3.11.0
   ```

   **Optional Variables:**
   ```
   PORT=10000
   WORKERS=4
   LOG_LEVEL=info
   ```

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy
   - Wait 2-5 minutes for deployment to complete

### 4. Verify Deployment

Once deployed, you'll get a URL like:
```
https://railchinh-mobile-backend.onrender.com
```

**Test endpoints:**
- Health Check: `https://your-app.onrender.com/health`
- API Docs: `https://your-app.onrender.com/docs`
- Root: `https://your-app.onrender.com/`

---

## 📝 Configuration Files

### Create `runtime.txt` (Optional)
```txt
python-3.11.0
```

### Create `render.yaml` (Recommended)
```yaml
services:
  - type: web
    name: railchinh-mobile-backend
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        value: postgresql://postgres.aktfgilmfoprdkwkzybd:Alqawwiy%40123@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres
      - key: PYTHON_VERSION
        value: 3.11.0
    plan: free
    region: oregon
    rootDir: mobile_backend
```

### Update `requirements.txt`
```txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
pydantic==2.5.3
python-multipart==0.0.6
```

---

## 🔧 Advanced Configuration

### Custom Domain (Optional)
1. Go to your service settings
2. Click "Custom Domain"
3. Add your domain: `api.yourdomain.com`
4. Configure DNS records as instructed

### Health Checks
Render automatically pings: `GET /` or `GET /health`

If you want custom health check path, add to `main.py`:
```python
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }
```

### Logs
View logs in Render dashboard:
1. Go to your service
2. Click "Logs" tab
3. See real-time logs

### Scaling
**Free Tier Limitations:**
- Sleeps after 15 minutes of inactivity
- 750 hours/month free
- 512 MB RAM

**Upgrade Options:**
- Starter: $7/month (512 MB RAM, no sleep)
- Standard: $25/month (2 GB RAM)
- Pro: $85/month (4 GB RAM)

---

## 🔒 Security Best Practices

### 1. Use Environment Variables
Never commit sensitive data. Store in Render environment variables:
- Database passwords
- API keys
- Secret keys

### 2. Enable HTTPS
Render automatically provides free SSL certificates.

### 3. CORS Configuration
Update `main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-flutter-app.com",
        "https://your-website.com"
    ],  # Update with your actual domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Rate Limiting
Consider adding rate limiting for production:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

---

## 🐛 Troubleshooting

### Deployment Failed
**Check build logs:**
1. Go to service dashboard
2. Click "Logs"
3. Look for errors in build phase

**Common issues:**
- Missing dependencies in `requirements.txt`
- Wrong Python version
- Database connection issues

### App Crashes on Start
**Check runtime logs:**
```bash
# In Render logs, look for:
ModuleNotFoundError
ImportError
Database connection errors
```

**Solutions:**
- Verify all dependencies installed
- Check DATABASE_URL is correct
- Ensure PORT environment variable used

### Database Connection Timeout
**Update connection string:**
Use Supabase **Session Pooler** for better connection handling:
```
postgresql://postgres.xxx:password@xxx.pooler.supabase.com:6543/postgres
```

Not the direct connection (port 5432).

### Cold Starts (Free Tier)
Free tier sleeps after 15 minutes. First request after sleep takes 30-60 seconds.

**Solutions:**
1. Upgrade to paid tier (no sleep)
2. Use a ping service (e.g., UptimeRobot)
3. Accept the cold start delay

---

## 📱 Update Flutter App

Once deployed, update your Flutter app's API base URL:

```dart
// In your Flutter app
const String API_BASE_URL = 'https://railchinh-mobile-backend.onrender.com';
```

---

## 🔄 CI/CD (Automatic Deployments)

Render automatically deploys when you push to your branch:

```bash
git add .
git commit -m "Update mobile backend"
git push origin daksh
```

Render will:
1. Detect changes
2. Build automatically
3. Deploy new version
4. Zero-downtime deployment

---

## 📊 Monitoring

### View Metrics
Render dashboard shows:
- CPU usage
- Memory usage
- Request count
- Response times
- Error rates

### Alerts
Set up email alerts for:
- Service down
- High error rate
- High memory usage

---

## 💰 Cost Estimation

**Free Tier:**
- 750 hours/month free
- Good for development/testing
- Sleeps after inactivity

**Paid Tiers:**
- **Starter ($7/mo):** No sleep, better for production
- **Standard ($25/mo):** More resources, better performance
- **Pro ($85/mo):** Production-grade, scaling

---

## 🆘 Support Resources

- **Render Docs:** https://render.com/docs
- **Render Status:** https://status.render.com
- **Support:** support@render.com
- **Community:** https://community.render.com

---

## ✅ Deployment Checklist

Before going to production:

- [ ] All sensitive data in environment variables
- [ ] CORS configured for production domains
- [ ] Health check endpoint working
- [ ] Database connection tested
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] API documentation updated
- [ ] Load testing completed
- [ ] Backup strategy in place
- [ ] Monitoring set up
- [ ] SSL certificate active
- [ ] Custom domain configured (if needed)

---

## 🚀 Quick Commands Reference

```bash
# Push to GitHub
git add .
git commit -m "Deploy update"
git push origin daksh

# Local test before deploy
cd mobile_backend
uvicorn main:app --reload --host 0.0.0.0 --port 8080

# Test deployed API
curl https://your-app.onrender.com/health
curl https://your-app.onrender.com/docs
```

---

## 📝 Post-Deployment

1. **Update mobile app** with new API URL
2. **Test all endpoints** in production
3. **Monitor logs** for first few hours
4. **Set up alerts** for critical issues
5. **Document** the deployed URL
6. **Update** LOGIN_CREDENTIALS.md with production URL

---

**Deployed URL Example:**
```
Production API: https://railchinh-mobile-backend.onrender.com
API Docs: https://railchinh-mobile-backend.onrender.com/docs
Health: https://railchinh-mobile-backend.onrender.com/health
```

Update your mobile app to use this URL instead of `localhost:8080`!
