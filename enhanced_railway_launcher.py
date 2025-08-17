#!/usr/bin/env python3
"""
Railway launcher for Enhanced Telegram Bot
Fixes import paths for the enhanced bot with full AI features
"""
import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Set up environment
from dotenv import load_dotenv
load_dotenv()

import asyncio
import logging
from loguru import logger

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

def main():
    """Main launcher function"""
    print("\n" + "="*60)
    print("▲ BECOMING ONE™ ENHANCED AI TELEGRAM BOT")
    print("="*60)
    print("■ Full AI system with RBAC and payments")
    print("◆ Initializing enhanced features...")
    
    # Check for required environment variables
    required_vars = ["TELEGRAM_BOT_TOKEN"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return
    
    print("✅ Environment variables loaded")
    
    try:
        # Import and run the enhanced bot
        from bots.telegram.enhanced_telegram_bot import EnhancedBecomingOneTelegramBot
        
        bot = EnhancedBecomingOneTelegramBot()
        
        print("● Starting Enhanced Becoming One™ AI Bot...")
        print("■ RBAC system enabled")
        print("◆ Payment system ready")
        print("▲ Full AI engine loaded")
        print("● Bot is running... Press Ctrl+C to stop")
        
        asyncio.run(bot.run())
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("■ Falling back to simple bot...")
        
        # Fallback to simple bot if enhanced bot fails
        try:
            from simple_railway_bot import main as simple_main
            simple_main()
        except Exception as fallback_error:
            print(f"❌ Fallback failed: {fallback_error}")
            return
            
    except Exception as e:
        logger.error(f"Enhanced bot failed: {e}")
        print(f"❌ Enhanced bot error: {e}")
        print("■ Check logs for details")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n● Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Check your configuration and try again.")
