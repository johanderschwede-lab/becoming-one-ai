#!/usr/bin/env python3
"""
Minimal Deployment Script for Becoming One™ AI Journey System
Creates a working version with existing infrastructure, ready for API keys
"""
import os
import sys
from pathlib import Path

def print_header():
    print("\n" + "="*60)
    print("🚀 BECOMING ONE™ AI - MINIMAL DEPLOYMENT")
    print("="*60)
    print("Setting up working system with your existing infrastructure...")
    print("-" * 60)

def create_development_env():
    """Create a development environment file for immediate testing"""
    print("\n📝 CREATING DEVELOPMENT ENVIRONMENT")
    print("-" * 40)
    
    dev_env = """# Becoming One™ AI Journey System - Development Environment
# This version works with your existing Supabase infrastructure

# === WORKING CONNECTIONS ===
SUPABASE_URL=https://emgidzzjpjtujozttzyv.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVtZ2lkenpqcGp0dWpvenR0enl2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUxNTMyMDksImV4cCI6MjA3MDcyOTIwOX0.JpMhtzZFqSP1C9BFcWypfZ2o9m8jheKoQgfhwFxUWxQ

# === SECURE CREDENTIALS (Ready for your API keys) ===
PINECONE_API_KEY=pcsk_2nX8US_Mku3PJmJ7hoe67kaw1tGHL7TwerFJ5zsjuakrSMjkvm1JcCDurxFpXcGDWd7yju
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=becoming-one-embeddings

# === ADD YOUR API KEYS HERE ===
OPENAI_API_KEY=sk-your-openai-key-here
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here

# === BUSINESS CONFIGURATION ===
MAKE_AGENT_ID=14ddbe97-b677-4073-9c6d-5d83f30ebc30
TELEGRAM_ESCALATION_CHAT_ID=1139989892

# === SYSTEM SETTINGS ===
DEBUG=true
LOG_LEVEL=info
ENVIRONMENT=development

# === BECOMING ONE™ METHOD CONFIGURATION ===
DEFAULT_PERSONALITY_PROFILE=adaptive_mentor
RESPONSE_STYLE=empathetic_guidance
LEARNING_MODE=continuous
ENABLE_EMOTIONAL_ANCHOR_RECOGNITION=true
ENABLE_JOURNEY_STAGE_DETECTION=true
ENABLE_CROSS_PLATFORM_MEMORY=true
"""
    
    with open(".env", "w") as f:
        f.write(dev_env)
    
    print("✅ Development environment created: .env")
    print("   Ready for your OpenAI and Telegram API keys")

def create_startup_script():
    """Create a simple startup script for the Telegram bot"""
    print("\n🤖 CREATING TELEGRAM BOT STARTUP SCRIPT")
    print("-" * 40)
    
    startup_script = """#!/usr/bin/env python3
\"\"\"
Becoming One™ AI Telegram Bot - Startup Script
Simple launcher that checks configuration and starts the bot
\"\"\"
import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

def check_environment():
    \"\"\"Check if all required environment variables are set\"\"\"
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY", 
        "OPENAI_API_KEY",
        "TELEGRAM_BOT_TOKEN"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var) or os.getenv(var).startswith(('your-', 'sk-your-')):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   • {var}")
        print("\\nPlease add these to your .env file before starting the bot.")
        return False
    
    print("✅ All required environment variables are set")
    return True

def main():
    print("🤖 Starting Becoming One™ AI Telegram Bot...")
    print("-" * 50)
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ Environment variables loaded")
    except ImportError:
        print("⚠️  python-dotenv not installed, using system environment")
    
    # Check configuration
    if not check_environment():
        sys.exit(1)
    
    # Start the bot
    try:
        from bots.telegram.telegram_bot import BecomingOneTelegramBot
        
        print("🚀 Initializing Becoming One™ AI Bot...")
        bot = BecomingOneTelegramBot()
        
        print("🌟 Bot ready! Starting conversation handler...")
        print("💬 Users can now interact with your Becoming One™ AI mentor")
        print("🎯 Features: Emotional anchor recognition, journey tracking, cross-platform memory")
        print("-" * 50)
        
        # Run the bot
        import asyncio
        asyncio.run(bot.run())
        
    except KeyboardInterrupt:
        print("\\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        print("\\nCheck your API keys and try again.")

if __name__ == "__main__":
    main()
"""
    
    with open("start_bot.py", "w") as f:
        f.write(startup_script)
    
    os.chmod("start_bot.py", 0o755)
    print("✅ Bot startup script created: start_bot.py")

def show_next_steps():
    """Show what Johan needs to do next"""
    print("\n🎯 NEXT STEPS FOR JOHAN")
    print("-" * 40)
    
    print("1. GET YOUR OPENAI API KEY (2 minutes):")
    print("   • Go to: https://platform.openai.com/api-keys")
    print("   • Create a new API key")
    print("   • Copy the key (starts with 'sk-')")
    print()
    
    print("2. GET YOUR TELEGRAM BOT TOKEN (3 minutes):")
    print("   • Message @BotFather on Telegram")
    print("   • Send: /newbot")
    print("   • Choose a name: 'Becoming One AI'")
    print("   • Choose a username: 'becoming_one_ai_bot' (or similar)")
    print("   • Copy the bot token")
    print()
    
    print("3. UPDATE YOUR .env FILE (1 minute):")
    print("   • Open: .env in a text editor")
    print("   • Replace 'sk-your-openai-key-here' with your OpenAI key")
    print("   • Replace 'your-telegram-bot-token-here' with your bot token")
    print("   • Save the file")
    print()
    
    print("4. START YOUR AI MENTOR BOT:")
    print("   • Run: python3 start_bot.py")
    print("   • Find your bot on Telegram and send /start")
    print("   • Begin conversations with your AI mentor!")
    print()
    
    print("🎉 TOTAL TIME: ~6 minutes to live AI mentorship system!")

def show_system_capabilities():
    """Show what the deployed system can do"""
    print("\n🌟 YOUR AI SYSTEM CAPABILITIES")
    print("-" * 40)
    
    print("✅ BECOMING ONE™ METHODOLOGY:")
    print("   • Emotional anchor recognition and processing")
    print("   • Journey stage detection (discovery → mastery)")
    print("   • Personalized guidance based on your 20 Schaubilder")
    print("   • Procrastination treated as portal, not problem")
    print()
    
    print("✅ TECHNICAL FEATURES:")
    print("   • Cross-platform identity management")
    print("   • Complete conversation history and context")
    print("   • Professional error handling and logging")
    print("   • Scalable architecture for thousands of users")
    print()
    
    print("✅ BUSINESS READY:")
    print("   • Premium Essence Coach service framework")
    print("   • Corporate Resilience OS foundation")
    print("   • Revenue tracking and analytics")
    print("   • Facilitator co-pilot capabilities")
    print()
    
    print("🚀 IMMEDIATE OPPORTUNITIES:")
    print("   • Launch €97/month Essence Coach service")
    print("   • Offer corporate transformation demos")
    print("   • Scale to thousands of users instantly")
    print("   • Generate revenue within days, not months")

def main():
    print_header()
    
    # Create development environment
    create_development_env()
    
    # Create startup script
    create_startup_script()
    
    # Show system capabilities
    show_system_capabilities()
    
    # Show next steps
    show_next_steps()
    
    print("\n" + "="*60)
    print("🎉 MINIMAL DEPLOYMENT COMPLETE")
    print("="*60)
    print("Your Becoming One™ AI system is ready for API keys!")
    print("Add OpenAI + Telegram keys → Launch in 6 minutes!")

if __name__ == "__main__":
    main()
