#!/usr/bin/env python3
"""
TEST DIRECT SUPABASE ACCESS
Using the exact same approach as your working database operations
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

def test_existing_supabase():
    """Test using your existing working Supabase operations"""
    try:
        from database.operations import SupabaseClient
        
        print("✅ Successfully imported existing SupabaseClient")
        
        # Initialize using your working pattern
        db = SupabaseClient()
        print("✅ SupabaseClient initialized successfully")
        
        # Test connection
        result = db.client.table('people').select('*').limit(1).execute()
        print(f"✅ Connection test successful - found {len(result.data)} records")
        
        return db
        
    except Exception as e:
        print(f"❌ Existing Supabase client failed: {e}")
        return None

def upload_sample_quote(db):
    """Upload a single quote to test the upload process"""
    try:
        # Sample quote data
        sample_quote = {
            'content': 'Test quote from Hylozoics Sacred Library',
            'title': 'Hylozoics: Test Quote - Chunk 1',
            'category': 'hylozoics_sacred',
            'source_file': 'test.pdf',
            'language': 'en',
            'metadata': {
                'book': 'Test Book',
                'chunk_index': 1,
                'confidence_score': 1.0,
                'sacred_library': True,
                'verbatim_quote': True
            }
        }
        
        result = db.client.table('teaching_materials').insert(sample_quote).execute()
        print("✅ Sample quote uploaded successfully!")
        print(f"📝 Uploaded quote ID: {result.data[0].get('id', 'unknown')}")
        return True
        
    except Exception as e:
        print(f"❌ Sample upload failed: {e}")
        return False

def main():
    print("🧪 TESTING DIRECT SUPABASE ACCESS")
    print("=" * 40)
    
    # Load environment
    load_environment()
    
    # Test existing Supabase client
    db = test_existing_supabase()
    if not db:
        sys.exit(1)
    
    # Test upload
    if upload_sample_quote(db):
        print("\n🎉 Supabase upload is working!")
        print("✅ Ready to upload full Sacred Library")
    else:
        print("\n❌ Upload test failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
