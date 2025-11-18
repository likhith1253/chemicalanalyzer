# Backend Setup Documentation

## Final Folder Structure

```
backend/
├── chemviz_backend/          # Django project
│   ├── __init__.py
│   ├── settings.py           # Django settings with DRF, CORS, TokenAuth
│   ├── urls.py               # Main URL configuration
│   ├── wsgi.py
│   └── asgi.py
├── equipment/                 # Main Django app
│   ├── __init__.py
│   ├── models.py             # Dataset and Equipment models
│   ├── views.py              # All API views (auth, upload, datasets, PDF)
│   ├── serializers.py        # DRF serializers
│   ├── urls.py               # App URL patterns
│   ├── services.py            # Pandas CSV analysis functions
│   ├── pdf_utils.py          # ReportLab PDF generation
│   ├── admin.py              # Django admin configuration
│   └── utils.py              # Utility functions
├── media/                     # Uploaded files storage
│   └── uploads/              # CSV files stored here
├── tests/                     # Test suite
├── manage.py                  # Django management script
├── db.sqlite3                 # SQLite database
├── requirements.txt           # Python dependencies
└── .env.example              # Environment variables template
```

## Environment Variables (.env.example)

Create a `.env` file in the `backend/` directory with:

```env
# Django Settings
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (SQLite is default, no config needed)
# For PostgreSQL, uncomment and configure:
# DATABASE_NAME=chemviz_db
# DATABASE_USER=your_user
# DATABASE_PASSWORD=your_password
# DATABASE_HOST=localhost
# DATABASE_PORT=5432
```

## API Documentation

### Base URL
All endpoints are prefixed with `/api/`

### Authentication

All endpoints (except register/login) require authentication via:
- **Token Authentication**: `Authorization: Token <your-token>`
- **Session Authentication**: Django session
- **Basic Authentication**: HTTP Basic Auth

### Endpoints

#### 1. User Registration
- **URL**: `POST /api/auth/register/`
- **Auth**: Not required
- **Request Body**:
  ```json
  {
    "username": "string",
    "email": "string (optional)",
    "password": "string (min 8 chars)",
    "password_confirm": "string"
  }
  ```
- **Response** (201):
  ```json
  {
    "message": "User registered successfully",
    "user": {
      "id": 1,
      "username": "string",
      "email": "string",
      "token": "authentication-token"
    }
  }
  ```

#### 2. User Login
- **URL**: `POST /api/auth/login/`
- **Auth**: Not required
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response** (200):
  ```json
  {
    "message": "Login successful",
    "token": "authentication-token",
    "user": {
      "id": 1,
      "username": "string",
      "email": "string"
    }
  }
  ```

#### 3. Upload CSV Dataset
- **URL**: `POST /api/upload/`
- **Auth**: Required (Token)
- **Content-Type**: `multipart/form-data`
- **Request Body**:
  - `file`: CSV file (required)
  - `name`: Dataset name (optional, defaults to timestamp)
- **Response** (201):
  ```json
  {
    "message": "Dataset uploaded and analyzed successfully",
    "data": {
      "id": 1,
      "name": "Dataset Name",
      "original_filename": "equipment.csv",
      "uploaded_by": "username",
      "uploaded_at": "2024-01-01 12:00:00",
      "total_count": 150,
      "avg_flowrate": 25.5,
      "avg_pressure": 10.2,
      "avg_temperature": 75.3,
      "type_distribution": {
        "Pump": 50,
        "Valve": 30,
        "Tank": 70
      },
      "preview_rows": [
        {
          "equipment_name": "Pump-001",
          "type": "Pump",
          "flowrate": 25.5,
          "pressure": 10.2,
          "temperature": 75.3
        },
        ...
      ],
      "equipment": [...]
    }
  }
  ```

#### 4. List Datasets
- **URL**: `GET /api/datasets/`
- **Auth**: Required (Token)
- **Response** (200):
  ```json
  [
    {
      "id": 1,
      "name": "Dataset Name",
      "original_filename": "equipment.csv",
      "uploaded_by": "username",
      "uploaded_at": "2024-01-01 12:00:00",
      "total_count": 150,
      "avg_flowrate": 25.5,
      "avg_pressure": 10.2,
      "avg_temperature": 75.3,
      "type_distribution": {
        "Pump": 50,
        "Valve": 30,
        "Tank": 70
      }
    },
    ...
  ]
  ```
- **Note**: Returns last 5 datasets only (auto-pruned)

#### 5. Get Dataset Detail
- **URL**: `GET /api/datasets/<id>/`
- **Auth**: Required (Token)
- **Response** (200):
  ```json
  {
    "id": 1,
    "name": "Dataset Name",
    "original_filename": "equipment.csv",
    "uploaded_by": "username",
    "uploaded_at": "2024-01-01 12:00:00",
    "total_count": 150,
    "avg_flowrate": 25.5,
    "avg_pressure": 10.2,
    "avg_temperature": 75.3,
    "type_distribution": {
      "Pump": 50,
      "Valve": 30,
      "Tank": 70
    },
    "preview_rows": [
      {
        "equipment_name": "Pump-001",
        "type": "Pump",
        "flowrate": 25.5,
        "pressure": 10.2,
        "temperature": 75.3
      },
      ...
    ],
    "equipment": [...]
  }
  ```
- **Note**: `preview_rows` contains first 100 rows

#### 6. Generate PDF Report
- **URL**: `GET /api/datasets/<id>/report/pdf/`
- **Auth**: Required (Token)
- **Response**: PDF file download
- **Content-Type**: `application/pdf`
- **Filename**: `dataset_<id>_report.pdf`

### CSV File Format

Required columns (case-insensitive, spaces/underscores flexible):
- `equipment_name` (or `Equipment Name`, `equipmentname`)
- `type` (or `Type`, `equipment_type`)
- `flowrate` (or `Flowrate`, `flow_rate`, `Flow`)
- `pressure` (or `Pressure`)
- `temperature` (or `Temperature`, `temp`)

## Commands to Run Backend

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Environment

```bash
# Create .env file from template
cp .env.example .env
# Edit .env with your settings
```

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 5. Run Development Server

```bash
python manage.py runserver
```

Server will start at `http://localhost:8000/`

### 6. Run Tests (Optional)

```bash
pytest
# or
python manage.py test
```

## Key Features Implemented

✅ **Django + DRF + SQLite**: Full Django REST Framework setup
✅ **CSV Upload**: Multipart form-data file upload
✅ **Pandas CSV Parsing**: Robust CSV analysis with column normalization
✅ **Summary Computation**: 
   - total_count
   - avg_flowrate
   - avg_pressure
   - avg_temperature
   - type_distribution
✅ **Database Storage**: Dataset and Equipment models
✅ **Auto-pruning**: Keeps only last 5 datasets (deletes older ones)
✅ **Authentication**: 
   - POST /api/auth/register/
   - POST /api/auth/login/
   - TokenAuthentication
✅ **Dataset APIs**:
   - POST /api/upload/
   - GET /api/datasets/
   - GET /api/datasets/<id>/
   - GET /api/datasets/<id>/report/pdf/
✅ **PDF Generation**: ReportLab with dataset summary
✅ **CORS Enabled**: Configured for cross-origin requests
✅ **Preview Rows**: First 100 rows in detail view

## Technical Details

### Models
- **Dataset**: Stores CSV metadata, statistics, and file reference
- **Equipment**: Stores individual equipment records from CSV

### Services
- **analyze_equipment_csv_from_uploaded_file()**: Pandas-based CSV analysis
- **normalize_column_name()**: Flexible column name matching

### PDF Generation
- Uses ReportLab to generate professional PDF reports
- Includes dataset info, statistics, type distribution, and sample records

### Auto-pruning Logic
- After saving a new dataset, automatically deletes datasets beyond the 5 most recent
- Deletes both database records and associated CSV files

## Troubleshooting

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify virtual environment is activated

### Database Errors
- Run migrations: `python manage.py migrate`
- Delete `db.sqlite3` and re-run migrations if needed

### File Upload Issues
- Check `MEDIA_ROOT` and `MEDIA_URL` in settings.py
- Ensure `media/` directory exists and is writable

### CORS Issues
- Verify `CORS_ALLOW_ALL_ORIGINS = True` in settings.py
- For production, configure `CORS_ALLOWED_ORIGINS` with specific domains

### Authentication Issues
- Verify token is included in request headers: `Authorization: Token <token>`
- Check that user is authenticated: `request.user.is_authenticated`

