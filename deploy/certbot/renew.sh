#!/bin/bash
# Renews the TLS certificate if it is close to expiry, then has nginx load
# it. Run every day by cron (renew_cron, installed by certbot.sh).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "$(date -u +%FT%TZ) checking the certificate..."
docker compose run --rm certbot renew
docker compose exec -T nginx nginx -s reload
echo "$(date -u +%FT%TZ) done"
