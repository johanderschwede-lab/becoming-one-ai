#!/usr/bin/env python3
"""
Set up local development environment for Becoming One™ AI
"""
import os
import sys
import venv
import subprocess
from pathlib import Path

def create_venv():
    """Create virtual environment"""
    print("\n🔧 Creating virtual environment...")
    
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    try:
        venv.create(venv_path, with_pip=True)
        print("✅ Virtual environment created")
        return True
    except Exception as e:
        print(f"❌ Error creating virtual environment: {e}")
        return False

def install_dependencies():
    """Install project dependencies"""
    print("\n📦 Installing dependencies...")
    
    try:
        # Use the virtual environment's pip
        pip_path = "venv/bin/pip" if os.name != "nt" else r"venv\Scripts\pip"
        
        result = subprocess.run(
            [pip_path, "install", "-r", "requirements.txt"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("❌ Failed to install dependencies")
            print(f"Error: {result.stderr}")
            return False
        
        print("✅ Dependencies installed")
        return True
        
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def setup_database():
    """Set up database tables"""
    print("\n🗄️ Setting up database tables...")
    
    try:
        # Use the virtual environment's Python
        python_path = "venv/bin/python" if os.name != "nt" else r"venv\Scripts\python"
        
        result = subprocess.run(
            [python_path, "scripts/setup_database.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("❌ Failed to set up database")
            print(f"Error: {result.stderr}")
            return False
        
        print("✅ Database tables created")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False

def sync_railway_env():
    """Sync environment variables from Railway"""
    print("\n🔄 Syncing Railway environment...")
    
    try:
        # Use the virtual environment's Python
        python_path = "venv/bin/python" if os.name != "nt" else r"venv\Scripts\python"
        
        result = subprocess.run(
            [python_path, "scripts/sync_railway_env.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("❌ Failed to sync Railway environment")
            print(f"Error: {result.stderr}")
            return False
        
        print("✅ Environment variables synced")
        return True
        
    except Exception as e:
        print(f"❌ Error syncing environment: {e}")
        return False

def verify_setup():
    """Verify the setup"""
    print("\n🔍 Verifying setup...")
    
    try:
        # Use the virtual environment's Python
        python_path = "venv/bin/python" if os.name != "nt" else r"venv\Scripts\python"
        
        result = subprocess.run(
            [python_path, "scripts/dev_env.py", "--verify"],
            capture_output=True,
            text=True
        )
        
        print("\nVerification Results:")
        print(result.stdout)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error verifying setup: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🛠️  BECOMING ONE™ AI - DEVELOPMENT SETUP")
    print("="*60)
    
    steps = [
        ("Create virtual environment", create_venv),
        ("Sync Railway environment", sync_railway_env),
        ("Install dependencies", install_dependencies),
        ("Set up database", setup_database),
        ("Verify setup", verify_setup)
    ]
    
    success = True
    for step_name, step_func in steps:
        print(f"\n▶️  {step_name}...")
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            success = False
            break
    
    if success:
        print("\n✅ Development environment setup complete!")
        print("\nNext steps:")
        print("1. Activate virtual environment:")
        print("   source venv/bin/activate  # Unix")
        print("   .\\venv\\Scripts\\activate  # Windows")
        print("\n2. Start development:")
        print("   python scripts/dev_env.py --help")
    else:
        print("\n❌ Setup failed - please fix errors and try again")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
