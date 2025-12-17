@echo off
REM Script pour automatiser le build iOS avec GitHub Actions
REM Usage: build-ios.bat "Votre message de commit"

setlocal enabledelayedexpansion

REM Couleurs en ANSI (Windows 10+)
for /F %%A in ('copy /Z "%~f0" nul') do set "BS=%%A"

REM Variables de couleur
set "BLUE=[94m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "NC=[0m"

REM Message de commit
if "%~1"=="" (
    set "COMMIT_MESSAGE=chore: Build iOS app"
) else (
    set "COMMIT_MESSAGE=%~1"
)

cls
echo.
echo %BLUE%======================================%NC%
echo %BLUE%   FaxCloud iOS Build Script%NC%
echo %BLUE%======================================%NC%
echo.

REM Vérifier que Git est installé
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo %RED%[ERROR] Git n'est pas installé%NC%
    echo Please install Git from: https://git-scm.com/download/win
    pause
    exit /b 1
)

REM Afficher le status Git
echo %YELLOW%[*] Status Git:%NC%
git status --short
echo.

REM Ajouter les changements
echo %YELLOW%[*] Ajout des changements...%NC%
git add .
echo %GREEN%[OK] Changements ajoutés%NC%
echo.

REM Commit
echo %YELLOW%[*] Commit: %COMMIT_MESSAGE%%NC%
git commit -m "%COMMIT_MESSAGE%"
if %ERRORLEVEL% EQU 1 (
    echo %YELLOW%[INFO] Aucun changement à committer%NC%
)
echo.

REM Push
echo %YELLOW%[*] Push vers GitHub...%NC%
git push origin main
if %ERRORLEVEL% NEQ 0 (
    echo %YELLOW%[*] Tentative: git push -u origin main...%NC%
    git push -u origin main
)
echo %GREEN%[OK] Code poussé avec succès!%NC%
echo.

REM Extraire le repo owner et name
for /f "tokens=*" %%i in ('git config --get remote.origin.url') do set "REPO_URL=%%i"

REM Extraire le owner du URL (https://github.com/OWNER/repo.git)
REM Utilise PowerShell pour parser le URL proprement
for /f "tokens=*" %%i in ('powershell -Command "[System.Uri]::new('%REPO_URL%').Segments[1].Trim('/')"') do (
    set "REPO_OWNER=%%i"
)

echo %BLUE%======================================%NC%
echo.
echo %BLUE%[*] Voir le build:%NC%
echo     https://github.com/%REPO_OWNER%/faxcloud-analyzer/actions
echo.
echo %GREEN%[OK] Le build démarre automatiquement!%NC%
echo %YELLOW%[*] Attendez 5-10 minutes pour la compilation%NC%
echo.

echo %BLUE%[*] Pour télécharger l'app:%NC%
echo     1. Allez sur le lien ci-dessus
echo     2. Cliquez sur "Build iOS App"
echo     3. Cliquez sur votre build (en vert si succès)
echo     4. Scroll down pour "Artifacts"
echo     5. Téléchargez "FaxCloudAnalyzer.ipa"
echo.

echo %GREEN%========================================%NC%
echo %GREEN%   Votre app iOS est en cours de build!%NC%
echo %GREEN%========================================%NC%
echo.

REM Ouvrir le navigateur
start https://github.com/%REPO_OWNER%/faxcloud-analyzer/actions

pause
