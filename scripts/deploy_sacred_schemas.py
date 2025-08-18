#!/usr/bin/env python3
"""
Sacred Library Schema Deployment
================================

Deploy all Sacred Library database schemas to Supabase
"""

import os
from supabase import create_client, Client
from pathlib import Path

def deploy_schemas():
    """Deploy all Sacred Library schemas to Supabase"""
    
    # Initialize Supabase
    supabase: Client = create_client(
        os.getenv('SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_KEY')  # Need service key for schema operations
    )
    
    print("🏛️  SACRED LIBRARY SCHEMA DEPLOYMENT")
    print("=" * 50)
    
    # Schema files to deploy
    schema_files = [
        "database/schemas/enhanced_hylozoics_schema.sql",
        "database/schemas/tiered_synthesis_schema.sql"
    ]
    
    for schema_file in schema_files:
        schema_path = Path(schema_file)
        
        if not schema_path.exists():
            print(f"❌ Schema file not found: {schema_file}")
            continue
        
        print(f"📋 Deploying: {schema_path.name}")
        
        try:
            # Read schema SQL
            with open(schema_path, 'r') as f:
                sql_content = f.read()
            
            # Execute schema
            result = supabase.rpc('exec_sql', {'sql': sql_content}).execute()
            
            print(f"✅ Successfully deployed: {schema_path.name}")
            
        except Exception as e:
            print(f"❌ Failed to deploy {schema_path.name}: {e}")
    
    print(f"\n🎉 Schema deployment complete!")
    print("🏛️  Sacred Library database is ready!")

if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_SERVICE_KEY'):
        print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY environment variables")
        print("Please set these before running schema deployment.")
        exit(1)
    
    deploy_schemas()
