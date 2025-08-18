#!/usr/bin/env python3
"""
Ultra-simple working Telegram bot
No complexity, just works
"""
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hello! I am your Becoming One™ AI assistant. How can I help you today?')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text("""
🏛️ Becoming One™ AI Assistant

Available commands:
/start - Start conversation
/help - Show this help

I'm here to help with your personal development journey using the Becoming One™ method.
""")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the user message with a simple response."""
    user_message = update.message.text
    
    # Simple AI-like response
    response = f"""Thank you for sharing: "{user_message}"

I'm here to support your journey of authentic self-discovery. What would you like to explore about yourself today?

This is a basic response while we complete the full Sacred Library integration."""
    
    await update.message.reply_text(response)

def main():
    """Start the bot."""
    # Get token from environment
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not found!")
        print("Set it in Railway environment variables")
        return
    
    print(f"🤖 Starting simple bot with token: {token[:10]}...")
    
    # Create the Application
    application = Application.builder().token(token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("✅ Bot configured, starting polling...")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
