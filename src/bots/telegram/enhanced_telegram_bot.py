"""
Enhanced Telegram Bot for Becoming One™ AI Journey System
Integrates RBAC, Sacred Library, and Advanced Features
"""
import os
import asyncio
import uuid
from typing import Optional, Dict, Any
from datetime import datetime
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from loguru import logger

from database.operations import db
from core.ai_engine import BecomingOneAI
from core.rbac_system import SimpleRBAC, UserTier, Permission

class EnhancedBecomingOneTelegramBot:
    """Enhanced Telegram bot with RBAC and Sacred Library"""
    
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN must be set")
        
        self.ai_engine = BecomingOneAI()
        self.rbac = SimpleRBAC()
        self.application = None
        
        logger.info("Enhanced Telegram Bot initialized")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """▲ Welcome to your Becoming One™ AI Journey!

I'm here to guide you through personalized mentorship using the Becoming One™ method.

■ **I can help you with:**
• Emotional anchor recognition and processing
• Understanding stuck patterns and resistance  
• Transforming procrastination into portals for growth
• Journey stage guidance (discovery → mastery)
• Sacred Library wisdom from Hylozoics

**Just tell me what's on your mind!** I'll respond with deep, transformational guidance.

Try: "I'm feeling stuck with my goals" or "Tell me about consciousness"

Type /help for more commands!"""
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """■ **Available Commands:**

/start - Begin your journey
/help - Show this help message
/sacred <term> - Search Sacred Library
/browse_sacred - Browse teachings
/study - Enter Hylozoic study mode

💬 **Just talk naturally!** I understand:
• Emotional patterns and stuck places
• Questions about consciousness and reality
• Personal growth and transformation
• Hylozoic teachings and wisdom

◆ **Try these conversation starters:**
• "What is consciousness?"
• "Tell me about emotional development"
• "How do I understand my patterns?"
• "What does Laurency say about..."

▲ **I'll respond with personalized wisdom and authentic teachings!**"""
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages with AI responses"""
        try:
            print("📨 Received message...")
            
        user = update.effective_user
        chat_id = str(update.effective_chat.id)
            message_text = update.message.text if update.message.text else ""
            
            print(f"  👤 From: {user.first_name} (ID: {user.id})")
            print(f"  💬 Message: {message_text[:50]}...")
            
            if not message_text:
                print("  ⚠️ Empty message, ignoring")
                return
            
            # Send typing indicator
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="typing"
            )
            
            # Process with AI engine
            response = await self.ai_engine.process_message(
                person_id=str(uuid.uuid4()),  # Temporary ID
                message=message_text,
                source="telegram",
                user_tier="premium"  # Full access for now
            )
            
            # Send response
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text(
                "■ I encountered an issue processing your message. Please try again in a moment."
            )
    
    def setup_handlers(self):
        """Set up all bot handlers"""
        print("📝 Setting up handlers...")
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        print("✅ Command handlers added")
        
        # Message handler
        self.application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND,
                self.handle_message,
                block=False
        )
        )
        print("✅ Message handler added")
    
    async def run(self):
        """Run the enhanced bot"""
        print("🚀 Starting bot application...")
        try:
            print("  🔧 Building application...")
        self.application = Application.builder().token(self.token).build()
            print("  ✅ Application built")
            
            print("  📝 Setting up handlers...")
        self.setup_handlers()
            print("  ✅ Handlers set up")
            
            print("  ▶️ Starting polling...")
            print("  📋 Configuration:")
            print(f"    Token (first 10): {self.token[:10]}...")
            
            logger.info("▲ Starting Becoming One™ Telegram Bot...")
            await self.application.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True
            )
        except Exception as e:
            print(f"❌ Error in run(): {e}")
            print("📋 Full error details:")
            import traceback
            traceback.print_exc()
            raise e