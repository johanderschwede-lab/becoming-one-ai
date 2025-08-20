"""
Expandable Personality Synthesis Framework
==========================================

A living, growing system that can continuously integrate new personality frameworks,
refine existing ones, and prune outdated concepts over time.

Current Systems:
- Enneagram
- Human Design  
- Astrology
- Maya Calendar Zuvuya
- Myers-Briggs/Jung
- Becoming One™ Method

Planned Additions:
- Fourth Way (Gurdjieff/Ouspensky)
- Hylozoics (Henry T. Laurency)
- Future systems as they emerge

Architecture designed for continuous expansion and refinement.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

class SystemStatus(Enum):
    """Status of personality systems in the framework"""
    ACTIVE = "active"
    EXPERIMENTAL = "experimental"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ConceptConfidence(Enum):
    """Confidence levels for personality concepts"""
    CORE = "core"           # Fundamental, well-established
    VALIDATED = "validated" # Proven through experience
    WORKING = "working"     # Useful but still being refined
    EXPERIMENTAL = "experimental"  # New, being tested
    QUESTIONABLE = "questionable"  # May need revision


@dataclass
class PersonalityFramework:
    """Base class for all personality frameworks"""
    framework_id: str
    name: str
    description: str
    version: str
    status: SystemStatus
    confidence: ConceptConfidence
    source_authority: str  # e.g., "Gurdjieff", "Ichazo", "Ra Uru Hu"
    integration_date: datetime
    last_updated: datetime
    
    # Core concepts this framework contributes
    core_concepts: List[str] = field(default_factory=list)
    
    # How this framework maps to others
    cross_references: Dict[str, Any] = field(default_factory=dict)
    
    # Validation criteria
    validation_methods: List[str] = field(default_factory=list)
    
    # Usage statistics
    usage_stats: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PersonalityConcept:
    """Individual concepts that can be validated, refined, or pruned"""
    concept_id: str
    name: str
    description: str
    framework_origin: str
    confidence: ConceptConfidence
    
    # Evidence supporting this concept
    supporting_evidence: List[str] = field(default_factory=list)
    
    # Counter-evidence or limitations
    limitations: List[str] = field(default_factory=list)
    
    # Related concepts from other frameworks
    cross_framework_correlations: Dict[str, str] = field(default_factory=dict)
    
    # Usage in analysis
    analysis_frequency: int = 0
    accuracy_score: float = 0.0
    
    # Evolution tracking
    concept_evolution: List[Dict[str, Any]] = field(default_factory=list)


class ExpandablePersonalityFramework:
    """Main framework that can grow and evolve over time"""
    
    def __init__(self, base_data_path: str = "personality_data"):
        self.data_path = Path(base_data_path)
        self.data_path.mkdir(exist_ok=True)
        
        # Core storage
        self.frameworks: Dict[str, PersonalityFramework] = {}
        self.concepts: Dict[str, PersonalityConcept] = {}
        self.analysis_prompts: Dict[str, Dict[str, Any]] = {}
        
        # Evolution tracking
        self.framework_history: List[Dict[str, Any]] = []
        self.refinement_log: List[Dict[str, Any]] = []
        
        # Load existing data
        self._load_frameworks()
        self._initialize_core_frameworks()
    
    def add_framework(self, framework: PersonalityFramework) -> bool:
        """Add a new personality framework to the system"""
        try:
            # Validate framework
            if not self._validate_framework(framework):
                return False
            
            # Store framework
            self.frameworks[framework.framework_id] = framework
            
            # Log addition
            self.framework_history.append({
                "action": "framework_added",
                "framework_id": framework.framework_id,
                "timestamp": datetime.now().isoformat(),
                "version": framework.version
            })
            
            # Save to disk
            self._save_framework(framework)
            
            print(f"✅ Added framework: {framework.name} v{framework.version}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add framework {framework.name}: {e}")
            return False
    
    def add_concept(self, concept: PersonalityConcept) -> bool:
        """Add a new personality concept"""
        try:
            # Validate concept
            if not self._validate_concept(concept):
                return False
            
            # Store concept
            self.concepts[concept.concept_id] = concept
            
            # Update framework if it exists
            if concept.framework_origin in self.frameworks:
                framework = self.frameworks[concept.framework_origin]
                if concept.name not in framework.core_concepts:
                    framework.core_concepts.append(concept.name)
            
            # Log addition
            self.refinement_log.append({
                "action": "concept_added",
                "concept_id": concept.concept_id,
                "framework": concept.framework_origin,
                "timestamp": datetime.now().isoformat()
            })
            
            # Save to disk
            self._save_concept(concept)
            
            print(f"✅ Added concept: {concept.name} ({concept.framework_origin})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to add concept {concept.name}: {e}")
            return False
    
    def refine_concept(self, concept_id: str, updates: Dict[str, Any]) -> bool:
        """Refine an existing concept based on new insights"""
        if concept_id not in self.concepts:
            print(f"❌ Concept not found: {concept_id}")
            return False
        
        concept = self.concepts[concept_id]
        old_version = self._concept_to_dict(concept)
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(concept, key):
                # Track evolution
                concept.concept_evolution.append({
                    "timestamp": datetime.now().isoformat(),
                    "field": key,
                    "old_value": getattr(concept, key),
                    "new_value": value,
                    "reason": updates.get("refinement_reason", "Manual update")
                })
                
                setattr(concept, key, value)
        
        # Log refinement
        self.refinement_log.append({
            "action": "concept_refined",
            "concept_id": concept_id,
            "changes": list(updates.keys()),
            "timestamp": datetime.now().isoformat()
        })
        
        # Save changes
        self._save_concept(concept)
        
        print(f"✅ Refined concept: {concept.name}")
        return True
    
    def prune_concept(self, concept_id: str, reason: str) -> bool:
        """Remove or deprecate a concept that's no longer useful"""
        if concept_id not in self.concepts:
            print(f"❌ Concept not found: {concept_id}")
            return False
        
        concept = self.concepts[concept_id]
        
        # Archive rather than delete
        concept.confidence = ConceptConfidence.QUESTIONABLE
        concept.concept_evolution.append({
            "timestamp": datetime.now().isoformat(),
            "action": "pruned",
            "reason": reason
        })
        
        # Log pruning
        self.refinement_log.append({
            "action": "concept_pruned",
            "concept_id": concept_id,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        })
        
        # Save changes
        self._save_concept(concept)
        
        print(f"⚠️ Pruned concept: {concept.name} - {reason}")
        return True
    
    def add_analysis_prompt(self, framework_id: str, prompt_data: Dict[str, Any]) -> bool:
        """Add or update AI analysis prompt for a framework"""
        try:
            if framework_id not in self.analysis_prompts:
                self.analysis_prompts[framework_id] = {}
            
            self.analysis_prompts[framework_id].update(prompt_data)
            
            # Save to disk
            prompt_file = self.data_path / "analysis_prompts" / f"{framework_id}.json"
            prompt_file.parent.mkdir(exist_ok=True)
            
            with open(prompt_file, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_prompts[framework_id], f, indent=2)
            
            print(f"✅ Updated analysis prompt for: {framework_id}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update analysis prompt: {e}")
            return False
    
    def get_active_frameworks(self) -> List[PersonalityFramework]:
        """Get all currently active frameworks"""
        return [fw for fw in self.frameworks.values() 
                if fw.status == SystemStatus.ACTIVE]
    
    def get_framework_concepts(self, framework_id: str) -> List[PersonalityConcept]:
        """Get all concepts from a specific framework"""
        return [concept for concept in self.concepts.values()
                if concept.framework_origin == framework_id]
    
    def get_cross_framework_correlations(self, concept_id: str) -> Dict[str, Any]:
        """Get how a concept relates to other frameworks"""
        if concept_id not in self.concepts:
            return {}
        
        concept = self.concepts[concept_id]
        correlations = {}
        
        for fw_id, correlation in concept.cross_framework_correlations.items():
            if fw_id in self.frameworks:
                correlations[self.frameworks[fw_id].name] = correlation
        
        return correlations
    
    def generate_synthesis_analysis_prompt(self) -> str:
        """Generate comprehensive analysis prompt using all active frameworks"""
        active_frameworks = self.get_active_frameworks()
        
        prompt_sections = []
        
        for framework in active_frameworks:
            if framework.framework_id in self.analysis_prompts:
                prompt_data = self.analysis_prompts[framework.framework_id]
                prompt_sections.append(f"""
{framework.name} Analysis:
{prompt_data.get('analysis_prompt', 'Analyze using ' + framework.name + ' principles.')}

Key concepts to identify: {', '.join(framework.core_concepts)}
""")
        
        synthesis_prompt = f"""
Analyze this message using the Becoming One™ Expandable Personality Synthesis Model.

Apply the following frameworks in combination:

{''.join(prompt_sections)}

Cross-Framework Integration:
- Look for correlations between frameworks
- Identify contradictions that need resolution
- Note areas where frameworks complement each other
- Highlight unique insights from each system

Return comprehensive JSON analysis with insights from all active frameworks.
"""
        
        return synthesis_prompt
    
    def _initialize_core_frameworks(self):
        """Initialize the core personality frameworks"""
        
        # Enneagram
        enneagram = PersonalityFramework(
            framework_id="enneagram",
            name="Enneagram",
            description="Nine personality types based on core motivations and fears",
            version="1.0",
            status=SystemStatus.ACTIVE,
            confidence=ConceptConfidence.VALIDATED,
            source_authority="Ichazo/Naranjo/Riso-Hudson",
            integration_date=datetime.now(),
            last_updated=datetime.now(),
            core_concepts=[
                "type_identification", "centers_of_intelligence", "wings", 
                "levels_of_development", "instinctual_variants", "arrows"
            ],
            validation_methods=["behavioral_observation", "self_reporting", "motivation_analysis"]
        )
        
        # Human Design
        human_design = PersonalityFramework(
            framework_id="human_design",
            name="Human Design",
            description="Synthesis of astrology, I Ching, Kabbalah, and chakras",
            version="1.0", 
            status=SystemStatus.ACTIVE,
            confidence=ConceptConfidence.WORKING,
            source_authority="Ra Uru Hu",
            integration_date=datetime.now(),
            last_updated=datetime.now(),
            core_concepts=[
                "type_manifestor_generator_projector_reflector", "strategy", "authority",
                "profile", "centers", "channels", "gates"
            ],
            validation_methods=["birth_data_calculation", "strategy_testing", "authority_validation"]
        )
        
        # Becoming One™ Method
        becoming_one = PersonalityFramework(
            framework_id="becoming_one",
            name="Becoming One™ Method",
            description="Emotional anchor recognition and feeling-state navigation",
            version="2.0",
            status=SystemStatus.ACTIVE,
            confidence=ConceptConfidence.CORE,
            source_authority="Johan/Marianne",
            integration_date=datetime.now(),
            last_updated=datetime.now(),
            core_concepts=[
                "emotional_anchors", "feeling_states", "anti_bypass", "procrastination_as_portal",
                "loyalty_debts", "secondary_gains", "the_pearl", "anchor_burning", "turn_180"
            ],
            validation_methods=["experiential_validation", "transformation_tracking", "pearl_extraction"]
        )
        
        # Add frameworks
        for framework in [enneagram, human_design, becoming_one]:
            if framework.framework_id not in self.frameworks:
                self.add_framework(framework)
    
    def prepare_for_fourth_way(self) -> Dict[str, Any]:
        """Prepare framework for Fourth Way integration"""
        fourth_way_structure = {
            "framework_id": "fourth_way",
            "name": "Fourth Way",
            "description": "Gurdjieff/Ouspensky system of conscious development",
            "planned_concepts": [
                "centers_of_intelligence",  # Thinking, Feeling, Moving
                "states_of_consciousness",  # Sleep, Waking, Self-remembering, Objective
                "chief_feature",           # Main personality defect
                "false_personality",       # Acquired patterns vs essence
                "self_remembering",        # Conscious attention
                "work_on_self",           # Conscious suffering and voluntary discomfort
                "being_vs_knowing",       # Development of being vs accumulation of knowledge
                "octaves_and_laws",       # Law of Three, Law of Seven
                "types_of_man"            # Man 1-7 classification
            ],
            "integration_points": {
                "enneagram": "Both use nine types, Gurdjieff originated enneagram symbol",
                "becoming_one": "Self-remembering aligns with anti-bypass approach",
                "human_design": "Centers concept has parallels in both systems"
            },
            "validation_methods": [
                "self_observation", "conscious_suffering", "work_verification",
                "being_level_assessment", "presence_quality"
            ]
        }
        
        # Save preparation data
        prep_file = self.data_path / "framework_preparations" / "fourth_way.json"
        prep_file.parent.mkdir(exist_ok=True)
        
        with open(prep_file, 'w', encoding='utf-8') as f:
            json.dump(fourth_way_structure, f, indent=2)
        
        print("✅ Fourth Way integration structure prepared")
        return fourth_way_structure
    
    def prepare_for_hylozoics(self) -> Dict[str, Any]:
        """Prepare framework for Hylozoics integration"""
        hylozoics_structure = {
            "framework_id": "hylozoics",
            "name": "Hylozoics",
            "description": "Henry T. Laurency's worldview and life view system",
            "planned_concepts": [
                "kingdoms_of_nature",     # Mineral, plant, animal, human, superhuman
                "worlds_and_dimensions",  # Physical, emotional, mental, etc.
                "stages_of_human_development",  # Barbarism, civilization, culture, humanity, ideality
                "consciousness_development",    # Expansion through the kingdoms
                "law_of_development",          # Evolution of consciousness
                "esoteric_knowledge_degrees",  # Levels of understanding
                "life_view_vs_world_view",     # Understanding reality vs living it
                "causal_consciousness",        # Higher mental development
                "group_consciousness",         # Beyond individual development
                "planetary_hierarchy"          # Organizational structure of evolved beings
            ],
            "integration_points": {
                "fourth_way": "Both emphasize stages of consciousness development",
                "human_design": "Both describe energy centers/bodies",
                "becoming_one": "Both focus on consciousness expansion through experience"
            },
            "validation_methods": [
                "consciousness_expansion_tracking", "life_view_application",
                "developmental_stage_assessment", "group_work_effectiveness"
            ]
        }
        
        # Save preparation data
        prep_file = self.data_path / "framework_preparations" / "hylozoics.json"
        prep_file.parent.mkdir(exist_ok=True)
        
        with open(prep_file, 'w', encoding='utf-8') as f:
            json.dump(hylozoics_structure, f, indent=2)
        
        print("✅ Hylozoics integration structure prepared")
        return hylozoics_structure
    
    def _validate_framework(self, framework: PersonalityFramework) -> bool:
        """Validate framework before adding"""
        if not framework.framework_id or not framework.name:
            return False
        
        if framework.framework_id in self.frameworks:
            print(f"⚠️ Framework {framework.framework_id} already exists")
            return False
        
        return True
    
    def _validate_concept(self, concept: PersonalityConcept) -> bool:
        """Validate concept before adding"""
        if not concept.concept_id or not concept.name:
            return False
        
        return True
    
    def _save_framework(self, framework: PersonalityFramework):
        """Save framework to disk"""
        fw_file = self.data_path / "frameworks" / f"{framework.framework_id}.json"
        fw_file.parent.mkdir(exist_ok=True)
        
        with open(fw_file, 'w', encoding='utf-8') as f:
            json.dump(self._framework_to_dict(framework), f, indent=2, default=str)
    
    def _save_concept(self, concept: PersonalityConcept):
        """Save concept to disk"""
        concept_file = self.data_path / "concepts" / f"{concept.concept_id}.json"
        concept_file.parent.mkdir(exist_ok=True)
        
        with open(concept_file, 'w', encoding='utf-8') as f:
            json.dump(self._concept_to_dict(concept), f, indent=2, default=str)
    
    def _load_frameworks(self):
        """Load existing frameworks from disk"""
        frameworks_dir = self.data_path / "frameworks"
        if frameworks_dir.exists():
            for fw_file in frameworks_dir.glob("*.json"):
                try:
                    with open(fw_file, 'r', encoding='utf-8') as f:
                        fw_data = json.load(f)
                        # Convert back to PersonalityFramework object
                        # Implementation depends on serialization format
                except Exception as e:
                    print(f"⚠️ Could not load framework {fw_file}: {e}")
    
    def _framework_to_dict(self, framework: PersonalityFramework) -> Dict[str, Any]:
        """Convert framework to dictionary for serialization"""
        return {
            "framework_id": framework.framework_id,
            "name": framework.name,
            "description": framework.description,
            "version": framework.version,
            "status": framework.status.value,
            "confidence": framework.confidence.value,
            "source_authority": framework.source_authority,
            "integration_date": framework.integration_date.isoformat(),
            "last_updated": framework.last_updated.isoformat(),
            "core_concepts": framework.core_concepts,
            "cross_references": framework.cross_references,
            "validation_methods": framework.validation_methods,
            "usage_stats": framework.usage_stats
        }
    
    def _concept_to_dict(self, concept: PersonalityConcept) -> Dict[str, Any]:
        """Convert concept to dictionary for serialization"""
        return {
            "concept_id": concept.concept_id,
            "name": concept.name,
            "description": concept.description,
            "framework_origin": concept.framework_origin,
            "confidence": concept.confidence.value,
            "supporting_evidence": concept.supporting_evidence,
            "limitations": concept.limitations,
            "cross_framework_correlations": concept.cross_framework_correlations,
            "analysis_frequency": concept.analysis_frequency,
            "accuracy_score": concept.accuracy_score,
            "concept_evolution": concept.concept_evolution
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive status of the personality framework"""
        active_frameworks = self.get_active_frameworks()
        
        return {
            "total_frameworks": len(self.frameworks),
            "active_frameworks": len(active_frameworks),
            "total_concepts": len(self.concepts),
            "framework_names": [fw.name for fw in active_frameworks],
            "last_refinement": max([entry["timestamp"] for entry in self.refinement_log]) if self.refinement_log else None,
            "system_version": "2.0",
            "expandability_status": "Ready for continuous growth"
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize expandable framework
    framework = ExpandablePersonalityFramework()
    
    # Prepare for new integrations
    framework.prepare_for_fourth_way()
    framework.prepare_for_hylozoics()
    
    # Show system status
    status = framework.get_system_status()
    print(f"🌱 Expandable Personality Framework Status:")
    for key, value in status.items():
        print(f"   {key}: {value}")
    
    print(f"\n✅ Framework ready for continuous expansion!")
    print(f"📁 Data stored in: {framework.data_path}")
