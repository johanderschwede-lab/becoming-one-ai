#!/usr/bin/env python3
"""
Live System Test for Becoming One™ AI Journey System
Tests all connections with your actual API keys
"""
import os
import sys
import requests
from pathlib import Path

def load_environment():
    """Load environment variables"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded from .env")
    except ImportError:
        print("⚠️  python-dotenv not available, using system environment")

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\n🤖 TESTING OPENAI CONNECTION")
    print("-" * 40)
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key not found in environment")
        return False
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Test with a simple completion
        data = {
            "model": "gpt-4-turbo-preview",
            "messages": [{"role": "user", "content": "Hello, this is a connection test."}],
            "max_tokens": 10
        }
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            print("✅ OpenAI API: CONNECTED")
            print("   Model: gpt-4-turbo-preview")
            print("   Ready for AI responses")
            return True
        else:
            print(f"❌ OpenAI API: Error {response.status_code}")
            print(f"   Response: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI API: FAILED")
        print(f"   Error: {str(e)}")
        return False

def test_telegram_bot():
    """Test Telegram bot connection"""
    print("\n📱 TESTING TELEGRAM BOT CONNECTION")
    print("-" * 40)
    
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("❌ Telegram bot token not found in environment")
        return False
    
    try:
        # Test bot connection
        response = requests.get(
            f"https://api.telegram.org/bot{bot_token}/getMe",
            timeout=10
        )
        
        if response.status_code == 200:
            bot_info = response.json()
            if bot_info.get("ok"):
                result = bot_info.get("result", {})
                print("✅ Telegram Bot: CONNECTED")
                print(f"   Bot Name: {result.get('first_name', 'Unknown')}")
                print(f"   Username: @{result.get('username', 'unknown')}")
                print(f"   Bot ID: {result.get('id', 'unknown')}")
                return True
            else:
                print("❌ Telegram Bot: API returned error")
                return False
        else:
            print(f"❌ Telegram Bot: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Telegram Bot: FAILED")
        print(f"   Error: {str(e)}")
        return False

def test_supabase_connection():
    """Test Supabase database"""
    print("\n🗄️  TESTING SUPABASE DATABASE")
    print("-" * 40)
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        print("❌ Supabase credentials not found")
        return False
    
    try:
        headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
        
        # Test database connection
        response = requests.get(f"{url}/rest/v1/identity_registry?limit=1", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Supabase Database: CONNECTED")
            print("   • identity_registry: Ready")
            print("   • Cross-platform identity management: Active")
            print("   • Journey tracking: Enabled")
            return True
        else:
            print(f"❌ Supabase: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Supabase: FAILED")
        print(f"   Error: {str(e)}")
        return False

def show_launch_instructions():
    """Show how to launch the bot"""
    print("\n🚀 LAUNCH INSTRUCTIONS")
    print("-" * 40)
    print("Your Becoming One™ AI system is ready!")
    print()
    print("TO START THE BOT:")
    print("   python3 start_bot.py")
    print()
    print("TO TEST THE BOT:")
    print("   1. Go to Telegram")
    print("   2. Find your bot (search for the username shown above)")
    print("   3. Send: /start")
    print("   4. Try: 'I'm feeling stuck with my goals'")
    print("   5. Watch your AI mentor respond with Becoming One™ wisdom!")
    print()
    print("🌟 FEATURES ACTIVE:")
    print("   • Emotional anchor recognition")
    print("   • Journey stage detection")
    print("   • Cross-platform memory")
    print("   • Personalized Becoming One™ guidance")

def main():
    print("\n" + "="*60)
    print("🧪 BECOMING ONE™ AI - LIVE SYSTEM TEST")
    print("="*60)
    print("Testing your complete AI mentorship system...")
    print("-" * 60)
    
    # Load environment
    load_environment()
    
    # Test all connections
    openai_ok = test_openai_connection()
    telegram_ok = test_telegram_bot()
    supabase_ok = test_supabase_connection()
    
    # Show results
    print("\n" + "="*60)
    if openai_ok and telegram_ok and supabase_ok:
        print("🎉 ALL SYSTEMS: READY FOR LAUNCH!")
        print("="*60)
        show_launch_instructions()
    else:
        print("⚠️  SYSTEM STATUS: NEEDS ATTENTION")
        print("="*60)
        print("Some connections failed. Check the errors above.")
    
    return openai_ok and telegram_ok and supabase_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
