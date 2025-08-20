import os
import json
import shutil
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import re

class CuratedExporter:
    def __init__(self, base_export_dir: str = "EXPORT"):
        self.base_export_dir = base_export_dir
        
        # Export structure definition
        self.export_structure = {
            "COMPASS_CORE": {
                "description": "Clean, structured source of truth for AI use",
                "subfolders": {
                    "prompts": "System prompts and instruction sets",
                    "method": "Core Becoming One™ method content",
                    "offers": "Service and product offerings",
                    "platform": "Technical platform documentation",
                    "tone": "Communication style and voice guidelines",
                    "community": "WillB.one community content",
                    "content": "General content and resources",
                    "strategy": "Strategic planning and frameworks"
                }
            },
            "HUMAN_REVIEW": {
                "description": "Content requiring human assessment and refinement",
                "subfolders": {
                    "research": "Research findings and insights",
                    "drafts": "Work in progress content",
                    "uncategorized": "Content that couldn't be automatically classified",
                    "high_potential": "High-value content needing structure",
                    "chat_transcripts": "Chat conversations with user prompts marked"
                }
            },
            "QUARANTINE_RESCUE": {
                "description": "Flagged content with recovery options",
                "subfolders": {
                    "flagged_files": "Files flagged as potentially problematic",
                    "fluff_reasons": "Detailed analysis of why content was flagged",
                    "top_keywords": "Key terms found in flagged content",
                    "recovery_candidates": "Content that might be salvageable"
                }
            }
        }
        
        # Initialize export directory structure
        self._create_export_structure()

    def _create_export_structure(self):
        """Create the export directory structure"""
        for main_folder, config in self.export_structure.items():
            main_path = os.path.join(self.base_export_dir, main_folder)
            os.makedirs(main_path, exist_ok=True)
            
            # Create README for main folder
            readme_content = f"""# {main_folder}

{config['description']}

## Subfolders:
"""
            for subfolder, description in config["subfolders"].items():
                readme_content += f"- **{subfolder}**: {description}\n"
            
            with open(os.path.join(main_path, "README.md"), 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            # Create subfolders
            for subfolder in config["subfolders"].keys():
                subfolder_path = os.path.join(main_path, subfolder)
                os.makedirs(subfolder_path, exist_ok=True)

    def export_content(self, source_file: str, classification: Dict, 
                      strategic_score: Dict, fluff_analysis: Dict = None) -> str:
        """Export content to appropriate location based on analysis"""
        
        # Determine export path
        export_path = self._determine_export_path(classification, strategic_score)
        
        # Create destination path
        dest_path = os.path.join(self.base_export_dir, export_path)
        os.makedirs(dest_path, exist_ok=True)
        
        # Copy file to destination
        filename = os.path.basename(source_file)
        dest_file = os.path.join(dest_path, filename)
        
        try:
            shutil.copy2(source_file, dest_file)
            
            # Create metadata file
            metadata = self._create_export_metadata(
                source_file, classification, strategic_score, fluff_analysis
            )
            metadata_file = f"{dest_file}.meta.json"
            
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logging.info(f"Exported {filename} to {export_path}")
            return dest_file
            
        except Exception as e:
            logging.error(f"Failed to export {source_file}: {str(e)}")
            return None

    def _determine_export_path(self, classification: Dict, strategic_score: Dict) -> str:
        """Determine the export path based on classification and strategic score"""
        
        # Check if content should go to Compass Core
        if strategic_score.get("processing_decision", "").startswith("SAFE_CORE"):
            primary_category = classification.get("primary_category", "content")
            return f"COMPASS_CORE/{primary_category}"
        
        # Check if content should go to Review Core
        if strategic_score.get("processing_decision", "").startswith("REVIEW_CORE"):
            primary_category = classification.get("primary_category", "content")
            return f"COMPASS_CORE/{primary_category}"
        
        # Check if content should go to Rescue Queue
        if strategic_score.get("processing_decision", "").startswith("RESCUE_QUEUE"):
            return "HUMAN_REVIEW/high_potential"
        
        # Check if content should be quarantined
        if strategic_score.get("processing_decision", "").startswith("QUARANTINE"):
            return "QUARANTINE_RESCUE/flagged_files"
        
        # Check if content needs human review
        if strategic_score.get("processing_decision", "").startswith("HUMAN_REVIEW"):
            primary_category = classification.get("primary_category", "uncategorized")
            return f"HUMAN_REVIEW/{primary_category}"
        
        # Default to human review drafts
        return "HUMAN_REVIEW/drafts"

    def _create_export_metadata(self, source_file: str, classification: Dict,
                              strategic_score: Dict, fluff_analysis: Dict = None) -> Dict:
        """Create metadata for exported content"""
        
        metadata = {
            "export_info": {
                "exported_at": datetime.now().isoformat(),
                "source_file": source_file,
                "export_path": self._determine_export_path(classification, strategic_score),
                "export_version": "1.0"
            },
            "classification": classification,
            "strategic_score": strategic_score,
            "file_info": {
                "filename": os.path.basename(source_file),
                "file_size": os.path.getsize(source_file) if os.path.exists(source_file) else 0,
                "file_extension": os.path.splitext(source_file)[1]
            }
        }
        
        if fluff_analysis:
            metadata["fluff_analysis"] = fluff_analysis
        
        return metadata

    def create_compass_core_summary(self) -> str:
        """Create a summary of all content in Compass Core"""
        compass_core_path = os.path.join(self.base_export_dir, "COMPASS_CORE")
        
        if not os.path.exists(compass_core_path):
            return "No Compass Core content found"
        
        summary = "# Compass Core Summary\n\n"
        summary += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        total_files = 0
        
        for subfolder in os.listdir(compass_core_path):
            subfolder_path = os.path.join(compass_core_path, subfolder)
            
            if os.path.isdir(subfolder_path) and subfolder != "__pycache__":
                files = [f for f in os.listdir(subfolder_path) 
                        if f.endswith(('.md', '.txt', '.json')) and not f.endswith('.meta.json')]
                
                if files:
                    summary += f"## {subfolder.title()}\n\n"
                    summary += f"Files: {len(files)}\n\n"
                    
                    for file in sorted(files):
                        summary += f"- {file}\n"
                    
                    summary += "\n"
                    total_files += len(files)
        
        summary += f"\n## Total Files: {total_files}\n"
        
        # Save summary
        summary_file = os.path.join(compass_core_path, "COMPASS_CORE_SUMMARY.md")
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        return summary_file

    def create_human_review_queue(self) -> str:
        """Create a prioritized queue for human review"""
        human_review_path = os.path.join(self.base_export_dir, "HUMAN_REVIEW")
        
        if not os.path.exists(human_review_path):
            return "No Human Review content found"
        
        queue = "# Human Review Queue\n\n"
        queue += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Collect all files with their metadata
        review_items = []
        
        for root, dirs, files in os.walk(human_review_path):
            for file in files:
                if file.endswith('.meta.json'):
                    metadata_file = os.path.join(root, file)
                    content_file = metadata_file.replace('.meta.json', '')
                    
                    if os.path.exists(content_file):
                        try:
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                            
                            strategic_score = metadata.get("strategic_score", {})
                            total_score = strategic_score.get("total_score", 0)
                            
                            review_items.append({
                                "file": content_file,
                                "score": total_score,
                                "decision": strategic_score.get("processing_decision", ""),
                                "category": metadata.get("classification", {}).get("primary_category", ""),
                                "relative_path": os.path.relpath(content_file, human_review_path)
                            })
                        except Exception as e:
                            logging.warning(f"Could not read metadata for {metadata_file}: {str(e)}")
        
        # Sort by score (highest first)
        review_items.sort(key=lambda x: x["score"], reverse=True)
        
        # Group by priority
        priorities = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        for item in review_items:
            if item["score"] >= 8.0:
                priorities["critical"].append(item)
            elif item["score"] >= 5.0:
                priorities["high"].append(item)
            elif item["score"] >= 3.0:
                priorities["medium"].append(item)
            else:
                priorities["low"].append(item)
        
        # Write queue
        for priority, items in priorities.items():
            if items:
                queue += f"## {priority.title()} Priority ({len(items)} items)\n\n"
                
                for item in items:
                    queue += f"### {os.path.basename(item['file'])}\n"
                    queue += f"- **Score**: {item['score']}\n"
                    queue += f"- **Decision**: {item['decision']}\n"
                    queue += f"- **Category**: {item['category']}\n"
                    queue += f"- **Path**: {item['relative_path']}\n\n"
        
        # Save queue
        queue_file = os.path.join(human_review_path, "HUMAN_REVIEW_QUEUE.md")
        with open(queue_file, 'w', encoding='utf-8') as f:
            f.write(queue)
        
        return queue_file

    def create_quarantine_rescue_report(self) -> str:
        """Create a report of quarantined content with recovery options"""
        quarantine_path = os.path.join(self.base_export_dir, "QUARANTINE_RESCUE")
        
        if not os.path.exists(quarantine_path):
            return "No quarantined content found"
        
        report = "# Quarantine Rescue Report\n\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        flagged_files_path = os.path.join(quarantine_path, "flagged_files")
        if os.path.exists(flagged_files_path):
            files = [f for f in os.listdir(flagged_files_path) 
                    if f.endswith(('.md', '.txt', '.json')) and not f.endswith('.meta.json')]
            
            if files:
                report += f"## Flagged Files ({len(files)})\n\n"
                
                for file in sorted(files):
                    file_path = os.path.join(flagged_files_path, file)
                    metadata_file = f"{file_path}.meta.json"
                    
                    report += f"### {file}\n"
                    
                    if os.path.exists(metadata_file):
                        try:
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                            
                            fluff_analysis = metadata.get("fluff_analysis", {})
                            strategic_score = metadata.get("strategic_score", {})
                            
                            report += f"- **Fluff Score**: {fluff_analysis.get('fluff_score', 'N/A')}\n"
                            report += f"- **Signal Score**: {strategic_score.get('signal_score', 'N/A')}\n"
                            report += f"- **Danger Score**: {strategic_score.get('danger_score', 'N/A')}\n"
                            report += f"- **Rescue Reasons**: {', '.join(fluff_analysis.get('rescue_reasons', []))}\n"
                            
                        except Exception as e:
                            report += f"- **Error reading metadata**: {str(e)}\n"
                    
                    report += "\n"
        
        # Save report
        report_file = os.path.join(quarantine_path, "QUARANTINE_RESCUE_REPORT.md")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return report_file

    def generate_export_stats(self) -> Dict:
        """Generate statistics about the export"""
        stats = {
            "total_files": 0,
            "compass_core": 0,
            "human_review": 0,
            "quarantine": 0,
            "categories": {},
            "processing_decisions": {}
        }
        
        for root, dirs, files in os.walk(self.base_export_dir):
            for file in files:
                if file.endswith(('.md', '.txt', '.json')) and not file.endswith('.meta.json'):
                    stats["total_files"] += 1
                    
                    # Count by main folder
                    relative_path = os.path.relpath(root, self.base_export_dir)
                    main_folder = relative_path.split(os.sep)[0]
                    
                    if main_folder == "COMPASS_CORE":
                        stats["compass_core"] += 1
                    elif main_folder == "HUMAN_REVIEW":
                        stats["human_review"] += 1
                    elif main_folder == "QUARANTINE_RESCUE":
                        stats["quarantine"] += 1
                    
                    # Read metadata for detailed stats
                    metadata_file = os.path.join(root, f"{file}.meta.json")
                    if os.path.exists(metadata_file):
                        try:
                            with open(metadata_file, 'r', encoding='utf-8') as f:
                                metadata = json.load(f)
                            
                            # Count categories
                            category = metadata.get("classification", {}).get("primary_category", "unknown")
                            stats["categories"][category] = stats["categories"].get(category, 0) + 1
                            
                            # Count processing decisions
                            decision = metadata.get("strategic_score", {}).get("processing_decision", "unknown")
                            stats["processing_decisions"][decision] = stats["processing_decisions"].get(decision, 0) + 1
                            
                        except Exception as e:
                            logging.warning(f"Could not read metadata for {metadata_file}: {str(e)}")
        
        return stats

    def create_export_overview(self) -> str:
        """Create an overview of the entire export"""
        stats = self.generate_export_stats()
        
        overview = "# Compass Export Overview\n\n"
        overview += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        overview += "## Summary\n\n"
        overview += f"- **Total Files**: {stats['total_files']}\n"
        overview += f"- **Compass Core**: {stats['compass_core']}\n"
        overview += f"- **Human Review**: {stats['human_review']}\n"
        overview += f"- **Quarantine**: {stats['quarantine']}\n\n"
        
        overview += "## Categories\n\n"
        for category, count in sorted(stats["categories"].items(), key=lambda x: x[1], reverse=True):
            overview += f"- **{category}**: {count}\n"
        
        overview += "\n## Processing Decisions\n\n"
        for decision, count in sorted(stats["processing_decisions"].items(), key=lambda x: x[1], reverse=True):
            overview += f"- **{decision}**: {count}\n"
        
        # Save overview
        overview_file = os.path.join(self.base_export_dir, "EXPORT_OVERVIEW.md")
        with open(overview_file, 'w', encoding='utf-8') as f:
            f.write(overview)
        
        return overview_file

# Example usage
if __name__ == "__main__":
    exporter = CuratedExporter()
    
    # Example classification and strategic score
    classification = {
        "primary_category": "method_model",
        "secondary_categories": ["prompt_module"],
        "confidence": 0.85,
        "keywords_found": ["emotional anchor", "stance", "nervous system"],
        "compass_tags": ["compass:method_model", "keyword:emotional_anchor"],
        "processing_priority": "critical",
        "export_path": "COMPASS_CORE/method"
    }
    
    strategic_score = {
        "signal_score": 7.5,
        "danger_score": 0.5,
        "quality_score": 4.2,
        "originality_score": 3.8,
        "actionability_score": 4.5,
        "total_score": 8.2,
        "processing_decision": "SAFE_CORE - Add directly to Compass core"
    }
    
    # Create a test file
    test_file = "test_content.md"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("# Test Content\n\nThis is test content for export.")
    
    # Export the content
    exported_file = exporter.export_content(test_file, classification, strategic_score)
    
    if exported_file:
        print(f"Exported to: {exported_file}")
        
        # Generate reports
        summary_file = exporter.create_compass_core_summary()
        queue_file = exporter.create_human_review_queue()
        report_file = exporter.create_quarantine_rescue_report()
        overview_file = exporter.create_export_overview()
        
        print(f"Generated reports:")
        print(f"- Compass Core Summary: {summary_file}")
        print(f"- Human Review Queue: {queue_file}")
        print(f"- Quarantine Report: {report_file}")
        print(f"- Export Overview: {overview_file}")
    
    # Clean up test file
    if os.path.exists(test_file):
        os.remove(test_file)
