@echo off
REM =============================================================================
REM FaxCloud Analyzer - Installation complète
REM =============================================================================

setlocal enabledelayedexpansion

cls
echo.
echo ===============================================================================
echo                 FaxCloud Analyzer - Installation
echo                        Version 1.0.0
echo ===============================================================================
echo.

REM =============================================================================
REM ETAPE 1: Verifier Python
REM =============================================================================

echo [ETAPE 1] Verification de Python...
echo ───────────────────────────────────────────────────────────────────────────

python --version
if errorlevel 1 (
    echo.
    echo ERREUR: Python n'est pas trouve
    echo.
    echo Pour corriger:
    echo   1. Telechargez Python 3.8+ depuis https://www.python.org/downloads/
    echo   2. Cochez "Add Python to PATH" lors de l'installation
    echo   3. Redemarrez votre ordinateur
    echo   4. Relancez ce script
    echo.
    echo Appuyez sur une touche pour fermer...
    pause >nul
    exit /b 1
)

echo OK: Python trouve
echo.

REM =============================================================================
REM ETAPE 2: Creer l'environnement virtuel
REM =============================================================================

echo [ETAPE 2] Creation de l'environnement virtuel...
echo ───────────────────────────────────────────────────────────────────────────

if exist venv (
    echo OK: Environnement virtuel existe deja
) else (
    echo - Cela peut prendre quelques secondes...
    python -m venv venv
    if errorlevel 1 (
        echo.
        echo ERREUR: Impossible de creer le venv
        echo.
        echo Appuyez sur une touche pour fermer...
        pause >nul
        exit /b 1
    )
    echo OK: Environnement virtuel cree
)
echo.

REM =============================================================================
REM ETAPE 3: Activer l'environnement virtuel
REM =============================================================================

echo [ETAPE 3] Activation de l'environnement virtuel...
echo ───────────────────────────────────────────────────────────────────────────

call venv\Scripts\activate.bat
if errorlevel 1 (
    echo.
    echo ERREUR: Impossible d'activer le venv
    echo.
    echo Appuyez sur une touche pour fermer...
    pause >nul
    exit /b 1
)

echo OK: Environnement virtuel active
echo.

REM =============================================================================
REM ETAPE 4: Mettre a jour pip
REM =============================================================================

echo [ETAPE 4] Mise a jour de pip...
echo ───────────────────────────────────────────────────────────────────────────

echo - Cela peut prendre quelques secondes...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ERREUR: Impossible de mettre a jour pip
    echo.
    echo Appuyez sur une touche pour fermer...
    pause >nul
    exit /b 1
)

pip --version
echo OK: pip mis a jour
echo.

REM =============================================================================
REM ETAPE 5: Installer les dependances
REM =============================================================================

echo [ETAPE 5] Installation des dependances...
echo ───────────────────────────────────────────────────────────────────────────

echo - Installation en cours (cela peut prendre 2-3 minutes)...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ERREUR: L'installation des dependances a echoue
    echo.
    echo Appuyez sur une touche pour fermer...
    pause >nul
    exit /b 1
)

echo.
echo OK: Toutes les dependances installees
echo.

REM =============================================================================
REM ETAPE 6: Verification finale
REM =============================================================================

echo [ETAPE 6] Verification finale...
echo ───────────────────────────────────────────────────────────────────────────

pip list | findstr /i "pandas flask qrcode"
if errorlevel 1 (
    echo ATTENTION: Certains packages pourraient ne pas etre installes
) else (
    echo OK: Packages cles detectes
)

echo.

REM =============================================================================
REM SUCCES
REM =============================================================================

echo ===============================================================================
echo                  OK: INSTALLATION REUSSIE
echo ===============================================================================
echo.
echo Prochaines etapes:
echo.
echo 1. Initialiser le projet:
echo    python main.py init
echo.
echo 2. Importer un fichier:
echo    python main.py import --file exports/data.csv
echo.
echo 3. Lancer le serveur web:
echo    python web/app.py
echo    Puis accedez a: http://localhost:5000
echo.
echo Pour plus d'informations, consultez: README.md
echo.
echo Appuyez sur une touche pour fermer...
pause >nul
