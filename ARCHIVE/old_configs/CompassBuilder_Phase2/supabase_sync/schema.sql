-- add supabase insert

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Prompt modules table
CREATE TABLE prompt_modules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    version TEXT NOT NULL,
    type TEXT NOT NULL,
    yaml JSONB NOT NULL,
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    status TEXT DEFAULT 'active',
    metadata JSONB DEFAULT '{}'
);

-- Version history table
CREATE TABLE prompt_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    module_id UUID REFERENCES prompt_modules(id),
    version TEXT NOT NULL,
    yaml JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    changes TEXT,
    created_by TEXT
);

-- Insert function with versioning
CREATE OR REPLACE FUNCTION insert_prompt_module(
    p_title TEXT,
    p_version TEXT,
    p_type TEXT,
    p_yaml JSONB,
    p_tags TEXT[] DEFAULT '{}',
    p_created_by TEXT DEFAULT NULL
) RETURNS UUID AS $$
DECLARE
    v_module_id UUID;
BEGIN
    -- Insert new module
    INSERT INTO prompt_modules (title, version, type, yaml, tags)
    VALUES (p_title, p_version, p_type, p_yaml, p_tags)
    RETURNING id INTO v_module_id;
    
    -- Create initial version
    INSERT INTO prompt_versions (module_id, version, yaml, created_by)
    VALUES (v_module_id, p_version, p_yaml, p_created_by);
    
    RETURN v_module_id;
END;
$$ LANGUAGE plpgsql;

-- Update function with version tracking
CREATE OR REPLACE FUNCTION update_prompt_module(
    p_id UUID,
    p_version TEXT,
    p_yaml JSONB,
    p_changes TEXT DEFAULT NULL,
    p_created_by TEXT DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    -- Update module
    UPDATE prompt_modules
    SET version = p_version,
        yaml = p_yaml,
        last_updated = NOW()
    WHERE id = p_id;
    
    -- Create new version
    INSERT INTO prompt_versions (module_id, version, yaml, changes, created_by)
    VALUES (p_id, p_version, p_yaml, p_changes, p_created_by);
END;
$$ LANGUAGE plpgsql;

-- Add indexes
CREATE INDEX idx_prompt_modules_type ON prompt_modules(type);
CREATE INDEX idx_prompt_modules_tags ON prompt_modules USING gin(tags);
CREATE INDEX idx_prompt_versions_module ON prompt_versions(module_id);

-- Add RLS policies
ALTER TABLE prompt_modules ENABLE ROW LEVEL SECURITY;
ALTER TABLE prompt_versions ENABLE ROW LEVEL SECURITY;

-- Allow read access to authenticated users
CREATE POLICY "Allow read access to authenticated users"
ON prompt_modules FOR SELECT
TO authenticated
USING (true);

-- Allow write access to authenticated users
CREATE POLICY "Allow write access to authenticated users"
ON prompt_modules FOR INSERT
TO authenticated
WITH CHECK (true);

CREATE POLICY "Allow update access to authenticated users"
ON prompt_modules FOR UPDATE
TO authenticated
USING (true)
WITH CHECK (true);
