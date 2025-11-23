# Backend Development Experience

Building the backend for ChemViz was all about creating a robust, scalable API that could handle data processing, AI integration, and user management. I chose Django REST Framework because it provides excellent tools for building APIs quickly while maintaining production-quality code.

## Tech Stack

**Core Framework**: Django 4.2 with Django REST Framework 3.14

I picked Django because:
- Excellent ORM for database operations
- Built-in admin panel for data management
- Strong security features out of the box
- Amazing community and documentation

**Key Libraries**:
- **Pandas** (2.2.0) - For heavy-duty data processing and CSV analysis
- **Google Generative AI** (0.8.3) - Integration with Gemini 2.5 for AI insights
- **ReportLab** (4.2.5) - Professional PDF report generation
- **Gunicorn** (22.0.0) - Production WSGI server
- **WhiteNoise** (6.7.0) - Serving static files efficiently
- **psycopg2-binary** (2.9.9) - PostgreSQL database adapter

## Project Architecture

```
backend/
├── chemviz_backend/        # Main Django project
│   ├── settings.py        # Configuration
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI config
├── equipment/             # Main app
│   ├── models.py         # Database models
│   ├── views.py          # API endpoints
│   ├── serializers.py    # Data validation & serialization
│   ├── services.py       # Business logic
│   └── urls.py           # App-specific routes
├── tests/                # Test suite
└── manage.py
```

## Database Design

I designed three main models:

### User Model
Extended Django's built-in User model with token-based authentication. Each user has their own isolated datasets.

### Dataset Model
```python
class Dataset(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='datasets/')
    upload_date = models.DateTimeField(auto_now_add=True)
    analysis_results = models.JSONField(null=True, blank=True)
```

The `analysis_results` field stores the computed statistics as JSON, avoiding repeated calculations.

### Equipment Model
```python
class Equipment(models.Model):
    dataset = models.ForeignKey(Dataset)
    name = models.CharField(max_length=200)
    equipment_type = models.CharField(max_length=100)
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()
```

Each CSV row becomes an Equipment instance linked to its Dataset.

## Authentication System

I implemented token-based authentication using DRF's TokenAuthentication:

**Registration**: POST `/api/auth/register/`
- Validates username uniqueness
- Requires password confirmation
- Automatically generates auth token
- Returns user info + token

**Login**: POST `/api/auth/login/`
- Accepts username/password
- Returns existing or creates new token
- Token never expires (session-based)

**Logout**: POST `/api/auth/logout/`
- Deletes the user's token
- Requires authentication

This approach is simpler than JWT and works perfectly for this use case.

## Data Processing Pipeline

The most interesting part was the data processing. When a CSV is uploaded:

1. **Validation**: Check file format, required columns
2. **Parsing**: Use Pandas to read the CSV
3. **Database Storage**: Create Dataset and Equipment records
4. **Analysis**: Compute statistics (mean, std, distributions)
5. **Storage**: Save analysis results as JSON

The analysis happens in `services.py`:

```python
def analyze_dataset(dataset_id):
    equipment_list = Equipment.objects.filter(dataset_id=dataset_id)
    df = pd.DataFrame(list(equipment_list.values()))
    
    stats = {
        'total_equipment': len(df),
        'avg_flowrate': df['flowrate'].mean(),
        'avg_pressure': df['pressure'].mean(),
        'avg_temperature': df['temperature'].mean(),
        # ... more statistics
    }
    return stats
```

Pandas makes this incredibly efficient even with large datasets.

## AI Integration with Google Gemini

This was one of the coolest features. I integrated Google's Gemini 2.5 API to generate maintenance recommendations:

```python
import google.generativeai as genai

genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash-exp')

prompt = f"""
Analyze this chemical equipment data and provide maintenance insights:
{analysis_data}
"""

response = model.generate_content(prompt)
insights = response.text
```

I added fallback logic to try multiple model versions (gemini-2.0-flash-exp, gemini-1.5-flash, gemini-1.5-pro) in case one isn't available.

The AI generates:
- Equipment condition assessments
- Maintenance priorities
- Potential issues to watch for
- Optimization recommendations

## PDF Report Generation

Used ReportLab to create professional PDF reports:

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table

def generate_pdf_report(dataset):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    # Build report with stats, charts, AI insights
    doc.build(story)
    return buffer.getvalue()
```

Each report includes:
- Dataset summary
- Statistical analysis
- Equipment listings
- AI-generated insights
- Visual charts (as embedded images)

## API Endpoints

### Dataset Endpoints

**Upload**: `POST /api/upload/`
- Accepts CSV file via multipart/form-data
- Validates and processes
- Returns dataset ID and initial stats

**List**: `GET /api/datasets/`
- Returns all datasets for authenticated user
- Includes basic metadata

**Detail**: `GET /api/datasets/{id}/`
- Full dataset with all equipment records
- Includes cached analysis results

**Analyze**: `GET /api/datasets/{id}/analyze/`
- Triggers AI analysis if not done
- Returns insights and recommendations

**PDF Report**: `GET /api/datasets/{id}/report/pdf/`
- Generates and downloads PDF
- Returns file as attachment

## CORS & Security Configuration

Production security was critical:

```python
CORS_ALLOWED_ORIGINS = [
    'https://chemicalanalyzer.vercel.app',
]

CSRF_TRUSTED_ORIGINS = [
    'https://chemicalanalyzer.vercel.app',
    'https://chemicalanalyzer.onrender.com',
]

ALLOWED_HOSTS = [
    'chemicalanalyzer.onrender.com',
    'localhost',
]
```

Also disabled DEBUG in production and used environment variables for secrets.

## Environment Configuration

Created a robust environment variable system:

```python
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG', 'False') == 'True'
GOOGLE_GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY')
```

The `.env` file never gets committed - it's in `.gitignore`.

## Database: SQLite to PostgreSQL

Developed with SQLite locally for simplicity. For production on Render, I configured PostgreSQL:

```python
import dj_database_url

if 'DATABASE_URL' in os.environ:
    DATABASES['default'] = dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
    )
```

This automatically switches to PostgreSQL in production when `DATABASE_URL` is set.

## Static Files with WhiteNoise

Configured WhiteNoise to serve static files without needing a separate CDN:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Right after security
    # ... other middleware
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

This compresses and caches static files for optimal performance.

## Deployment to Render

Deployment setup:

**Build Command**: `pip install -r requirements.txt`

**Start Command**: Created a custom `start.sh`:
```bash
#!/bin/bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn chemviz_backend.wsgi:application
```

This ensures migrations run and static files are collected on every deployment.

**Environment Variables**:
- `SECRET_KEY` - Django secret
- `DEBUG=False` - Production mode
- `GOOGLE_GEMINI_API_KEY` - AI integration
- `ALLOWED_HOSTS` - Comma-separated domains
- `CORS_ALLOWED_ORIGINS` - Frontend URL
- `DATABASE_URL` - Auto-set by Render PostgreSQL

## Testing

Created comprehensive tests in the `tests/` directory:

- `test_auth.py` - Registration, login, logout
- `test_upload.py` - CSV upload and validation
- `test_datasets.py` - Dataset CRUD operations
- `test_models.py` - Model validations
- `test_serializers.py` - Data serialization
- `test_integration.py` - End-to-end workflows

Run with: `python manage.py test`

The tests ensure the core functionality works and catch regressions.

## Challenges & Solutions

**CSV Column Mapping**: Different datasets might have slight variations in column names. Added flexible column detection.

**Large File Uploads**: Had to configure file size limits in both Django and Nginx/Gunicorn settings.

**AI API Rate Limits**: Added retry logic and fallback to different Gemini models.

**Cold Starts on Render**: Free tier services sleep after inactivity. First request takes ~30 seconds to wake up - documented this for users.

**CORS Pre-flight**: Initially had issues with OPTIONS requests. Fixed by enabling CORS middleware properly.

## Performance Optimizations

- **Database Indexing**: Added indexes on foreign keys and frequently queried fields
- **Query Optimization**: Used `select_related()` and `prefetch_related()` to avoid N+1 queries
- **Caching**: Stored analysis results as JSON to avoid recalculating
- **Pandas Vectorization**: Used Pandas' vectorized operations instead of loops

## Admin Panel

Django's admin panel is incredibly useful. I customized it to show:
- User statistics
- Dataset listings with filters
- Equipment records with search
- Inline equipment editing within datasets

Access at: `https://chemicalanalyzer.onrender.com/admin/`

## Final Thoughts

Building this Django backend taught me so much about API design, data processing, and production deployment. The combination of DRF for the API, Pandas for data processing, and Gemini for AI creates a powerful platform. Deploying on Render with PostgreSQL gives it production-grade reliability.

The API is live at: https://chemicalanalyzer.onrender.com/api
