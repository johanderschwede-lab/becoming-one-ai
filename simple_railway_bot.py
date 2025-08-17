#!/usr/bin/env python3
"""
Simple Becoming One™ AI Telegram Bot for Railway Deployment
Minimal version without external database dependencies
"""
import os
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class HealthHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler for Railway health checks"""
    def do_GET(self):
        if self.path == '/health' or self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Becoming One™ AI Bot is running')
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress HTTP server logs to keep output clean
        pass

def start_health_server():
    """Start HTTP health check server for Railway"""
    port = int(os.getenv('PORT', 8000))
    try:
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        logger.info(f"● Health server starting on port {port}")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Health server failed: {e}")

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

Just talk to me naturally. What's on your mind?

Type /help for more options."""
    
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """● Becoming One™ AI Commands:

/start - Begin conversation
/help - Show this message
/about - Learn about our approach

◆ How to use:
Just talk naturally! Share what you're experiencing, what you're stuck on, or what you're curious about.

Examples:
• "I keep procrastinating on important things"
• "I'm feeling stuck in my relationships"
• "How do I handle difficult emotions?"

■ Our approach:
We meet you exactly where you are, without judgment. Every challenge is a doorway to growth when approached with the right methods."""
    
    await update.message.reply_text(help_text)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /about command"""
    about_text = """▲ About Becoming One™

We're two humans who've discovered practical methods for personal development that actually work.

■ Our Philosophy:
• Clear, simple language (no mystical jargon)
• Meet people where they are
• Practical methods over theory
• Human connection, not guru worship
• Honest about limitations

◆ What makes this different:
Instead of avoiding difficult feelings, we've learned to work WITH them. Every "problem" becomes a doorway when you know how to approach it.

● Ready to explore what might be useful for you?"""
    
    await update.message.reply_text(about_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages with simple responses"""
    user = update.effective_user
    message_text = update.message.text
    
    logger.info(f"Message from {user.first_name}: {message_text[:50]}...")
    
    try:
        # Send typing indicator
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        # Simple response logic (no AI for now)
        response = generate_simple_response(message_text)
        
        # Send response
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        error_message = """◆ Something went wrong on my end.

In the meantime, here's a practical question: What feels most important to you right now in this moment?

Sometimes the most profound insights come from simply pausing and noticing what's actually present."""
        
        await update.message.reply_text(error_message)

def generate_simple_response(message_text: str) -> str:
    """Generate simple responses based on keywords"""
    message_lower = message_text.lower()
    
    if any(word in message_lower for word in ['stuck', 'procrastination', 'procrastinating']):
        return """▲ Procrastination as Portal ▲

What you call "procrastination" might actually be your system's way of protecting you from something.

■ Practical question: What would you have to feel if you actually did this thing you're avoiding?

Often we're not avoiding the task - we're avoiding a feeling state. When you can identify what you're really avoiding, you've found your doorway."""
    
    elif any(word in message_lower for word in ['emotion', 'feeling', 'sad', 'angry', 'fear']):
        return """◆ Working with Feelings ◆

Feelings aren't problems to solve - they're information and energy.

● Try this: Instead of trying to change the feeling, can you simply be present with it for 30 seconds?

■ Notice: Where do you feel it in your body? What would happen if you didn't resist it?

The energy that's locked up in resistance often contains exactly what you need."""
    
    elif any(word in message_lower for word in ['relationship', 'communication', 'conflict']):
        return """● Human Connection ●

Real connection happens when we stop trying to be perfect and start being honest about our actual experience.

◆ Practical approach: What's one thing you haven't said because you're afraid of how they'll react?

■ The very thing we're afraid to share is often the doorway to deeper intimacy."""
    
    elif any(word in message_lower for word in ['goal', 'want', 'desire', 'dream']):
        return """▲ Beyond Goal-Setting ▲

Traditional goal-setting often fails because it focuses on external outcomes rather than internal states.

■ Different approach: What would you need to FEEL to naturally move toward what you want?

◆ The feeling-state you're seeking is available now. When you can generate it internally, external movement becomes natural."""
    
    else:
        return """◆ GitHub auth test ◆

I hear you. What you're experiencing is valid and workable.

■ Practical question: If this situation is here to teach you something about yourself, what might that be?

● Sometimes the very thing we're struggling with contains the seed of our next evolution.

What feels most alive or important about what you shared?"""

def main():
    """Main function to run the bot"""
    print("\n" + "="*60)
    print("▲ BECOMING ONE™ AI TELEGRAM BOT")
    print("="*60)
    print("■ Simple deployment version")
    print("◆ Initializing...")
    
    # Check for bot token
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("❌ Missing TELEGRAM_BOT_TOKEN environment variable")
        return
    
    print("✅ Bot token loaded")
    
    # Start health server for Railway in background thread
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    print("✅ Health server started for Railway")
    
    # Create application
    application = Application.builder().token(bot_token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("● Starting Becoming One™ AI Bot...")
    print("■ Ready for authentic conversations")
    print("◆ Bot is running... Press Ctrl+C to stop")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n● Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Check your bot token and network connection.")
