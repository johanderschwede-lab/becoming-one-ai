#!/usr/bin/env python3
"""
Notification System Setup

This script helps you configure notifications for your Compass system.
You'll get alerts when content is added to your master prompt.
"""

import os
import sys
from dotenv import load_dotenv

def setup_telegram_notifications():
    """Setup Telegram notifications"""
    print("\n📱 TELEGRAM NOTIFICATIONS SETUP")
    print("="*40)
    
    # Check if already configured
    if os.getenv("TELEGRAM_BOT_TOKEN") and os.getenv("TELEGRAM_CHAT_ID"):
        print("✅ Telegram notifications already configured!")
        return True
    
    print("To get Telegram notifications, you need:")
    print("1. A Telegram bot token")
    print("2. Your personal chat ID")
    
    choice = input("\nWould you like to configure Telegram notifications? (y/n): ").lower()
    if choice != 'y':
        return False
    
    print("\n📋 SETUP STEPS:")
    print("1. Create a bot with @BotFather on Telegram")
    print("2. Get your bot token")
    print("3. Start a chat with your bot")
    print("4. Get your chat ID by sending /start to your bot")
    print("5. Visit: https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates")
    print("6. Find your chat_id in the response")
    
    bot_token = input("\nEnter your bot token: ").strip()
    chat_id = input("Enter your chat ID: ").strip()
    
    if bot_token and chat_id:
        # Add to .env file
        env_file = ".env"
        with open(env_file, "a") as f:
            f.write(f"\n# Telegram Notifications\n")
            f.write(f"TELEGRAM_BOT_TOKEN={bot_token}\n")
            f.write(f"TELEGRAM_CHAT_ID={chat_id}\n")
        
        print("✅ Telegram notifications configured!")
        return True
    else:
        print("❌ Configuration incomplete")
        return False

def setup_email_notifications():
    """Setup email notifications"""
    print("\n📧 EMAIL NOTIFICATIONS SETUP")
    print("="*40)
    
    # Check if already configured
    if os.getenv("EMAIL_NOTIFICATIONS") == "true":
        print("✅ Email notifications already configured!")
        return True
    
    choice = input("\nWould you like to configure email notifications? (y/n): ").lower()
    if choice != 'y':
        return False
    
    print("\n📋 EMAIL SETUP:")
    print("For Gmail, you'll need an App Password")
    print("1. Enable 2-factor authentication")
    print("2. Generate an App Password")
    print("3. Use that password below")
    
    email_user = input("\nEnter your email address: ").strip()
    email_password = input("Enter your app password: ").strip()
    email_recipient = input("Enter recipient email (same as above): ").strip()
    
    if email_user and email_password and email_recipient:
        # Add to .env file
        env_file = ".env"
        with open(env_file, "a") as f:
            f.write(f"\n# Email Notifications\n")
            f.write(f"EMAIL_NOTIFICATIONS=true\n")
            f.write(f"EMAIL_USER={email_user}\n")
            f.write(f"EMAIL_PASSWORD={email_password}\n")
            f.write(f"EMAIL_RECIPIENT={email_recipient}\n")
        
        print("✅ Email notifications configured!")
        return True
    else:
        print("❌ Configuration incomplete")
        return False

def test_notifications():
    """Test the notification system"""
    print("\n🧪 TESTING NOTIFICATIONS")
    print("="*40)
    
    try:
        from notification_system import NotificationSystem
        
        notifier = NotificationSystem()
        results = notifier.test_notifications()
        
        print(f"Telegram test: {'✅' if results['telegram'] else '❌'}")
        print(f"Email test: {'✅' if results['email'] else '❌'}")
        
        if results['telegram'] or results['email']:
            print("\n🎉 Notification system is working!")
            return True
        else:
            print("\n⚠️  No notifications sent. Check your configuration.")
            return False
            
    except Exception as e:
        print(f"❌ Error testing notifications: {e}")
        return False

def show_notification_status():
    """Show current notification status"""
    print("\n📊 NOTIFICATION STATUS")
    print("="*40)
    
    # Check Telegram
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat = os.getenv("TELEGRAM_CHAT_ID")
    
    print(f"Telegram: {'✅ Configured' if telegram_token and telegram_chat else '❌ Not configured'}")
    
    # Check Email
    email_enabled = os.getenv("EMAIL_NOTIFICATIONS") == "true"
    email_user = os.getenv("EMAIL_USER")
    
    print(f"Email: {'✅ Configured' if email_enabled and email_user else '❌ Not configured'}")
    
    if not telegram_token and not email_enabled:
        print("\n⚠️  No notifications configured!")
        print("You won't receive alerts when content is added to your master prompt.")

def main():
    """Main setup function"""
    load_dotenv()
    
    print("🔔 COMPASS NOTIFICATION SYSTEM SETUP")
    print("="*50)
    print("This will help you get notified when content is added to your master prompt.")
    
    while True:
        print("\nOptions:")
        print("1. 📱 Setup Telegram notifications")
        print("2. 📧 Setup Email notifications")
        print("3. 🧪 Test notifications")
        print("4. 📊 Show notification status")
        print("5. 🚪 Exit")
        
        choice = input("\nSelect an option (1-5): ").strip()
        
        if choice == "1":
            setup_telegram_notifications()
        elif choice == "2":
            setup_email_notifications()
        elif choice == "3":
            test_notifications()
        elif choice == "4":
            show_notification_status()
        elif choice == "5":
            print("\n👋 Setup complete!")
            break
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    main()
