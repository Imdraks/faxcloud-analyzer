@echo off
REM ═══════════════════════════════════════════════════════════════════════
REM FaxCloud Analyzer - Installation des dépendances
REM ═══════════════════════════════════════════════════════════════════════
REM Ce script installe tous les packages Python nécessaires

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

echo [OK] Python détecté
python --version

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  Étape 1: Création de l'environnement virtuel
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

if exist venv (
    echo [INFO] Environnement virtuel existe déjà
    echo [INFO] Utilisation de l'environnement existant...
) else (
    echo [*] Création de l'environnement virtuel 'venv'...
    python -m venv venv
    if errorlevel 1 (
        echo [ERREUR] Échec de création du venv
        pause
        exit /b 1
    )
    echo [OK] Environnement virtuel créé
)

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  Étape 2: Activation de l'environnement virtuel
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERREUR] Impossible d'activer l'environnement virtuel
    pause
    exit /b 1
)

echo [OK] Environnement virtuel activé

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  Étape 3: Mise à jour de pip
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

echo [*] Mise à jour de pip...
python -m pip install --upgrade pip

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  Étape 4: Installation des dépendances
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

echo [*] Installation des packages depuis requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERREUR] Échec de l'installation des packages
    echo.
    echo Essayez manuellement:
    echo   1. Ouvrez un terminal dans ce dossier
    echo   2. Tapez: venv\Scripts\activate
    echo   3. Tapez: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Tous les packages installés avec succès

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  Étape 5: Vérification des dépendances
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

echo [*] Vérification des packages...
python -c "import pandas; print('  pandas: OK')"
python -c "import openpyxl; print('  openpyxl: OK')"
python -c "import mysql.connector; print('  mysql-connector-python: OK')"
python -c "import qrcode; print('  qrcode: OK')"
python -c "import flask; print('  flask: OK')"

echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  Prochaines étapes
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

echo 1. Initialiser MySQL:
echo    python init_mysql.py
echo.

echo 2. Lancer l'interface web:
echo    launch-web.bat
echo.

echo 3. Ou utiliser la CLI:
echo    python main.py import --file data.csv --contract "CLIENT_001"
echo.

echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo  Installation terminée !
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.

pause
