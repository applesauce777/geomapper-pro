# GeoMapper Pro - Windows PowerShell Installer
# Run as: powershell -ExecutionPolicy Bypass -File install_windows.ps1

param(
    [string]$InstallDir = "$env:LOCALAPPDATA\GeoMapperPro",
    [switch]$AddToPath,
    [switch]$CreateDesktopShortcut,
    [switch]$CreateStartMenuShortcut
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "   GeoMapper Pro - Windows Installer" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[1/7] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python not found. Please install Python 3.7+ first." -ForegroundColor Red
    exit 1
}

# Create install directory
Write-Host "[2/7] Creating installation directory..." -ForegroundColor Yellow
if (!(Test-Path $InstallDir)) {
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
}
Write-Host "  Location: $InstallDir" -ForegroundColor Green

# Copy files
Write-Host "[3/7] Copying GeoMapper files..." -ForegroundColor Yellow
$sourceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$filesToCopy = @("geomap.py", "flask_app.py", "requirements.txt")

foreach ($file in $filesToCopy) {
    $sourcePath = Join-Path $sourceDir $file
    if (Test-Path $sourcePath) {
        Copy-Item $sourcePath $InstallDir -Force
        Write-Host "  Copied: $file" -ForegroundColor Green
    }
}

# Copy icon if exists
$iconSource = Join-Path $sourceDir "icons\GeoMapperPro.ico"
$iconDest = Join-Path $InstallDir "GeoMapperPro.ico"
if (Test-Path $iconSource) {
    Copy-Item $iconSource $iconDest -Force
    Write-Host "  Copied: GeoMapperPro.ico" -ForegroundColor Green
}

# Install dependencies
Write-Host "[4/7] Installing Python dependencies..." -ForegroundColor Yellow
$reqFile = Join-Path $InstallDir "requirements.txt"
if (Test-Path $reqFile) {
    python -m pip install -r $reqFile --quiet
    Write-Host "  Dependencies installed" -ForegroundColor Green
} else {
    python -m pip install pandas folium numpy openpyxl pyarrow flask --quiet
    Write-Host "  Core dependencies installed" -ForegroundColor Green
}

# Create batch launchers
Write-Host "[5/7] Creating launchers..." -ForegroundColor Yellow

# CLI launcher
$batchContent = @"
@echo off
python "%~dp0geomap.py" %*
"@
$batchPath = Join-Path $InstallDir "geomap.bat"
Set-Content -Path $batchPath -Value $batchContent
Write-Host "  Created: geomap.bat" -ForegroundColor Green

# Web UI launcher (visible console)
$webBatchContent = @"
@echo off
title GeoMapper Pro - Web UI
echo.
echo   Starting GeoMapper Pro Web UI...
echo   Browser will open to http://localhost:5000
echo   Keep this window open while using the app.
echo.
python "%~dp0flask_app.py"
"@
$webBatchPath = Join-Path $InstallDir "geomap-web.bat"
Set-Content -Path $webBatchPath -Value $webBatchContent
Write-Host "  Created: geomap-web.bat" -ForegroundColor Green

# Web UI launcher (hidden console via VBS)
$vbsContent = @"
Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "$InstallDir"
WshShell.Run "pythonw flask_app.py", 0, False
"@
$vbsPath = Join-Path $InstallDir "GeoMapper Web.vbs"
Set-Content -Path $vbsPath -Value $vbsContent
Write-Host "  Created: GeoMapper Web.vbs (hidden console)" -ForegroundColor Green

# Create shortcuts
Write-Host "[6/7] Creating shortcuts..." -ForegroundColor Yellow

function Create-Shortcut {
    param($ShortcutPath, $TargetPath, $Arguments, $IconPath, $WorkingDir, $Description)
    
    $WshShell = New-Object -ComObject WScript.Shell
    $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = $TargetPath
    $Shortcut.Arguments = $Arguments
    $Shortcut.WorkingDirectory = $WorkingDir
    $Shortcut.Description = $Description
    if ($IconPath -and (Test-Path $IconPath)) {
        $Shortcut.IconLocation = $IconPath
    }
    $Shortcut.Save()
}

$desktopPath = [Environment]::GetFolderPath("Desktop")

# Desktop shortcuts
if ($CreateDesktopShortcut -or (-not $PSBoundParameters.ContainsKey('CreateDesktopShortcut'))) {
    # CLI shortcut
    $shortcutPath = Join-Path $desktopPath "GeoMapper Pro.lnk"
    Create-Shortcut -ShortcutPath $shortcutPath `
                    -TargetPath "cmd.exe" `
                    -Arguments "/k cd /d `"$InstallDir`" && echo GeoMapper Pro v2.1.0 Ready. Type: python geomap.py --help" `
                    -IconPath $iconDest `
                    -WorkingDir $InstallDir `
                    -Description "GeoMapper Pro CLI"
    Write-Host "  Created: GeoMapper Pro.lnk (CLI)" -ForegroundColor Green
    
    # Web UI shortcut
    $webShortcutPath = Join-Path $desktopPath "GeoMapper Pro Web.lnk"
    Create-Shortcut -ShortcutPath $webShortcutPath `
                    -TargetPath (Join-Path $InstallDir "geomap-web.bat") `
                    -Arguments "" `
                    -IconPath $iconDest `
                    -WorkingDir $InstallDir `
                    -Description "GeoMapper Pro Web Interface"
    Write-Host "  Created: GeoMapper Pro Web.lnk (Web UI)" -ForegroundColor Green
}

# Start Menu shortcuts
if ($CreateStartMenuShortcut) {
    $startMenuPath = [Environment]::GetFolderPath("StartMenu")
    $programsPath = Join-Path $startMenuPath "Programs\GeoMapper Pro"
    if (!(Test-Path $programsPath)) {
        New-Item -ItemType Directory -Path $programsPath -Force | Out-Null
    }
    
    # CLI
    $shortcutPath = Join-Path $programsPath "GeoMapper Pro.lnk"
    Create-Shortcut -ShortcutPath $shortcutPath `
                    -TargetPath "cmd.exe" `
                    -Arguments "/k cd /d `"$InstallDir`" && echo GeoMapper Pro v2.1.0 Ready." `
                    -IconPath $iconDest `
                    -WorkingDir $InstallDir `
                    -Description "GeoMapper Pro CLI"
    
    # Web UI
    $webShortcutPath = Join-Path $programsPath "GeoMapper Pro Web.lnk"
    Create-Shortcut -ShortcutPath $webShortcutPath `
                    -TargetPath (Join-Path $InstallDir "geomap-web.bat") `
                    -Arguments "" `
                    -IconPath $iconDest `
                    -WorkingDir $InstallDir `
                    -Description "GeoMapper Pro Web Interface"
    
    Write-Host "  Created: Start Menu shortcuts" -ForegroundColor Green
}

# Add to PATH
Write-Host "[7/7] Finalizing..." -ForegroundColor Yellow
if ($AddToPath) {
    $userPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($userPath -notlike "*$InstallDir*") {
        [Environment]::SetEnvironmentVariable("PATH", "$userPath;$InstallDir", "User")
        Write-Host "  Added to PATH (restart terminal to use)" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "   Installation Complete!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Command-line usage:" -ForegroundColor Yellow
Write-Host "  cd `"$InstallDir`""
Write-Host "  python geomap.py yourdata.csv"
Write-Host ""
Write-Host "Web interface:" -ForegroundColor Yellow
Write-Host "  Double-click 'GeoMapper Pro Web' on Desktop"
Write-Host "  Or run: geomap-web.bat"
Write-Host "  (Opens browser to http://localhost:5000)"
Write-Host ""
