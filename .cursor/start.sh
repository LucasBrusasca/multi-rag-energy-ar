#!/usr/bin/env bash
# Per-boot startup: bring PostgreSQL online. Idempotent and non-blocking.
set -euo pipefail

PG_VERSION=16

# Start the cluster if it is not already running.
sudo pg_ctlcluster "${PG_VERSION}" main start 2>/dev/null || true

# Wait (bounded) until the server accepts connections.
for _ in $(seq 1 30); do
  if sudo -u postgres pg_isready -q; then
    echo "PostgreSQL ${PG_VERSION} is ready."
    exit 0
  fi
  sleep 1
done

echo "PostgreSQL ${PG_VERSION} did not become ready in time." >&2
exit 1
