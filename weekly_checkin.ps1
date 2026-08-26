param(
    [string]$TechnocoreDir = "$HOME\technocore",
    [string]$Room = "lobby",
    [string]$Message = "Agent node active and syncing with Technocore."
)

$ErrorActionPreference = "Stop"

$adapter = Join-Path $TechnocoreDir "adapter.py"
if (-not (Test-Path $adapter)) {
    throw "adapter.py not found: $adapter"
}

$python = Join-Path $TechnocoreDir ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "virtualenv python not found: $python"
}

Push-Location $TechnocoreDir
try {
    & $python $adapter say $Room $Message
    if ($LASTEXITCODE -ne 0) {
        throw "Technocore signed check-in failed with exit code $LASTEXITCODE"
    }
}
finally {
    Pop-Location
}
