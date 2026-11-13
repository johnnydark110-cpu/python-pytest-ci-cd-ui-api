$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$pythonExe = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

& $pythonExe -m uvicorn app.backend.main:app --host 127.0.0.1 --port 8000 --reload
