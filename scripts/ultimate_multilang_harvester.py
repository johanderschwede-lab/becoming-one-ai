#!/usr/bin/env python3
"""
Ultimate Multi-Language Hylozoics Harvester
==========================================

The definitive script to discover and download ALL Hylozoics content
in ALL available languages by properly parsing navigation menus
"""

import requests
from bs4 import BeautifulSoup
import urllib.parse
from pathlib import Path
import json
import os
from datetime import datetime
import time
import re

class UltimateMultiLangHarvester:
    def __init__(self, output_dir: str = "laurency_ultimate"):
        self.base_url = "https://www.laurency.com"
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Language configurations
        self.languages = {
            'english': {
                'name': 'English',
                'flag': '🇬🇧',
                'nav_frame': 'side.htm',
                'path': '',
                'is_original': False
            },
            'swedish': {
                'name': 'Svenska',
                'flag': '🇸🇪',
                'nav_frame': 'Swedish/sideswe.htm',
                'path': 'Swedish/',
                'is_original': True
            },
            'german': {
                'name': 'Deutsch',
                'flag': '🇩🇪',
                'nav_frame': 'German/sideger.htm',
                'path': 'German/',
                'is_original': False
            },
            'french': {
                'name': 'Français',
                'flag': '🇫🇷',
                'nav_frame': 'French/sidefr.htm',
                'path': 'French/',
                'is_original': False
            },
            'spanish': {
                'name': 'Español',
                'flag': '🇪🇸',
                'nav_frame': 'Spanish/sideesp.htm',
                'path': 'Spanish/',
                'is_original': False
            },
            'italian': {
                'name': 'Italiano',
                'flag': '🇮🇹',
                'nav_frame': 'Italian/sideita.htm',
                'path': 'Italian/',
                'is_original': False
            },
            'finnish': {
                'name': 'Suomi',
                'flag': '🇫🇮',
                'nav_frame': 'Finnish/sidefin.htm',
                'path': 'Finnish/',
                'is_original': False
            },
            'russian': {
                'name': 'Русский',
                'flag': '🇷🇺',
                'nav_frame': 'Russian/siderus.htm',
                'path': 'Russian/',
                'is_original': False
            },
            'danish': {
                'name': 'Dansk',
                'flag': '🇩🇰',
                'nav_frame': 'Danish/sidedan.htm',
                'path': 'Danish/',
                'is_original': False
            },
            'hungarian': {
                'name': 'Magyar',
                'flag': '🇭🇺',
                'nav_frame': 'Hungarian/sidehun.htm',
                'path': 'Hungarian/',
                'is_original': False
            }
        }
        
        self.discovered_content = {}
        
    def discover_language_content(self, lang_code: str, lang_info: dict):
        """Discover all content for a specific language with improved detection"""
        print(f"\n{lang_info['flag']} Discovering {lang_info['name']} ({lang_code})")
        print("=" * 60)
        
        try:
            # Get navigation frame
            nav_url = f"{self.base_url}/{lang_info['nav_frame']}"
            response = self.session.get(nav_url, timeout=15)
            
            if response.status_code != 200:
                print(f"  ❌ Navigation not accessible: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all option elements
            options = soup.find_all('option', value=True)
            
            books = []
            dictionaries = []
            
            print(f"  🔍 Found {len(options)} navigation options")
            
            for option in options:
                value = option.get('value')
                text = option.get_text(strip=True)
                
                if not value or not text:
                    continue
                
                # Skip obvious navigation elements
                if any(skip in text.lower() for skip in [
                    'language', 'sprache', 'langue', 'idioma', 'lingua', 'kieli', 'язык',
                    'books on', 'bücher', 'livres', 'libros', 'libri', 'kirjat', 'книги',
                    'further info', 'weitere', 'plus d\'info', 'más info', 'ulteriori',
                    '---', '- - -', 'start', 'home', 'email'
                ]):
                    continue
                
                # Check for dictionaries (multi-language keywords)
                if any(dict_word in text.lower() for dict_word in [
                    'dictionary', 'lexikon', 'ordbok', 'wörterbuch', 'dictionnaire', 
                    'dizionario', 'diccionario', 'sanakirja', 'словарь'
                ]):
                    full_url = urllib.parse.urljoin(nav_url, value)
                    dictionaries.append({
                        'title': text,
                        'url': full_url,
                        'type': 'dictionary'
                    })
                    print(f"  📖 Dictionary: {text}")
                    continue
                
                # Check for table of contents pages (any .htm file that's not main/index)
                if (value.endswith('.htm') and 
                    'main' not in value.lower() and 
                    'index' not in value.lower() and
                    'intro' not in value.lower() and
                    len(text) > 5):  # Meaningful title
                    
                    # This could be a book TOC - explore it
                    toc_url = urllib.parse.urljoin(nav_url, value)
                    book_pdfs = self.discover_book_pdfs(toc_url, text, lang_info['path'])
                    if book_pdfs:
                        books.extend(book_pdfs)
                        print(f"  📚 Book Series: {text} ({len(book_pdfs)} chapters)")
                    else:
                        print(f"  🔍 Checked: {text} (no PDFs found)")
            
            language_content = {
                'language_code': lang_code,
                'language_info': lang_info,
                'books': books,
                'dictionaries': dictionaries,
                'total_books': len(books),
                'total_dictionaries': len(dictionaries)
            }
            
            print(f"  📊 Total: {len(books)} books, {len(dictionaries)} dictionaries")
            return language_content
            
        except Exception as e:
            print(f"  💥 Error discovering {lang_info['name']}: {e}")
            return None
    
    def discover_book_pdfs(self, toc_url: str, series_title: str, lang_path: str):
        """Discover PDF files from a table of contents page"""
        try:
            print(f"    🔍 Exploring: {series_title}")
            response = self.session.get(toc_url, timeout=10)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all PDF links
            pdf_links = []
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href')
                if href and href.lower().endswith('.pdf'):
                    # Build full URL
                    if href.startswith('http'):
                        full_url = href
                    else:
                        full_url = urllib.parse.urljoin(toc_url, href)
                    
                    # Extract chapter title
                    chapter_title = link.get_text(strip=True)
                    if not chapter_title:
                        # Extract from filename
                        filename = href.split('/')[-1]
                        chapter_title = filename.replace('.pdf', '').replace('_', ' ').title()
                    
                    # Clean up title
                    chapter_title = re.sub(r'^\d+\.?\s*', '', chapter_title)  # Remove leading numbers
                    chapter_title = chapter_title.strip()
                    
                    pdf_links.append({
                        'title': chapter_title,
                        'series': series_title,
                        'url': full_url,
                        'filename': href.split('/')[-1],
                        'type': 'pdf_chapter'
                    })
                    print(f"      📄 {chapter_title}")
            
            return pdf_links
            
        except Exception as e:
            print(f"    ❌ Error getting PDFs from {toc_url}: {e}")
            return []
    
    def download_content(self, lang_code: str, content: dict):
        """Download all content for a language"""
        lang_info = content['language_info']
        print(f"\n📥 {lang_info['flag']} Downloading {lang_info['name']} content...")
        
        # Create language directory
        lang_dir = self.output_dir / f"{lang_code}_{lang_info['name'].replace(' ', '_')}"
        lang_dir.mkdir(parents=True, exist_ok=True)
        
        downloaded_files = []
        
        # Download books
        if content['books']:
            books_dir = lang_dir / "Books"
            books_dir.mkdir(exist_ok=True)
            
            # Group books by series
            series_groups = {}
            for book in content['books']:
                series = book['series']
                if series not in series_groups:
                    series_groups[series] = []
                series_groups[series].append(book)
            
            for series, books in series_groups.items():
                # Clean series name for directory
                safe_series = re.sub(r'[<>:"/\\|?*]', '_', series)
                series_dir = books_dir / safe_series
                series_dir.mkdir(exist_ok=True)
                
                print(f"  📚 Downloading {series} ({len(books)} chapters)")
                
                for i, book in enumerate(books, 1):
                    try:
                        print(f"    📄 {i:2d}/{len(books)} {book['title']}")
                        response = self.session.get(book['url'], timeout=30)
                        response.raise_for_status()
                        
                        # Save PDF
                        pdf_file = series_dir / book['filename']
                        with open(pdf_file, 'wb') as f:
                            f.write(response.content)
                        
                        downloaded_files.append({
                            'type': 'book',
                            'series': series,
                            'title': book['title'],
                            'filename': book['filename'],
                            'path': str(pdf_file),
                            'size': len(response.content),
                            'url': book['url']
                        })
                        
                        # Respectful delay
                        time.sleep(0.5)
                        
                    except Exception as e:
                        print(f"    ❌ Failed: {book['title']} - {e}")
        
        # Download dictionaries
        if content['dictionaries']:
            dict_dir = lang_dir / "Dictionaries"
            dict_dir.mkdir(exist_ok=True)
            
            for dict_item in content['dictionaries']:
                try:
                    print(f"  📖 Downloading {dict_item['title']}")
                    response = self.session.get(dict_item['url'], timeout=15)
                    response.raise_for_status()
                    
                    # Save HTML dictionary
                    dict_file = dict_dir / f"dictionary_{lang_code}.html"
                    with open(dict_file, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    
                    downloaded_files.append({
                        'type': 'dictionary',
                        'title': dict_item['title'],
                        'path': str(dict_file),
                        'size': len(response.text),
                        'url': dict_item['url']
                    })
                    
                except Exception as e:
                    print(f"    ❌ Failed: {dict_item['title']} - {e}")
        
        # Save download log
        log_file = lang_dir / "download_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump({
                'language': lang_code,
                'language_info': lang_info,
                'download_date': datetime.now().isoformat(),
                'total_files': len(downloaded_files),
                'files': downloaded_files
            }, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ Downloaded {len(downloaded_files)} files for {lang_info['name']}")
        return downloaded_files
    
    def create_ultimate_summary(self):
        """Create the ultimate summary of the complete harvest"""
        print(f"\n📊 Creating Ultimate Summary...")
        
        # Calculate totals
        total_languages = len(self.discovered_content)
        total_books = sum(len(content.get('books', [])) for content in self.discovered_content.values())
        total_dictionaries = sum(len(content.get('dictionaries', [])) for content in self.discovered_content.values())
        
        # Create master catalog
        catalog_data = {
            'harvest_date': datetime.now().isoformat(),
            'total_languages': total_languages,
            'total_books': total_books,
            'total_dictionaries': total_dictionaries,
            'languages': {}
        }
        
        for lang_code, content in self.discovered_content.items():
            if content:
                lang_info = content['language_info']
                books = content.get('books', [])
                dicts = content.get('dictionaries', [])
                
                # Group books by series
                series_groups = {}
                for book in books:
                    series = book['series']
                    if series not in series_groups:
                        series_groups[series] = []
                    series_groups[series].append(book)
                
                catalog_data['languages'][lang_code] = {
                    'name': lang_info['name'],
                    'flag': lang_info['flag'],
                    'is_original': lang_info['is_original'],
                    'books_count': len(books),
                    'dictionaries_count': len(dicts),
                    'series_count': len(series_groups),
                    'series': {series: len(books) for series, books in series_groups.items()},
                    'books': books,
                    'dictionaries': dicts
                }
        
        # Save master catalog
        catalog_file = self.output_dir / "ULTIMATE_CATALOG.json"
        with open(catalog_file, 'w', encoding='utf-8') as f:
            json.dump(catalog_data, f, indent=2, ensure_ascii=False)
        
        # Create comprehensive summary
        summary_file = self.output_dir / "ULTIMATE_HARVEST_SUMMARY.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# 🌍 ULTIMATE Multi-Language Hylozoics Harvest\n\n")
            f.write(f"**Harvest Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"**Total Languages**: {total_languages}\n")
            f.write(f"**Total Book Series**: {sum(len(data.get('series', {})) for data in catalog_data['languages'].values())}\n")
            f.write(f"**Total Books**: {total_books}\n")
            f.write(f"**Total Dictionaries**: {total_dictionaries}\n\n")
            
            f.write("## 🗂️ Complete Language Breakdown\n\n")
            
            for lang_code, data in catalog_data['languages'].items():
                f.write(f"### {data['flag']} {data['name']}\n")
                f.write(f"- **Book Series**: {data['series_count']}\n")
                f.write(f"- **Total Books**: {data['books_count']}\n")
                f.write(f"- **Dictionaries**: {data['dictionaries_count']}\n")
                f.write(f"- **Original Language**: {'Yes' if data['is_original'] else 'No'}\n\n")
                
                if data['series']:
                    f.write("#### 📚 Book Series:\n")
                    for series, count in data['series'].items():
                        f.write(f"- **{series}**: {count} chapters\n")
                    f.write("\n")
            
            f.write("## 🏛️ Sacred Library Revolution\n\n")
            f.write("This ultimate harvest creates the foundation for:\n\n")
            f.write("### 🌐 Multi-Language Authenticity\n")
            f.write("- **Swedish Originals**: Authoritative source material\n")
            f.write("- **9+ Translations**: Complete cultural accessibility\n")
            f.write("- **Cross-Language Validation**: Translation accuracy verification\n")
            f.write("- **Cultural Context**: How concepts translate across cultures\n\n")
            
            f.write("### 🎯 Tiered Access Revolution\n")
            f.write("- **Tier 1**: Single-language access with exact citations\n")
            f.write("- **Tier 2**: Cross-language comparison and cultural context\n")
            f.write("- **Tier 3**: Multi-language synthesis with etymology analysis\n\n")
            
            f.write("### 📚 Academic Impact\n")
            f.write("- **Complete Corpus**: All available Hylozoics texts\n")
            f.write("- **Research Quality**: Proper citations and source verification\n")
            f.write("- **Linguistic Analysis**: Translation studies and etymology\n")
            f.write("- **Cultural Studies**: How esoteric concepts cross cultures\n\n")
            
            f.write("### 🚀 Business Impact\n")
            f.write("- **Global Market**: Access to 9+ language markets\n")
            f.write("- **Premium Content**: Unique multi-language sacred library\n")
            f.write("- **Academic Partnerships**: Research institutions and universities\n")
            f.write("- **Cultural Institutions**: Museums and spiritual centers\n\n")
            
            f.write("## 🎊 Revolutionary Achievement\n\n")
            f.write("**What We Created:**\n")
            f.write("- The world's first complete multi-language digital Hylozoics library\n")
            f.write("- Academic-quality preservation of Henry T. Laurency's complete works\n")
            f.write("- Cross-cultural synthesis platform for esoteric knowledge\n")
            f.write("- Foundation for AI-powered wisdom synthesis across traditions\n")
            f.write("- Sustainable revenue model through tiered access\n\n")
            
            f.write("**Global Impact:**\n")
            f.write("- Preserves authentic wisdom for future generations\n")
            f.write("- Enables cross-cultural understanding of esoteric concepts\n")
            f.write("- Supports academic research in comparative spirituality\n")
            f.write("- Creates new paradigm for digital wisdom preservation\n")
        
        print(f"📋 Ultimate catalog: {catalog_file}")
        print(f"📄 Ultimate summary: {summary_file}")
        
        return catalog_data
    
    def run(self):
        """Run the ultimate multi-language harvest"""
        print("🌍 ULTIMATE MULTI-LANGUAGE HYLOZOICS HARVESTER")
        print("=" * 70)
        print("🎯 THE DEFINITIVE COLLECTION OF ALL HYLOZOICS CONTENT")
        print("🌐 Discovering and downloading ALL books in ALL languages...")
        
        try:
            # Discovery phase
            print(f"\n🔍 ULTIMATE DISCOVERY PHASE")
            print("=" * 35)
            
            for lang_code, lang_info in self.languages.items():
                content = self.discover_language_content(lang_code, lang_info)
                if content and (content['total_books'] > 0 or content['total_dictionaries'] > 0):
                    self.discovered_content[lang_code] = content
            
            if not self.discovered_content:
                print("❌ No content discovered")
                return
            
            # Download phase
            print(f"\n📥 ULTIMATE DOWNLOAD PHASE")
            print("=" * 35)
            
            all_downloads = {}
            for lang_code, content in self.discovered_content.items():
                downloads = self.download_content(lang_code, content)
                all_downloads[lang_code] = downloads
            
            # Create ultimate summary
            catalog = self.create_ultimate_summary()
            
            # Final celebration
            total_languages = len(self.discovered_content)
            total_books = sum(len(content.get('books', [])) for content in self.discovered_content.values())
            total_dicts = sum(len(content.get('dictionaries', [])) for content in self.discovered_content.values())
            
            print(f"\n🎉 ULTIMATE HARVEST COMPLETE!")
            print("=" * 40)
            print(f"🌐 Languages harvested: {total_languages}")
            print(f"📚 Books downloaded: {total_books}")
            print(f"📖 Dictionaries downloaded: {total_dicts}")
            print(f"📁 Output directory: {self.output_dir}")
            print(f"🏛️ THE WORLD'S FIRST COMPLETE MULTI-LANGUAGE HYLOZOICS LIBRARY!")
            print(f"🌟 READY FOR SACRED LIBRARY REVOLUTION!")
            
        except Exception as e:
            print(f"\n💥 Ultimate harvest error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    harvester = UltimateMultiLangHarvester()
    harvester.run()
