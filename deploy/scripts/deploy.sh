#!/bin/bash
# Deploys the images named in deploy/.env: pulls them, checks nginx's
# configuration, migrates the database, restarts, and waits until every
# service is healthy. If the new images do not come up healthy, the
# previous ones are started again.
#
# Run on the server after `git pull` (the deploy workflow does both), from
# anywhere. Migrations are not undone by a rollback: write them so that the
# previous version of the API still runs on the new schema.
set -euo pipefail
cd "$(dirname "$0")/.."

set -a
# shellcheck source=/dev/null
source ./.env
set +a

images=("$DOCKER_IMAGE_API:$DOCKER_TAG" "$DOCKER_IMAGE_WEB:$DOCKER_TAG")
wait_seconds=180

step() {
    echo
    echo "==> $*"
}

put_back_previous_images() {
    for image in "${images[@]}"; do
        if docker image inspect "$image-bkp" > /dev/null 2>&1; then
            docker tag "$image-bkp" "$image"
            docker rmi "$image-bkp" > /dev/null
            echo "$image is the previous image again"
        fi
    done
}

step "Keeping the current images as a backup"
for image in "${images[@]}"; do
    if docker image inspect "$image" > /dev/null 2>&1; then
        docker tag "$image" "$image-bkp"
        echo "$image -> $image-bkp"
    else
        echo "$image is not on this server yet: no backup"
    fi
done

# Until the new images are started, a failure has changed no running
# container: putting the old tags back is enough.
trap 'echo "Deploy failed; the running containers were not changed."; put_back_previous_images' ERR

step "Pulling the new images"
docker compose pull api nginx

step "Checking nginx's configuration in the new image"
docker compose run --rm --no-deps -e NGINX_ENTRYPOINT_QUIET_LOGS=1 nginx nginx -t

step "Migrating the database"
docker compose up -d --wait db
docker compose run --rm --no-deps api alembic upgrade head

step "Seeding plans, flags, subjects and topics"
docker compose run --rm --no-deps api python -m app.cli seed

trap - ERR

step "Starting the new images"
if docker compose up -d --wait --wait-timeout "$wait_seconds"; then
    for image in "${images[@]}"; do
        docker rmi "$image-bkp" > /dev/null 2>&1 || true
    done
    docker image prune -f > /dev/null
    docker compose ps
    echo
    echo "Deployed: every service is healthy."
    exit 0
fi

step "The new images are not healthy: starting the previous ones"
docker compose logs --tail 40 api nginx || true
put_back_previous_images
docker compose up -d --wait --wait-timeout "$wait_seconds"
docker compose ps
echo
echo "Rolled back to the previous images. Migrations stay applied."
exit 1
