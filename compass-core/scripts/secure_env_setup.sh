#!/usr/bin/env bash
set -euo pipefail

ENV_FILE=".env"

PREFIX_DEFAULT="${SEC_COMPASS_PREFIX:-compass-2025-08-v1}"

if [[ -n "${SEC_SUPABASE_DB_URL:-}" && -n "${SEC_ADMIN_TOKEN:-}" ]]; then
  echo "Non-interactive mode: using SEC_SUPABASE_DB_URL and SEC_ADMIN_TOKEN from environment."
  SUPABASE_DB_URL="$SEC_SUPABASE_DB_URL"
  ADMIN_TOKEN="$SEC_ADMIN_TOKEN"
  PREFIX_INPUT="$PREFIX_DEFAULT"
else
  echo "This will create/update ${ENV_FILE} locally. Values are not echoed."
  read -r -p "Project prefix [${PREFIX_DEFAULT}]: " PREFIX_INPUT || true
  PREFIX_INPUT=${PREFIX_INPUT:-$PREFIX_DEFAULT}
  read -r -s -p "Paste SUPABASE_DB_URL (postgresql://...): " SUPABASE_DB_URL; echo
  read -r -s -p "Set ADMIN_TOKEN (long random string): " ADMIN_TOKEN; echo
fi

{
  echo "# Generated $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "SUPABASE_DB_URL=${SUPABASE_DB_URL}"
  echo "COMPASS_PROJECT_PREFIX=${PREFIX_INPUT}"
  echo "ADMIN_TOKEN=${ADMIN_TOKEN}"
} > "${ENV_FILE}"

chmod 600 "${ENV_FILE}"
echo "Wrote ${ENV_FILE} (600)."
