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

-- ============================================================================
-- PERSONALITY SYNTHESIS EXTENSION
-- ============================================================================

-- Main personality synthesis profile table
CREATE TABLE personality_synthesis (
    synthesis_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID REFERENCES identity_registry(person_id) ON DELETE CASCADE,
    
    -- Confidence scores for each system (0.0 to 1.0)
    enneagram_confidence DECIMAL(3,2) DEFAULT 0.0,
    human_design_confidence DECIMAL(3,2) DEFAULT 0.0,
    astrology_confidence DECIMAL(3,2) DEFAULT 0.0,
    maya_calendar_confidence DECIMAL(3,2) DEFAULT 0.0,
    jungian_confidence DECIMAL(3,2) DEFAULT 0.0,
    gene_keys_confidence DECIMAL(3,2) DEFAULT 0.0,
    theosophy_confidence DECIMAL(3,2) DEFAULT 0.0,
    hylozoics_confidence DECIMAL(3,2) DEFAULT 0.0,
    becoming_one_confidence DECIMAL(3,2) DEFAULT 0.0,
    
    -- Data sources tracking
    data_sources JSONB DEFAULT '{}',
    
    -- Synthesis insights
    core_patterns TEXT[],
    cross_system_correlations JSONB DEFAULT '{}',
    recommended_practices TEXT[],
    growth_edges TEXT[],
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(person_id)
);

-- Becoming One™ unique profile data
CREATE TABLE becoming_one_profiles (
    profile_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    synthesis_id UUID REFERENCES personality_synthesis(synthesis_id) ON DELETE CASCADE,
    
    primary_essence_level VARCHAR(20), -- physical, emotional, mental, essential
    current_vertical_stage VARCHAR(20), -- survival, personality, essence, unity
    manifestation_style VARCHAR(50), -- mental_goal_setting, emotional_feeling_state, etc.
    
    dominant_anchor_patterns TEXT[], -- abandonment, unworthiness, powerlessness, etc.
    avoidance_signatures TEXT[], -- procrastination, perfectionism, people_pleasing, etc.
    journey_stage VARCHAR(20) DEFAULT 'discovery', -- discovery, exploration, integration, mastery
    essence_qualities TEXT[], -- peace, joy, love, power, etc.
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Track personality indicators detected from user interactions
CREATE TABLE personality_indicators (
    indicator_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID REFERENCES identity_registry(person_id) ON DELETE CASCADE,
    event_id UUID REFERENCES event_log(event_id) ON DELETE CASCADE,
    
    system_type VARCHAR(30), -- enneagram, human_design, astrology, etc.
    indicator_type VARCHAR(50), -- specific pattern detected
    indicator_value TEXT, -- the actual indicator
    confidence DECIMAL(3,2), -- 0.0 to 1.0
    source VARCHAR(20), -- text_analysis, voice_analysis, behavioral, etc.
    
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Track emotional anchor activations
CREATE TABLE anchor_activations (
    activation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID REFERENCES identity_registry(person_id) ON DELETE CASCADE,
    event_id UUID REFERENCES event_log(event_id) ON DELETE CASCADE,
    
    anchor_type VARCHAR(30), -- abandonment, unworthiness, etc.
    intensity DECIMAL(3,2), -- 0.0 to 1.0
    trigger_context TEXT,
    somatic_markers TEXT[],
    language_patterns TEXT[],
    
    resolution_attempted BOOLEAN DEFAULT false,
    resolution_method VARCHAR(50),
    resolution_effectiveness DECIMAL(3,2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for personality synthesis performance
CREATE INDEX idx_personality_synthesis_person_id ON personality_synthesis(person_id);
CREATE INDEX idx_personality_indicators_person_id ON personality_indicators(person_id);
CREATE INDEX idx_personality_indicators_system_type ON personality_indicators(system_type);
CREATE INDEX idx_anchor_activations_person_id ON anchor_activations(person_id);
CREATE INDEX idx_anchor_activations_anchor_type ON anchor_activations(anchor_type);

-- Personality synthesis updated_at trigger
CREATE TRIGGER update_personality_synthesis_updated_at 
    BEFORE UPDATE ON personality_synthesis 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_becoming_one_profiles_updated_at 
    BEFORE UPDATE ON becoming_one_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- View for complete personality overview
CREATE VIEW personality_overview AS
SELECT 
    ps.person_id,
    ir.name,
    ps.synthesis_id,
    
    -- System confidence scores
    ps.enneagram_confidence,
    ps.human_design_confidence,
    ps.astrology_confidence,
    ps.maya_calendar_confidence,
    ps.jungian_confidence,
    ps.becoming_one_confidence,
    
    -- Core patterns and insights
    ps.core_patterns,
    ps.recommended_practices,
    ps.growth_edges,
    
    -- Becoming One™ specific data
    bo.primary_essence_level,
    bo.current_vertical_stage,
    bo.journey_stage,
    bo.dominant_anchor_patterns,
    bo.avoidance_signatures,
    
    ps.updated_at
    
FROM personality_synthesis ps
JOIN identity_registry ir ON ps.person_id = ir.person_id
LEFT JOIN becoming_one_profiles bo ON ps.synthesis_id = bo.synthesis_id;

-- Function to get personality context for AI
CREATE OR REPLACE FUNCTION get_personality_context(target_person_id UUID)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'person_id', person_id,
        'essence_level', primary_essence_level,
        'vertical_stage', current_vertical_stage,
        'journey_stage', journey_stage,
        'anchor_patterns', dominant_anchor_patterns,
        'avoidance_signatures', avoidance_signatures,
        'core_patterns', core_patterns,
        'recommended_practices', recommended_practices,
        'confidence_scores', jsonb_build_object(
            'enneagram', enneagram_confidence,
            'human_design', human_design_confidence,
            'astrology', astrology_confidence,
            'maya_calendar', maya_calendar_confidence,
            'jungian', jungian_confidence,
            'gene_keys', gene_keys_confidence,
            'theosophy', theosophy_confidence,
            'hylozoics', hylozoics_confidence,
            'becoming_one', becoming_one_confidence
        )
    ) INTO result
    FROM personality_overview
    WHERE person_id = target_person_id;
    
    RETURN COALESCE(result, '{}'::jsonb);
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- KNOWLEDGE MANAGEMENT SYSTEM TABLES
-- =============================================================================

-- Core content storage and metadata
CREATE TABLE schaubilder (
    schaubild_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    description TEXT,
    content_hash TEXT UNIQUE NOT NULL,
    metadata JSONB DEFAULT '{}',
    concepts TEXT[] DEFAULT '{}',
    feeling_states TEXT[] DEFAULT '{}',
    anchor_types TEXT[] DEFAULT '{}',
    difficulty_level INTEGER DEFAULT 1 CHECK (difficulty_level BETWEEN 1 AND 10),
    prerequisites TEXT[] DEFAULT '{}',
    related_schaubilder UUID[] DEFAULT '{}',
    upload_date TIMESTAMPTZ DEFAULT NOW(),
    status TEXT DEFAULT 'active' CHECK (status IN ('processing', 'active', 'archived')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Master prompts and AI instructions
CREATE TABLE master_prompts (
    prompt_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    content TEXT NOT NULL,
    context JSONB DEFAULT '{}',
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    upload_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Human-generated answers for continuous learning
CREATE TABLE human_generated_answers (
    answer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    source_person TEXT NOT NULL,
    context JSONB DEFAULT '{}',
    validation_status TEXT DEFAULT 'pending' CHECK (validation_status IN ('pending', 'approved', 'rejected')),
    validated_by UUID REFERENCES people(person_id),
    validation_date TIMESTAMPTZ,
    created_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Teaching materials and method descriptions
CREATE TABLE teaching_materials (
    material_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    material_type TEXT NOT NULL CHECK (material_type IN ('method_description', 'protocol', 'case_study', 'exercise')),
    source_type TEXT NOT NULL CHECK (source_type IN ('johan_original', 'marianne_original', 'workshop_recording', 'presentation_transcript')),
    metadata JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    difficulty_level INTEGER DEFAULT 1 CHECK (difficulty_level BETWEEN 1 AND 10),
    prerequisites TEXT[] DEFAULT '{}',
    related_materials UUID[] DEFAULT '{}',
    content_hash TEXT UNIQUE NOT NULL,
    upload_date TIMESTAMPTZ DEFAULT NOW(),
    status TEXT DEFAULT 'active' CHECK (status IN ('processing', 'active', 'archived')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Content chunks for vector embeddings (metadata only, vectors in Pinecone)
CREATE TABLE content_chunks (
    chunk_id TEXT PRIMARY KEY,
    parent_id UUID NOT NULL,
    parent_type TEXT NOT NULL CHECK (parent_type IN ('schaubild', 'master_prompt', 'teaching_material', 'human_answer')),
    chunk_index INTEGER NOT NULL,
    content_preview TEXT, -- First 200 chars for reference
    token_count INTEGER NOT NULL,
    metadata JSONB DEFAULT '{}',
    pinecone_stored BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Query tracking for learning and improvement
CREATE TABLE knowledge_queries (
    query_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id UUID REFERENCES people(person_id),
    query_text TEXT NOT NULL,
    query_context JSONB DEFAULT '{}',
    response_generated TEXT,
    sources_used JSONB DEFAULT '[]',
    confidence_score DECIMAL(3,2),
    needs_human_input BOOLEAN DEFAULT false,
    human_feedback TEXT,
    feedback_rating INTEGER CHECK (feedback_rating BETWEEN 1 AND 5),
    query_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Knowledge base statistics and health monitoring
CREATE TABLE knowledge_stats (
    stat_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    date DATE DEFAULT CURRENT_DATE,
    total_schaubilder INTEGER DEFAULT 0,
    total_chunks INTEGER DEFAULT 0,
    total_queries INTEGER DEFAULT 0,
    avg_confidence DECIMAL(3,2) DEFAULT 0.00,
    human_input_requests INTEGER DEFAULT 0,
    new_content_added INTEGER DEFAULT 0,
    stats_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Community content from participants/audience
CREATE TABLE community_content (
    content_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('question', 'feedback', 'insight', 'discussion', 'testimonial')),
    themes TEXT[] DEFAULT '{}',
    source_file TEXT,
    metadata JSONB DEFAULT '{}',
    auto_processed BOOLEAN DEFAULT false,
    created_date TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- INBOX processing log
CREATE TABLE inbox_processing_log (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL,
    processing_status TEXT NOT NULL CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed', 'skipped')),
    teaching_segments INTEGER DEFAULT 0,
    community_segments INTEGER DEFAULT 0,
    content_suggestions INTEGER DEFAULT 0,
    processing_time DECIMAL(8,2) DEFAULT 0.00,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    processed_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Content suggestions generated from processed files
CREATE TABLE content_suggestions (
    suggestion_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_file TEXT NOT NULL,
    platform TEXT NOT NULL CHECK (platform IN ('tiktok', 'youtube_shorts', 'instagram_reels', 'instagram_post', 'twitter', 'linkedin')),
    content_type TEXT NOT NULL CHECK (content_type IN ('short_form_video', 'social_post', 'quote_graphic', 'thread')),
    title TEXT NOT NULL,
    hook TEXT,
    main_content TEXT NOT NULL,
    call_to_action TEXT,
    hashtags TEXT[] DEFAULT '{}',
    visual_suggestions TEXT[] DEFAULT '{}',
    engagement_score DECIMAL(3,2) DEFAULT 0.00,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'approved', 'scheduled', 'published')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_schaubilder_concepts ON schaubilder USING GIN(concepts);
CREATE INDEX idx_schaubilder_feeling_states ON schaubilder USING GIN(feeling_states);
CREATE INDEX idx_schaubilder_status ON schaubilder(status);
CREATE INDEX idx_master_prompts_active ON master_prompts(is_active);
CREATE INDEX idx_human_answers_validation ON human_generated_answers(validation_status);
CREATE INDEX idx_teaching_materials_type ON teaching_materials(material_type);
CREATE INDEX idx_content_chunks_parent ON content_chunks(parent_id, parent_type);
CREATE INDEX idx_knowledge_queries_person ON knowledge_queries(person_id);
CREATE INDEX idx_knowledge_queries_date ON knowledge_queries(query_date);
CREATE INDEX idx_community_content_category ON community_content(category);
CREATE INDEX idx_community_content_themes ON community_content USING GIN(themes);
CREATE INDEX idx_inbox_processing_status ON inbox_processing_log(processing_status);
CREATE INDEX idx_inbox_processing_date ON inbox_processing_log(processed_at);
CREATE INDEX idx_content_suggestions_platform ON content_suggestions(platform);
CREATE INDEX idx_content_suggestions_status ON content_suggestions(status);

-- Triggers for updated_at
CREATE TRIGGER update_schaubilder_updated_at BEFORE UPDATE ON schaubilder FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_master_prompts_updated_at BEFORE UPDATE ON master_prompts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_human_answers_updated_at BEFORE UPDATE ON human_generated_answers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_teaching_materials_updated_at BEFORE UPDATE ON teaching_materials FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_content_chunks_updated_at BEFORE UPDATE ON content_chunks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_knowledge_queries_updated_at BEFORE UPDATE ON knowledge_queries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_community_content_updated_at BEFORE UPDATE ON community_content FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_content_suggestions_updated_at BEFORE UPDATE ON content_suggestions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- KNOWLEDGE BASE VIEWS AND FUNCTIONS
-- =============================================================================

-- View for knowledge base overview
CREATE VIEW knowledge_overview AS
SELECT 
    s.schaubild_id,
    s.title,
    s.concepts,
    s.feeling_states,
    s.difficulty_level,
    s.status,
    COUNT(cc.chunk_id) as chunk_count,
    s.upload_date
FROM schaubilder s
LEFT JOIN content_chunks cc ON s.schaubild_id = cc.parent_id AND cc.parent_type = 'schaubild'
GROUP BY s.schaubild_id, s.title, s.concepts, s.feeling_states, s.difficulty_level, s.status, s.upload_date;

-- Function to get knowledge context for AI responses
CREATE OR REPLACE FUNCTION get_knowledge_context(
    target_concepts TEXT[],
    target_feeling_states TEXT[],
    max_results INTEGER DEFAULT 10
)
RETURNS TABLE(
    content_id UUID,
    content_type TEXT,
    title TEXT,
    relevance_score INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        s.schaubild_id as content_id,
        'schaubild'::TEXT as content_type,
        s.title,
        (
            CASE WHEN s.concepts && target_concepts THEN 2 ELSE 0 END +
            CASE WHEN s.feeling_states && target_feeling_states THEN 2 ELSE 0 END
        ) as relevance_score
    FROM schaubilder s
    WHERE s.status = 'active'
        AND (
            s.concepts && target_concepts 
            OR s.feeling_states && target_feeling_states
        )
    ORDER BY relevance_score DESC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;
