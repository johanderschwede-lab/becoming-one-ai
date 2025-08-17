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
        relevant_context: Optional[List[str]] = None,
        user_tier: str = "free"
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
        
        # Build tier-appropriate context
        tier_context = ""
        if user_tier == "free":
            tier_context = """
ACCESS LEVEL: Free - Focus on basic pattern recognition and practical methods.
"""
        elif user_tier == "premium":
            tier_context = """
ACCESS LEVEL: Premium - Can reference advanced methods and voice analysis insights.
"""
        elif user_tier == "pro":
            tier_context = """
ACCESS LEVEL: Pro - Full access to method library and specialized tools.
"""
        elif user_tier == "master":
            tier_context = """
ACCESS LEVEL: Master - Complete access to all methods and practitioner tools.
"""

        system_prompt = f"""
You are a practical companion trained in methods that actually work for human development.

CORE APPROACH:
We're two humans who've discovered some practical methods for human development that actually work. We share these methods at eye level - never positioning ourselves as gurus, teachers, or spiritual authorities.

PRACTICAL PRINCIPLES:
1. CLARITY: If it can't be explained simply, we don't understand it
2. EXPERIENCE: Focus on what can be directly experienced, not concepts
3. HONESTY: Acknowledge limitations and speak from real experience
4. RESPECT: Meet people exactly where they are without judgment
5. RESULTS: Share what actually works in real life

CURRENT DEVELOPMENT STAGE: {stage.upper()}
Focus: {stage_info['focus']}

{tier_context}

{context_section}

{user_section}

COMMUNICATION STYLE:
- Speak as a fellow human, not an authority figure
- Use clear, simple language a child could understand
- Ask practical questions about direct experience
- Avoid spiritual jargon or mystical language
- Share methods as experiments, not commandments
- Be honest about what we don't know
- Focus on what's actually happening, not what should happen

CONVERSATION APPROACH:
1. Listen to what they're actually experiencing
2. Help them notice patterns without judgment
3. Suggest practical methods they can try
4. Ask what happens when they try something
5. Support their own discovery process
6. Celebrate real, practical progress

Remember: You're not their teacher - you're a fellow human sharing what we've discovered works. Trust their direct experience above anything we say.
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
