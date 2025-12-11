@echo off
REM ═══════════════════════════════════════════════════════════════════════
REM FaxCloud Analyzer - Installation des dépendances (Windows)
REM ═══════════════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  FaxCloud Analyzer - Installation
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

REM Vérifier si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installé ou n'est pas dans le PATH
    echo.
    echo Téléchargez Python 3.8+ depuis https://www.python.org/downloads/
    echo N'oubliez pas de cocher "Add Python to PATH" lors de l'installation
    echo.
    pause
    exit /b 1
)

echo [✓] Python détecté
python --version
echo.

REM Créer ou utiliser l'environnement virtuel
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  Étape 1: Configuration de l'environnement virtuel
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

if exist venv (
    echo [INFO] Environnement virtuel existe déjà
) else (
    echo [*] Création de l'environnement virtuel...
    python -m venv venv
    if errorlevel 1 (
        echo [ERREUR] Impossible de créer le venv
        pause
        exit /b 1
    )
    echo [✓] Environnement virtuel créé
)
echo.

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERREUR] Impossible d'activer l'environnement virtuel
    pause
    exit /b 1
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  Étape 2: Mise à jour de pip et installation des dépendances
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

echo [*] Mise à jour de pip...
python -m pip install --upgrade pip --quiet

echo [*] Installation des packages...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [ERREUR] Impossible d'installer les packages
    echo.
    echo Essayez manuellement:
    echo   1. venv\Scripts\activate
    echo   2. pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo [✓] Tous les packages installés
echo.

REM Vérification rapide
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  Étape 3: Vérification des dépendances
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

python -c "import pandas; import openpyxl; import qrcode; import flask; print('  ✓ Tous les packages vérifié')" 2>nul

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  ✅ Installation terminée avec succès !
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

echo Prochaines étapes:
echo.
echo 1. Initialiser le projet:
echo    python main.py init
echo.
echo 2. Lancer l'interface web (Windows):
echo    cd web
echo    launch-web.bat
echo.
echo 3. Ou importer un fichier (CLI):
echo    python main.py import --file data.csv --contract "CLIENT_001"
echo.
echo 4. Consulter l'aide:
echo    python main.py --help
echo.

pause
