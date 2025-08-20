#!/usr/bin/env python3
"""
SUPABASE SACRED LIBRARY UPLOADER
Direct upload using proper Supabase client
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

def create_tables(supabase: Client):
    """Create Sacred Library tables using Supabase client"""
    print("🏛️  Creating Sacred Library tables...")
    
    # Create sacred_library_quotes table
    create_quotes_table = """
    CREATE TABLE IF NOT EXISTS sacred_library_quotes (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        quote_text TEXT NOT NULL,
        source_book VARCHAR(255) NOT NULL,
        source_language VARCHAR(10) NOT NULL,
        source_file VARCHAR(255) NOT NULL,
        chunk_index INTEGER NOT NULL,
        page_number INTEGER,
        paragraph_number INTEGER,
        confidence_score DECIMAL(3,2) DEFAULT 1.0,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    
    # Create indexes
    create_indexes = """
    CREATE INDEX IF NOT EXISTS idx_sacred_quotes_book ON sacred_library_quotes(source_book);
    CREATE INDEX IF NOT EXISTS idx_sacred_quotes_language ON sacred_library_quotes(source_language);
    CREATE INDEX IF NOT EXISTS idx_sacred_quotes_text ON sacred_library_quotes USING gin(to_tsvector('english', quote_text));
    """
    
    try:
        # Execute table creation
        result = supabase.rpc('exec_sql', {'sql': create_quotes_table}).execute()
        print("✅ Sacred Library quotes table created")
        
        # Execute index creation
        result = supabase.rpc('exec_sql', {'sql': create_indexes}).execute()
        print("✅ Indexes created")
        
        return True
    except Exception as e:
        print(f"❌ Table creation failed: {e}")
        return False

def upload_quotes(supabase: Client):
    """Upload all quotes from file-based Sacred Library to Supabase"""
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
    batch_size = 100
    
    # Process in batches
    for i in range(0, len(quote_files), batch_size):
        batch_files = quote_files[i:i + batch_size]
        batch_data = []
        
        for quote_file in batch_files:
            try:
                with open(quote_file, 'r', encoding='utf-8') as f:
                    quote_data = json.load(f)
                
                # Prepare data for Supabase
                upload_data = {
                    'quote_text': quote_data['text'],
                    'source_book': quote_data['metadata']['book'],
                    'source_language': quote_data['metadata']['language'],
                    'source_file': quote_data['metadata']['source_file'],
                    'chunk_index': quote_data['metadata']['chunk_index'],
                    'page_number': quote_data['metadata'].get('page_number'),
                    'paragraph_number': quote_data['metadata'].get('paragraph_number'),
                    'confidence_score': quote_data['metadata'].get('confidence_score', 1.0)
                }
                
                batch_data.append(upload_data)
                
            except Exception as e:
                print(f"⚠️  Error processing {quote_file.name}: {e}")
                continue
        
        # Upload batch to Supabase
        if batch_data:
            try:
                result = supabase.table('sacred_library_quotes').insert(batch_data).execute()
                uploaded_count += len(batch_data)
                print(f"✅ Uploaded batch {i//batch_size + 1}: {len(batch_data)} quotes (Total: {uploaded_count})")
                
            except Exception as e:
                print(f"❌ Batch upload failed: {e}")
                # Try individual uploads for this batch
                for item in batch_data:
                    try:
                        result = supabase.table('sacred_library_quotes').insert(item).execute()
                        uploaded_count += 1
                    except Exception as individual_error:
                        print(f"⚠️  Individual upload failed: {individual_error}")
    
    print(f"\n🎉 Upload complete! {uploaded_count} quotes uploaded to Supabase")
    return uploaded_count > 0

def main():
    print("🏛️  SUPABASE SACRED LIBRARY UPLOADER")
    print("=" * 50)
    
    # Load environment
    if not load_environment():
        sys.exit(1)
    
    # Initialize Supabase client
    try:
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        # Simple client initialization without additional options
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Supabase client initialized")
        
    except Exception as e:
        print(f"❌ Failed to initialize Supabase client: {e}")
        sys.exit(1)
    
    # Create tables
    if not create_tables(supabase):
        print("❌ Failed to create tables")
        sys.exit(1)
    
    # Upload quotes
    if upload_quotes(supabase):
        print("\n🎉 Sacred Library successfully uploaded to Supabase!")
    else:
        print("\n❌ Upload failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
