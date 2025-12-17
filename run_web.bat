@echo off
setlocal

set PORT=%1
if "%PORT%"=="" set PORT=8000

echo Démarrage du serveur statique sur http://localhost:%PORT% (dossier web)
python -m http.server %PORT% --directory web

endlocal
