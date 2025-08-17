#!/usr/bin/env python3
"""
Becoming One™ AI Telegram Bot - Startup Script
Simple launcher that checks configuration and starts the bot
"""
import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY", 
        "OPENAI_API_KEY",
        "TELEGRAM_BOT_TOKEN"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var).startswith(('your-', 'sk-your-')):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   • {var}")
        print("\nPlease add these to your .env file before starting the bot.")
        return False
    
    print("✅ All required environment variables are set")
    return True

def main():
    print("🤖 Starting Becoming One™ AI Telegram Bot...")
    print("-" * 50)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
    except ImportError:
        print("⚠️  python-dotenv not installed, using system environment")
    
    # Check configuration
    if not check_environment():
        sys.exit(1)
    
    # Start the bot
    try:
        from bots.telegram.telegram_bot import BecomingOneTelegramBot
        
        print("🚀 Initializing Becoming One™ AI Bot...")
        bot = BecomingOneTelegramBot()
        
        print("🌟 Bot ready! Starting conversation handler...")
        print("💬 Users can now interact with your Becoming One™ AI mentor")
        print("🎯 Features: Emotional anchor recognition, journey tracking, cross-platform memory")
        print("-" * 50)
        
        # Run the bot
        import asyncio
        asyncio.run(bot.run())
        
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        print("\nCheck your API keys and try again.")

if __name__ == "__main__":
    main()
