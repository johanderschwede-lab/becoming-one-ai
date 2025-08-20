"""
Telegram Bot for Becoming One™ AI Journey System
Integrates with Make.com webhooks and Supabase
"""
import os
import asyncio
from typing import Optional, Dict, Any
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from loguru import logger

from ...database.operations import db
from ...core.ai_engine import BecomingOneAI
from ...integrations.make_webhooks import MakeWebhookClient


class BecomingOneTelegramBot:
    """Telegram bot implementation"""
    
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN must be set")
        
        self.ai_engine = BecomingOneAI()
        self.make_client = MakeWebhookClient()
        self.application = None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        chat_id = str(update.effective_chat.id)
        
        # Get or create person_id
        person_id = await db.get_or_create_person_id(
            channel_type="telegram",
            channel_id=chat_id,
            name=f"{user.first_name} {user.last_name}".strip()
        )
        
        # Log the start event
        await db.log_event(
            person_id=person_id,
            event_type="command",
            content="/start",
            source="telegram",
            metadata={"user_id": user.id, "username": user.username}
        )
        
        welcome_message = """
🌟 Welcome to your Becoming One™ AI Journey!

I'm here to guide you through personalized mentorship using the Becoming One™ method. 

To get started:
• Share what's on your mind or ask any question
• I'll learn your preferences and adapt my guidance
• All conversations are logged to provide continuous, personalized support

Type /help for more commands or just start talking with me!

✨ Your journey of becoming begins now.
        """.strip()
        
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🤖 Becoming One™ AI Commands:

/start - Begin your journey
/help - Show this help message
/profile - View your journey profile
/consent - Manage data consent
/reset - Start fresh (clears history)

💬 Just message me naturally - I understand context and will guide you through the Becoming One™ method!

🔒 Privacy: Your conversations are securely stored to provide personalized guidance.
        """.strip()
        
        await update.message.reply_text(help_text)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages"""
        user = update.effective_user
        chat_id = str(update.effective_chat.id)
        message_text = update.message.text
        
        try:
            # Get person_id
            person_id = await db.get_or_create_person_id(
                channel_type="telegram",
                channel_id=chat_id,
                name=f"{user.first_name} {user.last_name}".strip()
            )
            
            # Log the incoming message
            await db.log_event(
                person_id=person_id,
                event_type="message",
                content=message_text,
                source="telegram",
                metadata={
                    "user_id": user.id,
                    "username": user.username,
                    "chat_id": chat_id
                }
            )
            
            # Send typing indicator
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="typing"
            )
            
            # Process with AI engine
            response = await self.ai_engine.process_message(
                person_id=person_id,
                message=message_text,
                source="telegram"
            )
            
            # Log the response
            await db.log_event(
                person_id=person_id,
                event_type="response",
                content=response,
                source="telegram",
                metadata={"ai_generated": True}
            )
            
            # Send response
            await update.message.reply_text(response)
            
            # Trigger Make.com webhook if configured
            await self.make_client.trigger_message_webhook({
                "person_id": str(person_id),
                "message": message_text,
                "response": response,
                "source": "telegram",
                "user_info": {
                    "telegram_id": user.id,
                    "username": user.username,
                    "name": f"{user.first_name} {user.last_name}".strip()
                }
            })
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text(
                "I encountered an issue processing your message. Please try again in a moment."
            )
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's profile"""
        chat_id = str(update.effective_chat.id)
        
        person_id = await db.get_or_create_person_id(
            channel_type="telegram",
            channel_id=chat_id
        )
        
        profile = await db.get_user_profile(person_id)
        history_count = len(await db.get_user_history(person_id, limit=1000))
        
        profile_text = f"""
👤 Your Becoming One™ Profile:

🆔 Person ID: {str(person_id)[:8]}...
📅 Member since: {profile['created_at'][:10] if profile else 'Today'}
💬 Total interactions: {history_count}
✅ Data consent: {'Yes' if profile and profile['consent'] else 'No'}

🌱 Your journey is unique and evolving with each interaction.
        """.strip()
        
        await update.message.reply_text(profile_text)
    
    async def consent_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle consent management"""
        chat_id = str(update.effective_chat.id)
        
        person_id = await db.get_or_create_person_id(
            channel_type="telegram",
            channel_id=chat_id
        )
        
        consent_text = """
🔒 Data Consent for Becoming One™ AI:

Your conversations help me provide personalized guidance. I store:
• Your messages and my responses
• Interaction patterns and preferences
• Journey progress and insights

Type "I consent" to enable full personalization.
Type "withdraw consent" to limit data usage.

Current status will be shown after your choice.
        """.strip()
        
        await update.message.reply_text(consent_text)
    
    def setup_handlers(self):
        """Set up bot handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("profile", self.profile_command))
        self.application.add_handler(CommandHandler("consent", self.consent_command))
        
        # Handle all text messages
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
    
    async def run(self):
        """Run the bot"""
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
        
        logger.info("Starting Becoming One™ Telegram Bot...")
        await self.application.run_polling()


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    bot = BecomingOneTelegramBot()
    asyncio.run(bot.run())
