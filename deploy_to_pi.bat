@echo off
REM =====================================================
REM FaxCloud Analyzer - Deploiement vers Raspberry Pi
REM =====================================================

setlocal enabledelayedexpansion

echo.
echo ====================================================
echo    FaxCloud Analyzer - Deploiement vers Raspberry Pi
echo ====================================================
echo.

REM Configuration - MODIFIEZ CES VALEURS
set PI_USER=pi
set PI_HOST=raspberrypi.local
set PI_PATH=/home/pi/faxcloud-analyzer

REM Demander l'adresse si besoin
set /p "PI_INPUT=Adresse du Pi [%PI_HOST%]: "
if not "%PI_INPUT%"=="" set PI_HOST=%PI_INPUT%

echo.
echo Configuration:
echo   Utilisateur: %PI_USER%
echo   Hote: %PI_HOST%
echo   Chemin: %PI_PATH%
echo.

REM Vérifier si scp est disponible
where scp >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERREUR] scp n'est pas disponible.
    echo Installez OpenSSH ou utilisez Git Bash.
    pause
    exit /b 1
)

echo [1/3] Synchronisation des fichiers...
echo.

REM Créer le dossier distant
ssh %PI_USER%@%PI_HOST% "mkdir -p %PI_PATH%"

REM Copier les fichiers (exclure les dossiers inutiles)
scp -r src web main.py requirements.txt Dockerfile docker-compose.yml raspberry-pi %PI_USER%@%PI_HOST%:%PI_PATH%/

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERREUR] Echec de la copie des fichiers
    pause
    exit /b 1
)

echo.
echo [2/3] Fichiers copies avec succes!
echo.

REM Demander si on veut lancer la mise à jour
set /p "UPDATE=Lancer la mise a jour sur le Pi? (o/n): "
if /i "%UPDATE%"=="o" (
    echo.
    echo [3/3] Lancement de la mise a jour...
    ssh %PI_USER%@%PI_HOST% "cd %PI_PATH% && sudo ./raspberry-pi/update.sh"
) else (
    echo.
    echo Pour mettre a jour manuellement:
    echo   ssh %PI_USER%@%PI_HOST%
    echo   cd %PI_PATH%
    echo   sudo ./raspberry-pi/update.sh
)

echo.
echo ====================================================
echo    Deploiement termine!
echo ====================================================
echo.
pause
