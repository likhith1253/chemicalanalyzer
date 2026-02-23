# ChemViz - Chemical Equipment Analyzer

A full-stack web application built to analyze chemical equipment performance data using AI. It transforms raw CSV data into interactive charts and professional PDF reports, complete with actionable insights.

![Home Screen](docs/images/ui_screenshot_home.png)

🌐 **Live Demo**: [chemicalanalyzer.vercel.app](https://chemicalanalyzer.vercel.app)

## What It Does

ChemViz solves the problem of manual data analysis for chemical engineers by automating the processing of equipment logs (flowrate, pressure, temperature). Instead of spending hours in Excel, users can simply upload a dataset and instantly view statistical summaries, data distributions, and most importantly, AI-generated maintenance recommendations powered by Google Gemini.

### Example Workflow
**Input**: A CSV file with equipment readings (see [sample input format](docs/images/sample_input_format.png)).
**Output**: An interactive analytics dashboard and a detailed, downloadable [PDF report](docs/images/ui_screenshot_output.png).

## Tech Stack

| Layer | Technologies Used | Description |
|---|---|---|
| **Frontend** | React 18, Vite, Chart.js, Tailwind CSS | Modern, responsive SPA with glassmorphism design. |
| **Backend** | Django 4.2, Django REST Framework, Pandas | Robust API handling file processing and mathematics. |
| **AI Integration** | Google Gemini 2.5 API | Generates contextual, natural language insights. |
| **Database** | PostgreSQL | Production database hosted on Render. |
| **DevOps** | Vercel (Frontend), Render (Backend), GitHub Actions | Fully automated deployment pipeline. |

## Architecture Overview

ChemViz follows a standard decoupled full-stack architecture. The robust Django backend acts as the central data processing and intelligence hub, serving requests from the lightweight React frontend.

![Architecture Diagram](docs/images/architecture_diagram.png)

*For a detailed breakdown of the system components, see [Architecture Documentation](docs/architecture.md).*

## High-Level Data Flow

1. **User Upload**: A CSV file is uploaded via the React frontend.
2. **Backend Processing**: Django validates the file, and Pandas calculates statistical metrics.
3. **Database Insertion**: Raw data and computed metrics are stored in PostgreSQL.
4. **AI Analysis**: Google Gemini analyzes the metrics to generate maintenance recommendations.
5. **Presentation**: The frontend renders the results using Chart.js, or the user exports them via a ReportLab-generated PDF.

![Data Flow Diagram](docs/images/data_flow_diagram.png)

*For an in-depth look at the data pipeline, see [Data Flow Documentation](docs/data_flow.md).*

## Documentation Links

- [🔧 Setup Guide](docs/setup.md) - How to run the project locally.
- [✨ Features list](docs/features.md) - Detailed breakdown of what the application can do.
- [📖 User Guide](docs/how_to_use.md) - Step-by-step instructions for end-users.
- [🖥️ UI Components](docs/ui_components.md) - Explanations of the different pages and visuals.
- [🚀 Deployment](docs/deployment.md) - Instructions for pushing to production.
- [🏗️ Architecture](docs/architecture.md) - Deep dive into the system design.
- [🔄 Data Flow](docs/data_flow.md) - How data moves through the app.

## Future Enhancements
- Real-time collaboration on datasets.
- Export to Excel format.
- Historical trend analysis across datasets.
- Email notifications for analysis completion.
- API rate limiting and Redis caching.

## Contact

Built by Likhith.
- **Source Code**: [GitHub](https://github.com/likhith1253/chemicalanalyzer)
- Questions or want to discuss the implementation? Feel free to reach out via GitHub!
