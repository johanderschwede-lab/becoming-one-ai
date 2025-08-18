#!/usr/bin/env python3
"""
Sacred Library Builder
=====================

Complete pipeline to process the ultimate Hylozoics collection into
a dual-mode Sacred Library (Relational + Vector databases)
"""

import os
import json
import PyPDF2
import fitz  # PyMuPDF - better PDF text extraction
from pathlib import Path
import openai
import pinecone
from supabase import create_client, Client
import uuid
from datetime import datetime
import time
import re
from typing import List, Dict, Optional
import hashlib

class SacredLibraryBuilder:
    def __init__(self):
        # Initialize APIs
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.supabase: Client = create_client(
            os.getenv('SUPABASE_URL'),
            os.getenv('SUPABASE_ANON_KEY')
        )
        
        # Initialize Pinecone
        pinecone.init(
            api_key=os.getenv('PINECONE_API_KEY'),
            environment=os.getenv('PINECONE_ENV')
        )
        self.pinecone_index = pinecone.Index('hylozoics-sacred-library')
        
        # Configuration
        self.embedding_model = "text-embedding-3-large"
        self.chunk_size = 1000  # Characters per chunk
        self.overlap_size = 200  # Overlap between chunks
        
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
        
        # Book series mapping for better organization
        self.series_map = {
            'Knowledge_of_Reality': 'The Knowledge of Reality',
            'Philosophers_Stone': "The Philosopher's Stone",
            'Way_of_Man': 'The Way of Man',
            'Knowledge_of_Life_One': 'Knowledge of Life One',
            'Knowledge_of_Life_Two': 'Knowledge of Life Two',
            'Knowledge_of_Life_Three': 'Knowledge of Life Three',
            'Knowledge_of_Life_Four': 'Knowledge of Life Four',
            'Knowledge_of_Life_Five': 'Knowledge of Life Five',
            'Explanation': 'The Explanation'
        }
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF using PyMuPDF for better quality"""
        try:
            print(f"    📄 Extracting text from: {pdf_path.name}")
            
            # Try PyMuPDF first (better quality)
            try:
                doc = fitz.open(pdf_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                
                if len(text.strip()) > 100:  # Good extraction
                    return text
            except Exception as e:
                print(f"      ⚠️  PyMuPDF failed, trying PyPDF2: {e}")
            
            # Fallback to PyPDF2
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                return text
                
        except Exception as e:
            print(f"      ❌ PDF extraction failed: {e}")
            self.stats['errors'].append(f"PDF extraction failed: {pdf_path} - {e}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers
        text = re.sub(r'\n\d+\n', '\n', text)
        text = re.sub(r'Page \d+', '', text)
        
        # Fix common PDF extraction issues
        text = text.replace('ﬁ', 'fi').replace('ﬂ', 'fl')
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text.strip()
    
    def create_text_chunks(self, text: str, metadata: Dict) -> List[Dict]:
        """Split text into chunks for processing"""
        chunks = []
        text_length = len(text)
        
        start = 0
        chunk_num = 1
        
        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            
            # Try to break at sentence boundary
            if end < text_length:
                sentence_break = text.rfind('.', start, end)
                if sentence_break > start + self.chunk_size // 2:
                    end = sentence_break + 1
            
            chunk_text = text[start:end].strip()
            
            if len(chunk_text) > 50:  # Only meaningful chunks
                chunk_id = f"{metadata['file_id']}_chunk_{chunk_num:03d}"
                
                chunks.append({
                    'chunk_id': chunk_id,
                    'text': chunk_text,
                    'metadata': {
                        **metadata,
                        'chunk_number': chunk_num,
                        'total_chunks': 0,  # Will update later
                        'start_char': start,
                        'end_char': end
                    }
                })
                
                chunk_num += 1
            
            start = end - self.overlap_size if end < text_length else end
        
        # Update total chunks count
        for chunk in chunks:
            chunk['metadata']['total_chunks'] = len(chunks)
        
        return chunks
    
    def create_embeddings(self, chunks: List[Dict]) -> List[Dict]:
        """Create embeddings for text chunks"""
        print(f"    🧠 Creating embeddings for {len(chunks)} chunks...")
        
        embedded_chunks = []
        batch_size = 100  # Process in batches to avoid rate limits
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            texts = [chunk['text'] for chunk in batch]
            
            try:
                # Create embeddings
                response = self.openai_client.embeddings.create(
                    model=self.embedding_model,
                    input=texts
                )
                
                # Add embeddings to chunks
                for j, chunk in enumerate(batch):
                    chunk['embedding'] = response.data[j].embedding
                    embedded_chunks.append(chunk)
                
                self.stats['embeddings_created'] += len(batch)
                print(f"      ✅ Created {len(batch)} embeddings")
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"      ❌ Embedding creation failed: {e}")
                self.stats['errors'].append(f"Embedding failed for batch {i}: {e}")
                continue
        
        return embedded_chunks
    
    def upload_to_supabase(self, chunks: List[Dict]) -> int:
        """Upload chunks to Supabase Sacred Library"""
        print(f"    🏛️  Uploading {len(chunks)} quotes to Sacred Library...")
        
        uploaded_count = 0
        
        for chunk in chunks:
            try:
                # Create sacred library entry
                quote_data = {
                    'quote_id': chunk['chunk_id'],
                    'text': chunk['text'],
                    'source_book': chunk['metadata']['book_series'],
                    'chapter': chunk['metadata']['filename'].replace('.pdf', ''),
                    'language': chunk['metadata']['language_code'],
                    'author': 'Henry T. Laurency',
                    'tradition': 'Hylozoics',
                    'verified': True,
                    'hylozoics_terms': [],  # TODO: Extract terms
                    'metadata': {
                        'file_path': chunk['metadata']['file_path'],
                        'chunk_number': chunk['metadata']['chunk_number'],
                        'total_chunks': chunk['metadata']['total_chunks'],
                        'extraction_date': datetime.now().isoformat()
                    }
                }
                
                # Upload to Supabase
                result = self.supabase.table('hylozoics_sacred_quotes').insert(quote_data).execute()
                
                if result.data:
                    uploaded_count += 1
                
            except Exception as e:
                print(f"      ❌ Supabase upload failed: {e}")
                self.stats['errors'].append(f"Supabase upload failed: {chunk['chunk_id']} - {e}")
                continue
        
        self.stats['quotes_uploaded'] += uploaded_count
        print(f"      ✅ Uploaded {uploaded_count} quotes to Sacred Library")
        return uploaded_count
    
    def upload_to_pinecone(self, chunks: List[Dict]) -> int:
        """Upload embeddings to Pinecone vector database"""
        print(f"    📊 Uploading {len(chunks)} vectors to Pinecone...")
        
        vectors = []
        for chunk in chunks:
            if 'embedding' in chunk:
                vectors.append({
                    'id': chunk['chunk_id'],
                    'values': chunk['embedding'],
                    'metadata': {
                        'text': chunk['text'][:1000],  # Truncate for metadata limits
                        'book': chunk['metadata']['book_series'],
                        'language': chunk['metadata']['language_code'],
                        'filename': chunk['metadata']['filename'],
                        'chunk_num': chunk['metadata']['chunk_number']
                    }
                })
        
        try:
            # Upload in batches
            batch_size = 100
            uploaded_count = 0
            
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.pinecone_index.upsert(vectors=batch)
                uploaded_count += len(batch)
                print(f"      ✅ Uploaded batch {i//batch_size + 1}")
                time.sleep(0.5)  # Rate limiting
            
            print(f"      🎉 Successfully uploaded {uploaded_count} vectors")
            return uploaded_count
            
        except Exception as e:
            print(f"      ❌ Pinecone upload failed: {e}")
            self.stats['errors'].append(f"Pinecone upload failed: {e}")
            return 0
    
    def process_pdf_file(self, pdf_path: Path, language: str, book_series: str) -> bool:
        """Process a single PDF file through the complete pipeline"""
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
                'book_series': book_series,
                'processed_date': datetime.now().isoformat()
            }
            
            # Extract text
            text = self.extract_text_from_pdf(pdf_path)
            if not text or len(text) < 100:
                print(f"    ❌ No meaningful text extracted")
                return False
            
            # Clean text
            text = self.clean_text(text)
            
            # Create chunks
            chunks = self.create_text_chunks(text, metadata)
            if not chunks:
                print(f"    ❌ No chunks created")
                return False
            
            print(f"    📝 Created {len(chunks)} text chunks")
            
            # Create embeddings
            embedded_chunks = self.create_embeddings(chunks)
            
            # Upload to both databases
            supabase_count = self.upload_to_supabase(embedded_chunks)
            pinecone_count = self.upload_to_pinecone(embedded_chunks)
            
            self.stats['pdfs_processed'] += 1
            self.stats['chunks_created'] += len(chunks)
            
            print(f"    ✅ Completed: {supabase_count} quotes, {pinecone_count} vectors")
            return True
            
        except Exception as e:
            print(f"    ❌ Processing failed: {e}")
            self.stats['errors'].append(f"Processing failed: {pdf_path} - {e}")
            return False
    
    def process_language_collection(self, language_dir: Path) -> Dict:
        """Process all PDFs in a language directory"""
        language = language_dir.name
        print(f"\n🌐 Processing {language}")
        print("=" * 50)
        
        language_stats = {
            'language': language,
            'pdfs_found': 0,
            'pdfs_processed': 0,
            'total_chunks': 0,
            'books_by_series': {}
        }
        
        # Find all PDF files
        pdf_files = list(language_dir.rglob("*.pdf"))
        language_stats['pdfs_found'] = len(pdf_files)
        
        print(f"📁 Found {len(pdf_files)} PDF files")
        
        # Process each PDF
        for pdf_path in pdf_files:
            # Determine book series from directory structure
            book_series = "Unknown Series"
            for series_key, series_name in self.series_map.items():
                if series_key.lower() in str(pdf_path).lower():
                    book_series = series_name
                    break
            
            # Track by series
            if book_series not in language_stats['books_by_series']:
                language_stats['books_by_series'][book_series] = 0
            
            # Process the PDF
            if self.process_pdf_file(pdf_path, language, book_series):
                language_stats['pdfs_processed'] += 1
                language_stats['books_by_series'][book_series] += 1
        
        print(f"✅ {language} complete: {language_stats['pdfs_processed']}/{language_stats['pdfs_found']} PDFs processed")
        return language_stats
    
    def run_complete_build(self, collection_dir: Path = Path("laurency_ultimate")):
        """Run the complete Sacred Library build process"""
        print("🏛️  SACRED LIBRARY BUILDER")
        print("=" * 60)
        print("🎯 Building dual-mode Sacred Library from complete Hylozoics collection")
        print(f"📁 Source: {collection_dir}")
        
        start_time = datetime.now()
        
        # Find all language directories
        language_dirs = [d for d in collection_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
        
        print(f"\n🌍 Found {len(language_dirs)} language collections:")
        for lang_dir in language_dirs:
            pdf_count = len(list(lang_dir.rglob("*.pdf")))
            print(f"  📚 {lang_dir.name}: {pdf_count} PDFs")
        
        # Process each language
        all_language_stats = []
        
        for lang_dir in language_dirs:
            try:
                lang_stats = self.process_language_collection(lang_dir)
                all_language_stats.append(lang_stats)
            except Exception as e:
                print(f"❌ Failed to process {lang_dir.name}: {e}")
                self.stats['errors'].append(f"Language processing failed: {lang_dir.name} - {e}")
        
        # Final summary
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n🎉 SACRED LIBRARY BUILD COMPLETE!")
        print("=" * 60)
        print(f"⏱️  Total time: {duration}")
        print(f"🌐 Languages processed: {len(all_language_stats)}")
        print(f"📚 PDFs processed: {self.stats['pdfs_processed']}")
        print(f"📝 Text chunks created: {self.stats['chunks_created']}")
        print(f"🧠 Embeddings created: {self.stats['embeddings_created']}")
        print(f"🏛️  Sacred quotes uploaded: {self.stats['quotes_uploaded']}")
        
        if self.stats['errors']:
            print(f"⚠️  Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:5]:  # Show first 5 errors
                print(f"   • {error}")
        
        # Save detailed report
        report = {
            'build_date': end_time.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'overall_stats': self.stats,
            'language_stats': all_language_stats
        }
        
        report_file = Path("SACRED_LIBRARY_BUILD_REPORT.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📋 Detailed report saved: {report_file}")
        print(f"🏛️  Your Sacred Library is ready for queries!")

if __name__ == "__main__":
    # Check for required environment variables
    required_vars = ['OPENAI_API_KEY', 'SUPABASE_URL', 'SUPABASE_ANON_KEY', 'PINECONE_API_KEY', 'PINECONE_ENV']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these in your environment before running.")
        exit(1)
    
    # Build Sacred Library
    builder = SacredLibraryBuilder()
    builder.run_complete_build()
