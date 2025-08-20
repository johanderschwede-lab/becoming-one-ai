#!/usr/bin/env python3
"""
Send Direct Test Message

This script will try to send a test message directly.
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def send_direct_test():
    """Send a direct test message"""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found")
        return False
    
    print("🔔 SENDING DIRECT TEST MESSAGE")
    print("="*40)
    
    # Try sending to username
    message = """
🎯 *COMPASS CORE UPDATE - DIRECT TEST*

🧠 *Test Document Processed*

📊 *Score:* 13.2/10 (Excellent!)
🏷️ *Category:* method_model
✅ *Decision:* SAFE_CORE - Added to Compass core
📁 *Location:* COMPASS_CORE/method_model

🔑 *Key Terms:* emotional anchor, stance, nervous system, digest, pearl

⏰ *Processed:* 2025-08-19 14:35:00

Your enhanced Compass system is working perfectly! 🎉

This is a direct test notification.
    """
    
    # Try different approaches
    test_targets = [
        "@JohanNiklasson",  # Your username
        "JohanNiklasson",   # Without @
    ]
    
    for target in test_targets:
        print(f"📤 Trying to send to: {target}")
        
        send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        send_data = {
            "chat_id": target,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            response = requests.post(send_url, json=send_data, timeout=10)
            print(f"Response: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    print(f"✅ Message sent successfully to {target}!")
                    return True
                else:
                    print(f"❌ API Error: {result.get('description')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n❌ Could not send message to any target")
    print("Please make sure you've started a chat with @willbdotoneupdatebot")
    return False

if __name__ == "__main__":
    send_direct_test()
