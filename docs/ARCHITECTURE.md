# ChemViz Architecture Documentation

## Overview

ChemViz is a three-tier application for visualizing and analyzing chemical equipment parameters. The system consists of a Django REST API backend, a React web frontend, and a PyQt5 desktop frontend, all communicating through a shared REST API.

## Backend (Django REST API)

### Role
The backend serves as the central data processing and storage layer, providing RESTful API endpoints for all frontend applications.

### Key Responsibilities
- **Authentication**: Token-based user authentication using Django REST Framework
- **Data Processing**: CSV file parsing, validation, and storage
- **Data Analysis**: Statistical calculations (averages, counts, distributions)
- **Report Generation**: PDF report creation using ReportLab
- **API Endpoints**: RESTful services for all operations

### Core Components
- **Models**: `EquipmentDataset` for storing processed data
- **Serializers**: Data validation and API response formatting
- **Views**: API endpoint logic and business rules
- **Services**: Data processing and PDF generation utilities

### API Endpoints
```
POST /api/auth/login/          # User authentication
POST /api/upload/              # CSV file upload
GET  /api/datasets/            # List all datasets
GET  /api/datasets/<id>/       # Get dataset details
GET  /api/datasets/<id>/report/pdf/  # Download PDF report
```

## Web Frontend (React)

### Role
The web frontend provides a modern, browser-based interface for users to interact with the ChemViz system.

### Key Responsibilities
- **User Interface**: Modern glassmorphism design with responsive layout
- **Authentication**: Login/logout functionality with token management
- **File Upload**: Drag-and-drop CSV upload with progress tracking
- **Data Visualization**: Interactive charts using Chart.js
- **Dataset Management**: Browse, view, and manage datasets
- **Report Download**: PDF report generation and download

### Core Technologies
- **React 18**: Component-based UI framework
- **Vite**: Fast development build tool
- **Chart.js**: Data visualization library
- **Axios**: HTTP client with authentication interceptors
- **TailwindCSS**: Utility-first CSS framework

### Key Features
- Real-time data updates
- Loading states and error handling
- Responsive design for all screen sizes
- Token-based authentication with localStorage
- Interactive charts and data tables

## Desktop Frontend (PyQt5)

### Role
The desktop frontend provides a native desktop application experience with offline capabilities and system integration.

### Key Responsibilities
- **Native Interface**: Desktop-optimized UI with system integration
- **Authentication**: Secure login with token management
- **File Management**: Direct file system access for CSV uploads
- **Data Visualization**: Matplotlib charts for data analysis
- **Local Storage**: Configuration and preference management
- **PDF Handling**: Direct file system access for report downloads

### Core Technologies
- **PyQt5**: Cross-platform GUI framework
- **Matplotlib**: Scientific plotting and visualization
- **Requests**: HTTP client library
- **JSON**: Configuration management

### Key Features
- Native desktop performance
- File dialog integration
- Progress tracking for uploads
- Async API calls with worker threads
- Modern glassmorphism styling

## System Interaction

### Communication Flow
```
Frontend (React/PyQt5) → HTTP/HTTPS → Django REST API → Database
```

### Authentication Flow
1. User submits credentials to frontend
2. Frontend sends POST request to `/api/auth/login/`
3. Backend validates credentials and returns auth token
4. Frontend stores token (localStorage/memory) and includes in all subsequent requests
5. Backend validates token on each API call

### Data Flow
1. **Upload**: Frontend → POST `/api/upload/` → Backend processes CSV → Database
2. **Retrieve**: Frontend → GET `/api/datasets/` → Backend queries → JSON response
3. **Visualization**: Frontend receives data → Renders charts/tables
4. **Reports**: Frontend → GET `/api/datasets/<id>/report/pdf/` → Backend generates PDF → Download

### Shared API Contract
Both frontends use the same REST API endpoints, ensuring:
- **Consistency**: Same data format across platforms
- **Maintainability**: Single backend to maintain
- **Scalability**: Multiple frontends can use same backend
- **Flexibility**: Easy to add new frontend platforms

## Data Architecture

### CSV Processing Pipeline
```
CSV File → Upload → Validation → Processing → Storage → Analysis → Visualization
```

### Data Storage
- **Raw Data**: Original CSV content stored in database
- **Processed Data**: Parsed equipment records with metadata
- **Analysis Results**: Pre-calculated statistics for fast retrieval
- **User Data**: Authentication tokens and user preferences

### Response Formats
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

## Security Considerations

### Authentication
- Token-based authentication with Django REST Framework
- Tokens stored securely (localStorage for web, memory for desktop)
- Automatic token refresh and validation

### Data Validation
- Server-side CSV validation and sanitization
- File type restrictions and size limits
- Input validation on all API endpoints

### CORS Configuration
- Proper CORS settings for web frontend
- Secure origin validation
- Development vs production configuration

## Deployment Architecture

### Development
```
Django Backend (localhost:8000)
├── React Frontend (localhost:5173)
└── PyQt5 Desktop (local application)
```

### Production
```
Django Backend (production server)
├── React Frontend (static files on CDN/web server)
└── PyQt5 Desktop (distributed application)
```

## Benefits of This Architecture

### Scalability
- Backend can serve multiple frontend types
- Easy to add new client applications
- Horizontal scaling of backend services

### Maintainability
- Single source of truth for data processing
- Shared API contract reduces duplication
- Separation of concerns across tiers

### User Experience
- Choice of web or desktop interface
- Consistent functionality across platforms
- Native performance on desktop, web accessibility online

### Development Efficiency
- Parallel development of frontends
- Shared testing and validation
- Reusable backend components
