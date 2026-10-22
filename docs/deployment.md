# Deployment Guide

ChemViz utilizes a seamless CI/CD pipeline leveraging Vercel for the frontend and Render for the backend. Both services automatically build and deploy the latest codebase whenever changes are pushed to the main branch of the GitHub repository.

## 1. Backend Deployment (Render)

The Django backend is hosted on a Render Web Service, connected to a managed PostgreSQL database.

### Prerequisites on Render
- A free PostgreSQL database instance.
- A new Web Service linked to your GitHub repository.

### Render Configuration
When setting up the Web Service on Render, configure the following:

- **Environment**: Python
- **Build Command**: 
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```bash
  ./start.sh
  ```
  *(Note: `start.sh` handles database migrations, collects static files via WhiteNoise, and starts the Gunicorn server).*

### Backend Environment Variables
Configure the following secrets in the Render dashboard:
- `SECRET_KEY`: Your Django secret key (required: the app refuses to start without it when `DEBUG` is off).
- `DEBUG`: Set to `False`.
- `GOOGLE_GEMINI_API_KEY`: Your valid API key for AI generation.
- `ALLOWED_HOSTS`: `your-render-app-url.onrender.com`
- `CORS_ALLOWED_ORIGINS`: `https://your-vercel-app-url.vercel.app` (comma separated; no wildcard)
- `CSRF_TRUSTED_ORIGINS`: your frontend and backend https origins (comma separated)
- `DATABASE_URL`: Automatically populated by Render when attaching the database.

## 2. Frontend Deployment (Vercel)

The React frontend is hosted on Vercel, which provides a lightning-fast global CDN for static assets.

### Vercel Configuration
1. Import the GitHub repository into Vercel.
2. Select the `web-frontend` directory as the **Root Directory**.
3. Vercel automatically detects the Vite framework and sets the Build Command (`npm run build`) and Output Directory (`dist`).

### Frontend Environment Variables
Configure the following environment variable in the Vercel dashboard:
- `VITE_API_BASE_URL`: `https://your-render-app-url.onrender.com/api`

## 3. Post-Deployment Verification

1. Ensure the Render deployment completes successfully and the database migrations (`python manage.py migrate`) are applied.
2. Visit the Vercel URL and attempt to register a new user account.
3. Upload a sample dataset to verify end-to-end connectivity, background Pandas processing, and database persistence.
4. Request AI insights to verify the `GOOGLE_GEMINI_API_KEY` is functioning correctly.

*(Note: Render free-tier services sleep after periods of inactivity. The initial API request may take up to 30 seconds to wake the service.)*
