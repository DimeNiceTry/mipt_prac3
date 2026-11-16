#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
docker compose up -d --build --wait
docker compose exec -T master ansible-playbook site.yml
