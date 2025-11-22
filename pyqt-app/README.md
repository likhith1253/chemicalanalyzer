# PyQt Desktop App Configuration

This file configures the desktop application settings.

## API Configuration

The desktop app connects to the same backend as the web app:
- **Production**: `https://chemicalanalyzer.onrender.com/api`
- **Local Development**: `http://127.0.0.1:8000/api`

## Usage

Edit `config.json` to switch between production and local:

```json
{
    "api": {
        "base_url": "https://chemicalanalyzer.onrender.com/api",
        "timeout": 30
    }
}
```

For local development, change `base_url` to `http://127.0.0.1:8000/api`.

## Running the Desktop App

```powershell
.\run_desktop_app.ps1
```

This will:
1. Create/activate virtual environment
2. Install dependencies (PyQt5, matplotlib, etc.)
3. Launch the desktop application

## Features

- Same backend API as web app
- Token-based authentication
- Upload CSV files
- View data tables and charts
- Generate PDF reports
- System tray integration

## Troubleshooting

**"Connection refused" error:**
- Check that backend is running (either locally or on Render)
- Verify `config.json` has correct `base_url`

**"Login failed" error:**
- Use same credentials as web app
- Make sure backend API is accessible

**Missing dependencies:**
- Run: `pip install -r requirements.txt`
