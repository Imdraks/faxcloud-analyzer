@echo off
REM Installe ngrok sur Windows

echo.
echo ════════════════════════════════════════════════════════════════════════
echo   Installation de ngrok
echo ════════════════════════════════════════════════════════════════════════
echo.

REM Vérifier que curl ou wget sont disponibles
where curl >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ curl n'est pas disponible
    echo Veuillez télécharger ngrok manuellement:
    echo   https://ngrok.com/download
    echo.
    pause
    exit /b 1
)

echo 📥 Téléchargement de ngrok...
REM Télécharger ngrok
curl -L -o ngrok.zip "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"

if %errorlevel% neq 0 (
    echo ❌ Erreur téléchargement
    pause
    exit /b 1
)

echo ✅ Téléchargement terminé

echo 📦 Extraction...
REM Extraire ngrok
PowerShell -Command "Expand-Archive -Path ngrok.zip -DestinationPath . -Force"

if %errorlevel% neq 0 (
    echo ❌ Erreur extraction
    pause
    exit /b 1
)

echo ✅ Extraction terminée

echo 🧹 Nettoyage...
del /Q ngrok.zip

echo.
echo ✅ ngrok installé!
echo.
echo 📝 Prochaines étapes:
echo   1. Créer un compte: https://ngrok.com
echo   2. Obtenir votre authtoken: https://dashboard.ngrok.com/auth
echo   3. Configurer: ngrok config add-authtoken YOUR_TOKEN
echo   4. Lancer: python web/app.py (avec USE_NGROK=true)
echo.
pause
