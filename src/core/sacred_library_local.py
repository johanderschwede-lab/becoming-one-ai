"""
Sacred Library Local Search
===========================
Local fallback search for Sacred Library when Supabase is unavailable
"""

import json
import re
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from loguru import logger

class LocalSacredLibrary:
    """Local Sacred Library search when Supabase is unavailable"""
    
    def __init__(self):
        self.sacred_dir = Path("sacred_library_files")
        self.quotes_dir = self.sacred_dir / "quotes"
        self.cache = {}  # Simple in-memory cache
        
    def search_quotes(self, query: str, language: Optional[str] = None, limit: int = 3) -> List[Dict[str, Any]]:
        """Search quotes locally"""
        try:
            # Extract search terms (longer words)
            words = [w.lower() for w in re.findall(r'\b\w{4,}\b', query)]
            if not words:
                words = ['life', 'development']  # Default fallback
            
            results = []
            
            # Check if quotes directory exists
            if not self.quotes_dir.exists():
                logger.warning(f"Sacred library quotes directory not found: {self.quotes_dir}")
                return []
            
            # Search through quote files
            quote_files = list(self.quotes_dir.glob("*.json"))
            
            for quote_file in quote_files:
                try:
                    # Load quote data
                    with open(quote_file, 'r', encoding='utf-8') as f:
                        quote_data = json.load(f)
                    
                    # Filter by language if specified
                    if language and quote_data.get('language', '').lower() != language.lower():
                        continue
                    
                    # Search for any of the words in the quote text
                    quote_text = quote_data.get('text', '').lower()
                    if any(word in quote_text for word in words):
                        # Format for compatibility with AI engine
                        result = {
                            'title': f"Hylozoics Quote {quote_data.get('quote_id', 'Unknown')}",
                            'content': quote_data.get('text', ''),
                            'metadata': {
                                'quote_id': quote_data.get('quote_id'),
                                'chapter': quote_data.get('chapter', 'Unknown'),
                                'language': quote_data.get('language', 'unknown'),
                                'author': quote_data.get('author', 'Henry T. Laurency'),
                                'source_book': quote_data.get('source_book', 'Hylozoics'),
                                'tradition': quote_data.get('tradition', 'Hylozoics'),
                                'verified': quote_data.get('verified', True)
                            }
                        }
                        results.append(result)
                        
                        if len(results) >= limit:
                            break
                            
                except Exception as e:
                    logger.debug(f"Error processing quote file {quote_file}: {e}")
                    continue
            
            logger.info(f"Local Sacred Library search for '{query}': found {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error in local Sacred Library search: {e}")
            return []
    
    def get_random_quotes(self, limit: int = 3) -> List[Dict[str, Any]]:
        """Get random quotes when no search terms work"""
        try:
            import random
            
            quote_files = list(self.quotes_dir.glob("*.json"))
            if not quote_files:
                return []
            
            # Select random files
            selected_files = random.sample(quote_files, min(limit, len(quote_files)))
            
            results = []
            for quote_file in selected_files:
                try:
                    with open(quote_file, 'r', encoding='utf-8') as f:
                        quote_data = json.load(f)
                    
                    result = {
                        'title': f"Hylozoics Quote {quote_data.get('quote_id', 'Unknown')}",
                        'content': quote_data.get('text', ''),
                        'metadata': {
                            'quote_id': quote_data.get('quote_id'),
                            'chapter': quote_data.get('chapter', 'Unknown'),
                            'language': quote_data.get('language', 'unknown'),
                            'author': quote_data.get('author', 'Henry T. Laurency'),
                            'source_book': quote_data.get('source_book', 'Hylozoics'),
                            'tradition': quote_data.get('tradition', 'Hylozoics'),
                            'verified': quote_data.get('verified', True)
                        }
                    }
                    results.append(result)
                    
                except Exception as e:
                    logger.debug(f"Error processing random quote file {quote_file}: {e}")
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting random quotes: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if local Sacred Library is available"""
        return self.quotes_dir.exists() and any(self.quotes_dir.glob("*.json"))

# Global instance
local_sacred_library = LocalSacredLibrary()
