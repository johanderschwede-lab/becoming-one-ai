#!/usr/bin/env python3
"""
Local Development Environment for Becoming One™ AI
Provides local testing, debugging, and deployment verification
"""
import os
import sys
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
import webbrowser
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

class DevEnvironment:
    """Local development environment manager"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Configure logging
        logger.add(
            self.logs_dir / "dev_{time}.log",
            rotation="1 day",
            level="DEBUG"
        )
    
    async def verify_setup(self):
        """Verify development environment setup"""
        print("\n🔍 Verifying development setup...")
        
        checks = {
            "Python": self._check_python(),
            "Virtual Environment": self._check_venv(),
            "Dependencies": await self._check_dependencies(),
            "Environment Variables": self._check_env_vars(),
            "Database Tables": await self._check_database(),
            "Git Configuration": self._check_git()
        }
        
        print("\n=== Development Environment Status ===")
        all_passed = True
        for check, (passed, message) in checks.items():
            status = "✅" if passed else "❌"
            print(f"{status} {check}: {message}")
            all_passed = all_passed and passed
        
        return all_passed
    
    def _check_python(self):
        """Check Python version"""
        version = sys.version_info
        required = (3, 9)
        if version >= required:
            return True, f"Python {version.major}.{version.minor} (Required: 3.9+)"
        return False, f"Python {version.major}.{version.minor} (Need 3.9+)"
    
    def _check_venv(self):
        """Check if running in virtual environment"""
        in_venv = sys.prefix != sys.base_prefix
        return in_venv, "Active" if in_venv else "Not active"
    
    async def _check_dependencies(self):
        """Check required packages"""
        try:
            import telegram
            import openai
            from supabase import create_client
            return True, "All required packages installed"
        except ImportError as e:
            return False, f"Missing package: {str(e)}"
    
    def _check_env_vars(self):
        """Check required environment variables"""
        required_vars = [
            "TELEGRAM_BOT_TOKEN",
            "OPENAI_API_KEY",
            "SUPABASE_URL",
            "SUPABASE_ANON_KEY"
        ]
        
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            return False, f"Missing: {', '.join(missing)}"
        return True, "All required variables set"
    
    async def _check_database(self):
        """Check database tables"""
        try:
            from database.operations import SupabaseClient
            client = SupabaseClient()
            
            # Check essential tables
            tables = [
                "teaching_materials",
                "personality_profiles",
                "personality_analysis"
            ]
            
            for table in tables:
                result = client.client.table(table).select("*").limit(1).execute()
            
            return True, "All required tables accessible"
        except Exception as e:
            return False, f"Database error: {str(e)}"
    
    def _check_git(self):
        """Check git configuration"""
        try:
            remote = subprocess.check_output(
                ["git", "remote", "get-url", "origin"],
                text=True
            ).strip()
            
            if "becoming-one-ai" in remote:
                return True, f"Git configured: {remote}"
            return False, f"Unexpected remote: {remote}"
        except Exception as e:
            return False, f"Git error: {str(e)}"
    
    async def run_local_bot(self):
        """Run the bot locally for testing"""
        print("\n🤖 Starting local bot instance...")
        
        # First verify environment
        if not await self.verify_setup():
            print("\n❌ Environment verification failed")
            print("Please fix issues before running the bot")
            return
        
        try:
            from bots.telegram.enhanced_telegram_bot import EnhancedBecomingOneTelegramBot
            
            bot = EnhancedBecomingOneTelegramBot()
            print("\n✅ Bot initialized successfully")
            print("■ RBAC system: ENABLED")
            print("◆ Payment system: READY")
            print("🏛️ Sacred Library: INTEGRATED")
            print("🧠 AI Engine: FULL ACCESS")
            print("\n📱 Send a message to your bot to test!")
            
            await bot.run()
            
        except Exception as e:
            print(f"\n❌ Bot error: {e}")
            import traceback
            traceback.print_exc()
    
    async def test_sacred_library(self):
        """Test Sacred Library integration"""
        print("\n📚 Testing Sacred Library...")
        
        try:
            from core.ai_engine import BecomingOneAI
            
            ai = BecomingOneAI()
            test_queries = [
                "What does Laurency say about consciousness?",
                "How does development work?",
                "What is the meaning of life?"
            ]
            
            for query in test_queries:
                print(f"\nTesting query: {query}")
                quotes = await ai.search_sacred_library(query)
                print(f"Found {len(quotes)} relevant quotes:")
                for i, quote in enumerate(quotes, 1):
                    print(f"\n{i}. From {quote['metadata'].get('chapter', 'Unknown')}:")
                    print(f"   {quote['content'][:200]}...")
            
            print("\n✅ Sacred Library test complete!")
            
        except Exception as e:
            print(f"\n❌ Sacred Library error: {e}")
            import traceback
            traceback.print_exc()
    
    async def test_personality_analysis(self):
        """Test personality analysis system"""
        print("\n🧠 Testing personality analysis...")
        
        try:
            from core.ai_engine import BecomingOneAI
            
            ai = BecomingOneAI()
            test_message = """I've been feeling stuck lately. 
            I meditate daily but still feel like something's missing. 
            Maybe I need to change my approach to spiritual development."""
            
            print("\nAnalyzing test message...")
            response = await ai.process_message(
                person_id="test_user",
                message=test_message,
                source="test",
                user_tier="premium"
            )
            
            print("\nAI Response:")
            print(response)
            
            print("\n✅ Personality analysis test complete!")
            
        except Exception as e:
            print(f"\n❌ Personality analysis error: {e}")
            import traceback
            traceback.print_exc()

async def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Local Development Environment",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify development environment"
    )
    
    parser.add_argument(
        "--bot",
        action="store_true",
        help="Run bot locally"
    )
    
    parser.add_argument(
        "--test-library",
        action="store_true",
        help="Test Sacred Library integration"
    )
    
    parser.add_argument(
        "--test-analysis",
        action="store_true",
        help="Test personality analysis"
    )
    
    args = parser.parse_args()
    
    dev = DevEnvironment()
    
    if args.verify:
        await dev.verify_setup()
    elif args.bot:
        await dev.run_local_bot()
    elif args.test_library:
        await dev.test_sacred_library()
    elif args.test_analysis:
        await dev.test_personality_analysis()
    else:
        print("\n🛠️  Becoming One™ AI - Local Development")
        print("\nUsage:")
        print("  --verify         : Verify development environment")
        print("  --bot           : Run bot locally")
        print("  --test-library  : Test Sacred Library")
        print("  --test-analysis : Test personality analysis")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n● Development session ended by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
