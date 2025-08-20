from telebot import TeleBot
import httpx
from typing import Optional
from pydantic_settings import BaseSettings

class BotSettings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    API_URL: str = "http://localhost:8000"
    API_KEY: str = "internal"
    class Config:
        env_file = ".env"

settings = BotSettings()
bot = TeleBot(settings.TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['idea'])
def handle_idea(msg):
    """Handle /idea command - submit new ideas to the proposal system"""
    # Extract text after command
    text = msg.text.split(' ', 1)[1] if ' ' in msg.text else ''
    
    if not text:
        bot.reply_to(msg, "Please provide an idea after the command, like: /idea My brilliant idea")
        return

    # Prepare proposal payload
    payload = {
        "submitted_by": str(msg.from_user.id),
        "source": "telegram",
        "raw_idea": text,
        "normalized": {
            "target_section": "parked_ideas",
            "change_type": "add",
            "patch": {"text": text},
            "impact": "low"
        }
    }

    # Submit to API
    try:
        response = httpx.post(
            f"{settings.API_URL}/proposals",
            json=payload,
            headers={"Authorization": f"Bearer {settings.API_KEY}"},
            timeout=10.0
        )
        response.raise_for_status()
        bot.reply_to(msg, "✅ Noted. Logged as a proposal.")
    except Exception as e:
        bot.reply_to(msg, f"❌ Sorry, couldn't save your idea right now. Please try again later.")
        print(f"Error submitting proposal: {e}")

def run_bot():
    """Run the bot in polling mode"""
    print(f"Starting Telegram bot...")
    bot.infinity_polling()

