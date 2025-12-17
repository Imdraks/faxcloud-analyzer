@echo off
setlocal

set PORT=%1
if "%PORT%"=="" set PORT=5000

set OPEN=%2
set OPEN_BROWSER=
if /I "%OPEN%"=="open" set OPEN_BROWSER=1
if /I "%OPEN%"=="--open" set OPEN_BROWSER=1
if /I "%OPEN%"=="/open" set OPEN_BROWSER=1
if /I "%OPEN%"=="1" set OPEN_BROWSER=1

echo Demarrage du serveur FaxCloud Analyzer
echo http://127.0.0.1:%PORT%
echo CTRL+C pour arreter

if not "%OPEN_BROWSER%"=="" (
	echo Ouverture du navigateur...
	start "" "http://127.0.0.1:%PORT%/"
)

python -m src.server --host 127.0.0.1 --port %PORT%

endlocal
