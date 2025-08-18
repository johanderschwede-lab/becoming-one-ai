"""
Core AI Engine for Becoming One™ Method
Integrates OpenAI, Pinecone, and comprehensive personality analysis
"""
import os
from typing import Dict, Any, List, Optional
from openai import OpenAI
import uuid
from loguru import logger

from ..database.operations import db
from ..integrations.pinecone_client import PineconeClient
from .becoming_one_method import BecomingOneMethod
from .personality_analyzer import BecomingOnePersonalityAnalyzer
from .personality_synthesis_model import SynthesisPersonalityProfile


class BecomingOneAI:
    """Main AI processing engine"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.pinecone_client = PineconeClient()
        self.becoming_one = BecomingOneMethod()
        self.personality_analyzer = BecomingOnePersonalityAnalyzer()
        
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        
    async def search_sacred_library(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Search Sacred Library for relevant Hylozoics quotes"""
        try:
            # Extract key concepts for better search
            search_terms = self._extract_search_terms(query)
            all_quotes = []
            
            for term in search_terms[:3]:  # Try top 3 concepts
                result = db.client.table('teaching_materials').select(
                    'content, title, metadata'
                ).eq(
                    'material_type', 'sacred_quote'
                ).ilike(
                    'content', f'%{term}%'
                ).limit(limit).execute()
                
                if result.data:
                    all_quotes.extend(result.data)
            
            # Remove duplicates and return top results
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
    
    def _extract_search_terms(self, message: str) -> List[str]:
        """Extract key search terms from user message"""
        # Key concepts that often have relevant Hylozoics content
        spiritual_concepts = [
            'meditation', 'consciousness', 'development', 'evolution', 'knowledge',
            'wisdom', 'understanding', 'reality', 'truth', 'purpose', 'meaning',
            'growth', 'learning', 'experience', 'awareness', 'mind', 'thinking',
            'emotion', 'feeling', 'relationship', 'love', 'life', 'death',
            'soul', 'spirit', 'energy', 'power', 'will', 'harmony', 'peace'
        ]
        
        message_lower = message.lower()
        found_terms = []
        
        # Find spiritual concepts in the message
        for concept in spiritual_concepts:
            if concept in message_lower:
                found_terms.append(concept)
        
        # If no spiritual concepts found, try key words from the message
        if not found_terms:
            words = message_lower.split()
            # Filter out common words and keep meaningful ones
            meaningful_words = [w for w in words if len(w) > 4 and w not in 
                             ['that', 'this', 'with', 'from', 'they', 'have', 'been', 'were']]
            found_terms.extend(meaningful_words[:3])
        
        return found_terms if found_terms else ['life', 'development']

    async def process_message(
        self, 
        person_id: uuid.UUID, 
        message: str, 
        source: str,
        user_tier: str = "free"
    ) -> str:
        """Process a user message with comprehensive personality analysis and generate personalized response"""
        try:
            # STEP 1: Analyze message for personality patterns
            personality_analysis = await self.personality_analyzer.analyze_message(
                person_id=person_id,
                message=message,
                context={"source": source}
            )
            
            # STEP 2: Get or create personality synthesis profile
            personality_profile = await self._get_or_create_personality_profile(person_id)
            
            # STEP 3: Update personality profile with new analysis
            updated_profile = await self.personality_analyzer.update_personality_profile(
                person_id=person_id,
                analysis_results=personality_analysis,
                existing_profile=personality_profile
            )
            
            # STEP 4: Store personality insights in database
            await self._store_personality_insights(person_id, personality_analysis, updated_profile)
            
            # STEP 5: Get user context and history
            user_profile = await db.get_user_profile(person_id)
            recent_history = await db.get_user_history(person_id, limit=10)
            
            # STEP 6: Retrieve relevant context from Pinecone
            relevant_context = await self.pinecone_client.search_similar_content(
                query=message,
                person_id=person_id,
                top_k=5
            )
            
            # STEP 6.5: Search Sacred Library for relevant Hylozoics quotes
            sacred_quotes = await self.search_sacred_library(message, limit=2)
            if sacred_quotes:
                logger.info(f"Found {len(sacred_quotes)} relevant Sacred Library quotes")
            
            # STEP 7: Generate personalized response using complete personality synthesis
            personalized_response = self.personality_analyzer.generate_personalized_response(
                profile=updated_profile,
                current_message=message,
                context={
                    "user_profile": user_profile,
                    "recent_history": recent_history,
                    "relevant_context": relevant_context,
                    "source": source,
                    "sacred_quotes": sacred_quotes
                }
            )
            
            # STEP 8: If personalized response fails, fall back to standard method
            if personalized_response.get("personalization_level") == "fallback":
                # Build system prompt using Becoming One™ method
                system_prompt = self.becoming_one.build_system_prompt(
                    user_profile=user_profile,
                    recent_history=recent_history,
                    relevant_context=relevant_context,
                    user_tier=user_tier,
                    sacred_quotes=sacred_quotes
                )
                
                # Build conversation context
                messages = self._build_conversation_context(
                    system_prompt=system_prompt,
                    recent_history=recent_history,
                    current_message=message
                )
                
                # Generate response with OpenAI
                response = await self._generate_response(messages)
            else:
                response = personalized_response["personalized_response"]
            
            # STEP 9: Store the interaction in Pinecone for future retrieval
            await self.pinecone_client.store_interaction(
                person_id=person_id,
                message=message,
                response=response,
                source=source
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message with personality analysis: {e}")
            return self._get_fallback_response()
    
    def _build_conversation_context(
        self, 
        system_prompt: str, 
        recent_history: List[Dict[str, Any]], 
        current_message: str
    ) -> List[Dict[str, str]]:
        """Build conversation context for OpenAI"""
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add recent history (alternating user/assistant)
        for event in reversed(recent_history[-6:]):  # Last 6 events (3 exchanges)
            if event["type"] == "message":
                messages.append({
                    "role": "user",
                    "content": event["content"]
                })
            elif event["type"] == "response":
                messages.append({
                    "role": "assistant", 
                    "content": event["content"]
                })
        
        # Add current message
        messages.append({"role": "user", "content": current_message})
        
        return messages
    
    async def _generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using OpenAI"""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """Fallback response when AI processing fails"""
        return """
I'm experiencing a temporary issue processing your message. 

In the spirit of the Becoming One™ method, let me offer this:
Sometimes the most profound insights come from pausing and reflecting. 

What feels most important to you right now in this moment?
        """.strip()
    
    async def analyze_user_journey(self, person_id: uuid.UUID) -> Dict[str, Any]:
        """Analyze user's journey progress and insights"""
        history = await db.get_user_history(person_id, limit=100)
        
        # Extract patterns and insights
        message_count = len([h for h in history if h["type"] == "message"])
        topics = self._extract_topics(history)
        sentiment_trend = self._analyze_sentiment_trend(history)
        
        return {
            "total_interactions": message_count,
            "primary_topics": topics,
            "sentiment_trend": sentiment_trend,
            "journey_stage": self._determine_journey_stage(history),
            "recommendations": self._generate_recommendations(history)
        }
    
    def _extract_topics(self, history: List[Dict[str, Any]]) -> List[str]:
        """Extract main topics from conversation history"""
        # Simple keyword extraction (can be enhanced with NLP)
        topics = []
        content_texts = [h["content"] for h in history if h.get("content")]
        
        # Common Becoming One™ themes
        theme_keywords = {
            "identity": ["identity", "self", "who am i", "purpose"],
            "growth": ["growth", "develop", "improve", "change"],
            "relationships": ["relationship", "connection", "love", "family"],
            "career": ["work", "career", "job", "professional"],
            "spirituality": ["spiritual", "meaning", "soul", "purpose"],
            "creativity": ["creative", "art", "express", "create"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in " ".join(content_texts).lower() for keyword in keywords):
                topics.append(theme)
        
        return topics[:3]  # Top 3 topics
    
    def _analyze_sentiment_trend(self, history: List[Dict[str, Any]]) -> str:
        """Analyze sentiment trend over time"""
        # Simplified sentiment analysis
        return "positive_growth"  # Placeholder
    
    def _determine_journey_stage(self, history: List[Dict[str, Any]]) -> str:
        """Determine user's current journey stage"""
        interaction_count = len(history)
        
        if interaction_count < 5:
            return "discovery"
        elif interaction_count < 20:
            return "exploration"
        elif interaction_count < 50:
            return "integration"
        else:
            return "mastery"
    
    def _generate_recommendations(self, history: List[Dict[str, Any]]) -> List[str]:
        """Generate personalized recommendations"""
        return [
            "Continue exploring your authentic self",
            "Practice daily reflection and mindfulness",
            "Consider journaling your insights"
        ]
    
    # ============================================================================
    # PERSONALITY SYNTHESIS INTEGRATION METHODS
    # ============================================================================
    
    async def _get_or_create_personality_profile(self, person_id: uuid.UUID) -> Optional[SynthesisPersonalityProfile]:
        """Get existing personality profile or create new one"""
        try:
            # Try to get existing profile from database
            # This would need to be implemented in database operations
            # For now, return None to create new profiles each time
            return None
        except Exception as e:
            logger.error(f"Error retrieving personality profile: {e}")
            return None
    
    async def _store_personality_insights(
        self, 
        person_id: uuid.UUID, 
        analysis: Dict[str, Any], 
        profile: SynthesisPersonalityProfile
    ) -> bool:
        """Store personality analysis insights in database"""
        try:
            # Store personality indicators
            await self._store_personality_indicators(person_id, analysis)
            
            # Store emotional anchor activations
            await self._store_anchor_activations(person_id, analysis)
            
            # Store avoidance pattern detections
            await self._store_avoidance_detections(person_id, analysis)
            
            # Store synthesis profile updates
            await self._store_synthesis_profile(profile)
            
            logger.info(f"Stored personality insights for person {person_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing personality insights: {e}")
            return False
    
    async def _store_personality_indicators(self, person_id: uuid.UUID, analysis: Dict[str, Any]):
        """Store detected personality indicators"""
        indicators_to_store = []
        
        # Process Enneagram indicators
        enneagram_data = analysis.get("enneagram_analysis", {})
        if "primary_type_indicators" in enneagram_data:
            for indicator in enneagram_data["primary_type_indicators"]:
                indicators_to_store.append({
                    "person_id": person_id,
                    "system_type": "enneagram",
                    "indicator_type": f"type_{indicator.get('type')}",
                    "indicator_value": str(indicator.get('type')),
                    "confidence": indicator.get('confidence', 0.0),
                    "source": "text_analysis",
                    "metadata": {"evidence": indicator.get('evidence', '')}
                })
        
        # Process Human Design indicators
        hd_data = analysis.get("human_design_analysis", {})
        if "type_indicators" in hd_data:
            for indicator in hd_data["type_indicators"]:
                indicators_to_store.append({
                    "person_id": person_id,
                    "system_type": "human_design",
                    "indicator_type": "type",
                    "indicator_value": indicator.get('type'),
                    "confidence": indicator.get('confidence', 0.0),
                    "source": "text_analysis",
                    "metadata": {}
                })
        
        # Process Essence Level indicators
        essence_data = analysis.get("essence_level_analysis", {})
        if "level_indicators" in essence_data:
            for indicator in essence_data["level_indicators"]:
                indicators_to_store.append({
                    "person_id": person_id,
                    "system_type": "becoming_one",
                    "indicator_type": "essence_level",
                    "indicator_value": indicator.get('level'),
                    "confidence": indicator.get('confidence', 0.0),
                    "source": "text_analysis",
                    "metadata": {"evidence": indicator.get('evidence', '')}
                })
        
        # Store all indicators (would need database implementation)
        # For now, just log them
        for indicator in indicators_to_store:
            logger.info(f"Personality indicator: {indicator}")
    
    async def _store_anchor_activations(self, person_id: uuid.UUID, analysis: Dict[str, Any]):
        """Store emotional anchor activations"""
        anchor_data = analysis.get("emotional_anchor_analysis", {})
        
        if "anchor_activations" in anchor_data:
            for activation in anchor_data["anchor_activations"]:
                anchor_info = {
                    "person_id": person_id,
                    "anchor_type": activation.get('anchor'),
                    "intensity": activation.get('intensity', 0.0),
                    "trigger_context": activation.get('evidence', ''),
                    "somatic_markers": anchor_data.get('somatic_markers', []),
                    "language_patterns": [],  # Could be extracted from analysis
                }
                
                # Log anchor activation (would need database implementation)
                logger.info(f"Anchor activation: {anchor_info}")
    
    async def _store_avoidance_detections(self, person_id: uuid.UUID, analysis: Dict[str, Any]):
        """Store avoidance pattern detections"""
        avoidance_data = analysis.get("avoidance_pattern_analysis", {})
        
        if "avoidance_signatures" in avoidance_data:
            for pattern in avoidance_data["avoidance_signatures"]:
                avoidance_info = {
                    "person_id": person_id,
                    "avoidance_type": pattern.get('pattern'),
                    "behavioral_markers": [],
                    "language_hedges": avoidance_data.get('hedging_language', []),
                    "time_patterns": avoidance_data.get('time_patterns', {}),
                    "underlying_fears": avoidance_data.get('underlying_fears', [])
                }
                
                # Log avoidance detection (would need database implementation)
                logger.info(f"Avoidance pattern: {avoidance_info}")
    
    async def _store_synthesis_profile(self, profile: SynthesisPersonalityProfile):
        """Store or update synthesis personality profile"""
        try:
            # This would need to be implemented with proper database operations
            # For now, just log the profile summary
            logger.info(f"Synthesis profile update for {profile.person_id}:")
            logger.info(f"  Core patterns: {profile.core_patterns}")
            logger.info(f"  Growth edges: {profile.growth_edges}")
            logger.info(f"  Recommended practices: {profile.recommended_practices}")
            
            if profile.becoming_one:
                logger.info(f"  Essence level: {profile.becoming_one.primary_essence_level}")
                logger.info(f"  Vertical stage: {profile.becoming_one.current_vertical_stage}")
                logger.info(f"  Anchor patterns: {[a.value for a in profile.becoming_one.dominant_anchor_patterns]}")
            
        except Exception as e:
            logger.error(f"Error storing synthesis profile: {e}")
    
    async def get_personality_context_for_ai(self, person_id: uuid.UUID) -> Dict[str, Any]:
        """Get personality context for AI prompt enhancement"""
        try:
            # This would retrieve from database using the SQL function we created
            # For now, return empty context
            return {
                "personality_available": False,
                "systems_identified": [],
                "confidence_scores": {},
                "core_patterns": [],
                "anchor_patterns": [],
                "growth_edges": []
            }
        except Exception as e:
            logger.error(f"Error getting personality context: {e}")
            return {}
