#!/usr/bin/env python3
"""
Test Notification Now

This script will send a test notification to your Telegram.
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def send_test_notification():
    """Send a test notification"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found")
        return False
    
    print("🔔 SENDING TEST NOTIFICATION")
    print("="*40)
    print("This will send a test message to your Telegram bot.")
    print("Make sure you've started a chat with @willbdotoneupdatebot")
    
    # Try to get chat ID from recent updates
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        if data["ok"] and data["result"]:
            # Get the most recent chat ID
            for update in reversed(data["result"]):
                if "message" in update:
                    chat_id = update["message"]["chat"]["id"]
                    user_name = update["message"]["from"].get("first_name", "Unknown")
                    print(f"✅ Found chat ID: {chat_id}")
                    print(f"👤 User: {user_name}")
                    
                    # Send test message
                    message = """
🎯 *COMPASS CORE UPDATE - TEST*

🧠 *Test Document Processed*

📊 *Score:* 13.2/10 (Excellent!)
🏷️ *Category:* method_model
✅ *Decision:* SAFE_CORE - Added to Compass core
📁 *Location:* COMPASS_CORE/method_model

🔑 *Key Terms:* emotional anchor, stance, nervous system, digest, pearl

⏰ *Processed:* 2025-08-19 14:30:00

Your enhanced Compass system is working perfectly! 🎉

This is a test notification to confirm the system is operational.
                    """
                    
                    send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
                    send_data = {
                        "chat_id": chat_id,
                        "text": message,
                        "parse_mode": "Markdown"
                    }
                    
                    try:
                        send_response = requests.post(send_url, json=send_data, timeout=10)
                        if send_response.status_code == 200:
                            print("✅ Test notification sent successfully!")
                            print("📱 Check your Telegram for the message!")
                            
                            # Save chat ID to .env
                            with open(".env", "a") as f:
                                f.write(f"TELEGRAM_CHAT_ID={chat_id}\n")
                            print(f"✅ Chat ID saved to .env file")
                            
                            return True
                        else:
                            print(f"❌ Failed to send: {send_response.status_code}")
                            return False
                    except Exception as e:
                        print(f"❌ Error sending: {e}")
                        return False
        else:
            print("❌ No messages found in bot updates")
            print("Please:")
            print("1. Open Telegram")
            print("2. Search for @willbdotoneupdatebot")
            print("3. Start a chat and send 'hello'")
            print("4. Run this script again")
            return False
    else:
        print(f"❌ Error getting updates: {response.status_code}")
        return False

if __name__ == "__main__":
    send_test_notification()
