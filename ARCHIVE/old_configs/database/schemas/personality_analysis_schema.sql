-- Personality Analysis Tables for Background Processing

-- Main personality profiles table
CREATE TABLE personality_profiles (
    profile_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID NOT NULL,
    core_patterns TEXT[],
    growth_edges TEXT[],
    essence_level TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Analysis results table
CREATE TABLE personality_analysis (
    analysis_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID NOT NULL,
    message TEXT NOT NULL,
    source TEXT NOT NULL,
    analysis_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_personality_profiles_person_id ON personality_profiles(person_id);
CREATE INDEX idx_personality_analysis_person_id ON personality_analysis(person_id);

-- Updated timestamp trigger
CREATE TRIGGER update_personality_profiles_updated_at 
    BEFORE UPDATE ON personality_profiles 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
