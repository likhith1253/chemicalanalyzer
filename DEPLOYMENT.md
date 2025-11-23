# Deployment Experience

Deploying ChemViz to production was a learning experience that taught me a lot about cloud platforms and full-stack deployment. I chose Render for the backend and Vercel for the frontend - both offer generous free tiers and integrate seamlessly with GitHub.

## Why These Platforms?

**Vercel for Frontend**: 
- Insanely fast global CDN
- Perfect for React/Vite apps
- Auto-deploys on every GitHub push
- Zero configuration needed

**Render for Backend**:
- Free PostgreSQL database
- Easy Django deployment
- Auto-deploys from GitHub
- Simple environment variable management

## Backend Deployment Journey

### Setting Up PostgreSQL

First, I created a PostgreSQL database on Render:

1. Clicked "New +" → "PostgreSQL"
2. Named it `chemicalanalyzer-db`
3. Selected the free tier
4. Let Render provision it (took about 2 minutes)

Render gave me an "Internal Database URL" - this is what the backend uses to connect. The cool thing is Render services in the same region can connect via this internal URL without going over the public internet.

### Preparing the Django App

I had to make several changes to make Django production-ready:

**Created `start.sh` script**:
```bash
#!/bin/bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn chemviz_backend.wsgi:application
```

This ensures:
- Database migrations run automatically
- Static files are collected
- Gunicorn serves the app (not Django's dev server)

**Updated `settings.py`**:
- Made DEBUG configurable via environment variable
- Added production ALLOWED_HOSTS
- Configured CORS for the frontend URL
- Set up WhiteNoise for static files
- Added PostgreSQL database configuration

### Creating the Web Service

1. Clicked "New +" → "Web Service"
2. Connected my GitHub repository
3. Configured the service:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `./start.sh`
   - **Python Version**: 3.11

### Environment Variables

This was crucial. I configured:

```
SECRET_KEY=<generated-with-django-command>
DEBUG=False
GOOGLE_GEMINI_API_KEY=<my-api-key>
ALLOWED_HOSTS=chemicalanalyzer.onrender.com,localhost
CORS_ALLOWED_ORIGINS=https://chemicalanalyzer.vercel.app
CSRF_TRUSTED_ORIGINS=https://chemicalanalyzer.vercel.app,https://chemicalanalyzer.onrender.com
```

Getting the SECRET_KEY: I ran this locally:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### First Deployment

Hit "Create Web Service" and watched the logs:

- Installed Python packages ✓
- Collected static files ✓
- Ran migrations ✓
- Started Gunicorn ✓
- Service went live! ✓

The backend was now accessible at: `https://chemicalanalyzer.onrender.com/api`

Tested it by visiting the root URL - saw the DRF browsable API interface. Success!

## Frontend Deployment Journey

The frontend deployment was even simpler.

### Configure for Production

Updated `config.js` to read from environment:
```javascript
const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
};
```

### Deploy to Vercel

1. Logged into Vercel
2. Clicked "Add New" → "Project"
3. Imported my GitHub repository
4. Vercel auto-detected:
   - Framework: Vite
   - Root Directory: `web-frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`

5. Added environment variable:
   - `VITE_API_BASE_URL` = `https://chemicalanalyzer.onrender.com/api`

6. Hit "Deploy"

Build completed in under 2 minutes. The site was live at: `https://chemicalanalyzer.vercel.app`

### Connecting Frontend to Backend

Visited the site, tried to register - got CORS error! 

Right, I needed to add the Vercel URL to the backend's CORS settings. Went back to Render, updated:
```
CORS_ALLOWED_ORIGINS=https://chemicalanalyzer.vercel.app
CSRF_TRUSTED_ORIGINS=https://chemicalanalyzer.vercel.app,https://chemicalanalyzer.onrender.com
```

Render auto-redeployed. Waited 3 minutes, tried again - everything worked!

## Testing the Production App

Ran through the full workflow:

1. **Registration**: Created a test account ✓
2. **Login**: Logged in successfully ✓
3. **Upload CSV**: Uploaded sample equipment data ✓
4. **View Dashboard**: Saw charts and statistics ✓
5. **AI Analysis**: Generated insights (took ~5 seconds) ✓
6. **PDF Download**: Downloaded report ✓

Everything worked perfectly!

## Setting Up Auto-Deployment

Both platforms auto-deploy when I push to the `main` branch:

**My workflow now**:
1. Make changes locally
2. Test with `npm run dev` (frontend) and `python manage.py runserver` (backend)
3. Commit and push to GitHub
4. Vercel rebuilds frontend (~2 min)
5. Render rebuilds backend (~5 min)
6. Check production to verify

No manual deployment steps needed!

## Challenges I Encountered

### Challenge 1: CORS Configuration

**Problem**: Frontend couldn't connect to backend - got CORS errors.

**Solution**: Made sure both CORS_ALLOWED_ORIGINS and CSRF_TRUSTED_ORIGINS were set correctly in the backend. The Vercel URL had to be exact - no trailing slashes.

### Challenge 2: Static Files

**Problem**: Django admin panel had no styling.

**Solution**: Added WhiteNoise to serve static files:
```python
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ...
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Challenge 3: Environment Variables

**Problem**: Frontend couldn't read API URL - kept using localhost.

**Solution**: Learned that Vite requires environment variables to start with `VITE_`. Changed to `VITE_API_BASE_URL` and it worked.

### Challenge 4: Database Migrations

**Problem**: First deployment failed because tables didn't exist.

**Solution**: Added `python manage.py migrate` to the start.sh script so migrations run automatically on every deployment.

### Challenge 5: Cold Starts

**Problem**: First request to the backend after inactivity took 30+ seconds.

**Solution**: This is a limitation of Render's free tier - the service spins down after 15 minutes of inactivity. Not much I could do except document it for users. Upgrading to a paid plan would solve this.

### Challenge 6: File Upload Size

**Problem**: Couldn't upload large CSV files.

**Solution**: Set `DATA_UPLOAD_MAX_MEMORY_SIZE` in Django settings to 10MB. For even larger files, would need to configure Gunicorn's timeout settings.

## Production Configuration Summary

### Render (Backend)

**Service Type**: Web Service  
**Region**: Oregon (US West)  
**Plan**: Free  
**Build Command**: `pip install -r requirements.txt`  
**Start Command**: `./start.sh`  
**Auto-Deploy**: Yes (on push to main)

**Environment Variables**:
- SECRET_KEY
- DEBUG=False
- GOOGLE_GEMINI_API_KEY
- ALLOWED_HOSTS
- CORS_ALLOWED_ORIGINS
- CSRF_TRUSTED_ORIGINS
- DATABASE_URL (auto-set)

### Vercel (Frontend)

**Framework**: Vite  
**Region**: Global CDN  
**Build Command**: `npm run build`  
**Output Directory**: `dist`  
**Root Directory**: `web-frontend`  
**Auto-Deploy**: Yes (on push to main)

**Environment Variables**:
- VITE_API_BASE_URL

## Monitoring & Maintenance

### Checking Logs

**Render**: Dashboard → Service → Logs tab
- Shows real-time logs from Gunicorn
- Can see database queries, errors, requests
- Extremely helpful for debugging production issues

**Vercel**: Dashboard → Deployments → Click deployment → View logs
- Shows build logs
- Runtime logs for serverless functions (though we don't use any)

### Database Management

Access PostgreSQL via Render's dashboard:
- Click database → "Connect" → Get connection string
- Can use psql or any PostgreSQL client
- Also accessible via Django admin panel

### Updating the App

**For code changes**:
1. Make changes locally
2. Test thoroughly
3. Push to GitHub
4. Both platforms auto-deploy

**For dependency changes**:
- Update `requirements.txt` (backend) or `package.json` (frontend)
- Push to GitHub
- Platforms will reinstall dependencies during build

**For database changes**:
- Create migration locally: `python manage.py makemigrations`
- Push to GitHub
- Migration runs automatically via `start.sh`

## Performance

### Frontend (Vercel)
- **Load Time**: ~1.2 seconds (first visit)
- **Subsequent Loads**: ~200ms (cached)
- **Global CDN**: Fast everywhere
- **Lighthouse Score**: 95+ on Performance

### Backend (Render)
- **Cold Start**: ~30 seconds (free tier limitation)
- **Warm Response**: ~200-500ms per API call
- **Database Queries**: ~50-100ms average
- **AI Insights**: ~3-5 seconds (depends on Gemini API)

## Cost

**Total Monthly Cost**: $0

Both platforms offer generous free tiers:
- **Render Free**: 750 hours/month (enough for one service)
- **Vercel Free**: Unlimited bandwidth, 100 GB-hours

For a portfolio project or small-scale app, this is perfect. For production scale, would need:
- **Render**: Starter plan ($7/month) for no cold starts
- **Vercel**: Pro plan ($20/month) for advanced features

## Custom Domain (Optional)

Both platforms support custom domains:

**Vercel**: Settings → Domains → Add custom domain  
**Render**: Settings → Custom Domain → Add

Would need to:
1. Buy a domain (e.g., from Namecheap, Google Domains)
2. Point DNS to Vercel/Render
3. SSL certificates are automatic (Let's Encrypt)

## Backup Strategy

**Database**: 
- Render free tier doesn't include automatic backups
- Could set up a cron job to dump the database periodically
- For production, would use Render's paid backup feature

**Code**:
- Git repository is the source of truth
- Pushed to GitHub
- Could be cloned/deployed anywhere

## Security Considerations

What I implemented:

✓ HTTPS enforced (automatic on both platforms)  
✓ DEBUG=False in production  
✓ Strong SECRET_KEY  
✓ ALLOWED_HOSTS set to specific domains (not `*`)  
✓ CORS restricted to frontend domain only  
✓ CSRF protection enabled  
✓ Environment variables for secrets (not in code)  
✓ SQL injection protection (Django ORM)  
✓ XSS protection (React escaping)  

## Final Thoughts

Deploying to Render and Vercel was surprisingly smooth. The hardest part was getting the CORS configuration right - once that was done, everything just worked.

The CI/CD integration with GitHub is fantastic - I can push changes and they're live in minutes. The free tiers are more than adequate for a portfolio project.

If I were to do this again, I'd:
1. Set up the environment variables before the first deployment
2. Test CORS locally using the production URLs
3. Document all environment variables in a .env.example file
4. Create a deployment checklist

**Live URLs**:
- Frontend: https://chemicalanalyzer.vercel.app
- Backend: https://chemicalanalyzer.onrender.com/api
- Admin: https://chemicalanalyzer.onrender.com/admin
