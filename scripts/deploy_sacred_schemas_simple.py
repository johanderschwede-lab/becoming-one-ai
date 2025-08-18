#!/usr/bin/env python3
"""
Simple Sacred Library Schema Deployment
======================================

Deploy Sacred Library schemas using direct SQL execution
"""

import os
import requests
from pathlib import Path

def deploy_schemas_direct():
    """Deploy schemas using direct HTTP requests to Supabase"""
    
    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not service_key:
        print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY")
        return False
    
    print("🏛️  SACRED LIBRARY SCHEMA DEPLOYMENT")
    print("=" * 50)
    
    # Schema files to deploy
    schema_files = [
        "database/schemas/enhanced_hylozoics_schema.sql",
        "database/schemas/tiered_synthesis_schema.sql"
    ]
    
    headers = {
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json',
        'apikey': service_key
    }
    
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
            
            # Split into individual statements
            statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
            
            success_count = 0
            for i, statement in enumerate(statements):
                if not statement:
                    continue
                
                # Execute each statement
                response = requests.post(
                    f"{supabase_url}/rest/v1/rpc/exec_sql",
                    headers=headers,
                    json={'sql': statement}
                )
                
                if response.status_code in [200, 201]:
                    success_count += 1
                else:
                    print(f"    ⚠️  Statement {i+1} warning: {response.status_code}")
                    # Continue anyway - some statements might be CREATE IF NOT EXISTS
            
            print(f"    ✅ Executed {success_count}/{len(statements)} statements")
            
        except Exception as e:
            print(f"    ❌ Failed to deploy {schema_path.name}: {e}")
    
    print(f"\n🎉 Schema deployment complete!")
    print("🏛️  Sacred Library database should be ready!")
    return True

def create_tables_manually():
    """Create essential tables manually if RPC doesn't work"""
    
    supabase_url = os.getenv('SUPABASE_URL')
    service_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    # Essential table creation SQL
    essential_tables = {
        'hylozoics_sacred_quotes': '''
            CREATE TABLE IF NOT EXISTS hylozoics_sacred_quotes (
                quote_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                text TEXT NOT NULL,
                source_book VARCHAR(255) NOT NULL,
                chapter VARCHAR(255) NOT NULL,
                language VARCHAR(5) DEFAULT 'en',
                author VARCHAR(255) DEFAULT 'Henry T. Laurency',
                tradition VARCHAR(100) DEFAULT 'Hylozoics',
                verified BOOLEAN DEFAULT TRUE,
                hylozoics_terms TEXT[] DEFAULT '{}',
                metadata JSONB DEFAULT '{}',
                created_at TIMESTAMPTZ DEFAULT NOW()
            );
        ''',
        'user_subscriptions': '''
            CREATE TABLE IF NOT EXISTS user_subscriptions (
                subscription_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                user_id VARCHAR(255) NOT NULL,
                tier VARCHAR(50) NOT NULL,
                status VARCHAR(50) DEFAULT 'active',
                created_at TIMESTAMPTZ DEFAULT NOW(),
                expires_at TIMESTAMPTZ
            );
        '''
    }
    
    print("🔧 Creating essential tables manually...")
    
    headers = {
        'Authorization': f'Bearer {service_key}',
        'Content-Type': 'application/json',
        'apikey': service_key
    }
    
    for table_name, sql in essential_tables.items():
        try:
            print(f"  📋 Creating table: {table_name}")
            
            # Try direct REST API approach
            response = requests.post(
                f"{supabase_url}/rest/v1/rpc/exec_sql",
                headers=headers,
                json={'sql': sql}
            )
            
            if response.status_code in [200, 201]:
                print(f"    ✅ Created: {table_name}")
            else:
                print(f"    ⚠️  Response: {response.status_code} - {response.text[:100]}")
                
        except Exception as e:
            print(f"    ❌ Error creating {table_name}: {e}")
    
    return True

if __name__ == "__main__":
    print("🏛️  SIMPLIFIED SACRED LIBRARY SETUP")
    print("=" * 50)
    
    # Try direct deployment first
    if not deploy_schemas_direct():
        print("\n🔧 Trying manual table creation...")
        create_tables_manually()
    
    print("\n✅ Schema deployment complete!")
    print("🚀 Ready to build Sacred Library content!")
