#!/usr/bin/env python3
"""
Create local .env file with known working credentials
"""
import os
from pathlib import Path

def create_local_env():
    """Create .env file with working credentials"""
    env_content = """# Local development environment for Becoming One™ AI
# Created from known working credentials

# === WORKING DATABASE CONNECTION ===
SUPABASE_URL=https://emgidzzjpjtujozttzyv.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVtZ2lkenpqcGp0dWpvenR0enl2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUxNTMyMDksImV4cCI6MjA3MDcyOTIwOX0.JpMhtzZFqSP1C9BFcWypfZ2o9m8jheKoQgfhwFxUWxQ

# === SECURE VECTOR DATABASE ===
PINECONE_API_KEY=pcsk_2nX8US_Mku3PJmJ7hoe67kaw1tGHL7TwerFJ5zsjuakrSMjkvm1JcCDurxFpXcGDWd7yju
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=becoming-one-embeddings

# === AI CONFIGURATION ===
OPENAI_API_KEY=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
OPENAI_MODEL=gpt-4-turbo-preview

# === TELEGRAM BOT ===
TELEGRAM_BOT_TOKEN=8244158767:AAGJveKJcOwFO_PxaeROpiQ7FKGSv-0aFrQ

# === BUSINESS CONFIGURATION ===
MAKE_AGENT_ID=14ddbe97-b677-4073-9c6d-5d83f30ebc30
TELEGRAM_ESCALATION_CHAT_ID=1139989892

# === SYSTEM SETTINGS ===
DEBUG=true
LOG_LEVEL=info
ENVIRONMENT=development

# === BECOMING ONE™ METHOD ===
DEFAULT_PERSONALITY_PROFILE=adaptive_mentor
RESPONSE_STYLE=empathetic_guidance
LEARNING_MODE=continuous
ENABLE_EMOTIONAL_ANCHOR_RECOGNITION=true
ENABLE_JOURNEY_STAGE_DETECTION=true
ENABLE_CROSS_PLATFORM_MEMORY=true
ENABLE_SCHAUBILDER_INTEGRATION=true
"""
    
    env_path = Path(".env")
    
    try:
        with open(env_path, "w") as f:
            f.write(env_content)
        
        print(f"✅ Environment file created: {env_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def main():
    print("\n🔧 Creating local development environment...")
    return create_local_env()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
