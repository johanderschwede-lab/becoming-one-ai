# build this

from typing import Dict, List, Tuple
import re

class FluffDetector:
    def __init__(self):
        # Buzzword patterns that often indicate AI fluff
        self.buzzword_patterns = [
            r"unified\s+\w+\s+protocol",
            r"revolutionary\s+breakthrough",
            r"paradigm\s+shift",
            r"next-generation\s+solution",
            r"innovative\s+framework",
            r"transformative\s+platform",
            r"synergistic\s+approach",
            r"holistic\s+integration",
            r"seamless\s+orchestration",
            r"cutting-edge\s+methodology"
        ]
        
        # Circular reasoning patterns
        self.circular_patterns = [
            r"because\s+it\s+is\s+\w+",
            r"which\s+means\s+that\s+it\s+is",
            r"therefore\s+it\s+follows\s+that",
            r"as\s+a\s+result\s+of\s+this\s+result"
        ]
        
        # Repetitive phrase detection
        self.repetition_threshold = 3
        
        # Vague qualifier patterns
        self.vague_qualifiers = [
            r"very\s+\w+",
            r"extremely\s+\w+",
            r"incredibly\s+\w+",
            r"essentially\s+\w+",
            r"basically\s+\w+",
            r"fundamentally\s+\w+",
            r"virtually\s+\w+",
            r"literally\s+\w+"
        ]
        
        # AI-generated template markers
        self.template_markers = [
            r"as\s+an\s+ai\s+language\s+model",
            r"i\s+apologize\s+for\s+any\s+confusion",
            r"i\s+cannot\s+provide\s+specific",
            r"it's\s+important\s+to\s+note\s+that",
            r"please\s+consult\s+with\s+appropriate",
            r"this\s+is\s+a\s+general\s+overview"
        ]
    
    def analyze_content(self, text: str) -> Dict[str, List[str]]:
        """Analyze text for various types of fluff"""
        results = {
            "buzzwords": [],
            "circular_reasoning": [],
            "repetitive_phrases": [],
            "vague_qualifiers": [],
            "template_markers": [],
            "score": 0
        }
        
        # Check for buzzwords
        for pattern in self.buzzword_patterns:
            matches = re.finditer(pattern, text.lower())
            results["buzzwords"].extend([m.group() for m in matches])
        
        # Check for circular reasoning
        for pattern in self.circular_patterns:
            matches = re.finditer(pattern, text.lower())
            results["circular_reasoning"].extend([m.group() for m in matches])
        
        # Check for repetitive phrases
        phrases = self._find_repetitive_phrases(text)
        results["repetitive_phrases"] = phrases
        
        # Check for vague qualifiers
        for pattern in self.vague_qualifiers:
            matches = re.finditer(pattern, text.lower())
            results["vague_qualifiers"].extend([m.group() for m in matches])
        
        # Check for template markers
        for pattern in self.template_markers:
            matches = re.finditer(pattern, text.lower())
            results["template_markers"].extend([m.group() for m in matches])
        
        # Calculate fluff score
        results["score"] = self._calculate_fluff_score(results)
        
        return results
    
    def _find_repetitive_phrases(self, text: str, min_length: int = 4) -> List[str]:
        """Find phrases that repeat more than threshold times"""
        words = text.lower().split()
        phrases = {}
        
        for i in range(len(words) - min_length):
            phrase = " ".join(words[i:i+min_length])
            phrases[phrase] = phrases.get(phrase, 0) + 1
        
        return [phrase for phrase, count in phrases.items() 
                if count >= self.repetition_threshold]
    
    def _calculate_fluff_score(self, results: Dict) -> float:
        """Calculate a fluff score from 0 to 1"""
        score = 0
        
        # Each buzzword adds 0.1
        score += len(results["buzzwords"]) * 0.1
        
        # Each circular reasoning instance adds 0.15
        score += len(results["circular_reasoning"]) * 0.15
        
        # Each repetitive phrase adds 0.2
        score += len(results["repetitive_phrases"]) * 0.2
        
        # Each vague qualifier adds 0.05
        score += len(results["vague_qualifiers"]) * 0.05
        
        # Each template marker adds 0.25
        score += len(results["template_markers"]) * 0.25
        
        return min(score, 1.0)
    
    def should_quarantine(self, text: str) -> Tuple[bool, Dict]:
        """Determine if content should be quarantined"""
        analysis = self.analyze_content(text)
        
        # Quarantine if:
        # 1. Fluff score > 0.6
        # 2. More than 2 template markers
        # 3. More than 3 buzzwords
        # 4. Any circular reasoning
        should_quarantine = (
            analysis["score"] > 0.6 or
            len(analysis["template_markers"]) > 2 or
            len(analysis["buzzwords"]) > 3 or
            len(analysis["circular_reasoning"]) > 0
        )
        
        return should_quarantine, analysis
