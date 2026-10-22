# Data Flow Pipeline

This document outlines the step-by-step journey of data as it passes through the ChemViz system, from user upload to final report generation.



## 1. Data Ingestion (React -> Django)

The user begins by uploading a CSV file through the React frontend wrapper component.
- The `Upload.jsx` component wraps the file into a `multipart/form-data` payload.
- An Axios POST request, authenticated via header tokens, sends the file to the Django `/api/upload/` endpoint.

## 2. Validation & Parsing (Django -> Pandas)

Once the file reaches the backend, the processing pipeline begins:
- **Sanity Checks**: File extension validation and size checks are performed.
- **Pandas DataFrame**: The CSV is loaded into memory as a Pandas DataFrame, which expects columns such as `Equipment Name`, `Type`, `Flowrate`, `Pressure`, and `Temperature`.
- **Typing Verification**: Pandas ensures numeric columns are treated as floats, dropping or flagging malformed rows.

## 3. Storage (Django ORM -> PostgreSQL)

To prevent data loss and enable historic analysis, the data is persisted:
- **Dataset Initialization**: A `Dataset` instance is created and linked via ForeignKey to the authenticated `User`.
- **Bulk Creation**: The validated DataFrame is converted into a list of model instances, and a bulk insert writes all rows concurrently to the `Equipment` table in PostgreSQL.

## 4. Execution of Analysis (Pandas)

Before returning a response to the user, background statistical calculations occur:
- Metrics such as `mean`, `standard deviation`, `min`, and `max` are vectorized across the numerical columns using Pandas' native, highly optimized functions.
- These computed statistics are serialized as a JSON string and saved directly onto the `Dataset` record caching them for future requests.

## 5. AI Reasoning Generation (Django -> Gemini API)

If the user requests AI insights:
- The backend retrieves the cached JSON statistics.
- A carefully crafted prompt string, embedding these statistics, is sent securely to the Google Gemini endpoint.
- The returned AI-generated insights—covering maintenance priorities and system anomalies—are saved to the database to prevent redundant API calls.

## 6. Presentation layer (Backend API -> React)

- Data is requested via `GET` calls to `/api/datasets/{id}/`.
- The Django REST Framework serializes the dataset alongside its computed statistics.
- The React frontend receives this payload and passes the values down as props to `Chart.js` components for dynamic rendering.

## 7. Exporting (Django -> ReportLab)

When the user requests a physical download:
- A separate endpoint (`/api/datasets/{id}/report/pdf/`) triggers a ReportLab routine.
- The system reads the raw data, cached metrics, and AI recommendations.
- A virtual buffer (`BytesIO`) constructs the PDF document entirely in-memory.
- The binary PDF stream is returned directly in the HTTP response matching standard browser attachment protocols.
