#!/usr/bin/env powershell
# Quick Start - FaxCloud Analyzer v2.0 Liquid Glass Edition

Write-Host "🚀 FaxCloud Analyzer - Liquid Glass Optimized" -ForegroundColor Cyan
Write-Host "Version: 2.0.0 - Features: SVG Liquid Glass + Performance Optimization" -ForegroundColor Gray

# Colors
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"

Write-Host "`n📋 QUICK START GUIDE`n" -ForegroundColor Cyan

# Check if Python installed
Write-Host "1️⃣  Checking Python installation..." -ForegroundColor Yellow
$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    Write-Host "✅ Python found: $($python.Source)" -ForegroundColor $Green
} else {
    Write-Host "❌ Python not found! Install Python 3.9+" -ForegroundColor $Red
    exit 1
}

# Check MySQL
Write-Host "`n2️⃣  Checking MySQL connection..." -ForegroundColor Yellow
Write-Host "⚠️  Make sure WampServer MySQL is running!" -ForegroundColor Yellow
Write-Host "   or adjust DB_HOST in src/core/config.py" -ForegroundColor Gray

# Start server
Write-Host "`n3️⃣  Starting server..." -ForegroundColor Yellow
Write-Host "   Running: python web\app.py" -ForegroundColor Gray

Push-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
python web\app.py

<#
Expected Output:
  [INFO] Base de donnees initialisee
  [INFO] Demarrage du serveur: http://127.0.0.1:5000
  [INFO] Running on http://127.0.0.1:5000
  ✅ Server ready!

Then:
  - Open: http://127.0.0.1:5000
  - View ngrok URL in console for remote access
  - Test liquid glass effects on buttons
#>
