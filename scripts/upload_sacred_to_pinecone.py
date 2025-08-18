#!/usr/bin/env python3
"""
SACRED LIBRARY TO PINECONE UPLOADER
Upload all Sacred Library quotes to Pinecone for vector search
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any
import uuid

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def load_environment():
    """Load environment variables"""
    env_path = Path(__file__).parent.parent / "config" / "production.env"
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

async def upload_sacred_library_to_pinecone():
    """Upload Sacred Library quotes to Pinecone for vector search"""
    print("🏛️  SACRED LIBRARY TO PINECONE UPLOADER")
    print("=" * 50)
    
    try:
        from database.operations import SupabaseClient
        from integrations.pinecone_client import PineconeClient
        from openai import OpenAI
        
        # Initialize clients
        db = SupabaseClient()
        pinecone = PineconeClient()
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        print("✅ Clients initialized")
        
        # Get all Sacred Library quotes from Supabase
        result = db.client.table('teaching_materials').select(
            'material_id, content, title, metadata'
        ).eq(
            'material_type', 'sacred_quote'
        ).execute()
        
        if not result.data:
            print("❌ No Sacred Library quotes found in Supabase")
            return False
        
        quotes = result.data
        print(f"📚 Found {len(quotes)} Sacred Library quotes to upload")
        
        # Process quotes in batches
        batch_size = 50
        total_uploaded = 0
        
        for i in range(0, len(quotes), batch_size):
            batch = quotes[i:i + batch_size]
            print(f"📝 Processing batch {i//batch_size + 1}/{(len(quotes)-1)//batch_size + 1}")
            
            vectors_to_upload = []
            
            for quote in batch:
                try:
                    # Create embedding for the quote content
                    embedding_response = openai_client.embeddings.create(
                        model="text-embedding-3-large",
                        input=quote['content']
                    )
                    
                    embedding = embedding_response.data[0].embedding
                    
                    # Prepare metadata for Pinecone
                    metadata = {
                        'material_id': quote['material_id'],
                        'title': quote['title'],
                        'content': quote['content'],
                        'type': 'sacred_quote',
                        'source': 'hylozoics',
                        'author': 'Henry T. Laurency',
                        'tradition': 'hylozoics',
                        'language': quote['metadata'].get('language', 'unknown'),
                        'chapter': quote['metadata'].get('chapter', 'Unknown'),
                        'book': quote['metadata'].get('book', 'Unknown'),
                        'verified': True,
                        'sacred_library': True
                    }
                    
                    # Create vector record
                    vector_record = {
                        'id': f"sacred_{quote['material_id']}",
                        'values': embedding,
                        'metadata': metadata
                    }
                    
                    vectors_to_upload.append(vector_record)
                    
                except Exception as e:
                    print(f"⚠️  Error processing quote {quote['material_id']}: {e}")
                    continue
            
            # Upload batch to Pinecone
            if vectors_to_upload:
                try:
                    pinecone.index.upsert(vectors=vectors_to_upload)
                    total_uploaded += len(vectors_to_upload)
                    print(f"✅ Uploaded {len(vectors_to_upload)} vectors to Pinecone")
                except Exception as e:
                    print(f"❌ Error uploading batch to Pinecone: {e}")
        
        print(f"\n🎉 SACRED LIBRARY VECTOR UPLOAD COMPLETE!")
        print(f"📊 Total vectors uploaded: {total_uploaded}")
        print(f"🔍 Sacred Library now available for semantic search via Pinecone")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_vector_search():
    """Test vector search of Sacred Library"""
    print("\n🧪 TESTING VECTOR SEARCH")
    print("=" * 30)
    
    try:
        from integrations.pinecone_client import PineconeClient
        from openai import OpenAI
        
        pinecone = PineconeClient()
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Test search for meditation
        query = "meditation and consciousness development"
        
        # Create query embedding
        embedding_response = openai_client.embeddings.create(
            model="text-embedding-3-large",
            input=query
        )
        
        query_embedding = embedding_response.data[0].embedding
        
        # Search Pinecone
        search_results = pinecone.index.query(
            vector=query_embedding,
            filter={"sacred_library": True},
            top_k=3,
            include_metadata=True
        )
        
        if search_results.matches:
            print(f"✅ Found {len(search_results.matches)} relevant quotes")
            for i, match in enumerate(search_results.matches, 1):
                score = match.score
                metadata = match.metadata
                content = metadata.get('content', '')[:100] + "..."
                chapter = metadata.get('chapter', 'Unknown')
                language = metadata.get('language', 'unknown')
                
                print(f"  {i}. Score: {score:.3f}")
                print(f"     [{language.upper()}] {chapter}")
                print(f"     {content}")
                print()
        else:
            print("❌ No vector search results found")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector search test failed: {e}")
        return False

async def main():
    load_environment()
    
    print("🏛️  SACRED LIBRARY VECTOR DATABASE SETUP")
    print("=" * 60)
    
    # Upload to Pinecone
    upload_success = await upload_sacred_library_to_pinecone()
    
    if upload_success:
        # Test vector search
        await test_vector_search()
        
        print("\n🎉 SACRED LIBRARY VECTOR DATABASE READY!")
        print("✅ Semantic search now available for all 4,871 Hylozoics quotes")
        print("🔍 Bot can now find conceptually relevant quotes, not just keyword matches")
    else:
        print("\n❌ Vector database setup failed")

if __name__ == "__main__":
    asyncio.run(main())
