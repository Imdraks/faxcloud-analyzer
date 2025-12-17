@echo off
REM ========================================
REM FaxCloud Analyzer v3.0 - Démarrage
REM ========================================

setlocal enabledelayedexpansion

title FaxCloud Analyzer v3.0

echo.
echo ========================================
echo   FAXCLOUD ANALYZER v3.0
echo   Plateforme d'analyse FAX avancee
echo ========================================
echo.

REM Vérifier si virtualenv existe
if not exist ".venv" (
    echo [!] Virtual environment not found
    echo [*] Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Failed to create venv
        pause
        exit /b 1
    )
)

REM Activer virtualenv
echo [*] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate venv
    pause
    exit /b 1
)

REM Installer dépendances
echo [*] Checking dependencies...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

REM Initialiser base de données
echo [*] Initializing database...
python scripts/init_db.py
if errorlevel 1 (
    echo [ERROR] Failed to initialize database
    REM Continuer quand même
)

REM Démarrer l'app
echo.
echo [OK] Starting Flask server...
echo.
echo Access the application at: http://127.0.0.1:5000
echo Admin dashboard: http://127.0.0.1:5000/admin
echo API health check: http://127.0.0.1:5000/api/health
echo.
echo Press Ctrl+C to stop
echo.

python run.py

pause
