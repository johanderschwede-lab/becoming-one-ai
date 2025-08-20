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
