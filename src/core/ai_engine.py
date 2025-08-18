"""
Core AI Engine for Becoming One™ Method
Integrates OpenAI, Sacred Library, and asynchronous personality analysis
"""
import os
import asyncio
from typing import Dict, Any, List, Optional
from openai import OpenAI
from loguru import logger
import uuid
from datetime import datetime

from database.operations import db
from core.personality_analyzer import BecomingOnePersonalityAnalyzer
from core.personality_synthesis_model import SynthesisPersonalityProfile
from core.sacred_library_local import local_sacred_library

class BecomingOneAI:
    """Main AI processing engine with async analysis"""
    
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
        
        self.personality_analyzer = BecomingOnePersonalityAnalyzer()
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        
        # Queue for background analysis
        self.analysis_queue = asyncio.Queue()
        self.background_task = None
        
        # Start background analysis task (only if not in test mode and event loop is running)
        if not os.getenv("TESTING_MODE"):
            try:
                loop = asyncio.get_running_loop()
                self.background_task = loop.create_task(self._process_analysis_queue())
            except RuntimeError:
                # No event loop running, skip background analysis
                logger.warning("No event loop running, background analysis disabled")
                self.background_task = None
    
    async def search_sacred_library(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Search Sacred Library for relevant quotes"""
        try:
            # Try Supabase first
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
            
            # If we got results, return them
            if unique_quotes:
                logger.info(f"Sacred Library search via Supabase: found {len(unique_quotes)} quotes")
                return unique_quotes
            
            # If no results, this might be a Supabase issue, try local fallback
            logger.warning("No results from Supabase, trying local Sacred Library fallback")
            
        except Exception as e:
            logger.warning(f"Supabase Sacred Library error: {e}, falling back to local search")
        
        # Fallback to local search
        try:
            if local_sacred_library.is_available():
                local_quotes = local_sacred_library.search_quotes(query, limit=limit)
                if local_quotes:
                    logger.info(f"Sacred Library search via local fallback: found {len(local_quotes)} quotes")
                    return local_quotes
                else:
                    # If no search results, get random quotes
                    random_quotes = local_sacred_library.get_random_quotes(limit=limit)
                    if random_quotes:
                        logger.info(f"Sacred Library providing {len(random_quotes)} random quotes")
                        return random_quotes
            else:
                logger.error("Local Sacred Library not available")
        except Exception as e:
            logger.error(f"Local Sacred Library error: {e}")
        
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
            # Queue message for background analysis (if available)
            if self.background_task:
                try:
                    await self.analysis_queue.put({
                        'person_id': person_id,
                        'message': message,
                        'source': source,
                        'timestamp': datetime.utcnow()
                    })
                except:
                    # Skip if queue not available
                    pass
            
            # Get any existing personality insights
            personality_context = await self._get_quick_personality_context(person_id)
            
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
CRITICAL: If RELEVANT TEACHINGS are provided below, you MUST use them directly in your response.
1. Share the exact quotes immediately with full citations
2. Provide zero-hallucination vector summary
3. Connect to their specific question

FORMAT when Sacred Library quotes are available:
◆ SACRED LIBRARY ◆
[Quote with citation]
▲ REFLECTION ▲
[Your commentary and connection to their question]"""

            # Add personality context if available
            if personality_context:
                system_prompt += "\n\nPERSONALITY INSIGHTS:\n"
                if personality_context.get('core_patterns'):
                    system_prompt += f"Core patterns: {', '.join(personality_context['core_patterns'])}\n"
                if personality_context.get('growth_edges'):
                    system_prompt += f"Growth edges: {', '.join(personality_context['growth_edges'])}\n"
                if personality_context.get('essence_level'):
                    system_prompt += f"Essence level: {personality_context['essence_level']}\n"

            # Add Sacred Library quotes if available
            if sacred_quotes:
                logger.info(f"Adding {len(sacred_quotes)} Sacred Library quotes to prompt")
                system_prompt += "\n\nRELEVANT TEACHINGS:\n"
                for i, quote in enumerate(sacred_quotes):
                    chapter = quote['metadata'].get('chapter', 'Unknown')
                    language = quote['metadata'].get('language', 'unknown').upper()
                    content = quote["content"][:100] + "..." if len(quote["content"]) > 100 else quote["content"]
                    logger.info(f"Quote {i+1}: {chapter} ({language}): {content}")
                    system_prompt += f"\nFrom {quote['metadata'].get('chapter', 'Unknown')} ({quote['metadata'].get('language', 'unknown').upper()}):\n"
                    system_prompt += f'"{quote["content"]}"\n'
            else:
                logger.warning("No Sacred Library quotes found for this query")
            
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

    async def _process_analysis_queue(self):
        """Background task to process personality analysis queue"""
        while True:
            try:
                # Get next message from queue
                message_data = await self.analysis_queue.get()
                
                try:
                    # Run full personality analysis
                    analysis_results = await self.personality_analyzer.analyze_message(
                        person_id=message_data['person_id'],
                        message=message_data['message'],
                        context={"source": message_data['source']}
                    )
                    
                    # Get or create personality profile
                    profile = await self._get_or_create_personality_profile(message_data['person_id'])
                    
                    # Update profile with new analysis
                    updated_profile = await self.personality_analyzer.update_personality_profile(
                        person_id=message_data['person_id'],
                        analysis_results=analysis_results,
                        existing_profile=profile
                    )
                    
                    # Store results
                    await self._store_analysis_results(
                        person_id=message_data['person_id'],
                        analysis=analysis_results,
                        profile=updated_profile,
                        message_data=message_data
                    )
                    
                    logger.info(f"Completed background analysis for person {message_data['person_id']}")
                    
                except Exception as e:
                    logger.error(f"Error in background analysis: {e}")
                finally:
                    # Mark task as done
                    self.analysis_queue.task_done()
                
            except asyncio.CancelledError:
                # Handle graceful shutdown
                logger.info("Background analysis queue cancelled")
                break
            except Exception as e:
                logger.error(f"Critical error in analysis queue: {e}")
                # Small delay before continuing
                await asyncio.sleep(1.0)
    
    async def _get_quick_personality_context(self, person_id: str) -> Optional[Dict[str, Any]]:
        """Get cached personality context for quick access"""
        try:
            # Get latest profile from database
            result = db.client.table('personality_profiles').select(
                'core_patterns, growth_edges, essence_level'
            ).eq(
                'person_id', person_id
            ).order('created_at', desc=True).limit(1).execute()
            
            if result.data:
                return result.data[0]
            return None
            
        except Exception as e:
            logger.warning(f"Personality profiles table not available: {e}")
            # Return None gracefully - bot can work without personality context
            return None
    
    async def _get_or_create_personality_profile(self, person_id: str) -> Optional[SynthesisPersonalityProfile]:
        """Get existing personality profile or create new one"""
        try:
            # Get profile from database
            result = db.client.table('personality_profiles').select(
                '*'
            ).eq(
                'person_id', person_id
            ).order('created_at', desc=True).limit(1).execute()
            
            if result.data:
                # Convert to SynthesisPersonalityProfile
                return SynthesisPersonalityProfile.from_dict(result.data[0])
            
            # Create new profile
            return SynthesisPersonalityProfile(
                person_id=person_id,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error getting personality profile: {e}")
            return None
    
    async def _store_analysis_results(
        self,
        person_id: str,
        analysis: Dict[str, Any],
        profile: SynthesisPersonalityProfile,
        message_data: Dict[str, Any]
    ):
        """Store analysis results and updated profile"""
        try:
            # Store analysis results
            db.client.table('personality_analysis').insert({
                'person_id': person_id,
                'analysis_data': analysis,
                'message': message_data['message'],
                'source': message_data['source'],
                'created_at': message_data['timestamp']
            }).execute()
            
            # Store updated profile
            db.client.table('personality_profiles').insert({
                'person_id': person_id,
                'core_patterns': profile.core_patterns,
                'growth_edges': profile.growth_edges,
                'essence_level': profile.becoming_one.primary_essence_level if profile.becoming_one else None,
                'created_at': datetime.utcnow()
            }).execute()
            
        except Exception as e:
            logger.warning(f"Could not store personality analysis (tables may not exist): {e}")
            # Continue without storing - bot can work without personality storage