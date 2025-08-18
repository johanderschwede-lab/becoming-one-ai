#!/usr/bin/env python3
"""
Multi-Language Dictionary Discovery
==================================

Discovers and downloads Hylozoics dictionaries in all available languages
"""

import requests
from bs4 import BeautifulSoup
import urllib.parse
from pathlib import Path

class MultiLanguageDictionaryDiscovery:
    def __init__(self):
        self.base_url = "https://www.laurency.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.language_sections = {
            'english': ['', 'english/', 'English/'],
            'swedish': ['Swedish/', 'svenska/', 'Svensk/'],
            'german': ['German/', 'Deutsch/', 'german/'],
            'finnish': ['Finnish/', 'Suomi/'],
            'italian': ['Italian/', 'Italiano/'],
            'french': ['French/', 'Francais/'],
            'spanish': ['Spanish/', 'Espanol/']
        }
        
        self.dictionary_keywords = [
            'dictionary', 'Dictionary', 'DICTIONARY',
            'ordbok', 'Ordbok', 'ORDBOK',  # Swedish
            'wörterbuch', 'Wörterbuch', 'WÖRTERBUCH',  # German
            'sanakirja', 'Sanakirja',  # Finnish
            'dizionario', 'Dizionario',  # Italian
            'dictionnaire', 'Dictionnaire',  # French
            'diccionario', 'Diccionario'  # Spanish
        ]
    
    def discover_dictionaries(self):
        """Discover dictionaries in all languages"""
        print("🔍 Discovering dictionaries in all languages...")
        
        found_dictionaries = {}
        
        # Check main dictionary (already known)
        found_dictionaries['english'] = [{
            'url': f"{self.base_url}/Dictionary.htm",
            'title': 'The Basic Esoteric Dictionary',
            'type': 'main_dictionary'
        }]
        
        # Explore language sections
        for language, paths in self.language_sections.items():
            print(f"\n🌐 Checking {language}...")
            lang_dictionaries = []
            
            for path in paths:
                section_url = f"{self.base_url}/{path}"
                try:
                    print(f"  🔍 Exploring: {section_url}")
                    response = self.session.get(section_url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for dictionary links
                        links = soup.find_all('a', href=True)
                        for link in links:
                            href = link.get('href')
                            link_text = link.get_text(strip=True)
                            
                            # Check if this looks like a dictionary link
                            if any(keyword in href or keyword in link_text for keyword in self.dictionary_keywords):
                                full_url = urllib.parse.urljoin(section_url, href)
                                lang_dictionaries.append({
                                    'url': full_url,
                                    'title': link_text,
                                    'type': 'dictionary_link',
                                    'found_in': section_url
                                })
                                print(f"    📚 Found: {link_text} -> {href}")
                        
                        # Also look for any files that might be dictionaries
                        for link in links:
                            href = link.get('href')
                            if href and (href.lower().endswith('.htm') or href.lower().endswith('.html')):
                                link_text = link.get_text(strip=True).lower()
                                if any(keyword.lower() in link_text for keyword in self.dictionary_keywords):
                                    full_url = urllib.parse.urljoin(section_url, href)
                                    if full_url not in [d['url'] for d in lang_dictionaries]:
                                        lang_dictionaries.append({
                                            'url': full_url,
                                            'title': link.get_text(strip=True),
                                            'type': 'potential_dictionary',
                                            'found_in': section_url
                                        })
                                        print(f"    📖 Potential: {link.get_text(strip=True)} -> {href}")
                
                except Exception as e:
                    print(f"    ❌ Error checking {section_url}: {e}")
            
            if lang_dictionaries:
                found_dictionaries[language] = lang_dictionaries
        
        return found_dictionaries
    
    def verify_dictionaries(self, found_dictionaries):
        """Verify that discovered links are actually dictionaries"""
        print("\n🔍 Verifying discovered dictionaries...")
        
        verified_dictionaries = {}
        
        for language, dictionaries in found_dictionaries.items():
            verified_dicts = []
            
            for dict_info in dictionaries:
                try:
                    print(f"  🔍 Verifying {language}: {dict_info['title']}")
                    response = self.session.get(dict_info['url'], timeout=10)
                    
                    if response.status_code == 200:
                        # Check if content looks like a dictionary
                        content = response.text.lower()
                        
                        # Look for dictionary indicators
                        dictionary_indicators = [
                            'dictionary', 'ordbok', 'wörterbuch', 'sanakirja',
                            'dizionario', 'dictionnaire', 'diccionario',
                            'esoteric', 'hylozoic', 'laurency',
                            'definition', 'term', 'concept'
                        ]
                        
                        indicator_count = sum(1 for indicator in dictionary_indicators if indicator in content)
                        
                        if indicator_count >= 3:  # At least 3 indicators
                            dict_info['verified'] = True
                            dict_info['content_length'] = len(response.text)
                            verified_dicts.append(dict_info)
                            print(f"    ✅ Verified: {dict_info['title']} ({len(response.text):,} chars)")
                        else:
                            print(f"    ❌ Not a dictionary: {dict_info['title']}")
                    else:
                        print(f"    ❌ Not accessible: {dict_info['title']}")
                
                except Exception as e:
                    print(f"    ❌ Error verifying {dict_info['title']}: {e}")
            
            if verified_dicts:
                verified_dictionaries[language] = verified_dicts
        
        return verified_dictionaries
    
    def download_all_dictionaries(self, verified_dictionaries, output_dir="laurency_organized"):
        """Download all verified dictionaries"""
        print("\n📥 Downloading all verified dictionaries...")
        
        output_path = Path(output_dir) / "04_Terminology_Dictionary" / "MultiLanguage"
        output_path.mkdir(parents=True, exist_ok=True)
        
        downloaded_files = []
        
        for language, dictionaries in verified_dictionaries.items():
            lang_dir = output_path / language
            lang_dir.mkdir(exist_ok=True)
            
            for dict_info in dictionaries:
                try:
                    print(f"  📥 Downloading {language}: {dict_info['title']}")
                    
                    response = self.session.get(dict_info['url'])
                    response.raise_for_status()
                    
                    # Create filename
                    filename = f"dictionary_{language}.html"
                    if len(dictionaries) > 1:
                        # Multiple dictionaries in same language
                        safe_title = "".join(c for c in dict_info['title'] if c.isalnum() or c in (' ', '-', '_')).strip()
                        safe_title = safe_title.replace(' ', '_')[:50]
                        filename = f"dictionary_{language}_{safe_title}.html"
                    
                    file_path = lang_dir / filename
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    
                    downloaded_files.append({
                        'language': language,
                        'title': dict_info['title'],
                        'url': dict_info['url'],
                        'file_path': str(file_path),
                        'size': len(response.text)
                    })
                    
                    print(f"    ✅ Downloaded: {filename} ({len(response.text):,} chars)")
                
                except Exception as e:
                    print(f"    ❌ Error downloading {dict_info['title']}: {e}")
        
        return downloaded_files
    
    def create_multilang_summary(self, downloaded_files, output_dir="laurency_organized"):
        """Create summary of all downloaded dictionaries"""
        summary_file = Path(output_dir) / "04_Terminology_Dictionary" / "MultiLanguage" / "MULTILANG_SUMMARY.md"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("# Multi-Language Hylozoics Dictionaries\n\n")
            f.write("Complete collection of Hylozoics terminology dictionaries in all available languages.\n\n")
            
            f.write("## Available Languages\n\n")
            
            by_language = {}
            for file_info in downloaded_files:
                lang = file_info['language']
                if lang not in by_language:
                    by_language[lang] = []
                by_language[lang].append(file_info)
            
            for language, files in by_language.items():
                f.write(f"### {language.title()}\n")
                for file_info in files:
                    f.write(f"- **{file_info['title']}**\n")
                    f.write(f"  - File: `{Path(file_info['file_path']).name}`\n")
                    f.write(f"  - Size: {file_info['size']:,} characters\n")
                    f.write(f"  - Source: {file_info['url']}\n\n")
            
            f.write("## Sacred Library Integration\n\n")
            f.write("Each dictionary should be processed to:\n")
            f.write("1. Extract terminology definitions\n")
            f.write("2. Create language-specific terminology databases\n")
            f.write("3. Map equivalent terms across languages\n")
            f.write("4. Integrate with multi-language Sacred Library system\n\n")
            
            f.write("## Translation Quality\n\n")
            f.write("- **Swedish**: Original authoritative source\n")
            f.write("- **English**: Primary translation for international access\n")
            f.write("- **German**: Secondary translation\n")
            f.write("- **Other languages**: Additional accessibility\n\n")
            
            f.write("## Usage in Tiered System\n\n")
            f.write("- **Tier 1**: Single-language term definitions\n")
            f.write("- **Tier 2**: Cross-language term comparisons\n")
            f.write("- **Tier 3**: Multi-language synthesis with cultural context\n")
        
        print(f"📋 Summary created: {summary_file}")
    
    def run(self):
        """Run complete multi-language dictionary discovery"""
        print("🌍 Multi-Language Dictionary Discovery")
        print("=" * 40)
        
        try:
            # Discover dictionaries
            found_dictionaries = self.discover_dictionaries()
            
            if not any(found_dictionaries.values()):
                print("❌ No dictionaries found")
                return
            
            # Verify dictionaries
            verified_dictionaries = self.verify_dictionaries(found_dictionaries)
            
            # Download all verified dictionaries
            downloaded_files = self.download_all_dictionaries(verified_dictionaries)
            
            # Create summary
            self.create_multilang_summary(downloaded_files)
            
            print(f"\n🎉 MULTI-LANGUAGE DISCOVERY COMPLETE!")
            print(f"🌐 Languages found: {len(verified_dictionaries)}")
            print(f"📚 Dictionaries downloaded: {len(downloaded_files)}")
            print(f"📁 Location: laurency_organized/04_Terminology_Dictionary/MultiLanguage/")
            
        except Exception as e:
            print(f"\n💥 Error in discovery: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    discovery = MultiLanguageDictionaryDiscovery()
    discovery.run()
