#!/usr/bin/env bash
set -euo pipefail

GATEWAY_URL="${FLINT_GATEWAY_URL:-http://localhost:8088}"
PROJECT_NAME="${FLINT_PROJECT_NAME:-env1-project}"
CONTAINER_NAME="${FLINT_GATEWAY_CONTAINER:-ignition-env1-gateway}"
TOKEN_PATH="${FLINT_TOKEN_PATH:-/usr/local/bin/ignition/data/modules/flint/gateway/api-token.json}"

TOKEN="$(
  sudo docker exec "$CONTAINER_NAME" sh -lc \
    "sed -n 's/.*\"token\":\"\\([^\"]*\\)\".*/\\1/p' '$TOKEN_PATH'"
)"

if [ -z "$TOKEN" ]; then
  echo "Could not read Flint bearer token from $CONTAINER_NAME:$TOKEN_PATH" >&2
  exit 1
fi

RESPONSE="$(
  curl --fail --silent --show-error --max-time 20 \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    --data "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"project.scan\",\"params\":{\"project\":\"${PROJECT_NAME}\"}}" \
    "${GATEWAY_URL}/data/flint/rpc"
)"

echo "$RESPONSE"
