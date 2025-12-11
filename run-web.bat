@echo off
REM Démarrage du serveur web FaxCloud Analyzer
REM Ouvre automatiquement le navigateur

cd /d "%~dp0"

REM Activer l'environnement virtuel
call .\venv\Scripts\Activate.ps1

REM Démarrer le serveur Flask
echo.
echo ========================================
echo  Démarrage du serveur FaxCloud Analyzer
echo ========================================
echo.
echo Ouverture: http://localhost:5000
echo.

python web/app.py

pause
