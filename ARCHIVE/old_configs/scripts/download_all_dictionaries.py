#!/usr/bin/env python3
"""
Complete Multi-Language Dictionary Downloader
=============================================

Downloads Hylozoics dictionaries in all available languages
Organizes them for Sacred Library integration with proper language mapping
"""

import os
import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
from datetime import datetime
import urllib.parse

class CompleteDictionaryDownloader:
    def __init__(self, output_dir: str = "laurency_organized"):
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Known dictionary locations
        self.dictionaries = {
            'english': {
                'url': 'https://www.laurency.com/Dictionary.htm',
                'title': 'The Basic Esoteric Dictionary',
                'language_name': 'English',
                'flag': '🇬🇧',
                'is_translation': True,
                'source_language': 'Swedish'
            },
            'swedish': {
                'url': 'https://www.laurency.com/Swedish/lexikon.htm',
                'title': 'Litet esoteriskt lexikon',
                'language_name': 'Svenska (Swedish)',
                'flag': '🇸🇪',
                'is_translation': False,
                'source_language': 'Swedish'
            }
        }
        
        # Check for additional languages
        self.additional_language_paths = [
            ('german', 'https://www.laurency.com/German/', 'Deutsch'),
            ('finnish', 'https://www.laurency.com/Finnish/', 'Suomi'),
            ('italian', 'https://www.laurency.com/Italian/', 'Italiano'),
        ]
        
    def discover_additional_dictionaries(self):
        """Try to discover dictionaries in other languages"""
        print("🔍 Searching for additional language dictionaries...")
        
        for lang_code, base_url, lang_name in self.additional_language_paths:
            try:
                print(f"  🌐 Checking {lang_name}...")
                response = self.session.get(base_url, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for dictionary-related links
                    links = soup.find_all('a', href=True)
                    for link in links:
                        href = link.get('href')
                        link_text = link.get_text(strip=True).lower()
                        
                        # Check for dictionary keywords in various languages
                        dict_keywords = [
                            'dictionary', 'wörterbuch', 'sanakirja', 'dizionario',
                            'lexikon', 'ordbok', 'glossar', 'terms'
                        ]
                        
                        if any(keyword in href.lower() or keyword in link_text for keyword in dict_keywords):
                            full_url = urllib.parse.urljoin(base_url, href)
                            
                            # Verify it's actually a dictionary
                            try:
                                dict_response = self.session.get(full_url, timeout=10)
                                if dict_response.status_code == 200 and len(dict_response.text) > 5000:
                                    flag_map = {'german': '🇩🇪', 'finnish': '🇫🇮', 'italian': '🇮🇹'}
                                    
                                    self.dictionaries[lang_code] = {
                                        'url': full_url,
                                        'title': link.get_text(strip=True),
                                        'language_name': lang_name,
                                        'flag': flag_map.get(lang_code, '🌐'),
                                        'is_translation': True,
                                        'source_language': 'Swedish'
                                    }
                                    print(f"    ✅ Found: {link.get_text(strip=True)}")
                            except:
                                continue
                
            except Exception as e:
                print(f"    ❌ Error checking {lang_name}: {e}")
    
    def download_dictionary(self, lang_code: str, dict_info: dict) -> dict:
        """Download a single dictionary"""
        print(f"📥 {dict_info['flag']} Downloading {dict_info['language_name']}: {dict_info['title']}")
        
        try:
            response = self.session.get(dict_info['url'])
            response.raise_for_status()
            
            # Create language-specific directory
            lang_dir = self.output_dir / "04_Terminology_Dictionary" / "MultiLanguage" / lang_code
            lang_dir.mkdir(parents=True, exist_ok=True)
            
            # Save raw HTML
            html_file = lang_dir / f"dictionary_{lang_code}_raw.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            # Extract clean text
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get clean text
            clean_text = soup.get_text()
            lines = (line.strip() for line in clean_text.splitlines())
            clean_text = '\n'.join(line for line in lines if line)
            
            # Save clean text
            text_file = lang_dir / f"dictionary_{lang_code}_clean.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(clean_text)
            
            download_info = {
                'language': lang_code,
                'language_name': dict_info['language_name'],
                'title': dict_info['title'],
                'url': dict_info['url'],
                'flag': dict_info['flag'],
                'is_translation': dict_info['is_translation'],
                'source_language': dict_info['source_language'],
                'html_file': str(html_file),
                'text_file': str(text_file),
                'size_html': len(response.text),
                'size_text': len(clean_text),
                'downloaded_at': datetime.now().isoformat(),
                'success': True
            }
            
            print(f"    ✅ Downloaded: {len(response.text):,} chars HTML, {len(clean_text):,} chars text")
            return download_info
            
        except Exception as e:
            print(f"    ❌ Failed: {e}")
            return {
                'language': lang_code,
                'title': dict_info['title'],
                'url': dict_info['url'],
                'error': str(e),
                'success': False
            }
    
    def extract_terminology(self, download_info: dict) -> list:
        """Extract terminology from downloaded dictionary"""
        if not download_info['success']:
            return []
        
        print(f"📝 Extracting terms from {download_info['language_name']}")
        
        try:
            with open(download_info['text_file'], 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple term extraction (this would need refinement for each language)
            terms = []
            lines = content.split('\n')
            
            current_term = None
            current_definition = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Heuristic: if line is short and looks like a term (all caps or title case)
                if len(line) < 100 and (line.isupper() or (line[0].isupper() and not line.endswith('.'))):
                    # Save previous term
                    if current_term and current_definition:
                        definition_text = ' '.join(current_definition).strip()
                        if len(definition_text) > 20:  # Only meaningful definitions
                            terms.append({
                                'term': current_term,
                                'definition': definition_text,
                                'language': download_info['language'],
                                'source': download_info['title']
                            })
                    
                    current_term = line
                    current_definition = []
                else:
                    current_definition.append(line)
            
            # Don't forget the last term
            if current_term and current_definition:
                definition_text = ' '.join(current_definition).strip()
                if len(definition_text) > 20:
                    terms.append({
                        'term': current_term,
                        'definition': definition_text,
                        'language': download_info['language'],
                        'source': download_info['title']
                    })
            
            # Save terms as JSON
            terms_file = Path(download_info['text_file']).parent / f"terms_{download_info['language']}.json"
            with open(terms_file, 'w', encoding='utf-8') as f:
                json.dump(terms, f, indent=2, ensure_ascii=False)
            
            print(f"    📚 Extracted {len(terms)} terms")
            return terms
            
        except Exception as e:
            print(f"    ❌ Term extraction failed: {e}")
            return []
    
    def create_multilang_database(self, all_downloads: list):
        """Create comprehensive multi-language database"""
        print("📊 Creating multi-language terminology database...")
        
        # Collect all terms from all languages
        all_terms = []
        terms_by_language = {}
        
        for download_info in all_downloads:
            if download_info['success']:
                terms = self.extract_terminology(download_info)
                all_terms.extend(terms)
                terms_by_language[download_info['language']] = terms
        
        # Create comprehensive database
        database_dir = self.output_dir / "04_Terminology_Dictionary" / "MultiLanguage"
        
        # Complete database
        complete_db = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'total_languages': len(terms_by_language),
                'total_terms': len(all_terms),
                'source': 'laurency.com multi-language dictionaries'
            },
            'languages': {
                lang: {
                    'term_count': len(terms),
                    'download_info': next(d for d in all_downloads if d.get('language') == lang and d.get('success')),
                    'terms': terms
                }
                for lang, terms in terms_by_language.items()
            }
        }
        
        # Save complete database
        db_file = database_dir / "complete_multilang_database.json"
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(complete_db, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Complete database: {db_file}")
        
        # Create Sacred Library format
        sacred_entries = []
        entry_id = 1
        
        for lang, terms in terms_by_language.items():
            for term in terms:
                sacred_entries.append({
                    "quote_id": f"hyl_term_{lang}_{entry_id:03d}",
                    "text": f"{term['term']}: {term['definition']}",
                    "source_book": term['source'],
                    "chapter": "Terminology",
                    "language": lang,
                    "hylozoics_terms": [term['term'].lower()],
                    "content_type": "terminology_definition",
                    "verified": True,
                    "author": "Henry T. Laurency",
                    "tradition": "Hylozoics"
                })
                entry_id += 1
        
        sacred_file = database_dir / "sacred_library_multilang_terms.json"
        with open(sacred_file, 'w', encoding='utf-8') as f:
            json.dump(sacred_entries, f, indent=2, ensure_ascii=False)
        
        print(f"🏛️ Sacred Library format: {sacred_file}")
        
        return len(all_terms)
    
    def create_usage_guide(self, all_downloads: list, total_terms: int):
        """Create comprehensive usage guide"""
        guide_file = self.output_dir / "04_Terminology_Dictionary" / "MultiLanguage" / "USAGE_GUIDE.md"
        
        successful_downloads = [d for d in all_downloads if d.get('success')]
        
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write("# Multi-Language Hylozoics Dictionary Usage Guide\n\n")
            
            f.write("## Overview\n")
            f.write(f"Complete collection of Hylozoics terminology in {len(successful_downloads)} languages.\n")
            f.write(f"Total terms extracted: {total_terms}\n\n")
            
            f.write("## Available Languages\n\n")
            for download in successful_downloads:
                f.write(f"### {download['flag']} {download['language_name']}\n")
                f.write(f"- **Title**: {download['title']}\n")
                f.write(f"- **Source**: {download['url']}\n")
                f.write(f"- **Type**: {'Original' if not download['is_translation'] else 'Translation from ' + download['source_language']}\n")
                f.write(f"- **Content**: {download['size_text']:,} characters\n\n")
            
            f.write("## Sacred Library Integration\n\n")
            f.write("### Tier 1: Sacred Source\n")
            f.write("- Provide exact term definitions in user's preferred language\n")
            f.write("- Show Swedish original for authoritative definitions\n")
            f.write("- Include complete source citations\n\n")
            
            f.write("### Tier 2: Cross-Library Wisdom\n")
            f.write("- Compare term definitions across languages\n")
            f.write("- Show translation variations and cultural context\n")
            f.write("- Cross-reference with other wisdom traditions\n\n")
            
            f.write("### Tier 3: Synthesis Master\n")
            f.write("- Multi-language synthesis with cultural nuances\n")
            f.write("- Etymology and linguistic analysis\n")
            f.write("- Personality-type specific explanations in preferred language\n\n")
            
            f.write("## Language Priority\n")
            f.write("1. **Swedish**: Authoritative original definitions\n")
            f.write("2. **English**: Primary international access\n")
            f.write("3. **German**: Secondary European access\n")
            f.write("4. **Other languages**: Regional accessibility\n\n")
            
            f.write("## Implementation Notes\n")
            f.write("- Terms may have different emphasis across languages\n")
            f.write("- Some concepts are untranslatable and should be preserved in Swedish\n")
            f.write("- Cultural context is crucial for accurate understanding\n")
            f.write("- Cross-language validation helps identify translation issues\n")
        
        print(f"📋 Usage guide: {guide_file}")
    
    def run(self):
        """Run complete multi-language dictionary download"""
        print("🌍 Complete Multi-Language Dictionary Downloader")
        print("=" * 50)
        
        try:
            # Discover additional dictionaries
            self.discover_additional_dictionaries()
            
            print(f"\n📚 Found {len(self.dictionaries)} dictionaries:")
            for lang, info in self.dictionaries.items():
                print(f"  {info['flag']} {info['language_name']}: {info['title']}")
            
            # Download all dictionaries
            print(f"\n📥 Downloading all dictionaries...")
            all_downloads = []
            
            for lang_code, dict_info in self.dictionaries.items():
                download_result = self.download_dictionary(lang_code, dict_info)
                all_downloads.append(download_result)
            
            # Create multi-language database
            total_terms = self.create_multilang_database(all_downloads)
            
            # Create usage guide
            self.create_usage_guide(all_downloads, total_terms)
            
            successful = len([d for d in all_downloads if d.get('success')])
            failed = len([d for d in all_downloads if not d.get('success')])
            
            print(f"\n🎉 MULTI-LANGUAGE DOWNLOAD COMPLETE!")
            print(f"🌐 Languages: {successful} successful, {failed} failed")
            print(f"📚 Total terms extracted: {total_terms}")
            print(f"📁 Location: {self.output_dir / '04_Terminology_Dictionary' / 'MultiLanguage'}")
            print(f"🏛️ Ready for Sacred Library integration!")
            
        except Exception as e:
            print(f"\n💥 Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    downloader = CompleteDictionaryDownloader()
    downloader.run()
