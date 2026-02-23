# Application Features

ChemViz provides a robust suite of tools designed to streamline the analysis of chemical equipment data. Below is a detailed breakdown of the core features.

## 1. Secure Data Management
- **User Authentication**: Secure registration and login flows using token-based authentication.
- **Data Isolation**: Each user's datasets are isolated and secure; you only see the data you uploaded.
- **Session Continuity**: Seamlessly pick up where you left off across login sessions.

## 2. Intelligent Data Ingestion
- **CSV Processing**: Upload raw `.csv` files containing equipment logs.
- **Format Validation**: The backend automatically validates that required columns (e.g., Equipment Name, Type, Flowrate, Pressure, Temperature) exist and data types are correct before processing.
- **Pandas Integration**: High-performance parsing and data structuring leveraging the Pandas library.

## 3. Advanced Statistical Analysis
- **Automated Metrics**: Instantly calculates averages, standard deviations, and identifies min/max outliers across all numerical columns.
- **Equipment Profiling**: Summarizes the total number of items, categorizes equipment by type, and calculates the overall health of the dataset.

## 4. AI-Powered Insights (Google Gemini)
- **Contextual Recommendations**: Sends statistical summaries to the Google Gemini API to return natural-language maintenance recommendations.
- **Anomaly Detection**: The AI highlights specific data points (e.g., unusually high pressure readings) that require immediate engineer attention.
- **Model Fallbacks**: Intelligently cycles between Gemini model versions (flash, pro) to ensure uptime during API rate limits.

## 5. Interactive Visualizations
- **Dynamic Charts**: Powered by Chart.js, datasets are visualized as interactive bar charts, line graphs, and scatter plots.
- **Responsive Design**: Dashboards automatically adjust layout whether viewed on a desktop monitor or mobile device.
- **Glassmorphism Aesthetic**: A modern, premium UI standard utilizing translucent components and clean typography.

## 6. Professional Exporting
- **PDF Report Generation**: Consolidate analysis, statistics, and AI recommendations into a polished, downloadable PDF.
- **ReportLab Integration**: Documents are constructed server-side, ensuring crisp formatting suitable for enterprise stakeholders.

## 7. Operational Robustness
- **CI/CD Integrated**: Automated pipeline pushing updates seamlessly to production servers.
- **Environment Driven Settings**: Secure segregation of secrets and variables between local and production environments.
