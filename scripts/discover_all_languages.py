#!/usr/bin/env python3
"""
Complete Multi-Language Hylozoics Discovery
==========================================

Discovers ALL languages and ALL books available on laurency.com
Explores left navigation menus systematically
"""

import requests
from bs4 import BeautifulSoup
import urllib.parse
from pathlib import Path
import json
from datetime import datetime

class CompleteLanguageDiscovery:
    def __init__(self):
        self.base_url = "https://www.laurency.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # All possible language paths to explore
        self.language_paths = [
            ('english', '', 'English', '🇬🇧'),
            ('swedish', 'Swedish/', 'Svenska', '🇸🇪'),
            ('german', 'German/', 'Deutsch', '🇩🇪'),
            ('french', 'French/', 'Français', '🇫🇷'),
            ('spanish', 'Spanish/', 'Español', '🇪🇸'),
            ('italian', 'Italian/', 'Italiano', '🇮🇹'),
            ('finnish', 'Finnish/', 'Suomi', '🇫🇮'),
            ('dutch', 'Dutch/', 'Nederlands', '🇳🇱'),
            ('portuguese', 'Portuguese/', 'Português', '🇵🇹'),
            ('russian', 'Russian/', 'Русский', '🇷🇺'),
            ('norwegian', 'Norwegian/', 'Norsk', '🇳🇴'),
            ('danish', 'Danish/', 'Dansk', '🇩🇰')
        ]
        
        self.discovered_languages = {}
        
    def explore_language_section(self, lang_code, path, lang_name, flag):
        """Explore a specific language section"""
        print(f"\n{flag} Exploring {lang_name} ({lang_code})")
        print("=" * 50)
        
        try:
            # First, check if the language section exists
            section_url = f"{self.base_url}/{path}"
            response = self.session.get(section_url, timeout=15)
            
            if response.status_code != 200:
                print(f"  ❌ Language section not found: {response.status_code}")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for frameset structure
            framesets = soup.find_all('frameset')
            frames = soup.find_all('frame')
            
            if frames:
                print(f"  🖼️  Frame-based site detected")
                # Find navigation frame
                nav_frame = None
                main_frame = None
                
                for frame in frames:
                    src = frame.get('src', '')
                    name = frame.get('name', '')
                    
                    if 'side' in src.lower() or 'nav' in src.lower() or 'menu' in src.lower():
                        nav_frame = src
                        print(f"    📋 Navigation frame: {src}")
                    elif 'main' in src.lower():
                        main_frame = src
                        print(f"    📄 Main frame: {src}")
                
                # Get the navigation content
                if nav_frame:
                    nav_url = urllib.parse.urljoin(section_url, nav_frame)
                    return self.explore_navigation_menu(lang_code, nav_url, lang_name, flag, section_url)
            
            # If not frame-based, look for direct navigation
            else:
                print(f"  📄 Direct HTML site")
                return self.explore_direct_navigation(lang_code, section_url, lang_name, flag)
                
        except Exception as e:
            print(f"  💥 Error exploring {lang_name}: {e}")
            return None
    
    def explore_navigation_menu(self, lang_code, nav_url, lang_name, flag, base_url):
        """Explore the navigation menu to find all books"""
        print(f"  🔍 Analyzing navigation menu: {nav_url}")
        
        try:
            response = self.session.get(nav_url, timeout=10)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links that could be books
            links = soup.find_all('a', href=True)
            books = []
            dictionaries = []
            
            for link in links:
                href = link.get('href')
                text = link.get_text(strip=True)
                
                if not href or not text:
                    continue
                
                # Skip navigation elements
                if any(skip in text.lower() for skip in ['home', 'start', 'index', 'back', 'menu']):
                    continue
                
                full_url = urllib.parse.urljoin(nav_url, href)
                
                # Categorize links
                if any(dict_word in text.lower() for dict_word in ['dictionary', 'lexikon', 'ordbok', 'wörterbuch', 'dictionnaire', 'dizionario']):
                    dictionaries.append({
                        'title': text,
                        'url': full_url,
                        'type': 'dictionary'
                    })
                    print(f"    📖 Dictionary: {text}")
                
                elif href.lower().endswith('.pdf'):
                    books.append({
                        'title': text,
                        'url': full_url,
                        'type': 'pdf_book',
                        'filename': href.split('/')[-1]
                    })
                    print(f"    📚 PDF Book: {text}")
                
                elif any(book_indicator in text.lower() for book_indicator in ['knowledge', 'philosophy', 'stone', 'explanation', 'volume', 'chapter', 'kunskap', 'filosofi']):
                    # This might be a book section - explore further
                    book_info = self.explore_potential_book_section(full_url, text, base_url)
                    if book_info:
                        books.extend(book_info)
            
            language_data = {
                'language_code': lang_code,
                'language_name': lang_name,
                'flag': flag,
                'base_url': base_url,
                'navigation_url': nav_url,
                'books': books,
                'dictionaries': dictionaries,
                'total_items': len(books) + len(dictionaries)
            }
            
            print(f"  📊 Found: {len(books)} books, {len(dictionaries)} dictionaries")
            return language_data
            
        except Exception as e:
            print(f"  💥 Error in navigation analysis: {e}")
            return None
    
    def explore_potential_book_section(self, url, title, base_url):
        """Explore a potential book section to find PDFs"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            books = []
            
            # Look for PDF links
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                if href and href.lower().endswith('.pdf'):
                    full_url = urllib.parse.urljoin(url, href)
                    books.append({
                        'title': link.get_text(strip=True) or href.split('/')[-1],
                        'url': full_url,
                        'type': 'pdf_book',
                        'filename': href.split('/')[-1],
                        'section': title
                    })
            
            return books
            
        except:
            return []
    
    def explore_direct_navigation(self, lang_code, url, lang_name, flag):
        """Explore direct HTML navigation"""
        print(f"  🔍 Analyzing direct navigation")
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            links = soup.find_all('a', href=True)
            books = []
            dictionaries = []
            
            for link in links:
                href = link.get('href')
                text = link.get_text(strip=True)
                
                if href and href.lower().endswith('.pdf'):
                    full_url = urllib.parse.urljoin(url, href)
                    books.append({
                        'title': text or href.split('/')[-1],
                        'url': full_url,
                        'type': 'pdf_book',
                        'filename': href.split('/')[-1]
                    })
            
            return {
                'language_code': lang_code,
                'language_name': lang_name,
                'flag': flag,
                'base_url': url,
                'books': books,
                'dictionaries': dictionaries,
                'total_items': len(books) + len(dictionaries)
            }
            
        except Exception as e:
            print(f"  💥 Error in direct navigation: {e}")
            return None
    
    def discover_all_languages(self):
        """Discover all available languages and their content"""
        print("🌍 COMPLETE MULTI-LANGUAGE DISCOVERY")
        print("🔍 Searching for ALL 9+ languages...")
        print("=" * 60)
        
        discovered = {}
        
        for lang_code, path, lang_name, flag in self.language_paths:
            result = self.explore_language_section(lang_code, path, lang_name, flag)
            if result and result['total_items'] > 0:
                discovered[lang_code] = result
        
        self.discovered_languages = discovered
        return discovered
    
    def create_complete_summary(self):
        """Create comprehensive summary of all discoveries"""
        print(f"\n📊 DISCOVERY SUMMARY")
        print("=" * 60)
        
        total_languages = len(self.discovered_languages)
        total_books = sum(len(lang['books']) for lang in self.discovered_languages.values())
        total_dictionaries = sum(len(lang['dictionaries']) for lang in self.discovered_languages.values())
        
        print(f"🌐 Languages found: {total_languages}")
        print(f"📚 Total books: {total_books}")
        print(f"📖 Total dictionaries: {total_dictionaries}")
        print(f"📄 Total items: {total_books + total_dictionaries}")
        
        # Language breakdown
        print(f"\n🗂️  LANGUAGE BREAKDOWN:")
        for lang_code, data in self.discovered_languages.items():
            print(f"  {data['flag']} {data['language_name']}: {len(data['books'])} books, {len(data['dictionaries'])} dictionaries")
        
        # Save complete discovery data
        output_dir = Path("laurency_organized") / "00_Discovery_Data"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        discovery_file = output_dir / "complete_language_discovery.json"
        with open(discovery_file, 'w', encoding='utf-8') as f:
            json.dump({
                'discovery_date': datetime.now().isoformat(),
                'total_languages': total_languages,
                'total_books': total_books,
                'total_dictionaries': total_dictionaries,
                'languages': self.discovered_languages
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Complete discovery saved: {discovery_file}")
        
        # Create download plan
        self.create_download_plan()
        
        return self.discovered_languages
    
    def create_download_plan(self):
        """Create comprehensive download plan"""
        plan_file = Path("laurency_organized") / "00_Discovery_Data" / "COMPLETE_DOWNLOAD_PLAN.md"
        
        with open(plan_file, 'w', encoding='utf-8') as f:
            f.write("# 🌍 Complete Multi-Language Hylozoics Download Plan\n\n")
            f.write(f"**Discovery Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"**Total Languages**: {len(self.discovered_languages)}\n")
            
            total_books = sum(len(lang['books']) for lang in self.discovered_languages.values())
            total_dicts = sum(len(lang['dictionaries']) for lang in self.discovered_languages.values())
            
            f.write(f"**Total Books**: {total_books}\n")
            f.write(f"**Total Dictionaries**: {total_dicts}\n\n")
            
            f.write("## 📋 Languages and Content\n\n")
            
            for lang_code, data in self.discovered_languages.items():
                f.write(f"### {data['flag']} {data['language_name']}\n")
                f.write(f"- **Books**: {len(data['books'])}\n")
                f.write(f"- **Dictionaries**: {len(data['dictionaries'])}\n")
                f.write(f"- **Base URL**: {data['base_url']}\n\n")
                
                if data['books']:
                    f.write("#### 📚 Books:\n")
                    for book in data['books']:
                        f.write(f"- {book['title']} - `{book['filename']}`\n")
                    f.write("\n")
                
                if data['dictionaries']:
                    f.write("#### 📖 Dictionaries:\n")
                    for dict_item in data['dictionaries']:
                        f.write(f"- {dict_item['title']}\n")
                    f.write("\n")
            
            f.write("## 🚀 Next Steps\n\n")
            f.write("1. **Download All Content** - Use automated scripts to download all books and dictionaries\n")
            f.write("2. **Organize by Language** - Create structured directories for each language\n")
            f.write("3. **Extract Text Content** - Convert PDFs to text for Sacred Library\n")
            f.write("4. **Create Multi-Language Database** - Build cross-language reference system\n")
            f.write("5. **Sacred Library Integration** - Upload all content with proper citations\n\n")
            
            f.write("## 🎯 Sacred Library Impact\n\n")
            f.write("This complete collection will enable:\n")
            f.write("- **Multi-language authenticity** - Original Swedish + 8 translations\n")
            f.write("- **Cultural context preservation** - How concepts translate across cultures\n")
            f.write("- **Translation validation** - Compare versions for accuracy\n")
            f.write("- **Global accessibility** - Users can access content in their preferred language\n")
            f.write("- **Academic research** - Complete corpus for scholarly analysis\n")
        
        print(f"📋 Download plan created: {plan_file}")
    
    def run(self):
        """Run complete discovery process"""
        try:
            discovered = self.discover_all_languages()
            
            if not discovered:
                print("❌ No languages discovered")
                return
            
            self.create_complete_summary()
            
            print(f"\n🎉 COMPLETE DISCOVERY FINISHED!")
            print(f"🌐 Ready to download content from {len(discovered)} languages")
            print(f"📁 Discovery data saved in: laurency_organized/00_Discovery_Data/")
            
        except Exception as e:
            print(f"\n💥 Discovery error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    discovery = CompleteLanguageDiscovery()
    discovery.run()
