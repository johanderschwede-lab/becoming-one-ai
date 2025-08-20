-- Hylozoics Sacred Library Database Schema
-- Zero-hallucination teaching system for Henry T. Laurency's works

-- Table for storing exact quotes from Laurency's works
CREATE TABLE IF NOT EXISTS hylozoics_quotes (
    quote_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    text TEXT NOT NULL, -- Exact quote from source
    source_book VARCHAR(255) NOT NULL, -- e.g., "The Knowledge of Reality"
    page_number INTEGER,
    chapter VARCHAR(255) NOT NULL,
    section VARCHAR(255),
    paragraph_number INTEGER,
    hylozoics_terms TEXT[] DEFAULT '{}', -- Array of key terms in this quote
    related_concepts TEXT[] DEFAULT '{}', -- Related Hylozoics concepts
    context TEXT, -- Surrounding context for understanding
    verified BOOLEAN DEFAULT FALSE, -- Must be manually verified
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table for Hylozoics terminology index
CREATE TABLE IF NOT EXISTS hylozoics_terminology (
    term_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    term VARCHAR(255) UNIQUE NOT NULL,
    definition TEXT NOT NULL, -- Laurency's definition
    source_quote_id UUID REFERENCES hylozoics_quotes(quote_id),
    related_terms TEXT[] DEFAULT '{}',
    kingdom_context VARCHAR(100), -- Which kingdom this term primarily relates to
    world_context VARCHAR(100), -- Which world/plane this term relates to
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table for book structure and navigation
CREATE TABLE IF NOT EXISTS hylozoics_books (
    book_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) UNIQUE NOT NULL,
    author VARCHAR(255) DEFAULT 'Henry T. Laurency',
    publication_year INTEGER,
    total_pages INTEGER,
    description TEXT,
    difficulty_level INTEGER CHECK (difficulty_level BETWEEN 1 AND 5),
    prerequisites TEXT[], -- Other books to read first
    main_concepts TEXT[], -- Key concepts covered
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table for chapter structure
CREATE TABLE IF NOT EXISTS hylozoics_chapters (
    chapter_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    book_id UUID REFERENCES hylozoics_books(book_id) ON DELETE CASCADE,
    chapter_number INTEGER,
    chapter_title VARCHAR(255) NOT NULL,
    summary TEXT,
    key_concepts TEXT[],
    quote_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(book_id, chapter_number)
);

-- Table for tracking user interactions with Sacred Library
CREATE TABLE IF NOT EXISTS hylozoics_interactions (
    interaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID REFERENCES identity_registry(person_id),
    quote_id UUID REFERENCES hylozoics_quotes(quote_id),
    question TEXT, -- User's original question
    response_type VARCHAR(50), -- 'quote_found', 'no_quote', 'error'
    satisfaction_rating INTEGER CHECK (satisfaction_rating BETWEEN 1 AND 5),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table for Sacred Library access control
CREATE TABLE IF NOT EXISTS sacred_library_access (
    access_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID REFERENCES identity_registry(person_id),
    library_name VARCHAR(100) NOT NULL, -- 'hylozoics', 'fourth_way', etc.
    access_level VARCHAR(50) DEFAULT 'basic', -- 'basic', 'advanced', 'teacher'
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    granted_by VARCHAR(255), -- Who granted access
    notes TEXT,
    UNIQUE(person_id, library_name)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_hylozoics_quotes_source_book ON hylozoics_quotes(source_book);
CREATE INDEX IF NOT EXISTS idx_hylozoics_quotes_chapter ON hylozoics_quotes(chapter);
CREATE INDEX IF NOT EXISTS idx_hylozoics_quotes_terms ON hylozoics_quotes USING GIN(hylozoics_terms);
CREATE INDEX IF NOT EXISTS idx_hylozoics_quotes_concepts ON hylozoics_quotes USING GIN(related_concepts);
CREATE INDEX IF NOT EXISTS idx_hylozoics_quotes_verified ON hylozoics_quotes(verified);

CREATE INDEX IF NOT EXISTS idx_hylozoics_terminology_term ON hylozoics_terminology(term);
CREATE INDEX IF NOT EXISTS idx_hylozoics_terminology_related ON hylozoics_terminology USING GIN(related_terms);

CREATE INDEX IF NOT EXISTS idx_hylozoics_interactions_person ON hylozoics_interactions(person_id);
CREATE INDEX IF NOT EXISTS idx_hylozoics_interactions_quote ON hylozoics_interactions(quote_id);
CREATE INDEX IF NOT EXISTS idx_hylozoics_interactions_created ON hylozoics_interactions(created_at);

CREATE INDEX IF NOT EXISTS idx_sacred_library_access_person ON sacred_library_access(person_id);
CREATE INDEX IF NOT EXISTS idx_sacred_library_access_library ON sacred_library_access(library_name);

-- Function to update quote count in chapters
CREATE OR REPLACE FUNCTION update_chapter_quote_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE hylozoics_chapters 
    SET quote_count = (
        SELECT COUNT(*) 
        FROM hylozoics_quotes q
        JOIN hylozoics_books b ON q.source_book = b.title
        WHERE b.book_id = hylozoics_chapters.book_id 
        AND q.chapter = hylozoics_chapters.chapter_title
    )
    WHERE book_id IN (
        SELECT book_id FROM hylozoics_books WHERE title = COALESCE(NEW.source_book, OLD.source_book)
    );
    
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update quote counts
CREATE TRIGGER trigger_update_chapter_quote_count
    AFTER INSERT OR UPDATE OR DELETE ON hylozoics_quotes
    FOR EACH ROW EXECUTE FUNCTION update_chapter_quote_count();

-- Row Level Security (RLS) policies
ALTER TABLE hylozoics_quotes ENABLE ROW LEVEL SECURITY;
ALTER TABLE hylozoics_terminology ENABLE ROW LEVEL SECURITY;
ALTER TABLE hylozoics_interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE sacred_library_access ENABLE ROW LEVEL SECURITY;

-- Policy: Anyone can read verified quotes
CREATE POLICY "Anyone can read verified quotes" ON hylozoics_quotes
    FOR SELECT USING (verified = true);

-- Policy: Only admins can insert/update quotes
CREATE POLICY "Only admins can modify quotes" ON hylozoics_quotes
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM sacred_library_access 
            WHERE person_id = auth.uid() 
            AND library_name = 'hylozoics' 
            AND access_level IN ('teacher', 'admin')
        )
    );

-- Policy: Anyone can read terminology
CREATE POLICY "Anyone can read terminology" ON hylozoics_terminology
    FOR SELECT TO PUBLIC USING (true);

-- Policy: Users can read their own interactions
CREATE POLICY "Users can read their own interactions" ON hylozoics_interactions
    FOR SELECT USING (person_id = auth.uid());

-- Policy: Users can insert their own interactions
CREATE POLICY "Users can insert their own interactions" ON hylozoics_interactions
    FOR INSERT WITH CHECK (person_id = auth.uid());

-- Policy: Users can read their own access records
CREATE POLICY "Users can read their own access" ON sacred_library_access
    FOR SELECT USING (person_id = auth.uid());

-- Sample data for testing (Henry T. Laurency books)
INSERT INTO hylozoics_books (title, publication_year, description, difficulty_level, main_concepts) VALUES
('The Knowledge of Reality', 1979, 'Introduction to Hylozoics - the esoteric knowledge of life and matter', 2, ARRAY['consciousness', 'evolution', 'kingdoms', 'worlds']),
('The Philosopher''s Stone', 1980, 'Advanced teachings on consciousness and cosmic evolution', 3, ARRAY['monad', 'causal consciousness', 'mental worlds']),
('The Way of Man', 1981, 'Practical guidance for human development within Hylozoics framework', 2, ARRAY['self-realization', 'emotional development', 'mental development']);

-- Sample terminology entries
INSERT INTO hylozoics_terminology (term, definition, kingdom_context, world_context) VALUES
('hylozoics', 'The esoteric knowledge of life and matter, teaching that all existence is conscious', 'all', 'all'),
('monad', 'The ultimate, indivisible unit of consciousness', 'all', 'all'),
('envelope', 'The temporary vehicles of consciousness (physical, emotional, mental, causal)', 'human', 'multiple'),
('kingdom', 'Stages of evolution: mineral, vegetable, animal, human, superhuman', 'all', 'physical'),
('consciousness', 'The fundamental property of all existence, manifesting as awareness and will', 'all', 'all');
