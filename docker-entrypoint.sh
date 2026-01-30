#!/bin/sh
# docker-entrypoint.sh (bash)
set -e

# Ensure runtime-owned dirs are correct (safe if they are host-mounted)
for d in /var/lib/tor1 /var/lib/tor2 /var/lib/tor3 /var/lib/tor4 /var/log/tor; do
  if [ -e "$d" ]; then
    chown -R debian-tor:debian-tor "$d" || true
    chmod 700 "$d" || true
  fi
done

# Allow passing through alternative command
exec "$@"
