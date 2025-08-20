import json
import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import os

@dataclass
class CompassClassification:
    primary_category: str
    secondary_categories: List[str]
    confidence: float
    keywords_found: List[str]
    compass_tags: List[str]
    processing_priority: str
    export_path: str

class CompassClassifier:
    def __init__(self):
        # Compass Keyword Table - the "red thread" of your system
        self.compass_keywords = {
            "prompt_module": {
                "keywords": [
                    "system prompt", "persona", "agent logic", "role", "instruction",
                    "guidance", "behavior", "response pattern", "interaction style",
                    "conversation flow", "user experience", "engagement"
                ],
                "weight": 1.0,
                "export_path": "COMPASS_CORE/prompts"
            },
            "method_model": {
                "keywords": [
                    "schaubild", "digest", "nervous system", "field", "stance",
                    "emotional anchor", "pearl", "feeling-state", "anti-bypass",
                    "essence", "field-aware", "inner field", "subtle layer",
                    "consciousness", "awareness", "presence"
                ],
                "weight": 1.2,  # Higher weight for core method
                "export_path": "COMPASS_CORE/method"
            },
            "offer": {
                "keywords": [
                    "deep dive", "facilitator training", "capsules", "workshop",
                    "course", "program", "session", "guidance", "support",
                    "transformation", "development", "growth", "healing"
                ],
                "weight": 0.8,
                "export_path": "COMPASS_CORE/offers"
            },
            "platform": {
                "keywords": [
                    "telegram", "supabase", "pinecone", "railway", "fastapi",
                    "vector database", "rbac", "row level security", "migration",
                    "api", "endpoint", "database", "schema", "deployment",
                    "infrastructure", "architecture", "system design"
                ],
                "weight": 0.9,
                "export_path": "COMPASS_CORE/platform"
            },
            "tone": {
                "keywords": [
                    "essence", "poetic", "neutral", "field-aware", "authentic",
                    "human", "genuine", "real", "honest", "direct", "clear",
                    "simple", "practical", "accessible"
                ],
                "weight": 0.7,
                "export_path": "COMPASS_CORE/tone"
            },
            "community": {
                "keywords": [
                    "willb.one", "community", "group", "collective", "shared",
                    "collaboration", "support", "connection", "relationship",
                    "network", "ecosystem", "culture", "values"
                ],
                "weight": 0.8,
                "export_path": "COMPASS_CORE/community"
            },
            "content": {
                "keywords": [
                    "content", "material", "resource", "documentation", "guide",
                    "manual", "instruction", "tutorial", "example", "template",
                    "framework", "structure", "format"
                ],
                "weight": 0.6,
                "export_path": "COMPASS_CORE/content"
            },
            "research": {
                "keywords": [
                    "research", "study", "analysis", "investigation", "exploration",
                    "discovery", "insight", "finding", "observation", "pattern",
                    "trend", "data", "evidence", "validation"
                ],
                "weight": 0.7,
                "export_path": "HUMAN_REVIEW/research"
            },
            "strategy": {
                "keywords": [
                    "strategy", "plan", "approach", "methodology", "framework",
                    "process", "workflow", "system", "architecture", "design",
                    "blueprint", "roadmap", "vision", "goal"
                ],
                "weight": 0.8,
                "export_path": "COMPASS_CORE/strategy"
            }
        }
        
        # Priority levels for processing
        self.priority_levels = {
            "critical": ["prompt_module", "method_model"],
            "high": ["offer", "platform", "strategy"],
            "medium": ["tone", "community", "content"],
            "low": ["research"]
        }

    def classify_content(self, content: str, file_path: str = "") -> CompassClassification:
        """Classify content using Compass keywords"""
        
        # Find matching categories
        category_scores = self._calculate_category_scores(content)
        
        # Determine primary and secondary categories
        primary_category, secondary_categories = self._determine_categories(category_scores)
        
        # Calculate confidence
        confidence = self._calculate_confidence(category_scores, primary_category)
        
        # Get keywords found
        keywords_found = self._get_keywords_found(content)
        
        # Generate compass tags
        compass_tags = self._generate_compass_tags(category_scores, keywords_found)
        
        # Determine processing priority
        processing_priority = self._determine_priority(primary_category, secondary_categories)
        
        # Determine export path
        export_path = self._determine_export_path(primary_category, category_scores)
        
        return CompassClassification(
            primary_category=primary_category,
            secondary_categories=secondary_categories,
            confidence=confidence,
            keywords_found=keywords_found,
            compass_tags=compass_tags,
            processing_priority=processing_priority,
            export_path=export_path
        )

    def _calculate_category_scores(self, content: str) -> Dict[str, float]:
        """Calculate scores for each category based on keyword matches"""
        scores = {}
        content_lower = content.lower()
        
        for category, config in self.compass_keywords.items():
            score = 0.0
            keywords = config["keywords"]
            
            for keyword in keywords:
                # Count exact matches
                matches = content_lower.count(keyword.lower())
                score += matches * config["weight"]
                
                # Bonus for word boundaries
                if re.search(rf"\b{re.escape(keyword.lower())}\b", content_lower):
                    score += 0.5 * config["weight"]
            
            scores[category] = round(score, 3)
        
        return scores

    def _determine_categories(self, category_scores: Dict[str, float]) -> Tuple[str, List[str]]:
        """Determine primary and secondary categories"""
        # Sort categories by score
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Primary category is the highest scoring
        primary_category = sorted_categories[0][0] if sorted_categories else "content"
        
        # Secondary categories are those with scores > 0.5
        secondary_categories = [
            cat for cat, score in sorted_categories[1:] 
            if score > 0.5 and cat != primary_category
        ][:3]  # Limit to top 3 secondary categories
        
        return primary_category, secondary_categories

    def _calculate_confidence(self, category_scores: Dict[str, float], primary_category: str) -> float:
        """Calculate confidence in the classification"""
        primary_score = category_scores.get(primary_category, 0)
        total_score = sum(category_scores.values())
        
        if total_score == 0:
            return 0.0
        
        # Confidence based on primary category dominance
        confidence = primary_score / total_score
        
        # Boost confidence if primary score is high
        if primary_score >= 3.0:
            confidence += 0.2
        
        return round(min(confidence, 1.0), 3)

    def _get_keywords_found(self, content: str) -> List[str]:
        """Get all keywords found in the content"""
        keywords_found = []
        content_lower = content.lower()
        
        for category, config in self.compass_keywords.items():
            for keyword in config["keywords"]:
                if keyword.lower() in content_lower:
                    keywords_found.append(keyword)
        
        return list(set(keywords_found))  # Remove duplicates

    def _generate_compass_tags(self, category_scores: Dict[str, float], keywords_found: List[str]) -> List[str]:
        """Generate compass tags for the content"""
        tags = []
        
        # Add category tags for significant scores
        for category, score in category_scores.items():
            if score >= 1.0:
                tags.append(f"compass:{category}")
        
        # Add keyword tags for important keywords
        important_keywords = [
            "schaubild", "emotional anchor", "system prompt", "nervous system",
            "stance", "field", "essence", "willb.one", "telegram", "supabase"
        ]
        
        for keyword in important_keywords:
            if keyword.lower() in [k.lower() for k in keywords_found]:
                tags.append(f"keyword:{keyword.replace(' ', '_')}")
        
        return tags

    def _determine_priority(self, primary_category: str, secondary_categories: List[str]) -> str:
        """Determine processing priority based on categories"""
        all_categories = [primary_category] + secondary_categories
        
        for priority, categories in self.priority_levels.items():
            if any(cat in all_categories for cat in categories):
                return priority
        
        return "medium"

    def _determine_export_path(self, primary_category: str, category_scores: Dict[str, float]) -> str:
        """Determine the export path for the content"""
        if primary_category in self.compass_keywords:
            base_path = self.compass_keywords[primary_category]["export_path"]
            
            # Check if content should go to human review
            if self._should_human_review(category_scores):
                return f"HUMAN_REVIEW/{primary_category}"
            
            return base_path
        
        return "HUMAN_REVIEW/uncategorized"

    def _should_human_review(self, category_scores: Dict[str, float]) -> bool:
        """Determine if content should go to human review"""
        # Low confidence classifications
        total_score = sum(category_scores.values())
        if total_score < 1.0:
            return True
        
        # Multiple high-scoring categories (conflicting classification)
        high_scores = [score for score in category_scores.values() if score >= 2.0]
        if len(high_scores) > 2:
            return True
        
        return False

    def create_sidecar_metadata(self, classification: CompassClassification, 
                               file_path: str, additional_metadata: Dict = None) -> Dict:
        """Create sidecar metadata file"""
        metadata = {
            "compass_classification": {
                "primary_category": classification.primary_category,
                "secondary_categories": classification.secondary_categories,
                "confidence": classification.confidence,
                "keywords_found": classification.keywords_found,
                "compass_tags": classification.compass_tags,
                "processing_priority": classification.processing_priority,
                "export_path": classification.export_path
            },
            "file_info": {
                "original_path": file_path,
                "filename": os.path.basename(file_path),
                "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                "processed_at": self._get_timestamp()
            }
        }
        
        if additional_metadata:
            metadata["additional"] = additional_metadata
        
        return metadata

    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

    def save_sidecar_file(self, metadata: Dict, file_path: str) -> str:
        """Save sidecar metadata file"""
        sidecar_path = f"{file_path}.meta.json"
        
        with open(sidecar_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        return sidecar_path

    def load_sidecar_file(self, file_path: str) -> Optional[Dict]:
        """Load sidecar metadata file"""
        sidecar_path = f"{file_path}.meta.json"
        
        if os.path.exists(sidecar_path):
            with open(sidecar_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None

# Example usage
if __name__ == "__main__":
    classifier = CompassClassifier()
    
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
    
    This method integrates with our Telegram platform and Supabase database
    to provide comprehensive support for personal development.
    """
    
    classification = classifier.classify_content(test_content, "test_file.md")
    
    print(f"Primary Category: {classification.primary_category}")
    print(f"Secondary Categories: {classification.secondary_categories}")
    print(f"Confidence: {classification.confidence}")
    print(f"Keywords Found: {classification.keywords_found}")
    print(f"Compass Tags: {classification.compass_tags}")
    print(f"Processing Priority: {classification.processing_priority}")
    print(f"Export Path: {classification.export_path}")
    
    # Create sidecar metadata
    metadata = classifier.create_sidecar_metadata(classification, "test_file.md")
    print(f"\nMetadata: {json.dumps(metadata, indent=2)}")
