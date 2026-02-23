# Local Environment Setup

This guide provides step-by-step instructions for setting up the ChemViz project on your local machine for development and testing.

## Prerequisites

Before you begin, ensure you have the following installed on your system:
- **Python 3.11+**
- **Node.js 18+**
- **Git**
- **Google Gemini API Key** ([Get one here](https://aistudio.google.com/apikey))
- *(Optional but recommended)* PostgreSQL for local database parity with production.

---

## 1. Clone the Repository

Begin by cloning the source code to your machine:

```bash
git clone https://github.com/likhith1253/chemicalanalyzer
cd chemicalanalyzer
```

---

## 2. Backend Setup (Django)

The backend handles API requests, data processing with Pandas, and AI integration.

1. **Navigate to the backend directory and create a virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   ```

2. **Activate the virtual environment:**
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the `backend/` directory using the provided example:
   ```env
   GOOGLE_GEMINI_API_KEY=your_api_key_here
   DEBUG=True
   SECRET_KEY=your-secret-key-for-development
   # Omit DATABASE_URL to use the default SQLite database locally
   ```

5. **Initialize the Database:**
   Apply migrations to create the necessary tables:
   ```bash
   python manage.py migrate
   ```
   *(Optional)* Create an admin user to access the Django built-in admin panel:
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the Development Server:**
   ```bash
   python manage.py runserver
   ```
   The API will now be available at `http://localhost:8000/api`.

---

## 3. Frontend Setup (React)

The frontend is a React application built with Vite handling the user interface and data visualization.

1. **Open a new terminal window** (keep the backend server running) and navigate to the frontend directory:
   ```bash
   cd web-frontend
   ```

2. **Install Node modules:**
   ```bash
   npm install
   ```

3. **Configure Environment Variables:**
   Create a `.env` file in the `web-frontend/` directory (or copy `.env.example` if it exists):
   ```env
   VITE_API_BASE_URL=http://localhost:8000/api
   ```

4. **Start the Development Server:**
   ```bash
   npm run dev
   ```
   The frontend will now be available at `http://localhost:5173`.

---

## 4. Verification

1. Open your browser and navigate to `http://localhost:5173`.
2. Create a new test account using the application's registration page.
3. Upload the provided sample data located in `docs/sample_equipment_data.csv` to verify data processing and AI insights are functioning correctly.

---

## Troubleshooting

- **CORS Issues**: If the frontend cannot communicate with the backend, ensure your frontend URL (e.g., `http://localhost:5173`) is included in the `CORS_ALLOWED_ORIGINS` setting within `backend/chemviz_backend/settings.py`.
- **Database Errors**: If using PostgreSQL locally, ensure the service is running and your `DATABASE_URL` in the `.env` file is correct format (e.g., `postgres://user:password@localhost:5432/dbname`).
