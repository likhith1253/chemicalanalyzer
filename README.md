# Chemical Equipment Parameter Visualizer

A comprehensive three-tier application for visualizing and analyzing chemical equipment parameters from CSV data. The system features a Django REST API backend, a modern React web frontend, and a native PyQt5 desktop application.

## 🚀 Tech Stack

### Backend
- **Django** & **Django REST Framework** - REST API and data processing
- **PostgreSQL/SQLite** - Database storage
- **ReportLab** - PDF report generation
- **Token Authentication** - Secure user authentication

### Web Frontend
- **React 18** - Component-based UI framework
- **Vite** - Fast development build tool
- **Chart.js** - Interactive data visualization
- **Axios** - HTTP client with authentication
- **TailwindCSS** - Modern styling framework

### Desktop Frontend
- **PyQt5** - Cross-platform native desktop application
- **Matplotlib** - Scientific plotting and visualization
- **Requests** - HTTP client library

## ✨ Features

- **🔐 Secure Authentication**: Token-based login system across all platforms
- **📊 Data Visualization**: Interactive charts showing equipment type distribution
- **📁 CSV Upload**: Drag-and-drop file upload with validation and processing
- **📋 Dataset Management**: Browse, view, and manage historical datasets
- **📄 PDF Reports**: Generate and download comprehensive PDF reports
- **🎨 Modern UI**: Glassmorphism design with responsive layouts
- **⚡ Real-time Updates**: Live data updates and progress tracking
- **🔄 Cross-platform**: Web and desktop interfaces with shared backend

## 📁 Repository Structure

```
chemical-equipment-visualizer/
├── backend/                    # Django REST API
│   ├── chemviz_backend/        # Django project settings
│   ├── equipment/              # Main app with models, views, serializers
│   ├── manage.py              # Django management script
│   └── requirements.txt        # Python dependencies
├── web-frontend/               # React web application
│   ├── src/                    # React source code
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Page components
│   │   └── api/                # API client integration
│   ├── package.json            # Node.js dependencies
│   └── .env.example            # Environment variables template
├── pyqt-app/                   # PyQt5 desktop application
│   ├── widgets/                # UI components
│   ├── api_client.py           # Django API integration
│   ├── main.py                 # Application entry point
│   └── requirements.txt        # Python dependencies
├── docs/                       # Documentation
│   ├── sample_equipment_data.csv  # Sample data for testing
│   └── ARCHITECTURE.md         # System architecture overview
└── README.md                   # This file
```

## 🛠️ Setup Instructions

### Backend Setup

1. **Create and activate virtual environment:**
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run database migrations:**
```bash
python manage.py migrate
```

4. **Create superuser (optional):**
```bash
python manage.py createsuperuser
```

5. **Start the development server:**
```bash
python manage.py runserver
```

The backend API will be available at `http://localhost:8000/api/`

### Web Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd web-frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Create environment file:**
```bash
cp .env.example .env
```

4. **Set API base URL in `.env`:**
```
VITE_API_BASE_URL=http://localhost:8000/api
```

5. **Start development server:**
```bash
npm run dev
```

The web application will be available at `http://localhost:5173`

**For production:**
```bash
npm run build
npm run preview
```

### Desktop Client Setup

1. **Navigate to desktop client directory:**
```bash
cd pyqt-app
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python main.py
```

## 📖 Usage Guide

### User Registration

You can register users through:
- Django admin interface (`/admin/`)
- API endpoint `POST /api/auth/register/` (if implemented)
- Direct database creation

### Login Process

**Web Frontend:**
1. Open `http://localhost:8000` in browser
2. Enter credentials on login page
3. Access dashboard after successful authentication

**Desktop Application:**
1. Launch the PyQt5 application
2. Enter credentials in login dialog
3. Main dashboard opens automatically

### CSV Upload and Analytics

1. **Upload CSV file:**
   - Web: Drag-and-drop or use file picker
   - Desktop: Use "Upload CSV" button

2. **Sample data:** Use `docs/sample_equipment_data.csv` for testing

3. **View analytics:**
   - Summary cards with key metrics
   - Interactive charts showing type distribution
   - Data table with equipment details

### Dataset Management

1. **View recent datasets:** Last 5 datasets shown in history
2. **Select dataset:** Click any dataset to view detailed analytics
3. **Refresh data:** Use refresh button to update dataset list

### PDF Report Generation

1. **Generate PDF:**
   - Web: "Download PDF" button on dashboard
   - Desktop: "📄 Download PDF" button

2. **Report includes:**
   - Dataset summary statistics
   - Equipment type distribution charts
   - Detailed equipment data table

## 📊 Sample Data

Use the provided sample data file for testing:
```
docs/sample_equipment_data.csv
```

Contains 15 rows of realistic chemical equipment data with:
- Equipment types: Pump, Valve, Reactor, Column
- Parameters: Flowrate, Pressure, Temperature
- Properly formatted for CSV upload

## 🚀 Deployment Options

### Backend Deployment

**Render:**
- Connect GitHub repository
- Set build command: `pip install -r requirements.txt`
- Set start command: `gunicorn chemviz_backend.wsgi:application`
- Configure environment variables for database

**Heroku:**
- Use Heroku CLI: `heroku create`
- Set buildpacks: Python
- Push code: `git push heroku main`
- Configure environment variables

**DigitalOcean App Platform:**
- Create new app from GitHub
- Configure as Python web service
- Set environment variables and database

### Web Frontend Deployment

**Netlify:**
- Connect GitHub repository
- Set build command: `npm run build`
- Set publish directory: `dist`
- Configure environment variables

**Vercel:**
- Import project from GitHub
- Framework preset: React
- Configure environment variables
- Automatic deployment on push

**AWS S3 + CloudFront:**
- Build static files: `npm run build`
- Upload to S3 bucket
- Configure CloudFront distribution

### Desktop Application Distribution

**PyInstaller (Windows):**
```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

**cx_Freeze (Cross-platform):**
```bash
pip install cx_freeze
python setup.py build
```

## 🔧 Development

### Running Full Stack Locally

1. Start backend: `cd backend && python manage.py runserver`
2. Start web frontend: `cd web-frontend && npm run dev`
3. Start desktop app: `cd pyqt-app && python main.py`

### API Documentation

When backend is running, visit:
- `http://localhost:8000/api/` - API root
- `http://localhost:8000/admin/` - Django admin
- `http://localhost:8000/api/docs/` - API documentation (if configured)

### Architecture Details

For detailed architecture information, see:
- `docs/ARCHITECTURE.md` - Complete system overview
- `backend/` - Django API implementation
- `web-frontend/src/api/` - React API client
- `pyqt-app/api_client.py` - PyQt5 API client

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make your changes
4. Add tests if applicable
5. Submit pull request

## 📄 License

This project is part of the Chemical Equipment Parameter Visualizer system.

## 🆘 Support

For issues and questions:
1. Check the documentation in `docs/ARCHITECTURE.md`
2. Review sample data format in `docs/sample_equipment_data.csv`
3. Ensure all environment variables are properly configured
4. Verify backend API is accessible from frontend applications
