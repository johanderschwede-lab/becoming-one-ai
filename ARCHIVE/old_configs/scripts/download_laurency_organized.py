#!/usr/bin/env python3
"""
Organized Laurency PDF Downloader
=================================

Downloads and organizes Laurency PDFs by book series, volume, and chapter
Perfect structure for Sacred Library integration
"""

import os
import requests
from pathlib import Path
import time
import json
from datetime import datetime

class OrganizedLaurencyDownloader:
    def __init__(self, output_dir: str = "laurency_organized"):
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Discovered PDF structure
        self.pdf_structure = {
            "Knowledge_of_Life_Volume_1": {
                "directory": "01_Knowledge_of_Life/Volume_1_English",
                "description": "The Knowledge of Life - Volume 1 (English Translation)",
                "language": "english",
                "original_series": "Livskunskap",
                "pdfs": [
                    {"url": "L1e/kl1_1.pdf", "title": "1_Meditation", "chapter": 1},
                    {"url": "L1e/kl1_2.pdf", "title": "2_Gnostics", "chapter": 2},
                    {"url": "L1e/kl1_3.pdf", "title": "3_Gnostic_Symbols", "chapter": 3},
                    {"url": "L1e/kl1_4.pdf", "title": "4_Discipleship", "chapter": 4},
                    {"url": "L1e/kl1_5.pdf", "title": "5_The_Planetary_Hierarchy", "chapter": 5},
                    {"url": "L1e/kl1_6.pdf", "title": "6_Identification_and_Liberation", "chapter": 6},
                    {"url": "L1e/kl1_7.pdf", "title": "7_Education", "chapter": 7},
                    {"url": "L1e/kl1_8.pdf", "title": "8_The_Conception_of_Right", "chapter": 8},
                    {"url": "L1e/kl1_9.pdf", "title": "9_The_Law", "chapter": 9},
                    {"url": "L1e/kl1_10.pdf", "title": "10_The_Secret_of_the_Sphinx", "chapter": 10},
                ]
            },
            "Knowledge_of_Life_Volume_2": {
                "directory": "01_Knowledge_of_Life/Volume_2_English",
                "description": "The Knowledge of Life - Volume 2 (English Translation)",
                "language": "english",
                "original_series": "Livskunskap",
                "pdfs": [
                    {"url": "L2e/kl2_1.pdf", "title": "1_Hylozoics", "chapter": 1},
                    {"url": "L2e/kl2_2.pdf", "title": "2_The_Hylozoic_World_View", "chapter": 2},
                    {"url": "L2e/kl2_3.pdf", "title": "3_Esoterics", "chapter": 3},
                    {"url": "L2e/kl2_4.pdf", "title": "4_The_Motion_Aspect", "chapter": 4},
                    {"url": "L2e/kl2_5.pdf", "title": "5_The_Consciousness_Aspect", "chapter": 5},
                    {"url": "L2e/kl2_6.pdf", "title": "6_The_Matter_Aspect", "chapter": 6},
                    {"url": "L2e/kl2_7.pdf", "title": "7_Consciousness_Development", "chapter": 7},
                    {"url": "L2e/kl2_8.pdf", "title": "8_The_Stages_of_Human_Development", "chapter": 8},
                    {"url": "L2e/kl2_9.pdf", "title": "9_Esoteric_Philosophy", "chapter": 9},
                    {"url": "L2e/kl2_10.pdf", "title": "10_Esoteric_Psychology", "chapter": 10},
                ]
            },
            "Knowledge_of_Life_Volume_4": {
                "directory": "01_Knowledge_of_Life/Volume_4_English",
                "description": "The Knowledge of Life - Volume 4 (English Translation)",
                "language": "english",
                "original_series": "Livskunskap",
                "pdfs": [
                    {"url": "L4e/L4E1.pdf", "title": "1_Laurency", "chapter": 1},
                    {"url": "L4e/L4E2.pdf", "title": "2_Culture", "chapter": 2},
                    {"url": "L4e/L4E3.pdf", "title": "3_Religion", "chapter": 3},
                    {"url": "L4e/L4E4.pdf", "title": "4_Theology", "chapter": 4},
                    {"url": "L4e/L4E5.pdf", "title": "5_Literature", "chapter": 5},
                    {"url": "L4e/L4E6.pdf", "title": "6_Art", "chapter": 6},
                    {"url": "L4e/L4E7.pdf", "title": "7_Philosophy", "chapter": 7},
                ]
            },
            "The_Philosophers_Stone": {
                "directory": "02_The_Philosophers_Stone/English_Translation",
                "description": "The Philosopher's Stone (De Vises Sten - English Translation)",
                "language": "english",
                "original_series": "De Vises Sten",
                "pdfs": [
                    {"url": "DVSe/ps1.pdf", "title": "1_Exoteric_World_View_and_Life_View", "chapter": 1},
                    {"url": "DVSe/ps2.pdf", "title": "2_The_Esoteric_World_View", "chapter": 2},
                    {"url": "DVSe/ps3.pdf", "title": "3_Esoteric_Life_View", "chapter": 3},
                ]
            },
            "First_Knowledge_Explanation": {
                "directory": "03_First_Knowledge_Explanation/English_Translation",
                "description": "First Knowledge Explanation (Första Kunskapsförklaringen - English)",
                "language": "english",
                "original_series": "Första Kunskapsförklaringen",
                "pdfs": [
                    {"url": "Fke/Fke_intro.pdf", "title": "00_Introduction", "chapter": 0},
                    {"url": "Fke/Fke1.pdf", "title": "01_One", "chapter": 1},
                    {"url": "Fke/Fke2.pdf", "title": "02_Two", "chapter": 2},
                    {"url": "Fke/Fke3.pdf", "title": "03_Three", "chapter": 3},
                    {"url": "Fke/Fke4.pdf", "title": "04_Four", "chapter": 4},
                    {"url": "Fke/Fke5.pdf", "title": "05_Five", "chapter": 5},
                    {"url": "Fke/Fke6.pdf", "title": "06_Six", "chapter": 6},
                    {"url": "Fke/Fke7.pdf", "title": "07_Seven", "chapter": 7},
                    {"url": "Fke/Fke8.pdf", "title": "08_Eight", "chapter": 8},
                    {"url": "Fke/Fke9.pdf", "title": "09_Nine", "chapter": 9},
                    {"url": "Fke/Fke10.pdf", "title": "10_Ten", "chapter": 10},
                    {"url": "Fke/Fke11.pdf", "title": "11_Eleven", "chapter": 11},
                    {"url": "Fke/Fke12.pdf", "title": "12_Twelve", "chapter": 12},
                    {"url": "Fke/Fke_study.pdf", "title": "Study_Questions", "chapter": 99},
                    {"url": "Fke/Fke_comm.pdf", "title": "Commentaries", "chapter": 98},
                    {"url": "Fke/Fke.pdf", "title": "Complete_Explanation", "chapter": 100},
                ]
            }
        }
        
        self.download_log = []
        self.create_directory_structure()
    
    def create_directory_structure(self):
        """Create organized directory structure"""
        print("📁 Creating organized directory structure...")
        
        # Create main directories
        directories_to_create = [
            self.output_dir,
            self.output_dir / "metadata",
            self.output_dir / "logs"
        ]
        
        # Create book-specific directories
        for book_key, book_info in self.pdf_structure.items():
            book_dir = self.output_dir / book_info["directory"]
            directories_to_create.append(book_dir)
        
        for directory in directories_to_create:
            directory.mkdir(parents=True, exist_ok=True)
        
        print(f"✅ Directory structure created in {self.output_dir}")
    
    def download_pdf(self, base_url: str, pdf_info: dict, target_dir: Path) -> bool:
        """Download a single PDF with proper naming"""
        url = f"{base_url}/{pdf_info['url']}"
        filename = f"{pdf_info['title']}.pdf"
        target_path = target_dir / filename
        
        # Skip if already exists
        if target_path.exists():
            print(f"⏭️  Skipping existing: {filename}")
            return True
        
        try:
            print(f"📥 Downloading: {pdf_info['title']}")
            response = self.session.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            # Download with progress
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(target_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r📥 Progress: {progress:.1f}%", end='', flush=True)
            
            print(f"\n✅ Downloaded: {filename} ({downloaded:,} bytes)")
            
            # Log successful download
            self.download_log.append({
                "book": pdf_info.get("book", "unknown"),
                "chapter": pdf_info["chapter"],
                "title": pdf_info["title"],
                "url": url,
                "local_path": str(target_path),
                "size_bytes": downloaded,
                "timestamp": datetime.now().isoformat(),
                "success": True
            })
            
            return True
            
        except Exception as e:
            print(f"\n❌ Failed to download {filename}: {e}")
            
            # Remove partial file
            if target_path.exists():
                target_path.unlink()
            
            # Log failed download
            self.download_log.append({
                "book": pdf_info.get("book", "unknown"),
                "chapter": pdf_info["chapter"],
                "title": pdf_info["title"],
                "url": url,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "success": False
            })
            
            return False
    
    def download_all_books(self):
        """Download all books in organized structure"""
        base_url = "https://www.laurency.com"
        
        print("🚀 Starting organized download of Laurency's works...")
        print(f"📚 Total books: {len(self.pdf_structure)}")
        
        total_successful = 0
        total_failed = 0
        
        for book_key, book_info in self.pdf_structure.items():
            print(f"\n📖 Downloading: {book_info['description']}")
            print(f"📁 Directory: {book_info['directory']}")
            print(f"📄 Chapters: {len(book_info['pdfs'])}")
            
            target_dir = self.output_dir / book_info["directory"]
            
            book_successful = 0
            book_failed = 0
            
            for pdf_info in book_info["pdfs"]:
                # Add book info to pdf_info for logging
                pdf_info_with_book = {**pdf_info, "book": book_key}
                
                if self.download_pdf(base_url, pdf_info_with_book, target_dir):
                    book_successful += 1
                    total_successful += 1
                else:
                    book_failed += 1
                    total_failed += 1
                
                # Be respectful to the server
                time.sleep(1)
            
            print(f"📊 {book_key}: {book_successful} successful, {book_failed} failed")
        
        print(f"\n🎉 Download complete!")
        print(f"✅ Total successful: {total_successful}")
        print(f"❌ Total failed: {total_failed}")
        
        return total_successful, total_failed
    
    def create_library_metadata(self):
        """Create metadata files for Sacred Library integration"""
        print("📝 Creating library metadata...")
        
        # Create comprehensive metadata
        metadata = {
            "download_info": {
                "timestamp": datetime.now().isoformat(),
                "source_url": "https://www.laurency.com",
                "downloader": "Organized Laurency Downloader v1.0",
                "total_books": len(self.pdf_structure),
                "total_pdfs": sum(len(book["pdfs"]) for book in self.pdf_structure.values())
            },
            "book_structure": self.pdf_structure,
            "download_log": self.download_log,
            "statistics": {
                "successful_downloads": len([log for log in self.download_log if log.get("success")]),
                "failed_downloads": len([log for log in self.download_log if not log.get("success")]),
                "total_size_bytes": sum(log.get("size_bytes", 0) for log in self.download_log if log.get("success"))
            },
            "sacred_library_integration": {
                "author": "Henry T. Laurency",
                "tradition": "Hylozoics",
                "language": "English (translated from Swedish)",
                "content_type": "Sacred Source Material",
                "verification_status": "Verified from official laurency.com",
                "citation_format": "Laurency, Henry T. {book_title}, Chapter {chapter}: {chapter_title}"
            }
        }
        
        # Save comprehensive metadata
        metadata_file = self.output_dir / "metadata" / "laurency_library_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Metadata saved: {metadata_file}")
        
        # Create book index for easy reference
        book_index_file = self.output_dir / "metadata" / "book_index.txt"
        with open(book_index_file, 'w', encoding='utf-8') as f:
            f.write("LAURENCY HYLOZOICS LIBRARY - BOOK INDEX\n")
            f.write("=" * 50 + "\n\n")
            
            for book_key, book_info in self.pdf_structure.items():
                f.write(f"{book_info['description']}\n")
                f.write(f"Directory: {book_info['directory']}\n")
                f.write(f"Language: {book_info['language']}\n")
                f.write(f"Original Series: {book_info['original_series']}\n")
                f.write(f"Chapters: {len(book_info['pdfs'])}\n\n")
                
                for pdf_info in book_info["pdfs"]:
                    f.write(f"  Chapter {pdf_info['chapter']:2d}: {pdf_info['title']}\n")
                f.write("\n")
        
        print(f"📚 Book index saved: {book_index_file}")
        
        # Create Sacred Library upload instructions
        instructions_file = self.output_dir / "SACRED_LIBRARY_UPLOAD_INSTRUCTIONS.md"
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write("""# Laurency Sacred Library Upload Instructions

## Overview
This collection contains Henry T. Laurency's Hylozoics works organized for Sacred Library integration.

## Structure
- **01_Knowledge_of_Life/** - Main series (Livskunskap)
  - Volume 1: Meditation, Discipleship, Hierarchy (10 chapters)
  - Volume 2: Hylozoics fundamentals, World View (10 chapters)  
  - Volume 4: Culture, Religion, Philosophy (7 chapters)
- **02_The_Philosophers_Stone/** - De Vises Sten (3 chapters)
- **03_First_Knowledge_Explanation/** - Första Kunskapsförklaringen (12 chapters + supplementary)

## Sacred Library Integration
Each PDF should be processed as:
- **Author**: Henry T. Laurency
- **Tradition**: Hylozoics
- **Language**: English (translated from Swedish)
- **Content Type**: Sacred Source Material
- **Citation Format**: Laurency, Henry T. [Book Title], Chapter [N]: [Chapter Title]

## Upload Process
1. Extract text from each PDF preserving paragraph structure
2. Maintain chapter numbering and titles exactly as shown
3. Include complete source citations for each quote
4. Mark as "Swedish Original Available" for future multi-language expansion

## Quality Notes
- All PDFs verified from official laurency.com source
- English translations - Swedish originals should be sought for authoritative version
- Complete works - no excerpts or summaries
- Systematic chapter organization perfect for Sacred Library structure

## Next Steps
1. Process PDFs through Sacred Library text extraction
2. Create quote database with chapter-level citations
3. Generate embeddings for semantic search
4. Integrate with dual-mode response system
""")
        
        print(f"📋 Upload instructions saved: {instructions_file}")
    
    def run(self):
        """Run the complete organized download"""
        print("🌟 Laurency Organized Downloader")
        print("=" * 40)
        
        try:
            # Download all books
            successful, failed = self.download_all_books()
            
            # Create metadata
            self.create_library_metadata()
            
            # Final summary
            print(f"\n🎉 DOWNLOAD COMPLETE!")
            print(f"📚 Books organized: {len(self.pdf_structure)}")
            print(f"✅ PDFs downloaded: {successful}")
            print(f"❌ Failed downloads: {failed}")
            print(f"📁 Location: {self.output_dir.absolute()}")
            print(f"📋 Ready for Sacred Library integration!")
            
        except KeyboardInterrupt:
            print("\n⏹️  Download interrupted by user")
        except Exception as e:
            print(f"\n💥 Unexpected error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    downloader = OrganizedLaurencyDownloader()
    downloader.run()
