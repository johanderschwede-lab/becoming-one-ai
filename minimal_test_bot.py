#!/usr/bin/env python3
"""
Minimal test bot to isolate the issue
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("🤖 Starting minimal test bot...")
    
    try:
        from telegram import Bot, Update
        from telegram.ext import Application, MessageHandler, filters
        
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        print(f"Token: {token[:10]}...")
        
        # Create application
        app = Application.builder().token(token).build()
        
        async def echo(update: Update, context):
            """Simple echo handler"""
            await update.message.reply_text(f"Echo: {update.message.text}")
        
        # Add handler
        app.add_handler(MessageHandler(filters.TEXT, echo))
        
        print("✅ Starting polling...")
        # Use run_polling without asyncio.run
        app.run_polling(drop_pending_updates=True)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()