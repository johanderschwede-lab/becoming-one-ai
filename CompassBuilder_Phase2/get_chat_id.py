#!/usr/bin/env python3
"""
Get Telegram Chat ID

This script helps you get your Telegram chat ID for notifications.
"""

import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()

def get_chat_id():
    """Get chat ID from Telegram bot"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in .env file")
        return None
    
    print("🔔 TELEGRAM CHAT ID SETUP")
    print("="*40)
    print("To get your chat ID:")
    print("1. Open Telegram")
    print("2. Search for your bot: @willbdotoneupdatebot")
    print("3. Start a chat with the bot")
    print("4. Send any message to the bot (like 'hello')")
    print("5. Then press Enter here to check for messages")
    
    input("\nPress Enter after sending a message to your bot...")
    
    # Get updates
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        if data["ok"] and data["result"]:
            for update in data["result"]:
                if "message" in update:
                    chat_id = update["message"]["chat"]["id"]
                    user_name = update["message"]["from"].get("first_name", "Unknown")
                    print(f"✅ Found chat ID: {chat_id}")
                    print(f"👤 User: {user_name}")
                    
                    # Add to .env file
                    with open(".env", "a") as f:
                        f.write(f"TELEGRAM_CHAT_ID={chat_id}\n")
                    
                    print(f"✅ Chat ID saved to .env file")
                    return chat_id
        else:
            print("❌ No messages found. Make sure you sent a message to your bot.")
            return None
    else:
        print(f"❌ Error getting updates: {response.status_code}")
        return None

def test_notification():
    """Test sending a notification"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("❌ Bot token or chat ID not configured")
        return False
    
    message = """
🎯 *COMPASS CORE UPDATE*

🧠 *Test Master Prompt Document*

📊 *Score:* 13.2/10
🏷️ *Category:* method_model
✅ *Decision:* SAFE_CORE - Add directly to Compass core
📁 *Location:* COMPASS_CORE/method_model

🔑 *Key Terms:* emotional anchor, stance, nervous system, digest, pearl

⏰ *Processed:* 2025-08-19 14:10:00

Your content has been added to the Compass Core! 🎉
    """
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            print("✅ Test notification sent successfully!")
            return True
        else:
            print(f"❌ Failed to send notification: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error sending notification: {e}")
        return False

if __name__ == "__main__":
    chat_id = get_chat_id()
    
    if chat_id:
        print(f"\n🧪 Testing notification...")
        test_notification()
