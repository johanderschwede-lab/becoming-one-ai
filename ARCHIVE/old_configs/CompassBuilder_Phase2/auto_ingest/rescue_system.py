# build this

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import yaml
from datetime import datetime

@dataclass
class RescueSnippet:
    filename: str
    fluff_score: float
    matched_patterns: List[str]
    context_paragraphs: List[str]
    clean_headers: List[str]
    glossary_terms: List[str]
    rescue_reason: Optional[str] = None

class RescueSystem:
    def __init__(self, quarantine_dir: str = "99_trash_quarantine"):
        self.quarantine_dir = Path(quarantine_dir)
        self.rescue_backup_dir = self.quarantine_dir / "_rescue_backup"
        self.rescue_backup_dir.mkdir(exist_ok=True)
        
        # Load glossary terms
        self.glossary_terms = self._load_glossary()
        
        # Initialize rescue queue
        self.rescue_queue_file = Path("logs/fluff_rescue_candidates.md")
        self._init_rescue_queue()
    
    def _load_glossary(self) -> List[str]:
        """Load internal glossary terms"""
        return [
            "essence", "digest", "stance", "pearl", "anchor",
            "emotional anchor", "feeling-state", "schaubilder",
            "becoming one", "transformation", "resistance",
            "capacity", "journey", "integration"
        ]
    
    def _init_rescue_queue(self):
        """Initialize rescue queue file"""
        if not self.rescue_queue_file.exists():
            self.rescue_queue_file.parent.mkdir(exist_ok=True)
            self.rescue_queue_file.write_text(
                "# Fluff Rescue Queue\n\n"
                "Files quarantined but potentially valuable:\n\n"
            )
    
    def extract_context(self, content: str, fluff_match: str) -> List[str]:
        """Extract paragraphs around fluff matches"""
        paragraphs = re.split(r'\n\s*\n', content)
        context = []
        
        for i, para in enumerate(paragraphs):
            if fluff_match.lower() in para.lower():
                # Get surrounding paragraphs
                start = max(0, i-1)
                end = min(len(paragraphs), i+2)
                context.extend(paragraphs[start:end])
        
        return context
    
    def extract_clean_headers(self, content: str) -> List[str]:
        """Extract non-fluff headers"""
        headers = re.findall(r'^#{2,3}\s+(.+)$', content, re.MULTILINE)
        
        # Load fluff patterns
        with open("enhanced_fluff_patterns.yaml", 'r') as f:
            patterns = yaml.safe_load(f)
        
        # Filter out headers containing fluff
        clean_headers = []
        for header in headers:
            if not any(pattern.lower() in header.lower() 
                      for pattern_list in patterns.values()
                      for pattern in pattern_list):
                clean_headers.append(header)
        
        return clean_headers[:3]  # Return first 3 clean headers
    
    def count_glossary_terms(self, content: str) -> List[str]:
        """Count occurrences of glossary terms"""
        found_terms = []
        for term in self.glossary_terms:
            if term.lower() in content.lower():
                found_terms.append(term)
        return found_terms
    
    def should_auto_rescue(self, content: str, fluff_score: float) -> Tuple[bool, str]:
        """Determine if content should be auto-rescued"""
        clean_headers = self.extract_clean_headers(content)
        glossary_terms = self.count_glossary_terms(content)
        
        rescue_reason = None
        
        if len(clean_headers) > 3:
            rescue_reason = f"Contains {len(clean_headers)} well-structured headers"
        elif len(glossary_terms) > 2:
            rescue_reason = f"Contains {len(glossary_terms)} glossary terms: {', '.join(glossary_terms)}"
        
        if rescue_reason:
            adjusted_score = max(0, fluff_score - 1)
            return adjusted_score <= 2, rescue_reason
            
        return False, None
    
    def backup_quarantined_content(self, file_path: str, content: str, 
                                 fluff_matches: List[str], fluff_score: float) -> RescueSnippet:
        """Create backup of quarantined content with context"""
        # Extract important content
        contexts = []
        for match in fluff_matches:
            contexts.extend(self.extract_context(content, match))
        
        clean_headers = self.extract_clean_headers(content)
        glossary_terms = self.count_glossary_terms(content)
        
        # Create rescue snippet
        snippet = RescueSnippet(
            filename=Path(file_path).name,
            fluff_score=fluff_score,
            matched_patterns=fluff_matches,
            context_paragraphs=contexts,
            clean_headers=clean_headers,
            glossary_terms=glossary_terms
        )
        
        # Save backup
        backup_path = self.rescue_backup_dir / f"{snippet.filename}_fluffmatch.txt"
        with open(backup_path, 'w') as f:
            f.write(f"# Rescue Backup for {snippet.filename}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            
            f.write("## Fluff Analysis\n")
            f.write(f"- Score: {snippet.fluff_score}\n")
            f.write(f"- Matched Patterns: {', '.join(snippet.matched_patterns)}\n")
            f.write(f"- Clean Headers: {', '.join(snippet.clean_headers)}\n")
            f.write(f"- Glossary Terms: {', '.join(snippet.glossary_terms)}\n\n")
            
            f.write("## Context Paragraphs\n")
            for i, para in enumerate(snippet.context_paragraphs, 1):
                f.write(f"\n### Context {i}\n{para}\n")
        
        return snippet
    
    def add_to_rescue_queue(self, snippet: RescueSnippet):
        """Add file to rescue queue"""
        with open(self.rescue_queue_file, 'a') as f:
            patterns_str = ', '.join(snippet.matched_patterns[:2])  # Show first 2 patterns
            f.write(
                f"- [ ] `{snippet.filename}` – score: {snippet.fluff_score:.1f} – "
                f"pattern: \"{patterns_str}\" – headers: {len(snippet.clean_headers)} – "
                f"terms: {len(snippet.glossary_terms)}\n"
            )
            if snippet.rescue_reason:
                f.write(f"      ↳ *Potential value: {snippet.rescue_reason}*\n")
    
    def process_quarantined_file(self, file_path: str, content: str, 
                               fluff_matches: List[str], fluff_score: float) -> str:
        """Process a quarantined file and determine its fate"""
        # Check for auto-rescue
        should_rescue, reason = self.should_auto_rescue(content, fluff_score)
        
        # Create backup with context
        snippet = self.backup_quarantined_content(
            file_path, content, fluff_matches, fluff_score
        )
        
        if should_rescue:
            snippet.rescue_reason = reason
            destination = "Phase0/40_drafts"
        else:
            destination = "99_trash_quarantine"
        
        # Add to rescue queue
        self.add_to_rescue_queue(snippet)
        
        return destination
