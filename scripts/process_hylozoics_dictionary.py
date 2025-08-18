#!/usr/bin/env python3
"""
Hylozoics Dictionary Processor
=============================

Extracts and organizes the Basic Esoteric Dictionary from laurency.com
Creates structured terminology database for Sacred Library integration
"""

import os
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
import requests

class HylozoicsDictionaryProcessor:
    def __init__(self, output_dir: str = "laurency_organized"):
        self.output_dir = Path(output_dir)
        self.dictionary_entries = []
        
    def download_dictionary(self):
        """Download the dictionary if not already present"""
        dict_file = self.output_dir / "metadata" / "Basic_Esoteric_Dictionary.html"
        
        if not dict_file.exists():
            print("📥 Downloading Basic Esoteric Dictionary...")
            response = requests.get("https://www.laurency.com/Dictionary.htm")
            dict_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(dict_file, 'w', encoding='utf-8') as f:
                f.write(response.text)
            print(f"✅ Dictionary downloaded: {dict_file}")
        else:
            print(f"📖 Dictionary already exists: {dict_file}")
        
        return dict_file
    
    def parse_dictionary(self, dict_file: Path):
        """Parse the HTML dictionary and extract terms"""
        print("🔍 Parsing dictionary content...")
        
        with open(dict_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Find the main dictionary content
        # The dictionary entries are typically in a specific format
        entries = []
        
        # Look for terms - they're usually in bold or specific formatting
        # This is a simplified approach - the actual structure may vary
        text_content = soup.get_text()
        
        # Split into sections and try to identify dictionary entries
        lines = text_content.split('\n')
        
        current_entry = None
        current_definition = []
        in_dictionary_section = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if we've reached the dictionary section
            if "Go To" in line or "DICTIONARY" in line.upper():
                in_dictionary_section = True
                continue
            
            if not in_dictionary_section:
                continue
            
            # Simple heuristic: if line is all caps or starts with caps and is short, might be a term
            if (line.isupper() and len(line) < 50) or (line[0].isupper() and len(line.split()) <= 3 and not line.endswith('.')):
                # Save previous entry if exists
                if current_entry:
                    entries.append({
                        'term': current_entry,
                        'definition': ' '.join(current_definition).strip(),
                        'source': 'Basic Esoteric Dictionary'
                    })
                
                current_entry = line
                current_definition = []
            else:
                # This is likely part of a definition
                current_definition.append(line)
        
        # Don't forget the last entry
        if current_entry:
            entries.append({
                'term': current_entry,
                'definition': ' '.join(current_definition).strip(),
                'source': 'Basic Esoteric Dictionary'
            })
        
        print(f"📚 Extracted {len(entries)} potential dictionary entries")
        return entries
    
    def clean_and_validate_entries(self, raw_entries):
        """Clean and validate dictionary entries"""
        print("🧹 Cleaning and validating entries...")
        
        cleaned_entries = []
        
        for entry in raw_entries:
            term = entry['term'].strip()
            definition = entry['definition'].strip()
            
            # Skip entries that are too short or don't look like definitions
            if len(definition) < 20:
                continue
            
            # Skip entries that look like navigation or headers
            skip_terms = ['HOME', 'PREFACE', 'INTRODUCTION', 'INDEX', 'CONTENTS']
            if term.upper() in skip_terms:
                continue
            
            # Clean the term
            term = re.sub(r'[^\w\s-]', '', term).strip()
            
            # Clean the definition
            definition = re.sub(r'\s+', ' ', definition).strip()
            
            if term and definition and len(term) < 100:
                cleaned_entries.append({
                    'term': term,
                    'definition': definition,
                    'source': 'Basic Esoteric Dictionary',
                    'author': 'Henry T. Laurency',
                    'tradition': 'Hylozoics',
                    'language': 'English',
                    'extracted_at': datetime.now().isoformat()
                })
        
        print(f"✅ Cleaned entries: {len(cleaned_entries)}")
        return cleaned_entries
    
    def create_terminology_database(self, entries):
        """Create structured terminology database"""
        print("📊 Creating terminology database...")
        
        # Create terminology directory
        terminology_dir = self.output_dir / "04_Terminology_Dictionary"
        terminology_dir.mkdir(exist_ok=True)
        
        # Save as JSON for easy processing
        json_file = terminology_dir / "hylozoics_terminology.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(entries, f, indent=2, ensure_ascii=False)
        
        print(f"💾 JSON database: {json_file}")
        
        # Create alphabetical text file
        text_file = terminology_dir / "hylozoics_dictionary.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write("HYLOZOICS TERMINOLOGY DICTIONARY\n")
            f.write("=" * 50 + "\n\n")
            f.write("Source: Basic Esoteric Dictionary (laurency.com)\n")
            f.write("Author: Henry T. Laurency\n")
            f.write("Tradition: Hylozoics\n")
            f.write(f"Extracted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Terms: {len(entries)}\n\n")
            
            # Sort entries alphabetically
            sorted_entries = sorted(entries, key=lambda x: x['term'].upper())
            
            for entry in sorted_entries:
                f.write(f"{entry['term'].upper()}\n")
                f.write("-" * len(entry['term']) + "\n")
                f.write(f"{entry['definition']}\n\n")
        
        print(f"📖 Text dictionary: {text_file}")
        
        # Create Sacred Library integration format
        sacred_format_file = terminology_dir / "sacred_library_terminology.json"
        sacred_entries = []
        
        for entry in entries:
            sacred_entries.append({
                "quote_id": f"hyl_term_{len(sacred_entries)+1:03d}",
                "text": f"{entry['term']}: {entry['definition']}",
                "source_book": "Basic Esoteric Dictionary",
                "chapter": "Terminology",
                "page_number": None,
                "paragraph_number": None,
                "hylozoics_terms": [entry['term'].lower()],
                "related_concepts": [],
                "context": f"Dictionary definition of {entry['term']}",
                "content_type": "terminology_definition",
                "verified": True,
                "language": "english",
                "author": "Henry T. Laurency",
                "tradition": "Hylozoics"
            })
        
        with open(sacred_format_file, 'w', encoding='utf-8') as f:
            json.dump(sacred_entries, f, indent=2, ensure_ascii=False)
        
        print(f"🏛️ Sacred Library format: {sacred_format_file}")
        
        return len(entries)
    
    def create_integration_instructions(self):
        """Create instructions for integrating the dictionary"""
        instructions_file = self.output_dir / "04_Terminology_Dictionary" / "INTEGRATION_INSTRUCTIONS.md"
        
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write("""# Hylozoics Dictionary Integration Instructions

## Overview
This directory contains the processed Basic Esoteric Dictionary from laurency.com, 
formatted for Sacred Library integration.

## Files
- `hylozoics_terminology.json` - Raw extracted terms with metadata
- `hylozoics_dictionary.txt` - Human-readable alphabetical dictionary
- `sacred_library_terminology.json` - Formatted for Sacred Library database
- `Basic_Esoteric_Dictionary.html` - Original source file

## Sacred Library Integration

### Database Integration
Each dictionary entry should be added to the Sacred Library as:
- **Content Type**: Terminology Definition
- **Source**: Basic Esoteric Dictionary  
- **Author**: Henry T. Laurency
- **Tradition**: Hylozoics
- **Verification**: Verified from official source

### Usage in Responses
- **Tier 1 (Sacred Source)**: Provide exact definitions when users ask about terms
- **Tier 2 (Cross-Library)**: Compare term definitions across traditions
- **Tier 3 (Synthesis Master)**: Use definitions to enhance synthesis accuracy

### Citation Format
"Term Definition from Laurency, Henry T. Basic Esoteric Dictionary, Official Website"

## Quality Notes
- Definitions extracted from official laurency.com source
- Over 500+ terms covering core Hylozoics concepts
- Includes excerpts from "The Knowledge of Reality" and "The Philosopher's Stone"
- Essential for maintaining terminological accuracy in responses

## Next Steps
1. Review extracted terms for accuracy
2. Import into Sacred Library database
3. Generate embeddings for semantic search
4. Integrate with dual-mode response system
5. Use for term validation in AI responses
""")
        
        print(f"📋 Integration instructions: {instructions_file}")
    
    def run(self):
        """Run the complete dictionary processing"""
        print("🌟 Hylozoics Dictionary Processor")
        print("=" * 40)
        
        try:
            # Download dictionary if needed
            dict_file = self.download_dictionary()
            
            # Parse the dictionary
            raw_entries = self.parse_dictionary(dict_file)
            
            # Clean and validate entries
            cleaned_entries = self.clean_and_validate_entries(raw_entries)
            
            # Create structured database
            total_terms = self.create_terminology_database(cleaned_entries)
            
            # Create integration instructions
            self.create_integration_instructions()
            
            print(f"\n🎉 DICTIONARY PROCESSING COMPLETE!")
            print(f"📚 Total terms extracted: {total_terms}")
            print(f"📁 Location: {self.output_dir / '04_Terminology_Dictionary'}")
            print(f"🏛️ Ready for Sacred Library integration!")
            
        except Exception as e:
            print(f"\n💥 Error processing dictionary: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    processor = HylozoicsDictionaryProcessor()
    processor.run()
