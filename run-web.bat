@echo off
REM =============================================================================
REM FaxCloud Analyzer - Demarrage du serveur web
REM =============================================================================

cd /d "%~dp0"

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

REM Demarrer le serveur Flask
echo.
echo =========================================
echo  Demarrage du serveur FaxCloud Analyzer
echo =========================================
echo.
echo Ouverture: http://localhost:5000
echo.

python web/app.py

pause
