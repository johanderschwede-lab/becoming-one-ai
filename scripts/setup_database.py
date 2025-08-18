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
    
    # Get credentials from environment (set by Railway)
    url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not url or not service_role_key:
        logger.error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in Railway")
        return False
    
    try:
        # Use service role key for admin operations
        supabase = create_client(url, service_role_key)
        
        # Load schema files
        schema_path = Path(__file__).parent.parent / "database" / "schemas"
        
        # Personality analysis schema
        personality_schema = load_sql_file(str(schema_path / "personality_analysis_schema.sql"))
        logger.info("Creating personality analysis tables...")
        supabase.rpc("exec_sql", {"sql": personality_schema})
        
        logger.info("Database setup completed successfully!")
        
        # Test the setup
        logger.info("Testing database connection...")
        test_client = SupabaseClient()
        
        # Try to insert test records
        identity_result = test_client.client.table("identity_registry").select("*").limit(1).execute()
        if identity_result.data:
            test_person_id = identity_result.data[0]["person_id"]
            logger.info(f"Using existing person_id: {test_person_id}")
            
            # Test personality profile
            profile_result = test_client.client.table("personality_profiles").insert({
                "person_id": test_person_id,
                "core_patterns": ["test_pattern"],
                "growth_edges": ["test_edge"],
                "essence_level": "test_level"
            }).execute()
            
            if profile_result.data:
                logger.info("Test personality profile created")
                
                # Clean up test profile
                test_client.client.table("personality_profiles").delete().eq(
                    "person_id", test_person_id
                ).execute()
                logger.info("Test profile cleaned up")
        
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
        tables_to_check = [
            "personality_profiles",
            "personality_analysis"
        ]
        
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