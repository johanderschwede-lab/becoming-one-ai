#!/usr/bin/env python3
"""
Start Complete Local System for Immediate Use
============================================

Starts the complete Becoming One™ system locally for immediate content processing
and testing, while we prepare for cloud deployment tomorrow.

Usage:
    python start_local_system.py
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/live.env')

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.inbox_processor import InboxProcessor
from src.core.expandable_personality_framework import ExpandablePersonalityFramework

class LocalBecomingOneSystem:
    """Complete local system for immediate use"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.local_inbox = self.project_root / "LOCAL_INBOX"
        
        # Initialize components
        self.inbox_processor = InboxProcessor(str(self.local_inbox / "inbox"))
        self.personality_framework = ExpandablePersonalityFramework(
            str(self.project_root / "personality_data")
        )
        
        print(f"🏠 Local Becoming One™ System Initialized")
        print(f"📁 INBOX: {self.local_inbox / 'inbox'}")
        print(f"🧠 Personality Data: {self.project_root / 'personality_data'}")
    
    async def start_system(self):
        """Start the complete local system"""
        print("\n🚀 Starting Local Becoming One™ System")
        print("="*60)
        print("READY FOR:")
        print("1. Drop files in LOCAL_INBOX/inbox/ for processing")
        print("2. Transcribe audio/video with: python transcribe_media.py file.mp4 --inbox LOCAL_INBOX/inbox")
        print("3. Add personality framework content")
        print("4. Test all AI capabilities locally")
        print("5. Prepare content for cloud migration tomorrow")
        print("="*60)
        
        # Prepare for Fourth Way and Hylozoics
        print("\n🌱 Preparing expandable personality framework...")
        fourth_way_prep = self.personality_framework.prepare_for_fourth_way()
        hylozoics_prep = self.personality_framework.prepare_for_hylozoics()
        
        print(f"✅ Fourth Way structure prepared: {len(fourth_way_prep['planned_concepts'])} concepts")
        print(f"✅ Hylozoics structure prepared: {len(hylozoics_prep['planned_concepts'])} concepts")
        
        # Show framework status
        status = self.personality_framework.get_system_status()
        print(f"\n📊 Personality Framework Status:")
        print(f"   Active frameworks: {status['active_frameworks']}")
        print(f"   Framework names: {', '.join(status['framework_names'])}")
        print(f"   Total concepts: {status['total_concepts']}")
        print(f"   Expandability: {status['expandability_status']}")
        
        # Start INBOX monitoring
        print(f"\n👁️  Starting INBOX monitoring...")
        print(f"📂 Watching: {self.local_inbox / 'inbox'}")
        print(f"📂 Results in: {self.local_inbox / 'completed'}")
        print(f"📂 Content suggestions: {self.local_inbox / 'content_suggestions'}")
        print(f"📂 Processing logs: {self.local_inbox / 'logs'}")
        
        try:
            # Start INBOX processor
            self.inbox_processor.start_watching()
        except KeyboardInterrupt:
            print("\n🛑 Local system stopped by user")
        except Exception as e:
            print(f"❌ System error: {e}")
    
    def show_usage_guide(self):
        """Show how to use the local system"""
        guide = f"""
🏠 LOCAL BECOMING ONE™ SYSTEM USAGE GUIDE

📁 FOLDER STRUCTURE:
{self.local_inbox}/
├── inbox/              ← DROP FILES HERE for processing
├── processing/         ← Files being processed
├── completed/          ← Successfully processed files  
├── failed/            ← Files that need attention
├── content_suggestions/ ← Generated social media content
└── logs/              ← Processing history

🎵 TRANSCRIPTION WORKFLOW:
1. Record workshop/interview (any format: .mp4, .mp3, .wav, etc.)
2. Transcribe: python transcribe_media.py recording.mp4 --inbox LOCAL_INBOX/inbox
3. Transcript automatically processed by INBOX system
4. Teaching content → Knowledge base
5. Social content → Generated automatically

📝 CONTENT PROCESSING:
1. Drop any text file (.txt, .md, .docx) in LOCAL_INBOX/inbox/
2. AI automatically identifies Johan vs Marianne vs participants
3. Teaching content uploaded to knowledge base
4. Community content stored separately
5. Social media suggestions generated

🧠 PERSONALITY FRAMEWORK EXPANSION:
- Fourth Way concepts ready for integration
- Hylozoics system prepared for addition
- Framework designed for continuous growth
- All changes tracked and versioned

🚀 TOMORROW'S CLOUD MIGRATION:
- All local content will sync to cloud
- System will run 24/7 on your NAS
- Local testing ensures everything works perfectly

💡 QUICK TESTS:
python transcribe_media.py --show-options
python start_local_system.py
echo "Test content from Johan about emotional anchors" > LOCAL_INBOX/inbox/test.txt

🎯 READY TO START ADDING YOUR FOURTH WAY AND HYLOZOICS CONTENT!
        """
        
        print(guide)


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Local Becoming One™ System")
    parser.add_argument("--guide", action="store_true", help="Show usage guide")
    parser.add_argument("--status", action="store_true", help="Show system status")
    
    args = parser.parse_args()
    
    system = LocalBecomingOneSystem()
    
    if args.guide:
        system.show_usage_guide()
        return
    
    if args.status:
        status = system.personality_framework.get_system_status()
        print("📊 System Status:")
        for key, value in status.items():
            print(f"   {key}: {value}")
        return
    
    # Start the system
    await system.start_system()


if __name__ == "__main__":
    asyncio.run(main())
