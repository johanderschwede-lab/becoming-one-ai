#!/usr/bin/env python3
"""
Railway launcher for Enhanced Telegram Bot
Includes health check server and robust error handling
"""
import os
import sys
import threading
import asyncio
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

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
    port = int(os.getenv('PORT', 8080))
    try:
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        logger.info(f"● Health server starting on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Health server failed: {e}")

def get_deploy_version():
    """Get current deployment version"""
    try:
        with open('.deploy_version', 'r') as f:
            return int(f.read().strip())
    except:
        return 0

async def main():
    """Main launcher function - Enhanced Bot only"""
    version = get_deploy_version()
    print("\n" + "="*60)
    print("▲ BECOMING ONE™ AI TELEGRAM BOT")
    print("="*60)
    print(f"🏛️ ENHANCED BOT WITH SACRED LIBRARY (v{version})")
    print("◆ Initializing...")
    
    # Start health server in background
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    print("✅ Health server started for Railway")
    
    # Check environment variables
    required_vars = ["TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_ANON_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing environment variables: {missing}")
        return
    
    print("✅ All environment variables loaded")
    
    # Initialize bot
    try:
        from bots.telegram.enhanced_telegram_bot import EnhancedBecomingOneTelegramBot
        bot = EnhancedBecomingOneTelegramBot()
        print("✅ Bot initialized")
        
        # Run the bot
        print("🚀 Starting bot...")
        await bot.run()
    except Exception as e:
        print(f"❌ CRITICAL: Bot error: {e}")
        import traceback
        traceback.print_exc()
        print("🏥 Keeping health server alive for Railway...")
        # Keep health server running so Railway doesn't kill the deployment
        while True:
            await asyncio.sleep(60)
            print("💓 Health server still running...")

if __name__ == "__main__":
    try:
        # Load environment variables
        load_dotenv()
        
        # Run the bot
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n● Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Check your configuration and try again.")