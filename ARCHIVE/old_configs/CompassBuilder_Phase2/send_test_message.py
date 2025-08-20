#!/usr/bin/env python3
"""
Send Test Message

This script will send a test message to the user.
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def send_test_message():
    """Send a test message"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found")
        return False
    
    print("🔔 SENDING TEST MESSAGE")
    print("="*40)
    
    # Create a simple test message
    message = """
🎯 *COMPASS CORE UPDATE - TEST MESSAGE*

🧠 *Your Enhanced Compass System is Working!*

📊 *System Status:* ✅ FULLY OPERATIONAL
🏷️ *Documents Processed:* 12 total
✅ *Compass Core:* 6 files
📁 *Human Review:* 3 files
🗑️ *Quarantine:* 2 files

🔑 *Key Features Working:*
• Enhanced Fluff Detector
• Compass Classifier  
• Strategic Scorer
• Curated Exporter
• Master Prompt Review
• Supabase Integration

⏰ *Test Time:* 2025-08-19 14:40:00

Your system is ready for 200+ documents! 🎉
    """
    
    # Try to send to username
    print("📤 Attempting to send test message...")
    
    send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    # Try different chat ID formats
    test_chat_ids = [
        "@JohanNiklasson",
        "JohanNiklasson", 
        "@johanniklasson",
        "johanniklasson"
    ]
    
    for chat_id in test_chat_ids:
        print(f"  Trying: {chat_id}")
        
        send_data = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(send_url, json=send_data, timeout=10)
            print(f"    Response: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    print(f"✅ SUCCESS! Message sent to {chat_id}")
                    print("📱 Check your Telegram for the message!")
                    return True
                else:
                    print(f"    API Error: {result.get('description')}")
            else:
                print(f"    HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"    Error: {e}")
    
    print("\n❌ Could not send message to any target")
    print("\nTo get notifications working:")
    print("1. Open Telegram")
    print("2. Search for: @willbdotoneupdatebot")
    print("3. Click 'Start' or send 'hello'")
    print("4. Wait 10 seconds")
    print("5. Run this script again")
    
    return False

if __name__ == "__main__":
    send_test_message()
