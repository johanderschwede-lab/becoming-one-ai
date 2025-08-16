"""
Core AI Engine for Becoming One™ Method
Integrates OpenAI, Pinecone, and personalization logic
"""
import os
from typing import Dict, Any, List, Optional
from openai import OpenAI
import uuid
from loguru import logger

from ..database.operations import db
from ..integrations.pinecone_client import PineconeClient
from .becoming_one_method import BecomingOneMethod


class BecomingOneAI:
    """Main AI processing engine"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.pinecone_client = PineconeClient()
        self.becoming_one = BecomingOneMethod()
        
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
        
    async def process_message(
        self, 
        person_id: uuid.UUID, 
        message: str, 
        source: str
    ) -> str:
        """Process a user message and generate response"""
        try:
            # Get user context and history
            user_profile = await db.get_user_profile(person_id)
            recent_history = await db.get_user_history(person_id, limit=10)
            
            # Retrieve relevant context from Pinecone
            relevant_context = await self.pinecone_client.search_similar_content(
                query=message,
                person_id=person_id,
                top_k=5
            )
            
            # Build system prompt using Becoming One™ method
            system_prompt = self.becoming_one.build_system_prompt(
                user_profile=user_profile,
                recent_history=recent_history,
                relevant_context=relevant_context
            )
            
            # Build conversation context
            messages = self._build_conversation_context(
                system_prompt=system_prompt,
                recent_history=recent_history,
                current_message=message
            )
            
            # Generate response with OpenAI
            response = await self._generate_response(messages)
            
            # Store the interaction in Pinecone for future retrieval
            await self.pinecone_client.store_interaction(
                person_id=person_id,
                message=message,
                response=response,
                source=source
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
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
