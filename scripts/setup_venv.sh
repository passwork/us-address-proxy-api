#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_DIR/venv"

echo "=== US Address Proxy Service Setup ==="

# 1. Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists."
fi

# 2. Activate and install dependencies
echo "Installing dependencies..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r "$PROJECT_DIR/requirements.txt"

# 3. Run tests
echo "Running tests..."
cd "$PROJECT_DIR"
pytest -v

echo ""
echo "=== Setup complete ==="
echo "To activate the environment: source venv/bin/activate"
echo "To start the server: uvicorn app.main:app --reload --port 8000"
