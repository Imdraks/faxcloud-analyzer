@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM FaxCloud Analyzer - Installation complète
REM ═══════════════════════════════════════════════════════════════════════════
REM Ce script installe Python, crée l'environnement virtuel et installe les dépendances

setlocal enabledelayedexpansion

REM Couleurs et styles
cls
echo.
echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                 FaxCloud Analyzer - Installation                          ║
echo ║                        Version 1.0.0                                      ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM ÉTAPE 1: Vérifier Python
REM ═══════════════════════════════════════════════════════════════════════════

echo [ÉTAPE 1] Vérification de Python...
echo ──────────────────────────────────────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ ERREUR: Python n'est pas installé ou n'est pas dans le PATH
    echo.
    echo Solution:
    echo   1. Téléchargez Python 3.8+ depuis https://www.python.org/downloads/
    echo   2. Lors de l'installation, cochez "Add Python to PATH"
    echo   3. Relancez ce script
    echo.
    pause
    exit /b 1
)

REM Afficher la version
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python détecté: %PYTHON_VERSION%
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM ÉTAPE 2: Créer l'environnement virtuel
REM ═══════════════════════════════════════════════════════════════════════════

echo [ÉTAPE 2] Configuration de l'environnement virtuel...
echo ──────────────────────────────────────────────────────────────────────────

if exist venv (
    echo ✓ Environnement virtuel (venv) existe déjà
) else (
    echo • Création de l'environnement virtuel...
    python -m venv venv
    if errorlevel 1 (
        echo.
        echo ❌ ERREUR: Impossible de créer le venv
        pause
        exit /b 1
    )
    echo ✓ Environnement virtuel créé
)
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM ÉTAPE 3: Activer l'environnement virtuel
REM ═══════════════════════════════════════════════════════════════════════════

echo [ÉTAPE 3] Activation de l'environnement virtuel...
echo ──────────────────────────────────────────────────────────────────────────

call venv\Scripts\activate.bat
if errorlevel 1 (
    echo.
    echo ❌ ERREUR: Impossible d'activer le venv
    pause
    exit /b 1
)

echo ✓ Environnement virtuel activé
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM ÉTAPE 4: Mettre à jour pip
REM ═══════════════════════════════════════════════════════════════════════════

echo [ÉTAPE 4] Mise à jour de pip...
echo ──────────────────────────────────────────────────────────────────────────

python -m pip install --upgrade pip --quiet
if errorlevel 1 (
    echo ❌ ERREUR: Impossible de mettre à jour pip
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('pip --version') do set PIP_VERSION=%%i
echo ✓ pip mis à jour: %PIP_VERSION%
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM ÉTAPE 5: Installer les dépendances
REM ═══════════════════════════════════════════════════════════════════════════

echo [ÉTAPE 5] Installation des dépendances de requirements.txt...
echo ──────────────────────────────────────────────────────────────────────────

pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ❌ ERREUR: L'installation des dépendances a échoué
    pause
    exit /b 1
)

echo.
echo ✓ Toutes les dépendances installées avec succès
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM ÉTAPE 6: Vérification finale
REM ═══════════════════════════════════════════════════════════════════════════

echo [ÉTAPE 6] Vérification de l'installation...
echo ──────────────────────────────────────────────────────────────────────────

echo • Packages installés:
pip list

echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM SUCCÈS
REM ═══════════════════════════════════════════════════════════════════════════

echo ╔═══════════════════════════════════════════════════════════════════════════╗
echo ║                  ✓ INSTALLATION RÉUSSIE                                   ║
echo ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
echo Prochaines étapes:
echo.
echo 1. Initialiser le projet:
echo    python main.py init
echo.
echo 2. Importer un fichier:
echo    python main.py import --file exports/data.csv
echo.
echo 3. Lancer le serveur web:
echo    python web/app.py
echo    Puis accédez à: http://localhost:5000
echo.
echo Pour plus d'informations, consultez: README.md
echo.

pause
