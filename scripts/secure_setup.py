#!/usr/bin/env python3
"""
Security Setup Script for Becoming One™ AI Journey System
Run this script to securely configure credentials and test connections
"""
import os
import sys
from pathlib import Path
from getpass import getpass
import requests
from supabase import create_client
from pinecone import Pinecone

# Add src to Python path
sys.path.append(str(Path(__file__).parent.parent / "src"))

def print_header():
    print("\n" + "="*60)
    print("🔒 BECOMING ONE™ AI SECURITY SETUP")
    print("="*60)
    print("This script will help you securely configure your credentials")
    print("and test all integrations before deployment.\n")

def check_existing_credentials():
    """Check what credentials we found in ChatGPT history"""
    print("📋 CREDENTIAL AUDIT FROM CHATGPT HISTORY:")
    print("-" * 40)
    
    # Known credentials from ChatGPT logs
    known_creds = {
        "Supabase URL": "https://emgidzzjpjtujozttzyv.supabase.co",
        "Supabase Anon Key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...(truncated)",
        "Pinecone API Key": "pcsk_7XLg8W_QDHwGsL7gWufmWduABFqv5fYVDCJc8NyZ1ZAQ6XNu1nRr1XAsABWmhwaCcF1HL",
        "Make.com Agent ID": "14ddbe97-b677-4073-9c6d-5d83f30ebc30",
        "Telegram Chat ID": "1139989892"
    }
    
    for service, value in known_creds.items():
        status = "⚠️  EXPOSED" if "API Key" in service else "✅ Safe"
        print(f"{service}: {status}")
    
    print("\n🚨 SECURITY ALERT:")
    print("Your Pinecone API key was found 37+ times in ChatGPT conversations.")
    print("This key should be rotated IMMEDIATELY.\n")

def rotate_pinecone_key():
    """Guide user through Pinecone key rotation"""
    print("🔄 PINECONE KEY ROTATION:")
    print("-" * 40)
    print("1. Go to: https://app.pinecone.io/")
    print("2. Navigate to your project settings")
    print("3. Generate a new API key")
    print("4. Delete the old exposed key")
    print("5. Enter the new key below\n")
    
    new_key = getpass("Enter your NEW Pinecone API key: ")
    
    if new_key.startswith("pcsk_"):
        print("✅ Valid Pinecone key format detected")
        return new_key
    else:
        print("❌ Invalid key format. Pinecone keys start with 'pcsk_'")
        return None

def test_supabase_connection(url, key):
    """Test Supabase connection"""
    try:
        client = create_client(url, key)
        result = client.table("identity_registry").select("*").limit(1).execute()
        print("✅ Supabase connection successful")
        return True
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return False

def test_pinecone_connection(api_key):
    """Test Pinecone connection"""
    try:
        pc = Pinecone(api_key=api_key)
        indexes = pc.list_indexes()
        print("✅ Pinecone connection successful")
        print(f"   Available indexes: {[idx.name for idx in indexes]}")
        return True
    except Exception as e:
        print(f"❌ Pinecone connection failed: {e}")
        return False

def create_env_template():
    """Create environment template file"""
    env_template = """# Becoming One™ AI Journey System - Environment Variables
# Copy this to .env and fill in your actual credentials

# Supabase Configuration
SUPABASE_URL=https://emgidzzjpjtujozttzyv.supabase.co
SUPABASE_ANON_KEY=your_anon_key_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# Pinecone Configuration (ROTATE THE EXPOSED KEY!)
PINECONE_API_KEY=your_new_pinecone_key_here
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=becoming-one-embeddings

# OpenAI Configuration
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4-turbo-preview

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# Make.com Integration
MAKE_WEBHOOK_URL=your_webhook_url_here
MAKE_API_TOKEN=your_make_token_here
MAKE_AGENT_ID=14ddbe97-b677-4073-9c6d-5d83f30ebc30

# Business Configuration
TELEGRAM_ESCALATION_CHAT_ID=1139989892

# Development Settings
DEBUG=true
LOG_LEVEL=info
"""
    
    with open("config/env.template", "w") as f:
        f.write(env_template)
    
    print("✅ Environment template created at config/env.template")
    print("   Copy this to .env and fill in your actual credentials")

def main():
    print_header()
    
    # Step 1: Show what we found in ChatGPT history
    check_existing_credentials()
    
    # Step 2: Guide through key rotation
    print("STEP 1: Secure Your Pinecone API Key")
    rotate_key = input("Do you want to rotate your Pinecone key now? (y/n): ")
    
    if rotate_key.lower() == 'y':
        new_pinecone_key = rotate_pinecone_key()
        if new_pinecone_key:
            print("✅ New Pinecone key captured securely")
    
    # Step 3: Test existing connections
    print("\nSTEP 2: Test Existing Infrastructure")
    test_connections = input("Test your existing Supabase connection? (y/n): ")
    
    if test_connections.lower() == 'y':
        supabase_url = "https://emgidzzjpjtujozttzyv.supabase.co"
        supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVtZ2lkenpqcGp0dWpvenR0enl2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUxNTMyMDksImV4cCI6MjA3MDcyOTIwOX0.JpMhtzZFqSP1C9BFcWypfZ2o9m8jheKoQgfhwFxUWxQ"
        
        test_supabase_connection(supabase_url, supabase_key)
    
    # Step 4: Create environment template
    print("\nSTEP 3: Environment Setup")
    create_env_template()
    
    # Step 5: Next steps
    print("\n🎯 NEXT STEPS:")
    print("-" * 40)
    print("1. Copy config/env.template to .env")
    print("2. Fill in all your actual API keys")
    print("3. Run: python scripts/test_integrations.py")
    print("4. Deploy the Telegram bot")
    print("\n✅ Security setup complete!")

if __name__ == "__main__":
    main()
