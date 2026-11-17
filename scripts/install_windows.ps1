$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$installRoot = Join-Path $env:LOCALAPPDATA "KnowledgeVaultAI"
$venvPath = Join-Path $installRoot ".venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"

New-Item -ItemType Directory -Force -Path $installRoot | Out-Null

$pythonCommand = Get-Command py -ErrorAction SilentlyContinue
if ($pythonCommand) {
    & py -3 -m venv $venvPath
}
else {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCommand) {
        throw "Python 3.10 or newer was not found. Install Python from https://python.org and run this script again."
    }
    & python -m venv $venvPath
}

& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install $projectRoot

Write-Host ""
Write-Host "Knowledge Vault AI installed successfully."
Write-Host "Run it with:"
Write-Host "  & '$venvPython' -m streamlit run '$projectRoot\knowledge_vault\ui\app.py'"
