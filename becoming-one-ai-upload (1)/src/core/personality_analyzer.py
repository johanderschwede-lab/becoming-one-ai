"""
Becoming One™ Personality Analysis Engine
==========================================

AI-powered system that analyzes user interactions to build comprehensive
personality synthesis profiles combining multiple established systems
with Becoming One™ unique dimensions.
"""

import re
import json
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import uuid
from dataclasses import asdict

from openai import OpenAI
import os

from .personality_synthesis_model import (
    SynthesisPersonalityProfile,
    PersonalityAnalyzer,
    EnneagramType,
    HDType,
    ZodiacSign,
    EssenceLevel,
    VerticalStage,
    ManifestationStyle,
    EmotionalAnchorPattern,
    AvoidanceSignature
)


class BecomingOnePersonalityAnalyzer:
    """
    Main personality analysis engine that processes user interactions
    to build and update comprehensive personality synthesis profiles
    """
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.analysis_prompts = self._load_analysis_prompts()
    
    def _load_analysis_prompts(self) -> Dict[str, str]:
        """Load specialized prompts for different personality systems"""
        return {
            "enneagram_analysis": """
            Analyze this text for Enneagram type indicators. Look for:
            - Core motivations and fears
            - Behavioral patterns
            - Language patterns
            - Emotional responses
            - Coping mechanisms
            
            Return JSON with:
            {
                "primary_type_indicators": [{"type": 1-9, "confidence": 0.0-1.0, "evidence": "text"}],
                "wing_indicators": [{"wing": "w1-w9", "confidence": 0.0-1.0}],
                "instinct_indicators": [{"instinct": "sp/so/sx", "confidence": 0.0-1.0}],
                "health_level_estimate": 1-9
            }
            """,
            
            "human_design_analysis": """
            Analyze this text for Human Design indicators. Look for:
            - Energy patterns (how they engage with life)
            - Decision-making style
            - Response patterns
            - Authority indicators
            - Strategy alignment
            
            Return JSON with:
            {
                "type_indicators": [{"type": "manifestor/generator/projector/reflector", "confidence": 0.0-1.0}],
                "authority_indicators": [{"authority": "emotional/sacral/splenic/etc", "confidence": 0.0-1.0}],
                "strategy_alignment": {"strategy": "...", "evidence": "text"}
            }
            """,
            
            "emotional_anchor_analysis": """
            Analyze this text for Becoming One™ emotional anchor patterns (stored emotional matter). Look for:
            - Anchors in time: abandonment, unworthiness, powerlessness, betrayal, shame, fear of bigness
            - Age epochs: conception, infancy, childhood, school age, adolescence, past-life recurrencies
            - Loyalty debts to family/tribe/old self that prevent growth
            - Secondary gains: what benefit the anchor provides (safety, belonging, predictability)
            - Somatic markers: body sensations indicating anchor activation
            - The Pearl: transformational insights when anchors are digested
            
            Return JSON with:
            {
                "anchor_activations": [{"anchor": "unworthiness", "intensity": 0.8, "age_epoch": "school_age", "evidence": "text"}],
                "loyalty_debts": [{"to_whom": "family", "vow": "I mustn't surpass them", "evidence": "text"}],
                "secondary_gains": ["belonging", "safety", "predictability"],
                "somatic_markers": ["tight chest", "shallow breathing", "throat constriction"],
                "pearls_detected": [{"insight": "I can feel anger without becoming it", "quality_gained": "steadiness"}],
                "recurrency_themes": ["abandonment pattern repeating across relationships"]
            }
            """,
            
            "avoidance_pattern_analysis": """
            Analyze this text for avoidance patterns using Becoming One™ anti-bypass framework. Look for:
            - Procrastination archetypes: fog walker, perfectionist, shame avoider, overwhelm freezer
            - Hedging language: "should", "maybe", "I can't because", "when I... then I", "someday"
            - Escape moves: analysis, humor, busyness, speed, helpfulness
            - Nervous system responses: freeze, flight, fight, fawn, collapse
            - What they're protecting themselves from feeling (the anchor behind the avoidance)
            - Turn 180° opportunities: where they need to feel instead of flee
            
            Return JSON with:
            {
                "procrastination_archetype": "perfectionist",
                "avoidance_signatures": [{"pattern": "perfectionism", "confidence": 0.8, "evidence": "text"}],
                "hedging_language": ["should", "maybe later", "I can't because"],
                "escape_moves": ["analysis", "humor", "busyness"],
                "nervous_system_response": "freeze",
                "protecting_from_feeling": ["inadequacy", "visibility", "judgment"],
                "turn_180_opportunities": ["feel the inadequacy instead of perfecting"],
                "underlying_anchors": ["unworthiness", "fear_of_visibility"]
            }
            """,
            
            "feeling_state_manifestation_analysis": """
            Analyze this text for Becoming One™ manifestation and feeling-state patterns. Look for:
            - Target feeling-states (not objects): safety, belonging, potency, significance, wonder, peace, joy
            - External desires vs. underlying feeling desires (car = freedom, house = safety, partner = belonging)
            - Manifestation style: mental goal-setting vs. feeling-state generation
            - Delay factors: ambiguity, counter-intent, somatic resistance, loyalty debts
            - Bridge-of-incidents: tiny acts that match the feeling-state
            - Synchronicities: meaningful coincidences as navigation beacons
            
            Return JSON with:
            {
                "target_feelings": [{"feeling": "belonging", "confidence": 0.8, "evidence": "text"}],
                "external_desires": ["house", "relationship", "career"],
                "underlying_feeling_desire": "safety",
                "manifestation_style": "mental_goal_setting",
                "delay_factors": ["ambiguity about what they really want", "loyalty to family's expectations"],
                "bridge_opportunities": ["one tiny ask per day", "micro-commitment that honors the feeling"],
                "synchronicity_patterns": ["mentors appearing", "resources showing up"],
                "time_compression_potential": 0.7
            }
            """,
            
            "synthesis_analysis": """
            Based on all the personality analysis data provided, create a synthesis that:
            1. Identifies core patterns across all systems
            2. Finds correlations and contradictions
            3. Generates personalized Becoming One™ guidance
            4. Recommends specific practices and growth edges
            
            Consider how the traditional systems (Enneagram, Human Design, etc.) 
            intersect with the Becoming One™ dimensions of essence level and vertical development.
            
            Return JSON with comprehensive synthesis insights.
            """
        }
    
    async def analyze_message(
        self, 
        person_id: uuid.UUID, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze a single message for personality indicators across all systems
        """
        analysis_results = {}
        
        # Run parallel analysis across all systems
        systems_to_analyze = [
            "enneagram_analysis",
            "human_design_analysis", 
            "emotional_anchor_analysis",
            "avoidance_pattern_analysis",
            "feeling_state_manifestation_analysis"
        ]
        
        for system in systems_to_analyze:
            try:
                result = await self._analyze_with_system(system, message, context)
                analysis_results[system] = result
            except Exception as e:
                print(f"Error analyzing {system}: {e}")
                analysis_results[system] = {"error": str(e)}
        
        # Add metadata
        analysis_results["metadata"] = {
            "person_id": str(person_id),
            "message_length": len(message),
            "analysis_timestamp": datetime.now().isoformat(),
            "context_provided": context is not None
        }
        
        return analysis_results
    
    async def _analyze_with_system(
        self, 
        system: str, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run analysis for a specific personality system
        """
        system_prompt = f"""
        You are an expert in personality analysis using the {system.replace('_', ' ')} framework.
        
        {self.analysis_prompts[system]}
        
        Text to analyze: "{message}"
        
        Context: {json.dumps(context) if context else "None provided"}
        
        Provide detailed analysis in the requested JSON format.
        Be specific about evidence found in the text.
        Use confidence scores based on strength of indicators.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Analyze this message: {message}"}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON response
            try:
                return json.loads(result_text)
            except json.JSONDecodeError:
                # If not valid JSON, return as text with error flag
                return {
                    "raw_analysis": result_text,
                    "json_parse_error": True
                }
                
        except Exception as e:
            return {"error": f"OpenAI API error: {str(e)}"}
    
    async def update_personality_profile(
        self, 
        person_id: uuid.UUID, 
        analysis_results: Dict[str, Any],
        existing_profile: Optional[SynthesisPersonalityProfile] = None
    ) -> SynthesisPersonalityProfile:
        """
        Update or create personality synthesis profile based on new analysis
        """
        if existing_profile:
            profile = existing_profile
        else:
            profile = SynthesisPersonalityProfile(person_id=person_id)
        
        # Process each system's analysis results
        self._process_enneagram_analysis(profile, analysis_results.get("enneagram_analysis", {}))
        self._process_human_design_analysis(profile, analysis_results.get("human_design_analysis", {}))
        self._process_emotional_anchor_analysis(profile, analysis_results.get("emotional_anchor_analysis", {}))
        self._process_avoidance_analysis(profile, analysis_results.get("avoidance_pattern_analysis", {}))
        self._process_essence_level_analysis(profile, analysis_results.get("essence_level_analysis", {}))
        
        # Update synthesis insights
        await self._update_synthesis_insights(profile, analysis_results)
        
        profile.last_updated = datetime.now()
        return profile
    
    def _process_enneagram_analysis(self, profile: SynthesisPersonalityProfile, analysis: Dict[str, Any]):
        """Process Enneagram analysis results"""
        if not analysis or "error" in analysis:
            return
        
        # Update confidence scores and profile data
        primary_indicators = analysis.get("primary_type_indicators", [])
        if primary_indicators:
            # Find highest confidence type
            best_match = max(primary_indicators, key=lambda x: x.get("confidence", 0))
            if best_match.get("confidence", 0) > 0.6:  # Threshold for updating
                if not profile.enneagram:
                    from .personality_synthesis_model import EnneagramProfile
                    profile.enneagram = EnneagramProfile(
                        core_type=EnneagramType(best_match["type"])
                    )
                
                # Update confidence tracking
                profile.confidence_scores["enneagram"] = best_match["confidence"]
    
    def _process_human_design_analysis(self, profile: SynthesisPersonalityProfile, analysis: Dict[str, Any]):
        """Process Human Design analysis results"""
        if not analysis or "error" in analysis:
            return
        
        type_indicators = analysis.get("type_indicators", [])
        if type_indicators:
            best_match = max(type_indicators, key=lambda x: x.get("confidence", 0))
            if best_match.get("confidence", 0) > 0.6:
                if not profile.human_design:
                    from .personality_synthesis_model import HumanDesignProfile
                    profile.human_design = HumanDesignProfile(
                        type=HDType(best_match["type"]),
                        strategy=HDType(best_match["type"]).value,  # Simplified mapping
                        authority="emotional"  # Default, would be determined by full analysis
                    )
                
                profile.confidence_scores["human_design"] = best_match["confidence"]
    
    def _process_emotional_anchor_analysis(self, profile: SynthesisPersonalityProfile, analysis: Dict[str, Any]):
        """Process emotional anchor analysis results"""
        if not analysis or "error" in analysis:
            return
        
        anchor_activations = analysis.get("anchor_activations", [])
        if anchor_activations:
            if not profile.becoming_one:
                from .personality_synthesis_model import BecomingOneProfile
                profile.becoming_one = BecomingOneProfile(
                    primary_essence_level=EssenceLevel.EMOTIONAL,
                    current_vertical_stage=VerticalStage.PERSONALITY,
                    manifestation_style=ManifestationStyle.EMOTIONAL_FEELING_STATE
                )
            
            # Update dominant anchor patterns
            high_confidence_anchors = [
                EmotionalAnchorPattern(a["anchor"]) 
                for a in anchor_activations 
                if a.get("intensity", 0) > 0.7
            ]
            
            if high_confidence_anchors:
                profile.becoming_one.dominant_anchor_patterns = high_confidence_anchors[:3]  # Top 3
    
    def _process_avoidance_analysis(self, profile: SynthesisPersonalityProfile, analysis: Dict[str, Any]):
        """Process avoidance pattern analysis results"""
        if not analysis or "error" in analysis:
            return
        
        avoidance_signatures = analysis.get("avoidance_signatures", [])
        if avoidance_signatures and profile.becoming_one:
            high_confidence_patterns = [
                AvoidanceSignature(a["pattern"])
                for a in avoidance_signatures
                if a.get("confidence", 0) > 0.7
            ]
            
            if high_confidence_patterns:
                profile.becoming_one.avoidance_signatures = high_confidence_patterns[:3]
    
    def _process_essence_level_analysis(self, profile: SynthesisPersonalityProfile, analysis: Dict[str, Any]):
        """Process essence level analysis results"""
        if not analysis or "error" in analysis:
            return
        
        if not profile.becoming_one:
            from .personality_synthesis_model import BecomingOneProfile
            profile.becoming_one = BecomingOneProfile(
                primary_essence_level=EssenceLevel.EMOTIONAL,
                current_vertical_stage=VerticalStage.PERSONALITY,
                manifestation_style=ManifestationStyle.EMOTIONAL_FEELING_STATE
            )
        
        primary_level = analysis.get("primary_level")
        if primary_level:
            profile.becoming_one.primary_essence_level = EssenceLevel(primary_level)
        
        vertical_stage = analysis.get("vertical_stage")
        if vertical_stage:
            profile.becoming_one.current_vertical_stage = VerticalStage(vertical_stage)
        
        manifestation_style = analysis.get("manifestation_style")
        if manifestation_style:
            profile.becoming_one.manifestation_style = ManifestationStyle(manifestation_style)
    
    async def _update_synthesis_insights(self, profile: SynthesisPersonalityProfile, analysis_results: Dict[str, Any]):
        """Generate synthesis insights across all systems"""
        # Create synthesis prompt with all analysis data
        synthesis_prompt = f"""
        Based on this comprehensive personality analysis, provide synthesis insights:
        
        Analysis Results:
        {json.dumps(analysis_results, indent=2)}
        
        Current Profile Summary:
        - Enneagram: {profile.enneagram.core_type.value if profile.enneagram else "Unknown"}
        - Human Design: {profile.human_design.type.value if profile.human_design else "Unknown"}
        - Essence Level: {profile.becoming_one.primary_essence_level.value if profile.becoming_one else "Unknown"}
        - Vertical Stage: {profile.becoming_one.current_vertical_stage.value if profile.becoming_one else "Unknown"}
        
        Generate:
        1. Core patterns that emerge across systems
        2. Cross-system correlations
        3. Specific Becoming One™ practices for this profile
        4. Growth edges and next development steps
        
        Return as JSON with these fields.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a master synthesizer of personality systems with deep knowledge of the Becoming One™ method."},
                    {"role": "user", "content": synthesis_prompt}
                ],
                temperature=0.4,
                max_tokens=2000
            )
            
            synthesis_text = response.choices[0].message.content.strip()
            
            try:
                synthesis_data = json.loads(synthesis_text)
                
                # Update profile with synthesis insights
                profile.core_patterns = synthesis_data.get("core_patterns", [])
                profile.cross_system_correlations = synthesis_data.get("cross_system_correlations", {})
                profile.recommended_practices = synthesis_data.get("recommended_practices", [])
                profile.growth_edges = synthesis_data.get("growth_edges", [])
                
            except json.JSONDecodeError:
                # Store raw text if JSON parsing fails
                profile.core_patterns = [synthesis_text[:500]]  # Truncated
                
        except Exception as e:
            print(f"Error generating synthesis: {e}")
    
    def generate_personalized_response(
        self, 
        profile: SynthesisPersonalityProfile, 
        current_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        Generate personalized Becoming One™ response based on complete personality synthesis
        """
        # Create personalization prompt
        personalization_prompt = f"""
        Generate a personalized Becoming One™ response for this individual based on their complete personality synthesis.
        
        Current Message: "{current_message}"
        
        Personality Profile:
        - Enneagram: {profile.enneagram.core_type.value if profile.enneagram else "Unknown"}
        - Human Design: {profile.human_design.type.value if profile.human_design else "Unknown"}
        - Essence Level: {profile.becoming_one.primary_essence_level.value if profile.becoming_one else "Unknown"}
        - Vertical Stage: {profile.becoming_one.current_vertical_stage.value if profile.becoming_one else "Unknown"}
        - Dominant Anchors: {[a.value for a in profile.becoming_one.dominant_anchor_patterns] if profile.becoming_one else []}
        - Avoidance Patterns: {[a.value for a in profile.becoming_one.avoidance_signatures] if profile.becoming_one else []}
        - Core Patterns: {profile.core_patterns}
        - Growth Edges: {profile.growth_edges}
        
        Using the Becoming One™ methodology, provide:
        1. Immediate empathetic response
        2. Deeper inquiry question
        3. Specific practice suggestion
        4. Essence-level invitation
        5. Growth edge acknowledgment
        
        Tailor the language, depth, and approach to their specific personality synthesis.
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are a master Becoming One™ facilitator with deep knowledge of personality synthesis."},
                    {"role": "user", "content": personalization_prompt}
                ],
                temperature=0.6,
                max_tokens=1500
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse into structured response (could be improved with better prompting)
            return {
                "personalized_response": response_text,
                "personalization_level": "high",
                "systems_used": self._get_active_systems(profile)
            }
            
        except Exception as e:
            return {
                "personalized_response": "I'm experiencing a temporary issue with personalization. Let me offer this reflection: What feels most alive for you in this moment?",
                "personalization_level": "fallback",
                "error": str(e)
            }
    
    def _get_active_systems(self, profile: SynthesisPersonalityProfile) -> List[str]:
        """Get list of personality systems that have data for this profile"""
        systems = []
        if profile.enneagram:
            systems.append("enneagram")
        if profile.human_design:
            systems.append("human_design")
        if profile.astrology:
            systems.append("astrology")
        if profile.maya_calendar:
            systems.append("maya_calendar")
        if profile.jungian:
            systems.append("jungian")
        if profile.becoming_one:
            systems.append("becoming_one")
        return systems


# ============================================================================
# PATTERN DETECTION UTILITIES
# ============================================================================

class PatternDetector:
    """
    Utility class for detecting specific patterns in text
    """
    
    @staticmethod
    def detect_hedging_language(text: str) -> List[str]:
        """Detect hedging and avoidance language patterns"""
        hedging_patterns = [
            r'\bshould\b', r'\bmust\b', r'\bhave to\b',
            r'\bmaybe\b', r'\bperhaps\b', r'\bpossibly\b',
            r'\bI can\'t because\b', r'\bI don\'t have time\b',
            r'\bI\'m not ready\b', r'\bwhen I\b.*\bthen I\b',
            r'\bif only\b', r'\bbut first I need to\b'
        ]
        
        found_patterns = []
        for pattern in hedging_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            found_patterns.extend(matches)
        
        return found_patterns
    
    @staticmethod
    def detect_somatic_markers(text: str) -> List[str]:
        """Detect body-based and somatic indicators"""
        somatic_patterns = [
            r'\btense\b', r'\btight\b', r'\bheavy\b', r'\blight\b',
            r'\bbreathing\b', r'\bbreath\b', r'\bchest\b', r'\bheart\b',
            r'\bstomach\b', r'\bgut\b', r'\bthroat\b', r'\bshoulders\b',
            r'\benergy\b', r'\btired\b', r'\bexhausted\b', r'\balive\b'
        ]
        
        found_markers = []
        for pattern in somatic_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            found_markers.extend(matches)
        
        return found_markers
    
    @staticmethod
    def detect_time_patterns(text: str) -> Dict[str, bool]:
        """Detect time-related patterns indicating avoidance"""
        return {
            "future_focus": bool(re.search(r'\bwhen I\b|\bafter I\b|\bonce I\b', text, re.IGNORECASE)),
            "urgency": bool(re.search(r'\bneed to\b|\bhurry\b|\bquickly\b|\basap\b', text, re.IGNORECASE)),
            "delays": bool(re.search(r'\blater\b|\btomorrow\b|\bnext week\b|\bsomeday\b', text, re.IGNORECASE)),
            "overwhelm": bool(re.search(r'\btoo much\b|\bcan\'t handle\b|\boverwhelmed\b', text, re.IGNORECASE))
        }
