#!/usr/bin/env python3
"""
DIRECT SUPABASE SACRED LIBRARY UPLOADER
Uses simple table operations to upload Sacred Library
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from supabase import create_client, Client

def load_environment():
    """Load environment variables from production.env"""
    env_path = Path(__file__).parent.parent / "config" / "production.env"
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Check required environment variables
    required_vars = ['SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    return True

def test_connection(supabase: Client):
    """Test Supabase connection by trying to access existing tables"""
    try:
        # Try to query an existing table to test connection
        result = supabase.table('people').select('*').limit(1).execute()
        print("✅ Supabase connection verified")
        return True
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

def upload_quotes_to_existing_table(supabase: Client):
    """Upload quotes to an existing table (like teaching_materials)"""
    sacred_dir = Path(__file__).parent.parent / "sacred_library_files"
    quotes_dir = sacred_dir / "quotes"
    
    if not quotes_dir.exists():
        print(f"❌ Sacred Library quotes directory not found: {quotes_dir}")
        return False
    
    print(f"📁 Found Sacred Library at: {sacred_dir}")
    
    # Load master index
    master_index_path = sacred_dir / "MASTER_INDEX.json"
    if master_index_path.exists():
        with open(master_index_path, 'r') as f:
            master_index = json.load(f)
        print(f"📊 Master index shows {master_index['total_quotes']} quotes")
    
    # Get all quote files
    quote_files = list(quotes_dir.glob("*.json"))
    print(f"📝 Found {len(quote_files)} quote files to upload")
    
    uploaded_count = 0
    batch_size = 50  # Smaller batches
    
    # Process in batches
    for i in range(0, min(100, len(quote_files)), batch_size):  # Start with just 100 for testing
        batch_files = quote_files[i:i + batch_size]
        batch_data = []
        
        for quote_file in batch_files:
            try:
                with open(quote_file, 'r', encoding='utf-8') as f:
                    quote_data = json.load(f)
                
                # Prepare data for teaching_materials table
                upload_data = {
                    'content': quote_data['text'],
                    'title': f"{quote_data['metadata']['book']} - Chunk {quote_data['metadata']['chunk_index']}",
                    'category': 'hylozoics_sacred',
                    'source_file': quote_data['metadata']['source_file'],
                    'language': quote_data['metadata']['language'],
                    'metadata': {
                        'book': quote_data['metadata']['book'],
                        'chunk_index': quote_data['metadata']['chunk_index'],
                        'confidence_score': quote_data['metadata'].get('confidence_score', 1.0),
                        'sacred_library': True,
                        'verbatim_quote': True
                    }
                }
                
                batch_data.append(upload_data)
                
            except Exception as e:
                print(f"⚠️  Error processing {quote_file.name}: {e}")
                continue
        
        # Upload batch to Supabase
        if batch_data:
            try:
                result = supabase.table('teaching_materials').insert(batch_data).execute()
                uploaded_count += len(batch_data)
                print(f"✅ Uploaded batch {i//batch_size + 1}: {len(batch_data)} quotes (Total: {uploaded_count})")
                
            except Exception as e:
                print(f"❌ Batch upload failed: {e}")
                print(f"Error details: {str(e)}")
                # Try individual uploads for this batch
                for idx, item in enumerate(batch_data):
                    try:
                        result = supabase.table('teaching_materials').insert(item).execute()
                        uploaded_count += 1
                        if idx % 10 == 0:
                            print(f"  ✅ Individual upload {idx + 1}/{len(batch_data)}")
                    except Exception as individual_error:
                        print(f"⚠️  Individual upload failed: {individual_error}")
    
    print(f"\n🎉 Upload complete! {uploaded_count} quotes uploaded to Supabase")
    return uploaded_count > 0

def main():
    print("🏛️  DIRECT SUPABASE SACRED LIBRARY UPLOADER")
    print("=" * 50)
    
    # Load environment
    if not load_environment():
        sys.exit(1)
    
    # Initialize Supabase client
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        print(f"🔗 Connecting to: {supabase_url}")
        
        # Simple client initialization
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client initialized")
        
    except Exception as e:
        print(f"❌ Failed to initialize Supabase client: {e}")
        sys.exit(1)
    
    # Test connection
    if not test_connection(supabase):
        print("❌ Connection test failed")
        sys.exit(1)
    
    # Upload quotes to existing table
    if upload_quotes_to_existing_table(supabase):
        print("\n🎉 Sacred Library successfully uploaded to Supabase!")
    else:
        print("\n❌ Upload failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
