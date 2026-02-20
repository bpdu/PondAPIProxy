#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DOCKER_DIR="$PROJECT_DIR/docker"

cd "$DOCKER_DIR"

echo "Building Docker images..."
docker-compose build

echo "Starting services..."
docker-compose up -d

echo "Waiting for Vault..."
until docker-compose exec -T vault vault status > /dev/null 2>&1; do
    echo "Vault not ready yet..."
    sleep 2
done

echo "Services started. Run './deploy/init_vault.sh' to configure Vault."
echo ""
echo "Service URLs:"
echo "  - API: http://localhost:8000"
echo "  - Health: http://localhost:8000/health"
echo "  - Via Caddy: http://localhost"
