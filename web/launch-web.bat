@echo off
REM FaxCloud Analyzer - Lancer l'interface web

title FaxCloud Analyzer - Web Interface
cls

echo.
echo ╔════════════════════════════════════════════╗
echo ║  FaxCloud Analyzer - Interface Web         ║
echo ╚════════════════════════════════════════════╝
echo.

REM Vérifier si venv existe
if not exist "venv\" (
    echo ⚠️  Environnement virtuel non trouvé
    echo Création en cours...
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Démarrer le serveur
echo.
echo 🚀 Démarrage du serveur web...
echo.

cd web
python server.py 8000

pause
