$ErrorActionPreference = "Stop"

try {
    $Source = Split-Path -Parent $MyInvocation.MyCommand.Path
    $InstallDir = Join-Path $env:LOCALAPPDATA "DirectDrop"
    $TaskName = "DirectDrop Background Agent"

    Write-Host "[1/5] Preparing installation..."
    New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null

    Get-ChildItem -Path $Source -Force |
        Where-Object { $_.Name -notin @(".git", ".venv", "build", "dist") } |
        Copy-Item -Destination $InstallDir -Recurse -Force

    Write-Host "[2/5] Finding Python..."
    $Py = Get-Command py.exe -ErrorAction SilentlyContinue

    if ($Py) {
        $versions = @("3.13", "3.12", "3.14", "3.11")
        $selected = $null

        foreach ($version in $versions) {
            try {
                & $Py.Source -$version --version *> $null
                if ($LASTEXITCODE -eq 0) {
                    $selected = $version
                    break
                }
            } catch {}
        }

        if (-not $selected) {
            throw "Python 3.11+ was not found. Install Python 3.12 or 3.13 and run Install.bat again."
        }

        Write-Host "Using Python $selected"
        & $Py.Source -$selected -m venv (Join-Path $InstallDir ".venv")
    }
    else {
        $Python = (Get-Command python.exe -ErrorAction SilentlyContinue).Source
        if (-not $Python) {
            throw "Python was not found. Install Python 3.12 or 3.13 and run Install.bat again."
        }
        & $Python -m venv (Join-Path $InstallDir ".venv")
    }

    $VenvPython = Join-Path $InstallDir ".venv\Scripts\python.exe"
    $VenvPythonW = Join-Path $InstallDir ".venv\Scripts\pythonw.exe"
    $Requirements = Join-Path $InstallDir "requirements.txt"
    $RunPy = Join-Path $InstallDir "run.py"

    if (-not (Test-Path $VenvPython)) {
        throw "Python virtual environment could not be created."
    }

    Write-Host "[3/5] Installing DirectDrop dependencies..."
    & $VenvPython -m pip install --upgrade pip
    if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed." }

    & $VenvPython -m pip install -r $Requirements
    if ($LASTEXITCODE -ne 0) { throw "Dependency installation failed." }

    Write-Host "[4/5] Registering background agent..."
    $Action = '"' + $VenvPythonW + '" "' + $RunPy + '" --agent'
    schtasks.exe /Create /TN $TaskName /SC ONLOGON /TR $Action /F | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Could not register the Windows startup task." }

    Write-Host "[5/5] Starting DirectDrop..."
    Start-Process -FilePath $VenvPythonW -ArgumentList @($RunPy, "--agent") -WindowStyle Hidden

    Write-Host ""
    Write-Host "============================================"
    Write-Host " DirectDrop installation completed"
    Write-Host "============================================"
    Write-Host ""
    Write-Host "Connect a supported USB-C/USB4 network link after installing on both laptops."
}
catch {
    Write-Host ""
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
