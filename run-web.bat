@echo off
REM =============================================================================
REM FaxCloud Analyzer v3.0 - Demarrage du serveur web
REM =============================================================================
REM Features: API v3, Admin Dashboard, CLI, Audit Logging, Metrics
REM =============================================================================

cd /d "%~dp0"

REM Activer l'environnement virtuel
echo [*] Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat

REM Initialiser la base de donnees MySQL
echo.
echo [*] Initialisation de la base de donnees MySQL...
python init_mysql.py
echo.

REM Afficher les informations de demarrage
echo.
echo =====================================================
echo    FaxCloud Analyzer v3.0 - STARTING SERVER
echo =====================================================
echo.
echo [+] Features activees:
echo     * API v3 avec 10+ endpoints avances
echo     * Dashboard Admin: http://localhost:5000/admin
echo     * CLI Administration: python cli.py
echo     * Audit Logging: logs/audit.log
echo     * Metriques Systeme en temps reel
echo     * Rate Limiting & Webhooks
echo.
echo [+] Accès:
echo     - Dashboard: http://localhost:5000
echo     - Admin: http://localhost:5000/admin
echo     - API v3: http://localhost:5000/api/v3/health
echo.

REM Configuration du serveur
set FLASK_ENV=development
set FLASK_DEBUG=1
set USE_NGROK=false

REM Demarrer le serveur Flask avec compression GZIP
echo [*] Demarrage du serveur Flask...
echo.
python web/app.py

pause
