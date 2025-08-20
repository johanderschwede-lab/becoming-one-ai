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
