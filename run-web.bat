@echo off
REM =============================================================================
REM FaxCloud Analyzer v3.0 - Demarrage du serveur web
REM =============================================================================

cd /d "%~dp0"

REM Activer l'environnement virtuel
call .venv\Scripts\activate.bat

REM Demarrer le serveur Flask
echo.
echo =========================================
echo  FaxCloud Analyzer v3.0
echo  Serveur demarrage...
echo =========================================
echo.
echo Ouverture: http://127.0.0.1:5000
echo.

REM Lancer la nouvelle application
python run.py

pause
