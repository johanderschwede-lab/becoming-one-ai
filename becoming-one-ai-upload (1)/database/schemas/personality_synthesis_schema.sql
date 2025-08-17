-- Becoming One™ Personality Synthesis Schema Extension
-- Adds comprehensive personality mapping capabilities

-- ============================================================================
-- PERSONALITY SYNTHESIS TABLES
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

-- Enneagram profile data
CREATE TABLE enneagram_profiles (
    profile_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    synthesis_id UUID REFERENCES personality_synthesis(synthesis_id) ON DELETE CASCADE,
    
    core_type INTEGER CHECK (core_type >= 1 AND core_type <= 9),
    wing INTEGER CHECK (wing >= 1 AND wing <= 9),
    instinct_stack TEXT[], -- ['sp', 'so', 'sx'] in order
    integration_direction INTEGER CHECK (integration_direction >= 1 AND integration_direction <= 9),
    disintegration_direction INTEGER CHECK (disintegration_direction >= 1 AND disintegration_direction <= 9),
    health_level INTEGER CHECK (health_level >= 1 AND health_level <= 9) DEFAULT 5,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Human Design profile data
CREATE TABLE human_design_profiles (
    profile_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    synthesis_id UUID REFERENCES personality_synthesis(synthesis_id) ON DELETE CASCADE,
    
    type VARCHAR(50), -- manifestor, generator, manifesting_generator, projector, reflector
    strategy VARCHAR(50),
    authority VARCHAR(50),
    profile VARCHAR(10), -- e.g., "1/3", "4/6"
    defined_centers TEXT[],
    undefined_centers TEXT[],
    gates INTEGER[],
    channels TEXT[],
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Astrology profile data
CREATE TABLE astrology_profiles (
    profile_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    synthesis_id UUID REFERENCES personality_synthesis(synthesis_id) ON DELETE CASCADE,
    
    sun_sign VARCHAR(20),
    moon_sign VARCHAR(20),
    rising_sign VARCHAR(20),
    planetary_positions JSONB DEFAULT '{}',
    dominant_element VARCHAR(10), -- fire, earth, air, water
    dominant_modality VARCHAR(10), -- cardinal, fixed, mutable
    birth_chart_emphasis TEXT[],
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Maya Calendar profile data
CREATE TABLE maya_calendar_profiles (
    profile_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    synthesis_id UUID REFERENCES personality_synthesis(synthesis_id) ON DELETE CASCADE,
    
    kin_number INTEGER CHECK (kin_number >= 1 AND kin_number <= 260),
    seal VARCHAR(50),
    tone INTEGER CHECK (tone >= 1 AND tone <= 13),
    color VARCHAR(10), -- red, white, blue, yellow
    guide VARCHAR(50),
    challenge VARCHAR(50),
    occult VARCHAR(50),
    analog VARCHAR(50),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Jungian/MBTI profile data
CREATE TABLE jungian_profiles (
    profile_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    synthesis_id UUID REFERENCES personality_synthesis(synthesis_id) ON DELETE CASCADE,
    
    mbti_type VARCHAR(4), -- INTJ, ENFP, etc.
    dominant_function VARCHAR(2), -- Ne, Si, Fi, Te, etc.
    auxiliary_function VARCHAR(2),
    tertiary_function VARCHAR(2),
    inferior_function VARCHAR(2),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Becoming One™ unique profile data
CREATE TABLE becoming_one_profiles (
    profile_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    synthesis_id UUID REFERENCES personality_synthesis(synthesis_id) ON DELETE CASCADE,
    
    primary_essence_level VARCHAR(20), -- physical, emotional, mental, essential
    current_vertical_stage VARCHAR(20), -- survival, personality, essence, unity
    manifestation_style VARCHAR(30), -- mental_goal_setting, emotional_feeling_state, etc.
    
    dominant_anchor_patterns TEXT[], -- abandonment, unworthiness, powerlessness, etc.
    avoidance_signatures TEXT[], -- procrastination, perfectionism, people_pleasing, etc.
    journey_stage VARCHAR(20) DEFAULT 'discovery', -- discovery, exploration, integration, mastery
    essence_qualities TEXT[], -- peace, joy, love, power, etc.
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- DYNAMIC PATTERN TRACKING
-- ============================================================================

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

-- Track avoidance pattern detections
CREATE TABLE avoidance_detections (
    detection_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID REFERENCES identity_registry(person_id) ON DELETE CASCADE,
    event_id UUID REFERENCES event_log(event_id) ON DELETE CASCADE,
    
    avoidance_type VARCHAR(30), -- procrastination, perfectionism, etc.
    behavioral_markers TEXT[],
    language_hedges TEXT[],
    time_patterns JSONB DEFAULT '{}', -- when avoidance occurs
    
    underlying_anchor VARCHAR(30), -- suspected emotional anchor
    intervention_suggested VARCHAR(100),
    intervention_accepted BOOLEAN,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- SYNTHESIS ANALYSIS RESULTS
-- ============================================================================

-- Store AI analysis results for personality synthesis
CREATE TABLE synthesis_analysis (
    analysis_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID REFERENCES identity_registry(person_id) ON DELETE CASCADE,
    
    analysis_type VARCHAR(30), -- periodic_update, crisis_analysis, breakthrough_analysis
    trigger_event_id UUID REFERENCES event_log(event_id),
    
    -- Analysis results
    personality_shifts JSONB DEFAULT '{}',
    new_patterns_detected TEXT[],
    pattern_confirmations TEXT[],
    contradictions_found TEXT[],
    
    -- Recommendations generated
    immediate_guidance TEXT,
    practice_recommendations TEXT[],
    growth_edge_identified TEXT,
    essence_invitation TEXT,
    
    -- Meta-analysis
    analysis_confidence DECIMAL(3,2),
    human_review_needed BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX idx_personality_synthesis_person_id ON personality_synthesis(person_id);
CREATE INDEX idx_personality_indicators_person_id ON personality_indicators(person_id);
CREATE INDEX idx_personality_indicators_system_type ON personality_indicators(system_type);
CREATE INDEX idx_anchor_activations_person_id ON anchor_activations(person_id);
CREATE INDEX idx_anchor_activations_anchor_type ON anchor_activations(anchor_type);
CREATE INDEX idx_avoidance_detections_person_id ON avoidance_detections(person_id);
CREATE INDEX idx_synthesis_analysis_person_id ON synthesis_analysis(person_id);
CREATE INDEX idx_synthesis_analysis_created_at ON synthesis_analysis(created_at);

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- ============================================================================

-- Update synthesis profile when new indicators are detected
CREATE OR REPLACE FUNCTION trigger_synthesis_update()
RETURNS TRIGGER AS $$
BEGIN
    -- Update the synthesis profile's updated_at timestamp
    UPDATE personality_synthesis 
    SET updated_at = NOW()
    WHERE person_id = NEW.person_id;
    
    -- Check if confidence thresholds warrant a full re-analysis
    -- This would trigger background analysis job
    
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER personality_indicator_synthesis_update
    AFTER INSERT ON personality_indicators
    FOR EACH ROW EXECUTE FUNCTION trigger_synthesis_update();

CREATE TRIGGER anchor_activation_synthesis_update
    AFTER INSERT ON anchor_activations
    FOR EACH ROW EXECUTE FUNCTION trigger_synthesis_update();

-- Apply updated_at triggers to all profile tables
CREATE TRIGGER update_personality_synthesis_updated_at 
    BEFORE UPDATE ON personality_synthesis 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_enneagram_profiles_updated_at 
    BEFORE UPDATE ON enneagram_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_human_design_profiles_updated_at 
    BEFORE UPDATE ON human_design_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_astrology_profiles_updated_at 
    BEFORE UPDATE ON astrology_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_maya_calendar_profiles_updated_at 
    BEFORE UPDATE ON maya_calendar_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jungian_profiles_updated_at 
    BEFORE UPDATE ON jungian_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_becoming_one_profiles_updated_at 
    BEFORE UPDATE ON becoming_one_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- SAMPLE QUERIES AND VIEWS
-- ============================================================================

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
    
    -- Enneagram data
    en.core_type as enneagram_type,
    en.wing as enneagram_wing,
    
    -- Human Design data
    hd.type as hd_type,
    hd.strategy as hd_strategy,
    hd.authority as hd_authority,
    
    ps.updated_at
    
FROM personality_synthesis ps
JOIN identity_registry ir ON ps.person_id = ir.person_id
LEFT JOIN becoming_one_profiles bo ON ps.synthesis_id = bo.synthesis_id
LEFT JOIN enneagram_profiles en ON ps.synthesis_id = en.synthesis_id
LEFT JOIN human_design_profiles hd ON ps.synthesis_id = hd.synthesis_id;

-- View for recent personality insights
CREATE VIEW recent_personality_insights AS
SELECT 
    pi.person_id,
    ir.name,
    pi.system_type,
    pi.indicator_type,
    pi.indicator_value,
    pi.confidence,
    pi.created_at
FROM personality_indicators pi
JOIN identity_registry ir ON pi.person_id = ir.person_id
WHERE pi.created_at > NOW() - INTERVAL '30 days'
ORDER BY pi.created_at DESC;

-- Function to get personality summary for AI context
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
        'enneagram_type', (SELECT core_type FROM enneagram_profiles WHERE synthesis_id = ps.synthesis_id),
        'hd_type', (SELECT type FROM human_design_profiles WHERE synthesis_id = ps.synthesis_id),
        'confidence_scores', jsonb_build_object(
            'enneagram', enneagram_confidence,
            'human_design', human_design_confidence,
            'becoming_one', becoming_one_confidence
        )
    ) INTO result
    FROM personality_overview
    WHERE person_id = target_person_id;
    
    RETURN COALESCE(result, '{}'::jsonb);
END;
$$ LANGUAGE plpgsql;
