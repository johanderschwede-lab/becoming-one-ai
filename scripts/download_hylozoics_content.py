#!/usr/bin/env python3
"""
Hylozoics Content Downloader
============================

Systematically downloads Henry T. Laurency's works from laurency.com
Handles both Swedish originals and English translations
Preserves file structure and metadata for sacred library integration

Usage:
    python download_hylozoics_content.py
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

class HylozoicsDownloader:
    def __init__(self, base_url: str = "https://www.laurency.com", output_dir: str = "hylozoics_content"):
        self.base_url = base_url
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Create directory structure
        self.create_directories()
        
        # Download log
        self.download_log = []
        
    def create_directories(self):
        """Create organized directory structure"""
        directories = [
            self.output_dir,
            self.output_dir / "swedish_originals",
            self.output_dir / "english_translations", 
            self.output_dir / "german_translations",
            self.output_dir / "other_languages",
            self.output_dir / "metadata",
            self.output_dir / "raw_html",
            self.output_dir / "processed_text"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
        print(f"✅ Created directory structure in {self.output_dir}")
    
    def fetch_page(self, url: str, max_retries: int = 3) -> Optional[BeautifulSoup]:
        """Fetch and parse a web page with retries"""
        for attempt in range(max_retries):
            try:
                print(f"🔍 Fetching: {url} (attempt {attempt + 1})")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Handle different encodings
                if response.encoding is None or response.encoding == 'ISO-8859-1':
                    response.encoding = 'utf-8'
                
                soup = BeautifulSoup(response.content, 'html.parser')
                time.sleep(1)  # Be respectful to the server
                return soup
                
            except requests.RequestException as e:
                print(f"❌ Error fetching {url}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)  # Wait before retry
                else:
                    return None
    
    def discover_book_links(self) -> Dict[str, List[Dict[str, str]]]:
        """Discover all book links from the main site"""
        print("🔍 Discovering book links...")
        
        # Common patterns for Hylozoics books
        book_patterns = [
            r'verklighetskunskap',  # The Knowledge of Reality (Swedish)
            r'knowledge.*reality',   # The Knowledge of Reality (English)
            r'philosopher.*stone',   # The Philosopher's Stone
            r'de.*vises.*sten',     # De vises sten (Swedish)
            r'människans.*väg',     # Människans väg (Swedish)
            r'way.*man',            # The Way of Man (English)
            r'hylozoik',            # General Hylozoics
            r'laurency',            # Author name
        ]
        
        discovered_links = {
            'swedish': [],
            'english': [],
            'german': [],
            'other': []
        }
        
        # Try multiple entry points
        entry_points = [
            self.base_url,
            f"{self.base_url}/index.html",
            f"{self.base_url}/english.html",
            f"{self.base_url}/svenska.html",
            f"{self.base_url}/deutsch.html",
        ]
        
        for entry_point in entry_points:
            soup = self.fetch_page(entry_point)
            if soup:
                self.extract_links_from_page(soup, discovered_links, entry_point)
        
        return discovered_links
    
    def extract_links_from_page(self, soup: BeautifulSoup, discovered_links: Dict, base_url: str):
        """Extract relevant links from a page"""
        # Find all links
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href')
            if not href:
                continue
                
            # Make absolute URL
            full_url = urllib.parse.urljoin(base_url, href)
            link_text = link.get_text(strip=True).lower()
            
            # Determine language and relevance
            language = self.detect_language(link_text, href)
            if language and self.is_relevant_link(link_text, href):
                discovered_links[language].append({
                    'url': full_url,
                    'text': link.get_text(strip=True),
                    'href': href,
                    'source_page': base_url
                })
    
    def detect_language(self, text: str, href: str) -> Optional[str]:
        """Detect the language of a link"""
        text_lower = text.lower()
        href_lower = href.lower()
        
        # Swedish indicators
        if any(word in text_lower or word in href_lower for word in 
               ['svenska', 'svensk', 'verklighetskunskap', 'människans', 'vises']):
            return 'swedish'
        
        # English indicators  
        if any(word in text_lower or word in href_lower for word in
               ['english', 'knowledge', 'reality', 'philosopher', 'stone', 'way', 'man']):
            return 'english'
        
        # German indicators
        if any(word in text_lower or word in href_lower for word in
               ['deutsch', 'german', 'erkenntnis', 'wirklichkeit']):
            return 'german'
        
        # Default to other if it seems relevant
        if self.is_relevant_link(text, href):
            return 'other'
        
        return None
    
    def is_relevant_link(self, text: str, href: str) -> bool:
        """Check if a link is relevant to Hylozoics content"""
        text_lower = text.lower()
        href_lower = href.lower()
        
        relevant_terms = [
            'hylozoic', 'laurency', 'knowledge', 'reality', 'philosopher', 'stone',
            'way', 'man', 'verklighetskunskap', 'vises', 'sten', 'människans',
            'pdf', 'book', 'text', 'chapter', 'download'
        ]
        
        return any(term in text_lower or term in href_lower for term in relevant_terms)
    
    def download_file(self, url: str, local_path: Path) -> bool:
        """Download a file to local path"""
        try:
            print(f"📥 Downloading: {url}")
            response = self.session.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            # Create parent directories
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download with progress indication
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
            
            print(f"\n✅ Downloaded: {local_path}")
            
            # Log the download
            self.download_log.append({
                'url': url,
                'local_path': str(local_path),
                'size': downloaded,
                'timestamp': datetime.now().isoformat(),
                'success': True
            })
            
            return True
            
        except Exception as e:
            print(f"\n❌ Failed to download {url}: {e}")
            self.download_log.append({
                'url': url,
                'local_path': str(local_path),
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'success': False
            })
            return False
    
    def download_content(self, discovered_links: Dict[str, List[Dict[str, str]]]):
        """Download all discovered content"""
        print("📥 Starting content download...")
        
        for language, links in discovered_links.items():
            if not links:
                continue
                
            print(f"\n📚 Downloading {language} content ({len(links)} links)")
            
            for i, link_info in enumerate(links, 1):
                url = link_info['url']
                
                # Determine file extension and local path
                parsed_url = urllib.parse.urlparse(url)
                filename = os.path.basename(parsed_url.path)
                
                if not filename or filename == '/':
                    filename = f"{language}_content_{i}.html"
                
                # Ensure we have an extension
                if not os.path.splitext(filename)[1]:
                    filename += '.html'
                
                # Create local path based on language
                if language == 'swedish':
                    local_path = self.output_dir / "swedish_originals" / filename
                elif language == 'english':
                    local_path = self.output_dir / "english_translations" / filename
                elif language == 'german':
                    local_path = self.output_dir / "german_translations" / filename
                else:
                    local_path = self.output_dir / "other_languages" / filename
                
                # Skip if already downloaded
                if local_path.exists():
                    print(f"⏭️  Skipping existing: {filename}")
                    continue
                
                # Download the file
                self.download_file(url, local_path)
                
                # Be respectful to the server
                time.sleep(2)
    
    def extract_text_content(self):
        """Extract and process text content from downloaded files"""
        print("\n📝 Extracting text content...")
        
        for lang_dir in ['swedish_originals', 'english_translations', 'german_translations']:
            source_dir = self.output_dir / lang_dir
            target_dir = self.output_dir / "processed_text" / lang_dir
            target_dir.mkdir(parents=True, exist_ok=True)
            
            for file_path in source_dir.glob('*'):
                if file_path.is_file():
                    self.process_text_file(file_path, target_dir)
    
    def process_text_file(self, file_path: Path, target_dir: Path):
        """Process individual text file"""
        try:
            print(f"📝 Processing: {file_path.name}")
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # If it's HTML, extract text
            if file_path.suffix.lower() in ['.html', '.htm']:
                soup = BeautifulSoup(content, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Extract text
                text_content = soup.get_text()
                
                # Clean up text
                lines = (line.strip() for line in text_content.splitlines())
                text_content = '\n'.join(line for line in lines if line)
                
            else:
                text_content = content
            
            # Save processed text
            output_file = target_dir / f"{file_path.stem}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            print(f"✅ Processed: {output_file}")
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    def save_metadata(self, discovered_links: Dict[str, List[Dict[str, str]]]):
        """Save metadata about discovered content"""
        metadata = {
            'download_timestamp': datetime.now().isoformat(),
            'base_url': self.base_url,
            'discovered_links': discovered_links,
            'download_log': self.download_log,
            'statistics': {
                'total_links': sum(len(links) for links in discovered_links.values()),
                'successful_downloads': len([log for log in self.download_log if log.get('success')]),
                'failed_downloads': len([log for log in self.download_log if not log.get('success')])
            }
        }
        
        metadata_file = self.output_dir / "metadata" / "download_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Metadata saved to: {metadata_file}")
    
    def run(self):
        """Run the complete download process"""
        print("🚀 Starting Hylozoics Content Download")
        print(f"📁 Output directory: {self.output_dir.absolute()}")
        print(f"🌐 Base URL: {self.base_url}")
        
        try:
            # Step 1: Discover all relevant links
            discovered_links = self.discover_book_links()
            
            # Print discovery results
            total_links = sum(len(links) for links in discovered_links.values())
            print(f"\n📊 Discovery Results:")
            for language, links in discovered_links.items():
                if links:
                    print(f"  {language}: {len(links)} links")
            print(f"  Total: {total_links} links")
            
            if total_links == 0:
                print("❌ No relevant links discovered. Check site structure or patterns.")
                return
            
            # Step 2: Download content
            self.download_content(discovered_links)
            
            # Step 3: Extract text content
            self.extract_text_content()
            
            # Step 4: Save metadata
            self.save_metadata(discovered_links)
            
            # Summary
            successful = len([log for log in self.download_log if log.get('success')])
            failed = len([log for log in self.download_log if not log.get('success')])
            
            print(f"\n🎉 Download Complete!")
            print(f"✅ Successful: {successful}")
            print(f"❌ Failed: {failed}")
            print(f"📁 Content saved in: {self.output_dir.absolute()}")
            
        except KeyboardInterrupt:
            print("\n⏹️  Download interrupted by user")
        except Exception as e:
            print(f"\n💥 Unexpected error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main function"""
    print("🌟 Hylozoics Content Downloader")
    print("================================")
    
    # You can customize these settings
    base_url = "https://www.laurency.com"
    output_dir = "hylozoics_content"
    
    # Allow command line arguments
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    # Create and run downloader
    downloader = HylozoicsDownloader(base_url, output_dir)
    downloader.run()


if __name__ == "__main__":
    main()
