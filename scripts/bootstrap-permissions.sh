#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECTS_DIR="${PROJECTS_DIR:-${SCRIPT_DIR}/../data/projects}"
IGNITION_UID="${IGNITION_UID:-2003}"

if [[ ! -d "$PROJECTS_DIR" ]]; then
  echo "Error: project directory not found: $PROJECTS_DIR" >&2
  exit 1
fi

HOST_UID="${HOST_UID:-$(stat -c '%u' -- "$PROJECTS_DIR")}"

if ! command -v setfacl >/dev/null 2>&1; then
  echo "Error: setfacl is required. Install the 'acl' package." >&2
  exit 1
fi

if [[ ! "$HOST_UID" =~ ^[0-9]+$ ]] || [[ ! "$IGNITION_UID" =~ ^[0-9]+$ ]]; then
  echo "Error: HOST_UID and IGNITION_UID must be numeric." >&2
  exit 1
fi

trap 'echo "Error: unable to update every ACL. If another UID owns project resources, rerun this script with sudo." >&2' ERR

setfacl -R -m \
  "u:${HOST_UID}:rwX,u:${IGNITION_UID}:rwX,m::rwX" \
  "$PROJECTS_DIR"

while IFS= read -r -d '' directory; do
  setfacl -m \
    "d:u::rwx,d:u:${HOST_UID}:rwx,d:u:${IGNITION_UID}:rwx,d:g::r-x,d:m::rwx,d:o::r-x" \
    "$directory"
done < <(find "$PROJECTS_DIR" -type d -print0)

echo "Configured project access for host UID ${HOST_UID} and Ignition UID ${IGNITION_UID}."
