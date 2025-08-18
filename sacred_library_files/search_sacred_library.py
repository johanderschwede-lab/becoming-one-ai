#!/usr/bin/env python3
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
