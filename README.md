# ChemViz - Chemical Equipment Analyzer

A full-stack analytical platform that transforms chemical equipment data into actionable insights using AI. Built to handle real-world industrial datasets with enterprise-grade architecture.

[![Live Demo](https://img.shields.io/badge/demo-live-green)](https://chemicalanalyzer.vercel.app) [![Backend API](https://img.shields.io/badge/API-deployed-blue)](https://chemicalanalyzer.onrender.com/api)

## Overview

ChemViz analyzes chemical equipment performance data through advanced data processing and AI-powered insights. The platform supports both web and desktop interfaces, offering flexibility for different operational environments.

**Key Capabilities:**
- Automated data validation and statistical analysis
- AI-generated maintenance recommendations using Google Gemini
- Real-time visualization of equipment metrics
- Professional PDF report generation
- Multi-platform support (Web + Desktop)

## Architecture

### Technology Stack

**Backend (Django REST Framework)**
- Token-based authentication with session management
- Pandas for high-performance data processing
- Google Gemini 2.5 API integration for AI insights
- ReportLab for PDF generation
- PostgreSQL-ready with SQLite fallback

**Frontend (React + Vite)**
- Modern React with functional components and hooks
- Chart.js for interactive data visualizations
- Axios with centralized API client
- Toast notifications for UX feedback
- Responsive CSS with glassmorphism design

**Desktop Client (PyQt5)**
- Native Windows application
- System tray integration
- Cross-platform compatibility
- Shares backend infrastructure with web app

**DevOps**
- CI/CD: Auto-deployment via GitHub
- Frontend: Vercel (global CDN)
- Backend: Render (containerized deployment)
- Static Assets: WhiteNoise middleware

## Project Structure

```
chemicalanalyzer/
├── backend/                    # Django REST API
│   ├── chemviz_backend/
│   │   ├── settings.py        # Production-ready configuration
│   │   └── urls.py            # API routing
│   ├── equipment/
│   │   ├── models.py          # Data models
│   │   ├── views.py           # API endpoints
│   │   ├── services.py        # Business logic & AI integration
│   │   └── serializers.py     # Data validation
│   └── requirements.txt
│
├── web-frontend/               # React SPA
│   ├── src/
│   │   ├── api/               # API client & authentication
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Route components
│   │   └── config.js          # Environment configuration
│   └── package.json
│
├── pyqt-app/                   # Desktop application
│   ├── main.py
│   ├── api_client.py
│   └── widgets/
│
└── docs/
    └── sample_equipment_data.csv
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- [Google Gemini API Key](https://aistudio.google.com/apikey)

### Local Development

**1. Clone and Setup Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**2. Configure Environment**
```bash
# Create backend/.env
GOOGLE_GEMINI_API_KEY=your_api_key_here
DEBUG=True
SECRET_KEY=your-secret-key-here
```

**3. Initialize Database**
```bash
python manage.py migrate
python manage.py createsuperuser  # Optional: for admin access
```

**4. Start Backend**
```bash
python manage.py runserver
# API available at http://localhost:8000/api
```

**5. Launch Frontend**
```bash
cd web-frontend
npm install
npm run dev
# App available at http://localhost:5173
```

**6. Run Desktop App (Optional)**
```powershell
.\run_desktop_app.ps1
```

## Features

### Data Processing Pipeline
1. **Upload**: CSV validation with intelligent column mapping
2. **Analysis**: Statistical aggregation (mean, distribution, outliers)
3. **AI Insights**: GPT-powered recommendations via Gemini API
4. **Export**: Professional PDF reports with charts

### Supported CSV Format

| Column | Type | Description |
|--------|------|-------------|
| Equipment Name | String | Unique identifier |
| Type | String | Equipment category |
| Flowrate | Float | L/min |
| Pressure | Float | bar |
| Temperature | Float | °C |

*See [sample_equipment_data.csv](docs/sample_equipment_data.csv) for reference*

## API Documentation

### Authentication
```http
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/logout/
```

### Dataset Operations
```http
POST   /api/upload/              # Upload CSV
GET    /api/datasets/            # List all datasets
GET    /api/datasets/{id}/       # Get details
GET    /api/datasets/{id}/analyze/    # Generate AI insights
GET    /api/datasets/{id}/report/pdf/ # Download PDF
```

### Authentication Token
Include in headers:
```
Authorization: Token <your-auth-token>
```

## Deployment

### Production Environment

**Backend (Render)**
- Service Type: Web Service
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn chemviz_backend.wsgi`
- Environment Variables:
  - `GOOGLE_GEMINI_API_KEY`
  - `SECRET_KEY`
  - `DEBUG=False`

**Frontend (Vercel)**
- Framework: Vite
- Build Command: `npm run build`
- Output Directory: `dist`
- Root Directory: `web-frontend`

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GOOGLE_GEMINI_API_KEY` | Yes | AI insights generation |
| `SECRET_KEY` | Yes | Django security |
| `DEBUG` | Prod: No | Development mode toggle |
| `ALLOWED_HOSTS` | Prod: Yes | Comma-separated domains |
| `DATABASE_URL` | Optional | PostgreSQL connection |

## Technical Highlights

- **Scalable Architecture**: Stateless API design with token authentication
- **AI Integration**: Fallback mechanism for multiple Gemini model versions
- **Error Handling**: Comprehensive validation with user-friendly error messages
- **Performance**: Pandas vectorized operations for large datasets
- **Security**: CORS configuration, CSRF protection, environment-based secrets
- **Deployment**: Zero-downtime deployments via CI/CD integration

## Development

### Code Quality
- Type hints in Python for better IDE support
- ESLint configuration for JavaScript consistency
- Modular component architecture
- Centralized API client with interceptors

### Testing
```bash
# Backend
python manage.py test

# Frontend
npm run test
```

### Database Admin
Access Django admin panel:
```
http://localhost:8000/admin/
# Production: https://chemicalanalyzer.onrender.com/admin/
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| AI insights fail | Verify `GOOGLE_GEMINI_API_KEY` in environment |
| Upload errors | Check CSV column names match requirements |
| CORS errors | Ensure frontend URL in `CORS_ALLOWED_ORIGINS` |
| PDF generation fails | Install `python-dev` and `libcairo2-dev` |
| Render service sleeps | Free tier limitation - first request wakes service (~30s) |

## Contributing

This project demonstrates full-stack development skills including:
- RESTful API design
- Modern React patterns
- AI/ML integration
- Cloud deployment
- Database modeling
- Authentication & authorization

## License

MIT License - feel free to use this project as a portfolio reference.

---

**Live Demo**: [chemicalanalyzer.vercel.app](https://chemicalanalyzer.vercel.app)  
**API Endpoint**: [chemicalanalyzer.onrender.com/api](https://chemicalanalyzer.onrender.com/api)
