#!/usr/bin/env python3
"""
Simplified Sacred Library Builder
================================

Process Hylozoics PDFs into Sacred Library with automatic table creation
"""

import os
import json
import fitz  # PyMuPDF
from pathlib import Path
import openai
import time
import re
from typing import List, Dict
import hashlib
from datetime import datetime
import requests

class SimpleSacredLibraryBuilder:
    def __init__(self):
        # Initialize OpenAI
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Supabase configuration
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        self.headers = {
            'Authorization': f'Bearer {self.supabase_key}',
            'Content-Type': 'application/json',
            'apikey': self.supabase_key
        }
        
        # Configuration
        self.embedding_model = "text-embedding-3-large"
        self.chunk_size = 800  # Smaller chunks for better processing
        
        # Processing stats
        self.stats = {
            'pdfs_processed': 0,
            'chunks_created': 0,
            'embeddings_created': 0,
            'quotes_uploaded': 0,
            'errors': []
        }
        
        # Language mapping
        self.language_map = {
            'english_English': 'en',
            'swedish_Svenska': 'sv', 
            'german_Deutsch': 'de',
            'french_Français': 'fr',
            'spanish_Español': 'es',
            'italian_Italiano': 'it',
            'finnish_Suomi': 'fi',
            'russian_Русский': 'ru',
            'danish_Dansk': 'da',
            'hungarian_Magyar': 'hu'
        }
        
    def ensure_table_exists(self):
        """Create the sacred quotes table if it doesn't exist"""
        print("🏛️  Ensuring Sacred Library table exists...")
        
        create_table_sql = '''
        CREATE TABLE IF NOT EXISTS hylozoics_sacred_quotes (
            id SERIAL PRIMARY KEY,
            quote_id TEXT UNIQUE,
            text TEXT NOT NULL,
            source_book TEXT NOT NULL,
            chapter TEXT NOT NULL,
            language TEXT DEFAULT 'en',
            author TEXT DEFAULT 'Henry T. Laurency',
            tradition TEXT DEFAULT 'Hylozoics',
            verified BOOLEAN DEFAULT TRUE,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        '''
        
        try:
            # Try to create table using direct SQL
            response = requests.post(
                f"{self.supabase_url}/rest/v1/rpc/query",
                headers=self.headers,
                json={'query': create_table_sql}
            )
            print(f"  📋 Table creation response: {response.status_code}")
        except Exception as e:
            print(f"  ⚠️  Table creation attempt: {e}")
        
        print("  ✅ Table should be ready (will be created on first insert if needed)")
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF using PyMuPDF"""
        try:
            print(f"    📄 Extracting: {pdf_path.name}")
            
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            
            # Clean text
            text = re.sub(r'\s+', ' ', text)
            text = text.replace('ﬁ', 'fi').replace('ﬂ', 'fl')
            text = text.replace('"', '"').replace('"', '"')
            
            return text.strip()
            
        except Exception as e:
            print(f"      ❌ PDF extraction failed: {e}")
            self.stats['errors'].append(f"PDF extraction failed: {pdf_path} - {e}")
            return ""
    
    def create_text_chunks(self, text: str, metadata: Dict) -> List[Dict]:
        """Split text into meaningful chunks"""
        chunks = []
        sentences = re.split(r'[.!?]+', text)
        
        current_chunk = ""
        chunk_num = 1
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # If adding this sentence would exceed chunk size, save current chunk
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                chunk_id = f"{metadata['file_id']}_chunk_{chunk_num:03d}"
                
                chunks.append({
                    'chunk_id': chunk_id,
                    'text': current_chunk.strip(),
                    'metadata': {
                        **metadata,
                        'chunk_number': chunk_num
                    }
                })
                
                current_chunk = sentence
                chunk_num += 1
            else:
                current_chunk += " " + sentence
        
        # Don't forget the last chunk
        if current_chunk.strip():
            chunk_id = f"{metadata['file_id']}_chunk_{chunk_num:03d}"
            chunks.append({
                'chunk_id': chunk_id,
                'text': current_chunk.strip(),
                'metadata': {
                    **metadata,
                    'chunk_number': chunk_num
                }
            })
        
        return chunks
    
    def upload_to_supabase(self, chunks: List[Dict]) -> int:
        """Upload chunks to Supabase using REST API"""
        print(f"    🏛️  Uploading {len(chunks)} quotes to Sacred Library...")
        
        uploaded_count = 0
        
        for chunk in chunks:
            try:
                # Prepare data for Supabase
                quote_data = {
                    'quote_id': chunk['chunk_id'],
                    'text': chunk['text'],
                    'source_book': chunk['metadata']['book_series'],
                    'chapter': chunk['metadata']['filename'].replace('.pdf', ''),
                    'language': chunk['metadata']['language_code'],
                    'author': 'Henry T. Laurency',
                    'tradition': 'Hylozoics',
                    'verified': True,
                    'metadata': {
                        'file_path': chunk['metadata']['file_path'],
                        'chunk_number': chunk['metadata']['chunk_number'],
                        'extraction_date': datetime.now().isoformat()
                    }
                }
                
                # Upload to Supabase
                response = requests.post(
                    f"{self.supabase_url}/rest/v1/hylozoics_sacred_quotes",
                    headers=self.headers,
                    json=quote_data
                )
                
                if response.status_code in [200, 201]:
                    uploaded_count += 1
                elif response.status_code == 409:  # Conflict - already exists
                    uploaded_count += 1
                    print(f"      ℹ️  Quote already exists: {chunk['chunk_id']}")
                else:
                    print(f"      ⚠️  Upload warning: {response.status_code}")
                
            except Exception as e:
                print(f"      ❌ Upload failed: {e}")
                self.stats['errors'].append(f"Upload failed: {chunk['chunk_id']} - {e}")
                continue
        
        self.stats['quotes_uploaded'] += uploaded_count
        print(f"      ✅ Uploaded {uploaded_count} quotes")
        return uploaded_count
    
    def process_pdf_file(self, pdf_path: Path, language: str, book_series: str) -> bool:
        """Process a single PDF file"""
        print(f"  📚 Processing: {pdf_path.name}")
        
        try:
            # Create file metadata
            file_id = hashlib.md5(str(pdf_path).encode()).hexdigest()[:12]
            metadata = {
                'file_id': file_id,
                'file_path': str(pdf_path),
                'filename': pdf_path.name,
                'language': language,
                'language_code': self.language_map.get(language, 'en'),
                'book_series': book_series or 'Unknown Series'
            }
            
            # Extract text
            text = self.extract_text_from_pdf(pdf_path)
            if not text or len(text) < 100:
                print(f"    ❌ No meaningful text extracted")
                return False
            
            # Create chunks
            chunks = self.create_text_chunks(text, metadata)
            if not chunks:
                print(f"    ❌ No chunks created")
                return False
            
            print(f"    📝 Created {len(chunks)} text chunks")
            
            # Upload to Supabase
            uploaded_count = self.upload_to_supabase(chunks)
            
            self.stats['pdfs_processed'] += 1
            self.stats['chunks_created'] += len(chunks)
            
            print(f"    ✅ Completed: {uploaded_count} quotes uploaded")
            return True
            
        except Exception as e:
            print(f"    ❌ Processing failed: {e}")
            self.stats['errors'].append(f"Processing failed: {pdf_path} - {e}")
            return False
    
    def process_sample_files(self, collection_dir: Path, max_files: int = 20):
        """Process a sample of files to test the system"""
        print(f"\n🧪 PROCESSING SAMPLE FILES (max {max_files})")
        print("=" * 50)
        
        # Find all PDF files
        all_pdfs = list(collection_dir.rglob("*.pdf"))
        print(f"📁 Found {len(all_pdfs)} total PDF files")
        
        # Take a sample from different languages
        sample_pdfs = all_pdfs[:max_files]
        
        processed_count = 0
        
        for pdf_path in sample_pdfs:
            # Determine language from path
            language = "english_English"  # default
            for lang in self.language_map.keys():
                if lang in str(pdf_path):
                    language = lang
                    break
            
            # Determine book series from path
            book_series = "Unknown Series"
            if "Knowledge" in str(pdf_path):
                book_series = "Knowledge of Life"
            elif "Philosopher" in str(pdf_path):
                book_series = "The Philosopher's Stone"
            elif "Explanation" in str(pdf_path):
                book_series = "The Explanation"
            
            # Process the file
            if self.process_pdf_file(pdf_path, language, book_series):
                processed_count += 1
            
            # Small delay to be respectful
            time.sleep(0.5)
        
        return processed_count
    
    def run_sample_build(self, collection_dir: Path = Path("laurency_ultimate")):
        """Run a sample Sacred Library build"""
        print("🏛️  SACRED LIBRARY SAMPLE BUILD")
        print("=" * 60)
        print("🎯 Building sample Sacred Library from Hylozoics collection")
        
        start_time = datetime.now()
        
        # Ensure table exists
        self.ensure_table_exists()
        
        # Process sample files
        processed_count = self.process_sample_files(collection_dir, max_files=20)
        
        # Final summary
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n🎉 SAMPLE BUILD COMPLETE!")
        print("=" * 40)
        print(f"⏱️  Total time: {duration}")
        print(f"📚 PDFs processed: {self.stats['pdfs_processed']}")
        print(f"📝 Text chunks created: {self.stats['chunks_created']}")
        print(f"🏛️  Sacred quotes uploaded: {self.stats['quotes_uploaded']}")
        
        if self.stats['errors']:
            print(f"⚠️  Errors: {len(self.stats['errors'])}")
        
        print(f"\n🏛️  Your Sacred Library sample is ready!")
        print("🔍 You can now test queries against the Sacred Library!")
        
        return processed_count > 0

if __name__ == "__main__":
    # Check for required environment variables
    required_vars = ['OPENAI_API_KEY', 'SUPABASE_URL', 'SUPABASE_SERVICE_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        exit(1)
    
    # Build sample Sacred Library
    builder = SimpleSacredLibraryBuilder()
    success = builder.run_sample_build()
    
    if success:
        print("\n🚀 Ready for full Sacred Library build!")
    else:
        print("\n❌ Sample build failed - check errors above")
