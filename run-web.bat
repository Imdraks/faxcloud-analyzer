@echo off
REM =============================================================================
REM FaxCloud Analyzer - Demarrage du serveur web
REM =============================================================================

cd /d "%~dp0"

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

REM Initialiser la base de donnees MySQL
echo.
echo [*] Initialisation de la base de donnees MySQL...
python init_mysql.py
echo.

REM Demarrer le serveur Flask avec ngrok
echo.
echo =========================================
echo  Demarrage du serveur FaxCloud Analyzer
echo =========================================
echo.
echo Ouverture: http://localhost:5000
echo.

REM Lancer en mode ngrok
set USE_NGROK=true
python web/app.py

pause
