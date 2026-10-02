#!/usr/bin/env bash

set -e

PROJECT_DIR="$HOME/PycharmProjects/turing-test"

cd "$PROJECT_DIR"

echo "=== TURING TEST ==="
echo

echo "[1/3] Sprawdzam Cloudflare Tunnel..."

if ! systemctl is-active --quiet cloudflared; then
    echo "Cloudflare Tunnel nie działa. Uruchamiam..."
    sudo systemctl start cloudflared
fi

echo "✓ Cloudflare Tunnel działa."
echo

echo "[2/3] Sprawdzam konfigurację..."

source .venv/bin/activate
source scripts/env.sh

uv run python scripts/check_setup.py

echo

echo "[3/3] Uruchamiam aplikację..."

echo
echo "Lokalnie:"
echo "  http://127.0.0.1:8000"
echo
echo "Publicznie:"
echo "  https://turing-test.pl"
echo
echo "Zatrzymanie: Ctrl+C"
echo

exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000