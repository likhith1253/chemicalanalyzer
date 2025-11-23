# ChemViz - Chemical Equipment Analyzer

A full-stack web application I built to analyze chemical equipment performance data using AI. This project demonstrates my skills in React, Django, data processing, and cloud deployment.

🌐 **Live Demo**: [chemicalanalyzer.vercel.app](https://chemicalanalyzer.vercel.app)  
🔗 **API**: [chemicalanalyzer.onrender.com/api](https://chemicalanalyzer.onrender.com/api)

## What It Does

ChemViz takes CSV files containing chemical equipment data (flowrate, pressure, temperature) and transforms them into actionable insights. Users can upload datasets, view interactive charts, get AI-powered maintenance recommendations, and generate professional PDF reports.

**Key Features**:
- 📊 Real-time data visualization with interactive charts
- 🤖 AI-powered insights using Google Gemini 2.5
- 📄 Professional PDF report generation
- 🔐 Secure user authentication and data isolation
- 📱 Responsive design that works on all devices

## Tech Stack

### Frontend
- **React 18** - Modern UI with hooks and functional components
- **Vite** - Lightning-fast development and optimized production builds
- **Chart.js** - Interactive data visualizations
- **Axios** - API communication with interceptors
- **React Router v6** - Client-side routing
- **Glassmorphism CSS** - Modern, premium design aesthetic

### Backend
- **Django 4.2** - Robust server framework
- **Django REST Framework** - RESTful API design
- **Pandas** - High-performance data processing
- **Google Gemini API** - AI-powered insights
- **ReportLab** - PDF generation
- **PostgreSQL** - Production database
- **Gunicorn + WhiteNoise** - Production-ready serving

### DevOps
- **Vercel** - Frontend hosting with global CDN
- **Render** - Backend hosting with PostgreSQL
- **GitHub** - Version control with auto-deployment
- **Environment Variables** - Secure configuration management

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Vercel    │  HTTPS  │    Render    │  API    │   Google    │
│  (React)    │────────▶│   (Django)   │────────▶│   Gemini    │
│  Frontend   │◀────────│   Backend    │◀────────│     AI      │
└─────────────┘         └──────────────┘         └─────────────┘
                              │
                              │ SQL
                              ▼
                        ┌──────────────┐
                        │ PostgreSQL   │
                        │   Database   │
                        └──────────────┘
```

## Project Structure

```
chemicalanalyzer/
├── web-frontend/          # React application
│   ├── src/
│   │   ├── api/          # API client & auth
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Route pages
│   │   └── config.js     # Environment config
│   └── package.json
│
├── backend/              # Django REST API
│   ├── chemviz_backend/  # Project settings
│   ├── equipment/        # Main app (models, views, serializers)
│   ├── tests/           # Test suite
│   └── requirements.txt
│
├── pyqt-app/            # Desktop application (bonus)
├── docs/                # Documentation & samples
├── frontend.md          # Frontend development notes
├── backend.md           # Backend development notes
└── deployment.md        # Deployment guide
```

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google Gemini API key ([get one free here](https://aistudio.google.com/apikey))

### Local Development Setup

**1. Clone the repository**
```bash
git clone https://github.com/likhith1253/chemicalanalyzer
cd chemicalanalyzer
```

**2. Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Configure Environment**

Create `backend/.env`:
```env
GOOGLE_GEMINI_API_KEY=your_api_key_here
DEBUG=True
SECRET_KEY=your-secret-key-for-development
```

**4. Initialize Database**
```bash
python manage.py migrate
python manage.py createsuperuser  # Optional: for admin access
```

**5. Start Backend Server**
```bash
python manage.py runserver
# Running at http://localhost:8000/api
```

**6. Frontend Setup** (new terminal)
```bash
cd web-frontend
npm install
npm run dev
# Running at http://localhost:5173
```

**7. Open Browser**

Visit `http://localhost:5173` and create an account to start uploading datasets!

### Desktop App (Optional)

I also built a PyQt5 desktop application:
```powershell
.\run_desktop_app.ps1
```

## How It Works

### Data Processing Pipeline

1. **Upload**: User uploads CSV with equipment data
2. **Validation**: Backend validates file format and required columns
3. **Parsing**: Pandas reads and processes the CSV
4. **Storage**: Data saved to PostgreSQL database
5. **Analysis**: Statistical calculations (mean, std dev, distributions)
6. **AI Insights**: Google Gemini analyzes data and generates recommendations
7. **Visualization**: Frontend displays interactive charts
8. **Export**: User can download PDF report

### Expected CSV Format

| Column | Type | Description |
|--------|------|-------------|
| Equipment Name | String | Unique identifier |
| Type | String | Equipment category |
| Flowrate | Float | Liters per minute |
| Pressure | Float | Pressure in bar |
| Temperature | Float | Temperature in °C |

See `docs/sample_equipment_data.csv` for an example.

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Create new account
- `POST /api/auth/login/` - Login and get token
- `POST /api/auth/logout/` - Logout

### Datasets
- `POST /api/upload/` - Upload CSV file
- `GET /api/datasets/` - List all user's datasets
- `GET /api/datasets/{id}/` - Get dataset details
- `GET /api/datasets/{id}/analyze/` - Generate AI insights
- `GET /api/datasets/{id}/report/pdf/` - Download PDF report

All dataset endpoints require authentication token in headers:
```
Authorization: Token <your-token>
```

## Key Features I'm Proud Of

### 1. Smart Data Processing
Using Pandas for data processing was a game-changer. It handles large CSV files efficiently and makes statistical calculations super fast.

### 2. AI Integration
Integrating Google's Gemini 2.5 API to generate contextual maintenance recommendations. The AI analyzes the data patterns and provides actionable insights.

### 3. Security
Implemented proper authentication, CORS configuration, CSRF protection, and environment-based secrets management. Production-ready security.

### 4. Glassmorphism Design
The frontend uses modern glassmorphism effects with smooth animations. Looks professional and feels premium.

### 5. Full CI/CD
Push to GitHub → Auto-deploy to production. No manual steps needed. Both frontend and backend automatically update.

## Testing

Backend tests cover auth, uploads, data processing, and API endpoints:
```bash
cd backend
python manage.py test
```

Tests include:
- User registration and authentication
- CSV upload and validation  
- Data processing accuracy
- API endpoint responses
- Model validations

## Deployment

The app is deployed on two platforms:

- **Frontend**: Vercel (global CDN, instant deploys)
- **Backend**: Render (free PostgreSQL, auto-scaling)

See [deployment.md](deployment.md) for detailed deployment instructions.

## Environment Variables

### Backend (Required)
- `SECRET_KEY` - Django secret key
- `GOOGLE_GEMINI_API_KEY` - For AI insights
- `DEBUG` - Set to False in production
- `ALLOWED_HOSTS` - Comma-separated domains
- `CORS_ALLOWED_ORIGINS` - Frontend URL
- `DATABASE_URL` - PostgreSQL connection (auto-set on Render)

### Frontend (Required)
- `VITE_API_BASE_URL` - Backend API URL

## What I Learned

Building this project taught me:

- **Full-stack integration**: Connecting React frontend with Django backend
- **Data processing**: Using Pandas for efficient data manipulation
- **AI integration**: Working with Google's Gemini API
- **Cloud deployment**: Deploying to production on Vercel and Render
- **Security best practices**: CORS, CSRF, authentication, environment variables
- **Modern React patterns**: Hooks, context, routing, state management
- **API design**: RESTful endpoints, proper error handling, token auth
- **DevOps**: CI/CD pipelines, environment configuration, database migrations

## Challenges Overcome

1. **CORS Configuration**: Spent time debugging CORS issues - learned the importance of exact URL matching
2. **File Uploads**: Figured out multipart/form-data handling between React and Django
3. **AI API Integration**: Implemented fallback logic for different Gemini model versions
4. **Production Database**: Migrated from SQLite to PostgreSQL for production
5. **Static Files**: Configured WhiteNoise for efficient static file serving
6. **Cold Starts**: Documented Render free tier limitations for users

## Future Enhancements

Ideas for v2:
- [ ] Real-time collaboration on datasets
- [ ] Export to Excel format
- [ ] Historical trend analysis across datasets
- [ ] Email notifications for analysis completion
- [ ] Shareable dataset links
- [ ] API rate limiting
- [ ] Caching layer with Redis
- [ ] WebSocket support for real-time updates

## Contributing

This is a portfolio project, but I'm open to suggestions! Feel free to:
- Report bugs via GitHub issues
- Suggest features
- Submit pull requests

## License

MIT License - feel free to use this project as inspiration or reference for your own work.

## Contact

Questions or want to discuss the implementation? Feel free to reach out!

---

**Live Demo**: [chemicalanalyzer.vercel.app](https://chemicalanalyzer.vercel.app)  
**Source Code**: This repository  
**Documentation**: See [frontend.md](frontend.md), [backend.md](backend.md), [deployment.md](deployment.md)

Built with ❤️ using React, Django, and AI
