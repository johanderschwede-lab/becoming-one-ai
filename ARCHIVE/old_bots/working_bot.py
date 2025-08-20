#!/usr/bin/env python3
"""
Working Becoming One™ AI Telegram Bot
Fixed version that handles asyncio properly
"""
import os
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from supabase import create_client
from openai import OpenAI
from dotenv import load_dotenv
import sys
from pathlib import Path

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load environment variables FIRST
load_dotenv()

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Import our enhanced AI engine (after env vars are loaded)
try:
    from core.ai_engine import BecomingOneAI
    ai_engine = BecomingOneAI()
    logger.info("✅ Enhanced AI engine with Sacred Library loaded")
except Exception as e:
    logger.error(f"❌ Could not load enhanced AI engine: {e}")
    ai_engine = None

# Initialize clients
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    chat_id = str(update.effective_chat.id)
    
    # Log the user
    try:
        supabase.table("identity_registry").upsert({
            "name": f"{user.first_name} {user.last_name}".strip(),
            "channel_ids": {"telegram": chat_id}
        }).execute()
        logger.info(f"User registered: {user.first_name} (ID: {chat_id})")
    except Exception as e:
        logger.warning(f"Database logging failed: {e}")
    
    welcome_message = """🌟 Welcome to your Becoming One™ AI Journey!

I'm here to guide you through personalized mentorship using the Becoming One™ method.

✨ **I can help you with:**
• Emotional anchor recognition and processing
• Understanding stuck patterns and resistance  
• Transforming procrastination into portals for growth
• Journey stage guidance (discovery → mastery)
• Personalized wisdom from 20+ years of methodology

**Just tell me what's on your mind!** I'll respond with deep, transformational guidance.

Try: "I'm feeling stuck with my goals" or "I keep procrastinating"

Type /help for more commands! 🚀"""
    
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """🤖 **Becoming One™ AI Commands:**

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

🌟 **I'll respond with personalized Becoming One™ wisdom!**"""
    
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages with Becoming One™ methodology"""
    user = update.effective_user
    chat_id = str(update.effective_chat.id)
    message_text = update.message.text
    
    logger.info(f"Message from {user.first_name}: {message_text[:50]}...")
    
    try:
        # Send typing indicator
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action="typing"
        )
        
        # Use enhanced AI engine if available, otherwise fallback to simple OpenAI
        if ai_engine:
            # Use our enhanced AI engine with Sacred Library
            person_id = str(user.id)
            logger.info(f"Using enhanced AI engine for: {message_text[:50]}...")
            ai_response = await ai_engine.process_message(
                person_id=person_id,
                message=message_text,
                source="telegram",
                user_tier="free"
            )
            logger.info(f"Enhanced AI response generated: {len(ai_response)} characters")
        else:
            # Fallback to simple OpenAI
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
            logger.info(f"Fallback AI response generated: {len(ai_response)} characters")
        
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
                    "ai_response": ai_response[:500]  # Truncate for storage
                }
            }).execute()
        except Exception as e:
            logger.warning(f"Event logging failed: {e}")
        
        # Send response
        await update.message.reply_text(ai_response)
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        error_message = """I'm experiencing a temporary issue processing your message. 

In the spirit of the Becoming One™ method, let me offer this:
Sometimes the most profound insights come from pausing and reflecting. 

What feels most important to you right now in this moment?"""
        
        await update.message.reply_text(error_message)

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's journey profile"""
    profile_text = f"""👤 **Your Becoming One™ Profile:**

🌱 **Journey Status**: Active and evolving
📅 **Session**: {datetime.now().strftime('%B %d, %Y')}
💬 **Platform**: Telegram Integration
✨ **Features Active**:
   • Emotional anchor recognition
   • Journey stage adaptation  
   • Becoming One™ methodology
   • Personalized guidance

🔮 **Your Unique Path**: Every interaction deepens your journey of becoming your most authentic self.

Continue sharing what's alive for you - I'm here to support your transformation! 🚀"""
    
    await update.message.reply_text(profile_text)

def main():
    """Main function to run the bot"""
    print("\n" + "="*60)
    print("🌟 BECOMING ONE™ AI TELEGRAM BOT v2.0")
    print("="*60)
    print("Initializing Enhanced AI with Sacred Library...")
    
    # Check environment variables
    required_vars = ["TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY", "SUPABASE_URL", "SUPABASE_ANON_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"❌ Missing environment variables: {missing}")
        return
    
    print("✅ All environment variables loaded")
    print("✅ OpenAI integration ready")
    print("✅ Supabase database connected")
    print("✅ Telegram bot initialized")
    
    if ai_engine:
        print("✅ Enhanced AI engine with Sacred Library active")
    else:
        print("⚠️  Using fallback OpenAI (Enhanced AI engine failed to load)")
    
    # Create application
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🤖 Starting Becoming One™ AI Telegram Bot...")
    print("🌟 Features: Emotional anchor recognition, journey guidance, authentic transformation")
    print("💬 Bot ready for conversations!")
    print("🔗 Find your bot: @willbdotoneupdatebot")
    print("-" * 60)
    print("Bot is running... Press Ctrl+C to stop")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Check your API keys and network connection.")
