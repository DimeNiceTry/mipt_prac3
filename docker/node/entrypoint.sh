#!/bin/sh
set -eu

mkdir -p /run/sshd /root/.ssh /hostkeys
chmod 700 /root/.ssh
cp /publickeys/authorized_keys /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys
if [ ! -s /hostkeys/ssh_host_ed25519_key ]; then
    ssh-keygen -q -t ed25519 -N '' -f /hostkeys/ssh_host_ed25519_key
fi
chmod 600 /hostkeys/ssh_host_ed25519_key

if command -v supervisord >/dev/null 2>&1; then
    supervisord -c /etc/supervisor/supervisord.conf
fi
exec /usr/sbin/sshd -D -e
