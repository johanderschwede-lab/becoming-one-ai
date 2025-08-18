#!/usr/bin/env python3
"""
Create personality analysis tables in Supabase
Uses existing database connection
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

def create_tables():
    """Create personality analysis tables"""
    try:
        from database.operations import SupabaseClient
        
        print("🗄️ Creating personality analysis tables...")
        
        client = SupabaseClient()
        
        # Create personality_profiles table
        print("Creating personality_profiles table...")
        
        # Try to query the table first to see if it exists
        try:
            result = client.client.table('personality_profiles').select('*').limit(1).execute()
            print("✅ personality_profiles table already exists")
        except Exception:
            print("❌ personality_profiles table doesn't exist")
            print("⚠️  Need service role key to create tables")
            return False
        
        # Try personality_analysis table
        try:
            result = client.client.table('personality_analysis').select('*').limit(1).execute()
            print("✅ personality_analysis table already exists")
        except Exception:
            print("❌ personality_analysis table doesn't exist")
            print("⚠️  Need service role key to create tables")
            return False
            
        print("✅ All personality tables verified!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n🔍 Checking personality analysis tables...")
    
    success = create_tables()
    
    if success:
        print("\n✅ Database tables ready!")
    else:
        print("\n⚠️  Tables need to be created manually in Supabase dashboard")
        print("\nSQL to run in Supabase SQL Editor:")
        print("""
-- Create personality_profiles table
CREATE TABLE personality_profiles (
    profile_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID NOT NULL,
    core_patterns TEXT[],
    growth_edges TEXT[],
    essence_level TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create personality_analysis table  
CREATE TABLE personality_analysis (
    analysis_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    person_id UUID NOT NULL,
    message TEXT NOT NULL,
    source TEXT NOT NULL,
    analysis_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_personality_profiles_person_id ON personality_profiles(person_id);
CREATE INDEX idx_personality_analysis_person_id ON personality_analysis(person_id);
        """)

if __name__ == "__main__":
    main()
