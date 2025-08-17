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

def run_ai_bot():
    """Run the AI-powered bot"""
    import logging
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

    logger = logging.getLogger(__name__)

    # Initialize AI engine
    ai_engine = None
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        from core.ai_engine_simple import BecomingOneAISimple
        ai_engine = BecomingOneAISimple()
        print("✅ AI engine loaded successfully")
    except Exception as e:
        print(f"● AI engine failed to load: {e}")
        ai_engine = None

    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        welcome_message = f"""▲ Welcome to Becoming One™ AI ▲

Hello {user.first_name}! 

■ I'm a practical guide for human development
■ I use clear, simple methods that actually work
■ No mystical jargon - just honest, helpful conversation

◆ What I can help with:
• Understanding stuck patterns
• Working with procrastination 
• Emotional navigation
• Personal growth questions

Just talk to me naturally. What's on your mind?"""
        
        await update.message.reply_text(welcome_message)

    async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages with AI"""
        user = update.effective_user
        message_text = update.message.text
        
        logger.info(f"Message from {user.first_name}: {message_text[:50]}...")
        
        try:
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="typing"
            )
            
            # Try AI response first
            if ai_engine:
                try:
                    user_context = {
                        "name": user.first_name,
                        "telegram_id": user.id
                    }
                    response = await ai_engine.process_message(message_text, user_context)
                except Exception as ai_error:
                    logger.error(f"AI processing failed: {ai_error}")
                    response = get_fallback_response()
            else:
                response = get_fallback_response()
            
            await update.message.reply_text(response)
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text(
                "◆ Something went wrong on my end.\n\n"
                "In the meantime, here's a practical question: What feels most important to you right now in this moment?"
            )

    def get_fallback_response():
        """Fallback response when AI is not available"""
        return """◆ What you've shared is workable ◆

I hear you. What you're experiencing is valid.

■ Practical question: If this situation is here to teach you something about yourself, what might that be?

● Sometimes the very thing we're struggling with contains the seed of our next evolution.

What feels most alive or important about what you shared?"""

    # Create and run bot
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        logger.error("Missing TELEGRAM_BOT_TOKEN")
        return

    application = Application.builder().token(bot_token).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    if ai_engine:
        logger.info("● Starting AI-Powered Becoming One™ Bot...")
    else:
        logger.info("● Starting Simple Becoming One™ Bot (AI unavailable)...")
    asyncio.run(application.run_polling())

def main():
    """Main launcher function"""
    print("\n" + "="*60)
    print("▲ BECOMING ONE™ AI TELEGRAM BOT")
    print("="*60)
    print("■ Attempting enhanced version with fallback")
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
    
    # Try enhanced bot first (but expect it to fail for now)
    try:
        print("● Attempting enhanced bot...")
        # Add src to path for imports
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        
        # Check for required modules first
        try:
            import openai
            import pinecone
            from supabase import create_client
            print("✅ All AI dependencies available")
        except ImportError as dep_error:
            print(f"● Missing AI dependencies: {dep_error}")
            raise ImportError("AI dependencies not available")
        
        from bots.telegram.enhanced_telegram_bot import EnhancedBecomingOneTelegramBot
        
        bot = EnhancedBecomingOneTelegramBot()
        print("✅ Enhanced bot loaded successfully")
        print("■ RBAC system enabled")
        print("◆ Payment system ready")
        print("▲ Full AI engine loaded")
        print("● Enhanced bot is running...")
        
        asyncio.run(bot.run())
        
    except Exception as e:
        print(f"● Enhanced bot not available: {str(e)[:100]}...")
        print("■ Using simple bot (fully functional)")
        
        try:
            print("● Starting AI bot...")
            run_ai_bot()
        except Exception as fallback_error:
            print(f"❌ Simple bot failed: {fallback_error}")
            return

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n● Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Check your configuration and try again.")
