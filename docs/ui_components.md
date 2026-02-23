# UI Components & Page Structure

The React frontend of ChemViz is composed of several key pages and reusable UI components designed to provide a cohesive, modern user experience using a glassmorphism design language.

![Home Screen UI](images/ui_screenshot_home.png)

## Core Pages

### 1. The Dashboard (`Home.jsx` / `Dashboard.jsx`)
The entry point for authenticated users. It provides an immediate overview of their data.
- **SummaryCards**: Reusable components displaying KPI metrics (e.g., Total Datasets, Uploads this week) utilizing translucent `backdrop-filter` CSS effects.
- **DatasetCard Grid**: A responsive grid rendering individual `DatasetCard.jsx` components. Each card displays preview metadata (date uploaded, item count) and acts as an interactive link to the detailed view.

### 2. The Upload Page (`Upload.jsx`)
The interface for data ingestion.
- Features a drag-and-drop or click-to-select file input specifically tailored for `.csv` files.
- Includes visual loading states and toast notifications (via `react-hot-toast`) to provide immediate feedback during backend validation and processing.

### 3. The Dataset Details Page (`DatasetDetail.jsx`)
The analytical hub for a specific dataset.
- **Interactive Charts**: Embeds `react-chartjs-2` canvas elements. Bar charts compare flowrates across equipment, while scatter plots correlate pressure and temperature.
- **AI Insights Panel**: A dedicated section that displays the natural-language recommendations fetched from the Gemini AI, complete with a call-to-action button to trigger the analysis if it hasn't been cached yet.
- **Export Controls**: A prominent "Download PDF" button that triggers the ReportLab generation on the backend.

![Dataset Details UI](images/ui_screenshot_output.png)

## Reusable UI Elements

- **Navigation (`Navigation.jsx`)**: A responsive top app bar that handles routing and authentication state (showing Login/Register vs Dashboard/Logout).
- **Form Controls**: Standardized input fields and buttons infused with hover animations and focus rings for accessibility and aesthetics.
- **Loading Spinners**: Deployed across components to mask network latency during API calls or AI generation.
