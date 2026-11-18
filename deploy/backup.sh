#!/bin/bash
# A dump of the production database, run every night by cron (backup_cron).
# Keeps the newest BACKUP_KEEP dumps (14) in BACKUP_DIR and deletes older
# ones. Restoring one: docs/RUNBOOK.md, "Backup and restore".
set -euo pipefail
cd "$(dirname "$0")"

set -a
# shellcheck source=/dev/null
source ./.env
set +a

backup_dir="${BACKUP_DIR:-/var/backups/caramelcase}"
keep="${BACKUP_KEEP:-14}"

# The dumps hold students' data: readable by their owner only.
umask 077
mkdir -p "$backup_dir"
file="$backup_dir/caramelcase-$(date -u +%Y%m%dT%H%M%SZ).dump"
trap 'rm -f "$file.partial"' EXIT

# pg_dump runs inside the database container, with its user and database.
# The custom format is compressed and restored with pg_restore.
docker compose exec -T db sh -c \
    'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --format=custom' \
    > "$file.partial"
mv "$file.partial" "$file"
echo "$(date -u +%FT%TZ) wrote $file ($(du -h "$file" | cut -f1))"

# The names sort by date, oldest first: delete all but the newest $keep.
dumps=("$backup_dir"/caramelcase-*.dump)
excess=$((${#dumps[@]} - keep))
for ((i = 0; i < excess; i++)); do
    rm -- "${dumps[$i]}"
    echo "deleted ${dumps[$i]}"
done
