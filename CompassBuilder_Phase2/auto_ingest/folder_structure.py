# build this

import os
from pathlib import Path
from typing import Dict, List

class FolderStructure:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        
        # Define complete folder structure
        self.structure = {
            "Phase1_Legacy_Imports": {
                "preserved_chats": {
                    "original_files": {},
                    "extracted_prompts": {},
                    "prompt_index": {}
                },
                "raw_documents": {},
                "initial_prompts": {},
                "archived_versions": {},
                "historical_data": {}
            },
            "Phase2_Clean_Logic": {
                "supabase_sync": {
                    "schemas": {},
                    "migrations": {},
                    "sync_logs": {}
                },
                "visual_index": {
                    "dashboards": {},
                    "tag_maps": {},
                    "visualizations": {}
                },
                "versioning": {
                    "diffs": {},
                    "summaries": {},
                    "change_logs": {}
                },
                "auto_ingest": {
                    "pipelines": {},
                    "processors": {},
                    "logs": {}
                },
                "agent_feeds": {
                    "prompt_versions": {},
                    "digests": {},
                    "summaries": {}
                }
            },
            "Phase3_AgentExpansions": {
                "personas": {
                    "amanita": {},
                    "laurency": {},
                    "coach": {},
                    "telegram": {}
                },
                "plugin_layer": {
                    "hooks": {},
                    "extensions": {},
                    "configs": {}
                },
                "ui_builder": {
                    "templates": {},
                    "components": {},
                    "layouts": {}
                },
                "nlp_engine": {
                    "models": {},
                    "training": {},
                    "evaluation": {}
                }
            },
            "Phase4_MethodCore": {
                "becoming_one": {
                    "principles": {},
                    "practices": {},
                    "models": {}
                },
                "consciousness_mapping": {
                    "systems": {},
                    "integrations": {},
                    "synthesis": {}
                },
                "sacred_library": {
                    "hylozoics": {},
                    "fourth_way": {},
                    "references": {}
                }
            },
            "Phase5_UserJourneys": {
                "onboarding": {
                    "flows": {},
                    "content": {},
                    "triggers": {}
                },
                "transformation": {
                    "paths": {},
                    "exercises": {},
                    "tracking": {}
                },
                "community": {
                    "interactions": {},
                    "guidance": {},
                    "support": {}
                }
            },
            "PhaseX_Experimental": {
                "concepts": {},
                "prototypes": {},
                "research": {}
            },
            "__trash_fluff_review": {
                "ai_generated": {},
                "redundant": {},
                "unclear": {}
            },
            "docs": {
                "user_guides": {},
                "api_docs": {},
                "architecture": {},
                "examples": {}
            }
        }
    
    def create_structure(self):
        """Create the complete folder structure"""
        def create_recursive(path: Path, structure: Dict):
            for name, substructure in structure.items():
                current = path / name
                current.mkdir(exist_ok=True)
                
                if substructure:  # If has subfolders
                    create_recursive(current, substructure)
        
        create_recursive(self.base_dir, self.structure)
    
    def get_appropriate_folder(self, categories: List[str], content_type: str) -> Path:
        """Determine appropriate folder based on categories and content"""
        if not categories:
            return self.base_dir / "PhaseX_Experimental" / "unclear"
        
        # Map categories to phases
        phase_mapping = {
            "master_prompt": "Phase2_Clean_Logic",
            "becoming_one_method": "Phase4_MethodCore/becoming_one",
            "personality_systems": "Phase4_MethodCore/consciousness_mapping",
            "sacred_library": "Phase4_MethodCore/sacred_library",
            "ai_agents": "Phase3_AgentExpansions/personas",
            "technical": "Phase2_Clean_Logic",
            "user_experience": "Phase5_UserJourneys",
            "strategic": "Phase1_Legacy_Imports"
        }
        
        # Get primary category
        primary_cat = categories[0]
        
        # Determine phase
        phase = phase_mapping.get(primary_cat, "Phase1_Legacy_Imports")
        
        # Create path
        path = self.base_dir / phase
        
        # Add content-type specific subfolder
        if content_type == "prompt":
            path = path / "prompts"
        elif content_type == "config":
            path = path / "configs"
        elif content_type == "doc":
            path = path / "docs"
        
        return path
    
    def move_file(self, source: Path, categories: List[str], content_type: str):
        """Move file to appropriate location in structure"""
        target_dir = self.get_appropriate_folder(categories, content_type)
        target_dir.mkdir(parents=True, exist_ok=True)
        
        target_path = target_dir / source.name
        source.rename(target_path)
        
        return target_path
