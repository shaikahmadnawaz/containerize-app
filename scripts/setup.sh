#!/usr/bin/env bash
# setup.sh — bootstrap the local development environment.
set -euo pipefail

echo "==> Checking prerequisites..."

command -v docker >/dev/null 2>&1 || { echo "ERROR: docker is required"; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "ERROR: docker compose plugin is required"; exit 1; }

echo "==> Building image..."
docker build --target runtime -t containerize-app:local .

echo "==> Starting full stack..."
docker compose up -d

echo ""
echo "Stack is up. Available endpoints:"
echo "  http://localhost:8000       — API root"
echo "  http://localhost:8000/health — liveness probe"
echo "  http://localhost:8000/ready  — readiness probe"
echo "  http://localhost:8000/metrics — Prometheus metrics"
echo "  http://localhost:8000/info   — runtime info"
echo "  http://localhost:8000/docs   — Swagger UI"
echo ""
echo "Useful commands:"
echo "  make logs   — tail app logs"
echo "  make stop   — stop the stack"
echo "  make scan   — vulnerability scan (requires trivy)"
