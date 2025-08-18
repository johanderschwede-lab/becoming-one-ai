#!/usr/bin/env python3
"""
File-Based Sacred Library Builder
================================

Create a file-based Sacred Library that works immediately
Later can be migrated to Supabase when tables are ready
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

class FileSacredLibrary:
    def __init__(self, output_dir: str = "sacred_library_files"):
        # Initialize OpenAI for future embedding use
        self.openai_client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Create output directory
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / "quotes").mkdir(exist_ok=True)
        (self.output_dir / "metadata").mkdir(exist_ok=True)
        (self.output_dir / "by_language").mkdir(exist_ok=True)
        (self.output_dir / "by_book").mkdir(exist_ok=True)
        
        # Configuration
        self.chunk_size = 800
        
        # Processing stats
        self.stats = {
            'pdfs_processed': 0,
            'chunks_created': 0,
            'quotes_saved': 0,
            'languages_found': set(),
            'books_found': set(),
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
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF using PyMuPDF"""
        try:
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
                    'quote_id': chunk_id,
                    'text': current_chunk.strip(),
                    'source_book': metadata['book_series'],
                    'chapter': metadata['filename'].replace('.pdf', ''),
                    'language': metadata['language_code'],
                    'author': 'Henry T. Laurency',
                    'tradition': 'Hylozoics',
                    'verified': True,
                    'metadata': {
                        'file_path': str(metadata['file_path']),
                        'chunk_number': chunk_num,
                        'extraction_date': datetime.now().isoformat()
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
                'quote_id': chunk_id,
                'text': current_chunk.strip(),
                'source_book': metadata['book_series'],
                'chapter': metadata['filename'].replace('.pdf', ''),
                'language': metadata['language_code'],
                'author': 'Henry T. Laurency',
                'tradition': 'Hylozoics',
                'verified': True,
                'metadata': {
                    'file_path': str(metadata['file_path']),
                    'chunk_number': chunk_num,
                    'extraction_date': datetime.now().isoformat()
                }
            })
        
        return chunks
    
    def save_quotes_to_files(self, chunks: List[Dict]) -> int:
        """Save quotes to organized file system"""
        saved_count = 0
        
        for chunk in chunks:
            try:
                # Save individual quote
                quote_file = self.output_dir / "quotes" / f"{chunk['quote_id']}.json"
                with open(quote_file, 'w', encoding='utf-8') as f:
                    json.dump(chunk, f, indent=2, ensure_ascii=False)
                
                # Add to language index
                lang_dir = self.output_dir / "by_language" / chunk['language']
                lang_dir.mkdir(exist_ok=True)
                lang_index = lang_dir / "quotes.jsonl"
                with open(lang_index, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
                
                # Add to book index
                book_name = chunk['source_book'].replace(' ', '_').replace('/', '_')
                book_dir = self.output_dir / "by_book" / book_name
                book_dir.mkdir(exist_ok=True)
                book_index = book_dir / "quotes.jsonl"
                with open(book_index, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(chunk, ensure_ascii=False) + '\n')
                
                # Track stats
                self.stats['languages_found'].add(chunk['language'])
                self.stats['books_found'].add(chunk['source_book'])
                
                saved_count += 1
                
            except Exception as e:
                self.stats['errors'].append(f"Save failed: {chunk['quote_id']} - {e}")
        
        self.stats['quotes_saved'] += saved_count
        return saved_count
    
    def process_pdf_file(self, pdf_path: Path, language: str, book_series: str) -> bool:
        """Process a single PDF file"""
        print(f"  📚 Processing: {pdf_path.name}")
        
        try:
            # Create file metadata
            file_id = hashlib.md5(str(pdf_path).encode()).hexdigest()[:12]
            metadata = {
                'file_id': file_id,
                'file_path': pdf_path,
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
            
            # Save to files
            saved_count = self.save_quotes_to_files(chunks)
            
            self.stats['pdfs_processed'] += 1
            self.stats['chunks_created'] += len(chunks)
            
            print(f"    ✅ Saved {saved_count} quotes to Sacred Library")
            return True
            
        except Exception as e:
            print(f"    ❌ Processing failed: {e}")
            self.stats['errors'].append(f"Processing failed: {pdf_path} - {e}")
            return False
    
    def create_master_index(self):
        """Create master index of all quotes"""
        print("📋 Creating master index...")
        
        master_index = {
            'created_at': datetime.now().isoformat(),
            'total_quotes': self.stats['quotes_saved'],
            'total_languages': len(self.stats['languages_found']),
            'total_books': len(self.stats['books_found']),
            'languages': list(self.stats['languages_found']),
            'books': list(self.stats['books_found']),
            'stats': dict(self.stats)
        }
        
        # Convert set to list for JSON serialization
        master_index['stats']['languages_found'] = list(self.stats['languages_found'])
        master_index['stats']['books_found'] = list(self.stats['books_found'])
        
        # Save master index
        index_file = self.output_dir / "MASTER_INDEX.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(master_index, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Master index saved: {index_file}")
    
    def create_search_interface(self):
        """Create simple search interface"""
        search_script = '''#!/usr/bin/env python3
"""
Sacred Library Search Interface
==============================
"""

import json
import re
from pathlib import Path

def search_quotes(query, language=None, book=None, limit=10):
    """Search quotes in the Sacred Library"""
    sacred_dir = Path("sacred_library_files")
    results = []
    
    # Search through all quote files
    quotes_dir = sacred_dir / "quotes"
    for quote_file in quotes_dir.glob("*.json"):
        try:
            with open(quote_file, 'r', encoding='utf-8') as f:
                quote = json.load(f)
            
            # Filter by language if specified
            if language and quote['language'] != language:
                continue
            
            # Filter by book if specified  
            if book and book.lower() not in quote['source_book'].lower():
                continue
            
            # Search in text
            if query.lower() in quote['text'].lower():
                results.append({
                    'quote_id': quote['quote_id'],
                    'text': quote['text'][:200] + "..." if len(quote['text']) > 200 else quote['text'],
                    'source': f"{quote['source_book']} - {quote['chapter']}",
                    'language': quote['language']
                })
                
                if len(results) >= limit:
                    break
                    
        except Exception as e:
            continue
    
    return results

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python search_sacred_library.py <query> [language] [book]")
        print("Example: python search_sacred_library.py meditation en")
        sys.exit(1)
    
    query = sys.argv[1]
    language = sys.argv[2] if len(sys.argv) > 2 else None
    book = sys.argv[3] if len(sys.argv) > 3 else None
    
    results = search_quotes(query, language, book)
    
    print(f"🔍 Found {len(results)} results for '{query}'")
    print("=" * 50)
    
    for result in results:
        print(f"📖 {result['source']} ({result['language']})")
        print(f"💬 {result['text']}")
        print()
'''
        
        search_file = self.output_dir / "search_sacred_library.py"
        with open(search_file, 'w', encoding='utf-8') as f:
            f.write(search_script)
        
        # Make it executable
        os.chmod(search_file, 0o755)
        
        print(f"🔍 Search interface created: {search_file}")
    
    def run_build(self, collection_dir: Path = Path("laurency_ultimate"), max_files: int = 50):
        """Build file-based Sacred Library"""
        print("🏛️  FILE-BASED SACRED LIBRARY BUILDER")
        print("=" * 60)
        print(f"🎯 Building Sacred Library from {max_files} sample files")
        
        start_time = datetime.now()
        
        # Find all PDF files
        all_pdfs = list(collection_dir.rglob("*.pdf"))
        print(f"📁 Found {len(all_pdfs)} total PDF files")
        
        # Take a sample
        sample_pdfs = all_pdfs[:max_files]
        print(f"📋 Processing {len(sample_pdfs)} files")
        
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
            elif "Way" in str(pdf_path):
                book_series = "The Way of Man"
            
            # Process the file
            if self.process_pdf_file(pdf_path, language, book_series):
                processed_count += 1
            
            # Small delay
            time.sleep(0.1)
        
        # Create indices and search interface
        self.create_master_index()
        self.create_search_interface()
        
        # Final summary
        end_time = datetime.now()
        duration = end_time - start_time
        
        print(f"\n🎉 FILE-BASED SACRED LIBRARY COMPLETE!")
        print("=" * 50)
        print(f"⏱️  Total time: {duration}")
        print(f"📚 PDFs processed: {self.stats['pdfs_processed']}")
        print(f"📝 Text chunks created: {self.stats['chunks_created']}")
        print(f"🏛️  Sacred quotes saved: {self.stats['quotes_saved']}")
        print(f"🌐 Languages: {len(self.stats['languages_found'])}")
        print(f"📖 Books: {len(self.stats['books_found'])}")
        
        if self.stats['errors']:
            print(f"⚠️  Errors: {len(self.stats['errors'])}")
        
        print(f"\n📁 Sacred Library location: {self.output_dir}")
        print(f"🔍 Search with: python {self.output_dir}/search_sacred_library.py <query>")
        print(f"🏛️  Your Sacred Library is ready for queries!")
        
        return processed_count > 0

if __name__ == "__main__":
    builder = FileSacredLibrary()
    success = builder.run_build(max_files=50)
    
    if success:
        print("\n🎉 Sacred Library successfully built!")
        print("Example searches:")
        print("  python sacred_library_files/search_sacred_library.py meditation")
        print("  python sacred_library_files/search_sacred_library.py consciousness en")
        print("  python sacred_library_files/search_sacred_library.py hylozoics")
    else:
        print("\n❌ Sacred Library build failed")
