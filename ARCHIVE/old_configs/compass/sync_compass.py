"""
Sync the System Compass between Git and Supabase.
"""
import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any
import hashlib
from datetime import datetime

from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL", ""),
    os.getenv("SUPABASE_ANON_KEY", "")
)

def load_compass_yaml() -> Dict[str, Any]:
    """Load the compass.yaml file."""
    compass_path = Path(__file__).parent / "compass.yaml"
    with open(compass_path, "r") as f:
        return yaml.safe_load(f)

def calculate_checksum(content: Dict[str, Any]) -> str:
    """Calculate SHA256 checksum of compass content."""
    content_str = json.dumps(content, sort_keys=True)
    return hashlib.sha256(content_str.encode()).hexdigest()

def sync_compass_to_supabase() -> None:
    """Sync the current compass version to Supabase."""
    # Load compass content
    compass_content = load_compass_yaml()
    
    # Calculate checksum
    checksum = calculate_checksum(compass_content)
    
    # Check if version already exists
    version = compass_content.get("version")
    existing = supabase.table("compass_versions").select("*").eq("version", version).execute()
    
    if existing.data:
        print(f"Version {version} already exists in Supabase")
        if existing.data[0]["checksum"] != checksum:
            print("Warning: Content differs from Supabase version")
        return

    # Create new compass version
    user_id = os.getenv("SUPABASE_USER_ID")  # Set this in .env
    if not user_id:
        raise ValueError("SUPABASE_USER_ID must be set")

    result = supabase.rpc(
        "create_compass_version",
        {
            "p_version": version,
            "p_content": compass_content,
            "p_created_by": user_id
        }
    ).execute()

    print(f"Synced compass version {version} to Supabase")

if __name__ == "__main__":
    sync_compass_to_supabase()

