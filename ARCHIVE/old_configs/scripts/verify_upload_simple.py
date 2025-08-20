#!/usr/bin/env python3
"""
SIMPLE VERIFICATION OF SACRED LIBRARY UPLOAD
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

def verify_upload():
    """Simple verification of upload"""
    try:
        from database.operations import SupabaseClient
        
        db = SupabaseClient()
        print("✅ Supabase connected")
        
        # Simple count query
        result = db.client.table('teaching_materials').select('*', count='exact').eq('material_type', 'sacred_quote').execute()
        total_quotes = result.count
        print(f"📊 Total Sacred Library quotes: {total_quotes}")
        
        # Get a few sample records
        result = db.client.table('teaching_materials').select('title, metadata').eq('material_type', 'sacred_quote').limit(3).execute()
        print(f"📝 Sample records:")
        for i, record in enumerate(result.data):
            lang = record['metadata'].get('language', 'unknown')
            print(f"  {i+1}. [{lang}] {record['title']}")
        
        return total_quotes > 0
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

def main():
    print("🔍 VERIFYING SACRED LIBRARY UPLOAD")
    print("=" * 40)
    
    load_environment()
    
    if verify_upload():
        print("\n🎉 Sacred Library upload verified!")
    else:
        print("\n❌ Verification failed")

if __name__ == "__main__":
    main()
