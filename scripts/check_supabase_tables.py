#!/usr/bin/env python3
"""
CHECK SUPABASE TABLE STRUCTURES
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

def check_tables():
    """Check what tables exist and their structure"""
    try:
        from database.operations import SupabaseClient
        
        db = SupabaseClient()
        print("✅ Supabase connected")
        
        # Check teaching_materials table
        try:
            result = db.client.table('teaching_materials').select('*').limit(1).execute()
            print(f"✅ teaching_materials table exists - {len(result.data)} records")
            if result.data:
                print(f"📋 Sample record columns: {list(result.data[0].keys())}")
        except Exception as e:
            print(f"❌ teaching_materials error: {e}")
        
        # Check other relevant tables
        tables_to_check = ['content_chunks', 'community_content', 'people']
        
        for table_name in tables_to_check:
            try:
                result = db.client.table(table_name).select('*').limit(1).execute()
                print(f"✅ {table_name} table exists - {len(result.data)} records")
                if result.data:
                    print(f"📋 {table_name} columns: {list(result.data[0].keys())}")
            except Exception as e:
                print(f"❌ {table_name} error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to check tables: {e}")
        return False

def main():
    print("🔍 CHECKING SUPABASE TABLE STRUCTURES")
    print("=" * 40)
    
    load_environment()
    check_tables()

if __name__ == "__main__":
    main()
