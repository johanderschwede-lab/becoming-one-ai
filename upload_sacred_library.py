#!/usr/bin/env python3
"""
Upload Sacred Library to Supabase
=================================
Upload the 4,871 Hylozoics quotes from local JSON files to Supabase teaching_materials table
"""

import json
import os
import sys
from pathlib import Path
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def upload_sacred_library():
    """Upload all Sacred Library quotes to Supabase"""
    
    # Initialize Supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Missing SUPABASE_URL or SUPABASE_ANON_KEY environment variables")
        return False
    
    supabase = create_client(supabase_url, supabase_key)
    
    # Path to sacred library files
    sacred_dir = Path("sacred_library_files")
    quotes_dir = sacred_dir / "quotes"
    
    if not quotes_dir.exists():
        print(f"❌ Sacred library directory not found: {quotes_dir}")
        return False
    
    print("🏛️ Starting Sacred Library Upload...")
    print(f"📁 Source: {quotes_dir}")
    print(f"🎯 Target: Supabase teaching_materials table")
    
    # Get all quote files
    quote_files = list(quotes_dir.glob("*.json"))
    total_files = len(quote_files)
    
    print(f"📊 Found {total_files} quote files to upload")
    
    uploaded_count = 0
    error_count = 0
    batch_size = 100
    batch = []
    
    for i, quote_file in enumerate(quote_files):
        try:
            # Load quote data
            with open(quote_file, 'r', encoding='utf-8') as f:
                quote_data = json.load(f)
            
            # Prepare for Supabase upload
            upload_record = {
                'title': f"Hylozoics Quote {quote_data['quote_id']}",
                'content': quote_data['text'],
                'material_type': 'sacred_quote',
                'metadata': {
                    'quote_id': quote_data['quote_id'],
                    'source_book': quote_data['source_book'],
                    'chapter': quote_data['chapter'],
                    'language': quote_data['language'],
                    'author': quote_data['author'],
                    'tradition': quote_data['tradition'],
                    'verified': quote_data['verified'],
                    'file_path': quote_data['metadata']['file_path'],
                    'chunk_number': quote_data['metadata']['chunk_number'],
                    'extraction_date': quote_data['metadata']['extraction_date']
                }
            }
            
            batch.append(upload_record)
            
            # Upload batch when full or at end
            if len(batch) >= batch_size or i == total_files - 1:
                try:
                    result = supabase.table('teaching_materials').insert(batch).execute()
                    uploaded_count += len(batch)
                    print(f"✅ Uploaded batch: {uploaded_count}/{total_files} quotes")
                    batch = []  # Clear batch
                except Exception as e:
                    print(f"❌ Batch upload error: {e}")
                    error_count += len(batch)
                    batch = []
            
        except Exception as e:
            print(f"❌ Error processing {quote_file}: {e}")
            error_count += 1
        
        # Progress indicator
        if (i + 1) % 500 == 0:
            print(f"📈 Progress: {i + 1}/{total_files} files processed")
    
    print("\n🎉 Sacred Library Upload Complete!")
    print(f"✅ Successfully uploaded: {uploaded_count} quotes")
    print(f"❌ Errors: {error_count}")
    print(f"📊 Success rate: {(uploaded_count/(uploaded_count + error_count))*100:.1f}%")
    
    return uploaded_count > 0

def test_sacred_library_search():
    """Test that the uploaded quotes can be searched"""
    print("\n🔍 Testing Sacred Library Search...")
    
    # Initialize Supabase
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_ANON_KEY"))
    
    # Test search
    test_queries = ["consciousness", "evolution", "freedom", "knowledge"]
    
    for query in test_queries:
        try:
            result = supabase.table('teaching_materials').select(
                'title, content, metadata'
            ).eq(
                'material_type', 'sacred_quote'
            ).ilike(
                'content', f'%{query}%'
            ).limit(2).execute()
            
            print(f"\n🔍 Query: '{query}'")
            if result.data:
                print(f"✅ Found {len(result.data)} results")
                for quote in result.data:
                    print(f"📖 {quote['metadata']['chapter']} ({quote['metadata']['language']})")
                    print(f"💬 {quote['content'][:100]}...")
            else:
                print("❌ No results found")
                
        except Exception as e:
            print(f"❌ Search error for '{query}': {e}")

if __name__ == "__main__":
    print("🏛️ Sacred Library Upload Tool")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_sacred_library_search()
    else:
        success = upload_sacred_library()
        if success:
            print("\n🧪 Running test searches...")
            test_sacred_library_search()
        else:
            print("\n❌ Upload failed. Please check errors above.")
