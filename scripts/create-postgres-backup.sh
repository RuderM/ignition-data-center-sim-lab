#!/usr/bin/env bash
set -euo pipefail

CONTAINER_NAME="${POSTGRES_CONTAINER:-ignition-env1-postgres}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${SCRIPT_DIR}/../backups/postgres"
DATABASE_BACKUP_FILE="${BACKUP_DIR}/ignition.dump"
GLOBALS_BACKUP_FILE="${BACKUP_DIR}/globals.sql"
TEMP_DATABASE_BACKUP_FILE="${DATABASE_BACKUP_FILE}.tmp"
TEMP_GLOBALS_BACKUP_FILE="${GLOBALS_BACKUP_FILE}.tmp"
CONTAINER_DATABASE_BACKUP_FILE="/tmp/ignition.dump"
CONTAINER_GLOBALS_BACKUP_FILE="/tmp/globals.sql"

cleanup() {
  docker exec "$CONTAINER_NAME" rm -f \
    "$CONTAINER_DATABASE_BACKUP_FILE" "$CONTAINER_GLOBALS_BACKUP_FILE" \
    >/dev/null 2>&1 || true
  rm -f "$TEMP_DATABASE_BACKUP_FILE" "$TEMP_GLOBALS_BACKUP_FILE"
}
trap cleanup EXIT

mkdir -p "$BACKUP_DIR"
docker exec "$CONTAINER_NAME" sh -eu -c '
  pg_dump --format=custom --create --username="$POSTGRES_USER" \
    --file="$1" "$POSTGRES_DB"
  pg_restore --list "$1" >/dev/null
  pg_dumpall --globals-only --username="$POSTGRES_USER" > "$2"
  test -s "$2"
' sh "$CONTAINER_DATABASE_BACKUP_FILE" "$CONTAINER_GLOBALS_BACKUP_FILE"
docker cp "$CONTAINER_NAME:$CONTAINER_DATABASE_BACKUP_FILE" "$TEMP_DATABASE_BACKUP_FILE"
docker cp "$CONTAINER_NAME:$CONTAINER_GLOBALS_BACKUP_FILE" "$TEMP_GLOBALS_BACKUP_FILE"
mv -f "$TEMP_DATABASE_BACKUP_FILE" "$DATABASE_BACKUP_FILE"
mv -f "$TEMP_GLOBALS_BACKUP_FILE" "$GLOBALS_BACKUP_FILE"

echo "PostgreSQL database backup created: $DATABASE_BACKUP_FILE"
echo "PostgreSQL globals backup created: $GLOBALS_BACKUP_FILE"
