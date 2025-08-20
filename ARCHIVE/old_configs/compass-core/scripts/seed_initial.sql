-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS compass;

-- Create versions table if not exists
CREATE TABLE IF NOT EXISTS compass.versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version TEXT NOT NULL,
    status TEXT NOT NULL,
    checksum TEXT NOT NULL,
    created_by TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create sections table if not exists
CREATE TABLE IF NOT EXISTS compass.sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version_id UUID REFERENCES compass.versions(id),
    name TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create proposals table if not exists
CREATE TABLE IF NOT EXISTS compass.proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submitted_by TEXT NOT NULL,
    source TEXT NOT NULL,
    raw_idea TEXT NOT NULL,
    normalized JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed initial version
insert into compass.versions (version, status, checksum, created_by, notes)
values ('compass-2025-08-v1.0.0', 'active', 'sha256:placeholder', 'Johan', 'initial');

with v as (select id from compass.versions where version='compass-2025-08-v1.0.0')
insert into compass.sections (version_id, name, body)
select id, 'north_star', 'Purpose: TBD\nMission:\n- \n- \n- \n' from v
union all
select id, 'principles', 'Do: freeze scope; fetch canonical memory.\nDont: no unversion' from v
union all
select id, 'scope', 'in: telegram, supabase, retrieval, fsm\nout: payments, multiplafor' from v;

