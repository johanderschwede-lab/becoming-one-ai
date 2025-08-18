#!/usr/bin/env python3
"""
Railway Development & Debugging Tool for Becoming One™ AI
Provides local testing, verification, and fast deployment
"""
import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import httpx
from loguru import logger

# Add src to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from database.operations import SupabaseClient
from openai import OpenAI
from telegram import Bot

class RailwayDevTool:
    """Development and debugging tool for Railway deployments"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.version_file = self.project_root / ".deploy_version"
        self.changes_file = self.project_root / ".changes_summary"
        
        # Initialize version tracking
        self.current_version = self._get_current_version()
        
        # Configure logging
        logger.add(
            self.project_root / "logs/railway_dev_{time}.log",
            rotation="1 day",
            retention="7 days",
            level="DEBUG"
        )
    
    async def verify_all_connections(self) -> Dict[str, bool]:
        """Verify all external service connections"""
        results = {
            "supabase": False,
            "openai": False,
            "telegram": False,
            "railway": False
        }
        
        print("\n🔍 Verifying connections...")
        
        # Test Supabase
        try:
            client = SupabaseClient()
            result = client.client.table("teaching_materials").select("*").limit(1).execute()
            results["supabase"] = True
            print("✅ Supabase connection verified")
        except Exception as e:
            print(f"❌ Supabase error: {e}")
        
        # Test OpenAI
        try:
            openai = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url="https://api.openai.com/v1",
                timeout=10.0
            )
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            results["openai"] = True
            print("✅ OpenAI connection verified")
        except Exception as e:
            print(f"❌ OpenAI error: {e}")
        
        # Test Telegram
        try:
            bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
            me = await bot.get_me()
            results["telegram"] = True
            print("✅ Telegram connection verified")
        except Exception as e:
            print(f"❌ Telegram error: {e}")
        
        # Test Railway
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://web-production-048a5.up.railway.app/health",
                    timeout=5.0
                )
                results["railway"] = response.status_code == 200
                print("✅ Railway health check passed" if results["railway"] else "❌ Railway health check failed")
        except Exception as e:
            print(f"❌ Railway error: {e}")
        
        return results
    
    async def run_local_bot(self):
        """Run the bot locally for testing"""
        print("\n🤖 Starting local bot instance...")
        
        try:
            from bots.telegram.enhanced_telegram_bot import EnhancedBecomingOneTelegramBot
            
            bot = EnhancedBecomingOneTelegramBot()
            print("✅ Bot initialized successfully")
            print("■ RBAC system: ENABLED")
            print("◆ Payment system: READY")
            print("🏛️ Sacred Library: INTEGRATED")
            print("🧠 AI Engine: FULL ACCESS")
            
            await bot.run()
            
        except Exception as e:
            print(f"❌ Local bot error: {e}")
            import traceback
            traceback.print_exc()
    
    def _get_current_version(self) -> int:
        """Get current deployment version"""
        try:
            if self.version_file.exists():
                return int(self.version_file.read_text().strip())
            return 0
        except:
            return 0
    
    def _save_version(self, version: int):
        """Save deployment version"""
        self.version_file.write_text(str(version))
    
    def _get_changes_summary(self) -> List[str]:
        """Get summary of changes since last deployment"""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-status", "HEAD~1"],
                capture_output=True,
                text=True
            )
            changes = []
            for line in result.stdout.splitlines():
                if line.strip():
                    status, file = line.split(maxsplit=1)
                    changes.append(f"{status}: {file}")
            return changes
        except:
            return ["No changes detected"]
    
    async def fast_deploy(self):
        """Deploy changes to Railway quickly"""
        print("\n🚀 Starting fast deployment...")
        
        # Verify connections first
        results = await self.verify_all_connections()
        if not all(results.values()):
            print("\n❌ Connection verification failed!")
            print("Please fix connection issues before deploying.")
            return False
        
        try:
            # Get changes
            changes = self._get_changes_summary()
            
            # Increment version
            new_version = self.current_version + 1
            self._save_version(new_version)
            
            # Commit changes
            commit_msg = f"v{new_version}: Fast deploy\n\nChanges:\n" + "\n".join(changes)
            
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            subprocess.run(["git", "push"], check=True)
            
            print("\n✅ Changes pushed to Railway")
            print(f"Version: v{new_version}")
            print("\nChanges:")
            for change in changes:
                print(f"  • {change}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Deployment error: {e}")
            return False

async def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Railway Development Tool")
    parser.add_argument("--verify", action="store_true", help="Verify all connections")
    parser.add_argument("--local", action="store_true", help="Run bot locally")
    parser.add_argument("--deploy", action="store_true", help="Deploy to Railway")
    args = parser.parse_args()
    
    tool = RailwayDevTool()
    
    if args.verify:
        await tool.verify_all_connections()
    elif args.local:
        await tool.run_local_bot()
    elif args.deploy:
        await tool.fast_deploy()
    else:
        print("\n🛠️  Railway Development Tool")
        print("\nUsage:")
        print("  --verify  : Test all connections")
        print("  --local   : Run bot locally")
        print("  --deploy  : Deploy to Railway")

if __name__ == "__main__":
    asyncio.run(main())
