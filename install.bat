@echo off
REM ═══════════════════════════════════════════════════════════════════════════
REM FaxCloud Analyzer - Installation complète
REM ═══════════════════════════════════════════════════════════════════════════

setlocal enabledelayedexpansion

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

python --version
if errorlevel 1 (
    echo.
    echo ❌ ERREUR: Python n'est pas trouvé
    echo.
    echo Pour corriger:
    echo   1. Téléchargez Python 3.8+ depuis https://www.python.org/downloads/
    echo   2. Cochez "Add Python to PATH" lors de l'installation
    echo   3. Redémarrez votre ordinateur
    echo   4. Relancez ce script
    echo.
    echo Appuyez sur une touche pour fermer...
    pause >nul
    exit /b 1
)

echo ✓ Python trouvé
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM ÉTAPE 2: Créer l'environnement virtuel
REM ═══════════════════════════════════════════════════════════════════════════

echo [ÉTAPE 2] Création de l'environnement virtuel...
echo ──────────────────────────────────────────────────────────────────────────

if exist venv (
    echo ✓ Environnement virtuel existe déjà
) else (
    echo • Création du venv (cela peut prendre quelques secondes)...
    python -m venv venv
    if errorlevel 1 (
        echo.
        echo ❌ ERREUR: Impossible de créer le venv
        echo.
        echo Appuyez sur une touche pour fermer...
        pause >nul
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
    echo.
    echo Appuyez sur une touche pour fermer...
    pause >nul
    exit /b 1
)

echo ✓ Environnement virtuel activé
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM ÉTAPE 4: Mettre à jour pip
REM ═══════════════════════════════════════════════════════════════════════════

echo [ÉTAPE 4] Mise à jour de pip...
echo ──────────────────────────────────────────────────────────────────────────

echo • Cela peut prendre quelques secondes...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ❌ ERREUR: Impossible de mettre à jour pip
    echo.
    echo Appuyez sur une touche pour fermer...
    pause >nul
    exit /b 1
)

pip --version
echo ✓ pip mis à jour
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM ÉTAPE 5: Installer les dépendances
REM ═══════════════════════════════════════════════════════════════════════════

echo [ÉTAPE 5] Installation des dépendances...
echo ──────────────────────────────────────────────────────────────────────────

echo • Installation en cours (cela peut prendre 2-3 minutes)...
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ❌ ERREUR: L'installation des dépendances a échoué
    echo.
    echo Appuyez sur une touche pour fermer...
    pause >nul
    exit /b 1
)

echo.
echo ✓ Toutes les dépendances installées
echo.

REM ═══════════════════════════════════════════════════════════════════════════
REM ÉTAPE 6: Vérification finale
REM ═══════════════════════════════════════════════════════════════════════════

echo [ÉTAPE 6] Vérification finale...
echo ──────────────────────────────────────────────────────────────────────────

pip list | findstr /i "pandas flask qrcode"
if errorlevel 1 (
    echo ⚠ Avertissement: Certains packages pourraient ne pas être installés
) else (
    echo ✓ Packages clés détectés
)

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
echo Appuyez sur une touche pour fermer...
pause >nul
