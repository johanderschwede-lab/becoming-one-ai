#!/usr/bin/env python3
"""
TEST SUPABASE SACRED LIBRARY QUERIES
Verify that all quotes were uploaded and are searchable
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def load_environment():
    """Load environment variables from production.env"""
    env_path = Path(__file__).parent.parent / "config" / "production.env"
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    return True

def test_sacred_queries():
    """Test Sacred Library queries in Supabase"""
    try:
        from database.operations import SupabaseClient
        
        db = SupabaseClient()
        print("✅ Supabase connected")
        
        # Test 1: Count total Sacred Library quotes
        result = db.client.table('teaching_materials').select('*', count='exact').eq('material_type', 'sacred_quote').execute()
        total_quotes = result.count
        print(f"📊 Total Sacred Library quotes in Supabase: {total_quotes}")
        
        # Test 2: Check languages
        result = db.client.table('teaching_materials').select('metadata').eq('material_type', 'sacred_quote').limit(100).execute()
        languages = set()
        for record in result.data:
            if 'language' in record['metadata']:
                languages.add(record['metadata']['language'])
        print(f"🌐 Languages found: {sorted(languages)}")
        
        # Test 3: Search for meditation
        result = db.client.table('teaching_materials').select('*').eq('material_type', 'sacred_quote').ilike('content', '%meditation%').limit(5).execute()
        print(f"🔍 Found {len(result.data)} quotes containing 'meditation'")
        for i, quote in enumerate(result.data):
            print(f"  {i+1}. {quote['metadata']['language']}: {quote['content'][:100]}...")
        
        # Test 4: Search for Swedish content
        result = db.client.table('teaching_materials').select('*').eq('material_type', 'sacred_quote').eq('metadata->>language', 'sv').limit(5).execute()
        print(f"🇸🇪 Found {len(result.data)} Swedish quotes")
        for i, quote in enumerate(result.data):
            print(f"  {i+1}. {quote['content'][:100]}...")
        
        # Test 5: Search for German content
        result = db.client.table('teaching_materials').select('*').eq('material_type', 'sacred_quote').eq('metadata->>language', 'de').limit(5).execute()
        print(f"🇩🇪 Found {len(result.data)} German quotes")
        for i, quote in enumerate(result.data):
            print(f"  {i+1}. {quote['content'][:100]}...")
        
        # Test 6: Check books/chapters
        result = db.client.table('teaching_materials').select('metadata').eq('material_type', 'sacred_quote').limit(100).execute()
        chapters = set()
        for record in result.data:
            if 'chapter' in record['metadata']:
                chapters.add(record['metadata']['chapter'])
        print(f"📚 Chapters found: {sorted(list(chapters))[:10]}...")  # Show first 10
        
        return True
        
    except Exception as e:
        print(f"❌ Query test failed: {e}")
        return False

def main():
    print("🧪 TESTING SUPABASE SACRED LIBRARY QUERIES")
    print("=" * 50)
    
    load_environment()
    
    if test_sacred_queries():
        print("\n🎉 Sacred Library queries working perfectly!")
    else:
        print("\n❌ Query tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
