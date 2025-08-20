# build this

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import yaml
from dataclasses import dataclass, asdict
import jsonlines

@dataclass
class ProcessingLog:
    timestamp: str
    filename: str
    fluff_score: float
    detected_patterns: List[str]
    classified_as: str
    phase: str
    moved_to: str
    summary_action: str
    review_required: bool = False
    rescue_indicators: List[str] = None

class EnhancedLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Initialize log files
        self.fluff_log = self.log_dir / "fluff_detection.jsonl"
        self.move_log = self.log_dir / "move_tracking.log"
        self.stats_file = self.log_dir / "session_stats.md"
        
        # Set up logging handlers
        self._setup_logging()
        
        # Load fluff patterns
        self.patterns = self._load_patterns()
        
        # Session statistics
        self.session_stats = {
            "processed_files": 0,
            "quarantined_files": 0,
            "review_required": 0,
            "rescue_candidates": 0,
            "fluff_scores": [],
            "detected_patterns": {},
            "start_time": datetime.now().isoformat()
        }
    
    def _setup_logging(self):
        """Set up logging handlers"""
        # Move tracking logger
        self.move_logger = logging.getLogger("move_tracking")
        self.move_logger.setLevel(logging.INFO)
        move_handler = logging.FileHandler(self.move_log)
        move_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(message)s')
        )
        self.move_logger.addHandler(move_handler)
    
    def _load_patterns(self) -> Dict:
        """Load fluff detection patterns"""
        with open("enhanced_fluff_patterns.yaml", 'r') as f:
            return yaml.safe_load(f)
    
    def log_processing(self, file_path: str, analysis: Dict):
        """Log file processing with enhanced details"""
        # Calculate fluff score
        fluff_score = self._calculate_fluff_score(analysis)
        
        # Detect patterns
        detected = self._detect_patterns(analysis["content"])
        
        # Determine classification
        classified_as = self._classify_content(fluff_score, detected)
        
        # Create log entry
        log_entry = ProcessingLog(
            timestamp=datetime.now().isoformat(),
            filename=Path(file_path).name,
            fluff_score=fluff_score,
            detected_patterns=detected["patterns"],
            classified_as=classified_as,
            phase=self._determine_phase(file_path),
            moved_to=self._determine_destination(classified_as),
            summary_action=self._generate_summary(fluff_score, detected),
            review_required=2.0 <= fluff_score < 3.0,
            rescue_indicators=detected.get("rescue_indicators", [])
        )
        
        # Write to fluff detection log
        with jsonlines.open(self.fluff_log, mode='a') as writer:
            writer.write(asdict(log_entry))
        
        # Log move operation
        self.move_logger.info(
            f"Moved {log_entry.filename} to {log_entry.moved_to} "
            f"(Score: {log_entry.fluff_score:.1f})"
        )
        
        # Update session stats
        self._update_stats(log_entry)
    
    def _calculate_fluff_score(self, analysis: Dict) -> float:
        """Calculate detailed fluff score"""
        score = 0.0
        
        # Common GPT phrases (0.5 each)
        score += len(analysis.get("gpt_phrases", [])) * 0.5
        
        # Circular definitions (1.0 each)
        score += len(analysis.get("circular_defs", [])) * 1.0
        
        # Empty buzz structures (1.5 each)
        score += len(analysis.get("buzz_structures", [])) * 1.5
        
        # Redundancy pairs (0.75 each)
        score += len(analysis.get("redundancies", [])) * 0.75
        
        return min(score, 5.0)
    
    def _detect_patterns(self, content: str) -> Dict[str, List[str]]:
        """Detect various content patterns"""
        results = {
            "patterns": [],
            "rescue_indicators": []
        }
        
        # Check each pattern type
        for pattern_type, patterns in self.patterns.items():
            for pattern in patterns:
                if pattern.lower() in content.lower():
                    results["patterns"].append(f"{pattern_type}: {pattern}")
        
        # Check rescue indicators
        for indicator in self.patterns["rescue_indicators"]:
            if indicator.lower() in content.lower():
                results["rescue_indicators"].append(indicator)
        
        return results
    
    def _classify_content(self, fluff_score: float, detected: Dict) -> str:
        """Classify content based on analysis"""
        if fluff_score >= 3.0:
            return "Quarantine"
        elif fluff_score >= 2.0:
            return "Review Required"
        elif detected["rescue_indicators"]:
            return "Potential Value"
        else:
            return "Keep"
    
    def _determine_phase(self, file_path: str) -> str:
        """Determine appropriate phase for content"""
        path = Path(file_path)
        if "Phase" in str(path):
            return str(path).split("Phase")[1].split("/")[0]
        return "Phase1"
    
    def _determine_destination(self, classification: str) -> str:
        """Determine destination folder based on classification"""
        if classification == "Quarantine":
            return "99_trash_quarantine"
        elif classification == "Review Required":
            return "40_drafts"
        else:
            return "00_docs"
    
    def _generate_summary(self, fluff_score: float, detected: Dict) -> str:
        """Generate action summary"""
        if fluff_score >= 3.0:
            return f"Quarantined due to high fluff score ({fluff_score:.1f}) and patterns"
        elif fluff_score >= 2.0:
            return f"Marked for review (score: {fluff_score:.1f})"
        elif detected["rescue_indicators"]:
            return f"Kept due to valuable indicators: {', '.join(detected['rescue_indicators'])}"
        else:
            return "Kept as valuable content"
    
    def _update_stats(self, log_entry: ProcessingLog):
        """Update session statistics"""
        self.session_stats["processed_files"] += 1
        self.session_stats["fluff_scores"].append(log_entry.fluff_score)
        
        if log_entry.classified_as == "Quarantine":
            self.session_stats["quarantined_files"] += 1
        elif log_entry.review_required:
            self.session_stats["review_required"] += 1
        
        if log_entry.rescue_indicators:
            self.session_stats["rescue_candidates"] += 1
        
        # Update pattern counts
        for pattern in log_entry.detected_patterns:
            self.session_stats["detected_patterns"][pattern] = \
                self.session_stats["detected_patterns"].get(pattern, 0) + 1
    
    def write_stats_markdown(self):
        """Write session statistics to markdown"""
        stats_md = f"""# Processing Session Statistics
Generated: {datetime.now().isoformat()}

## Overview
- Processed Files: {self.session_stats['processed_files']}
- Quarantined: {self.session_stats['quarantined_files']}
- Review Required: {self.session_stats['review_required']}
- Rescue Candidates: {self.session_stats['rescue_candidates']}

## Fluff Scores
- Average: {sum(self.session_stats['fluff_scores']) / len(self.session_stats['fluff_scores']):.2f}
- Max: {max(self.session_stats['fluff_scores']):.2f}
- Min: {min(self.session_stats['fluff_scores']):.2f}

## Pattern Detection
Most Common Patterns:
{self._format_pattern_stats()}

## Session Duration
- Start: {self.session_stats['start_time']}
- End: {datetime.now().isoformat()}
"""
        
        with open(self.stats_file, 'w') as f:
            f.write(stats_md)
    
    def _format_pattern_stats(self) -> str:
        """Format pattern statistics for markdown"""
        sorted_patterns = sorted(
            self.session_stats["detected_patterns"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return "\n".join([
            f"- {pattern}: {count} occurrences"
            for pattern, count in sorted_patterns[:10]
        ])