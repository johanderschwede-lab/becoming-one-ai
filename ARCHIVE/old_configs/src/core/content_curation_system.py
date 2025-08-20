"""
Becoming One™ Automated Content Curation System
==============================================

This system automatically processes content from Obsidian into your knowledge base:
- Watches designated folders for new content
- Uses AI to identify speakers (Johan/Marianne vs. participants)
- Automatically categorizes and tags content
- Extracts teaching materials vs. community feedback
- Generates content suggestions for short-form videos
- Processes transcripts, documents, and media files
"""

import os
import json
import asyncio
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import re

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from openai import OpenAI

from .knowledge_management_system import BecomingOneKnowledgeSystem, ContentType, ContentSource


class ContentCategory(Enum):
    """Categories for auto-processed content"""
    JOHAN_TEACHING = "johan_teaching"
    MARIANNE_TEACHING = "marianne_teaching"
    JOINT_TEACHING = "joint_teaching"
    PARTICIPANT_QUESTION = "participant_question"
    PARTICIPANT_FEEDBACK = "participant_feedback"
    PARTICIPANT_INSIGHT = "participant_insight"
    COMMUNITY_DISCUSSION = "community_discussion"
    TECHNICAL_CONTENT = "technical_content"
    UNKNOWN = "unknown"


class ContentFormat(Enum):
    """Types of content we can process"""
    TRANSCRIPT = "transcript"
    MARKDOWN = "markdown"
    TEXT = "text"
    AUDIO_TRANSCRIPT = "audio_transcript"
    VIDEO_TRANSCRIPT = "video_transcript"
    WORKSHOP_NOTES = "workshop_notes"
    PRESENTATION_SLIDES = "presentation_slides"


@dataclass
class ContentSegment:
    """A processed segment of content"""
    segment_id: str
    content: str
    speaker: Optional[str] = None  # "johan", "marianne", "participant", "unknown"
    category: ContentCategory = ContentCategory.UNKNOWN
    timestamp: Optional[str] = None
    confidence: float = 0.0
    themes: List[str] = field(default_factory=list)
    concepts: List[str] = field(default_factory=list)
    feeling_states: List[str] = field(default_factory=list)
    anchor_types: List[str] = field(default_factory=list)
    short_form_potential: float = 0.0  # 0-1 score for video clip potential
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessedContent:
    """Complete processed content file"""
    file_path: str
    content_hash: str
    format_type: ContentFormat
    segments: List[ContentSegment]
    teaching_segments: List[ContentSegment]
    community_segments: List[ContentSegment]
    short_form_candidates: List[ContentSegment]
    processing_date: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContentCurationAgent:
    """AI agent that automatically curates and processes content"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.knowledge_system = BecomingOneKnowledgeSystem()
        
        # Speaker identification patterns
        self.speaker_patterns = {
            "johan": [
                r"\b(johan|j):\s*",
                r"\b(johan|j)\s+says?:?\s*",
                r"\bjohan\s+(niklasson)?\b",
                # Add more patterns based on your transcription style
            ],
            "marianne": [
                r"\b(marianne|m):\s*",
                r"\b(marianne|m)\s+says?:?\s*",
                r"\bmarianne\b",
                # Add more patterns
            ]
        }
        
        # Becoming One™ concept patterns
        self.concept_patterns = {
            "emotional_anchors": [
                r"emotional anchor",
                r"anchors?\s+in\s+time",
                r"stored emotional matter",
                r"anchor\s+patterns?"
            ],
            "feeling_states": [
                r"feeling[\-\s]states?",
                r"target feeling",
                r"feeling primitives?",
                r"safety|belonging|potency|significance"
            ],
            "manifestation": [
                r"manifestation?",
                r"manifesting",
                r"bridge[\-\s]of[\-\s]incidents?",
                r"end[\-\s]scene"
            ],
            "anti_bypass": [
                r"anti[\-\s]bypass",
                r"turn\s+180",
                r"spiritual bypass",
                r"no\s+bypass"
            ],
            "procrastination": [
                r"procrastination",
                r"avoidance pattern",
                r"procrastination archetype",
                r"portal"
            ]
        }
    
    async def process_content_file(self, file_path: str) -> ProcessedContent:
        """Process a single content file through the curation pipeline"""
        
        # 1. Read and analyze file
        content = self._read_file(file_path)
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        format_type = self._detect_format(file_path, content)
        
        # 2. Segment the content
        raw_segments = self._segment_content(content, format_type)
        
        # 3. Process each segment with AI
        processed_segments = []
        for segment_text in raw_segments:
            segment = await self._process_segment(segment_text, format_type)
            processed_segments.append(segment)
        
        # 4. Categorize segments
        teaching_segments = [s for s in processed_segments 
                           if s.category in [ContentCategory.JOHAN_TEACHING, 
                                           ContentCategory.MARIANNE_TEACHING, 
                                           ContentCategory.JOINT_TEACHING]]
        
        community_segments = [s for s in processed_segments 
                            if s.category in [ContentCategory.PARTICIPANT_QUESTION,
                                            ContentCategory.PARTICIPANT_FEEDBACK,
                                            ContentCategory.PARTICIPANT_INSIGHT,
                                            ContentCategory.COMMUNITY_DISCUSSION]]
        
        # 5. Identify short-form video candidates
        short_form_candidates = [s for s in processed_segments 
                               if s.short_form_potential > 0.7]
        
        return ProcessedContent(
            file_path=file_path,
            content_hash=content_hash,
            format_type=format_type,
            segments=processed_segments,
            teaching_segments=teaching_segments,
            community_segments=community_segments,
            short_form_candidates=short_form_candidates,
            metadata={"original_file": os.path.basename(file_path)}
        )
    
    async def _process_segment(self, segment_text: str, format_type: ContentFormat) -> ContentSegment:
        """Process a single segment with AI analysis"""
        
        # Generate segment ID
        segment_id = hashlib.sha256(segment_text.encode()).hexdigest()[:12]
        
        # AI analysis prompt
        analysis_prompt = f"""
        Analyze this content segment from a Becoming One™ workshop/presentation:
        
        Content: "{segment_text}"
        Format: {format_type.value}
        
        Identify:
        1. Speaker: Is this Johan, Marianne, a participant, or unknown?
        2. Category: Teaching content, question, feedback, insight, or discussion?
        3. Themes: What Becoming One™ themes are present?
        4. Concepts: Which specific concepts are discussed?
        5. Feeling states: Any feeling-states mentioned or implied?
        6. Anchor types: Any emotional anchors discussed?
        7. Short-form potential: Rate 0-1 how suitable this is for a short video clip
        8. Confidence: How confident are you in this analysis (0-1)?
        
        Return JSON:
        {{
            "speaker": "johan|marianne|participant|unknown",
            "category": "johan_teaching|marianne_teaching|joint_teaching|participant_question|participant_feedback|participant_insight|community_discussion|technical_content|unknown",
            "themes": ["theme1", "theme2"],
            "concepts": ["concept1", "concept2"],
            "feeling_states": ["safety", "belonging"],
            "anchor_types": ["abandonment", "unworthiness"],
            "short_form_potential": 0.8,
            "confidence": 0.9,
            "reasoning": "Brief explanation of the analysis"
        }}
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing Becoming One™ content and identifying speakers, themes, and teaching value."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            # Parse AI response
            analysis = json.loads(response.choices[0].message.content)
            
            # Create segment
            segment = ContentSegment(
                segment_id=segment_id,
                content=segment_text,
                speaker=analysis.get("speaker", "unknown"),
                category=ContentCategory(analysis.get("category", "unknown")),
                confidence=analysis.get("confidence", 0.0),
                themes=analysis.get("themes", []),
                concepts=analysis.get("concepts", []),
                feeling_states=analysis.get("feeling_states", []),
                anchor_types=analysis.get("anchor_types", []),
                short_form_potential=analysis.get("short_form_potential", 0.0),
                metadata={"ai_reasoning": analysis.get("reasoning", "")}
            )
            
        except Exception as e:
            # Fallback to pattern-based analysis
            segment = ContentSegment(
                segment_id=segment_id,
                content=segment_text,
                speaker=self._detect_speaker_patterns(segment_text),
                category=self._detect_category_patterns(segment_text),
                confidence=0.5,
                themes=self._extract_themes_patterns(segment_text),
                concepts=self._extract_concepts_patterns(segment_text),
                metadata={"processing_error": str(e)}
            )
        
        return segment
    
    def _read_file(self, file_path: str) -> str:
        """Read content from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return ""
    
    def _detect_format(self, file_path: str, content: str) -> ContentFormat:
        """Detect the format type of the content"""
        file_ext = Path(file_path).suffix.lower()
        filename = Path(file_path).name.lower()
        
        if "transcript" in filename:
            if "video" in filename:
                return ContentFormat.VIDEO_TRANSCRIPT
            elif "audio" in filename:
                return ContentFormat.AUDIO_TRANSCRIPT
            else:
                return ContentFormat.TRANSCRIPT
        elif file_ext == ".md":
            return ContentFormat.MARKDOWN
        elif "workshop" in filename or "notes" in filename:
            return ContentFormat.WORKSHOP_NOTES
        elif "presentation" in filename or "slides" in filename:
            return ContentFormat.PRESENTATION_SLIDES
        else:
            return ContentFormat.TEXT
    
    def _segment_content(self, content: str, format_type: ContentFormat) -> List[str]:
        """Break content into logical segments"""
        
        if format_type in [ContentFormat.TRANSCRIPT, ContentFormat.AUDIO_TRANSCRIPT, ContentFormat.VIDEO_TRANSCRIPT]:
            # Split by speaker changes or timestamps
            segments = re.split(r'\n\n+|\n(?=[A-Z][a-z]*:)|\n(?=\d+:\d+)', content)
        elif format_type == ContentFormat.MARKDOWN:
            # Split by headers or double newlines
            segments = re.split(r'\n#{1,6}\s+|\n\n+', content)
        else:
            # Split by paragraphs
            segments = re.split(r'\n\n+', content)
        
        # Clean and filter segments
        cleaned_segments = []
        for segment in segments:
            cleaned = segment.strip()
            if len(cleaned) > 50:  # Minimum length threshold
                cleaned_segments.append(cleaned)
        
        return cleaned_segments
    
    def _detect_speaker_patterns(self, text: str) -> str:
        """Use patterns to detect speaker"""
        text_lower = text.lower()
        
        for speaker, patterns in self.speaker_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return speaker
        
        return "unknown"
    
    def _detect_category_patterns(self, text: str) -> ContentCategory:
        """Use patterns to detect content category"""
        speaker = self._detect_speaker_patterns(text)
        
        if speaker == "johan":
            return ContentCategory.JOHAN_TEACHING
        elif speaker == "marianne":
            return ContentCategory.MARIANNE_TEACHING
        elif "question" in text.lower() or "?" in text:
            return ContentCategory.PARTICIPANT_QUESTION
        elif any(word in text.lower() for word in ["feedback", "comment", "think", "feel"]):
            return ContentCategory.PARTICIPANT_FEEDBACK
        else:
            return ContentCategory.UNKNOWN
    
    def _extract_themes_patterns(self, text: str) -> List[str]:
        """Extract themes using pattern matching"""
        themes = []
        text_lower = text.lower()
        
        theme_keywords = {
            "transformation": ["transform", "change", "growth", "evolution"],
            "emotional_work": ["emotion", "feeling", "anchor", "digest"],
            "manifestation": ["manifest", "create", "bridge", "end-scene"],
            "consciousness": ["conscious", "awareness", "presence", "essence"],
            "relationships": ["relationship", "partner", "connect", "relate"]
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        return themes
    
    def _extract_concepts_patterns(self, text: str) -> List[str]:
        """Extract Becoming One™ concepts using patterns"""
        concepts = []
        text_lower = text.lower()
        
        for concept, patterns in self.concept_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    concepts.append(concept)
                    break
        
        return concepts


class ContentWatcher(FileSystemEventHandler):
    """Watches Obsidian folder for new content to process"""
    
    def __init__(self, curation_agent: ContentCurationAgent, watch_folder: str):
        self.curation_agent = curation_agent
        self.watch_folder = watch_folder
        self.processing_queue = asyncio.Queue()
        
        # Start processing queue
        asyncio.create_task(self._process_queue())
    
    def on_created(self, event):
        """Handle new file creation"""
        if not event.is_directory:
            file_path = event.src_path
            if self._should_process_file(file_path):
                print(f"📁 New content detected: {file_path}")
                asyncio.create_task(self._queue_file_for_processing(file_path))
    
    def on_modified(self, event):
        """Handle file modification"""
        if not event.is_directory:
            file_path = event.src_path
            if self._should_process_file(file_path):
                print(f"📝 Content modified: {file_path}")
                asyncio.create_task(self._queue_file_for_processing(file_path))
    
    def _should_process_file(self, file_path: str) -> bool:
        """Check if file should be processed"""
        file_ext = Path(file_path).suffix.lower()
        filename = Path(file_path).name.lower()
        
        # Process these file types
        valid_extensions = ['.md', '.txt', '.docx']
        
        # Skip temporary files
        skip_patterns = ['.tmp', '~', '.DS_Store', '.git']
        
        return (
            file_ext in valid_extensions and
            not any(pattern in filename for pattern in skip_patterns)
        )
    
    async def _queue_file_for_processing(self, file_path: str):
        """Add file to processing queue"""
        await self.processing_queue.put(file_path)
    
    async def _process_queue(self):
        """Process files from the queue"""
        while True:
            try:
                file_path = await self.processing_queue.get()
                await self._process_file(file_path)
                self.processing_queue.task_done()
            except Exception as e:
                print(f"❌ Error processing queue: {e}")
                await asyncio.sleep(1)
    
    async def _process_file(self, file_path: str):
        """Process a single file"""
        try:
            print(f"🔄 Processing: {file_path}")
            
            # Process content
            processed_content = await self.curation_agent.process_content_file(file_path)
            
            # Upload teaching segments to knowledge base
            await self._upload_teaching_content(processed_content)
            
            # Store community content separately
            await self._store_community_content(processed_content)
            
            # Generate short-form content suggestions
            await self._generate_content_suggestions(processed_content)
            
            print(f"✅ Processed: {os.path.basename(file_path)}")
            print(f"   📚 Teaching segments: {len(processed_content.teaching_segments)}")
            print(f"   👥 Community segments: {len(processed_content.community_segments)}")
            print(f"   🎬 Short-form candidates: {len(processed_content.short_form_candidates)}")
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    async def _upload_teaching_content(self, processed_content: ProcessedContent):
        """Upload teaching segments to the knowledge base"""
        for segment in processed_content.teaching_segments:
            try:
                # Determine content type and source
                if segment.speaker == "johan":
                    source = ContentSource.JOHAN_ORIGINAL
                elif segment.speaker == "marianne":
                    source = ContentSource.MARIANNE_ORIGINAL
                else:
                    source = ContentSource.WORKSHOP_RECORDING
                
                # Upload to knowledge system
                await self.curation_agent.knowledge_system.upload_teaching_material(
                    title=f"Teaching Segment - {segment.segment_id}",
                    content=segment.content,
                    material_type="method_description",
                    source_type=source.value,
                    metadata={
                        "speaker": segment.speaker,
                        "themes": segment.themes,
                        "concepts": segment.concepts,
                        "feeling_states": segment.feeling_states,
                        "anchor_types": segment.anchor_types,
                        "confidence": segment.confidence,
                        "original_file": processed_content.file_path,
                        "auto_processed": True
                    }
                )
                
            except Exception as e:
                print(f"❌ Error uploading teaching segment: {e}")
    
    async def _store_community_content(self, processed_content: ProcessedContent):
        """Store community content in separate area"""
        # This could go to a separate table or be marked differently
        for segment in processed_content.community_segments:
            try:
                await self.curation_agent.knowledge_system.add_community_content(
                    content=segment.content,
                    category=segment.category.value,
                    themes=segment.themes,
                    metadata={
                        "original_file": processed_content.file_path,
                        "confidence": segment.confidence,
                        "auto_processed": True
                    }
                )
            except Exception as e:
                print(f"❌ Error storing community content: {e}")
    
    async def _generate_content_suggestions(self, processed_content: ProcessedContent):
        """Generate suggestions for short-form content"""
        if not processed_content.short_form_candidates:
            return
        
        suggestions = []
        for candidate in processed_content.short_form_candidates:
            suggestion = await self._create_content_suggestion(candidate)
            suggestions.append(suggestion)
        
        # Store suggestions
        await self._store_content_suggestions(processed_content.file_path, suggestions)
    
    async def _create_content_suggestion(self, segment: ContentSegment) -> Dict[str, Any]:
        """Create a content suggestion from a segment"""
        
        prompt = f"""
        Create a short-form video content suggestion based on this Becoming One™ teaching segment:
        
        Content: "{segment.content}"
        Speaker: {segment.speaker}
        Themes: {', '.join(segment.themes)}
        Concepts: {', '.join(segment.concepts)}
        
        Generate:
        1. Hook (first 3 seconds)
        2. Main teaching point (15-30 seconds)
        3. Call to action
        4. Suggested title
        5. Hashtags
        6. Platform recommendations (TikTok, YouTube Shorts, Instagram Reels)
        
        Return JSON format.
        """
        
        try:
            response = await self.curation_agent.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": "You are an expert at creating engaging short-form video content for spiritual and personal development topics."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )
            
            suggestion = json.loads(response.choices[0].message.content)
            suggestion["source_segment_id"] = segment.segment_id
            suggestion["potential_score"] = segment.short_form_potential
            
            return suggestion
            
        except Exception as e:
            return {
                "error": str(e),
                "source_segment_id": segment.segment_id,
                "fallback_title": f"Becoming One™ Insight: {segment.content[:50]}..."
            }
    
    async def _store_content_suggestions(self, source_file: str, suggestions: List[Dict[str, Any]]):
        """Store content suggestions for review"""
        # Create suggestions file
        suggestions_file = f"content_suggestions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        suggestions_path = os.path.join(os.path.dirname(source_file), "suggestions", suggestions_file)
        
        # Ensure suggestions directory exists
        os.makedirs(os.path.dirname(suggestions_path), exist_ok=True)
        
        # Store suggestions
        with open(suggestions_path, 'w', encoding='utf-8') as f:
            json.dump({
                "source_file": source_file,
                "generated_at": datetime.now().isoformat(),
                "suggestions": suggestions
            }, f, indent=2)
        
        print(f"💡 Content suggestions saved: {suggestions_path}")


class ContentCurationSystem:
    """Main system that orchestrates content curation"""
    
    def __init__(self, obsidian_watch_folder: str):
        self.obsidian_watch_folder = obsidian_watch_folder
        self.curation_agent = ContentCurationAgent()
        self.observer = Observer()
        
        # Setup folder structure
        self._setup_folders()
    
    def _setup_folders(self):
        """Setup required folder structure"""
        folders = [
            self.obsidian_watch_folder,
            os.path.join(self.obsidian_watch_folder, "processed"),
            os.path.join(self.obsidian_watch_folder, "suggestions"),
            os.path.join(self.obsidian_watch_folder, "community"),
            os.path.join(self.obsidian_watch_folder, "teaching")
        ]
        
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
    
    def start_watching(self):
        """Start watching the Obsidian folder"""
        event_handler = ContentWatcher(self.curation_agent, self.obsidian_watch_folder)
        
        self.observer.schedule(
            event_handler,
            self.obsidian_watch_folder,
            recursive=True
        )
        
        self.observer.start()
        print(f"👁️  Started watching: {self.obsidian_watch_folder}")
        print("🤖 Content curation agent is active!")
        print("📁 Drop files in the folder to auto-process them")
        
        try:
            while True:
                asyncio.sleep(1)
        except KeyboardInterrupt:
            self.stop_watching()
    
    def stop_watching(self):
        """Stop watching"""
        self.observer.stop()
        self.observer.join()
        print("🛑 Content curation system stopped")
    
    async def process_existing_files(self):
        """Process all existing files in the watch folder"""
        print("🔄 Processing existing files...")
        
        for root, dirs, files in os.walk(self.obsidian_watch_folder):
            for file in files:
                file_path = os.path.join(root, file)
                if ContentWatcher(self.curation_agent, "")._should_process_file(file_path):
                    await self.curation_agent.process_content_file(file_path)
        
        print("✅ Existing files processed")


# Extension to knowledge management system
async def upload_teaching_material(
    self,
    title: str,
    content: str,
    material_type: str,
    source_type: str,
    metadata: Dict[str, Any]
) -> str:
    """Upload teaching material to knowledge base"""
    material_id = str(uuid.uuid4())
    
    # Store in Supabase
    material_record = {
        "material_id": material_id,
        "title": title,
        "content": content,
        "material_type": material_type,
        "source_type": source_type,
        "metadata": metadata,
        "content_hash": hashlib.sha256(content.encode()).hexdigest(),
        "upload_date": datetime.now().isoformat(),
        "status": "active"
    }
    
    await self._store_in_supabase("teaching_materials", material_record)
    
    # Process into chunks and store in Pinecone
    chunks = await self._process_content_into_chunks(
        content=content,
        content_type=ContentType.TEACHING_MATERIAL,
        source=ContentSource(source_type),
        parent_id=material_id,
        metadata=metadata
    )
    
    await self._store_chunks_in_pinecone(chunks)
    
    return material_id


async def add_community_content(
    self,
    content: str,
    category: str,
    themes: List[str],
    metadata: Dict[str, Any]
) -> str:
    """Add community content (questions, feedback, insights)"""
    content_id = str(uuid.uuid4())
    
    # Store community content
    community_record = {
        "content_id": content_id,
        "content": content,
        "category": category,
        "themes": themes,
        "metadata": metadata,
        "created_date": datetime.now().isoformat()
    }
    
    # This could go to a separate community table
    await self._store_in_supabase("community_content", community_record)
    
    return content_id


# Add these methods to BecomingOneKnowledgeSystem class
BecomingOneKnowledgeSystem.upload_teaching_material = upload_teaching_material
BecomingOneKnowledgeSystem.add_community_content = add_community_content
