#!/usr/bin/env python3
"""
Complete Multi-Language Hylozoics Harvester
==========================================

Discovers and downloads ALL books in ALL 9 languages from laurency.com
Uses the navigation menu structure to find all content systematically
"""

import requests
from bs4 import BeautifulSoup
import urllib.parse
from pathlib import Path
import json
import os
from datetime import datetime
import time

class CompleteMultiLangHarvester:
    def __init__(self, output_dir: str = "laurency_complete"):
        self.base_url = "https://www.laurency.com"
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Language configurations based on the navigation menu
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
        """Discover all content for a specific language"""
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
            
            # Find all option elements with book links
            options = soup.find_all('option', value=True)
            
            books = []
            dictionaries = []
            
            for option in options:
                value = option.get('value')
                text = option.get_text(strip=True)
                
                if not value or not text or value in ['main.htm', '../index.html']:
                    continue
                
                # Skip navigation elements
                if any(skip in text.lower() for skip in ['language', 'books on', 'further info', '---', '- - -']):
                    continue
                
                # Check if it's a dictionary
                if any(dict_word in text.lower() for dict_word in ['dictionary', 'lexikon', 'ordbok']):
                    full_url = urllib.parse.urljoin(nav_url, value)
                    dictionaries.append({
                        'title': text,
                        'url': full_url,
                        'type': 'dictionary'
                    })
                    print(f"  📖 Dictionary: {text}")
                    continue
                
                # Check if it's a book table of contents
                if any(book_word in text.lower() for book_word in ['knowledge', 'philosopher', 'way of', 'explanation']):
                    # This is a table of contents page - explore it for PDFs
                    toc_url = urllib.parse.urljoin(nav_url, value)
                    book_pdfs = self.discover_book_pdfs(toc_url, text, lang_info['path'])
                    if book_pdfs:
                        books.extend(book_pdfs)
                        print(f"  📚 Book Series: {text} ({len(book_pdfs)} chapters)")
            
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
                        chapter_title = href.split('/')[-1].replace('.pdf', '').replace('_', ' ').title()
                    
                    pdf_links.append({
                        'title': chapter_title,
                        'series': series_title,
                        'url': full_url,
                        'filename': href.split('/')[-1],
                        'type': 'pdf_chapter'
                    })
            
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
                series_dir = books_dir / series.replace(' ', '_').replace('/', '_')
                series_dir.mkdir(exist_ok=True)
                
                print(f"  📚 Downloading {series} ({len(books)} chapters)")
                
                for book in books:
                    try:
                        print(f"    📄 {book['title']}")
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
                        
                        # Small delay to be respectful
                        time.sleep(0.5)
                        
                    except Exception as e:
                        print(f"    ❌ Failed to download {book['title']}: {e}")
        
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
                    print(f"    ❌ Failed to download {dict_item['title']}: {e}")
        
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
    
    def create_master_catalog(self):
        """Create comprehensive catalog of all content"""
        print(f"\n📊 Creating master catalog...")
        
        catalog_data = {
            'harvest_date': datetime.now().isoformat(),
            'total_languages': len(self.discovered_content),
            'languages': {}
        }
        
        total_books = 0
        total_dictionaries = 0
        
        for lang_code, content in self.discovered_content.items():
            if content:
                lang_info = content['language_info']
                books = content.get('books', [])
                dicts = content.get('dictionaries', [])
                
                catalog_data['languages'][lang_code] = {
                    'name': lang_info['name'],
                    'flag': lang_info['flag'],
                    'is_original': lang_info['is_original'],
                    'books_count': len(books),
                    'dictionaries_count': len(dicts),
                    'books': books,
                    'dictionaries': dicts
                }
                
                total_books += len(books)
                total_dictionaries += len(dicts)
        
        catalog_data['total_books'] = total_books
        catalog_data['total_dictionaries'] = total_dictionaries
        
        # Save master catalog
        catalog_file = self.output_dir / "MASTER_CATALOG.json"
        with open(catalog_file, 'w', encoding='utf-8') as f:
            json.dump(catalog_data, f, indent=2, ensure_ascii=False)
        
        # Create readable summary
        summary_file = self.output_dir / "COMPLETE_HARVEST_SUMMARY.md"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# 🌍 Complete Multi-Language Hylozoics Harvest\n\n")
            f.write(f"**Harvest Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"**Total Languages**: {len(self.discovered_content)}\n")
            f.write(f"**Total Books**: {total_books}\n")
            f.write(f"**Total Dictionaries**: {total_dictionaries}\n\n")
            
            f.write("## 🗂️ Language Breakdown\n\n")
            
            for lang_code, content in catalog_data['languages'].items():
                f.write(f"### {content['flag']} {content['name']}\n")
                f.write(f"- **Books**: {content['books_count']}\n")
                f.write(f"- **Dictionaries**: {content['dictionaries_count']}\n")
                f.write(f"- **Original Language**: {'Yes' if content['is_original'] else 'No'}\n\n")
                
                if content['books']:
                    # Group by series
                    series_groups = {}
                    for book in content['books']:
                        series = book['series']
                        if series not in series_groups:
                            series_groups[series] = []
                        series_groups[series].append(book)
                    
                    f.write("#### 📚 Book Series:\n")
                    for series, books in series_groups.items():
                        f.write(f"- **{series}**: {len(books)} chapters\n")
                    f.write("\n")
            
            f.write("## 🏛️ Sacred Library Impact\n\n")
            f.write("This complete harvest enables:\n")
            f.write("- **Multi-language authenticity** with Swedish originals\n")
            f.write("- **Complete cultural context** across 9+ languages\n")
            f.write("- **Translation validation** for accuracy verification\n")
            f.write("- **Global accessibility** in user's preferred language\n")
            f.write("- **Academic research** with complete corpus\n")
            f.write("- **Cross-cultural synthesis** for deeper understanding\n\n")
            
            f.write("## 🎯 Next Steps\n\n")
            f.write("1. **Text Extraction** - Convert all PDFs to searchable text\n")
            f.write("2. **Sacred Library Upload** - Import with proper citations\n")
            f.write("3. **Multi-language Database** - Cross-reference system\n")
            f.write("4. **Quality Assurance** - Verify translations and accuracy\n")
            f.write("5. **Tiered Integration** - Deploy subscription-based access\n")
        
        print(f"📋 Master catalog: {catalog_file}")
        print(f"📄 Summary: {summary_file}")
        
        return catalog_data
    
    def run(self):
        """Run complete multi-language harvest"""
        print("🌍 COMPLETE MULTI-LANGUAGE HYLOZOICS HARVESTER")
        print("=" * 70)
        print("🎯 Discovering and downloading ALL books in ALL languages...")
        
        try:
            # Discovery phase
            print(f"\n🔍 DISCOVERY PHASE")
            print("=" * 30)
            
            for lang_code, lang_info in self.languages.items():
                content = self.discover_language_content(lang_code, lang_info)
                if content and (content['total_books'] > 0 or content['total_dictionaries'] > 0):
                    self.discovered_content[lang_code] = content
            
            if not self.discovered_content:
                print("❌ No content discovered")
                return
            
            # Download phase
            print(f"\n📥 DOWNLOAD PHASE")
            print("=" * 30)
            
            all_downloads = {}
            for lang_code, content in self.discovered_content.items():
                downloads = self.download_content(lang_code, content)
                all_downloads[lang_code] = downloads
            
            # Create master catalog
            catalog = self.create_master_catalog()
            
            # Final summary
            total_languages = len(self.discovered_content)
            total_books = sum(len(content.get('books', [])) for content in self.discovered_content.values())
            total_dicts = sum(len(content.get('dictionaries', [])) for content in self.discovered_content.values())
            
            print(f"\n🎉 HARVEST COMPLETE!")
            print("=" * 30)
            print(f"🌐 Languages harvested: {total_languages}")
            print(f"📚 Books downloaded: {total_books}")
            print(f"📖 Dictionaries downloaded: {total_dicts}")
            print(f"📁 Output directory: {self.output_dir}")
            print(f"🏛️ Ready for Sacred Library integration!")
            
        except Exception as e:
            print(f"\n💥 Harvest error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    harvester = CompleteMultiLangHarvester()
    harvester.run()
