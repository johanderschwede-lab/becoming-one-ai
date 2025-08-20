#!/usr/bin/env python3
"""
Laurency PDF Downloader
=======================

Downloads all PDF files from laurency.com for Hylozoics Sacred Library
Organizes by language (Swedish originals, English translations, etc.)

Usage:
    python download_laurency_pdfs.py
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import json
from pathlib import Path
from typing import List, Dict, Optional
import re
from datetime import datetime

class LaurencyPDFDownloader:
    def __init__(self, base_url: str = "https://www.laurency.com", output_dir: str = "laurency_pdfs"):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Create directory structure
        self.create_directories()
        
        # Download tracking
        self.pdf_links = []
        self.download_log = []
        
    def create_directories(self):
        """Create organized directory structure for PDFs"""
        directories = [
            self.output_dir,
            self.output_dir / "swedish_originals",
            self.output_dir / "english_translations", 
            self.output_dir / "german_translations",
            self.output_dir / "other_languages",
            self.output_dir / "metadata"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
        print(f"✅ Created PDF directory structure in {self.output_dir}")
    
    def fetch_page(self, url: str, max_retries: int = 3) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page"""
        for attempt in range(max_retries):
            try:
                print(f"🔍 Fetching: {url} (attempt {attempt + 1})")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                time.sleep(1)  # Be respectful
                return soup
                
            except requests.RequestException as e:
                print(f"❌ Error fetching {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    return None
    
    def discover_pdf_links(self) -> List[Dict[str, str]]:
        """Find all PDF links on the site"""
        print("🔍 Discovering PDF links...")
        
        pdf_links = []
        
        # Try multiple entry points and common pages
        entry_points = [
            self.base_url,
            f"{self.base_url}/index.html",
            f"{self.base_url}/english.html",
            f"{self.base_url}/svenska.html", 
            f"{self.base_url}/deutsch.html",
            f"{self.base_url}/books.html",
            f"{self.base_url}/downloads.html",
            f"{self.base_url}/texts.html"
        ]
        
        visited_pages = set()
        
        for entry_point in entry_points:
            if entry_point in visited_pages:
                continue
                
            soup = self.fetch_page(entry_point)
            if soup:
                visited_pages.add(entry_point)
                
                # Find PDF links on this page
                page_pdfs = self.extract_pdf_links(soup, entry_point)
                pdf_links.extend(page_pdfs)
                
                # Also look for links to other pages that might contain PDFs
                other_pages = self.find_other_relevant_pages(soup, entry_point)
                for page_url in other_pages:
                    if page_url not in visited_pages:
                        page_soup = self.fetch_page(page_url)
                        if page_soup:
                            visited_pages.add(page_url)
                            more_pdfs = self.extract_pdf_links(page_soup, page_url)
                            pdf_links.extend(more_pdfs)
        
        # Remove duplicates
        unique_pdfs = []
        seen_urls = set()
        for pdf in pdf_links:
            if pdf['url'] not in seen_urls:
                unique_pdfs.append(pdf)
                seen_urls.add(pdf['url'])
        
        print(f"📄 Found {len(unique_pdfs)} unique PDF files")
        return unique_pdfs
    
    def extract_pdf_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract PDF links from a page"""
        pdf_links = []
        
        # Find all links ending in .pdf
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and href.lower().endswith('.pdf'):
                # Make absolute URL
                full_url = urllib.parse.urljoin(base_url, href)
                
                # Get link text for context
                link_text = link.get_text(strip=True)
                
                # Detect language and book info
                language = self.detect_pdf_language(link_text, href)
                book_info = self.extract_book_info(link_text, href)
                
                pdf_info = {
                    'url': full_url,
                    'filename': os.path.basename(urllib.parse.urlparse(full_url).path),
                    'link_text': link_text,
                    'language': language,
                    'book_title': book_info.get('title', ''),
                    'book_type': book_info.get('type', ''),
                    'source_page': base_url
                }
                
                pdf_links.append(pdf_info)
                print(f"  📄 Found: {pdf_info['filename']} ({language}) - {link_text}")
        
        return pdf_links
    
    def find_other_relevant_pages(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Find other pages that might contain PDFs"""
        relevant_pages = []
        
        # Look for links that might lead to book/text pages
        relevant_keywords = [
            'book', 'text', 'download', 'pdf', 'hylozoic', 'laurency',
            'knowledge', 'reality', 'philosopher', 'stone', 'way', 'man',
            'verklighetskunskap', 'vises', 'sten', 'människans'
        ]
        
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            link_text = link.get_text(strip=True).lower()
            
            if href and not href.lower().endswith('.pdf'):
                # Check if link text or href contains relevant keywords
                if any(keyword in link_text or keyword in href.lower() for keyword in relevant_keywords):
                    full_url = urllib.parse.urljoin(base_url, href)
                    if full_url.startswith(self.base_url):  # Stay within domain
                        relevant_pages.append(full_url)
        
        return relevant_pages
    
    def detect_pdf_language(self, link_text: str, href: str) -> str:
        """Detect language of PDF based on filename and link text"""
        text_lower = link_text.lower()
        href_lower = href.lower()
        
        # Swedish indicators
        swedish_indicators = [
            'svenska', 'svensk', 'sv', 'verklighetskunskap', 'människans', 
            'vises', 'sten', 'kunskap', 'väg', 'hylozoik'
        ]
        if any(indicator in text_lower or indicator in href_lower for indicator in swedish_indicators):
            return 'swedish'
        
        # English indicators
        english_indicators = [
            'english', 'eng', 'en', 'knowledge', 'reality', 'philosopher', 
            'stone', 'way', 'man', 'hylozoics'
        ]
        if any(indicator in text_lower or indicator in href_lower for indicator in english_indicators):
            return 'english'
        
        # German indicators
        german_indicators = [
            'deutsch', 'german', 'de', 'erkenntnis', 'wirklichkeit', 
            'philosoph', 'stein', 'weg', 'mensch'
        ]
        if any(indicator in text_lower or indicator in href_lower for indicator in german_indicators):
            return 'german'
        
        # Default to other
        return 'other'
    
    def extract_book_info(self, link_text: str, href: str) -> Dict[str, str]:
        """Extract book title and type information"""
        text_lower = link_text.lower()
        href_lower = href.lower()
        
        book_info = {'title': '', 'type': ''}
        
        # Known Laurency books
        books = {
            'knowledge of reality': 'The Knowledge of Reality',
            'verklighetskunskap': 'The Knowledge of Reality (Swedish)',
            'philosopher stone': "The Philosopher's Stone", 
            'vises sten': "The Philosopher's Stone (Swedish)",
            'way of man': 'The Way of Man',
            'människans väg': 'The Way of Man (Swedish)',
            'hylozoics': 'Hylozoics General'
        }
        
        for key, title in books.items():
            if key in text_lower or key in href_lower:
                book_info['title'] = title
                break
        
        # Determine type
        if 'complete' in text_lower or 'full' in text_lower:
            book_info['type'] = 'complete'
        elif 'chapter' in text_lower or 'part' in text_lower:
            book_info['type'] = 'chapter'
        elif 'summary' in text_lower or 'abstract' in text_lower:
            book_info['type'] = 'summary'
        else:
            book_info['type'] = 'book'
        
        return book_info
    
    def download_pdf(self, pdf_info: Dict[str, str]) -> bool:
        """Download a single PDF file"""
        url = pdf_info['url']
        language = pdf_info['language']
        filename = pdf_info['filename']
        
        # Determine target directory based on language
        if language == 'swedish':
            target_dir = self.output_dir / "swedish_originals"
        elif language == 'english':
            target_dir = self.output_dir / "english_translations"
        elif language == 'german':
            target_dir = self.output_dir / "german_translations"
        else:
            target_dir = self.output_dir / "other_languages"
        
        # Create a better filename if we have book info
        if pdf_info['book_title']:
            safe_title = re.sub(r'[^\w\s-]', '', pdf_info['book_title'])
            safe_title = re.sub(r'[-\s]+', '_', safe_title)
            filename = f"{safe_title}_{filename}"
        
        local_path = target_dir / filename
        
        # Skip if already exists
        if local_path.exists():
            print(f"⏭️  Skipping existing: {filename}")
            return True
        
        try:
            print(f"📥 Downloading: {filename}")
            response = self.session.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            # Download with progress
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(local_path, 'wb') as f:
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
                **pdf_info,
                'local_path': str(local_path),
                'size_bytes': downloaded,
                'timestamp': datetime.now().isoformat(),
                'success': True
            })
            
            return True
            
        except Exception as e:
            print(f"\n❌ Failed to download {filename}: {e}")
            self.download_log.append({
                **pdf_info,
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'success': False
            })
            return False
    
    def download_all_pdfs(self, pdf_links: List[Dict[str, str]]):
        """Download all discovered PDFs"""
        print(f"\n📥 Starting download of {len(pdf_links)} PDFs...")
        
        successful = 0
        failed = 0
        
        for i, pdf_info in enumerate(pdf_links, 1):
            print(f"\n[{i}/{len(pdf_links)}] ", end='')
            
            if self.download_pdf(pdf_info):
                successful += 1
            else:
                failed += 1
            
            # Be respectful to the server
            time.sleep(2)
        
        print(f"\n🎉 Download complete!")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
    
    def save_metadata(self, pdf_links: List[Dict[str, str]]):
        """Save metadata about discovered and downloaded PDFs"""
        metadata = {
            'download_timestamp': datetime.now().isoformat(),
            'base_url': self.base_url,
            'total_pdfs_discovered': len(pdf_links),
            'pdfs_by_language': {},
            'pdfs_by_book': {},
            'discovered_pdfs': pdf_links,
            'download_log': self.download_log,
            'statistics': {
                'successful_downloads': len([log for log in self.download_log if log.get('success')]),
                'failed_downloads': len([log for log in self.download_log if not log.get('success')])
            }
        }
        
        # Count by language
        for pdf in pdf_links:
            lang = pdf['language']
            metadata['pdfs_by_language'][lang] = metadata['pdfs_by_language'].get(lang, 0) + 1
        
        # Count by book
        for pdf in pdf_links:
            book = pdf['book_title'] or 'Unknown'
            metadata['pdfs_by_book'][book] = metadata['pdfs_by_book'].get(book, 0) + 1
        
        # Save metadata
        metadata_file = self.output_dir / "metadata" / "pdf_download_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Metadata saved to: {metadata_file}")
        
        # Also save a simple list of PDFs for reference
        pdf_list_file = self.output_dir / "metadata" / "pdf_list.txt"
        with open(pdf_list_file, 'w', encoding='utf-8') as f:
            f.write("Laurency PDF Downloads\n")
            f.write("======================\n\n")
            
            for lang in ['swedish', 'english', 'german', 'other']:
                lang_pdfs = [pdf for pdf in pdf_links if pdf['language'] == lang]
                if lang_pdfs:
                    f.write(f"{lang.upper()} ({len(lang_pdfs)} files):\n")
                    for pdf in lang_pdfs:
                        f.write(f"  - {pdf['filename']} - {pdf['book_title']}\n")
                    f.write("\n")
        
        print(f"📝 PDF list saved to: {pdf_list_file}")
    
    def run(self):
        """Run the complete PDF download process"""
        print("🚀 Starting Laurency PDF Download")
        print(f"📁 Output directory: {self.output_dir.absolute()}")
        print(f"🌐 Base URL: {self.base_url}")
        
        try:
            # Step 1: Discover all PDF links
            pdf_links = self.discover_pdf_links()
            
            if not pdf_links:
                print("❌ No PDF files found. Check site structure.")
                return
            
            # Print discovery summary
            print(f"\n📊 Discovery Summary:")
            by_language = {}
            for pdf in pdf_links:
                lang = pdf['language']
                by_language[lang] = by_language.get(lang, 0) + 1
            
            for lang, count in by_language.items():
                print(f"  {lang}: {count} PDFs")
            
            # Step 2: Download all PDFs
            self.download_all_pdfs(pdf_links)
            
            # Step 3: Save metadata
            self.save_metadata(pdf_links)
            
            print(f"\n🎉 All done! PDFs saved in: {self.output_dir.absolute()}")
            
        except KeyboardInterrupt:
            print("\n⏹️  Download interrupted by user")
        except Exception as e:
            print(f"\n💥 Unexpected error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main function"""
    print("📄 Laurency PDF Downloader")
    print("===========================")
    
    # Default settings
    base_url = "https://www.laurency.com"
    output_dir = "laurency_pdfs"
    
    # Allow command line arguments
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    # Create and run downloader
    downloader = LaurencyPDFDownloader(base_url, output_dir)
    downloader.run()


if __name__ == "__main__":
    main()
