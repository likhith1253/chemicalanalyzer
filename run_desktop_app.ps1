$ErrorActionPreference = "Stop"

Write-Host "Setting up ChemViz Desktop App..."

$venvPath = ".\pyqt-app\venv"
$reqPath = ".\pyqt-app\requirements.txt"
$mainPath = ".\pyqt-app\main.py"

# 1. Create Virtual Environment if it doesn't exist
if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..."
    python -m venv $venvPath
}

# 2. Activate Virtual Environment
Write-Host "Activating virtual environment..."
& "$venvPath\Scripts\Activate.ps1"

# 3. Install Dependencies
if (Test-Path $reqPath) {
    Write-Host "Installing dependencies..."
    pip install -r $reqPath
} else {
    Write-Error "requirements.txt not found at $reqPath"
}

# 4. Run Application
Write-Host "Starting application..."
python $mainPath

Write-Host "Application finished."
Read-Host "Press Enter to exit..."
