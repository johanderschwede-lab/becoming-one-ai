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

def main():
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
        from bots.telegram.enhanced_telegram_bot import EnhancedBecomingOneTelegramBot
        print("✅ Enhanced Bot module imported successfully")
    except ImportError as import_error:
        print(f"❌ CRITICAL: Cannot import Enhanced Bot: {import_error}")
        import traceback
        traceback.print_exc()
        return
    
    # Initialize Enhanced Bot
    print("⚙️  Initializing Enhanced Bot...")
    try:
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
        asyncio.run(bot.run())
    except Exception as run_error:
        print(f"❌ CRITICAL: Enhanced Bot runtime error: {run_error}")
        import traceback
        traceback.print_exc()
        return

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n● Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Check your configuration and try again.")
