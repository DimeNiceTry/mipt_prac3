#!/bin/sh
set -eu

mkdir -p /root/.ssh /publickeys
chmod 700 /root/.ssh
if [ ! -s /root/.ssh/id_ed25519 ]; then
    ssh-keygen -q -t ed25519 -N '' -f /root/.ssh/id_ed25519
fi
chmod 600 /root/.ssh/id_ed25519
cp /root/.ssh/id_ed25519.pub /publickeys/authorized_keys
chmod 644 /publickeys/authorized_keys

exec "$@"
