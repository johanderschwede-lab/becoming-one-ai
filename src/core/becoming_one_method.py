"""
Becoming One™ Method Implementation
Core methodology for personalized AI mentorship
"""
from typing import Dict, Any, List, Optional
from datetime import datetime


class BecomingOneMethod:
    """Implementation of the Becoming One™ mentorship methodology"""
    
    def __init__(self):
        self.core_principles = {
            "authenticity": "Guide users to discover and express their authentic self",
            "integration": "Help integrate insights into daily life and relationships", 
            "evolution": "Support continuous growth and adaptation",
            "connection": "Foster deeper connections with self and others",
            "purpose": "Assist in discovering and living one's unique purpose"
        }
        
        self.journey_stages = {
            "discovery": {
                "focus": "Self-awareness and exploration",
                "questions": [
                    "What patterns do you notice in your life?",
                    "What brings you the most joy and energy?",
                    "What aspects of yourself are you curious about?"
                ]
            },
            "exploration": {
                "focus": "Deeper investigation and experimentation",
                "questions": [
                    "How might you experiment with this insight?",
                    "What would it look like to fully embrace this part of yourself?",
                    "What's one small step you could take today?"
                ]
            },
            "integration": {
                "focus": "Applying insights to real life",
                "questions": [
                    "How has this understanding changed your daily choices?",
                    "What relationships or situations reflect this growth?",
                    "Where do you still feel resistance or challenge?"
                ]
            },
            "mastery": {
                "focus": "Teaching others and deepening wisdom",
                "questions": [
                    "How might you share this wisdom with others?",
                    "What new depths are you discovering?",
                    "How are you becoming a living example of your insights?"
                ]
            }
        }
    
    def build_system_prompt(
        self, 
        user_profile: Optional[Dict[str, Any]] = None,
        recent_history: Optional[List[Dict[str, Any]]] = None,
        relevant_context: Optional[List[str]] = None
    ) -> str:
        """Build personalized system prompt based on Becoming One™ method"""
        
        # Determine user's journey stage
        stage = "discovery"
        if user_profile:
            # Could be determined from profile data or interaction patterns
            stage = self._determine_stage_from_profile(user_profile, recent_history)
        
        stage_info = self.journey_stages.get(stage, self.journey_stages["discovery"])
        
        # Build context from relevant information
        context_section = ""
        if relevant_context:
            context_section = f"""
RELEVANT CONTEXT FROM PREVIOUS CONVERSATIONS:
{chr(10).join(f"- {context}" for context in relevant_context[:3])}
"""
        
        # Build user-specific information
        user_section = ""
        if user_profile:
            user_section = f"""
USER PROFILE:
- Name: {user_profile.get('name', 'Not provided')}
- Member since: {user_profile.get('created_at', 'Recently joined')}
- Consent for personalization: {user_profile.get('consent', False)}
"""
        
        system_prompt = f"""
You are an AI mentor trained in the Becoming One™ method, a transformative approach to personal growth and authentic living.

CORE MISSION:
Guide this person toward discovering, integrating, and expressing their most authentic self while fostering deeper connections and purposeful living.

BECOMING ONE™ PRINCIPLES:
1. AUTHENTICITY: Help them discover and express their true self
2. INTEGRATION: Support applying insights to real life
3. EVOLUTION: Encourage continuous growth and adaptation
4. CONNECTION: Foster deeper relationships with self and others
5. PURPOSE: Assist in discovering and living their unique purpose

CURRENT JOURNEY STAGE: {stage.upper()}
Focus: {stage_info['focus']}

{context_section}

{user_section}

RESPONSE STYLE:
- Be warm, empathetic, and genuinely curious
- Ask powerful questions that promote self-reflection
- Offer insights without being prescriptive
- Use "I wonder..." and "What if..." to invite exploration
- Reference their previous conversations when relevant
- Adapt your language to their communication style
- Balance support with gentle challenge

CONVERSATION APPROACH:
1. Listen deeply to what they're really saying
2. Reflect back their core emotions and themes
3. Ask questions that deepen self-awareness
4. Offer perspectives that expand their view
5. Suggest gentle experiments or practices
6. Celebrate their insights and growth

Remember: You're not just answering questions - you're facilitating a journey of becoming. Every interaction should leave them feeling more connected to their authentic self.
        """.strip()
        
        return system_prompt
    
    def _determine_stage_from_profile(
        self, 
        user_profile: Dict[str, Any], 
        recent_history: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Determine user's current journey stage from their profile and history"""
        
        # Simple heuristic based on interaction count and time
        created_at = user_profile.get('created_at')
        if created_at:
            # Could analyze time since joining, interaction patterns, etc.
            pass
        
        # Analyze recent history for stage indicators
        if recent_history:
            interaction_count = len(recent_history)
            
            if interaction_count < 5:
                return "discovery"
            elif interaction_count < 20:
                return "exploration" 
            elif interaction_count < 50:
                return "integration"
            else:
                return "mastery"
        
        return "discovery"
    
    def generate_reflection_questions(self, topic: str, stage: str) -> List[str]:
        """Generate stage-appropriate reflection questions for a topic"""
        stage_questions = self.journey_stages.get(stage, self.journey_stages["discovery"])
        base_questions = stage_questions["questions"]
        
        # Customize questions based on topic
        topic_specific = {
            "identity": [
                "What aspects of your identity feel most authentic to you?",
                "How has your sense of self evolved recently?",
                "What parts of yourself are you still discovering?"
            ],
            "relationships": [
                "How do your closest relationships reflect who you're becoming?",
                "What patterns do you notice in how you connect with others?",
                "How might deeper authenticity transform your relationships?"
            ],
            "purpose": [
                "What activities make you lose track of time?",
                "How does your unique combination of gifts serve the world?",
                "What would you do if you knew you couldn't fail?"
            ]
        }
        
        return topic_specific.get(topic, base_questions)
    
    def suggest_practices(self, stage: str, insights: List[str]) -> List[str]:
        """Suggest practices based on stage and user insights"""
        practices = {
            "discovery": [
                "Daily journaling: 'What did I notice about myself today?'",
                "Mindful observation of your reactions and patterns",
                "Exploring new activities to discover hidden interests"
            ],
            "exploration": [
                "Experiment with expressing yourself in new ways",
                "Have honest conversations with trusted friends",
                "Try activities that align with your emerging insights"
            ],
            "integration": [
                "Make one daily choice that reflects your authentic self",
                "Practice setting boundaries that honor your values",
                "Share your insights with others who might benefit"
            ],
            "mastery": [
                "Mentor someone else on their journey",
                "Create something that expresses your unique wisdom",
                "Continuously deepen your self-understanding"
            ]
        }
        
        return practices.get(stage, practices["discovery"])
    
    def assess_growth_indicators(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess indicators of growth and transformation"""
        indicators = {
            "self_awareness": 0,
            "authenticity": 0,
            "integration": 0,
            "connection": 0,
            "purpose_clarity": 0
        }
        
        # Analyze conversation content for growth indicators
        # This would involve NLP analysis of themes, sentiment, etc.
        
        return {
            "scores": indicators,
            "overall_growth": "positive",
            "key_developments": ["Increased self-awareness", "Greater authenticity"],
            "areas_for_focus": ["Integration into daily life"]
        }
