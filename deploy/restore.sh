#!/bin/bash
# Replaces the whole database with a dump written by backup.sh:
#
#   deploy/restore.sh /var/backups/caramelcase/caramelcase-20261118T030000Z.dump
#
# The app is down while it works: it stops nginx and the API, saves the
# current database beside the backups (before-restore-<time>.dump, which
# backup.sh never deletes), drops and recreates the database, restores the
# dump and starts everything again. docs/RUNBOOK.md, "Backup and restore".
set -euo pipefail

if [ $# -ne 1 ] || [ ! -f "$1" ]; then
    echo "usage: $0 <dump file written by backup.sh>" >&2
    exit 2
fi
dump="$(cd "$(dirname "$1")" && pwd)/$(basename "$1")"
cd "$(dirname "$0")"

set -a
# shellcheck source=/dev/null
source ./.env
set +a
backup_dir="${BACKUP_DIR:-/var/backups/caramelcase}"

echo "This replaces the database $POSTGRES_DB with $dump."
echo "Everything written to it since that dump will be gone."
read -r -p "Type the database's name to go on: " answer
if [ "$answer" != "$POSTGRES_DB" ]; then
    echo "Nothing was changed."
    exit 1
fi

echo "Stopping nginx and the API..."
docker compose stop nginx api

umask 077
mkdir -p "$backup_dir"
current="$backup_dir/before-restore-$(date -u +%Y%m%dT%H%M%SZ).dump"
echo "Saving the current database to $current..."
docker compose exec -T db sh -c \
    'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom' \
    > "$current"

echo "Recreating the database and restoring the dump..."
docker compose exec -T db sh -c \
    'dropdb -U "$POSTGRES_USER" --force "$POSTGRES_DB" && createdb -U "$POSTGRES_USER" "$POSTGRES_DB"'
docker compose exec -T db sh -c \
    'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --exit-on-error' \
    < "$dump"

echo "Starting everything again..."
docker compose up -d --wait
echo "Restored $dump."
