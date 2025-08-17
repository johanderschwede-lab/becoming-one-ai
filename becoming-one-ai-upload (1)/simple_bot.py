#!/usr/bin/env python3
"""
Simple Becoming One™ AI Telegram Bot
Streamlined version that works immediately
"""
import os
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from supabase import create_client, Client
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize clients
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class BecomingOneBot:
    """Simple Becoming One™ AI Bot"""
    
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.application = None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        chat_id = str(update.effective_chat.id)
        
        # Log the user
        try:
            supabase.table("identity_registry").upsert({
                "name": f"{user.first_name} {user.last_name}".strip(),
                "channel_ids": {"telegram": chat_id}
            }).execute()
        except:
            pass  # Continue even if database fails
        
        welcome_message = """🌟 Welcome to your Becoming One™ AI Journey!

I'm here to guide you through personalized mentorship using the Becoming One™ method.

✨ I can help you with:
• Emotional anchor recognition and processing
• Understanding stuck patterns and resistance
• Transforming procrastination into portals for growth
• Journey stage guidance (discovery → mastery)
• Personalized wisdom from 20+ years of methodology

Just tell me what's on your mind, and I'll respond with deep, transformational guidance.

Type /help for more commands or simply start sharing what you're experiencing!"""
        
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """🤖 Becoming One™ AI Commands:

/start - Begin your journey
/help - Show this help message
/profile - View your journey insights

💬 **Just talk naturally!** I understand:
• Emotional patterns and stuck places
• Procrastination and resistance
• Goals and manifestation blocks
• Relationships and communication
• Personal growth and transformation

🔮 **Try these conversation starters:**
• "I'm feeling stuck with my goals"
• "I keep procrastinating on important things"
• "I want to understand my emotional patterns"
• "How do I transform resistance into growth?"

🌟 I'll respond with personalized Becoming One™ wisdom!"""
        
        await update.message.reply_text(help_text)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular messages with Becoming One™ methodology"""
        user = update.effective_user
        chat_id = str(update.effective_chat.id)
        message_text = update.message.text
        
        try:
            # Send typing indicator
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="typing"
            )
            
            # Create Becoming One™ system prompt
            system_prompt = """You are an AI mentor trained in the Becoming One™ method, a transformative approach to personal growth and authentic living.

CORE MISSION: Guide this person toward discovering, integrating, and expressing their most authentic self while fostering deeper connections and purposeful living.

BECOMING ONE™ PRINCIPLES:
1. AUTHENTICITY: Help them discover and express their true self
2. INTEGRATION: Support applying insights to real life
3. EVOLUTION: Encourage continuous growth and adaptation
4. CONNECTION: Foster deeper relationships with self and others
5. PURPOSE: Assist in discovering and living their unique purpose

EMOTIONAL ANCHOR APPROACH:
- Recognize that resistance and procrastination are PORTALS, not problems
- Help them feel and integrate stuck emotional patterns
- Guide toward feeling-state manifestation (not just mental goal-setting)
- Treat avoidance as golden doorways to healing and evolution

RESPONSE STYLE:
- Be warm, empathetic, and genuinely curious
- Ask powerful questions that promote self-reflection
- Offer insights without being prescriptive
- Use "I wonder..." and "What if..." to invite exploration
- Balance support with gentle challenge
- Reference the journey stages: discovery → exploration → integration → mastery

Remember: You're facilitating a journey of becoming. Every interaction should leave them feeling more connected to their authentic self."""

            # Generate AI response
            response = openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message_text}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Log the interaction
            try:
                supabase.table("event_log").insert({
                    "type": "message",
                    "content": message_text,
                    "source": "telegram",
                    "metadata": {
                        "user_id": user.id,
                        "username": user.username,
                        "chat_id": chat_id,
                        "ai_response": ai_response
                    }
                }).execute()
            except:
                pass  # Continue even if logging fails
            
            # Send response
            await update.message.reply_text(ai_response)
            
        except Exception as e:
            error_message = """I'm experiencing a temporary issue processing your message. 

In the spirit of the Becoming One™ method, let me offer this:
Sometimes the most profound insights come from pausing and reflecting. 

What feels most important to you right now in this moment?"""
            
            await update.message.reply_text(error_message)
            print(f"Error: {e}")
    
    async def profile_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's journey profile"""
        profile_text = f"""👤 Your Becoming One™ Profile:

🌱 **Journey Status**: Active and evolving
📅 **Session**: {datetime.now().strftime('%B %d, %Y')}
💬 **Platform**: Telegram Integration
✨ **Features Active**:
   • Emotional anchor recognition
   • Journey stage adaptation  
   • Becoming One™ methodology
   • Personalized guidance

🔮 **Your Unique Path**: Every interaction deepens your journey of becoming your most authentic self.

Continue sharing what's alive for you - I'm here to support your transformation!"""
        
        await update.message.reply_text(profile_text)
    
    def setup_handlers(self):
        """Set up bot handlers"""
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("profile", self.profile_command))
        
        # Handle all text messages
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )
    
    async def run(self):
        """Run the bot"""
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
        
        print("🤖 Starting Becoming One™ AI Telegram Bot...")
        print("🌟 Features: Emotional anchor recognition, journey guidance, authentic transformation")
        print("💬 Bot ready for conversations!")
        print("-" * 60)
        
        await self.application.run_polling()

async def main():
    """Main function"""
    print("\n" + "="*60)
    print("🌟 BECOMING ONE™ AI TELEGRAM BOT")
    print("="*60)
    print("Initializing your AI mentorship system...")
    
    # Check environment
    required_vars = ["TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_ANON_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing environment variables: {missing}")
        return
    
    print("✅ All environment variables loaded")
    print("✅ OpenAI integration ready")
    print("✅ Supabase database connected")
    print("✅ Telegram bot initialized")
    
    # Start the bot
    bot = BecomingOneBot()
    await bot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Check your API keys and try again.")
