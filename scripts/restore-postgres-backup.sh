#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ] || [ "$1" != "--replace" ]; then
  cat >&2 <<'USAGE'
Usage: ./scripts/restore-postgres-backup.sh --replace

Restores backups/postgres/ignition.dump and backups/postgres/globals.sql into
PostgreSQL. This permanently replaces the target Ignition database.

Stop the Ignition Gateway before running this script.
USAGE
  exit 64
fi

CONTAINER_NAME="${POSTGRES_CONTAINER:-ignition-env1-postgres}"
GATEWAY_CONTAINER_NAME="${IGNITION_GATEWAY_CONTAINER:-ignition-env1-gateway}"
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
BACKUP_DIR="${SCRIPT_DIR}/../backups/postgres"
DATABASE_BACKUP_FILE="${BACKUP_DIR}/ignition.dump"
GLOBALS_BACKUP_FILE="${BACKUP_DIR}/globals.sql"
CONTAINER_DATABASE_BACKUP_FILE="/tmp/ignition-restore.dump"
CONTAINER_GLOBALS_BACKUP_FILE="/tmp/ignition-restore-globals.sql"

if [ ! -s "$DATABASE_BACKUP_FILE" ] || [ ! -s "$GLOBALS_BACKUP_FILE" ]; then
  echo "PostgreSQL backup artifacts are missing from $BACKUP_DIR" >&2
  exit 1
fi

if [ "$(docker inspect --format '{{.State.Running}}' "$GATEWAY_CONTAINER_NAME" 2>/dev/null || true)" = "true" ]; then
  echo "Stop the Ignition Gateway before restoring PostgreSQL: docker compose stop ignition" >&2
  exit 1
fi

if [ "$(docker inspect --format '{{.State.Running}}' "$CONTAINER_NAME" 2>/dev/null || true)" != "true" ]; then
  echo "PostgreSQL container is not running: $CONTAINER_NAME" >&2
  exit 1
fi

cleanup() {
  docker exec "$CONTAINER_NAME" rm -f \
    "$CONTAINER_DATABASE_BACKUP_FILE" "$CONTAINER_GLOBALS_BACKUP_FILE" \
    >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker cp "$DATABASE_BACKUP_FILE" "$CONTAINER_NAME:$CONTAINER_DATABASE_BACKUP_FILE"
docker cp "$GLOBALS_BACKUP_FILE" "$CONTAINER_NAME:$CONTAINER_GLOBALS_BACKUP_FILE"
docker exec "$CONTAINER_NAME" sh -eu -c '
  pg_restore --list "$1" >/dev/null

  # The Docker image creates POSTGRES_USER during initialization. Preserve that
  # role creation error-free while restoring its remaining role attributes.
  sed "/^CREATE ROLE ${POSTGRES_USER};$/d" "$2" |
    psql --username="$POSTGRES_USER" --dbname=postgres --set=ON_ERROR_STOP=1

  dropdb --if-exists --force --username="$POSTGRES_USER" "$POSTGRES_DB"
  pg_restore --create --exit-on-error --username="$POSTGRES_USER" \
    --dbname=postgres "$1"
  psql --username="$POSTGRES_USER" --dbname="$POSTGRES_DB" \
    --set=ON_ERROR_STOP=1 --command="SELECT 1" >/dev/null
' sh "$CONTAINER_DATABASE_BACKUP_FILE" "$CONTAINER_GLOBALS_BACKUP_FILE"

echo "PostgreSQL backup restored into $CONTAINER_NAME"
