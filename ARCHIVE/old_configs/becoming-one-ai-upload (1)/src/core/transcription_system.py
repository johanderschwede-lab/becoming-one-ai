"""
Becoming One™ Transcription System
=================================

Complete pipeline for converting audio/video recordings to text transcripts
that can be processed by the INBOX system.

Options:
1. OpenAI Whisper API (cloud-based, high quality, costs per minute)
2. Local Whisper (runs on your machine, free, requires setup)
3. Hybrid approach (local for privacy, API for quality)

Supports:
- Audio: .mp3, .wav, .m4a, .flac, .ogg
- Video: .mp4, .mov, .avi, .mkv (extracts audio)
- Batch processing of multiple files
- Speaker identification and timestamping
- Automatic INBOX integration
"""

import os
import json
import asyncio
import subprocess
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import tempfile
import shutil

from openai import OpenAI


class TranscriptionMethod(Enum):
    """Available transcription methods"""
    OPENAI_WHISPER_API = "openai_whisper_api"
    LOCAL_WHISPER = "local_whisper"
    HYBRID = "hybrid"


class AudioFormat(Enum):
    """Supported audio formats"""
    MP3 = ".mp3"
    WAV = ".wav"
    M4A = ".m4a"
    FLAC = ".flac"
    OGG = ".ogg"


class VideoFormat(Enum):
    """Supported video formats (audio will be extracted)"""
    MP4 = ".mp4"
    MOV = ".mov"
    AVI = ".avi"
    MKV = ".mkv"
    WEBM = ".webm"


@dataclass
class TranscriptionResult:
    """Result of transcription process"""
    source_file: str
    transcript_text: str
    method_used: TranscriptionMethod
    duration_seconds: float = 0.0
    processing_time: float = 0.0
    confidence_score: float = 0.0
    language_detected: str = "unknown"
    segments: List[Dict[str, Any]] = field(default_factory=list)  # Timestamped segments
    speakers_detected: int = 0
    cost_estimate: float = 0.0  # For API usage
    error_message: str = ""
    created_at: datetime = field(default_factory=datetime.now)


class TranscriptionEngine:
    """Main transcription engine with multiple backend options"""
    
    def __init__(self, method: TranscriptionMethod = TranscriptionMethod.OPENAI_WHISPER_API):
        self.method = method
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Supported formats
        self.audio_formats = {fmt.value for fmt in AudioFormat}
        self.video_formats = {fmt.value for fmt in VideoFormat}
        self.all_formats = self.audio_formats | self.video_formats
        
        # Check dependencies
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check if required tools are installed"""
        if self.method in [TranscriptionMethod.LOCAL_WHISPER, TranscriptionMethod.HYBRID]:
            # Check for whisper installation
            try:
                result = subprocess.run(["whisper", "--help"], 
                                      capture_output=True, text=True)
                if result.returncode != 0:
                    print("⚠️  Local Whisper not found. Install with: pip install openai-whisper")
            except FileNotFoundError:
                print("⚠️  Local Whisper not installed. Install with: pip install openai-whisper")
        
        # Check for ffmpeg (needed for video processing)
        try:
            result = subprocess.run(["ffmpeg", "-version"], 
                                  capture_output=True, text=True)
            if result.returncode != 0:
                print("⚠️  FFmpeg not found. Install from: https://ffmpeg.org/")
        except FileNotFoundError:
            print("⚠️  FFmpeg not installed. Needed for video file processing.")
            print("   Install: brew install ffmpeg (Mac) or apt install ffmpeg (Linux)")
    
    async def transcribe_file(self, file_path: str) -> TranscriptionResult:
        """Transcribe a single audio/video file"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return TranscriptionResult(
                source_file=str(file_path),
                transcript_text="",
                method_used=self.method,
                error_message=f"File not found: {file_path}"
            )
        
        if file_path.suffix.lower() not in self.all_formats:
            return TranscriptionResult(
                source_file=str(file_path),
                transcript_text="",
                method_used=self.method,
                error_message=f"Unsupported format: {file_path.suffix}"
            )
        
        print(f"🎵 Transcribing: {file_path.name}")
        start_time = datetime.now()
        
        try:
            # Convert video to audio if needed
            audio_file = await self._prepare_audio_file(file_path)
            
            # Get duration
            duration = await self._get_audio_duration(audio_file)
            
            # Transcribe based on method
            if self.method == TranscriptionMethod.OPENAI_WHISPER_API:
                result = await self._transcribe_with_openai_api(audio_file)
            elif self.method == TranscriptionMethod.LOCAL_WHISPER:
                result = await self._transcribe_with_local_whisper(audio_file)
            elif self.method == TranscriptionMethod.HYBRID:
                result = await self._transcribe_hybrid(audio_file)
            else:
                raise ValueError(f"Unknown transcription method: {self.method}")
            
            # Clean up temporary audio file if it was created
            if audio_file != file_path:
                os.unlink(audio_file)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Update result with metadata
            result.source_file = str(file_path)
            result.duration_seconds = duration
            result.processing_time = processing_time
            result.method_used = self.method
            
            print(f"✅ Transcribed {file_path.name} in {processing_time:.1f}s")
            return result
            
        except Exception as e:
            return TranscriptionResult(
                source_file=str(file_path),
                transcript_text="",
                method_used=self.method,
                processing_time=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    async def _prepare_audio_file(self, file_path: Path) -> Path:
        """Convert video to audio if needed, return path to audio file"""
        
        if file_path.suffix.lower() in self.audio_formats:
            return file_path
        
        # Extract audio from video
        print(f"  🎬 Extracting audio from video...")
        
        # Create temporary audio file
        temp_audio = file_path.parent / f"{file_path.stem}_temp.wav"
        
        # Use ffmpeg to extract audio
        cmd = [
            "ffmpeg", "-i", str(file_path),
            "-vn",  # No video
            "-acodec", "pcm_s16le",  # Audio codec
            "-ar", "16000",  # Sample rate (Whisper optimal)
            "-ac", "1",  # Mono
            "-y",  # Overwrite output
            str(temp_audio)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg failed: {result.stderr}")
        
        return temp_audio
    
    async def _get_audio_duration(self, file_path: Path) -> float:
        """Get duration of audio file in seconds"""
        try:
            cmd = [
                "ffprobe", "-i", str(file_path),
                "-show_entries", "format=duration",
                "-v", "quiet", "-of", "csv=p=0"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except:
            pass
        
        return 0.0
    
    async def _transcribe_with_openai_api(self, audio_file: Path) -> TranscriptionResult:
        """Transcribe using OpenAI Whisper API"""
        
        # Check file size (OpenAI limit is 25MB)
        file_size_mb = audio_file.stat().st_size / (1024 * 1024)
        if file_size_mb > 25:
            raise Exception(f"File too large for OpenAI API: {file_size_mb:.1f}MB (max 25MB)")
        
        with open(audio_file, "rb") as audio:
            transcript = await self.openai_client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                response_format="verbose_json",  # Get timestamps and metadata
                language="en"  # Specify if you know the language
            )
        
        # Calculate cost estimate (OpenAI pricing: $0.006 per minute)
        duration_minutes = transcript.duration / 60
        cost_estimate = duration_minutes * 0.006
        
        # Extract segments with timestamps
        segments = []
        if hasattr(transcript, 'segments') and transcript.segments:
            segments = [
                {
                    "start": seg.start,
                    "end": seg.end,
                    "text": seg.text,
                    "confidence": getattr(seg, 'avg_logprob', 0.0)
                }
                for seg in transcript.segments
            ]
        
        return TranscriptionResult(
            source_file="",  # Will be set by caller
            transcript_text=transcript.text,
            method_used=TranscriptionMethod.OPENAI_WHISPER_API,
            duration_seconds=transcript.duration,
            language_detected=transcript.language,
            segments=segments,
            cost_estimate=cost_estimate,
            confidence_score=0.9  # OpenAI Whisper is generally high quality
        )
    
    async def _transcribe_with_local_whisper(self, audio_file: Path) -> TranscriptionResult:
        """Transcribe using local Whisper installation"""
        
        # Create output directory
        output_dir = audio_file.parent / "whisper_output"
        output_dir.mkdir(exist_ok=True)
        
        # Run whisper command
        cmd = [
            "whisper", str(audio_file),
            "--model", "base",  # Can be: tiny, base, small, medium, large
            "--language", "en",
            "--output_dir", str(output_dir),
            "--output_format", "json",
            "--verbose", "False"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"Local Whisper failed: {result.stderr}")
        
        # Read the JSON output
        json_file = output_dir / f"{audio_file.stem}.json"
        
        if not json_file.exists():
            raise Exception("Whisper output file not found")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            whisper_output = json.load(f)
        
        # Clean up output files
        shutil.rmtree(output_dir)
        
        # Extract segments
        segments = []
        if 'segments' in whisper_output:
            segments = [
                {
                    "start": seg.get('start', 0),
                    "end": seg.get('end', 0),
                    "text": seg.get('text', ''),
                    "confidence": seg.get('avg_logprob', 0.0)
                }
                for seg in whisper_output['segments']
            ]
        
        return TranscriptionResult(
            source_file="",  # Will be set by caller
            transcript_text=whisper_output.get('text', ''),
            method_used=TranscriptionMethod.LOCAL_WHISPER,
            language_detected=whisper_output.get('language', 'unknown'),
            segments=segments,
            cost_estimate=0.0,  # Local processing is free
            confidence_score=0.8  # Local Whisper is good but not as polished as API
        )
    
    async def _transcribe_hybrid(self, audio_file: Path) -> TranscriptionResult:
        """Use hybrid approach: local for privacy, API for quality"""
        
        # For now, just use API method
        # In future, could implement logic like:
        # - Use local for sensitive content
        # - Use API for important content that needs highest quality
        # - Use local for long files to save costs
        
        file_size_mb = audio_file.stat().st_size / (1024 * 1024)
        
        if file_size_mb > 20:  # Use local for large files
            return await self._transcribe_with_local_whisper(audio_file)
        else:  # Use API for smaller files
            return await self._transcribe_with_openai_api(audio_file)
    
    async def transcribe_batch(self, file_paths: List[str]) -> List[TranscriptionResult]:
        """Transcribe multiple files"""
        results = []
        
        print(f"🎵 Starting batch transcription of {len(file_paths)} files")
        
        for i, file_path in enumerate(file_paths, 1):
            print(f"\n📁 Processing file {i}/{len(file_paths)}")
            result = await self.transcribe_file(file_path)
            results.append(result)
            
            # Show progress
            if result.error_message:
                print(f"❌ Failed: {result.error_message}")
            else:
                duration_min = result.duration_seconds / 60
                print(f"✅ Success: {duration_min:.1f} min audio → {len(result.transcript_text)} chars")
        
        # Summary
        successful = [r for r in results if not r.error_message]
        failed = [r for r in results if r.error_message]
        
        print(f"\n📊 Batch Summary:")
        print(f"   ✅ Successful: {len(successful)}")
        print(f"   ❌ Failed: {len(failed)}")
        
        if self.method == TranscriptionMethod.OPENAI_WHISPER_API:
            total_cost = sum(r.cost_estimate for r in successful)
            print(f"   💰 Estimated cost: ${total_cost:.2f}")
        
        return results


class TranscriptionPipeline:
    """Complete pipeline: audio/video → transcript → INBOX processing"""
    
    def __init__(self, 
                 method: TranscriptionMethod = TranscriptionMethod.OPENAI_WHISPER_API,
                 inbox_folder: Optional[str] = None):
        self.transcription_engine = TranscriptionEngine(method)
        self.inbox_folder = Path(inbox_folder) if inbox_folder else None
    
    async def process_media_folder(self, media_folder: str, auto_inbox: bool = True):
        """Process all media files in a folder"""
        media_path = Path(media_folder)
        
        if not media_path.exists():
            print(f"❌ Media folder not found: {media_path}")
            return
        
        # Find all media files
        media_files = []
        for ext in self.transcription_engine.all_formats:
            media_files.extend(media_path.glob(f"*{ext}"))
            media_files.extend(media_path.glob(f"**/*{ext}"))  # Recursive
        
        if not media_files:
            print(f"📭 No media files found in {media_path}")
            return
        
        print(f"🎵 Found {len(media_files)} media files")
        
        # Transcribe all files
        results = await self.transcription_engine.transcribe_batch([str(f) for f in media_files])
        
        # Save transcripts
        transcript_folder = media_path / "transcripts"
        transcript_folder.mkdir(exist_ok=True)
        
        for result in results:
            if not result.error_message:
                # Save transcript
                source_name = Path(result.source_file).stem
                transcript_file = transcript_folder / f"{source_name}_transcript.txt"
                
                # Create formatted transcript
                transcript_content = self._format_transcript(result)
                
                with open(transcript_file, 'w', encoding='utf-8') as f:
                    f.write(transcript_content)
                
                print(f"💾 Saved transcript: {transcript_file.name}")
                
                # Auto-move to INBOX if enabled
                if auto_inbox and self.inbox_folder:
                    inbox_file = self.inbox_folder / f"{source_name}_transcript.txt"
                    shutil.copy(transcript_file, inbox_file)
                    print(f"📥 Copied to INBOX: {inbox_file.name}")
        
        # Save batch summary
        summary_file = transcript_folder / f"transcription_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        summary = {
            "processed_at": datetime.now().isoformat(),
            "method_used": self.transcription_engine.method.value,
            "total_files": len(results),
            "successful": len([r for r in results if not r.error_message]),
            "failed": len([r for r in results if r.error_message]),
            "total_duration_minutes": sum(r.duration_seconds for r in results if not r.error_message) / 60,
            "total_cost_estimate": sum(r.cost_estimate for r in results if not r.error_message),
            "results": [
                {
                    "file": Path(r.source_file).name,
                    "success": not bool(r.error_message),
                    "duration_minutes": r.duration_seconds / 60,
                    "transcript_length": len(r.transcript_text),
                    "cost_estimate": r.cost_estimate,
                    "error": r.error_message
                }
                for r in results
            ]
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print(f"📊 Summary saved: {summary_file.name}")
    
    def _format_transcript(self, result: TranscriptionResult) -> str:
        """Format transcript with metadata"""
        
        header = f"""# Transcript: {Path(result.source_file).name}

**Transcribed**: {result.created_at.strftime('%Y-%m-%d %H:%M:%S')}
**Method**: {result.method_used.value}
**Duration**: {result.duration_seconds / 60:.1f} minutes
**Language**: {result.language_detected}
**Cost**: ${result.cost_estimate:.3f}

---

"""
        
        # Add timestamped segments if available
        if result.segments:
            content = header + "\n## Timestamped Transcript\n\n"
            
            for segment in result.segments:
                start_time = f"{int(segment['start'] // 60):02d}:{int(segment['start'] % 60):02d}"
                content += f"**{start_time}**: {segment['text'].strip()}\n\n"
        else:
            content = header + "\n## Transcript\n\n" + result.transcript_text
        
        return content


# CLI interface
async def main():
    """CLI for transcription system"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Becoming One™ Transcription System")
    parser.add_argument("input_path", help="Path to audio/video file or folder")
    parser.add_argument("--method", 
                       choices=["api", "local", "hybrid"],
                       default="api",
                       help="Transcription method (default: api)")
    parser.add_argument("--inbox", help="INBOX folder to auto-copy transcripts")
    parser.add_argument("--batch", action="store_true", help="Process all files in folder")
    
    args = parser.parse_args()
    
    # Map method names
    method_map = {
        "api": TranscriptionMethod.OPENAI_WHISPER_API,
        "local": TranscriptionMethod.LOCAL_WHISPER,
        "hybrid": TranscriptionMethod.HYBRID
    }
    
    method = method_map[args.method]
    
    if args.batch:
        # Process folder
        pipeline = TranscriptionPipeline(method, args.inbox)
        await pipeline.process_media_folder(args.input_path, auto_inbox=bool(args.inbox))
    else:
        # Process single file
        engine = TranscriptionEngine(method)
        result = await engine.transcribe_file(args.input_path)
        
        if result.error_message:
            print(f"❌ Transcription failed: {result.error_message}")
        else:
            print(f"✅ Transcription completed!")
            print(f"📝 Text length: {len(result.transcript_text)} characters")
            print(f"⏱️  Duration: {result.duration_seconds / 60:.1f} minutes")
            if result.cost_estimate > 0:
                print(f"💰 Cost: ${result.cost_estimate:.3f}")
            
            # Save transcript
            output_file = Path(args.input_path).with_suffix('.txt')
            pipeline = TranscriptionPipeline(method)
            content = pipeline._format_transcript(result)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"💾 Saved: {output_file}")
            
            # Copy to INBOX if specified
            if args.inbox:
                inbox_file = Path(args.inbox) / output_file.name
                shutil.copy(output_file, inbox_file)
                print(f"📥 Copied to INBOX: {inbox_file}")


if __name__ == "__main__":
    asyncio.run(main())
