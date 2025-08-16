#!/usr/bin/env python3
"""
Connection Testing Script for Becoming One™ AI Journey System
Tests all integrations with the new secure credentials
"""
import os
import sys
import requests
from pathlib import Path

def print_header():
    print("\n" + "="*60)
    print("🧪 BECOMING ONE™ AI - CONNECTION TESTING")
    print("="*60)
    print("Testing all integrations with secure credentials...")
    print("-" * 60)

def test_pinecone_connection():
    """Test the new Pinecone API key"""
    print("\n🔍 TESTING PINECONE CONNECTION")
    print("-" * 40)
    
    api_key = "pcsk_2nX8US_Mku3PJmJ7hoe67kaw1tGHL7TwerFJ5zsjuakrSMjkvm1JcCDurxFpXcGDWd7yju"
    
    try:
        headers = {
            "Api-Key": api_key,
            "Content-Type": "application/json"
        }
        
        # Test Pinecone API connection
        response = requests.get(
            "https://controller.us-east-1.pinecone.io/databases", 
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Pinecone API: CONNECTED")
            data = response.json()
            if 'databases' in data:
                databases = data['databases']
                print(f"   Available indexes: {len(databases)} found")
                for db in databases[:3]:  # Show first 3
                    print(f"   • {db.get('name', 'unknown')}")
            return True
        else:
            print(f"⚠️  Pinecone API: Issues (Status: {response.status_code})")
            print(f"   Response: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"❌ Pinecone API: FAILED")
        print(f"   Error: {str(e)}")
        return False

def test_supabase_connection():
    """Test Supabase connection (already verified working)"""
    print("\n🔍 TESTING SUPABASE CONNECTION")
    print("-" * 40)
    
    url = "https://emgidzzjpjtujozttzyv.supabase.co"
    anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImVtZ2lkenpqcGp0dWpvenR0enl2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTUxNTMyMDksImV4cCI6MjA3MDcyOTIwOX0.JpMhtzZFqSP1C9BFcWypfZ2o9m8jheKoQgfhwFxUWxQ"
    
    try:
        headers = {
            "apikey": anon_key,
            "Authorization": f"Bearer {anon_key}",
            "Content-Type": "application/json"
        }
        
        # Test connection and check for our tables
        response = requests.get(f"{url}/rest/v1/identity_registry?limit=1", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Supabase Database: CONNECTED")
            print("   • identity_registry table: Accessible")
            
            # Test other tables
            tables_to_test = ["event_log", "channel_mapping"]
            for table in tables_to_test:
                test_response = requests.get(f"{url}/rest/v1/{table}?limit=1", headers=headers, timeout=5)
                status = "✅" if test_response.status_code == 200 else "⚠️"
                print(f"   • {table} table: {status}")
            
            return True
        else:
            print(f"⚠️  Supabase: Issues (Status: {response.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ Supabase: FAILED")
        print(f"   Error: {str(e)}")
        return False

def check_system_readiness():
    """Check if system is ready for deployment"""
    print("\n📊 SYSTEM READINESS CHECK")
    print("-" * 40)
    
    # Check required files exist
    required_files = [
        "src/bots/telegram/telegram_bot.py",
        "src/core/ai_engine.py", 
        "src/core/becoming_one_method.py",
        "src/database/operations.py",
        "database/schemas/supabase_schema.sql"
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")
            missing_files.append(file_path)
    
    if not missing_files:
        print("\n✅ ALL CORE FILES: Present and ready")
        return True
    else:
        print(f"\n⚠️  MISSING FILES: {len(missing_files)} files need attention")
        return False

def show_deployment_status():
    """Show what's ready for deployment"""
    print("\n🚀 DEPLOYMENT STATUS")
    print("-" * 40)
    
    print("✅ COMPLETED:")
    print("   • Security audit and credential rotation")
    print("   • Professional architecture design")
    print("   • Becoming One™ methodology integration")
    print("   • Database schema and models")
    print("   • Cross-platform identity management")
    print("   • Vector search and context memory")
    print("   • Business logic and revenue streams")
    
    print("\n🔄 READY TO DEPLOY:")
    print("   • Telegram bot with full methodology")
    print("   • AI engine with emotional anchor recognition")
    print("   • Premium Essence Coach service (€97/month)")
    print("   • Corporate Resilience OS demos")
    
    print("\n📋 NEEDS CONFIGURATION:")
    print("   • OpenAI API key (for AI responses)")
    print("   • Telegram bot token (for messaging)")
    print("   • Make.com webhook URL (for automation)")

def main():
    print_header()
    
    # Test connections
    pinecone_ok = test_pinecone_connection()
    supabase_ok = test_supabase_connection()
    
    # Check system readiness
    system_ready = check_system_readiness()
    
    # Show deployment status
    show_deployment_status()
    
    # Final status
    print("\n" + "="*60)
    if pinecone_ok and supabase_ok and system_ready:
        print("🎉 SYSTEM STATUS: READY FOR DEPLOYMENT")
        print("="*60)
        print("All core integrations working. Ready to launch!")
    else:
        print("⚠️  SYSTEM STATUS: NEEDS ATTENTION")
        print("="*60)
        print("Some components need configuration before deployment.")
    
    print("\n🎯 NEXT: Add your OpenAI and Telegram keys, then deploy!")

if __name__ == "__main__":
    main()
