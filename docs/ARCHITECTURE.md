# Chemical Equipment Analyzer Architecture

## Overview

This is a three-tier application for analyzing chemical equipment data. It has a Django REST API backend, a React web frontend, and a PyQt5 desktop application that all talk to the same API.

## Backend (Django REST API)

### What it does
The backend handles data processing and storage, providing API endpoints for the frontends.

### Main tasks
- Authentication with tokens
- CSV file parsing and validation
- Data analysis (averages, counts, distributions)
- PDF report generation
- API endpoints for all operations

### Core parts
- Models: EquipmentDataset for storing data
- Serializers: Data validation and API formatting
- Views: API endpoint logic
- Services: Data processing and PDF utilities

### API endpoints
```
POST /api/auth/login/          # User login
POST /api/upload/              # CSV upload
GET  /api/datasets/            # List datasets
GET  /api/datasets/<id>/       # Get dataset details
GET  /api/datasets/<id>/report/pdf/  # Download PDF
```

## Web Frontend (React)

### What it does
The web frontend provides a browser interface for users.

### Main tasks
- User interface with modern design
- Login/logout with token management
- CSV upload with progress tracking
- Data visualization with charts
- Dataset management
- PDF report downloads

### Technologies used
- React 18 for UI components
- Vite for building
- Chart.js for charts
- Axios for API calls
- TailwindCSS for styling

### Features
- Real-time data updates
- Loading and error states
- Responsive design
- Token authentication with localStorage
- Interactive charts and tables

## Desktop Frontend (PyQt5)

### What it does
The desktop frontend provides a native application with offline capabilities.

### Main tasks
- Native desktop interface
- Authentication with token management
- CSV file uploads from file system
- Data visualization with Matplotlib
- Local configuration storage
- PDF report downloads

### Technologies used
- PyQt5 for GUI
- Matplotlib for charts
- Requests for HTTP calls
- JSON for configuration

### Features
- Native desktop performance
- File dialog integration
- Upload progress tracking
- Async API calls
- Modern styling

## System Interaction

### Communication
```
Frontend (React/PyQt5) → HTTP/HTTPS → Django REST API → Database
```

### Authentication flow
1. User enters credentials in frontend
2. Frontend sends POST to /api/auth/login/
3. Backend validates and returns auth token
4. Frontend stores token and uses it for requests
5. Backend validates token on each call

### Data flow
1. Upload: Frontend → POST /api/upload/ → Backend processes CSV → Database
2. Retrieve: Frontend → GET /api/datasets/ → Backend queries → JSON response
3. Visualization: Frontend gets data → Renders charts/tables
4. Reports: Frontend → GET /api/datasets/<id>/report/pdf/ → Backend generates PDF → Download

### Shared API
Both frontends use the same REST API:
- Consistent data format
- Single backend to maintain
- Scalable to multiple frontends
- Easy to add new platforms

## Data Architecture

### CSV processing
```
CSV File → Upload → Validation → Processing → Storage → Analysis → Visualization
```

### Data storage
- Raw CSV content in database
- Parsed equipment records
- Pre-calculated statistics
- User authentication data

### Response formats
```json
// Dataset List
{
  "results": [
    {
      "id": 1,
      "name": "equipment_data_2024_01_15",
      "uploaded_at": "2024-01-15T10:30:00Z",
      "total_count": 150
    }
  ]
}

// Dataset Detail
{
  "id": 1,
  "name": "equipment_data_2024_01_15",
  "total_count": 150,
  "avg_flowrate": 156.7,
  "avg_pressure": 2.6,
  "avg_temperature": 87.3,
  "type_distribution": {
    "Pump": 45,
    "Valve": 38,
    "Reactor": 32,
    "Column": 35
  },
  "preview_rows": [...]
}
```

## Security

### Authentication
- Token-based authentication with Django REST Framework
- Tokens stored securely (localStorage for web, memory for desktop)
- Token refresh and validation

### Data validation
- Server-side CSV validation
- File type and size limits
- Input validation on all endpoints

### CORS
- Proper CORS settings for web frontend
- Secure origin validation
- Different configs for dev/prod

## Deployment

### Development setup
```
Django Backend (localhost:8000)
├── React Frontend (localhost:5173)
└── PyQt5 Desktop (local app)
```

### Production setup
```
Django Backend (production server)
├── React Frontend (static files on web server)
└── PyQt5 Desktop (distributed app)
```

## Why this architecture

### Scalability
- Backend serves multiple frontend types
- Easy to add new clients
- Can scale backend services

### Maintainability
- Single source of truth for data
- Shared API reduces duplication
- Clear separation of concerns

### User experience
- Choice of web or desktop
- Consistent functionality
- Native desktop performance, web accessibility

### Development efficiency
- Parallel frontend development
- Shared testing
- Reusable backend components
