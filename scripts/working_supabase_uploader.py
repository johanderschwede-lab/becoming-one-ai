#!/usr/bin/env python3
"""
WORKING SUPABASE SACRED LIBRARY UPLOADER
Based on existing working Supabase client pattern
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

class SacredLibraryUploader:
    """Sacred Library uploader using working Supabase pattern"""
    
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        
        # Use the same pattern as your working database operations
        self.client: Client = create_client(url, key)
        print("✅ Supabase client initialized successfully")
    
    def test_connection(self):
        """Test connection by querying existing table"""
        try:
            result = self.client.table('people').select('*').limit(1).execute()
            print("✅ Supabase connection verified")
            return True
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def upload_to_teaching_materials(self):
        """Upload Sacred Library quotes to existing teaching_materials table"""
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
        batch_size = 25  # Small batches to avoid timeouts
        
        # Process in batches
        total_batches = (len(quote_files) + batch_size - 1) // batch_size
        
        for i in range(0, len(quote_files), batch_size):
            batch_files = quote_files[i:i + batch_size]
            batch_data = []
            
            print(f"📦 Processing batch {i//batch_size + 1}/{total_batches}")
            
            for quote_file in batch_files:
                try:
                    with open(quote_file, 'r', encoding='utf-8') as f:
                        quote_data = json.load(f)
                    
                    # Prepare data for teaching_materials table
                    upload_data = {
                        'content': quote_data['text'],
                        'title': f"Hylozoics: {quote_data['metadata']['source_file']} - Chunk {quote_data['metadata']['chunk_index']}",
                        'category': 'hylozoics_sacred',
                        'source_file': quote_data['metadata']['source_file'],
                        'language': quote_data['metadata']['language'],
                        'metadata': {
                            'book': quote_data['metadata']['book'],
                            'chunk_index': quote_data['metadata']['chunk_index'],
                            'confidence_score': quote_data['metadata'].get('confidence_score', 1.0),
                            'sacred_library': True,
                            'verbatim_quote': True,
                            'original_filename': quote_data['metadata']['source_file']
                        }
                    }
                    
                    batch_data.append(upload_data)
                    
                except Exception as e:
                    print(f"⚠️  Error processing {quote_file.name}: {e}")
                    continue
            
            # Upload batch to Supabase
            if batch_data:
                try:
                    result = self.client.table('teaching_materials').insert(batch_data).execute()
                    uploaded_count += len(batch_data)
                    print(f"✅ Uploaded batch {i//batch_size + 1}: {len(batch_data)} quotes (Total: {uploaded_count})")
                    
                except Exception as e:
                    print(f"❌ Batch upload failed: {e}")
                    
                    # Try individual uploads as fallback
                    print("🔄 Attempting individual uploads...")
                    for idx, item in enumerate(batch_data):
                        try:
                            result = self.client.table('teaching_materials').insert(item).execute()
                            uploaded_count += 1
                            if idx % 5 == 0:
                                print(f"  ✅ Individual upload {idx + 1}/{len(batch_data)}")
                        except Exception as individual_error:
                            print(f"⚠️  Individual upload failed for item {idx}: {individual_error}")
        
        print(f"\n🎉 Upload complete! {uploaded_count} quotes uploaded to Supabase")
        return uploaded_count > 0

def main():
    print("🏛️  WORKING SUPABASE SACRED LIBRARY UPLOADER")
    print("=" * 50)
    
    # Load environment
    if not load_environment():
        sys.exit(1)
    
    try:
        # Initialize uploader using working pattern
        uploader = SacredLibraryUploader()
        
        # Test connection
        if not uploader.test_connection():
            print("❌ Connection test failed")
            sys.exit(1)
        
        # Upload quotes
        if uploader.upload_to_teaching_materials():
            print("\n🎉 Sacred Library successfully uploaded to Supabase!")
        else:
            print("\n❌ Upload failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Uploader initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
