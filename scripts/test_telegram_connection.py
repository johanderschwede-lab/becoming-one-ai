#!/usr/bin/env python3
"""
Test Telegram bot connection
"""
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_telegram_bot():
    """Test if Telegram bot is working"""
    print("🤖 Testing Telegram bot connection...")
    
    try:
        from telegram import Bot
        
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            print("❌ TELEGRAM_BOT_TOKEN not found")
            return False
        
        print(f"✅ Token found: {token[:10]}...")
        
        bot = Bot(token=token)
        me = await bot.get_me()
        
        print(f"✅ Bot connected: @{me.username}")
        print(f"   Name: {me.first_name}")
        print(f"   ID: {me.id}")
        print(f"   Can join groups: {me.can_join_groups}")
        print(f"   Can read all messages: {me.can_read_all_group_messages}")
        
        # Test sending a message to yourself (bot creator)
        try:
            # Get updates to see if there are any pending
            updates = await bot.get_updates(limit=1)
            print(f"✅ Can get updates: {len(updates)} pending")
            
            if updates:
                chat_id = updates[0].effective_chat.id
                print(f"   Last chat ID: {chat_id}")
        except Exception as e:
            print(f"⚠️  Could not get updates: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Bot connection failed: {e}")
        return False

async def main():
    print("\n🔍 Telegram Bot Diagnostics")
    print("="*40)
    
    success = await test_telegram_bot()
    
    if success:
        print("\n✅ Bot connection is working!")
        print("\nPossible issues if bot not responding:")
        print("1. Bot might not be started with polling")
        print("2. Check Railway logs for errors")
        print("3. Verify bot is receiving messages")
    else:
        print("\n❌ Bot connection failed!")
        print("Check your TELEGRAM_BOT_TOKEN in Railway variables")

if __name__ == "__main__":
    asyncio.run(main())
