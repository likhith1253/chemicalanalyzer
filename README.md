# Chemical Equipment Data Analyzer

A full-stack application for analyzing chemical equipment data with AI-powered insights. Upload CSV files containing equipment information and get automated analysis with PDF reports.

## What It Does

- Upload CSV files with equipment data
- View statistics and visualizations
- Generate AI-powered insights
- Download PDF reports
- Cross-platform desktop app

## Tech Stack

### Backend
- Django REST Framework
- Token authentication
- Google Gemini API for AI insights
- Pandas for data processing
- ReportLab for PDF generation

### Frontend
- React with Vite
- Chart.js for visualizations
- Axios for API calls
- CSS for styling

### Desktop App
- PyQt5
- System tray integration
- Native notifications

## Project Structure

```
chemicalanalyzer/
├── backend/           # Django backend
│   ├── chemviz_backend/
│   │   ├── settings.py
│   │   └── urls.py
│   └── equipment/
│       ├── models.py
│       ├── views.py
│       ├── services.py
│       └── serializers.py
├── web-frontend/      # React frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── api/
│   └── package.json
├── desktop-client/    # PyQt5 desktop app
│   ├── main.py
│   └── requirements.txt
└── docs/
    ├── sample_equipment_data.csv
    └── ARCHITECTURE.md
```

## Setup

### Backend

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

3. Set environment variable:
```bash
export GOOGLE_GEMINI_API_KEY=your_api_key_here
# On Windows: set GOOGLE_GEMINI_API_KEY=your_api_key_here
```

4. Run migrations:
```bash
python backend/manage.py migrate
```

5. Start server:
```bash
python backend/manage.py runserver
```

Backend runs on http://localhost:8000

### Frontend

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

Frontend runs on http://localhost:5173

### Desktop Client

1. Install dependencies:
```bash
pip install -r desktop-client/requirements.txt
```

2. Run desktop app:
```bash
python desktop-client/main.py
```

## How to Use

1. Start the backend server
2. Start the frontend
3. Open browser to http://localhost:5173
4. Register/login to get auth token
5. Upload CSV file with equipment data
6. View analysis and insights
7. Download PDF report

## CSV Format

Required columns:
- Equipment Name
- Type
- Flowrate
- Pressure
- Temperature

Sample data in docs/sample_equipment_data.csv

## API Endpoints

- POST /api/auth/register/ - Register user
- POST /api/auth/login/ - Login and get token
- POST /api/datasets/upload/ - Upload CSV
- GET /api/datasets/ - List datasets
- GET /api/datasets/{id}/ - Get dataset details
- GET /api/datasets/{id}/pdf/ - Download PDF
- GET /api/datasets/{id}/ai-insights/ - Get AI insights

## Deployment

### Backend (Django)

Use gunicorn with nginx:
```bash
gunicorn chemviz_backend.wsgi:application --bind 0.0.0.0:8000
```

### Frontend (React)

Build for production:
```bash
npm run build
```

Serve static files with nginx or Apache.

### Environment Variables

- GOOGLE_GEMINI_API_KEY - Required for AI insights
- DEBUG - Set to False in production
- ALLOWED_HOSTS - Configure for production

## Development

### Adding New Features

1. Backend: Add views in equipment/views.py
2. Frontend: Create components in src/components/
3. Update API client in src/api/client.js

### Testing

Run backend tests:
```bash
python backend/manage.py test
```

### Database

Default uses SQLite. For production:
- PostgreSQL recommended
- Update DATABASES setting in settings.py

## Troubleshooting

- AI insights not working: Check GOOGLE_GEMINI_API_KEY
- Upload errors: Verify CSV format
- PDF generation issues: Check ReportLab installation
- Frontend not connecting: Verify CORS settings

## License

MIT License
