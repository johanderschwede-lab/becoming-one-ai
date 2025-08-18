#!/usr/bin/env python3
"""
Verify Railway environment variables
"""
import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_railway_env():
    """Check Railway environment variables"""
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "OPENAI_API_KEY"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print("❌ Missing environment variables:")
        for var in missing:
            print(f"  - {var}")
        return False
    
    print("✅ All required environment variables are set")
    return True

def test_telegram_token():
    """Test if Telegram token is valid"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        return False
        
    try:
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe")
        if response.status_code == 200:
            data = response.json()
            if data["ok"]:
                print(f"✅ Telegram token valid - Bot: @{data['result']['username']}")
                return True
        print("❌ Invalid Telegram token")
        return False
    except Exception as e:
        print(f"❌ Error testing Telegram token: {e}")
        return False

def test_supabase():
    """Test Supabase connection"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    if not url or not key:
        return False
        
    try:
        from supabase import create_client
        client = create_client(url, key)
        # Try a simple query
        result = client.table("teaching_materials").select("count", count="exact").execute()
        count = result.count
        print(f"✅ Supabase connection working - {count} teaching materials found")
        return True
    except Exception as e:
        print(f"❌ Error testing Supabase: {e}")
        return False

def test_openai():
    """Test OpenAI API key"""
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return False
        
    try:
        import openai
        openai.api_key = key
        # Try a simple completion
        response = openai.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": "Say 'test' in one word"}],
            max_tokens=1
        )
        if response:
            print("✅ OpenAI API key valid")
            return True
        print("❌ Invalid OpenAI API key")
        return False
    except Exception as e:
        print(f"❌ Error testing OpenAI API: {e}")
        return False

def main():
    """Main function"""
    print("\n=== Verifying Railway Environment ===\n")
    
    # Check environment variables
    if not check_railway_env():
        sys.exit(1)
    
    print("\n=== Testing API Connections ===\n")
    
    # Test each service
    telegram_ok = test_telegram_token()
    supabase_ok = test_supabase()
    openai_ok = test_openai()
    
    print("\n=== Summary ===\n")
    print(f"Telegram Bot API: {'✅' if telegram_ok else '❌'}")
    print(f"Supabase: {'✅' if supabase_ok else '❌'}")
    print(f"OpenAI API: {'✅' if openai_ok else '❌'}")
    
    if not all([telegram_ok, supabase_ok, openai_ok]):
        print("\n❌ Some services are not working correctly")
        sys.exit(1)
    
    print("\n✅ All services are working correctly")

if __name__ == "__main__":
    main()
