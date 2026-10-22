# How to Use ChemViz

Welcome to ChemViz! This guide will walk you through the process of analyzing your chemical equipment data using our platform.

## 1. Creating an Account
Before you can analyze data, you need to create a secure account. This ensures your datasets remain private and accessible only to you.
1. Navigate to the **Home** page.
2. Click on **Get Started** or **Register**.
3. Enter a unique username and a secure password.

## 2. Preparing Your Data
ChemViz requires your equipment data to be in a specific CSV (Comma Separated Values) format.

### Expected Input Format
Your CSV file must include a header row and contain the following columns:

| Column | Type | Description |
|--------|------|-------------|
| **Equipment Name** | Text | A unique identifier for the equipment (e.g., "Pump-A01"). |
| **Type** | Text | The category of the equipment (e.g., "Pump", "Valve"). |
| **Flowrate** | Number | Flowrate measured in Liters per minute. |
| **Pressure** | Number | Pressure measured in bar. |
| **Temperature** | Number | Temperature measured in °C. |


*(See `docs/sample_equipment_data.csv` in the repository for a working example).*

## 3. Uploading a Dataset
1. Log in to your account.
2. Navigate to the **Upload** page.
3. Click **Choose File** and select your prepared CSV file.
4. Click **Upload**. The system will validate your data and process it instantly.

## 4. Viewing Results & AI Insights
Once uploaded, you will be redirected to the **Dataset Details** page. Here you can:
- **View Interactive Charts**: Hover over the bar charts and scatter plots to see specific readings for each piece of equipment.
- **Review Statistics**: Check the top-level averages and extremes calculated across your dataset.
- **Generate AI Insights**: Click the **Analyze with AI** button. Our Google Gemini integration will read your statistics and provide natural-language maintenance recommendations and flag potential anomalies.

## 5. Exporting Your Report
Need to share the results with your team?
1. On the Dataset Details page, locate the **Download PDF** button.
2. Click it to generate a professional, formatted report containing your statistics, equipment list, and AI insights.
3. The report will download directly to your device.
