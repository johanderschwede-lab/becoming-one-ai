-- Becoming One™ AI Journey System - Supabase Schema
-- Phase 1: Foundation Tables

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Identity Registry Table
-- Tracks users across all platforms with unified person_id
CREATE TABLE identity_registry (
    person_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    channel_ids JSONB NOT NULL DEFAULT '{}', -- {"telegram": "123456", "email": "user@example.com"}
    name VARCHAR(255),
    consent BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Event Log Table  
-- Stores all interactions and system events
CREATE TABLE event_log (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID REFERENCES identity_registry(person_id),
    type VARCHAR(100) NOT NULL, -- 'message', 'query', 'response', 'system'
    content TEXT,
    source VARCHAR(50) NOT NULL, -- 'telegram', 'email', 'youtube', etc.
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'
);

-- Channel Mapping Table
-- Maps platform-specific IDs to person_id
CREATE TABLE channel_mapping (
    mapping_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    channel_type VARCHAR(50) NOT NULL, -- 'telegram', 'email', 'youtube'
    channel_id VARCHAR(255) NOT NULL, -- platform-specific user ID
    person_id UUID REFERENCES identity_registry(person_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(channel_type, channel_id)
);

-- Indexes for performance
CREATE INDEX idx_event_log_person_id ON event_log(person_id);
CREATE INDEX idx_event_log_timestamp ON event_log(timestamp);
CREATE INDEX idx_event_log_source ON event_log(source);
CREATE INDEX idx_channel_mapping_lookup ON channel_mapping(channel_type, channel_id);

-- Updated timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to identity_registry
CREATE TRIGGER update_identity_registry_updated_at 
    BEFORE UPDATE ON identity_registry 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) - Enable when needed
-- ALTER TABLE identity_registry ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE event_log ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE channel_mapping ENABLE ROW LEVEL SECURITY;

-- Sample data for testing (remove in production)
INSERT INTO identity_registry (name, consent) VALUES 
    ('Test User 1', true),
    ('Test User 2', false);

-- Sample channel mapping
INSERT INTO channel_mapping (channel_type, channel_id, person_id) VALUES 
    ('telegram', '123456789', (SELECT person_id FROM identity_registry LIMIT 1)),
    ('email', 'test@example.com', (SELECT person_id FROM identity_registry LIMIT 1));
