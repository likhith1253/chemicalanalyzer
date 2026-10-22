# ChemViz - Chemical Equipment Analyzer

Upload a CSV of chemical equipment readings (flowrate, pressure, temperature) and get summary statistics, a type-distribution chart, a downloadable PDF report and AI-generated maintenance notes from Google Gemini.

Live demo: [chemicalanalyzer.vercel.app](https://chemicalanalyzer.vercel.app) (the backend runs on a free Render instance, so the first request after idle can take a while).

## Components

| Directory | What it is |
|---|---|
| `backend/` | Django 5.2 + Django REST Framework API (token auth), pandas for CSV analysis, ReportLab for PDF reports, Gemini for insights |
| `web-frontend/` | React 18 + Vite single-page app (Chart.js / Recharts, axios) |
| `pyqt-app/` | Optional PyQt5 desktop client for the same API |
| `docs/` | Setup, deployment, features and architecture notes |

## CSV format

Required columns (case-insensitive, common variants such as `Flow Rate` are accepted): `Equipment Name`, `Type`, `Flowrate`, `Pressure`, `Temperature`. A sample is in [`docs/sample_equipment_data.csv`](docs/sample_equipment_data.csv).

## API overview

All endpoints except register/login require the header `Authorization: Token <token>`.

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/auth/register/`, `/api/auth/login/` | Returns `{token, username}` (rate limited) |
| POST | `/api/auth/logout/` | Deletes the caller's token |
| GET | `/api/auth/profile/` | Current user |
| POST | `/api/upload/` | Upload a CSV (`.csv`, max 10 MB) |
| GET | `/api/datasets/` | The caller's last 5 datasets |
| GET | `/api/datasets/<id>/` | Dataset detail with preview rows |
| GET | `/api/datasets/<id>/report/pdf/` | PDF report |
| GET | `/api/datasets/<id>/analyze/` | Gemini insights (needs `GOOGLE_GEMINI_API_KEY`) |

Datasets are private to the user who uploaded them, and only the 5 most recent per user are kept.

## Run locally

```bash
# backend
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then set SECRET_KEY, DEBUG=True for local use, GOOGLE_GEMINI_API_KEY (optional)
python manage.py migrate
python manage.py runserver

# frontend (new terminal)
cd web-frontend
npm ci
echo "VITE_API_BASE_URL=http://localhost:8000/api" > .env.local
npm run dev
```

Details: [docs/setup.md](docs/setup.md). Deployment (Render + Vercel): [docs/deployment.md](docs/deployment.md).

`SECRET_KEY` is mandatory whenever `DEBUG` is off; the app refuses to start without it. There is no default admin account: create one with `python manage.py createsuperuser`, or set `ADMIN_USERNAME` / `ADMIN_PASSWORD` and run `python manage.py create_admin`.

## Tests

```bash
cd backend
pip install -r requirements-test.txt
pytest
```

90 tests (pytest-django): authentication, per-user dataset isolation, CSV upload validation (extension, size, binary content, path traversal), PDF generation, rate limiting, error-leakage and settings hardening. The frontend has no automated tests; CI (`.github/workflows/ci.yml`) runs the backend tests and the frontend build.

## Documentation

- [Setup](docs/setup.md), [Deployment](docs/deployment.md), [Features](docs/features.md), [User guide](docs/how_to_use.md), [UI components](docs/ui_components.md), [Architecture](docs/architecture.md), [Data flow](docs/data_flow.md)
- Personal development write-ups (narrative, not reference): [`docs/notes/`](docs/notes/)

## Known limitations

- Auth tokens do not expire (DRF `TokenAuthentication`); they are removed on logout.
- Uploaded CSV files are stored on the web instance's local disk, which is ephemeral on Render's free tier; the parsed data and statistics live in the database.
- `google-generativeai` is a deprecated Google SDK; migrating to the newer `google-genai` package is pending.

## License

[MIT](LICENSE) (c) Likhith Ponnada
