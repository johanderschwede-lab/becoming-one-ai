"""
Core AI Engine for Becoming One™ Method
Integrates OpenAI and Sacred Library
"""
import os
from typing import Dict, Any, List
from openai import OpenAI
from loguru import logger

from database.operations import db

class BecomingOneAI:
    """Main AI processing engine"""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set")
            
        # Initialize OpenAI client
        self.openai_client = OpenAI(
            api_key=api_key,
            base_url="https://api.openai.com/v1",
            timeout=60.0,
            max_retries=2
        )
        
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    
    async def search_sacred_library(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Search Sacred Library for relevant quotes"""
        try:
            # Extract key terms
            words = [w for w in query.lower().split() if len(w) > 4]
            search_terms = words[:3] if words else ['life', 'development']
            
            # Search for each term
            all_quotes = []
            for term in search_terms:
                result = db.client.table('teaching_materials').select(
                    'content, title, metadata'
                ).eq(
                    'material_type', 'sacred_quote'
                ).ilike(
                    'content', f'%{term}%'
                ).limit(limit).execute()
                
                if result.data:
                    all_quotes.extend(result.data)
            
            # Remove duplicates
            seen = set()
            unique_quotes = []
            for quote in all_quotes:
                quote_id = quote['title'] + quote['content'][:50]
                if quote_id not in seen:
                    seen.add(quote_id)
                    unique_quotes.append(quote)
                    if len(unique_quotes) >= limit:
                        break
            
            return unique_quotes
            
        except Exception as e:
            logger.error(f"Error searching Sacred Library: {e}")
            return []
    
    async def process_message(
        self, 
        person_id: str,
        message: str,
        source: str,
        user_tier: str = "free"
    ) -> str:
        """Process a user message and generate response"""
        try:
            # Search Sacred Library
            sacred_quotes = await self.search_sacred_library(message, limit=2)
            
            # Build system prompt
            system_prompt = """You are an AI mentor trained in the Becoming One™ method, a transformative approach to personal growth and authentic living.

CORE MISSION: Guide this person toward discovering, integrating, and expressing their most authentic self.

RESPONSE STYLE:
- Be warm, empathetic, and genuinely curious
- Ask powerful questions that promote self-reflection
- Offer insights without being prescriptive
- Use "I wonder..." and "What if..." to invite exploration
- Balance support with gentle challenge

SACRED LIBRARY INTEGRATION:
1. If relevant quotes are available, ask permission to share them
2. Share quotes with proper citation (chapter and language)
3. Provide a vector-based summary ("Another way of saying this...")
4. Offer gentle commentary and connection to their situation"""

            # Add Sacred Library quotes if available
            if sacred_quotes:
                system_prompt += "\n\nRELEVANT TEACHINGS:\n"
                for quote in sacred_quotes:
                    system_prompt += f"\nFrom {quote['metadata'].get('chapter', 'Unknown')} ({quote['metadata'].get('language', 'unknown').upper()}):\n"
                    system_prompt += f'"{quote["content"]}"\n'
            
            # Generate response
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return """I'm experiencing a temporary issue processing your message. 

In the spirit of the Becoming One™ method, let me offer this:
Sometimes the most profound insights come from pausing and reflecting. 

What feels most important to you right now in this moment?"""