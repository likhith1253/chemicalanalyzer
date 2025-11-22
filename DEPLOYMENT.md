# 🚀 Deployment Guide: Chemical Analyzer

Complete guide for deploying the Chemical Analyzer application to production.

**Backend**: Render (Django + PostgreSQL)  
**Frontend**: Vercel (React + Vite)

---

## 📋 Prerequisites

Before deploying, ensure you have:

- [ ] GitHub repository with all code pushed
- [ ] Render account ([render.com](https://render.com))
- [ ] Vercel account ([vercel.com](https://vercel.com))
- [ ] Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

---

## 🔧 Backend Deployment (Render)

### Step 1: Create PostgreSQL Database

1. **Login to Render Dashboard**
2. **Click "New +"** → Select **"PostgreSQL"**
3. **Configure Database**:
   - **Name**: `chemicalanalyzer-db`
   - **Database**: `chemicalanalyzer`
   - **User**: (auto-generated)
   - **Region**: Choose closest to your users
   - **Plan**: Free (or upgrade as needed)
4. **Click "Create Database"**
5. **Copy the Internal Database URL** (starts with `postgresql://`)

### Step 2: Create Web Service

1. **Click "New +"** → Select **"Web Service"**
2. **Connect GitHub Repository**:
   - Authorize Render to access your GitHub
   - Select your `chemicalanalyzer` repository
3. **Configure Web Service**:

   | Setting | Value |
   |---------|-------|
   | **Name** | `chemicalanalyzer-backend` |
   | **Region** | Same as database |
   | **Branch** | `main` (or your default branch) |
   | **Root Directory** | `backend` |
   | **Runtime** | `Python 3` |
   | **Build Command** | `pip install -r requirements.txt` |
   | **Start Command** | `./start.sh` |
   | **Plan** | Free (or upgrade as needed) |

4. **Click "Advanced"** → **Add Environment Variables**:

   | Key | Value | Notes |
   |-----|-------|-------|
   | `SECRET_KEY` | (generate random 50+ chars) | Use: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
   | `DEBUG` | `False` | **CRITICAL**: Must be False in production |
   | `ALLOWED_HOSTS` | `<your-service-name>.onrender.com,localhost` | Replace `<your-service-name>` with actual |
   | `DATABASE_URL` | (paste Internal Database URL from Step 1) | Automatically set if database linked |
   | `CSRF_TRUSTED_ORIGINS` | `https://<your-vercel-app>.vercel.app,https://<your-service-name>.onrender.com` | Update after frontend deployment |
   | `CORS_ALLOWED_ORIGINS` | `https://<your-vercel-app>.vercel.app` | Update after frontend deployment |
   | `GOOGLE_GEMINI_API_KEY` | (your Gemini API key) | Optional but recommended for AI features |

5. **Click "Create Web Service"**

### Step 3: Verify Backend Deployment

1. **Wait for Build to Complete** (5-10 minutes)
2. **Check Logs** for any errors
3. **Visit Your Backend URL**: `https://<your-service-name>.onrender.com`
4. **You should see**: JSON response with available endpoints
5. **Test Admin Panel**: `https://<your-service-name>.onrender.com/admin`

### Step 4: Create Superuser (Optional)

1. **Go to Render Dashboard** → Your Web Service → **Shell**
2. **Run**:
   ```bash
   python manage.py createsuperuser
   ```
3. **Follow prompts** to create admin user

---

## 🎨 Frontend Deployment (Vercel)

### Step 1: Prepare for Deployment

1. **Create `.env.production` in `web-frontend/`** (optional, or use Vercel UI):
   ```env
   VITE_API_BASE_URL=https://your-backend.onrender.com/api
   VITE_ENVIRONMENT=production
   ```
   Replace `your-backend.onrender.com` with your actual Render backend URL.

### Step 2: Deploy to Vercel

1. **Login to Vercel Dashboard**
2. **Click "Add New"** → **"Project"**
3. **Import Git Repository**:
   - Connect GitHub account
   - Select your `chemicalanalyzer` repository
4. **Configure Project**:

   | Setting | Value |
   |---------|-------|
   | **Framework Preset** | `Vite` |
   | **Root Directory** | `web-frontend` |
   | **Build Command** | `npm run build` (auto-detected) |
   | **Output Directory** | `dist` (auto-detected) |
   | **Install Command** | `npm install` (auto-detected) |

5. **Add Environment Variables**:
   - **Key**: `VITE_API_BASE_URL`
   - **Value**: `https://your-backend.onrender.com/api`
   
   - **Key**: `VITE_ENVIRONMENT`
   - **Value**: `production`

6. **Click "Deploy"**

### Step 3: Verify Frontend Deployment

1. **Wait for Deployment** (2-5 minutes)
2. **Visit Your Frontend URL**: `https://<your-app>.vercel.app`
3. **Test Registration/Login**
4. **Upload a CSV file** to verify full integration

---

## 🔄 Update Backend CORS Settings

After frontend deployment, you **MUST** update backend environment variables:

1. **Go to Render Dashboard** → Your Backend Web Service → **Environment**
2. **Update Variables**:
   - `CSRF_TRUSTED_ORIGINS`: Add your Vercel URL
     ```
     https://your-app.vercel.app,https://your-backend.onrender.com
     ```
   - `CORS_ALLOWED_ORIGINS`: Add your Vercel URL
     ```
     https://your-app.vercel.app
     ```
3. **Click "Save Changes"** (will trigger auto-redeploy)

---

## ✅ Post-Deployment Checklist

- [ ] Backend responds at `https://your-backend.onrender.com`
- [ ] Frontend loads at `https://your-app.vercel.app`
- [ ] User registration works
- [ ] User login works
- [ ] CSV upload works
- [ ] Dataset visualization displays correctly
- [ ] AI insights generate (if Gemini API key configured)
- [ ] PDF report download works
- [ ] Admin panel accessible (if superuser created)

---

## 🐛 Troubleshooting

### Backend Issues

**Build Fails**:
- Check `requirements.txt` for syntax errors
- Verify Python version compatibility
- Check build logs in Render dashboard

**Database Connection Errors**:
- Verify `DATABASE_URL` is set correctly
- Ensure database and web service are in same region
- Check database is not suspended (free tier sleeps after inactivity)

**Static Files Not Loading**:
- Verify `STATIC_ROOT` is set in `settings.py`
- Check WhiteNoise middleware is added
- Run `python manage.py collectstatic` in Render shell

**CORS Errors**:
- Verify `CORS_ALLOWED_ORIGINS` includes frontend URL
- Ensure no trailing slashes in URLs
- Check browser console for exact error

### Frontend Issues

**API Connection Fails**:
- Verify `VITE_API_BASE_URL` matches backend URL exactly
- Check backend is running (visit backend URL directly)
- Verify CORS settings on backend

**Build Fails**:
- Check `package.json` for syntax errors
- Verify all dependencies are listed
- Check build logs in Vercel dashboard

**Environment Variables Not Working**:
- Ensure variables start with `VITE_`
- Redeploy after adding environment variables
- Check variable values have no typos

---

## 🔒 Security Recommendations

> [!WARNING]
> **Production Security Checklist**

- [ ] `DEBUG=False` on backend
- [ ] Strong `SECRET_KEY` (50+ random characters)
- [ ] `ALLOWED_HOSTS` set to specific domains (not `*`)
- [ ] HTTPS enforced (automatic on Render/Vercel)
- [ ] Database credentials secure (never commit)
- [ ] API keys in environment variables (never hardcoded)
- [ ] CORS restricted to frontend domain only
- [ ] CSRF protection enabled

---

## 📊 Monitoring & Maintenance

### Render (Backend)

- **View Logs**: Dashboard → Service → Logs
- **Monitor Performance**: Dashboard → Metrics
- **Shell Access**: Dashboard → Shell (for migrations, superuser creation)
- **Auto-Deploy**: Pushes to `main` branch trigger redeployment

### Vercel (Frontend)

- **View Deployments**: Dashboard → Deployments
- **Logs**: Click any deployment → View build/function logs
- **Analytics**: Dashboard → Analytics (paid plans)
- **Auto-Deploy**: Pushes to `main` branch trigger redeployment

---

## 🔄 Updating Your Application

### Backend Updates

1. **Make changes** to code
2. **Commit and push** to GitHub
3. **Render auto-deploys** from `main` branch
4. **Run migrations** if models changed (Render Shell):
   ```bash
   python manage.py migrate
   ```

### Frontend Updates

1. **Make changes** to code
2. **Commit and push** to GitHub
3. **Vercel auto-deploys** from `main` branch

---

## 📞 Support Resources

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **Django Deployment**: https://docs.djangoproject.com/en/4.2/howto/deployment/
- **Vite Deployment**: https://vitejs.dev/guide/static-deploy.html

---

## 🎯 Quick Reference

### Backend URL Structure
```
https://your-backend.onrender.com/          - API Root
https://your-backend.onrender.com/admin/    - Admin Panel
https://your-backend.onrender.com/api/      - API Endpoints
```

### Frontend URL
```
https://your-app.vercel.app                 - Main Application
```

### Key Files
```
backend/
├── start.sh                    - Production startup script
├── requirements.txt            - Python dependencies
├── chemviz_backend/settings.py - Django configuration
└── .env.example                - Environment variable template

web-frontend/
├── .env.example                - Environment variable template
└── src/api/client.js           - API configuration
```

---

**Deployment Date**: {{ date }}  
**Last Updated**: {{ date }}

> [!TIP]
> **After successful deployment**, update your repository README with the live URLs for easy access!
