#!/usr/bin/env python3
"""
Setup Supabase database schema for Compass system
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env')

def setup_supabase():
    """Setup Supabase database schema"""
    
    # Get Supabase credentials
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("Error: SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")
        return False
    
    # Read the schema file
    schema_path = "supabase_sync/schema.sql"
    if not os.path.exists(schema_path):
        print(f"Error: Schema file {schema_path} not found")
        return False
    
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    # Execute the schema via REST API
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/sql"
    }
    
    # Use the SQL endpoint
    sql_url = f"{url}/rest/v1/rpc/exec_sql"
    
    try:
        response = requests.post(sql_url, headers=headers, data=schema_sql)
        
        if response.status_code == 200:
            print("✅ Supabase schema setup successful!")
            return True
        else:
            print(f"❌ Schema setup failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up schema: {str(e)}")
        return False

if __name__ == "__main__":
    print("Setting up Supabase database schema...")
    success = setup_supabase()
    
    if success:
        print("Database is ready for document uploads!")
    else:
        print("Please check your Supabase configuration and try again.")
