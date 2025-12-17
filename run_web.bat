@echo off
setlocal

set PORT=%1
if "%PORT%"=="" set PORT=5000

echo Demarrage du serveur FaxCloud Analyzer
echo http://127.0.0.1:%PORT%
echo CTRL+C pour arreter

python -m src.server --port %PORT%

endlocal
