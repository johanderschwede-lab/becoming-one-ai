#!/usr/bin/env python3
"""
Database setup script for Becoming One™ AI Journey System
Run this script to initialize Supabase database with required tables
"""
import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from database.operations import SupabaseClient
from supabase import create_client
from loguru import logger


def load_sql_file(file_path: str) -> str:
    """Load SQL file content"""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"SQL file not found: {file_path}")
        raise


def setup_database():
    """Set up Supabase database with required tables"""
    logger.info("Starting database setup...")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not service_role_key:
        logger.error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        logger.error("Copy config/env.example to .env and fill in your credentials")
        return False
    
    try:
        # Use service role key for admin operations
        supabase = create_client(url, service_role_key)
        
        # Load schema file
        schema_path = Path(__file__).parent.parent / "database" / "schemas" / "supabase_schema.sql"
        schema_sql = load_sql_file(str(schema_path))
        
        # Execute schema
        logger.info("Creating database tables...")
        result = supabase.rpc("exec_sql", {"sql": schema_sql})
        
        logger.info("Database setup completed successfully!")
        
        # Test the setup
        logger.info("Testing database connection...")
        test_client = SupabaseClient()
        
        # Try to insert a test record
        identity_result = test_client.client.table("identity_registry").insert({
            "name": "Database Setup Test",
            "consent": False
        }).execute()
        
        if identity_result.data:
            test_person_id = identity_result.data[0]["person_id"]
            logger.info(f"Test record created with person_id: {test_person_id}")
            
            # Clean up test record
            test_client.client.table("identity_registry").delete().eq(
                "person_id", test_person_id
            ).execute()
            logger.info("Test record cleaned up")
        
        logger.info("✅ Database setup and testing completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        logger.error("Make sure your Supabase credentials are correct and you have admin access")
        return False


def verify_setup():
    """Verify database setup is working"""
    logger.info("Verifying database setup...")
    
    try:
        client = SupabaseClient()
        
        # Check if tables exist by trying to query them
        tables_to_check = ["identity_registry", "event_log", "channel_mapping"]
        
        for table in tables_to_check:
            result = client.client.table(table).select("*").limit(1).execute()
            logger.info(f"✅ Table '{table}' is accessible")
        
        logger.info("✅ All tables verified successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Database verification failed: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Set up Becoming One™ database")
    parser.add_argument("--verify-only", action="store_true", help="Only verify existing setup")
    args = parser.parse_args()
    
    if args.verify_only:
        success = verify_setup()
    else:
        success = setup_database()
        if success:
            verify_setup()
    
    sys.exit(0 if success else 1)
