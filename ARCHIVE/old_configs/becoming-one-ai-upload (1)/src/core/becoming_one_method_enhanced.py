"""
Enhanced Becoming One™ Method Integration
=========================================

Based on Johan's comprehensive chat revealing the core methodology:
- Manifestation through feeling-states, not objects
- Emotional anchors as energy bonds that must be felt/digested
- Procrastination/avoidance as portals, not problems
- The Pearl/Pearls as specific transformational insights
- Anti-bypass approach: turn 180° toward feeling everything
- Nervous system protection as the evolutionary bottleneck
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import uuid
from datetime import datetime


# ============================================================================
# CORE BECOMING ONE™ CONCEPTS FROM THE CHAT
# ============================================================================

class FeelingPrimitive(Enum):
    """Core feeling-states humans actually seek (not objects)"""
    SAFETY = "safety"
    BELONGING = "belonging"
    POTENCY = "potency"
    INNOCENCE = "innocence"
    SIGNIFICANCE = "significance"
    WONDER = "wonder"
    DEVOTION = "devotion"
    QUIET_CERTAINTY = "quiet_certainty"
    FEARLESS_TENDERNESS = "fearless_tenderness"
    ALIVENESS = "aliveness"
    FREEDOM = "freedom"
    PEACE = "peace"
    JOY = "joy"
    LOVE = "love"
    POWER = "power"
    CLARITY = "clarity"
    STEADINESS = "steadiness"
    WARMTH = "warmth"

class EmotionalAnchor(Enum):
    """Stored emotional matter that creates 'anchors in time'"""
    ABANDONMENT = "abandonment"
    UNWORTHINESS = "unworthiness"
    POWERLESSNESS = "powerlessness"
    BETRAYAL = "betrayal"
    INJUSTICE = "injustice"
    REJECTION = "rejection"
    HUMILIATION = "humiliation"
    SHAME = "shame"
    FEAR_OF_BIGNESS = "fear_of_bigness"
    LOYALTY_TO_SMALLNESS = "loyalty_to_smallness"
    FEAR_OF_VISIBILITY = "fear_of_visibility"
    FEAR_OF_HAVING = "fear_of_having"
    LOYALTY_DEBT_TO_FAMILY = "loyalty_debt_to_family"
    LOYALTY_DEBT_TO_TRIBE = "loyalty_debt_to_tribe"
    LOYALTY_DEBT_TO_OLD_SELF = "loyalty_debt_to_old_self"

class AvoidancePattern(Enum):
    """Ways the nervous system protects from feeling anchors"""
    PROCRASTINATION = "procrastination"
    PERFECTIONISM = "perfectionism"
    PEOPLE_PLEASING = "people_pleasing"
    DISTRACTION = "distraction"
    NUMBING = "numbing"
    AGGRESSION = "aggression"
    WITHDRAWAL = "withdrawal"
    BUSY_NESS = "busy_ness"
    ANALYSIS_PARALYSIS = "analysis_paralysis"
    HUMOR_DEFLECTION = "humor_deflection"
    SPEED = "speed"
    HELPFULNESS = "helpfulness"

class ProcrastinationArchetype(Enum):
    """Specific procrastination patterns from the chat"""
    FOG_WALKER = "fog_walker"           # "I don't know where to start"
    PERFECTIONIST = "perfectionist"     # "It needs to be perfect or I shut down"
    SHAME_AVOIDER = "shame_avoider"     # Avoiding feelings of inadequacy
    OVERWHELM_FREEZER = "overwhelm_freezer"  # "It's too much"
    MEANING_SEEKER = "meaning_seeker"   # "What's the point?"
    DISTRACTION_DANCER = "distraction_dancer"  # "I keep getting distracted"

class AnchorSignature(Enum):
    """Age epochs where anchors typically form"""
    CONCEPTION = "conception"
    INFANCY = "infancy_0_2"
    EARLY_CHILDHOOD = "early_childhood_3_6"
    SCHOOL_AGE = "school_age_7_12"
    ADOLESCENCE = "adolescence_13_18"
    EARLY_ADULT = "early_adult_19_25"
    ADULT = "adult_26_plus"
    PAST_LIFE = "past_life"  # From the chat: "past life recurrencies"

class ManifestationStyle(Enum):
    """How someone approaches creating their desires"""
    MENTAL_GOAL_SETTING = "mental_goal_setting"  # Traditional approach
    EMOTIONAL_FEELING_STATE = "emotional_feeling_state"  # Becoming One™ way
    SOMATIC_BODY_WISDOM = "somatic_body_wisdom"
    ESSENTIAL_BEINGNESS = "essential_beingness"
    DELAY_COMPRESSION = "delay_compression"  # From chat: collapsing time lag

class NervousSystemResponse(Enum):
    """How the nervous system reacts to anchor activation"""
    FREEZE = "freeze"
    FAWN = "fawn"
    FIGHT = "fight"
    FLIGHT = "flight"
    NUMB = "numb"
    COLLAPSE = "collapse"

# ============================================================================
# BECOMING ONE™ SPECIFIC METRICS (FROM THE CHAT)
# ============================================================================

@dataclass
class BecomingOneMetrics:
    """Metrics specific to the Becoming One™ method"""
    
    # Core metrics from the chat
    feeling_availability: float = 0.0  # FA: % of day target feeling is accessible
    time_to_shift: float = 0.0  # TTS: time from protocol start → reliable feeling access
    energy_release_index: float = 0.0  # ERI: vitality delta post-burn
    
    # Additional metrics
    anchor_load_index: float = 0.0  # How many active anchors are pulling
    avoidance_frequency: int = 0  # Avoidance moves per day
    decisive_acts_per_week: int = 0  # Actual bridges crossed
    kept_wins_rate: float = 0.0  # % of breakthroughs that stabilize
    recurrencies_per_month: int = 0  # Repeating patterns
    
    # From the chat: "Feeling-Shift Effect Size"
    feeling_shift_effect_size: float = 0.0  # Pre/post felt availability
    
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class Pearl:
    """The Pearl/Pearls - specific transformational insights (from chat)"""
    pearl_id: uuid.UUID = field(default_factory=uuid.uuid4)
    insight_text: str = ""
    feeling_unlocked: Optional[FeelingPrimitive] = None
    anchor_dissolved: Optional[EmotionalAnchor] = None
    quality_gained: str = ""  # steadiness, warmth, clarity, etc.
    discovered_at: datetime = field(default_factory=datetime.now)
    integration_status: str = "fresh"  # fresh, integrating, stabilized

@dataclass
class AnchorBurn:
    """Record of emotional anchor digestion/burning session"""
    anchor_type: EmotionalAnchor
    age_epoch: AnchorSignature
    burn_id: uuid.UUID = field(default_factory=uuid.uuid4)
    intensity_before: float = 0.0  # 0-1 scale
    intensity_after: float = 0.0
    duration_minutes: int = 0
    protocol_used: str = ""
    replacement_benefit: str = ""  # What the anchor provided that needs replacing
    secondary_gain: str = ""  # Hidden benefit of keeping the anchor
    energy_released: float = 0.0  # ERI measurement
    decisive_act_taken: str = ""  # Bridge crossed in the world
    integration_notes: str = ""
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class AvoidanceSignature:
    """Detailed pattern of how someone avoids feeling anchors"""
    primary_pattern: AvoidancePattern
    signature_id: uuid.UUID = field(default_factory=uuid.uuid4)
    hedging_language: List[str] = field(default_factory=list)  # "should", "maybe", "I can't because"
    somatic_markers: List[str] = field(default_factory=list)  # body sensations
    behavioral_markers: List[str] = field(default_factory=list)  # actions taken
    time_patterns: Dict[str, Any] = field(default_factory=dict)  # when avoidance occurs
    triggers: List[str] = field(default_factory=list)
    loyalty_debt: Optional[str] = None  # to whom/what
    underlying_anchor: Optional[EmotionalAnchor] = None
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class ManifestationDesire:
    """What someone wants to manifest (feeling-state first)"""
    target_feeling: FeelingPrimitive  # The actual desire
    desire_id: uuid.UUID = field(default_factory=uuid.uuid4)
    external_form: str = ""  # The car, house, relationship, etc.
    end_scene: str = ""  # Vivid description of having it
    current_blocks: List[EmotionalAnchor] = field(default_factory=list)
    bridge_acts: List[str] = field(default_factory=list)  # Tiny steps to take
    synchronicities: List[str] = field(default_factory=list)  # Meaningful coincidences
    delay_factors: List[str] = field(default_factory=list)  # What creates time lag
    created_at: datetime = field(default_factory=datetime.now)
    manifestation_status: str = "clarifying"  # clarifying, feeling, acting, integrating, complete

# ============================================================================
# BECOMING ONE™ PROTOCOL DEFINITIONS
# ============================================================================

@dataclass
class BecomingOneProtocol:
    """Specific protocols from the method"""
    protocol_id: str
    name: str
    description: str
    target_feeling: Optional[FeelingPrimitive] = None
    anchor_types: List[EmotionalAnchor] = field(default_factory=list)
    duration_minutes: int = 7  # Default from chat
    intensity_level: float = 0.6  # Consent thermostat
    contraindications: List[str] = field(default_factory=list)
    sequence: List[Dict[str, Any]] = field(default_factory=list)
    metrics_tracked: List[str] = field(default_factory=list)

# Standard protocols from the chat
TURN_180_PROTOCOL = BecomingOneProtocol(
    protocol_id="turn_180_v1",
    name="The 180° Turn",
    description="Train meeting—not minimizing—unpleasantness",
    duration_minutes=6,
    sequence=[
        {"step": "orient", "duration_s": 20, "instruction": "name place time; consent check"},
        {"step": "evoke", "duration_s": 45, "instruction": "invite the tug; stop before overwhelm"},
        {"step": "stay_with", "duration_s": 90, "instruction": "label urges to fix/flee; do nothing"},
        {"step": "soften", "duration_s": 60, "instruction": "micro-postures: jaw, throat, palms"},
        {"step": "allow_wave", "duration_s": 60, "instruction": "track peak → settle"},
        {"step": "reconsolidate", "duration_s": 45, "instruction": "install replacement benefit"},
        {"step": "decisive_act", "duration_s": 30, "instruction": "choose 1 step today"}
    ],
    metrics_tracked=["feeling_availability", "time_to_shift", "energy_release_index"]
)

ANCHOR_FURNACE_PROTOCOL = BecomingOneProtocol(
    protocol_id="anchor_furnace_v1",
    name="Anchor Furnace",
    description="Guided 6-9 min burn to digest stored emotional matter",
    duration_minutes=8,
    sequence=[
        {"step": "evoke_anchor", "duration_s": 60, "instruction": "bring up the stored emotion"},
        {"step": "name_secondary_gain", "duration_s": 30, "instruction": "what benefit does this provide?"},
        {"step": "feel_to_completion", "duration_s": 240, "instruction": "stay with sensation until natural completion"},
        {"step": "install_replacement", "duration_s": 60, "instruction": "install safe substitute benefit"},
        {"step": "bridge_act", "duration_s": 30, "instruction": "choose one decisive act today"}
    ],
    metrics_tracked=["feeling_availability", "time_to_shift", "energy_release_index", "anchor_load_index"]
)

# ============================================================================
# ANALYSIS PROMPTS ENHANCED WITH BECOMING ONE™ TERMINOLOGY
# ============================================================================

BECOMING_ONE_ANALYSIS_PROMPTS = {
    "feeling_state_analysis": """
    Analyze this text for Becoming One™ feeling-state indicators. Look for:
    - Target feeling-states (safety, belonging, potency, significance, etc.)
    - External desires vs. underlying feeling desires
    - Manifestation style indicators
    - Delay-compression opportunities
    
    Return JSON with:
    {
        "target_feelings": [{"feeling": "safety", "confidence": 0.8, "evidence": "text"}],
        "external_desires": ["car", "relationship", "house"],
        "underlying_feeling_desire": "belonging",
        "manifestation_style": "mental_goal_setting",
        "delay_factors": ["ambiguity", "counter_intent", "somatic_resistance"]
    }
    """,
    
    "anchor_detection_analysis": """
    Analyze this text for emotional anchors using Becoming One™ framework. Look for:
    - Stored emotional matter from different age epochs
    - Secondary gains from keeping blocks
    - Loyalty debts (to family, tribe, old self)
    - Somatic markers and body sensations
    - Past-life or ancestral recurrencies
    
    Return JSON with:
    {
        "active_anchors": [{"anchor": "unworthiness", "intensity": 0.7, "age_epoch": "school_age", "evidence": "text"}],
        "loyalty_debts": [{"to_whom": "family", "vow": "I mustn't surpass them"}],
        "secondary_gains": ["predictability", "belonging", "safety"],
        "somatic_markers": ["tight chest", "shallow breathing"],
        "recurrency_indicators": ["abandonment theme repeating"]
    }
    """,
    
    "avoidance_pattern_analysis": """
    Analyze this text for avoidance patterns using Becoming One™ anti-bypass framework. Look for:
    - Procrastination archetypes (fog walker, perfectionist, shame avoider)
    - Hedging language and escape moves
    - Nervous system responses (freeze, flight, fight, fawn)
    - What they're protecting themselves from feeling
    
    Return JSON with:
    {
        "procrastination_archetype": "perfectionist",
        "avoidance_patterns": [{"pattern": "perfectionism", "confidence": 0.8}],
        "hedging_language": ["should", "maybe later", "I can't because"],
        "nervous_system_response": "freeze",
        "protecting_from_feeling": ["inadequacy", "visibility", "judgment"],
        "escape_moves": ["analysis", "humor", "busyness"]
    }
    """,
    
    "pearl_extraction_analysis": """
    Analyze this text for Pearls - transformational insights in Becoming One™ terms. Look for:
    - Moments of clarity or breakthrough
    - Qualities gained (steadiness, warmth, clarity)
    - Shifts in capacity or understanding
    - Integration of previously avoided material
    
    Return JSON with:
    {
        "pearls_identified": [{"insight": "I can feel anger without becoming it", "quality_gained": "steadiness"}],
        "capacity_shifts": ["increased tolerance for uncertainty"],
        "integration_markers": ["able to stay present during conflict"],
        "feeling_availability_changes": [{"feeling": "potency", "before": 0.2, "after": 0.7}]
    }
    """
}

# ============================================================================
# BECOMING ONE™ SPECIFIC PATTERN DETECTION
# ============================================================================

class BecomingOnePatternDetector:
    """Pattern detection specifically for Becoming One™ methodology"""
    
    @staticmethod
    def detect_hedging_language(text: str) -> List[str]:
        """Detect language that indicates avoidance (from the chat)"""
        hedging_patterns = [
            r'\bshould\b', r'\bmust\b', r'\bhave to\b',
            r'\bmaybe\b', r'\bperhaps\b', r'\bpossibly\b',
            r'\bI can\'t because\b', r'\bI don\'t have time\b',
            r'\bI\'m not ready\b', r'\bwhen I\b.*\bthen I\b',
            r'\bif only\b', r'\bbut first I need to\b',
            r'\blater\b', r'\btomorrow\b', r'\bnext week\b',
            r'\bsomeday\b', r'\bafter I\b', r'\bonce I\b'
        ]
        
        found_patterns = []
        for pattern in hedging_patterns:
            import re
            matches = re.findall(pattern, text, re.IGNORECASE)
            found_patterns.extend(matches)
        
        return found_patterns
    
    @staticmethod
    def detect_loyalty_debts(text: str) -> List[Dict[str, str]]:
        """Detect loyalty conflicts that prevent growth"""
        loyalty_patterns = {
            "family": [r"my family", r"my parents", r"my mother", r"my father"],
            "tribe": [r"my community", r"my people", r"where I come from"],
            "old_self": [r"I've always been", r"that's not who I am", r"I'm not that kind of person"]
        }
        
        loyalty_debts = []
        for debt_type, patterns in loyalty_patterns.items():
            for pattern in patterns:
                import re
                if re.search(pattern, text, re.IGNORECASE):
                    loyalty_debts.append({
                        "to_whom": debt_type,
                        "evidence": pattern,
                        "context": text[:100] + "..."
                    })
        
        return loyalty_debts
    
    @staticmethod
    def detect_feeling_primitives(text: str) -> List[Dict[str, Any]]:
        """Detect mentions of core feeling-states people actually seek"""
        feeling_keywords = {
            FeelingPrimitive.SAFETY: ["safe", "secure", "protected", "stable"],
            FeelingPrimitive.BELONGING: ["belong", "accepted", "included", "home"],
            FeelingPrimitive.POTENCY: ["powerful", "capable", "strong", "effective"],
            FeelingPrimitive.SIGNIFICANCE: ["important", "matter", "valued", "meaningful"],
            FeelingPrimitive.FREEDOM: ["free", "liberated", "unconstrained", "open"],
            FeelingPrimitive.PEACE: ["peaceful", "calm", "serene", "still"],
            FeelingPrimitive.JOY: ["joyful", "happy", "delighted", "elated"],
            FeelingPrimitive.LOVE: ["loved", "cherished", "adored", "connected"]
        }
        
        detected_feelings = []
        for feeling, keywords in feeling_keywords.items():
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    detected_feelings.append({
                        "feeling": feeling.value,
                        "keyword": keyword,
                        "confidence": 0.7  # Base confidence
                    })
        
        return detected_feelings

# ============================================================================
# INTEGRATION WITH EXISTING PERSONALITY SYSTEM
# ============================================================================

def enhance_personality_profile_with_becoming_one(
    profile: 'SynthesisPersonalityProfile',
    becoming_one_analysis: Dict[str, Any]
) -> 'SynthesisPersonalityProfile':
    """Enhance existing personality profile with Becoming One™ insights"""
    
    if not profile.becoming_one:
        from .personality_synthesis_model import BecomingOneProfile, EssenceLevel, VerticalStage, ManifestationStyle
        profile.becoming_one = BecomingOneProfile(
            primary_essence_level=EssenceLevel.EMOTIONAL,
            current_vertical_stage=VerticalStage.PERSONALITY,
            manifestation_style=ManifestationStyle.EMOTIONAL_FEELING_STATE
        )
    
    # Add Becoming One™ specific insights
    if 'anchor_detection_analysis' in becoming_one_analysis:
        anchor_data = becoming_one_analysis['anchor_detection_analysis']
        if 'active_anchors' in anchor_data:
            profile.becoming_one.dominant_anchor_patterns = [
                anchor['anchor'] for anchor in anchor_data['active_anchors']
                if anchor.get('intensity', 0) > 0.6
            ]
    
    if 'avoidance_pattern_analysis' in becoming_one_analysis:
        avoidance_data = becoming_one_analysis['avoidance_pattern_analysis']
        if 'avoidance_patterns' in avoidance_data:
            profile.becoming_one.avoidance_signatures = [
                pattern['pattern'] for pattern in avoidance_data['avoidance_patterns']
                if pattern.get('confidence', 0) > 0.6
            ]
    
    # Add Pearls if detected
    if 'pearl_extraction_analysis' in becoming_one_analysis:
        pearl_data = becoming_one_analysis['pearl_extraction_analysis']
        if 'pearls_identified' in pearl_data:
            profile.becoming_one.essence_qualities = [
                pearl['quality_gained'] for pearl in pearl_data['pearls_identified']
            ]
    
    return profile
