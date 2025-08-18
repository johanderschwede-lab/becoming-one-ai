"""
SACRED LIBRARY INTEGRATION
Implements proper Sacred Library response sequence with permission, quotes, and commentary
"""

import os
from typing import Dict, Any, List, Optional
from openai import OpenAI
from loguru import logger
from database.operations import db


class SacredLibraryIntegration:
    """Handles Sacred Library search and response formatting"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def search_sacred_quotes(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Search Sacred Library for relevant quotes"""
        try:
            logger.info(f"Searching Sacred Library for: {query}")
            
            # Extract key spiritual concepts
            search_terms = self._extract_spiritual_concepts(query)
            all_quotes = []
            
            for term in search_terms[:3]:  # Try top 3 concepts
                logger.info(f"Searching for term: {term}")
                
                result = db.client.table('teaching_materials').select(
                    'material_id, content, title, metadata'
                ).eq(
                    'material_type', 'sacred_quote'
                ).ilike(
                    'content', f'%{term}%'
                ).limit(limit).execute()
                
                if result.data:
                    logger.info(f"Found {len(result.data)} quotes for term: {term}")
                    all_quotes.extend(result.data)
                else:
                    logger.info(f"No quotes found for term: {term}")
            
            # Remove duplicates
            seen = set()
            unique_quotes = []
            for quote in all_quotes:
                quote_id = quote['material_id']
                if quote_id not in seen:
                    seen.add(quote_id)
                    unique_quotes.append(quote)
                    if len(unique_quotes) >= limit:
                        break
            
            logger.info(f"Returning {len(unique_quotes)} unique Sacred Library quotes")
            return unique_quotes
            
        except Exception as e:
            logger.error(f"Error searching Sacred Library: {e}")
            return []
    
    def _extract_spiritual_concepts(self, message: str) -> List[str]:
        """Extract spiritual concepts from user message for better search"""
        spiritual_concepts = [
            'consciousness', 'awareness', 'meditation', 'development', 'evolution',
            'knowledge', 'wisdom', 'understanding', 'reality', 'truth', 'purpose',
            'meaning', 'growth', 'learning', 'experience', 'mind', 'thinking',
            'emotion', 'feeling', 'love', 'life', 'death', 'soul', 'spirit',
            'energy', 'power', 'will', 'harmony', 'peace', 'incarnation',
            'reincarnation', 'cosmic', 'universe', 'law', 'order'
        ]
        
        message_lower = message.lower()
        found_terms = []
        
        # Find spiritual concepts in the message
        for concept in spiritual_concepts:
            if concept in message_lower:
                found_terms.append(concept)
        
        # If no spiritual concepts found, try key words
        if not found_terms:
            words = message_lower.split()
            meaningful_words = [w for w in words if len(w) > 4 and w not in 
                             ['that', 'this', 'with', 'from', 'they', 'have', 'been', 'were']]
            found_terms.extend(meaningful_words[:3])
        
        return found_terms if found_terms else ['life', 'development']
    
    async def create_sacred_response(
        self, 
        user_message: str, 
        sacred_quotes: List[Dict[str, Any]],
        base_response: str
    ) -> str:
        """Create response following the preferred sequence"""
        
        if not sacred_quotes:
            return base_response
        
        # Step 1: Ask permission to share quotes
        permission_request = "I found some relevant teachings from Henry T. Laurency's Hylozoics that relate to your question. Would you like me to share the authentic quotes along with a summary?"
        
        # Step 2: Format authentic quotes with sources
        quotes_section = "\n\n🏛️ **AUTHENTIC HYLOZOICS TEACHINGS:**\n\n"
        
        for i, quote in enumerate(sacred_quotes, 1):
            content = quote['content']
            chapter = quote['metadata'].get('chapter', 'Unknown source')
            language = quote['metadata'].get('language', 'unknown')
            book = quote['metadata'].get('book', 'Unknown book')
            
            quotes_section += f"**{i}. From {chapter} ({language.upper()}):**\n"
            quotes_section += f'"{content}"\n\n'
        
        # Step 3: Create vector-based summary (zero hallucination)
        try:
            summary_prompt = f"""Based ONLY on these authentic Hylozoics quotes, create a brief summary that captures the essence without adding any information not present in the quotes:

QUOTES:
{chr(10).join([f'"{q["content"]}"' for q in sacred_quotes])}

USER QUESTION: {user_message}

Provide a summary that:
1. Uses ONLY information from the quotes above
2. Starts with "Another way of expressing this..." or "Hylozoics describes this as..." or "If expressed differently, Laurency says that..."
3. Does not add any interpretation beyond what's explicitly stated
4. Keeps it to 2-3 sentences maximum

Summary:"""

            summary_response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": summary_prompt}],
                temperature=0.1,  # Very low temperature for accuracy
                max_tokens=200
            )
            
            vector_summary = summary_response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error creating vector summary: {e}")
            vector_summary = "Another way of expressing this: The Hylozoics teachings provide specific guidance on this topic as shown in the quotes above."
        
        # Step 4: Soft rephrasing/commentary
        commentary_section = f"\n\n💭 **PRACTICAL APPLICATION:**\n{vector_summary}\n\nHow does this perspective resonate with your current experience?"
        
        # Combine all sections
        full_response = (
            base_response + 
            quotes_section + 
            commentary_section
        )
        
        return full_response
    
    async def should_include_sacred_library(self, message: str) -> bool:
        """Determine if Sacred Library should be included based on message content"""
        spiritual_indicators = [
            'laurency', 'hylozoics', 'consciousness', 'development', 'meditation',
            'spiritual', 'evolution', 'wisdom', 'understanding', 'reality',
            'truth', 'purpose', 'meaning', 'soul', 'spirit', 'incarnation'
        ]
        
        message_lower = message.lower()
        return any(indicator in message_lower for indicator in spiritual_indicators)
