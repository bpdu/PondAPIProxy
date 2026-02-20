#!/bin/bash
set -e

VAULT_ADDR=${VAULT_ADDR:-http://localhost:8200}
VAULT_TOKEN=${VAULT_TOKEN:-dev-only-token}
KV_PATH=${KV_PATH:-pondmobile}
TOKEN_FIELD=${TOKEN_FIELD:-token}

echo "Vault initialization..."
echo "VAULT_ADDR: $VAULT_ADDR"
echo "KV_PATH: $KV_PATH"

vault login -address="$VAULT_ADDR" "$VAULT_TOKEN"

echo "Enabling KV v2 secrets engine..."
vault secrets enable -address="$VAULT_ADDR" -path=secret kv-v2 2>/dev/null || true

echo "Adding Pond Mobile API token to Vault..."
echo "Enter Pond Mobile API token:"
read -s POND_TOKEN

vault kv put -address="$VAULT_ADDR" "secret/$KV_PATH" "$TOKEN_FIELD"="$POND_TOKEN"

echo "Verifying..."
vault kv get -address="$VAULT_ADDR" "secret/$KV_PATH"

echo "Vault initialization complete!"
