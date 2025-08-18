-- Tiered Wisdom Synthesis System Database Schema
-- Multi-library truth seeking with subscription-based access control

-- User subscription and tier management
CREATE TABLE IF NOT EXISTS user_subscriptions (
    subscription_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID REFERENCES identity_registry(person_id) UNIQUE,
    
    -- Tier information
    tier_level INTEGER CHECK (tier_level BETWEEN 1 AND 3) DEFAULT 1,
    tier_name VARCHAR(50) NOT NULL DEFAULT 'Sacred Source',
    tier_description TEXT,
    
    -- Feature access control
    features_enabled TEXT[] DEFAULT ARRAY['single_library_access', 'basic_search', 'quote_bookmarking'],
    monthly_query_limit INTEGER DEFAULT 100,
    queries_used_this_month INTEGER DEFAULT 0,
    
    -- Access permissions
    cross_library_access BOOLEAN DEFAULT false,
    synthesis_access BOOLEAN DEFAULT false,
    personality_integration BOOLEAN DEFAULT false,
    advanced_ai_access BOOLEAN DEFAULT false,
    
    -- Subscription management
    subscription_start TIMESTAMPTZ DEFAULT NOW(),
    subscription_end TIMESTAMPTZ,
    auto_renew BOOLEAN DEFAULT true,
    payment_status VARCHAR(20) DEFAULT 'active', -- 'active', 'past_due', 'canceled'
    
    -- Usage tracking
    last_query_date TIMESTAMPTZ,
    total_queries_lifetime INTEGER DEFAULT 0,
    favorite_libraries TEXT[] DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tier definitions and pricing
CREATE TABLE IF NOT EXISTS subscription_tiers (
    tier_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tier_level INTEGER UNIQUE NOT NULL,
    tier_name VARCHAR(50) NOT NULL,
    tier_description TEXT,
    monthly_price DECIMAL(10,2),
    annual_price DECIMAL(10,2),
    
    -- Feature limits
    monthly_query_limit INTEGER,
    libraries_accessible TEXT[], -- Which libraries this tier can access
    
    -- Feature flags
    cross_library_comparison BOOLEAN DEFAULT false,
    synthesis_responses BOOLEAN DEFAULT false,
    personality_integration BOOLEAN DEFAULT false,
    advanced_ai_consultation BOOLEAN DEFAULT false,
    study_group_access BOOLEAN DEFAULT false,
    beta_features BOOLEAN DEFAULT false,
    
    -- Additional benefits
    benefits TEXT[],
    limitations TEXT[],
    
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Cross-library synthesis responses cache
CREATE TABLE IF NOT EXISTS synthesis_responses (
    synthesis_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Query information
    query_topic VARCHAR(500) NOT NULL,
    query_hash VARCHAR(64) UNIQUE, -- Hash for deduplication
    normalized_query TEXT, -- Cleaned/normalized version
    
    -- Libraries and sources involved
    libraries_included TEXT[] NOT NULL, -- e.g., ['hylozoics', 'neville', 'scovel_shinn']
    total_quotes_found INTEGER DEFAULT 0,
    sacred_quotes JSONB NOT NULL, -- All source quotes with complete citations
    
    -- AI-generated synthesis
    synthesis_text TEXT NOT NULL,
    universal_principles TEXT[],
    tradition_differences JSONB,
    apparent_contradictions TEXT[],
    contradiction_resolutions TEXT[],
    
    -- Personality integration (Tier 3 only)
    personality_applications JSONB,
    enneagram_applications JSONB,
    human_design_applications JSONB,
    
    -- Study recommendations
    study_path_suggestions TEXT[],
    recommended_reading_order TEXT[],
    prerequisite_concepts TEXT[],
    
    -- Quality and access control
    confidence_score DECIMAL(3,2) NOT NULL,
    tier_required INTEGER NOT NULL DEFAULT 3,
    synthesis_quality_score DECIMAL(3,2),
    human_verified BOOLEAN DEFAULT false,
    verified_by VARCHAR(255),
    
    -- Performance tracking
    generation_time_ms INTEGER,
    tokens_used INTEGER,
    ai_model_used VARCHAR(50),
    
    -- Cache management
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '30 days'),
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMPTZ
);

-- Enhanced cross-library concept mapping
CREATE TABLE IF NOT EXISTS cross_library_concepts_enhanced (
    concept_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Core concept information
    concept_name VARCHAR(255) NOT NULL,
    concept_category VARCHAR(100), -- 'manifestation', 'consciousness', 'development', etc.
    concept_description TEXT,
    
    -- Library-specific representations
    hylozoics_term VARCHAR(255),
    hylozoics_definition TEXT,
    hylozoics_quote_ids UUID[],
    hylozoics_key_passages TEXT[],
    
    neville_term VARCHAR(255),
    neville_definition TEXT,
    neville_quote_ids UUID[],
    neville_key_passages TEXT[],
    
    scovel_shinn_term VARCHAR(255),
    scovel_shinn_definition TEXT,
    scovel_shinn_quote_ids UUID[],
    scovel_shinn_key_passages TEXT[],
    
    fourth_way_term VARCHAR(255),
    fourth_way_definition TEXT,
    fourth_way_quote_ids UUID[],
    fourth_way_key_passages TEXT[],
    
    -- Synthesis analysis
    universal_principle TEXT,
    common_themes TEXT[],
    key_differences JSONB,
    apparent_contradictions TEXT[],
    contradiction_explanations TEXT[],
    
    -- Personality system integration
    enneagram_relevance JSONB, -- How concept applies to each type
    human_design_relevance JSONB,
    gene_keys_relevance JSONB,
    
    -- Study progression
    difficulty_level INTEGER CHECK (difficulty_level BETWEEN 1 AND 5),
    prerequisite_concepts TEXT[],
    follow_up_concepts TEXT[],
    study_sequence_position INTEGER,
    
    -- Access control and quality
    tier_required INTEGER DEFAULT 2,
    synthesis_available BOOLEAN DEFAULT false,
    synthesis_quality DECIMAL(3,2),
    human_curated BOOLEAN DEFAULT false,
    curated_by VARCHAR(255),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- User query history and analytics
CREATE TABLE IF NOT EXISTS user_query_history (
    query_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID REFERENCES identity_registry(person_id),
    subscription_id UUID REFERENCES user_subscriptions(subscription_id),
    
    -- Query details
    query_text TEXT NOT NULL,
    query_category VARCHAR(100),
    libraries_requested TEXT[],
    response_mode VARCHAR(50), -- 'single_library', 'cross_library', 'synthesis'
    
    -- Response information
    response_type VARCHAR(50), -- 'sacred_only', 'comparison', 'synthesis'
    synthesis_id UUID REFERENCES synthesis_responses(synthesis_id),
    quotes_returned INTEGER,
    libraries_searched TEXT[],
    
    -- User interaction
    user_satisfaction INTEGER CHECK (user_satisfaction BETWEEN 1 AND 5),
    user_feedback TEXT,
    bookmarked BOOLEAN DEFAULT false,
    shared BOOLEAN DEFAULT false,
    
    -- Performance metrics
    response_time_ms INTEGER,
    tier_at_query_time INTEGER,
    query_within_limits BOOLEAN DEFAULT true,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Study progression tracking across libraries
CREATE TABLE IF NOT EXISTS cross_library_study_progression (
    progression_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID REFERENCES identity_registry(person_id),
    
    -- Current study focus
    primary_library VARCHAR(50),
    study_level VARCHAR(50) DEFAULT 'beginner',
    study_goals TEXT[],
    
    -- Progress across all libraries
    hylozoics_progress JSONB DEFAULT '{"quotes_studied": 0, "concepts_mastered": [], "books_completed": []}',
    neville_progress JSONB DEFAULT '{"quotes_studied": 0, "concepts_mastered": [], "books_completed": []}',
    scovel_shinn_progress JSONB DEFAULT '{"quotes_studied": 0, "concepts_mastered": [], "books_completed": []}',
    fourth_way_progress JSONB DEFAULT '{"quotes_studied": 0, "concepts_mastered": [], "books_completed": []}',
    
    -- Cross-library synthesis understanding
    synthesis_concepts_explored TEXT[],
    contradictions_resolved TEXT[],
    personal_insights TEXT[],
    
    -- Personality integration progress
    personality_type_confirmed VARCHAR(50),
    personality_applications_learned TEXT[],
    personalized_practices TEXT[],
    
    -- Recommendations and next steps
    ai_recommended_path TEXT[],
    human_mentor_suggestions TEXT[],
    study_group_participation TEXT[],
    
    -- Metrics
    total_study_hours INTEGER DEFAULT 0,
    consistency_score DECIMAL(3,2), -- How regularly user studies
    depth_score DECIMAL(3,2), -- How deeply user engages
    synthesis_ability_score DECIMAL(3,2), -- User's synthesis understanding
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(person_id)
);

-- Payment and subscription history
CREATE TABLE IF NOT EXISTS subscription_history (
    history_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID REFERENCES identity_registry(person_id),
    subscription_id UUID REFERENCES user_subscriptions(subscription_id),
    
    -- Event information
    event_type VARCHAR(50) NOT NULL, -- 'upgrade', 'downgrade', 'renewal', 'cancellation'
    from_tier INTEGER,
    to_tier INTEGER,
    
    -- Payment details
    amount_paid DECIMAL(10,2),
    currency VARCHAR(3) DEFAULT 'USD',
    payment_method VARCHAR(50),
    payment_status VARCHAR(20),
    
    -- Subscription period
    period_start TIMESTAMPTZ,
    period_end TIMESTAMPTZ,
    
    -- Context
    reason_for_change TEXT,
    promotional_code VARCHAR(50),
    discount_applied DECIMAL(10,2),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_person ON user_subscriptions(person_id);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_tier ON user_subscriptions(tier_level);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_status ON user_subscriptions(payment_status);
CREATE INDEX IF NOT EXISTS idx_user_subscriptions_end_date ON user_subscriptions(subscription_end);

CREATE INDEX IF NOT EXISTS idx_synthesis_responses_hash ON synthesis_responses(query_hash);
CREATE INDEX IF NOT EXISTS idx_synthesis_responses_topic ON synthesis_responses(query_topic);
CREATE INDEX IF NOT EXISTS idx_synthesis_responses_libraries ON synthesis_responses USING GIN(libraries_included);
CREATE INDEX IF NOT EXISTS idx_synthesis_responses_tier ON synthesis_responses(tier_required);
CREATE INDEX IF NOT EXISTS idx_synthesis_responses_expires ON synthesis_responses(expires_at);

CREATE INDEX IF NOT EXISTS idx_cross_library_concepts_name ON cross_library_concepts_enhanced(concept_name);
CREATE INDEX IF NOT EXISTS idx_cross_library_concepts_category ON cross_library_concepts_enhanced(concept_category);
CREATE INDEX IF NOT EXISTS idx_cross_library_concepts_tier ON cross_library_concepts_enhanced(tier_required);

CREATE INDEX IF NOT EXISTS idx_query_history_person ON user_query_history(person_id);
CREATE INDEX IF NOT EXISTS idx_query_history_created ON user_query_history(created_at);
CREATE INDEX IF NOT EXISTS idx_query_history_category ON user_query_history(query_category);
CREATE INDEX IF NOT EXISTS idx_query_history_mode ON user_query_history(response_mode);

CREATE INDEX IF NOT EXISTS idx_study_progression_person ON cross_library_study_progression(person_id);
CREATE INDEX IF NOT EXISTS idx_study_progression_library ON cross_library_study_progression(primary_library);
CREATE INDEX IF NOT EXISTS idx_study_progression_level ON cross_library_study_progression(study_level);

-- Functions for subscription management
CREATE OR REPLACE FUNCTION check_query_limit(p_person_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    current_usage INTEGER;
    usage_limit INTEGER;
BEGIN
    SELECT queries_used_this_month, monthly_query_limit
    INTO current_usage, usage_limit
    FROM user_subscriptions
    WHERE person_id = p_person_id;
    
    RETURN (current_usage < usage_limit);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION increment_query_usage(p_person_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE user_subscriptions
    SET 
        queries_used_this_month = queries_used_this_month + 1,
        total_queries_lifetime = total_queries_lifetime + 1,
        last_query_date = NOW()
    WHERE person_id = p_person_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION reset_monthly_usage()
RETURNS INTEGER AS $$
DECLARE
    reset_count INTEGER;
BEGIN
    UPDATE user_subscriptions
    SET queries_used_this_month = 0
    WHERE DATE_TRUNC('month', last_query_date) < DATE_TRUNC('month', NOW());
    
    GET DIAGNOSTICS reset_count = ROW_COUNT;
    RETURN reset_count;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION update_study_progression(
    p_person_id UUID,
    p_library VARCHAR(50),
    p_concepts_learned TEXT[]
)
RETURNS VOID AS $$
DECLARE
    progress_field TEXT;
    current_progress JSONB;
    updated_progress JSONB;
BEGIN
    -- Determine which progress field to update
    progress_field := p_library || '_progress';
    
    -- Get current progress
    EXECUTE format('SELECT %I FROM cross_library_study_progression WHERE person_id = $1', progress_field)
    INTO current_progress
    USING p_person_id;
    
    -- Update progress
    updated_progress := jsonb_set(
        current_progress,
        '{concepts_mastered}',
        (current_progress->'concepts_mastered')::jsonb || to_jsonb(p_concepts_learned)
    );
    
    -- Save updated progress
    EXECUTE format('UPDATE cross_library_study_progression SET %I = $1, updated_at = NOW() WHERE person_id = $2', progress_field)
    USING updated_progress, p_person_id;
    
    -- Insert if doesn't exist
    IF NOT FOUND THEN
        INSERT INTO cross_library_study_progression (person_id, primary_library)
        VALUES (p_person_id, p_library)
        ON CONFLICT (person_id) DO NOTHING;
        
        -- Try update again
        EXECUTE format('UPDATE cross_library_study_progression SET %I = $1, updated_at = NOW() WHERE person_id = $2', progress_field)
        USING updated_progress, p_person_id;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Row Level Security policies
ALTER TABLE user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE synthesis_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE cross_library_concepts_enhanced ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_query_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE cross_library_study_progression ENABLE ROW LEVEL SECURITY;
ALTER TABLE subscription_history ENABLE ROW LEVEL SECURITY;

-- Subscription policies
CREATE POLICY "Users can read their own subscription" ON user_subscriptions
    FOR SELECT USING (person_id = auth.uid());

CREATE POLICY "Users can update their own subscription" ON user_subscriptions
    FOR UPDATE USING (person_id = auth.uid());

-- Synthesis response policies based on tier
CREATE POLICY "Users can read synthesis based on tier" ON synthesis_responses
    FOR SELECT USING (
        tier_required <= (
            SELECT tier_level FROM user_subscriptions WHERE person_id = auth.uid()
        )
    );

-- Cross-library concept policies
CREATE POLICY "Users can read concepts based on tier" ON cross_library_concepts_enhanced
    FOR SELECT USING (
        tier_required <= (
            SELECT tier_level FROM user_subscriptions WHERE person_id = auth.uid()
        )
    );

-- Query history policies
CREATE POLICY "Users can read their own query history" ON user_query_history
    FOR SELECT USING (person_id = auth.uid());

CREATE POLICY "Users can insert their own queries" ON user_query_history
    FOR INSERT WITH CHECK (person_id = auth.uid());

-- Study progression policies
CREATE POLICY "Users can manage their own progression" ON cross_library_study_progression
    FOR ALL USING (person_id = auth.uid());

-- Subscription history policies
CREATE POLICY "Users can read their own subscription history" ON subscription_history
    FOR SELECT USING (person_id = auth.uid());

-- Insert default tier definitions
INSERT INTO subscription_tiers (
    tier_level, tier_name, tier_description, monthly_price, annual_price,
    monthly_query_limit, libraries_accessible,
    cross_library_comparison, synthesis_responses, personality_integration,
    benefits, limitations
) VALUES 
(
    1, 'Sacred Source', 'Access to authentic quotes from verified wisdom sources',
    9.99, 99.99, 100, 
    ARRAY['hylozoics', 'neville', 'scovel_shinn', 'fourth_way'],
    false, false, false,
    ARRAY['Exact quotes with citations', 'Basic search', 'Study progress tracking', 'Mobile app access'],
    ARRAY['Single tradition responses only', 'No cross-library comparison', 'No AI synthesis']
),
(
    2, 'Cross-Library Wisdom', 'Comparative analysis across multiple wisdom traditions',
    29.99, 299.99, 500,
    ARRAY['hylozoics', 'neville', 'scovel_shinn', 'fourth_way', 'personality_systems'],
    true, false, false,
    ARRAY['Multi-library comparisons', 'Side-by-side analysis', 'Advanced search', 'Study groups', 'Discussion forums'],
    ARRAY['No complete synthesis', 'No personality integration', 'No custom AI consultation']
),
(
    3, 'Synthesis Master', 'Complete AI-powered synthesis and personalized guidance',
    99.99, 999.99, 2000,
    ARRAY['hylozoics', 'neville', 'scovel_shinn', 'fourth_way', 'personality_systems', 'advanced_libraries'],
    true, true, true,
    ARRAY['Complete synthesis responses', 'AI truth extraction', 'Personality integration', 'Custom study paths', 'Direct AI consultation', 'Beta features'],
    ARRAY['Premium pricing', 'Advanced features may require learning curve']
);
