#!/usr/bin/env python3
"""
Sacred Library Setup
===================

Install dependencies and prepare for Sacred Library build
"""

import subprocess
import sys
import os
from pathlib import Path

def install_dependencies():
    """Install required Python packages"""
    print("📦 Installing Sacred Library dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def check_environment_variables():
    """Check if required environment variables are set"""
    print("🔍 Checking environment variables...")
    
    required_vars = {
        'OPENAI_API_KEY': 'OpenAI API key for embeddings',
        'SUPABASE_URL': 'Supabase project URL',
        'SUPABASE_ANON_KEY': 'Supabase anonymous key',
        'SUPABASE_SERVICE_KEY': 'Supabase service key (for schema deployment)',
        'PINECONE_API_KEY': 'Pinecone API key',
        'PINECONE_ENV': 'Pinecone environment'
    }
    
    missing_vars = []
    
    for var, description in required_vars.items():
        if os.getenv(var):
            print(f"  ✅ {var}: Set")
        else:
            print(f"  ❌ {var}: Missing - {description}")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing {len(missing_vars)} required environment variables")
        print("Please set these before running the Sacred Library builder:")
        for var in missing_vars:
            print(f"  export {var}=your_key_here")
        return False
    
    print("✅ All environment variables are set")
    return True

def check_data_directory():
    """Check if the Hylozoics collection directory exists"""
    print("📁 Checking data directory...")
    
    data_dir = Path("laurency_ultimate")
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        print("Please ensure the Hylozoics collection is available")
        return False
    
    # Count PDF files
    pdf_count = len(list(data_dir.rglob("*.pdf")))
    language_count = len([d for d in data_dir.iterdir() if d.is_dir()])
    
    print(f"✅ Data directory found: {pdf_count} PDFs in {language_count} languages")
    return True

def main():
    """Run complete Sacred Library setup"""
    print("🏛️  SACRED LIBRARY SETUP")
    print("=" * 40)
    
    success = True
    
    # Install dependencies
    if not install_dependencies():
        success = False
    
    # Check environment variables
    if not check_environment_variables():
        success = False
    
    # Check data directory
    if not check_data_directory():
        success = False
    
    print("\n" + "=" * 40)
    
    if success:
        print("🎉 SETUP COMPLETE!")
        print("✅ Ready to build Sacred Library")
        print("\nNext steps:")
        print("1. python scripts/deploy_sacred_schemas.py")
        print("2. python scripts/sacred_library_builder.py")
    else:
        print("❌ SETUP INCOMPLETE")
        print("Please resolve the issues above before proceeding")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
