$ErrorActionPreference = "Stop"

$Source = Split-Path -Parent $MyInvocation.MyCommand.Path
$InstallDir = Join-Path $env:LOCALAPPDATA "DirectDrop"
$TaskName = "DirectDrop Background Agent"

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Get-ChildItem -Path $Source -Force |
  Where-Object { $_.Name -notin @(".git", ".venv", "build", "dist") } |
  Copy-Item -Destination $InstallDir -Recurse -Force

$Py = Get-Command py.exe -ErrorAction SilentlyContinue
if ($Py) {
    & $Py.Source -m venv (Join-Path $InstallDir ".venv")
} else {
    $Python = (Get-Command python.exe -ErrorAction Stop).Source
    & $Python -m venv (Join-Path $InstallDir ".venv")
}

$VenvPython = Join-Path $InstallDir ".venv\Scripts\python.exe"
$VenvPythonW = Join-Path $InstallDir ".venv\Scripts\pythonw.exe"
$Requirements = Join-Path $InstallDir "requirements.txt"
$RunPy = Join-Path $InstallDir "run.py"

& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r $Requirements

$Action = '"' + $VenvPythonW + '" "' + $RunPy + '" --agent'
schtasks.exe /Create /TN $TaskName /SC ONLOGON /TR $Action /F | Out-Null
Start-Process -FilePath $VenvPythonW -ArgumentList @($RunPy, "--agent") -WindowStyle Hidden

Write-Host "DirectDrop installed."
Write-Host "The background agent starts automatically at Windows logon."
Write-Host "USB-C must expose a supported USB networking interface."
