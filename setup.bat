@echo off
REM ============================================================
REM FaxCloud Analyzer - Quick Setup Script
REM ============================================================

color 0B
cls

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║                                                        ║
echo ║     FaxCloud Analyzer v3.0 - Quick Setup              ║
echo ║                                                        ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
if not exist ".venv" (
    python -m venv .venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)

echo.
echo [2/5] Activating virtual environment...
call .venv\Scripts\activate.bat
echo [OK] Virtual environment activated

echo.
echo [3/5] Installing dependencies...
pip install -r requirements.txt -q
echo [OK] Dependencies installed

echo.
echo [4/5] Verifying installation...
python -c "import flask; import sqlalchemy; print('[OK] Core dependencies verified')"

echo.
echo [5/5] Starting application...
echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  Server is starting...                                 ║
echo ║  Access: http://127.0.0.1:5000                        ║
echo ║  Admin:  http://127.0.0.1:5000/admin                  ║
echo ║  API:    http://127.0.0.1:5000/api/health             ║
echo ║                                                        ║
echo ║  Press Ctrl+C to stop the server                       ║
echo ╚════════════════════════════════════════════════════════╝
echo.

python run.py

pause
