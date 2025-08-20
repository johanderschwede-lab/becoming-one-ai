#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────────────────────
# Compass Core — Supabase + FastAPI bootstrap
# Creates a minimal, durable, versioned "Compass" repo you can open in Cursor.
# ─────────────────────────────────────────────────────────────────────────────

PROJECT_DIR="compass-core"
PY_REQ_FILE="requirements.txt"

echo "Creating project at ./${PROJECT_DIR}"
mkdir -p "${PROJECT_DIR}"/{apps/api,core,scripts,tests,snapshots,ops,db}
cd "${PROJECT_DIR}"

# ── .gitignore ───────────────────────────────────────────────────────────────
cat > .gitignore <<'EOF'
.venv/
__pycache__/
*.pyc
.env
.env.local
.DS_Store
snapshots/*.yaml
EOF

# ── requirements.txt ─────────────────────────────────────────────────────────
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

# ── .env.example (copy to .env and fill values) ──────────────────────────────
cat > .env.example <<'EOF'
# Supabase direct Postgres connection URI (Project Settings → Database → Connection string → URI)
# Example: postgresql://postgres:<PASSWORD>@db.<HASH>.supabase.co:5432/postgres
SUPABASE_DB_URL=

# Optional (not used in code yet, reserved)
SUPABASE_URL=
SUPABASE_SERVICE_KEY=

# Compass config
COMPASS_PROJECT_PREFIX=compass-2025-08-v1
ADMIN_TOKEN=replace-me-with-a-long-random-string
EOF

# ── README.md ────────────────────────────────────────────────────────────────
cat > README.md <<'EOF'
# Compass Core

A lean, durable, versioned "System Compass" for your Telegram/AI orchestration.
- **Supabase (Postgres)** for canonical, versioned memory
- **FastAPI** service for reading active Compass YAML, idea intake, and admin approvals
- **Additive-only auto-growth** without breaking core truths

## Quick start

1) **Create Supabase project** (recommended name: `compass-core`).

2) In Supabase SQL editor, run `db/supabase_migration.sql` (copy-paste its content).

3) Copy environment:
```bash
cp .env.example .env
# Fill SUPABASE_DB_URL (from Supabase > Project Settings > Database > Connection string > URI)
# Set a strong ADMIN_TOKEN
```

4. Create venv & install:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

5. Seed initial Compass version (run in Supabase SQL editor):

```sql
insert into compass.versions (version, status, checksum, created_by, notes)
values ('compass-2025-08-v1.0.0', 'active', 'sha256:placeholder', 'johan', 'initial');

with v as (select id from compass.versions where version='compass-2025-08-v1.0.0')
insert into compass.sections (version_id, name, body)
select id, 'north_star', 'Purpose: TBD\nMission:\n- \n- \n- \n' from v
union all
select id, 'principles', 'Do: freeze scope; fetch canonical memory.\nDont: no unversioned prompts.' from v
union all
select id, 'scope', 'in: telegram, supabase, retrieval, fsm\nout: payments, multiplaform' from v;
```

6. Run API:

```bash
uvicorn apps.api.main:app --reload --port 8000
```

7. Test:

* `GET http://localhost:8000/health` → `{"ok": true}`
* `GET http://localhost:8000/compass/active.yaml` → YAML
* Submit an idea (proposal):

```bash
curl -X POST http://localhost:8000/proposals \
  -H 'Content-Type: application/json' \
  -d '{"submitted_by":"johan","source":"admin","raw_idea":"Add glossary entry for Deep Dive™","normalized":{"target_section":"glossary","change_type":"add","patch":{"text":"Deep Dive™: Our high-dose Amanita format."},"impact":"low"}}'
```

* Approve & merge (replace <ID> with returned proposal id):

```bash
curl -X POST http://localhost:8000/admin/approve/<ID> \
  -H 'X-Admin-Token: <your ADMIN_TOKEN>'
```

8. Snapshot active YAML to DB + local file:

```bash
python scripts/export_snapshot.py
```

Open the repo in **Cursor** and iterate with confidence. Your Compass is now a single source of truth.
EOF

# ── Supabase migration SQL ───────────────────────────────────────────────────

mkdir -p db
cat > db/supabase_migration.sql <<'EOF'
-- Enable required extensions
create extension if not exists pgcrypto;

-- Schema
create schema if not exists compass;

-- Immutable versions
create table if not exists compass.versions (
    id uuid primary key default gen_random_uuid(),
    version text not null unique,                 -- e.g., compass-2025-08-v1.0.0
    status text not null check (status in ('draft','active','archived')),
    checksum text not null,
    created_at timestamptz not null default now(),
    created_by text not null,
    notes text
);

-- Sectioned content (diffable)
create table if not exists compass.sections (
    id uuid primary key default gen_random_uuid(),
    version_id uuid not null references compass.versions(id) on delete cascade,
    name text not null,                           -- north_star, principles, scope, glossary, etc.
    body text not null,
    unique(version_id, name)
);

-- Idea intake → normalized proposals
create table if not exists compass.proposals (
    id uuid primary key default gen_random_uuid(),
    submitted_by text not null,
    source text not null,                         -- telegram | admin | api
    raw_idea text not null,
    normalized jsonb not null,                    -- {target_section, change_type, patch, impact}
    created_at timestamptz not null default now(),
    status text not null default 'queued' check (status in ('queued','approved','rejected','merged')),
    rationale text
);

-- Merge audit trail
create table if not exists compass.merges (
    id uuid primary key default gen_random_uuid(),
    proposal_id uuid not null references compass.proposals(id),
    from_version text not null,
    to_version text not null,
    diff jsonb not null,                          -- e.g. {section:"glossary", old:"...", new:"..."}
    merged_by text not null,
    merged_at timestamptz not null default now()
);

-- Snapshots (full YAML copies)
create table if not exists compass.snapshots (
    id uuid primary key default gen_random_uuid(),
    version text not null,
    yaml text not null,
    created_at timestamptz not null default now()
);

-- Policy toggles (future)
create table if not exists compass.policies (
    id uuid primary key default gen_random_uuid(),
    key text unique not null,                     -- e.g., 'auto_additive_sections'
    value jsonb not null                          -- e.g., ['parked_ideas','glossary','links']
);
EOF

# ── apps/api/main.py ─────────────────────────────────────────────────────────

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

# ── DB helper ────────────────────────────────────────────────────────────────

def pg_conn():
    return psycopg.connect(S.SUPABASE_DB_URL)

def _parse_semver_suffix(version: str) -> SemVer:
    """Expecting version like PREFIX.<semver> e.g., compass-2025-08-v1.0.0"""
    prefix = S.COMPASS_PROJECT_PREFIX + "."
    if not version.startswith(prefix):
        raise ValueError(f"Version '{version}' does not start with prefix '{prefix}'")
    return SemVer.parse(version[len(prefix):])

def _compose_version(semver_obj: SemVer) -> str:
    return f"{S.COMPASS_PROJECT_PREFIX}.{semver_obj}"

def _active_version(conn) -> Tuple[str, str]:
    """Return (version, version_id) for highest active semver matching prefix."""
    with conn.cursor() as cur:
        cur.execute("""
            select version, id from compass.versions
            where status='active' and version like %s
        """, (f"{S.COMPASS_PROJECT_PREFIX}%",))
        rows = cur.fetchall()
        if not rows:
            raise HTTPException(404, "No active version found")
        rows_sorted = sorted(rows, key=lambda r: _parse_semver_suffix(r[0]))
        return rows_sorted[-1][0], rows_sorted[-1][1]

def _sections_for_version(conn, version: str) -> Tuple[Dict[str,str], str]:
    with conn.cursor() as cur:
        cur.execute("""
            select v.id, s.name, s.body
            from compass.versions v
            join compass.sections s on s.version_id = v.id
            where v.version = %s
            order by s.name asc
        """, (version,))
        rows = cur.fetchall()
        if not rows:
            raise HTTPException(404, f"No sections found for version {version}")
        version_id = rows[0][0]
        sections = {name: body for _, name, body in rows}
        return sections, version_id

def _assemble_yaml(prefix: str, version: str, sections: Dict[str,str]) -> str:
    data = {
        "id": prefix,
        "version": version,
        "sections": sections
    }
    return yaml.safe_dump(data, sort_keys=True)

def _checksum(yaml_text: str) -> str:
    return "sha256:" + hashlib.sha256(yaml_text.encode("utf-8")).hexdigest()

# ── Models ───────────────────────────────────────────────────────────────────

class ProposalIn(BaseModel):
    submitted_by: str
    source: str
    raw_idea: str
    normalized: dict  # {target_section, change_type, patch, impact}

# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/compass/active.yaml")
def get_active_yaml():
    with pg_conn() as conn:
        active_version, _ = _active_version(conn)
        sections, _ = _sections_for_version(conn, active_version)
        yml = _assemble_yaml(S.COMPASS_PROJECT_PREFIX, active_version, sections)
        return Response(content=yml, media_type="text/yaml")

@app.post("/proposals")
def submit_proposal(p: ProposalIn):
    with pg_conn() as conn, conn.cursor() as cur:
        cur.execute("""
            insert into compass.proposals (submitted_by, source, raw_idea, normalized)
            values (%s, %s, %s, %s) returning id
        """, (p.submitted_by, p.source, p.raw_idea, Json(p.normalized)))
        pid = cur.fetchone()[0]
        conn.commit()
        return {"id": str(pid), "status": "queued"}

def _apply_additive_patch(sections: Dict[str,str], target: str, patch: Dict[str,Any]) -> Dict[str,str]:
    text = patch.get("text", "")
    if not text:
        raise HTTPException(400, "Patch missing 'text'")
    existing = sections.get(target, "")
    new_body = (existing + ("\n" if existing and not existing.endswith("\n") else "") + text + "\n").lstrip()
    s2 = dict(sections)
    s2[target] = new_body
    return s2

def _clone_with_bump(conn, from_version: str, sections: Dict[str,str], created_by: str, notes: str) -> str:
    # bump patch version
    sv = _parse_semver_suffix(from_version).bump_patch()
    new_version = _compose_version(sv)
    yml = _assemble_yaml(S.COMPASS_PROJECT_PREFIX, new_version, sections)
    chksum = _checksum(yml)
    with conn.cursor() as cur:
        # archive previous active
        cur.execute("update compass.versions set status='archived' where version = %s", (from_version,))
        # create new active version
        cur.execute("""
            insert into compass.versions (version, status, checksum, created_by, notes)
            values (%s, 'active', %s, %s, %s) returning id
        """, (new_version, chksum, created_by, notes))
        new_vid = cur.fetchone()[0]
        # insert sections
        for name, body in sections.items():
            cur.execute("""
                insert into compass.sections (version_id, name, body)
                values (%s, %s, %s)
            """, (new_vid, name, body))
        return new_version

@app.post("/admin/approve/{proposal_id}")
def approve_and_merge(proposal_id: str, x_admin_token: Optional[str] = Header(default=None)):
    if x_admin_token != S.ADMIN_TOKEN:
        raise HTTPException(401, "Unauthorized")

    with pg_conn() as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute("select submitted_by, source, raw_idea, normalized, status from compass.proposals where id = %s", (proposal_id,))
                row = cur.fetchone()
                if not row:
                    raise HTTPException(404, "Proposal not found")
                submitted_by, source, raw_idea, normalized, status = row
                if status not in ("queued", "approved"):
                    raise HTTPException(400, f"Proposal status is '{status}', cannot merge")

                target = normalized.get("target_section")
                change_type = normalized.get("change_type")
                patch = normalized.get("patch", {})
                impact = normalized.get("impact", "low")

                active_version, _ = _active_version(conn)
                sections, _vid = _sections_for_version(conn, active_version)

                if change_type == "add":
                    merged_sections = _apply_additive_patch(sections, target, patch)
                else:
                    raise HTTPException(400, f"Unsupported change_type '{change_type}' in MVP")

                # Prepare diff
                old_body = sections.get(target, "")
                new_body = merged_sections.get(target, "")
                diff = {"section": target, "old": old_body, "new": new_body, "change_type": change_type, "impact": impact}

                # Create new version (patch bump)
                new_version = _clone_with_bump(conn, active_version, merged_sections, created_by="admin", notes=f"merge proposal {proposal_id}")

                # Mark proposal merged
                cur.execute("update compass.proposals set status='merged', rationale=%s where id=%s",
                            (f"Merged into {new_version}", proposal_id))
                # Record merge
                cur.execute("""
                    insert into compass.merges (proposal_id, from_version, to_version, diff, merged_by)
                    values (%s, %s, %s, %s, %s)
                """, (proposal_id, active_version, new_version, Json(diff), "admin"))

        conn.commit()
        return {"ok": True, "merged_version": new_version}
EOF

# ── scripts/export_snapshot.py ───────────────────────────────────────────────

cat > scripts/export_snapshot.py <<'EOF'
import os, hashlib, yaml, datetime, pathlib, psycopg
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_DB_URL: str
    COMPASS_PROJECT_PREFIX: str = "compass-2025-08-v1"
    class Config: env_file = ".env"

S = Settings()
SNAP_DIR = pathlib.Path("snapshots")

def active_version(conn):
    with conn.cursor() as cur:
        cur.execute("""
            select version from compass.versions
            where status='active' and version like %s
        """, (f"{S.COMPASS_PROJECT_PREFIX}%",))
        rows = [r[0] for r in cur.fetchall()]
        if not rows:
            raise RuntimeError("No active version found")
        from semver import VersionInfo as SemVer
        rows_sorted = sorted(rows, key=lambda v: SemVer.parse(v.split(S.COMPASS_PROJECT_PREFIX + ".")[-1]))
        return rows_sorted[-1]

def sections(conn, version):
    with conn.cursor() as cur:
        cur.execute("""
            select s.name, s.body
            from compass.versions v
            join compass.sections s on s.version_id = v.id
            where v.version = %s
            order by s.name asc
        """, (version,))
        return dict(cur.fetchall())

def main():
    SNAP_DIR.mkdir(parents=True, exist_ok=True)
    with psycopg.connect(S.SUPABASE_DB_URL) as conn:
        v = active_version(conn)
        secs = sections(conn, v)
        data = {"id": S.COMPASS_PROJECT_PREFIX, "version": v, "sections": secs}
        yml = yaml.safe_dump(data, sort_keys=True)

        # Write to DB
        with conn.cursor() as cur:
            cur.execute("""
                insert into compass.snapshots (version, yaml) values (%s, %s)
            """, (v, yml))
            conn.commit()

        # Write local file
        ts = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
        path = SNAP_DIR / f"{v}-{ts}.yaml"
        path.write_text(yml, encoding="utf-8")
        print(f"Snapshot written: {path}")

if __name__ == "__main__":
    main()
EOF

# ── Finish up ────────────────────────────────────────────────────────────────

echo ""
echo "✅ Bootstrap complete."
echo "Next steps:"
echo "1) Open Supabase, create project, run: db/supabase_migration.sql"
echo "2) cp .env.example .env  # then fill SUPABASE_DB_URL and ADMIN_TOKEN"
echo "3) python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
echo "4) uvicorn apps.api.main:app --reload --port 8000"
echo "5) GET http://localhost:8000/compass/active.yaml  # should return YAML"

