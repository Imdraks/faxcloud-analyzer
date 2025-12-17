@echo off
REM Lance FaxCloud Analyzer avec ngrok ACTIVÉ

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   FaxCloud Analyzer - Avec ngrok PUBLIC
echo ════════════════════════════════════════════════════════════════════════
echo.

REM Vérifier que l'env venv existe
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Erreur: Environment virtuel non trouvé
    echo Exécutez d'abord: install.bat
    pause
    exit /b 1
)

REM Vérifier que ngrok est installé
where ngrok >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️  ngrok non trouvé dans le PATH
    echo.
    echo Options:
    echo   1. Installer ngrok: https://ngrok.com/download
    echo   2. Ou lancer sans ngrok: python web/app.py
    echo.
    pause
    exit /b 1
)

echo ✅ Configurations:
echo   - Serveur local: http://127.0.0.1:5000
echo   - ngrok activé: OUI
echo   - Public: OUI (URL sera affichée ci-dessous)
echo.

REM Activer ngrok
set USE_NGROK=true

echo 🚀 Lancement du serveur...
echo.

.venv\Scripts\python.exe web/app.py

echo.
echo ════════════════════════════════════════════════════════════════════════
echo.
pause
