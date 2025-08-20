import re
import json
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import os

@dataclass
class StrategicScore:
    signal_score: float
    danger_score: float
    quality_score: float
    originality_score: float
    actionability_score: float
    total_score: float
    recommendations: List[str]
    risk_factors: List[str]
    processing_decision: str

class StrategicScorer:
    def __init__(self):
        # Signal indicators - what makes content valuable
        self.signal_indicators = {
            "prompt_patterns": {
                "patterns": [
                    r"#{1,3}\s*system\s*prompt",
                    r"#{1,3}\s*instruction",
                    r"#{1,3}\s*guidance",
                    r"role:\s*\w+",
                    r"persona:\s*\w+",
                    r"behavior:\s*\w+"
                ],
                "weight": 2.0,
                "description": "Contains actual prompt patterns"
            },
            "original_phrases": {
                "min_words": 150,
                "weight": 1.0,
                "description": "Substantial original content"
            },
            "user_input": {
                "patterns": [
                    r"user:\s*\w+",
                    r"human:\s*\w+",
                    r"question:\s*\w+",
                    r"request:\s*\w+"
                ],
                "weight": 1.5,
                "description": "Contains user input/requests"
            },
            "becoming_one_terms": {
                "terms": [
                    "stance", "digest", "emotional anchor", "schaubild", "nervous system",
                    "field", "essence", "anti-bypass", "pearl", "feeling-state",
                    "inner field", "subtle layer", "willb.one", "amanita"
                ],
                "weight": 0.3,
                "description": "Uses Becoming One™ terminology"
            },
            "technical_specificity": {
                "patterns": [
                    r"\b(api|endpoint|database|schema|migration|deployment)\b",
                    r"\b(telegram|supabase|pinecone|railway|fastapi)\b",
                    r"\b(vector|embedding|similarity|query|index)\b"
                ],
                "weight": 1.0,
                "description": "Contains technical specifics"
            },
            "structured_content": {
                "patterns": [
                    r"^#{1,6}\s+\w+",  # Headers
                    r"^\d+\.\s+\w+",   # Numbered lists
                    r"^-\s+\w+",       # Bullet points
                    r"```\w*",         # Code blocks
                    r"`\w+`"           # Inline code
                ],
                "weight": 0.5,
                "description": "Well-structured content"
            }
        }
        
        # Danger indicators - what makes content risky
        self.danger_indicators = {
            "fluff_patterns": {
                "patterns": [
                    r"\b(very|extremely|absolutely|completely|totally)\s+\w+",
                    r"\b(amazing|incredible|fantastic|wonderful|excellent)\s+\w+",
                    r"\b(revolutionary|groundbreaking|innovative|cutting-edge)\s+\w+",
                    r"\b(transformative|life-changing|mind-blowing|game-changing)\s+\w+"
                ],
                "weight": 0.5,
                "description": "Contains fluff language"
            },
            "gpt_style": {
                "patterns": [
                    r"\b(as you can see|as we can observe|it is clear that)\b",
                    r"\b(in conclusion|to summarize|therefore|thus)\b",
                    r"\b(it is important to note|it should be mentioned)\b",
                    r"\b(this represents|this demonstrates|this shows)\b"
                ],
                "weight": 1.0,
                "description": "GPT-style over-explaining"
            },
            "vague_future": {
                "patterns": [
                    r"\b(in the future|eventually|someday|one day)\b",
                    r"\b(we will|we plan to|we intend to|we hope to)\b",
                    r"\b(aspirational|visionary|forward-thinking)\b"
                ],
                "weight": 0.8,
                "description": "Vague future plans without steps"
            },
            "generic_advice": {
                "patterns": [
                    r"\b(always|never|everyone|nobody|everything)\b",
                    r"\b(the key is|the secret is|the answer is)\b",
                    r"\b(simply|just|merely|only)\b"
                ],
                "weight": 0.3,
                "description": "Generic, non-specific advice"
            }
        }
        
        # Quality indicators
        self.quality_indicators = {
            "specific_examples": {
                "patterns": [
                    r"for example",
                    r"such as",
                    r"like",
                    r"including",
                    r"specifically"
                ],
                "weight": 0.5
            },
            "concrete_steps": {
                "patterns": [
                    r"step \d+",
                    r"\d+\.\s+\w+",
                    r"first.*then",
                    r"start with.*next"
                ],
                "weight": 1.0
            },
            "personal_experience": {
                "patterns": [
                    r"i found",
                    r"i discovered",
                    r"i learned",
                    r"my experience",
                    r"when i"
                ],
                "weight": 1.5
            }
        }

    def score_content(self, content: str, file_path: str = "", 
                     additional_context: Dict = None) -> StrategicScore:
        """Score content strategically"""
        
        # Calculate signal score
        signal_score = self._calculate_signal_score(content)
        
        # Calculate danger score
        danger_score = self._calculate_danger_score(content)
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(content)
        
        # Calculate originality score
        originality_score = self._calculate_originality_score(content, additional_context)
        
        # Calculate actionability score
        actionability_score = self._calculate_actionability_score(content)
        
        # Calculate total score
        total_score = self._calculate_total_score(
            signal_score, danger_score, quality_score, 
            originality_score, actionability_score
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            signal_score, danger_score, quality_score, 
            originality_score, actionability_score
        )
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(
            signal_score, danger_score, quality_score
        )
        
        # Make processing decision
        processing_decision = self._make_processing_decision(
            total_score, signal_score, danger_score
        )
        
        return StrategicScore(
            signal_score=signal_score,
            danger_score=danger_score,
            quality_score=quality_score,
            originality_score=originality_score,
            actionability_score=actionability_score,
            total_score=total_score,
            recommendations=recommendations,
            risk_factors=risk_factors,
            processing_decision=processing_decision
        )

    def _calculate_signal_score(self, content: str) -> float:
        """Calculate signal score based on valuable content indicators"""
        score = 0.0
        content_lower = content.lower()
        
        # Check prompt patterns
        for pattern in self.signal_indicators["prompt_patterns"]["patterns"]:
            if re.search(pattern, content_lower, re.IGNORECASE):
                score += self.signal_indicators["prompt_patterns"]["weight"]
        
        # Check original phrases length
        word_count = len(content.split())
        if word_count >= self.signal_indicators["original_phrases"]["min_words"]:
            score += self.signal_indicators["original_phrases"]["weight"]
        
        # Check user input
        for pattern in self.signal_indicators["user_input"]["patterns"]:
            if re.search(pattern, content_lower, re.IGNORECASE):
                score += self.signal_indicators["user_input"]["weight"]
        
        # Check Becoming One terms
        becoming_one_count = 0
        for term in self.signal_indicators["becoming_one_terms"]["terms"]:
            if term.lower() in content_lower:
                becoming_one_count += 1
        
        score += becoming_one_count * self.signal_indicators["becoming_one_terms"]["weight"]
        
        # Check technical specificity
        for pattern in self.signal_indicators["technical_specificity"]["patterns"]:
            if re.search(pattern, content_lower, re.IGNORECASE):
                score += self.signal_indicators["technical_specificity"]["weight"]
        
        # Check structured content
        structure_count = 0
        for pattern in self.signal_indicators["structured_content"]["patterns"]:
            matches = re.findall(pattern, content, re.MULTILINE)
            structure_count += len(matches)
        
        if structure_count >= 3:
            score += self.signal_indicators["structured_content"]["weight"]
        
        return round(min(score, 10.0), 3)  # Cap at 10.0

    def _calculate_danger_score(self, content: str) -> float:
        """Calculate danger score based on risky content indicators"""
        score = 0.0
        content_lower = content.lower()
        
        # Check fluff patterns
        for pattern in self.danger_indicators["fluff_patterns"]["patterns"]:
            matches = re.findall(pattern, content_lower)
            score += len(matches) * self.danger_indicators["fluff_patterns"]["weight"]
        
        # Check GPT style
        for pattern in self.danger_indicators["gpt_style"]["patterns"]:
            if re.search(pattern, content_lower):
                score += self.danger_indicators["gpt_style"]["weight"]
        
        # Check vague future
        for pattern in self.danger_indicators["vague_future"]["patterns"]:
            if re.search(pattern, content_lower):
                score += self.danger_indicators["vague_future"]["weight"]
        
        # Check generic advice
        for pattern in self.danger_indicators["generic_advice"]["patterns"]:
            matches = re.findall(pattern, content_lower)
            score += len(matches) * self.danger_indicators["generic_advice"]["weight"]
        
        return round(min(score, 5.0), 3)  # Cap at 5.0

    def _calculate_quality_score(self, content: str) -> float:
        """Calculate quality score based on content quality indicators"""
        score = 0.0
        content_lower = content.lower()
        
        # Check specific examples
        for pattern in self.quality_indicators["specific_examples"]["patterns"]:
            if re.search(pattern, content_lower):
                score += self.quality_indicators["specific_examples"]["weight"]
        
        # Check concrete steps
        for pattern in self.quality_indicators["concrete_steps"]["patterns"]:
            if re.search(pattern, content_lower):
                score += self.quality_indicators["concrete_steps"]["weight"]
        
        # Check personal experience
        for pattern in self.quality_indicators["personal_experience"]["patterns"]:
            if re.search(pattern, content_lower):
                score += self.quality_indicators["personal_experience"]["weight"]
        
        return round(min(score, 5.0), 3)  # Cap at 5.0

    def _calculate_originality_score(self, content: str, additional_context: Dict = None) -> float:
        """Calculate originality score"""
        score = 0.0
        
        # Base originality on unique word ratio
        words = content.lower().split()
        unique_words = set(words)
        
        if len(words) > 0:
            uniqueness_ratio = len(unique_words) / len(words)
            score += uniqueness_ratio * 2.0
        
        # Bonus for domain-specific terms
        domain_terms = [
            "schaubild", "emotional anchor", "stance", "field", "essence",
            "nervous system", "digest", "pearl", "anti-bypass"
        ]
        
        domain_term_count = sum(1 for term in domain_terms if term.lower() in content.lower())
        score += domain_term_count * 0.3
        
        # Bonus for personal pronouns (indicates original thought)
        personal_pronouns = ["i", "me", "my", "we", "our", "us"]
        pronoun_count = sum(1 for pronoun in personal_pronouns if pronoun in content.lower())
        score += pronoun_count * 0.1
        
        return round(min(score, 5.0), 3)  # Cap at 5.0

    def _calculate_actionability_score(self, content: str) -> float:
        """Calculate actionability score"""
        score = 0.0
        content_lower = content.lower()
        
        # Action verbs
        action_verbs = [
            "do", "make", "create", "build", "implement", "start", "begin",
            "try", "test", "experiment", "practice", "apply", "use"
        ]
        
        action_verb_count = sum(1 for verb in action_verbs if verb in content_lower)
        score += action_verb_count * 0.2
        
        # Imperative sentences
        imperative_patterns = [
            r"^\w+[^.!?]*[.!?]$",  # Sentences ending with punctuation
            r"start with",
            r"begin by",
            r"try this",
            r"do this"
        ]
        
        for pattern in imperative_patterns:
            if re.search(pattern, content_lower, re.MULTILINE):
                score += 0.5
        
        # Numbered steps
        step_patterns = [
            r"\d+\.\s+\w+",
            r"step \d+",
            r"first.*second",
            r"1\..*2\."
        ]
        
        for pattern in step_patterns:
            if re.search(pattern, content_lower):
                score += 1.0
        
        return round(min(score, 5.0), 3)  # Cap at 5.0

    def _calculate_total_score(self, signal_score: float, danger_score: float,
                             quality_score: float, originality_score: float,
                             actionability_score: float) -> float:
        """Calculate total strategic score"""
        # Base score from signal and quality
        base_score = signal_score + quality_score + originality_score + actionability_score
        
        # Penalty for danger
        penalty = danger_score * 0.5
        
        total_score = base_score - penalty
        
        return round(max(total_score, 0.0), 3)  # Minimum 0.0

    def _generate_recommendations(self, signal_score: float, danger_score: float,
                                quality_score: float, originality_score: float,
                                actionability_score: float) -> List[str]:
        """Generate recommendations based on scores"""
        recommendations = []
        
        if signal_score >= 5.0:
            recommendations.append("High signal content - prioritize for Compass core")
        
        if danger_score >= 3.0:
            recommendations.append("High danger score - review carefully before inclusion")
        
        if quality_score >= 3.0:
            recommendations.append("High quality content - ready for immediate use")
        
        if originality_score >= 3.0:
            recommendations.append("High originality - valuable unique insights")
        
        if actionability_score >= 3.0:
            recommendations.append("Highly actionable - implement immediately")
        
        if signal_score < 2.0:
            recommendations.append("Low signal - consider for human review")
        
        if danger_score < 1.0:
            recommendations.append("Low risk - safe for automated processing")
        
        return recommendations

    def _identify_risk_factors(self, signal_score: float, danger_score: float,
                             quality_score: float) -> List[str]:
        """Identify risk factors"""
        risk_factors = []
        
        if danger_score >= 2.0:
            risk_factors.append("High AI-generated content risk")
        
        if signal_score < 1.0:
            risk_factors.append("Very low signal content")
        
        if quality_score < 1.0:
            risk_factors.append("Poor content quality")
        
        if danger_score >= 1.0 and signal_score < 3.0:
            risk_factors.append("High risk, low reward content")
        
        return risk_factors

    def _make_processing_decision(self, total_score: float, signal_score: float,
                                danger_score: float) -> str:
        """Make processing decision based on scores"""
        
        if total_score >= 8.0 and danger_score <= 1.0:
            return "SAFE_CORE - Add directly to Compass core"
        
        if signal_score >= 5.0 and danger_score <= 2.0:
            return "REVIEW_CORE - Review then add to Compass core"
        
        if total_score >= 5.0:
            return "RESCUE_QUEUE - High potential, needs refinement"
        
        if danger_score >= 3.0:
            return "QUARANTINE - High risk content"
        
        if signal_score >= 2.0:
            return "HUMAN_REVIEW - Needs human assessment"
        
        return "DRAFT - Low priority, save for later"

    def should_add_to_compass_core(self, score: StrategicScore) -> bool:
        """Determine if content should be added to Compass core"""
        return score.processing_decision.startswith("SAFE_CORE") or \
               score.processing_decision.startswith("REVIEW_CORE")

    def get_priority_level(self, score: StrategicScore) -> str:
        """Get priority level for processing"""
        if score.total_score >= 8.0:
            return "critical"
        elif score.total_score >= 5.0:
            return "high"
        elif score.total_score >= 3.0:
            return "medium"
        else:
            return "low"

# Example usage
if __name__ == "__main__":
    scorer = StrategicScorer()
    
    # Test content
    test_content = """
    # System Prompt for Emotional Anchor Processing
    
    When working with emotional anchors, start with stance work.
    First, establish your inner field awareness. Then, begin the digest process.
    
    ## Step-by-Step Process:
    1. Recognize the emotional anchor
    2. Access your nervous system response
    3. Apply the anti-bypass approach
    4. Extract the pearl of wisdom
    
    I found that this method works best when you practice regularly.
    Try this approach for at least 10 minutes daily.
    
    This represents a comprehensive framework for personal development.
    """
    
    score = scorer.score_content(test_content, "test_file.md")
    
    print(f"Signal Score: {score.signal_score}")
    print(f"Danger Score: {score.danger_score}")
    print(f"Quality Score: {score.quality_score}")
    print(f"Originality Score: {score.originality_score}")
    print(f"Actionability Score: {score.actionability_score}")
    print(f"Total Score: {score.total_score}")
    print(f"Processing Decision: {score.processing_decision}")
    print(f"Recommendations: {score.recommendations}")
    print(f"Risk Factors: {score.risk_factors}")
    print(f"Priority Level: {scorer.get_priority_level(score)}")
    print(f"Add to Compass Core: {scorer.should_add_to_compass_core(score)}")
