import re
import json
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class FluffAnalysis:
    fluff_score: float
    signal_score: float
    danger_score: float
    rescue_reasons: List[str]
    domain_terms: List[str]
    structure_quality: str
    recommendation: str
    confidence: float

class EnhancedFluffDetector:
    def __init__(self):
        # Domain-specific terms that indicate valuable content
        self.domain_terms = {
            "becoming_one": [
                "stance", "digest", "inner field", "schaubild", "compass", 
                "subtle layer", "nervous system", "emotional anchor", "pearl",
                "feeling-state", "anti-bypass", "essence", "field-aware",
                "willb.one", "amanita", "microdosing", "personality mapping"
            ],
            "method_core": [
                "system prompt", "persona", "agent logic", "role", "deep dive",
                "facilitator training", "capsules", "journey orchestration",
                "omnichannel", "dual-purpose", "knowledge ingestion"
            ],
            "technical": [
                "telegram", "supabase", "pinecone", "railway", "fastapi",
                "vector database", "rbac", "row level security", "migration"
            ]
        }
        
        # Fluff patterns that indicate low-value content
        self.fluff_patterns = [
            r"\b(very|extremely|absolutely|completely|totally)\s+\w+",
            r"\b(amazing|incredible|fantastic|wonderful|excellent)\s+\w+",
            r"\b(revolutionary|groundbreaking|innovative|cutting-edge)\s+\w+",
            r"\b(transformative|life-changing|mind-blowing|game-changing)\s+\w+",
            r"\b(as you know|as we all know|obviously|clearly|naturally)",
            r"\b(in conclusion|to summarize|in summary|therefore|thus)",
            r"\b(it is important to note|it should be mentioned|it is worth noting)",
            r"\b(this is a|this represents|this demonstrates|this shows)",
            r"\b(we can see|we observe|we notice|we find|we discover)",
            r"\b(ultimately|finally|lastly|in the end|at the end of the day)"
        ]
        
        # Danger patterns that indicate AI-generated fluff
        self.danger_patterns = [
            r"\b(comprehensive|thorough|detailed|extensive|complete)\s+analysis",
            r"\b(robust|scalable|efficient|optimized|streamlined)\s+solution",
            r"\b(seamless|smooth|effortless|hassle-free|user-friendly)\s+experience",
            r"\b(innovative|revolutionary|groundbreaking|cutting-edge)\s+approach",
            r"\b(transformative|life-changing|game-changing)\s+impact",
            r"\b(comprehensive|holistic|integrated|unified)\s+framework",
            r"\b(advanced|sophisticated|complex|intricate)\s+system",
            r"\b(future-proof|scalable|flexible|adaptable)\s+architecture"
        ]
        
        # Protected folders that should never be quarantined
        self.protected_folders = [
            "Phase0/10_prompts",
            "Phase1/20_method", 
            "Phase2/30_core",
            "master_prompt",
            "system_prompts"
        ]
        
        # Structure indicators of high-quality content
        self.structure_indicators = [
            r"^#{1,6}\s+\w+",  # Markdown headers
            r"^\d+\.\s+\w+",   # Numbered lists
            r"^-\s+\w+",       # Bullet points
            r"^\*\s+\w+",      # Alternative bullets
            r"```\w*",         # Code blocks
            r"`\w+`",          # Inline code
            r"\[.*\]\(.*\)",   # Links
            r"!\[.*\]\(.*\)",  # Images
        ]

    def analyze_content(self, content: str, file_path: str = "") -> FluffAnalysis:
        """Analyze content for fluff, signal, and danger scores"""
        
        # Check if file is in protected folder
        is_protected = self._is_protected_file(file_path)
        
        # Count domain terms
        domain_terms = self._find_domain_terms(content)
        domain_score = len(domain_terms) * 0.3  # Each domain term adds 0.3 to signal
        
        # Calculate fluff score
        fluff_score = self._calculate_fluff_score(content)
        
        # Calculate signal score
        signal_score = self._calculate_signal_score(content, domain_score)
        
        # Calculate danger score
        danger_score = self._calculate_danger_score(content)
        
        # Analyze structure quality
        structure_quality = self._analyze_structure(content)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(
            fluff_score, signal_score, danger_score, is_protected, structure_quality
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(fluff_score, signal_score, danger_score)
        
        return FluffAnalysis(
            fluff_score=fluff_score,
            signal_score=signal_score,
            danger_score=danger_score,
            rescue_reasons=self._get_rescue_reasons(domain_terms, is_protected, structure_quality),
            domain_terms=domain_terms,
            structure_quality=structure_quality,
            recommendation=recommendation,
            confidence=confidence
        )

    def _is_protected_file(self, file_path: str) -> bool:
        """Check if file is in a protected folder"""
        if not file_path:
            return False
        
        file_path_lower = file_path.lower()
        return any(folder.lower() in file_path_lower for folder in self.protected_folders)

    def _find_domain_terms(self, content: str) -> List[str]:
        """Find domain-specific terms in content"""
        found_terms = []
        content_lower = content.lower()
        
        for category, terms in self.domain_terms.items():
            for term in terms:
                if term.lower() in content_lower:
                    found_terms.append(term)
        
        return found_terms

    def _calculate_fluff_score(self, content: str) -> float:
        """Calculate fluff score based on fluff patterns"""
        score = 0.0
        content_lower = content.lower()
        
        for pattern in self.fluff_patterns:
            matches = re.findall(pattern, content_lower)
            score += len(matches) * 0.1  # Each match adds 0.1 to fluff score
        
        # Normalize by content length
        word_count = len(content.split())
        if word_count > 0:
            score = min(score / (word_count / 100), 1.0)  # Normalize per 100 words
        
        return round(score, 3)

    def _calculate_signal_score(self, content: str, domain_score: float) -> float:
        """Calculate signal score based on valuable content indicators"""
        score = domain_score
        
        # +1 for real prompt patterns
        if re.search(r"#{1,3}\s*system\s*prompt", content, re.IGNORECASE):
            score += 1.0
        
        # +1 for original phrases > 150 words
        if len(content.split()) > 150:
            score += 1.0
        
        # +1 for structured content
        if self._has_good_structure(content):
            score += 1.0
        
        # +1 for specific technical terms
        if re.search(r"\b(api|endpoint|database|schema|migration)\b", content, re.IGNORECASE):
            score += 0.5
        
        return round(min(score, 5.0), 3)  # Cap at 5.0

    def _calculate_danger_score(self, content: str) -> float:
        """Calculate danger score based on AI-generated fluff patterns"""
        score = 0.0
        content_lower = content.lower()
        
        for pattern in self.danger_patterns:
            matches = re.findall(pattern, content_lower)
            score += len(matches) * 0.2  # Each match adds 0.2 to danger score
        
        # +1 for GPT-style over-explaining
        if re.search(r"\b(as you can see|as we can observe|it is clear that)", content_lower):
            score += 1.0
        
        # +1 for vague future plans
        if re.search(r"\b(in the future|eventually|someday|one day)\b", content_lower):
            score += 0.5
        
        return round(min(score, 3.0), 3)  # Cap at 3.0

    def _analyze_structure(self, content: str) -> str:
        """Analyze the structure quality of the content"""
        structure_count = 0
        
        for pattern in self.structure_indicators:
            matches = re.findall(pattern, content, re.MULTILINE)
            structure_count += len(matches)
        
        if structure_count >= 5:
            return "excellent"
        elif structure_count >= 3:
            return "good"
        elif structure_count >= 1:
            return "fair"
        else:
            return "poor"

    def _has_good_structure(self, content: str) -> bool:
        """Check if content has good structure"""
        return self._analyze_structure(content) in ["excellent", "good"]

    def _get_rescue_reasons(self, domain_terms: List[str], is_protected: bool, structure_quality: str) -> List[str]:
        """Get reasons why content should be rescued"""
        reasons = []
        
        if is_protected:
            reasons.append("Protected folder")
        
        if len(domain_terms) >= 2:
            reasons.append(f"Contains {len(domain_terms)} domain terms")
        
        if structure_quality in ["excellent", "good"]:
            reasons.append(f"Good structure quality: {structure_quality}")
        
        return reasons

    def _generate_recommendation(self, fluff_score: float, signal_score: float, 
                               danger_score: float, is_protected: bool, structure_quality: str) -> str:
        """Generate recommendation based on analysis"""
        
        if is_protected:
            return "PROTECTED - Never quarantine"
        
        if signal_score >= 3 and danger_score <= 1:
            return "SAFE - Add to Compass core"
        
        if signal_score >= 2 and fluff_score <= 0.3:
            return "RESCUE - High signal, low fluff"
        
        if danger_score >= 2:
            return "QUARANTINE - High danger score"
        
        if fluff_score >= 0.5:
            return "RESCUE_QUEUE - High fluff, needs review"
        
        return "DRAFT - Needs human review"

    def _calculate_confidence(self, fluff_score: float, signal_score: float, danger_score: float) -> float:
        """Calculate confidence in the analysis"""
        # Higher confidence when scores are more extreme
        confidence = 0.5  # Base confidence
        
        if fluff_score > 0.7 or fluff_score < 0.1:
            confidence += 0.2
        
        if signal_score > 3 or signal_score < 1:
            confidence += 0.2
        
        if danger_score > 2 or danger_score < 0.5:
            confidence += 0.1
        
        return round(min(confidence, 1.0), 3)

    def should_quarantine(self, analysis: FluffAnalysis) -> bool:
        """Determine if content should be quarantined"""
        if analysis.recommendation.startswith("PROTECTED"):
            return False
        
        if analysis.recommendation.startswith("QUARANTINE"):
            return True
        
        return analysis.fluff_score > 0.7 and analysis.signal_score < 2

    def get_processing_path(self, analysis: FluffAnalysis, file_path: str) -> str:
        """Determine the processing path for the file"""
        if analysis.recommendation.startswith("PROTECTED"):
            return "protected"
        
        if analysis.recommendation.startswith("SAFE"):
            return "compass_core"
        
        if analysis.recommendation.startswith("RESCUE"):
            return "rescue_queue"
        
        if analysis.recommendation.startswith("QUARANTINE"):
            return "quarantine"
        
        return "drafts"

# Example usage
if __name__ == "__main__":
    detector = EnhancedFluffDetector()
    
    # Test content
    test_content = """
    # System Prompt for Becoming One™ Method
    
    The nervous system plays a crucial role in emotional anchor digestion.
    Through careful stance work and inner field awareness, we can access
    the subtle layers of consciousness.
    
    ## Key Components:
    1. Emotional anchor recognition
    2. Schaubild integration
    3. Field-aware processing
    
    This represents a comprehensive framework for personal development.
    """
    
    analysis = detector.analyze_content(test_content, "Phase1/20_method/test.md")
    print(f"Fluff Score: {analysis.fluff_score}")
    print(f"Signal Score: {analysis.signal_score}")
    print(f"Danger Score: {analysis.danger_score}")
    print(f"Recommendation: {analysis.recommendation}")
    print(f"Rescue Reasons: {analysis.rescue_reasons}")
    print(f"Domain Terms: {analysis.domain_terms}")
