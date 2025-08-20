# Document tracking implementation

import json
import os
from datetime import datetime
from typing import Dict, List
from pathlib import Path

class DocumentTracker:
    def __init__(self, tracking_dir: str = "tracking"):
        self.tracking_dir = Path(tracking_dir)
        self.tracking_dir.mkdir(exist_ok=True)
        
        # Initialize tracking files
        self.processed_log = self.tracking_dir / "processed_documents.jsonl"
        self.category_index = self.tracking_dir / "category_index.json"
        self.stats_file = self.tracking_dir / "processing_stats.json"
        
        # Load or initialize tracking data
        self.load_tracking_data()
    
    def load_tracking_data(self):
        """Load or initialize tracking data"""
        # Load category index
        if self.category_index.exists():
            with open(self.category_index, 'r') as f:
                self.categories = json.load(f)
        else:
            self.categories = {}
        
        # Load stats
        if self.stats_file.exists():
            with open(self.stats_file, 'r') as f:
                self.stats = json.load(f)
        else:
            self.stats = {
                "total_processed": 0,
                "by_category": {},
                "by_status": {},
                "last_updated": datetime.now().isoformat()
            }
    
    def save_tracking_data(self):
        """Save tracking data to disk"""
        # Save category index
        with open(self.category_index, 'w') as f:
            json.dump(self.categories, f, indent=2)
        
        # Save stats
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def track_document(self, file_path: str, analysis: Dict, categories: List[str]):
        """Track document processing"""
        doc_info = {
            "file_path": str(file_path),
            "processed_at": datetime.now().isoformat(),
            "categories": categories,
            "analysis_summary": analysis.get("analysis", ""),
            "file_hash": self._calculate_file_hash(file_path)
        }
        
        # Append to processed log
        with open(self.processed_log, 'a') as f:
            f.write(json.dumps(doc_info) + '\n')
        
        # Update category index
        for category in categories:
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(doc_info["file_hash"])
        
        # Update stats
        self.stats["total_processed"] += 1
        for category in categories:
            self.stats["by_category"][category] = \
                self.stats["by_category"].get(category, 0) + 1
        
        self.stats["last_updated"] = datetime.now().isoformat()
        
        # Save updates
        self.save_tracking_data()
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file contents"""
        import hashlib
        
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def get_document_history(self, file_path: str = None, category: str = None) -> List[Dict]:
        """Get processing history for a file or category"""
        history = []
        
        with open(self.processed_log, 'r') as f:
            for line in f:
                entry = json.loads(line)
                if file_path and entry["file_path"] == str(file_path):
                    history.append(entry)
                elif category and category in entry["categories"]:
                    history.append(entry)
        
        return history
    
    def generate_report(self) -> str:
        """Generate markdown report of processing status"""
        report = f"""# Document Processing Report
Generated: {datetime.now().isoformat()}

## Overall Statistics
- Total Documents Processed: {self.stats['total_processed']}
- Last Updated: {self.stats['last_updated']}

## By Category
"""
        
        for category, count in self.stats["by_category"].items():
            report += f"- {category}: {count}\n"
        
        # Add recent history
        report += "\n## Recent Processing History\n"
        history = []
        with open(self.processed_log, 'r') as f:
            for line in f:
                history.append(json.loads(line))
        
        for entry in history[-10:]:  # Show last 10 entries
            report += f"- {Path(entry['file_path']).name} ({', '.join(entry['categories'])})\n"
        
        return report
