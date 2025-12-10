@echo off
REM FaxCloud Analyzer - Démarrage rapide

echo.
echo ╔════════════════════════════════════════════╗
echo ║  FaxCloud Analyzer - Démarrage             ║
echo ╚════════════════════════════════════════════╝
echo.

if not exist "venv\" (
    echo 📦 Création de l'environnement virtuel...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo ✓ Environnement créé
    echo.
    echo 📥 Installation des dépendances...
    pip install -r requirements.txt
    echo ✓ Dépendances installées
) else (
    echo ✓ Environnement virtuel trouvé
    call venv\Scripts\activate.bat
)

echo.
echo 🚀 Options:
echo   1. init         - Initialiser la base de données
echo   2. import       - Importer un fichier
echo   3. list         - Lister les rapports
echo   4. view         - Consulter un rapport
echo   5. help         - Afficher l'aide
echo.

set /p choice="Choisir une option (1-5): "

if "%choice%"=="1" (
    python main.py init
) else if "%choice%"=="2" (
    set /p file="Chemin du fichier: "
    set /p contract="ID du contrat: "
    set /p start="Date de début (YYYY-MM-DD): "
    set /p end="Date de fin (YYYY-MM-DD): "
    python main.py import --file %file% --contract %contract% --start %start% --end %end%
) else if "%choice%"=="3" (
    python main.py list
) else if "%choice%"=="4" (
    set /p reportid="ID du rapport: "
    python main.py view --report-id %reportid%
) else if "%choice%"=="5" (
    python main.py --help
) else (
    echo Choix invalide
)

echo.
pause
