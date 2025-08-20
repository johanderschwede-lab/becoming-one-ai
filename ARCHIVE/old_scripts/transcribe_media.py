#!/usr/bin/env python3
"""
Becoming One™ Media Transcription Tool
====================================

Simple tool to transcribe audio/video recordings and send them to your INBOX.

Usage:
    python transcribe_media.py recording.mp4                    # Single file
    python transcribe_media.py /path/to/recordings --batch      # Whole folder
    python transcribe_media.py recording.mp3 --inbox /path/to/inbox  # Auto-send to INBOX
    python transcribe_media.py recordings/ --batch --method local   # Use local Whisper
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/live.env')

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.transcription_system import TranscriptionEngine, TranscriptionPipeline, TranscriptionMethod


def show_transcription_options():
    """Show available transcription methods and their pros/cons"""
    print("""
🎵 TRANSCRIPTION OPTIONS:

1. OpenAI Whisper API (default - recommended)
   ✅ Highest quality transcription
   ✅ Handles multiple languages
   ✅ Fast processing
   ✅ No local setup needed
   ❌ Costs ~$0.006 per minute
   ❌ Requires internet connection
   ❌ Files sent to OpenAI (privacy consideration)

2. Local Whisper (free but requires setup)
   ✅ Completely free
   ✅ Works offline
   ✅ Full privacy (nothing sent to cloud)
   ❌ Requires installation: pip install openai-whisper
   ❌ Slower processing
   ❌ Uses your computer's resources

3. Hybrid (smart choice based on file)
   ✅ Best of both worlds
   ✅ Local for large/private files
   ✅ API for small/important files
   ❌ Requires both setups

📁 SUPPORTED FORMATS:
   Audio: .mp3, .wav, .m4a, .flac, .ogg
   Video: .mp4, .mov, .avi, .mkv, .webm (audio extracted)

💡 RECOMMENDATIONS:
   - Start with API method (easiest, highest quality)
   - Use local if you process lots of content (cost savings)
   - Use hybrid for mixed workload
    """)


def estimate_costs(file_paths, method):
    """Estimate transcription costs"""
    if method != "api":
        return "Free (local processing)"
    
    try:
        import subprocess
        total_duration = 0
        
        for file_path in file_paths:
            # Get duration using ffprobe
            cmd = [
                "ffprobe", "-i", file_path,
                "-show_entries", "format=duration",
                "-v", "quiet", "-of", "csv=p=0"
            ]
            
            try:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    duration = float(result.stdout.strip())
                    total_duration += duration
            except:
                continue
        
        total_minutes = total_duration / 60
        estimated_cost = total_minutes * 0.006
        
        return f"~${estimated_cost:.2f} ({total_minutes:.1f} minutes)"
    
    except:
        return "Unable to estimate (install ffmpeg for duration detection)"


async def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Transcribe audio/video files for Becoming One™ content processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python transcribe_media.py workshop_recording.mp4
    python transcribe_media.py recordings/ --batch
    python transcribe_media.py interview.mp3 --inbox /path/to/inbox
    python transcribe_media.py recordings/ --batch --method local
    python transcribe_media.py --show-options
        """
    )
    
    parser.add_argument("input_path", nargs="?", help="Audio/video file or folder path")
    parser.add_argument("--method", 
                       choices=["api", "local", "hybrid"],
                       default="api",
                       help="Transcription method (default: api)")
    parser.add_argument("--batch", action="store_true", help="Process all files in folder")
    parser.add_argument("--inbox", help="INBOX folder to auto-copy transcripts")
    parser.add_argument("--show-options", action="store_true", help="Show transcription options and exit")
    parser.add_argument("--estimate-cost", action="store_true", help="Estimate cost without processing")
    
    args = parser.parse_args()
    
    # Show options if requested
    if args.show_options:
        show_transcription_options()
        return
    
    # Validate input
    if not args.input_path:
        parser.print_help()
        return
    
    input_path = Path(args.input_path)
    if not input_path.exists():
        print(f"❌ Path not found: {input_path}")
        return
    
    # Check environment for API method
    if args.method == "api" and not os.getenv("OPENAI_API_KEY"):
        print("❌ OpenAI API key not found in environment")
        print("💡 Set OPENAI_API_KEY in your config/live.env file")
        print("   Or use --method local for offline processing")
        return
    
    # Map method names
    method_map = {
        "api": TranscriptionMethod.OPENAI_WHISPER_API,
        "local": TranscriptionMethod.LOCAL_WHISPER,
        "hybrid": TranscriptionMethod.HYBRID
    }
    
    method = method_map[args.method]
    
    # Estimate costs if requested
    if args.estimate_cost:
        if args.batch and input_path.is_dir():
            # Find all media files
            engine = TranscriptionEngine(method)
            media_files = []
            for ext in engine.all_formats:
                media_files.extend(input_path.glob(f"*{ext}"))
            file_paths = [str(f) for f in media_files]
        else:
            file_paths = [str(input_path)]
        
        cost_estimate = estimate_costs(file_paths, args.method)
        print(f"💰 Estimated cost: {cost_estimate}")
        print(f"📁 Files to process: {len(file_paths)}")
        return
    
    # Process files
    print(f"🚀 Starting transcription with {args.method} method")
    print(f"📁 Input: {input_path}")
    if args.inbox:
        print(f"📥 INBOX: {args.inbox}")
    print()
    
    try:
        if args.batch:
            # Process folder
            pipeline = TranscriptionPipeline(method, args.inbox)
            await pipeline.process_media_folder(str(input_path), auto_inbox=bool(args.inbox))
        else:
            # Process single file
            engine = TranscriptionEngine(method)
            result = await engine.transcribe_file(str(input_path))
            
            if result.error_message:
                print(f"❌ Transcription failed: {result.error_message}")
                return
            
            print(f"✅ Transcription completed!")
            print(f"📝 Text length: {len(result.transcript_text)} characters")
            print(f"⏱️  Duration: {result.duration_seconds / 60:.1f} minutes")
            if result.cost_estimate > 0:
                print(f"💰 Cost: ${result.cost_estimate:.3f}")
            
            # Save transcript
            output_file = input_path.with_suffix('.txt')
            pipeline = TranscriptionPipeline(method)
            content = pipeline._format_transcript(result)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"💾 Saved: {output_file.name}")
            
            # Copy to INBOX if specified
            if args.inbox:
                inbox_path = Path(args.inbox)
                inbox_file = inbox_path / output_file.name
                
                # Ensure INBOX exists
                inbox_path.mkdir(parents=True, exist_ok=True)
                
                import shutil
                shutil.copy(output_file, inbox_file)
                print(f"📥 Copied to INBOX: {inbox_file.name}")
                print("🤖 INBOX processor will automatically handle this file!")
    
    except KeyboardInterrupt:
        print("\n🛑 Transcription cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Show help if no arguments
    if len(sys.argv) == 1:
        show_transcription_options()
        print("\nUse --help for detailed usage information")
    else:
        asyncio.run(main())
