-- Enhanced Hylozoics Sacred Library Schema
-- Supports multi-language quotes and dual-mode responses (Sacred + Vector)

-- Enhanced quotes table with multi-language support
CREATE TABLE IF NOT EXISTS hylozoics_multilang_quotes (
    quote_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Original Swedish text (authoritative)
    original_text TEXT NOT NULL,
    original_language VARCHAR(5) DEFAULT 'sv',
    
    -- Translations
    english_translation TEXT,
    german_translation TEXT,
    
    -- Source information
    source_book VARCHAR(255) NOT NULL,
    source_book_swedish VARCHAR(255), -- Original Swedish title
    page_number INTEGER,
    chapter VARCHAR(255) NOT NULL,
    chapter_swedish VARCHAR(255), -- Original Swedish chapter title
    section VARCHAR(255),
    section_swedish VARCHAR(255),
    paragraph_number INTEGER,
    
    -- Hylozoics terminology
    hylozoics_terms TEXT[] DEFAULT '{}',
    untranslatable_terms TEXT[] DEFAULT '{}', -- Terms that don't translate well
    
    -- Translation metadata
    english_notes TEXT, -- Translation context/notes
    german_notes TEXT,
    translation_quality_english DECIMAL(3,2), -- Quality score 0.00-1.00
    translation_quality_german DECIMAL(3,2),
    
    -- Verification and metadata
    verified BOOLEAN DEFAULT FALSE,
    verified_by VARCHAR(255), -- Who verified the quote
    original_verified BOOLEAN DEFAULT FALSE, -- Swedish original verified
    translation_verified_english BOOLEAN DEFAULT FALSE,
    translation_verified_german BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Cross-library concept mappings for comparative analysis
CREATE TABLE IF NOT EXISTS cross_library_concepts (
    concept_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Core concept information
    concept_name VARCHAR(255) NOT NULL,
    concept_description TEXT,
    
    -- Hylozoics representation
    hylozoics_term VARCHAR(255),
    hylozoics_swedish_term VARCHAR(255),
    hylozoics_definition TEXT,
    hylozoics_quote_ids UUID[], -- References to relevant quotes
    
    -- Fourth Way representation (for future expansion)
    fourth_way_term VARCHAR(255),
    fourth_way_definition TEXT,
    fourth_way_quote_ids UUID[],
    
    -- Neville Goddard representation (for future expansion)
    neville_term VARCHAR(255),
    neville_definition TEXT,
    neville_quote_ids UUID[],
    
    -- Comparative analysis
    similarities TEXT[], -- How traditions agree
    differences TEXT[], -- How traditions differ
    synthesis_notes TEXT, -- AI-generated synthesis insights
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Term equivalency mappings across languages and traditions
CREATE TABLE IF NOT EXISTS term_equivalencies (
    mapping_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Core term
    base_concept VARCHAR(255) NOT NULL,
    
    -- Hylozoics terms
    swedish_term VARCHAR(255),
    english_term VARCHAR(255),
    german_term VARCHAR(255),
    
    -- Cross-tradition equivalents
    fourth_way_equivalent VARCHAR(255),
    neville_equivalent VARCHAR(255),
    
    -- Linguistic notes
    translation_difficulty VARCHAR(50), -- 'easy', 'moderate', 'difficult', 'impossible'
    cultural_context TEXT, -- Cultural background needed
    usage_notes TEXT, -- How the term is used
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Vector insights cache for performance
CREATE TABLE IF NOT EXISTS vector_insights_cache (
    cache_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Query information
    user_question TEXT NOT NULL,
    question_embedding_hash VARCHAR(64), -- Hash of the embedding for deduplication
    
    -- Primary quote
    primary_quote_id UUID REFERENCES hylozoics_multilang_quotes(quote_id),
    
    -- AI-generated insights
    concept_connections TEXT[], -- Related concepts found
    cross_references TEXT[], -- Other relevant quotes
    synthesis_summary TEXT, -- AI synthesis
    study_suggestions TEXT[], -- Recommended follow-up
    confidence_score DECIMAL(3,2), -- AI confidence 0.00-1.00
    
    -- Cache metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '7 days'), -- Cache for 1 week
    usage_count INTEGER DEFAULT 0,
    
    -- Performance tracking
    generation_time_ms INTEGER, -- Time to generate insights
    tokens_used INTEGER -- OpenAI tokens consumed
);

-- User interaction tracking with language preferences
CREATE TABLE IF NOT EXISTS hylozoics_interactions_enhanced (
    interaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID REFERENCES identity_registry(person_id),
    
    -- Query information
    question TEXT NOT NULL,
    response_mode VARCHAR(50) NOT NULL, -- 'sacred_only', 'vector_only', 'dual_mode'
    preferred_language VARCHAR(5) DEFAULT 'en', -- 'sv', 'en', 'de'
    
    -- Response information
    primary_quote_id UUID REFERENCES hylozoics_multilang_quotes(quote_id),
    related_quote_ids UUID[], -- Other quotes shown
    vector_insights_provided BOOLEAN DEFAULT FALSE,
    
    -- User feedback
    satisfaction_rating INTEGER CHECK (satisfaction_rating BETWEEN 1 AND 5),
    feedback_text TEXT,
    helpful_vote BOOLEAN, -- Was this response helpful?
    
    -- Analytics
    response_time_ms INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Study progression tracking across languages and traditions
CREATE TABLE IF NOT EXISTS study_progression (
    progression_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID REFERENCES identity_registry(person_id),
    
    -- Current study focus
    current_tradition VARCHAR(50) NOT NULL, -- 'hylozoics', 'fourth_way', 'neville'
    current_language VARCHAR(5) DEFAULT 'en',
    study_level VARCHAR(50) DEFAULT 'beginner', -- 'beginner', 'intermediate', 'advanced'
    
    -- Progress tracking
    quotes_studied INTEGER DEFAULT 0,
    concepts_explored TEXT[], -- Concepts user has engaged with
    books_accessed TEXT[], -- Books user has accessed
    favorite_quotes UUID[], -- User's favorite quotes
    
    -- Learning preferences
    prefers_original_language BOOLEAN DEFAULT FALSE,
    prefers_dual_mode BOOLEAN DEFAULT TRUE,
    interested_in_comparisons BOOLEAN DEFAULT FALSE,
    
    -- Goals and recommendations
    study_goals TEXT,
    next_recommendations TEXT[],
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(person_id, current_tradition)
);

-- Enhanced indexes for performance
CREATE INDEX IF NOT EXISTS idx_multilang_quotes_original ON hylozoics_multilang_quotes(original_language);
CREATE INDEX IF NOT EXISTS idx_multilang_quotes_source ON hylozoics_multilang_quotes(source_book);
CREATE INDEX IF NOT EXISTS idx_multilang_quotes_terms ON hylozoics_multilang_quotes USING GIN(hylozoics_terms);
CREATE INDEX IF NOT EXISTS idx_multilang_quotes_untranslatable ON hylozoics_multilang_quotes USING GIN(untranslatable_terms);
CREATE INDEX IF NOT EXISTS idx_multilang_quotes_verified ON hylozoics_multilang_quotes(verified, original_verified);

CREATE INDEX IF NOT EXISTS idx_cross_library_concept ON cross_library_concepts(concept_name);
CREATE INDEX IF NOT EXISTS idx_cross_library_hylozoics_quotes ON cross_library_concepts USING GIN(hylozoics_quote_ids);

CREATE INDEX IF NOT EXISTS idx_term_equivalencies_base ON term_equivalencies(base_concept);
CREATE INDEX IF NOT EXISTS idx_term_equivalencies_swedish ON term_equivalencies(swedish_term);
CREATE INDEX IF NOT EXISTS idx_term_equivalencies_difficulty ON term_equivalencies(translation_difficulty);

CREATE INDEX IF NOT EXISTS idx_vector_cache_hash ON vector_insights_cache(question_embedding_hash);
CREATE INDEX IF NOT EXISTS idx_vector_cache_expires ON vector_insights_cache(expires_at);
CREATE INDEX IF NOT EXISTS idx_vector_cache_quote ON vector_insights_cache(primary_quote_id);

CREATE INDEX IF NOT EXISTS idx_interactions_enhanced_person ON hylozoics_interactions_enhanced(person_id);
CREATE INDEX IF NOT EXISTS idx_interactions_enhanced_mode ON hylozoics_interactions_enhanced(response_mode);
CREATE INDEX IF NOT EXISTS idx_interactions_enhanced_language ON hylozoics_interactions_enhanced(preferred_language);
CREATE INDEX IF NOT EXISTS idx_interactions_enhanced_created ON hylozoics_interactions_enhanced(created_at);

CREATE INDEX IF NOT EXISTS idx_study_progression_person ON study_progression(person_id);
CREATE INDEX IF NOT EXISTS idx_study_progression_tradition ON study_progression(current_tradition);
CREATE INDEX IF NOT EXISTS idx_study_progression_level ON study_progression(study_level);

-- Functions for cache management
CREATE OR REPLACE FUNCTION clean_expired_vector_cache()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM vector_insights_cache WHERE expires_at < NOW();
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to update study progression
CREATE OR REPLACE FUNCTION update_study_progression(
    p_person_id UUID,
    p_quote_id UUID,
    p_concepts TEXT[]
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO study_progression (person_id, current_tradition, quotes_studied, concepts_explored)
    VALUES (p_person_id, 'hylozoics', 1, p_concepts)
    ON CONFLICT (person_id, current_tradition)
    DO UPDATE SET
        quotes_studied = study_progression.quotes_studied + 1,
        concepts_explored = array(SELECT DISTINCT unnest(study_progression.concepts_explored || p_concepts)),
        updated_at = NOW();
END;
$$ LANGUAGE plpgsql;

-- Row Level Security policies
ALTER TABLE hylozoics_multilang_quotes ENABLE ROW LEVEL SECURITY;
ALTER TABLE cross_library_concepts ENABLE ROW LEVEL SECURITY;
ALTER TABLE term_equivalencies ENABLE ROW LEVEL SECURITY;
ALTER TABLE vector_insights_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE hylozoics_interactions_enhanced ENABLE ROW LEVEL SECURITY;
ALTER TABLE study_progression ENABLE ROW LEVEL SECURITY;

-- Policies for multilang quotes
CREATE POLICY "Anyone can read verified multilang quotes" ON hylozoics_multilang_quotes
    FOR SELECT USING (verified = true);

CREATE POLICY "Admins can modify multilang quotes" ON hylozoics_multilang_quotes
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM sacred_library_access 
            WHERE person_id = auth.uid() 
            AND library_name = 'hylozoics' 
            AND access_level IN ('admin', 'translator')
        )
    );

-- Policies for cross-library concepts
CREATE POLICY "Anyone can read cross-library concepts" ON cross_library_concepts
    FOR SELECT TO PUBLIC USING (true);

-- Policies for term equivalencies
CREATE POLICY "Anyone can read term equivalencies" ON term_equivalencies
    FOR SELECT TO PUBLIC USING (true);

-- Policies for vector cache (performance optimization)
CREATE POLICY "Users can read vector cache" ON vector_insights_cache
    FOR SELECT TO PUBLIC USING (true);

CREATE POLICY "System can manage vector cache" ON vector_insights_cache
    FOR ALL USING (true);

-- Policies for enhanced interactions
CREATE POLICY "Users can read their own interactions" ON hylozoics_interactions_enhanced
    FOR SELECT USING (person_id = auth.uid());

CREATE POLICY "Users can insert their own interactions" ON hylozoics_interactions_enhanced
    FOR INSERT WITH CHECK (person_id = auth.uid());

-- Policies for study progression
CREATE POLICY "Users can manage their own progression" ON study_progression
    FOR ALL USING (person_id = auth.uid());

-- Sample data for testing multi-language support
INSERT INTO hylozoics_multilang_quotes (
    quote_id,
    original_text,
    english_translation,
    german_translation,
    source_book,
    source_book_swedish,
    chapter,
    chapter_swedish,
    hylozoics_terms,
    untranslatable_terms,
    english_notes,
    verified,
    original_verified,
    translation_verified_english
) VALUES (
    gen_random_uuid(),
    'Medvetenhet är den grundläggande egenskapen hos all tillvaro. Allt som existerar är medvetet.',
    'Consciousness is the fundamental property of all existence. Everything that exists is conscious.',
    'Bewusstsein ist die grundlegende Eigenschaft aller Existenz. Alles was existiert ist bewusst.',
    'The Knowledge of Reality',
    'Verklighetskunskap',
    'Chapter 1: The Nature of Reality',
    'Kapitel 1: Verklighetens natur',
    ARRAY['medvetenhet', 'tillvaro', 'existens'],
    ARRAY['medvetenhet'], -- Hard to translate precisely
    'The Swedish term "medvetenhet" encompasses both consciousness and awareness in a unified concept.',
    true,
    true,
    true
);

-- Sample cross-library concept
INSERT INTO cross_library_concepts (
    concept_name,
    concept_description,
    hylozoics_term,
    hylozoics_swedish_term,
    hylozoics_definition,
    similarities,
    differences
) VALUES (
    'Universal Consciousness',
    'The idea that consciousness is a fundamental property of reality',
    'consciousness',
    'medvetenhet',
    'The fundamental property of all existence according to Hylozoics',
    ARRAY['All traditions recognize consciousness as fundamental', 'Each sees consciousness as more than brain activity'],
    ARRAY['Hylozoics: consciousness in all matter', 'Fourth Way: levels of consciousness', 'Neville: consciousness as creative principle']
);

-- Sample term equivalencies
INSERT INTO term_equivalencies (
    base_concept,
    swedish_term,
    english_term,
    german_term,
    translation_difficulty,
    cultural_context,
    usage_notes
) VALUES 
(
    'consciousness',
    'medvetenhet',
    'consciousness',
    'Bewusstsein',
    'moderate',
    'Swedish "medvetenhet" has a more unified meaning than English "consciousness/awareness"',
    'Often used interchangeably with awareness in Hylozoics context'
),
(
    'monad',
    'monad',
    'monad',
    'Monade',
    'easy',
    'Technical term preserved across languages in esoteric traditions',
    'Refers to the ultimate unit of consciousness in Hylozoics'
);

-- Create scheduled job to clean cache (if supported by your Postgres setup)
-- SELECT cron.schedule('clean-vector-cache', '0 2 * * *', 'SELECT clean_expired_vector_cache();');
