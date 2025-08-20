#!/usr/bin/env python3
"""
Test bot locally without external dependencies
"""
import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set testing mode to prevent background tasks
os.environ["TESTING_MODE"] = "true"

# Add src to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

async def test_basic_bot():
    """Test basic bot functionality without Sacred Library"""
    print("\n🤖 Testing basic bot functionality...")
    
    try:
        # Test OpenAI connection first
        from openai import OpenAI
        
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://api.openai.com/v1",
            timeout=10.0
        )
        
        print("✅ OpenAI client initialized")
        
        # Test a simple chat completion
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": "Say hello"}
            ],
            max_tokens=50
        )
        
        print(f"✅ OpenAI response: {response.choices[0].message.content}")
        
        # Test Telegram bot initialization (without running)
        from telegram import Bot
        
        bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
        me = await bot.get_me()
        print(f"✅ Telegram bot connected: @{me.username}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing basic bot: {e}")
        return False

async def test_simple_ai_response():
    """Test AI response generation without Sacred Library"""
    print("\n🧠 Testing AI response generation...")
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url="https://api.openai.com/v1",
            timeout=30.0
        )
        
        # Simple Becoming One™ system prompt
        system_prompt = """You are an AI mentor trained in the Becoming One™ method.

CORE MISSION: Guide this person toward discovering their authentic self.

RESPONSE STYLE:
- Be warm, empathetic, and genuinely curious
- Ask powerful questions that promote self-reflection
- Use "I wonder..." and "What if..." to invite exploration
- Keep responses focused and meaningful"""

        test_message = "I've been feeling stuck lately and don't know what direction to take in my life."
        
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": test_message}
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        ai_response = response.choices[0].message.content
        
        print("\n--- Test Conversation ---")
        print(f"User: {test_message}")
        print(f"\nAI: {ai_response}")
        print("--- End Conversation ---")
        
        print("\n✅ AI response generation working!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing AI response: {e}")
        return False

async def main():
    print("\n" + "="*60)
    print("🧪 OFFLINE BOT TESTING")
    print("="*60)
    print("Testing core functionality without external services")
    
    tests = [
        ("Basic Bot Components", test_basic_bot),
        ("AI Response Generation", test_simple_ai_response)
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        print(f"\n▶️  {test_name}...")
        if not await test_func():
            all_passed = False
            break
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("The bot core functionality is working correctly.")
        print("\nNext: Fix async queue issue and deploy to Railway")
    else:
        print("❌ SOME TESTS FAILED")
        print("Please fix the issues before deploying")
    print("="*60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n● Testing stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
