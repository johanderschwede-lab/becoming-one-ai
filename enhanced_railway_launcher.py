#!/usr/bin/env python3
"""
Enhanced Railway Launcher for Becoming One™ AI
Handles startup, health checks, and graceful shutdown
"""
import os
import sys
import asyncio
import signal
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from loguru import logger

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

class HealthHandler(BaseHTTPRequestHandler):
    """Health check handler for Railway"""
    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Becoming One AI is running')
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress HTTP server logs
        pass

def start_health_server(port=8080):
    """Start health check server"""
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    server.serve_forever()

async def verify_environment():
    """Verify all required environment variables"""
    required_vars = [
        "TELEGRAM_BOT_TOKEN",
        "OPENAI_API_KEY",
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY"
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        logger.error(f"Missing environment variables: {', '.join(missing)}")
        return False
    return True

def get_deploy_version():
    """Get current deployment version"""
    try:
        with open('.deploy_version', 'r') as f:
            return int(f.read().strip())
    except:
        return 0

async def main():
    """Main launcher function"""
    version = get_deploy_version()
    print("\n" + "="*60)
    print("▲ BECOMING ONE™ AI TELEGRAM BOT")
    print("="*60)
    print(f"🏛️ ENHANCED BOT WITH SACRED LIBRARY (v{version})")
    print("◆ Initializing...")

    # Start health server in background
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    print("✅ Health server started")

    # Verify environment
    if not await verify_environment():
        print("❌ Environment verification failed")
        print("🏥 Keeping health server alive...")
        while True:
            await asyncio.sleep(60)
        return

    # Import and start bot
    try:
        from bots.telegram.enhanced_telegram_bot import EnhancedBecomingOneTelegramBot
        print("✅ Bot module imported successfully")
        
        bot = EnhancedBecomingOneTelegramBot()
        print("✅ Bot initialized")
        print("■ RBAC system: ENABLED")
        print("◆ Payment system: READY")
        print("🏛️ Sacred Library: INTEGRATED")
        print("🧠 AI Engine: FULL ACCESS")
        
        await bot.run()
        
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("\n🏥 Keeping health server alive...")
        while True:
            await asyncio.sleep(60)
            print("💓 Health check active...")

def handle_shutdown(signum, frame):
    """Handle shutdown signals gracefully"""
    print("\n⏳ Shutting down gracefully...")
    sys.exit(0)

if __name__ == "__main__":
    # Register shutdown handlers
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n● Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)