#!/bin/bash
# ============================================================
# FaxCloud Analyzer - Quick Setup Script (macOS/Linux)
# ============================================================

set -e

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║                                                        ║"
echo "║     FaxCloud Analyzer v3.0 - Quick Setup              ║"
echo "║                                                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    exit 1
fi

echo "[1/5] Creating virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "[OK] Virtual environment created"
else
    echo "[OK] Virtual environment already exists"
fi

echo ""
echo "[2/5] Activating virtual environment..."
source .venv/bin/activate
echo "[OK] Virtual environment activated"

echo ""
echo "[3/5] Installing dependencies..."
pip install -r requirements.txt -q
echo "[OK] Dependencies installed"

echo ""
echo "[4/5] Verifying installation..."
python -c "import flask; import sqlalchemy; print('[OK] Core dependencies verified')"

echo ""
echo "[5/5] Starting application..."
echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  Server is starting...                                 ║"
echo "║  Access: http://127.0.0.1:5000                        ║"
echo "║  Admin:  http://127.0.0.1:5000/admin                  ║"
echo "║  API:    http://127.0.0.1:5000/api/health             ║"
echo "║                                                        ║"
echo "║  Press Ctrl+C to stop the server                       ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

python run.py
