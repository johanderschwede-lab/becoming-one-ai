#!/usr/bin/env python3
"""
Quick Security Check for Becoming One™ AI Journey System
Simplified version that focuses on the immediate security issues
"""
import os
import sys
from pathlib import Path
from getpass import getpass
import requests

def print_header():
    print("\n" + "="*60)
    print("🔒 BECOMING ONE™ AI - QUICK SECURITY CHECK")
    print("="*60)
    print("Immediate security assessment and credential management")
    print("-" * 60)

def show_security_status():
    """Show the current security status from ChatGPT analysis"""
    print("\n🚨 SECURITY ALERT - IMMEDIATE ACTION REQUIRED")
    print("-" * 50)
    print("Based on ChatGPT conversation analysis:")
    print()
    print("❌ EXPOSED CREDENTIALS:")
    print("   • Pinecone API Key: Found 37+ times in ChatGPT logs")
    print("   • Key: pcsk_7XLg8W_QDHwGsL7gWufmWduABFqv5fYVDCJc8NyZ1ZAQ6XNu1nRr1XAsABWmhwaCcF1HL")
    print("   • Risk Level: HIGH - Full API access compromised")
    print()
    print("⚠️  POTENTIALLY EXPOSED:")
    print("   • Supabase URL: https://emgidzzjpjtujozttzyv.supabase.co")
    print("   • Supabase Anon Key: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    print("   • Risk Level: MEDIUM - Limited permissions")
    print()
    print("✅ SAFE IDENTIFIERS:")
    print("   • Make.com Agent ID: 14ddbe97-b677-4073-9c6d-5d83f30ebc30")
    print("   • Telegram Chat ID: 1139989892")
    print("   • Risk Level: LOW - No sensitive access")

def test_supabase_connection():
    """Test if Supabase is still accessible"""
    print("\n🔍 TESTING EXISTING INFRASTRUCTURE")
    print("-" * 50)
    
    url = "https://emgidzzjpjtujozttzyv.supabase.co"
    anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVtZ2lkenpqcGp0dWpvenR0enl2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUxNTMyMDksImV4cCI6MjA3MDcyOTIwOX0.JpMhtzZFqSP1C9BFcWypfZ2o9m8jheKoQgfhwFxUWxQ"
    
    try:
        headers = {
            "apikey": anon_key,
            "Authorization": f"Bearer {anon_key}",
            "Content-Type": "application/json"
        }
        
        # Test connection to Supabase
        response = requests.get(f"{url}/rest/v1/", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Supabase connection: WORKING")
            print("   Your existing database is accessible")
        else:
            print(f"⚠️  Supabase connection: ISSUES (Status: {response.status_code})")
            
    except Exception as e:
        print(f"❌ Supabase connection: FAILED ({str(e)})")

def create_env_template():
    """Create environment configuration template"""
    print("\n📝 CREATING SECURE ENVIRONMENT TEMPLATE")
    print("-" * 50)
    
    env_content = """# Becoming One™ AI Journey System - Environment Variables
# SECURITY: Copy this to .env and fill in your actual credentials
# DO NOT commit .env files to version control

# === IMMEDIATE ACTION REQUIRED ===
# 1. Rotate Pinecone API key (EXPOSED in ChatGPT logs)
# 2. Verify Supabase credentials are current
# 3. Generate new bot tokens if needed

# Supabase Configuration (from ChatGPT history - verify these work)
SUPABASE_URL=https://emgidzzjpjtujozttzyv.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVtZ2lkenpqcGp0dWpvenR0enl2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUxNTMyMDksImV4cCI6MjA3MDcyOTIwOX0.JpMhtzZFqSP1C9BFcWypfZ2o9m8jheKoQgfhwFxUWxQ
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# Pinecone Configuration - ROTATE THIS KEY IMMEDIATELY!
# OLD (EXPOSED): pcsk_7XLg8W_QDHwGsL7gWufmWduABFqv5fYVDCJc8NyZ1ZAQ6XNu1nRr1XAsABWmhwaCcF1HL
PINECONE_API_KEY=your_new_pinecone_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=becoming-one-embeddings

# OpenAI Configuration
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Make.com Integration (Agent ID from ChatGPT history)
MAKE_WEBHOOK_URL=your_webhook_url_here
MAKE_API_TOKEN=your_make_token_here
MAKE_AGENT_ID=14ddbe97-b677-4073-9c6d-5d83f30ebc30

# Business Configuration (from ChatGPT history)
TELEGRAM_ESCALATION_CHAT_ID=1139989892

# Development Settings
DEBUG=true
LOG_LEVEL=info
ENVIRONMENT=development

# Becoming One™ Method Settings
DEFAULT_PERSONALITY_PROFILE=adaptive_mentor
RESPONSE_STYLE=empathetic_guidance
LEARNING_MODE=continuous
"""
    
    # Write to config directory
    os.makedirs("config", exist_ok=True)
    
    with open("config/env.template", "w") as f:
        f.write(env_content)
    
    print("✅ Environment template created: config/env.template")
    print("   This contains your current credentials with security notes")

def show_next_steps():
    """Show immediate next steps for Johan"""
    print("\n🎯 IMMEDIATE NEXT STEPS (Human Action Required)")
    print("-" * 50)
    print()
    print("STEP 1: ROTATE PINECONE KEY (5 minutes)")
    print("   1. Go to: https://app.pinecone.io/")
    print("   2. Navigate to your project settings")
    print("   3. Generate a NEW API key")
    print("   4. DELETE the old exposed key")
    print("   5. Copy the new key for Step 2")
    print()
    print("STEP 2: CREATE SECURE ENVIRONMENT FILE")
    print("   1. Copy: config/env.template to .env")
    print("   2. Replace 'your_new_pinecone_key_here' with your new key")
    print("   3. Add your OpenAI API key")
    print("   4. Add your Telegram bot token")
    print()
    print("STEP 3: VERIFY SETUP")
    print("   1. Run: python3 scripts/test_connections.py")
    print("   2. All connections should show ✅")
    print()
    print("🚀 AFTER SECURITY IS FIXED:")
    print("   • Deploy professional Telegram bot")
    print("   • Launch Essence Coach premium service")
    print("   • Start generating revenue within days")

def main():
    print_header()
    
    # Show security status
    show_security_status()
    
    # Test existing infrastructure
    test_supabase_connection()
    
    # Create environment template
    create_env_template()
    
    # Show next steps
    show_next_steps()
    
    print("\n" + "="*60)
    print("🔒 SECURITY CHECK COMPLETE")
    print("="*60)
    print("Next: Follow the steps above, then we'll deploy your system!")

if __name__ == "__main__":
    main()
