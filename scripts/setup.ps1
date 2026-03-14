$ErrorActionPreference = 'Stop'

if (-not (Test-Path .venv)) {
    python -m venv .venv
}

.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-dev.txt

Write-Host '✅ Setup complete. Start with:'
Write-Host 'uvicorn backend.main:app --reload --port 8000'
