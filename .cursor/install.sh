#!/usr/bin/env bash
# Idempotent one-time setup for the Multi-RAG dev environment.
# Runs after the repository is checked out. Safe to run repeatedly.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

PG_VERSION=16
DB_USER="${DB_USER:-multirag}"
DB_PASSWORD="${DB_PASSWORD:-multirag}"
DB_NAME="${DB_NAME:-multirag}"
DB_PORT="${DB_PORT:-5432}"

echo "==> Installing system packages (PostgreSQL ${PG_VERSION} + pgvector, python venv)"
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -qq
sudo apt-get install -y -qq \
  "postgresql-${PG_VERSION}" \
  "postgresql-${PG_VERSION}-pgvector" \
  "postgresql-client-${PG_VERSION}" \
  python3.12-venv

echo "==> Creating Python virtual environment (.venv)"
if [ ! -x ".venv/bin/python" ]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip wheel setuptools
pip install -r requirements.txt

echo "==> Writing .env if absent"
if [ ! -f ".env" ]; then
  cat > .env <<EOF
DB_HOST=localhost
DB_PORT=${DB_PORT}
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}

# LLM provider key (LiteLLM). Required only for generation/judge steps.
# ANTHROPIC_API_KEY=sk-ant-...
EOF
fi

echo "==> Starting PostgreSQL cluster"
sudo pg_ctlcluster "${PG_VERSION}" main start 2>/dev/null || true
# Wait until the server accepts connections.
for _ in $(seq 1 30); do
  if sudo -u postgres pg_isready -q; then break; fi
  sleep 1
done

echo "==> Ensuring role and database exist (idempotent)"
sudo -u postgres psql -v ON_ERROR_STOP=1 <<SQL
DO \$\$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname='${DB_USER}') THEN
    CREATE ROLE ${DB_USER} LOGIN PASSWORD '${DB_PASSWORD}';
  END IF;
END \$\$;
SQL
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" | grep -q 1; then
  sudo -u postgres createdb -O "${DB_USER}" "${DB_NAME}"
fi
sudo -u postgres psql -d "${DB_NAME}" -c "GRANT ALL ON SCHEMA public TO ${DB_USER};" >/dev/null

echo "==> Enabling pgvector extension (requires superuser)"
sudo -u postgres psql -d "${DB_NAME}" -c "CREATE EXTENSION IF NOT EXISTS vector;" >/dev/null

echo "==> Applying database schema (chunks table + indexes)"
# apply_schema.py uses flat imports, so run it from the ingestion package dir.
( cd src/ingestion && "${REPO_ROOT}/.venv/bin/python" apply_schema.py )

echo "==> Install complete."
