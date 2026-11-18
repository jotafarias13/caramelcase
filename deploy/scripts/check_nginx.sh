#!/bin/bash
# Runs `nginx -t` on each of the three configurations, in the nginx image
# the web app is served by, with a throwaway certificate for the https one.
# CI runs it; run it after changing anything in deploy/nginx/.
set -euo pipefail
cd "$(dirname "$0")/.."

image=$(sed -n 's/^FROM \(nginx:[^ ]*\).*/\1/p' web.Dockerfile)
domain=example.com
certificates=$(mktemp -d)
trap 'rm -rf "$certificates"' EXIT

mkdir -p "$certificates/live/$domain"
openssl req -x509 -newkey rsa:2048 -nodes -days 1 -subj "/CN=$domain" \
    -keyout "$certificates/live/$domain/privkey.pem" \
    -out "$certificates/live/$domain/fullchain.pem" 2> /dev/null

for conf in default.conf.http default.conf.https default.conf.https.temp; do
    echo "$conf:"
    docker run --rm \
        -e DOMAIN="$domain" \
        -e NGINX_ENTRYPOINT_QUIET_LOGS=1 \
        -v "$PWD/nginx/nginx.conf:/etc/nginx/nginx.conf:ro" \
        -v "$PWD/nginx/app.conf:/etc/nginx/app.conf:ro" \
        -v "$PWD/nginx/$conf:/etc/nginx/templates/default.conf.template:ro" \
        -v "$certificates:/etc/nginx/ssl:ro" \
        "$image" nginx -t
done
