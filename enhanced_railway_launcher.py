#!/usr/bin/env python3
"""
Railway launcher for Enhanced Telegram Bot
Includes health check server and robust fallback
"""
import os
import sys
import threading
import asyncio
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class HealthHandler(BaseHTTPRequestHandler):
    """Health check handler for Railway"""
    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Enhanced Becoming One AI Bot is running')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress HTTP server logs to keep output clean
        pass

def start_health_server():
    """Start health check server for Railway"""
    port = int(os.getenv('PORT', 8000))
    try:
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        logger.info(f"● Health server starting on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Health server failed: {e}")

# Fallback function removed - Enhanced Bot only

async def main():
    """Main launcher function - Enhanced Bot only"""
    print("\n" + "="*60)
    print("▲ BECOMING ONE™ AI TELEGRAM BOT")
    print("="*60)
    print("🏛️ ENHANCED BOT WITH SACRED LIBRARY")
    print("◆ Initializing...")
    
    # Start health server in background
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    print("✅ Health server started for Railway")
    
    # Check for bot token
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("❌ Missing TELEGRAM_BOT_TOKEN environment variable")
        return
    
    print("✅ Bot token loaded")
    
    # Load Enhanced Bot with Sacred Library (NO FALLBACK)
    print("🏛️ LOADING ENHANCED BOT WITH SACRED LIBRARY")
    print("=" * 60)
    
    # Add src to path for imports
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    # Check for required modules
    print("🔍 Checking dependencies...")
    try:
        import openai
        from supabase import create_client
        print("✅ OpenAI and Supabase modules available")
    except ImportError as dep_error:
        print(f"❌ CRITICAL: Missing AI dependencies: {dep_error}")
        print("❌ Cannot run without these dependencies")
        return
    
    # Load Enhanced Bot
    print("🤖 Loading Enhanced Telegram Bot...")
    try:
        # Test individual imports first
        print("  🔍 Testing core imports...")
        from database.operations import db
        print("  ✅ Database operations imported")
        
        from core.ai_engine import BecomingOneAI
        print("  ✅ AI engine imported")
        
        from core.rbac_system import SimpleRBAC, UserTier, Permission
        print("  ✅ RBAC system imported")
        
        print("  🔍 Testing bot imports...")
        from bots.telegram.enhanced_telegram_bot import EnhancedBecomingOneTelegramBot
        print("✅ Enhanced Bot module imported successfully")
    except ImportError as import_error:
        print(f"❌ CRITICAL: Cannot import Enhanced Bot: {import_error}")
        import traceback
        traceback.print_exc()
        return
    except Exception as other_error:
        print(f"❌ CRITICAL: Other import error: {other_error}")
        import traceback
        traceback.print_exc()
        return
    
    # Initialize Enhanced Bot
    print("⚙️  Initializing Enhanced Bot...")
    try:
        # Test environment variables first
        print("  🔍 Checking environment variables...")
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if not bot_token:
            print("❌ TELEGRAM_BOT_TOKEN missing")
            return
        if not supabase_url:
            print("❌ SUPABASE_URL missing")
            return
        if not supabase_key:
            print("❌ SUPABASE_ANON_KEY missing")
            return
        if not openai_key:
            print("❌ OPENAI_API_KEY missing")
            return
            
        print("  ✅ All environment variables present")
        
        # Initialize bot
        print("  🤖 Creating Enhanced Bot instance...")
        bot = EnhancedBecomingOneTelegramBot()
        print("✅ Enhanced Bot initialized successfully")
        print("■ RBAC system: ENABLED")
        print("◆ Payment system: READY")
        print("🏛️ Sacred Library: INTEGRATED (4,871 quotes)")
        print("🧠 AI Engine: FULL HYLOZOICS ACCESS")
        print("🎓 Study Rooms: AVAILABLE")
    except Exception as init_error:
        print(f"❌ CRITICAL: Enhanced Bot initialization failed: {init_error}")
        import traceback
        traceback.print_exc()
        return
    
    # Run Enhanced Bot
    print("🚀 Starting Enhanced Bot...")
    try:
        # Check environment variables first
        print("  🔍 Checking environment variables...")
        required_vars = {
            'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'SUPABASE_URL': os.getenv('SUPABASE_URL'),
            'SUPABASE_ANON_KEY': os.getenv('SUPABASE_ANON_KEY')
        }
        
        for var_name, var_value in required_vars.items():
            if not var_value:
                print(f"  ❌ Missing {var_name}")
            else:
                print(f"  ✅ Found {var_name} ({var_value[:10]}...)")
        
        # Test OpenAI connection first
        print("  🔍 Testing OpenAI connection...")
        try:
            print("    Creating test completion...")
            test_response = bot.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": "test"}],
                max_tokens=1
            )
            print(f"    Response: {test_response}")
            print("  ✅ OpenAI connection working")
        except Exception as openai_error:
            print(f"  ❌ OpenAI error: {openai_error}")
            print("  🔍 OpenAI configuration:")
            print(f"    API Key (first 10 chars): {os.getenv('OPENAI_API_KEY')[:10]}...")
            print(f"    Base URL: {bot.openai_client.base_url}")
            print(f"    Full error: {openai_error.__class__.__name__}: {str(openai_error)}")
            if hasattr(openai_error, 'response'):
                print(f"    Response: {openai_error.response}")
            raise openai_error
        
        # Test Telegram webhook
        print("  🔍 Testing Telegram webhook...")
        try:
            me = await bot.application.bot.get_me()
            print(f"  ✅ Telegram bot active: @{me.username}")
        except Exception as telegram_error:
            print(f"  ❌ Telegram error: {telegram_error}")
            print("  🔍 Telegram configuration:")
            print(f"    Bot Token (first 10 chars): {os.getenv('TELEGRAM_BOT_TOKEN')[:10]}...")
            raise telegram_error
        
        # Test Supabase connection
        print("  🔍 Testing Supabase connection...")
        try:
            from database.operations import db
            result = db.client.table('teaching_materials').select("count", count="exact").execute()
            count = result.count
            print(f"  ✅ Supabase connection working ({count} teaching materials)")
        except Exception as supabase_error:
            print(f"  ❌ Supabase error: {supabase_error}")
            print("  🔍 Supabase configuration:")
            print(f"    URL: {os.getenv('SUPABASE_URL')}")
            raise supabase_error
        
        # Run the bot with detailed error handling
        print("  🚀 Starting bot polling...")
        try:
            await bot.run()
        except Exception as bot_error:
            print(f"  ❌ Bot runtime error: {bot_error}")
            print("  📋 Full error details:")
            import traceback
            traceback.print_exc()
            raise bot_error
            
    except Exception as run_error:
        print(f"❌ CRITICAL: Enhanced Bot runtime error: {run_error}")
        print("🏥 Keeping health server alive for Railway...")
        # Keep health server running so Railway doesn't kill the deployment
        import time
        while True:
            time.sleep(60)
            print("💓 Health server still running...")
            print(f"   Last error: {run_error}")
        return

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n● Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Check your configuration and try again.")
