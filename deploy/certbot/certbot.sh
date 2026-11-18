#!/bin/bash
# The first TLS certificate for DOMAIN, then the cron job that renews it.
#
# Run once on the server, as root (it writes /etc/cron.d), before the first
# deploy. DOMAIN must already point at the server, ports 80 and 443 must be
# open, and nothing else may be listening on port 80.
set -euo pipefail
cd "$(dirname "$0")/.."

set -a
# shellcheck source=/dev/null
source ./.env
set +a

echo "Starting nginx with the first-certificate configuration..."
# It serves certbot's challenge only, so it needs neither a certificate nor
# the API. The variable overrides NGINX_CONF_FILE of .env for this command.
NGINX_CONF_FILE=default.conf.https.temp \
    docker compose up -d --no-deps --force-recreate nginx

echo "Asking Let's Encrypt for a certificate..."
# Let's Encrypt limits how many certificates a domain gets each week. To
# try this script, add --staging to the command below.
docker compose run --rm certbot certonly \
    --webroot --webroot-path=/var/www/certbot \
    --email "$CERTBOT_EMAIL" --agree-tos --no-eff-email \
    -d "$DOMAIN"

echo "Stopping the temporary nginx..."
docker compose rm --stop --force nginx

echo "Installing the renewal cron job..."
# shellcheck disable=SC2016 # envsubst fills in this one variable
envsubst '${PROJECT_ROOT}' < certbot/renew_cron > /etc/cron.d/caramelcase_renew
chmod 644 /etc/cron.d/caramelcase_renew

echo "Done. With NGINX_CONF_FILE=default.conf.https in deploy/.env, deploy:"
echo "  deploy/scripts/deploy.sh"
