#!/usr/bin/env python3
"""
FINAL SACRED LIBRARY UPLOADER
Upload to existing teaching_materials table with correct structure
"""

import os
import json
import sys
import hashlib
from pathlib import Path
from datetime import datetime

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

def generate_content_hash(content: str) -> str:
    """Generate SHA-256 hash for content"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def upload_sacred_library():
    """Upload all Sacred Library quotes to Supabase teaching_materials table"""
    try:
        from database.operations import SupabaseClient
        
        db = SupabaseClient()
        print("✅ Supabase connected")
        
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
        batch_size = 20  # Small batches
        
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
                    
                    # Prepare data for teaching_materials table structure
                    content = quote_data['text']
                    
                    upload_data = {
                        'title': f"Hylozoics: {quote_data['chapter']} - Chunk {quote_data['metadata']['chunk_number']}",
                        'content': content,
                        'material_type': 'sacred_quote',
                        'source_type': 'hylozoics_pdf',
                        'metadata': {
                            'book': quote_data['source_book'],
                            'chapter': quote_data['chapter'],
                            'language': quote_data['language'],
                            'author': quote_data['author'],
                            'tradition': quote_data['tradition'],
                            'chunk_number': quote_data['metadata']['chunk_number'],
                            'file_path': quote_data['metadata']['file_path'],
                            'extraction_date': quote_data['metadata']['extraction_date'],
                            'verified': quote_data.get('verified', True),
                            'sacred_library': True,
                            'verbatim_quote': True,
                            'library_type': 'hylozoics'
                        },
                        'content_hash': generate_content_hash(content),
                        'status': 'active',
                        'content_visibility': 'public'
                    }
                    
                    batch_data.append(upload_data)
                    
                except Exception as e:
                    print(f"⚠️  Error processing {quote_file.name}: {e}")
                    continue
            
            # Upload batch to Supabase
            if batch_data:
                try:
                    result = db.client.table('teaching_materials').insert(batch_data).execute()
                    uploaded_count += len(batch_data)
                    print(f"✅ Uploaded batch {i//batch_size + 1}: {len(batch_data)} quotes (Total: {uploaded_count})")
                    
                except Exception as e:
                    print(f"❌ Batch upload failed: {e}")
                    
                    # Try individual uploads as fallback
                    print("🔄 Attempting individual uploads...")
                    for idx, item in enumerate(batch_data):
                        try:
                            result = db.client.table('teaching_materials').insert(item).execute()
                            uploaded_count += 1
                            if idx % 5 == 0:
                                print(f"  ✅ Individual upload {idx + 1}/{len(batch_data)}")
                        except Exception as individual_error:
                            print(f"⚠️  Individual upload failed for item {idx}: {individual_error}")
        
        print(f"\n🎉 Upload complete! {uploaded_count} quotes uploaded to Supabase")
        print(f"🏛️  Sacred Library is now live in your Supabase database!")
        return uploaded_count > 0
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False

def main():
    print("🏛️  FINAL SACRED LIBRARY UPLOADER")
    print("=" * 50)
    
    load_environment()
    
    if upload_sacred_library():
        print("\n🎉 SUCCESS! Sacred Library uploaded to Supabase!")
        print("🔍 Your Telegram bot can now access Sacred Library quotes!")
    else:
        print("\n❌ Upload failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
