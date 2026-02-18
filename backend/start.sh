#!/bin/bash
set -e

echo "========================================="
echo "🚀 Starting Thesis Engine Backend"
echo "========================================="

echo "[1/4] Checking environment variables..."
echo "  DATABASE_URL: ${DATABASE_URL:0:30}..."
echo "  GROQ_API_KEY: ${GROQ_API_KEY:0:10}..."
echo "  PORT: ${PORT:-8080}"

echo "[2/4] Running database migrations..."
echo "  Command: alembic upgrade head"
alembic upgrade head
echo "  ✅ Migrations complete"

echo "[3/4] Verifying server can import..."
python -c "from app.main import app; print('  ✅ App imports successfully')"

echo "[4/4] Starting uvicorn server..."
echo "  Command: uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"
echo "========================================="
echo "✨ Startup complete - server launching!"
echo "========================================="

exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
