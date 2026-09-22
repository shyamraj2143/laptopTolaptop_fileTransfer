$ErrorActionPreference = "SilentlyContinue"

$TaskName = "DirectDrop Background Agent"
schtasks.exe /End /TN $TaskName | Out-Null
schtasks.exe /Delete /TN $TaskName /F | Out-Null

$InstallDir = Join-Path $env:LOCALAPPDATA "DirectDrop"
Remove-Item -Recurse -Force $InstallDir

Write-Host "DirectDrop removed."
