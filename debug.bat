@echo off
REM Script de debug - Test import CSV et calculs pages SF/RF
REM Lance le debug sans la partie web Flask

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   FaxCloud Analyzer - DEBUG Script
echo ════════════════════════════════════════════════════════════════════════
echo.

REM Vérifier que l'env venv existe
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Erreur: Environment virtuel non trouvé
    echo Exécutez d'abord: install.bat
    pause
    exit /b 1
)

REM Lancer le debug script
echo Lancement du debug script...
echo.

.venv\Scripts\python.exe debug_import.py

echo.
echo ════════════════════════════════════════════════════════════════════════
echo.
pause
