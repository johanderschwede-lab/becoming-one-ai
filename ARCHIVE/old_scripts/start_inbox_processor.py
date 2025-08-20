#!/usr/bin/env python3
"""
Start Becoming One™ INBOX Processor
==================================

Simple script to start the automated content processing system.
Point it at your NAS INBOX folder and it will automatically process
everything you and Marianne drop there.

Usage:
    python start_inbox_processor.py /path/to/nas/inbox
    python start_inbox_processor.py /path/to/nas/inbox --process-existing
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

from src.core.inbox_processor import InboxProcessor


def validate_environment():
    """Check that required environment variables are set"""
    required_vars = [
        "OPENAI_API_KEY",
        "SUPABASE_URL", 
        "SUPABASE_ANON_KEY",
        "PINECONE_API_KEY",
        "PINECONE_ENVIRONMENT",
        "PINECONE_INDEX_NAME"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Make sure your config/live.env file contains all required API keys")
        return False
    
    return True


async def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Becoming One™ INBOX Processor - Automated Content Curation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python start_inbox_processor.py /Volumes/NAS/BecomingOne/INBOX
    python start_inbox_processor.py ~/Documents/INBOX --process-existing
    
The processor will:
    1. Watch the INBOX folder for new files
    2. Automatically identify Johan vs Marianne vs participants
    3. Extract teaching content → Knowledge base
    4. Store community content separately  
    5. Generate social media content suggestions
    6. Organize files into completed/failed folders
        """
    )
    
    parser.add_argument(
        "inbox_folder",
        help="Path to INBOX folder (can be on NAS, local drive, etc.)"
    )
    parser.add_argument(
        "--process-existing",
        action="store_true", 
        help="Process existing files in INBOX folder before starting to watch"
    )
    parser.add_argument(
        "--test-mode",
        action="store_true",
        help="Run in test mode (don't actually upload to knowledge base)"
    )
    
    args = parser.parse_args()
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    # Validate inbox folder
    inbox_path = Path(args.inbox_folder)
    if not inbox_path.exists():
        print(f"❌ INBOX folder does not exist: {inbox_path}")
        print("💡 Create the folder first or check the path")
        sys.exit(1)
    
    if not inbox_path.is_dir():
        print(f"❌ INBOX path is not a directory: {inbox_path}")
        sys.exit(1)
    
    # Create processor
    print("🚀 Starting Becoming One™ INBOX Processor")
    print(f"📁 INBOX: {inbox_path.absolute()}")
    print(f"🔧 Test mode: {'ON' if args.test_mode else 'OFF'}")
    print()
    
    try:
        processor = InboxProcessor(str(inbox_path))
        
        # Process existing files if requested
        if args.process_existing:
            print("🔄 Processing existing files...")
            
            existing_files = list(inbox_path.glob("*"))
            processable_files = [
                f for f in existing_files 
                if f.is_file() and f.suffix.lower() in processor.supported_extensions
            ]
            
            if processable_files:
                print(f"📋 Found {len(processable_files)} files to process:")
                for f in processable_files:
                    print(f"   - {f.name}")
                print()
                
                for file_path in processable_files:
                    await processor.add_file_to_queue(str(file_path))
                
                print("✅ Existing files queued for processing")
            else:
                print("📭 No existing files to process")
            print()
        
        # Start watching
        print("👁️  Starting file watcher...")
        processor.start_watching()
        
    except KeyboardInterrupt:
        print("\n🛑 INBOX processor stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting processor: {e}")
        sys.exit(1)


def show_usage_examples():
    """Show usage examples"""
    print("""
🎯 USAGE EXAMPLES:

1. Basic usage (watch folder):
   python start_inbox_processor.py /Volumes/NAS/BecomingOne/INBOX

2. Process existing files first, then watch:
   python start_inbox_processor.py ~/Documents/INBOX --process-existing

3. Test mode (analyze but don't upload):
   python start_inbox_processor.py ./test_inbox --test-mode

📁 SUPPORTED FILE TYPES:
   • Text: .txt, .md, .docx
   • Audio: .mp3, .wav, .m4a  
   • Video: .mp4, .mov, .avi
   • Data: .json

🤖 WHAT HAPPENS AUTOMATICALLY:
   • AI identifies Johan vs Marianne vs participants
   • Teaching content → Knowledge base (Pinecone + Supabase)
   • Community content → Separate storage
   • Content suggestions → Generated for social media
   • Files → Moved to organized folders (completed/failed)

💡 FOLDER STRUCTURE CREATED:
   INBOX/
   ├── [new files here] ← Drop files here
   ├── processing/      ← Files being processed  
   ├── completed/       ← Successfully processed
   ├── failed/          ← Processing failed
   ├── teaching_materials/
   ├── community_content/
   ├── content_suggestions/
   └── logs/            ← Processing logs
    """)


if __name__ == "__main__":
    # Show help if no arguments
    if len(sys.argv) == 1:
        show_usage_examples()
        sys.exit(0)
    
    # Run main function
    asyncio.run(main())
