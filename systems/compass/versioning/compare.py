# build this

import yaml
import difflib
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Version:
    content: Dict
    timestamp: datetime
    version_id: str
    
class PromptVersioner:
    def __init__(self, storage_dir: str = "version_history"):
        self.storage_dir = storage_dir
        
    def compare_yaml(self, old_version: Version, new_version: Version) -> List[str]:
        """Compare two versions and return differences"""
        old_lines = yaml.dump(old_version.content, sort_keys=False).splitlines()
        new_lines = yaml.dump(new_version.content, sort_keys=False).splitlines()
        
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f'v{old_version.version_id}',
            tofile=f'v{new_version.version_id}',
            lineterm=''
        ))
        
        return diff
        
    def extract_changes(self, diff_lines: List[str]) -> List[Tuple[str, str]]:
        """Extract meaningful changes from diff output"""
        changes = []
        for line in diff_lines:
            if line.startswith('+') and not line.startswith('+++'):
                changes.append(('addition', line[1:].strip()))
            elif line.startswith('-') and not line.startswith('---'):
                changes.append(('deletion', line[1:].strip()))
        return changes
        
    def summarize_changes(self, changes: List[Tuple[str, str]]) -> str:
        """Create a human-readable summary of changes"""
        summary = []
        additions = [c[1] for c in changes if c[0] == 'addition']
        deletions = [c[1] for c in changes if c[0] == 'deletion']
        
        if additions:
            summary.append(f"Added {len(additions)} items:")
            summary.extend([f"  + {item}" for item in additions[:3]])
            if len(additions) > 3:
                summary.append(f"  + ...and {len(additions)-3} more")
                
        if deletions:
            summary.append(f"Removed {len(deletions)} items:")
            summary.extend([f"  - {item}" for item in deletions[:3]])
            if len(deletions) > 3:
                summary.append(f"  - ...and {len(deletions)-3} more")
                
        return "\n".join(summary)

def main():
    """Main comparison routine"""
    versioner = PromptVersioner()
    # TODO: Add CLI interface for comparing specific versions
    print("Version comparison tool ready")
    print("Use: python compare.py <old_version> <new_version>")

if __name__ == "__main__":
    main()