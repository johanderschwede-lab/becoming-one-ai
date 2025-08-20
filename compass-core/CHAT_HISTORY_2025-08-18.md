# Chat History - Compass Core Bootstrap (2025-08-18)

This file preserves the key conversation context that led to the creation of the `compass-core` scaffold and bootstrap scripts. It is intended as a durable reference inside the repo, so future sessions (and different AI tools) can anchor to the same decisions.

> Note: This is an excerpted, consolidated record focusing on decisions, instructions, and scripts. The user provided a long chat transcript; this document captures the actionable parts and the bootstrap script inlined for convenience.

---

## Summary of Decisions

- Keep it Python-first (FastAPI + Supabase Postgres). No Make.com/Notion required for core.
- Use an append-only, versioned "Compass" schema for immutable versions and additive merges.
- Add proposal intake and admin approval → create new version with diff and checksum.
- Ship a minimal API: `/health`, `/compass/active.yaml`, `/proposals`, `/admin/approve/{id}`.
- Store daily snapshots (optional script provided).
- Railway/GitHub can be added for CI/CD; Supabase SQL migration lives in `db/supabase_migration.sql`.

---

## Bootstrap Script (as provided)

The following script was used to scaffold the repo and create all essential files. Save as `bootstrap_compass_core.sh` and run with `bash bootstrap_compass_core.sh`.

```bash
#!/usr/bin/env bash
set -euo pipefail

# Compass Core — Supabase + FastAPI bootstrap
PROJECT_DIR="compass-core"
PY_REQ_FILE="requirements.txt"

echo "Creating project at ./${PROJECT_DIR}"
mkdir -p "${PROJECT_DIR}"/{apps/api,core,scripts,tests,snapshots,ops,db}
cd "${PROJECT_DIR}"

cat > .gitignore <<'EOF'
.venv/
__pycache__/
*.pyc
.env
.env.local
.DS_Store
snapshots/*.yaml
EOF

cat > "${PY_REQ_FILE}" <<'EOF'
fastapi==0.111.0
uvicorn==0.30.1
pydantic==2.7.1
pydantic-settings==2.3.0
psycopg[binary]==3.1.19
PyYAML==6.0.1
python-dotenv==1.0.1
httpx==0.27.0
semver==3.0.2
EOF

cat > .env.example <<'EOF'
SUPABASE_DB_URL=
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
COMPASS_PROJECT_PREFIX=compass-2025-08-v1
ADMIN_TOKEN=replace-me-with-a-long-random-string
EOF

cat > README.md <<'EOF'
# Compass Core

... (omitted here for brevity – see repo README.md) ...
EOF

mkdir -p db
cat > db/supabase_migration.sql <<'EOF'
-- Enable required extensions
create extension if not exists pgcrypto;

-- Schema
create schema if not exists compass;

-- Versions
create table if not exists compass.versions (
  id uuid primary key default gen_random_uuid(),
  version text not null unique,
  status text not null check (status in ('draft','active','archived')),
  checksum text not null,
  created_at timestamptz not null default now(),
  created_by text not null,
  notes text
);

-- Sections
your tables here per the file in repo
EOF

cat > apps/api/main.py <<'EOF'
from fastapi import FastAPI, HTTPException, Response, Header
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Tuple, Any
import os, hashlib, yaml
import psycopg
from psycopg.types.json import Json
from semver import VersionInfo as SemVer

class Settings(BaseSettings):
    SUPABASE_DB_URL: str
    COMPASS_PROJECT_PREFIX: str = "compass-2025-08-v1"
    ADMIN_TOKEN: str = "replace-me"
    class Config:
        env_file = ".env"

S = Settings()
app = FastAPI(title="Compass Core API")

# DB helpers ... (full content in repo)
EOF

cat > scripts/export_snapshot.py <<'EOF'
# see repo scripts/export_snapshot.py
EOF

echo "✅ Bootstrap complete." 
```

> The actual repository contains the complete files; this inline script is a record of what was generated.

---

## Minimal API Endpoints

- `GET /health` → `{ "ok": true }`
- `GET /compass/active.yaml` → returns YAML with `id`, `version`, `sections`.
- `POST /proposals` → insert new idea/proposal.
- `POST /admin/approve/{proposal_id}` → admin merges proposal (additive), bumps patch version.

---

## Next Steps Checklist

- [ ] Edit `.env` (use `scripts/secure_env_setup.sh` to set secrets safely)
- [ ] Run SQL in Supabase: `db/supabase_migration.sql`
- [ ] Seed initial version via Supabase SQL editor
- [ ] Start API: `uvicorn apps.api.main:app --reload --port 8000`
- [ ] Test: `/health`, `/compass/active.yaml`
- [ ] Optional: Add CI and Railway deploy

---

## Notes

- `requirements.txt` updated in the working session to use a Python 3.9–compatible `psycopg[binary]==3.2.9` in the repo root.
- `scripts/secure_env_setup.sh` allows interactive or env-driven secret setup (non-echo). Set `SEC_SUPABASE_DB_URL` and `SEC_ADMIN_TOKEN` to run non-interactively.

---

This file was created to anchor project memory inside the repo and prevent drift across sessions/tools.

