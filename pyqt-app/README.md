# ChemViz - PyQt5 Desktop Application

A desktop application for visualizing and analyzing chemical equipment parameters from CSV data, integrated with Django REST API.

## Features

- **User Authentication**: Login with Django REST API using token-based authentication
- **CSV Upload**: Upload CSV files to the backend for processing
- **Data Visualization**: Interactive charts showing equipment type distribution
- **Dataset Management**: View and manage historical datasets
- **PDF Reports**: Download PDF reports for datasets
- **Modern UI**: Glassmorphism design with responsive layout

## Requirements

- Python 3.7+
- PyQt5
- matplotlib
- requests
- numpy

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API settings:
Edit `config.json` to match your Django backend URL:
```json
{
  "api": {
    "base_url": "http://localhost:8000/api",
    "timeout": 30
  }
}
```

## Usage

1. Make sure your Django backend is running on the configured URL
2. Run the application:
```bash
python main.py
```

3. Login with your Django credentials
4. Upload CSV files, view datasets, and generate reports

## Project Structure

```
pyqt-app/
├── main.py                 # Application entry point
├── api_client.py           # Django REST API client
├── config.json             # Configuration file
├── requirements.txt        # Python dependencies
├── widgets/
│   ├── __init__.py
│   ├── login_window.py     # Login window
│   └── main_window.py      # Main dashboard window
└── README.md              # This file
```

## API Integration

The application integrates with the following Django REST API endpoints:

- `POST /auth/login/` - User authentication
- `POST /upload/` - CSV file upload
- `GET /datasets/` - List datasets
- `GET /datasets/<id>/` - Get dataset details
- `GET /datasets/<id>/report/pdf/` - Download PDF report

## Development

### Adding New Features

1. Add new API methods to `api_client.py`
2. Update UI components in `widgets/` directory
3. Test with running Django backend

### Configuration

The application reads configuration from `config.json`:

- `api.base_url`: Django backend API URL
- `api.timeout`: Request timeout in seconds

## Troubleshooting

### Common Issues

1. **Connection Error**: Ensure Django backend is running and URL is correct
2. **Authentication Error**: Check credentials and token configuration
3. **Import Error**: Install all requirements from `requirements.txt`

### Debug Mode

To enable debug logging, modify `api_client.py` to print debug information.

## License

This project is part of the ChemViz chemical equipment parameter visualizer system.
