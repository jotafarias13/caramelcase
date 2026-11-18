#!/bin/bash
# What a fresh Ubuntu server needs before the first deploy: Docker with its
# compose plugin, git, make, and envsubst (gettext-base) for the cron jobs.
# Run once, as root: sudo deploy/scripts/install_server.sh
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "Run it as root: sudo $0" >&2
    exit 1
fi

echo "Installing git, make, envsubst and Docker's prerequisites..."
apt-get update -y
apt-get install -y ca-certificates curl gnupg git make gettext-base

echo "Adding Docker's apt repository..."
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | gpg --dearmor --yes -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
# shellcheck source=/dev/null
codename="$(. /etc/os-release && echo "$VERSION_CODENAME")"
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $codename stable" \
    > /etc/apt/sources.list.d/docker.list

echo "Installing Docker..."
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io \
    docker-buildx-plugin docker-compose-plugin

echo "Done: $(docker --version), $(docker compose version)"
