#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="${IGNITION_GATEWAY_CONTAINER:-ignition-env1-gateway}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${SCRIPT_DIR}/../backups/gateway"
BACKUP_FILE="${BACKUP_DIR}/ignition-env1.gwbk"
TEMP_BACKUP_FILE="${BACKUP_FILE}.tmp"
CONTAINER_BACKUP_FILE="/tmp/ignition-env1.gwbk"

cleanup() {
  docker exec "$CONTAINER_NAME" rm -f "$CONTAINER_BACKUP_FILE" >/dev/null 2>&1 || true
  rm -f "$TEMP_BACKUP_FILE"
}
trap cleanup EXIT

mkdir -p "$BACKUP_DIR"
docker exec "$CONTAINER_NAME" \
  /usr/local/bin/ignition/gwcmd.sh --backup "$CONTAINER_BACKUP_FILE" --timeout 300
docker cp "$CONTAINER_NAME:$CONTAINER_BACKUP_FILE" "$TEMP_BACKUP_FILE"
unzip -tq "$TEMP_BACKUP_FILE"
mv -f "$TEMP_BACKUP_FILE" "$BACKUP_FILE"

echo "Gateway backup created: $BACKUP_FILE"
