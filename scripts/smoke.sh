#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
uv sync
npm ci
uv run python test_server.py
uv run python -c "from granola_mcp_server.server import main; print('import_ok')"
echo "granola smoke passed"
