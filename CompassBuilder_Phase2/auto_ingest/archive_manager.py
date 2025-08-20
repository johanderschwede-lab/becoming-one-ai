# build this

import os
import shutil
from pathlib import Path
from datetime import datetime
import json
import yaml
from typing import Dict, List, Optional
import hashlib

class ArchiveManager:
    def __init__(self, base_dir: str = "archive"):
        self.base_dir = Path(base_dir)
        self.setup_archive_structure()
        
        # Load or create archive index
        self.index_file = self.base_dir / "archive_index.yaml"
        self.archive_index = self.load_archive_index()
        
    def setup_archive_structure(self):
        """Create archive directory structure"""
        # Main archive directories
        directories = {
            "processed": {
                "method_core": {},
                "technical": {},
                "prompts": {},
                "documentation": {}
            },
            "quarantined": {
                "fluff": {},
                "duplicates": {},
                "outdated": {}
            },
            "rescued": {
                "auto_rescued": {},
                "manual_rescued": {}
            },
            "metadata": {
                "processing_logs": {},
                "analysis_results": {},
                "rescue_records": {}
            }
        }
        
        def create_dirs(path: Path, structure: Dict):
            for name, substructure in structure.items():
                current = path / name
                current.mkdir(exist_ok=True, parents=True)
                if substructure:
                    create_dirs(current, substructure)
        
        create_dirs(self.base_dir, directories)
    
    def load_archive_index(self) -> Dict:
        """Load or create archive index"""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                return yaml.safe_load(f)
        else:
            return {
                "files": {},
                "statistics": {
                    "total_archived": 0,
                    "by_category": {},
                    "by_status": {}
                },
                "last_updated": datetime.now().isoformat()
            }
    
    def save_archive_index(self):
        """Save archive index"""
        self.archive_index["last_updated"] = datetime.now().isoformat()
        with open(self.index_file, 'w') as f:
            yaml.dump(self.archive_index, f, sort_keys=False)
    
    def calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file contents"""
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def determine_archive_category(self, file_path: str, analysis: Dict) -> str:
        """Determine appropriate archive category"""
        filename = Path(file_path).name.lower()
        content_type = analysis.get("content_type", "")
        
        if "prompt" in filename or "prompt" in content_type:
            return "prompts"
        elif any(term in filename for term in ["method", "becoming", "essence"]):
            return "method_core"
        elif any(term in filename for term in ["tech", "code", "api", "schema"]):
            return "technical"
        else:
            return "documentation"
    
    def archive_file(self, file_path: str, analysis: Dict, status: str = "processed") -> Dict:
        """Archive a processed file with metadata"""
        file_path = Path(file_path)
        
        # Calculate file hash
        file_hash = self.calculate_file_hash(file_path)
        
        # Check for duplicates
        if file_hash in self.archive_index["files"]:
            return self.handle_duplicate(file_path, file_hash)
        
        # Determine archive location
        if status == "processed":
            category = self.determine_archive_category(str(file_path), analysis)
            archive_subdir = self.base_dir / "processed" / category
        elif status == "quarantined":
            archive_subdir = self.base_dir / "quarantined" / "fluff"
        elif status == "rescued":
            archive_subdir = self.base_dir / "rescued" / "auto_rescued"
        else:
            raise ValueError(f"Unknown status: {status}")
        
        # Create archive metadata
        metadata = {
            "original_path": str(file_path),
            "archived_at": datetime.now().isoformat(),
            "status": status,
            "category": category if status == "processed" else None,
            "file_hash": file_hash,
            "analysis_summary": analysis,
            "size_bytes": file_path.stat().st_size
        }
        
        # Create archive filename with timestamp
        archive_name = f"{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_path.suffix}"
        archive_path = archive_subdir / archive_name
        
        # Copy file to archive
        shutil.copy2(file_path, archive_path)
        
        # Save metadata
        metadata_path = self.base_dir / "metadata" / "processing_logs" / f"{archive_name}.meta.yaml"
        with open(metadata_path, 'w') as f:
            yaml.dump(metadata, f, sort_keys=False)
        
        # Update index
        self.archive_index["files"][file_hash] = {
            "archive_path": str(archive_path),
            "metadata_path": str(metadata_path),
            "archived_at": metadata["archived_at"]
        }
        
        # Update statistics
        self.archive_index["statistics"]["total_archived"] += 1
        if status == "processed":
            self.archive_index["statistics"]["by_category"][category] = \
                self.archive_index["statistics"]["by_category"].get(category, 0) + 1
        self.archive_index["statistics"]["by_status"][status] = \
            self.archive_index["statistics"]["by_status"].get(status, 0) + 1
        
        self.save_archive_index()
        
        return metadata
    
    def handle_duplicate(self, file_path: Path, file_hash: str) -> Dict:
        """Handle duplicate file"""
        existing = self.archive_index["files"][file_hash]
        
        # Move to duplicates folder
        duplicate_dir = self.base_dir / "quarantined" / "duplicates"
        duplicate_path = duplicate_dir / f"{file_path.stem}_duplicate_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_path.suffix}"
        shutil.copy2(file_path, duplicate_path)
        
        metadata = {
            "original_path": str(file_path),
            "archived_at": datetime.now().isoformat(),
            "status": "duplicate",
            "duplicate_of": existing["archive_path"],
            "file_hash": file_hash
        }
        
        return metadata
    
    def get_archive_stats(self) -> Dict:
        """Get archive statistics"""
        stats = self.archive_index["statistics"].copy()
        stats["last_24h"] = {
            "total": 0,
            "by_status": {}
        }
        
        # Calculate last 24h stats
        cutoff = datetime.now().timestamp() - (24 * 60 * 60)
        for file_info in self.archive_index["files"].values():
            archived_at = datetime.fromisoformat(file_info["archived_at"]).timestamp()
            if archived_at > cutoff:
                stats["last_24h"]["total"] += 1
                
                # Get status from metadata
                with open(file_info["metadata_path"], 'r') as f:
                    metadata = yaml.safe_load(f)
                    status = metadata["status"]
                    stats["last_24h"]["by_status"][status] = \
                        stats["last_24h"]["by_status"].get(status, 0) + 1
        
        return stats
    
    def generate_archive_report(self) -> str:
        """Generate markdown report of archive status"""
        stats = self.get_archive_stats()
        
        report = f"""# Archive Status Report
Generated: {datetime.now().isoformat()}

## Overall Statistics
- Total Files Archived: {stats['total_archived']}
- Last 24 Hours: {stats['last_24h']['total']}

## By Category
"""
        for category, count in stats["by_category"].items():
            report += f"- {category}: {count}\n"
        
        report += "\n## By Status\n"
        for status, count in stats["by_status"].items():
            report += f"- {status}: {count}\n"
        
        report += "\n## Last 24 Hours by Status\n"
        for status, count in stats["last_24h"]["by_status"].items():
            report += f"- {status}: {count}\n"
        
        return report
    
    def cleanup_source_file(self, file_path: str):
        """Safely remove source file after archiving"""
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Warning: Could not remove source file {file_path}: {str(e)}")
    
    def find_archived_file(self, original_path: str) -> Optional[Dict]:
        """Find archived version of a file"""
        original_path = str(Path(original_path))
        
        for file_hash, info in self.archive_index["files"].items():
            with open(info["metadata_path"], 'r') as f:
                metadata = yaml.safe_load(f)
                if metadata["original_path"] == original_path:
                    return {
                        "archive_path": info["archive_path"],
                        "metadata": metadata
                    }
        
        return None
