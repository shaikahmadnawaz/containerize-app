#!/usr/bin/env bash
# cleanup.sh — tear down containers, volumes, and local images.
set -euo pipefail

echo "==> Stopping and removing containers and volumes..."
docker compose down -v --remove-orphans

echo "==> Removing local image..."
docker image rm -f containerize-app:local 2>/dev/null || true

echo "==> Pruning dangling build cache layers..."
docker builder prune -f --filter type=exec.cachemount

echo "Cleanup complete."
