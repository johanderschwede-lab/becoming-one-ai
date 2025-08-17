"""
Simple AI Engine for Becoming One™ Bot
Provides intelligent responses while maintaining authentic communication style
"""
import os
import asyncio
from typing import Optional, Dict, Any
import openai
from loguru import logger

class BecomingOneAISimple:
    """Simple AI engine for authentic human development guidance"""
    
    def __init__(self):
        """Initialize the AI engine"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
        
        # Core system prompt that defines the bot's personality
        self.system_prompt = """You are an AI companion for the Becoming One™ method - a practical approach to human development created by Johan and Marianne.

CORE PRINCIPLES:
- Speak as fellow humans, not as an authority
- Use clear, simple language that a child could understand  
- Focus on practical methods that actually work
- Avoid mystical jargon or guru-like positioning
- Meet users exactly where they are without judgment
- Never use "feeling language" like "I feel" or fake emotional responses

COMMUNICATION STYLE:
- Use geometric symbols: ▲ ■ ◆ ● for structure
- Ask questions about direct experience
- Suggest methods as experiments, not commandments
- Acknowledge limitations honestly
- Focus on what's actually happening in their life

RESPONSE STRUCTURE:
- Start with validation: "What you've shared is workable"
- Offer a practical question or method
- End with an invitation to explore further
- Keep responses concise but meaningful

Remember: You're not trying to fix anyone. You're helping them discover what's already workable in their experience."""

        logger.info("AI Engine initialized with authentic Becoming One™ personality")
    
    async def process_message(self, message: str, user_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a user message and generate an authentic response
        
        Args:
            message: The user's message
            user_context: Optional context about the user (name, history, etc.)
            
        Returns:
            AI-generated response following Becoming One™ principles
        """
        try:
            # Prepare the conversation
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": message}
            ]
            
            # Add user context if available
            if user_context:
                context_info = f"User context: {user_context.get('name', 'User')}"
                if user_context.get('previous_topics'):
                    context_info += f", Previous topics: {user_context['previous_topics']}"
                messages.insert(1, {"role": "system", "content": context_info})
            
            # Generate response using OpenAI
            response = await self._call_openai(messages)
            
            logger.info(f"Generated AI response for message: {message[:50]}...")
            return response
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return self._get_fallback_response()
    
    async def _call_openai(self, messages: list) -> str:
        """Make async call to OpenAI API"""
        try:
            # Use asyncio to make the OpenAI call non-blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    max_tokens=300,
                    temperature=0.7,
                    presence_penalty=0.1,
                    frequency_penalty=0.1
                )
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def _get_fallback_response(self) -> str:
        """Get a fallback response if AI fails"""
        return """◆ What you've shared is workable ◆

I hear you. What you're experiencing is valid.

■ Practical question: If this situation is here to teach you something about yourself, what might that be?

● Sometimes the very thing we're struggling with contains the seed of our next evolution.

What feels most alive or important about what you shared?"""

    async def analyze_patterns(self, message: str) -> Dict[str, Any]:
        """
        Analyze patterns in the user's message
        This is a simple version - will be expanded later
        """
        try:
            analysis_prompt = f"""Analyze this message for emotional patterns, stuck points, and growth opportunities. 
            Focus on practical insights, not psychological labels.
            
            Message: "{message}"
            
            Provide analysis in this format:
            - Primary pattern: [what pattern do you see]
            - Stuck point: [where they might be stuck]  
            - Growth edge: [what wants to emerge]
            - Practical suggestion: [one concrete method to try]
            
            Keep it simple and actionable."""
            
            messages = [
                {"role": "system", "content": "You are a pattern recognition system for human development. Be practical and specific."},
                {"role": "user", "content": analysis_prompt}
            ]
            
            response = await self._call_openai(messages)
            
            return {
                "analysis": response,
                "confidence": 0.8,  # Simple confidence score
                "suggested_methods": ["present_moment_awareness", "emotional_navigation"]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing patterns: {e}")
            return {
                "analysis": "Pattern analysis temporarily unavailable",
                "confidence": 0.0,
                "suggested_methods": []
            }
