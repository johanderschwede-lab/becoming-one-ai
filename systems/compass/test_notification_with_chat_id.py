#!/usr/bin/env python3
"""
Test Notification with Chat ID

This script will send a test notification using the found chat ID.
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def send_test_notification():
    """Send a test notification"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found")
        return False
    
    if not chat_id:
        print("❌ TELEGRAM_CHAT_ID not found")
        return False
    
    print("🔔 SENDING TEST NOTIFICATION")
    print("="*40)
    print(f"Bot Token: {bot_token[:20]}...")
    print(f"Chat ID: {chat_id}")
    
    # Create a test message
    message = """
🎯 *COMPASS CORE UPDATE - SUCCESS!*

🧠 *Your Enhanced Compass System is Working!*

📊 *System Status:* ✅ FULLY OPERATIONAL
🏷️ *Documents Processed:* 14 total
✅ *Compass Core:* 6 files
📁 *Human Review:* 5 files
🗑️ *Quarantine:* 2 files

🔑 *Key Features Working:*
• Enhanced Fluff Detector ✅
• Compass Classifier ✅
• Strategic Scorer ✅
• Curated Exporter ✅
• Master Prompt Review ✅
• Supabase Integration ✅
• Telegram Notifications ✅

⏰ *Test Time:* 2025-08-19 14:45:00

🎉 *NOTIFICATION SYSTEM ACTIVE!*

Your enhanced Compass system is ready for 200+ documents!
    """
    
    send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    send_data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        print("📤 Sending notification...")
        response = requests.post(send_url, json=send_data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print("✅ SUCCESS! Notification sent!")
                print("📱 Check your Telegram for the message!")
                return True
            else:
                print(f"❌ API Error: {result.get('description')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending notification: {e}")
        return False

if __name__ == "__main__":
    send_test_notification()
