-- Compass system tables for Supabase

-- Core compass metadata and content
CREATE TABLE compass_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    version VARCHAR NOT NULL,
    status VARCHAR NOT NULL CHECK (status IN ('draft', 'active', 'archived')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    activated_at TIMESTAMPTZ,
    created_by UUID NOT NULL,
    checksum VARCHAR NOT NULL,
    UNIQUE (version)
);

-- Individual compass components
CREATE TABLE compass_components (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    compass_version_id UUID NOT NULL REFERENCES compass_versions(id),
    component_type VARCHAR NOT NULL,
    content JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (compass_version_id, component_type)
);

-- Audit trail for compass changes
CREATE TABLE compass_audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    compass_version_id UUID NOT NULL REFERENCES compass_versions(id),
    action VARCHAR NOT NULL,
    changes JSONB NOT NULL,
    performed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    performed_by UUID NOT NULL
);

-- Enable RLS
ALTER TABLE compass_versions ENABLE ROW LEVEL SECURITY;
ALTER TABLE compass_components ENABLE ROW LEVEL SECURITY;
ALTER TABLE compass_audit_log ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Enable read access for authenticated users"
ON compass_versions
FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Enable read access for authenticated users"
ON compass_components
FOR SELECT
TO authenticated
USING (true);

CREATE POLICY "Enable read access for authenticated users"
ON compass_audit_log
FOR SELECT
TO authenticated
USING (true);

-- Only allow inserts through our API functions
CREATE POLICY "Enable insert for authenticated users through API"
ON compass_versions
FOR INSERT
TO authenticated
WITH CHECK (false);  -- Prevent direct inserts

CREATE POLICY "Enable insert for authenticated users through API"
ON compass_components
FOR INSERT
TO authenticated
WITH CHECK (false);  -- Prevent direct inserts

-- Functions for managing compass versions
CREATE OR REPLACE FUNCTION create_compass_version(
    p_version VARCHAR,
    p_content JSONB,
    p_created_by UUID
) RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_compass_id UUID;
BEGIN
    -- Insert new compass version
    INSERT INTO compass_versions (version, status, created_by, checksum)
    VALUES (p_version, 'draft', p_created_by, encode(sha256(p_content::text::bytea), 'hex'))
    RETURNING id INTO v_compass_id;

    -- Insert components
    INSERT INTO compass_components (compass_version_id, component_type, content)
    SELECT 
        v_compass_id,
        key,
        value
    FROM jsonb_each(p_content);

    -- Log the creation
    INSERT INTO compass_audit_log (compass_version_id, action, changes, performed_by)
    VALUES (v_compass_id, 'create', p_content, p_created_by);

    RETURN v_compass_id;
END;
$$;