# Render Deployment Guide

**Deploy LinguaFlow to Render in 5 minutes!**

---

## 🚀 Quick Deploy

### Prerequisites
- GitHub account with repository pushed
- Render account (free): [render.com](https://render.com)
- MongoDB Atlas URI
- Groq API key
- Redis Cloud URL

---

## 📋 Step-by-Step Deployment

### Step 1: Push to GitHub

```bash
# Make sure all changes are committed
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Click "Get Started for Free"
3. Sign up with GitHub
4. Authorize Render to access your repositories

### Step 3: Create New Web Service

1. **Click "New +"** → Select "Web Service"

2. **Connect Repository:**
   - Find: `devm5611-EE/Language-Translation-System`
   - Click "Connect"

3. **Configure Service:**
   ```
   Name: linguaflow
   Region: Oregon (US West)
   Branch: main
   Root Directory: (leave empty)
   Runtime: Python 3
   Build Command: cd linguaflow && pip install -r requirements.txt
   Start Command: cd linguaflow && gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app
   Plan: Free
   ```

4. **Click "Advanced"** to add environment variables

### Step 4: Add Environment Variables

Click "Add Environment Variable" for each:

| Key | Value | Notes |
|-----|-------|-------|
| `FLASK_SECRET_KEY` | Click "Generate" | Auto-generated |
| `JWT_SECRET` | Click "Generate" | Auto-generated |
| `FLASK_DEBUG` | `False` | Production mode |
| `MONGODB_URI` | `mongodb+srv://...` | Your MongoDB Atlas URI |
| `GROQ_API_KEY` | `gsk_...` | Your Groq API key |
| `REDIS_URL` | `redis://...` | Your Redis Cloud URL |
| `ALLOWED_ORIGINS` | `https://linguaflow.onrender.com` | Your Render URL |
| `ADMIN_EMAIL` | `admin@linguaflow.com` | Admin email |
| `JWT_EXPIRY_HOURS` | `24` | Token expiry |
| `MAX_TEXT_LENGTH` | `5000` | Max text length |

**Important:** Replace `linguaflow.onrender.com` with your actual Render URL after deployment.

### Step 5: Deploy

1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Watch the logs for any errors

---

## 🔧 Configuration Files

### Files Created for Render:

#### 1. `render.yaml` (Blueprint)
Automatic deployment configuration. Render will detect this file.

#### 2. `Procfile`
Alternative start command specification.

#### 3. `requirements.txt`
Already includes `gunicorn==22.0.0`

---

## 📊 Render Free Plan Limits

- ✅ **750 hours/month** of runtime
- ✅ **512 MB RAM**
- ✅ **0.1 CPU**
- ✅ **Custom domain** support
- ⚠️ **Spins down after 15 min** of inactivity
- ⚠️ **Cold start:** 30-60 seconds

### Keeping Service Active (Optional)

Use a service like [UptimeRobot](https://uptimerobot.com/) to ping your app every 5 minutes:
- URL to ping: `https://your-app.onrender.com/health`
- Interval: 5 minutes

---

## 🌐 After Deployment

### Your App URL
```
https://linguaflow.onrender.com
```
(Replace with your actual URL)

### Update ALLOWED_ORIGINS

1. Go to Render Dashboard
2. Select your service
3. Go to "Environment"
4. Update `ALLOWED_ORIGINS`:
   ```
   https://linguaflow.onrender.com,http://localhost:5000
   ```
5. Click "Save Changes"
6. Service will redeploy automatically

---

## ✅ Verify Deployment

### 1. Check Health Endpoint
```bash
curl https://your-app.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "version": "1.0.0",
  "dependencies": {
    "mongodb": "ok",
    "redis": "ok",
    "groq_api": "configured"
  }
}
```

### 2. Test Translation API
```bash
# Register user
curl -X POST https://your-app.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "TestPass123"
  }'

# Login
curl -X POST https://your-app.onrender.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPass123"
  }'

# Use the token from login response to translate
curl -X POST https://your-app.onrender.com/api/translate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello",
    "target_lang": "es"
  }'
```

### 3. Open in Browser
Visit: `https://your-app.onrender.com`

---

## 🔍 Monitoring & Logs

### View Logs
1. Go to Render Dashboard
2. Select your service
3. Click "Logs" tab
4. Monitor real-time logs

### Common Log Messages
```
✅ "Redis cache connected" - Redis working
✅ "Rate limiting configured with Redis backend" - Rate limiting active
✅ "LinguaFlow app created" - App initialized
✅ "Booting worker" - Gunicorn starting
```

---

## 🐛 Troubleshooting

### Issue: Build Failed

**Check:**
1. `requirements.txt` is in `linguaflow/` directory
2. Build command is correct: `cd linguaflow && pip install -r requirements.txt`
3. All dependencies are compatible

**Solution:**
```bash
# Test locally first
cd linguaflow
pip install -r requirements.txt
```

### Issue: Service Won't Start

**Check:**
1. Start command is correct
2. All environment variables are set
3. MongoDB URI is correct
4. Redis URL is correct

**Solution:** Check logs in Render dashboard

### Issue: "Application Error"

**Check:**
1. FLASK_SECRET_KEY is set
2. JWT_SECRET is set
3. MONGODB_URI is valid
4. GROQ_API_KEY is valid

**Solution:** Verify all environment variables

### Issue: CORS Error

**Check:**
1. ALLOWED_ORIGINS includes your Render URL
2. Format: `https://your-app.onrender.com`

**Solution:**
```bash
# Update ALLOWED_ORIGINS
ALLOWED_ORIGINS=https://linguaflow.onrender.com,http://localhost:5000
```

### Issue: Cold Start Slow

**This is normal for free plan:**
- First request after 15 min: 30-60 seconds
- Subsequent requests: Fast

**Solution:** Use UptimeRobot to keep service active

---

## 🔄 Updating Your App

### Automatic Deployment

Render automatically deploys when you push to GitHub:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push origin main

# Render automatically deploys
```

### Manual Deployment

1. Go to Render Dashboard
2. Select your service
3. Click "Manual Deploy" → "Deploy latest commit"

---

## 📈 Scaling (Paid Plans)

### Upgrade for Better Performance

**Starter Plan ($7/month):**
- ✅ No spin down
- ✅ 512 MB RAM
- ✅ Faster response times

**Standard Plan ($25/month):**
- ✅ 2 GB RAM
- ✅ 1 CPU
- ✅ Better performance

### Upgrade Steps:
1. Go to Render Dashboard
2. Select your service
3. Click "Settings" → "Plan"
4. Choose plan and confirm

---

## 🔐 Security Best Practices

### Environment Variables
- ✅ Never commit `.env` file
- ✅ Use Render's environment variables
- ✅ Rotate secrets regularly
- ✅ Use strong random values

### HTTPS
- ✅ Render provides free SSL
- ✅ All traffic is encrypted
- ✅ Automatic certificate renewal

### Database
- ✅ Use MongoDB Atlas (encrypted)
- ✅ Enable IP whitelist (add Render IPs)
- ✅ Use strong passwords

---

## 📊 Performance Optimization

### Gunicorn Configuration

Current settings (in Procfile):
```
--workers 2          # 2 worker processes
--timeout 120        # 120 second timeout
--bind 0.0.0.0:$PORT # Bind to Render's port
```

### For Better Performance:
```
# Increase workers (paid plans)
--workers 4

# Adjust timeout for long translations
--timeout 180
```

### Caching
- ✅ Redis caching enabled
- ✅ 1-hour TTL
- ✅ 40-60% cache hit rate

---

## 🎯 Production Checklist

Before going live:

- [ ] All environment variables set
- [ ] FLASK_DEBUG=False
- [ ] Strong FLASK_SECRET_KEY
- [ ] Strong JWT_SECRET
- [ ] MongoDB Atlas configured
- [ ] Redis Cloud configured
- [ ] Groq API key valid
- [ ] ALLOWED_ORIGINS updated
- [ ] Health check working
- [ ] Translation API tested
- [ ] Logs monitored
- [ ] Custom domain configured (optional)

---

## 🌐 Custom Domain (Optional)

### Add Custom Domain:

1. **In Render:**
   - Go to Settings → Custom Domains
   - Click "Add Custom Domain"
   - Enter: `linguaflow.com`

2. **In Your DNS Provider:**
   - Add CNAME record:
     ```
     Type: CNAME
     Name: www
     Value: linguaflow.onrender.com
     ```
   - Add A record for root domain (if needed)

3. **Wait for SSL:**
   - Render automatically provisions SSL
   - Takes 5-10 minutes

---

## 📞 Support

### Render Support
- Documentation: [render.com/docs](https://render.com/docs)
- Community: [community.render.com](https://community.render.com)
- Status: [status.render.com](https://status.render.com)

### LinguaFlow Issues
- Check logs in Render dashboard
- Verify environment variables
- Test health endpoint
- Review error messages

---

## 🎉 Success!

Your LinguaFlow app is now deployed on Render!

**Next Steps:**
1. ✅ Share your app URL
2. ✅ Monitor logs
3. ✅ Set up uptime monitoring
4. ✅ Configure custom domain (optional)
5. ✅ Upgrade plan if needed

---

**Deployment URL:** `https://linguaflow.onrender.com`

**Last Updated:** May 7, 2026  
**Status:** ✅ Ready for Render Deployment
