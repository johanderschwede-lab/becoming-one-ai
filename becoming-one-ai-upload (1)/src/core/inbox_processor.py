#!/usr/bin/env python3
"""
Becoming One™ INBOX Processor
============================

Simple, powerful system that watches your NAS INBOX folder and automatically:
- Detects new files (transcripts, documents, audio, video)
- Uses AI to identify Johan vs Marianne vs participants
- Automatically categorizes content (teaching vs community)
- Extracts and uploads to your knowledge base
- Generates content suggestions for social media
- Moves processed files to organized folders

Just drop files in INBOX and everything happens automatically!
"""

import os
import json
import asyncio
import hashlib
import shutil
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import re
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from openai import OpenAI

from .knowledge_management_system import BecomingOneKnowledgeSystem, ContentType, ContentSource


class ProcessingStatus(Enum):
    """Status of file processing"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class ProcessedFile:
    """Result of processing a file"""
    file_path: str
    original_name: str
    file_type: str
    processing_status: ProcessingStatus
    johan_content: List[str] = field(default_factory=list)
    marianne_content: List[str] = field(default_factory=list)
    participant_content: List[str] = field(default_factory=list)
    teaching_segments: int = 0
    community_segments: int = 0
    content_suggestions: int = 0
    processing_time: float = 0.0
    error_message: str = ""
    processed_at: datetime = field(default_factory=datetime.now)


class InboxProcessor:
    """AI agent that processes all content dropped in INBOX folder"""
    
    def __init__(self, inbox_folder: str):
        self.inbox_folder = Path(inbox_folder)
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.knowledge_system = BecomingOneKnowledgeSystem()
        
        # Create folder structure
        self._setup_folders()
        
        # Processing queue
        self.processing_queue = asyncio.Queue()
        self.is_processing = False
        
        # File type handlers
        self.supported_extensions = {
            '.txt', '.md', '.docx', '.pdf',  # Documents
            '.mp3', '.wav', '.m4a',          # Audio files
            '.mp4', '.mov', '.avi',          # Video files
            '.json'                          # Structured data
        }
    
    def _setup_folders(self):
        """Create organized folder structure"""
        folders = [
            self.inbox_folder,
            self.inbox_folder / "processing",
            self.inbox_folder / "completed",
            self.inbox_folder / "failed",
            self.inbox_folder / "teaching_materials",
            self.inbox_folder / "community_content",
            self.inbox_folder / "content_suggestions",
            self.inbox_folder / "logs"
        ]
        
        for folder in folders:
            folder.mkdir(parents=True, exist_ok=True)
        
        print(f"📁 INBOX system ready at: {self.inbox_folder}")
        print("   Drop files here for automatic processing!")
    
    def start_watching(self):
        """Start watching the INBOX folder"""
        event_handler = InboxFileHandler(self)
        observer = Observer()
        
        observer.schedule(event_handler, str(self.inbox_folder), recursive=False)
        observer.start()
        
        # Start processing queue
        asyncio.create_task(self._process_queue())
        
        print(f"👁️  Watching INBOX: {self.inbox_folder}")
        print("🤖 AI processor is active!")
        print("\n" + "="*60)
        print("USAGE:")
        print("1. Drop any file in the INBOX folder")
        print("2. AI automatically identifies Johan/Marianne/participants")
        print("3. Teaching content → Knowledge base")
        print("4. Community content → Separate storage")
        print("5. Content suggestions → Generated automatically")
        print("6. Files moved to organized folders")
        print("="*60 + "\n")
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
            observer.join()
            print("🛑 INBOX processor stopped")
    
    async def _process_queue(self):
        """Process files from the queue"""
        while True:
            try:
                if not self.processing_queue.empty() and not self.is_processing:
                    file_path = await self.processing_queue.get()
                    await self._process_file(file_path)
                    self.processing_queue.task_done()
                else:
                    await asyncio.sleep(1)
            except Exception as e:
                print(f"❌ Queue processing error: {e}")
                await asyncio.sleep(5)
    
    async def add_file_to_queue(self, file_path: str):
        """Add file to processing queue"""
        await self.processing_queue.put(file_path)
        print(f"📥 Queued for processing: {Path(file_path).name}")
    
    async def _process_file(self, file_path: str):
        """Process a single file with AI"""
        start_time = time.time()
        file_path = Path(file_path)
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return
        
        self.is_processing = True
        
        try:
            print(f"\n🔄 Processing: {file_path.name}")
            
            # Move to processing folder
            processing_path = self.inbox_folder / "processing" / file_path.name
            shutil.move(str(file_path), str(processing_path))
            
            # Process the file
            result = await self._analyze_and_categorize_content(processing_path)
            
            # Upload to knowledge base
            await self._upload_processed_content(result)
            
            # Generate content suggestions
            await self._generate_content_suggestions(result)
            
            # Move to completed folder
            completed_path = self.inbox_folder / "completed" / file_path.name
            shutil.move(str(processing_path), str(completed_path))
            
            # Log results
            result.processing_time = time.time() - start_time
            result.processing_status = ProcessingStatus.COMPLETED
            await self._log_processing_result(result)
            
            print(f"✅ Completed: {file_path.name}")
            print(f"   📚 Teaching segments: {result.teaching_segments}")
            print(f"   👥 Community segments: {result.community_segments}")
            print(f"   🎬 Content suggestions: {result.content_suggestions}")
            print(f"   ⏱️  Processing time: {result.processing_time:.1f}s")
            
        except Exception as e:
            # Move to failed folder
            try:
                failed_path = self.inbox_folder / "failed" / file_path.name
                if processing_path.exists():
                    shutil.move(str(processing_path), str(failed_path))
            except:
                pass
            
            # Log error
            result = ProcessedFile(
                file_path=str(file_path),
                original_name=file_path.name,
                file_type=file_path.suffix,
                processing_status=ProcessingStatus.FAILED,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
            await self._log_processing_result(result)
            
            print(f"❌ Failed to process {file_path.name}: {e}")
        
        finally:
            self.is_processing = False
    
    async def _analyze_and_categorize_content(self, file_path: Path) -> ProcessedFile:
        """Main AI analysis of the content"""
        
        # Read file content
        content = await self._read_file_content(file_path)
        
        # AI analysis prompt
        analysis_prompt = f"""
        Analyze this content from Johan and Marianne's Becoming One™ work.
        
        CONTENT:
        {content}
        
        TASKS:
        1. SPEAKER IDENTIFICATION: Identify what Johan says, what Marianne says, and what participants/audience say
        2. CONTENT CATEGORIZATION: Separate teaching content from community feedback/questions
        3. CONCEPT EXTRACTION: Find Becoming One™ concepts (emotional anchors, feeling-states, manifestation, etc.)
        4. SHORT-FORM POTENTIAL: Identify segments suitable for social media clips
        
        Return detailed JSON:
        {{
            "speakers_identified": {{
                "johan_segments": ["segment 1 text", "segment 2 text"],
                "marianne_segments": ["segment 1 text", "segment 2 text"],
                "participant_segments": ["question/feedback 1", "question/feedback 2"]
            }},
            "content_categories": {{
                "teaching_segments": [
                    {{
                        "speaker": "johan|marianne",
                        "content": "teaching content",
                        "concepts": ["emotional_anchors", "feeling_states"],
                        "feeling_states": ["safety", "belonging"],
                        "anchor_types": ["abandonment", "unworthiness"]
                    }}
                ],
                "community_segments": [
                    {{
                        "type": "question|feedback|insight",
                        "content": "participant content",
                        "themes": ["transformation", "relationships"]
                    }}
                ]
            }},
            "short_form_candidates": [
                {{
                    "content": "clip-worthy content",
                    "speaker": "johan|marianne",
                    "duration_estimate": 45,
                    "hook_potential": 0.8,
                    "platform_suitability": ["tiktok", "youtube_shorts"]
                }}
            ],
            "overall_themes": ["theme1", "theme2"],
            "confidence_score": 0.9
        }}
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are an expert at analyzing Becoming One™ content. You understand:
                        - Johan and Marianne's teaching style and voice
                        - Becoming One™ concepts: emotional anchors, feeling-states, manifestation, anti-bypass
                        - The difference between teaching content and participant responses
                        - What makes good short-form social media content
                        
                        Be thorough and accurate in your analysis."""
                    },
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=3000
            )
            
            # Parse AI response
            analysis = json.loads(response.choices[0].message.content)
            
            # Create result object
            result = ProcessedFile(
                file_path=str(file_path),
                original_name=file_path.name,
                file_type=file_path.suffix,
                processing_status=ProcessingStatus.PROCESSING,
                johan_content=analysis.get("speakers_identified", {}).get("johan_segments", []),
                marianne_content=analysis.get("speakers_identified", {}).get("marianne_segments", []),
                participant_content=analysis.get("speakers_identified", {}).get("participant_segments", []),
                teaching_segments=len(analysis.get("content_categories", {}).get("teaching_segments", [])),
                community_segments=len(analysis.get("content_categories", {}).get("community_segments", [])),
                content_suggestions=len(analysis.get("short_form_candidates", []))
            )
            
            # Store detailed analysis
            result.detailed_analysis = analysis
            
            return result
            
        except Exception as e:
            print(f"❌ AI analysis failed: {e}")
            # Return basic result
            return ProcessedFile(
                file_path=str(file_path),
                original_name=file_path.name,
                file_type=file_path.suffix,
                processing_status=ProcessingStatus.FAILED,
                error_message=f"AI analysis failed: {e}"
            )
    
    async def _read_file_content(self, file_path: Path) -> str:
        """Read content from various file types"""
        
        try:
            if file_path.suffix.lower() in ['.txt', '.md']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            
            elif file_path.suffix.lower() == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'transcript' in data:
                        return data['transcript']
                    else:
                        return json.dumps(data, indent=2)
            
            elif file_path.suffix.lower() == '.docx':
                try:
                    import docx
                    doc = docx.Document(file_path)
                    return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
                except ImportError:
                    return f"[DOCX file - install python-docx to process: {file_path.name}]"
            
            elif file_path.suffix.lower() == '.pdf':
                return f"[PDF file detected - manual processing needed: {file_path.name}]"
            
            elif file_path.suffix.lower() in ['.mp3', '.wav', '.m4a', '.mp4', '.mov']:
                return f"[Media file detected - transcription needed: {file_path.name}]"
            
            else:
                return f"[Unsupported file type: {file_path.suffix}]"
                
        except Exception as e:
            return f"[Error reading file: {e}]"
    
    async def _upload_processed_content(self, result: ProcessedFile):
        """Upload teaching content to knowledge base"""
        
        if not hasattr(result, 'detailed_analysis'):
            return
        
        analysis = result.detailed_analysis
        teaching_segments = analysis.get("content_categories", {}).get("teaching_segments", [])
        
        for segment in teaching_segments:
            try:
                # Determine source
                speaker = segment.get("speaker", "unknown")
                if speaker == "johan":
                    source = ContentSource.JOHAN_ORIGINAL
                elif speaker == "marianne":
                    source = ContentSource.MARIANNE_ORIGINAL
                else:
                    source = ContentSource.WORKSHOP_RECORDING
                
                # Upload to knowledge base
                material_id = await self.knowledge_system.upload_teaching_material(
                    title=f"Teaching - {result.original_name} - {speaker.title()}",
                    content=segment["content"],
                    material_type="method_description",
                    source_type=source.value,
                    metadata={
                        "speaker": speaker,
                        "concepts": segment.get("concepts", []),
                        "feeling_states": segment.get("feeling_states", []),
                        "anchor_types": segment.get("anchor_types", []),
                        "original_file": result.original_name,
                        "auto_processed": True,
                        "processed_date": datetime.now().isoformat()
                    }
                )
                
                print(f"  📚 Uploaded teaching segment: {material_id[:8]}")
                
            except Exception as e:
                print(f"  ❌ Failed to upload teaching segment: {e}")
        
        # Store community content
        community_segments = analysis.get("content_categories", {}).get("community_segments", [])
        for segment in community_segments:
            try:
                await self.knowledge_system.add_community_content(
                    content=segment["content"],
                    category=segment.get("type", "unknown"),
                    themes=segment.get("themes", []),
                    metadata={
                        "original_file": result.original_name,
                        "auto_processed": True,
                        "processed_date": datetime.now().isoformat()
                    }
                )
                print(f"  👥 Stored community segment")
                
            except Exception as e:
                print(f"  ❌ Failed to store community segment: {e}")
    
    async def _generate_content_suggestions(self, result: ProcessedFile):
        """Generate social media content suggestions"""
        
        if not hasattr(result, 'detailed_analysis'):
            return
        
        analysis = result.detailed_analysis
        short_form_candidates = analysis.get("short_form_candidates", [])
        
        if not short_form_candidates:
            return
        
        suggestions = []
        
        for candidate in short_form_candidates:
            try:
                suggestion = await self._create_content_suggestion(candidate, result.original_name)
                suggestions.append(suggestion)
            except Exception as e:
                print(f"  ❌ Failed to create content suggestion: {e}")
        
        # Save suggestions to file
        if suggestions:
            suggestions_file = self.inbox_folder / "content_suggestions" / f"{result.original_name}_suggestions.json"
            
            with open(suggestions_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "source_file": result.original_name,
                    "generated_at": datetime.now().isoformat(),
                    "suggestions": suggestions
                }, f, indent=2)
            
            print(f"  🎬 Saved {len(suggestions)} content suggestions")
    
    async def _create_content_suggestion(self, candidate: Dict[str, Any], source_file: str) -> Dict[str, Any]:
        """Create a single content suggestion"""
        
        prompt = f"""
        Create a TikTok/YouTube Shorts/Instagram Reels suggestion based on this Becoming One™ content:
        
        Content: "{candidate['content']}"
        Speaker: {candidate.get('speaker', 'unknown')}
        Estimated Duration: {candidate.get('duration_estimate', 60)} seconds
        
        Create:
        1. Hook (first 3 seconds) - attention-grabbing opener
        2. Main teaching point (clear, actionable insight)
        3. Visual suggestions (what to show on screen)
        4. Call to action
        5. Title options (3 variations)
        6. Hashtags (8-10 relevant ones)
        7. Platform recommendations
        
        Make it authentic to Johan/Marianne's voice and the Becoming One™ method.
        
        Return JSON format.
        """
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert at creating engaging short-form video content for spiritual and personal development. Focus on authentic, valuable content that helps people grow."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        suggestion = json.loads(response.choices[0].message.content)
        suggestion["source_file"] = source_file
        suggestion["hook_potential"] = candidate.get("hook_potential", 0.5)
        suggestion["platforms"] = candidate.get("platform_suitability", ["tiktok", "youtube_shorts", "instagram_reels"])
        
        return suggestion
    
    async def _log_processing_result(self, result: ProcessedFile):
        """Log processing results for tracking"""
        
        log_file = self.inbox_folder / "logs" / f"processing_log_{datetime.now().strftime('%Y%m')}.jsonl"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "file": result.original_name,
            "status": result.processing_status.value,
            "teaching_segments": result.teaching_segments,
            "community_segments": result.community_segments,
            "content_suggestions": result.content_suggestions,
            "processing_time": result.processing_time,
            "error": result.error_message
        }
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')


class InboxFileHandler(FileSystemEventHandler):
    """Handles file system events in the INBOX folder"""
    
    def __init__(self, processor: InboxProcessor):
        self.processor = processor
        self.processing_delay = 2  # Wait 2 seconds after file creation to ensure it's fully written
    
    def on_created(self, event):
        """Handle new file creation"""
        if not event.is_directory:
            file_path = Path(event.src_path)
            
            if self._should_process_file(file_path):
                # Add delay to ensure file is fully written
                asyncio.create_task(self._delayed_process(str(file_path)))
    
    def on_moved(self, event):
        """Handle file moves (like drag and drop completion)"""
        if not event.is_directory:
            file_path = Path(event.dest_path)
            
            if self._should_process_file(file_path):
                asyncio.create_task(self._delayed_process(str(file_path)))
    
    def _should_process_file(self, file_path: Path) -> bool:
        """Check if file should be processed"""
        
        # Skip if in subdirectories (already processed or processing)
        if len(file_path.parts) > len(self.processor.inbox_folder.parts) + 1:
            return False
        
        # Check file extension
        if file_path.suffix.lower() not in self.processor.supported_extensions:
            print(f"⚠️  Unsupported file type: {file_path.name}")
            return False
        
        # Skip temporary files
        if file_path.name.startswith('.') or '~' in file_path.name:
            return False
        
        # Skip if too small (likely incomplete)
        if file_path.stat().st_size < 100:  # Less than 100 bytes
            return False
        
        return True
    
    async def _delayed_process(self, file_path: str):
        """Add file to processing queue after delay"""
        await asyncio.sleep(self.processing_delay)
        await self.processor.add_file_to_queue(file_path)


# CLI interface
async def main():
    """Main function to run the INBOX processor"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Becoming One™ INBOX Processor")
    parser.add_argument(
        "inbox_folder", 
        help="Path to INBOX folder on your NAS"
    )
    parser.add_argument(
        "--process-existing", 
        action="store_true",
        help="Process existing files in INBOX folder"
    )
    
    args = parser.parse_args()
    
    # Create processor
    processor = InboxProcessor(args.inbox_folder)
    
    # Process existing files if requested
    if args.process_existing:
        print("🔄 Processing existing files...")
        inbox_path = Path(args.inbox_folder)
        
        for file_path in inbox_path.glob("*"):
            if file_path.is_file() and file_path.suffix.lower() in processor.supported_extensions:
                await processor.add_file_to_queue(str(file_path))
        
        print("✅ Existing files queued for processing")
    
    # Start watching
    processor.start_watching()


if __name__ == "__main__":
    asyncio.run(main())
