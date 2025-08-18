#!/usr/bin/env python3
"""
Local Bot Debugger
Runs the bot locally with detailed logging and instant feedback
"""
import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_openai():
    """Test OpenAI connection"""
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1
        )
        print("✅ OpenAI connection working")
        return True
    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        return False

async def test_telegram():
    """Test Telegram connection"""
    try:
        from telegram import Bot
        bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
        me = await bot.get_me()
        print(f"✅ Telegram connection working (@{me.username})")
        return True
    except Exception as e:
        print(f"❌ Telegram error: {e}")
        return False

async def test_supabase():
    """Test Supabase connection"""
    try:
        from database.operations import db
        result = db.client.table('teaching_materials').select("count", count="exact").execute()
        count = result.count
        print(f"✅ Supabase connection working ({count} teaching materials)")
        return True
    except Exception as e:
        print(f"❌ Supabase error: {e}")
        return False

async def run_bot(timeout=30):
    """Run the bot with timeout"""
    try:
        from bots.telegram.enhanced_telegram_bot import EnhancedBecomingOneTelegramBot
        
        print("\n=== Starting Bot ===")
        bot = EnhancedBecomingOneTelegramBot()
        
        # Run the bot with timeout
        try:
            await asyncio.wait_for(bot.run(), timeout=timeout)
        except asyncio.TimeoutError:
            print(f"✅ Bot ran successfully for {timeout} seconds")
            return True
        except Exception as e:
            print(f"❌ Bot runtime error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Bot initialization error: {e}")
        return False

async def main():
    print("\n=== Testing Environment ===")
    
    # Load environment variables
    load_dotenv()
    
    # Test all connections first
    openai_ok = await test_openai()
    telegram_ok = await test_telegram()
    supabase_ok = await test_supabase()
    
    print("\n=== Connection Summary ===")
    print(f"OpenAI API: {'✅' if openai_ok else '❌'}")
    print(f"Telegram API: {'✅' if telegram_ok else '❌'}")
    print(f"Supabase: {'✅' if supabase_ok else '❌'}")
    
    if not all([openai_ok, telegram_ok, supabase_ok]):
        print("\n❌ Some connections failed. Fix them before proceeding.")
        return
    
    # Run the bot for 30 seconds
    await run_bot(timeout=30)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n● Debugging stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
