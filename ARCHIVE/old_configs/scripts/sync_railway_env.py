#!/usr/bin/env python3
"""
Sync environment variables from Railway to local .env
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

def install_railway_cli():
    """Install Railway CLI"""
    print("\n📦 Installing Railway CLI...")
    
    try:
        # Check if npm is available
        subprocess.run(["npm", "--version"], capture_output=True, check=True)
        
        # Install Railway CLI
        result = subprocess.run(
            ["npm", "install", "-g", "@railway/cli"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("❌ Failed to install Railway CLI")
            print(f"Error: {result.stderr}")
            return False
        
        print("✅ Railway CLI installed")
        return True
        
    except subprocess.CalledProcessError:
        print("❌ npm not found")
        print("Please install Node.js: https://nodejs.org/")
        return False
    except Exception as e:
        print(f"❌ Error installing Railway CLI: {e}")
        return False

def get_railway_env():
    """Get environment variables from Railway"""
    try:
        # First try to log in
        login_result = subprocess.run(
            ["railway", "login"],
            capture_output=True,
            text=True
        )
        
        if login_result.returncode != 0:
            print("❌ Failed to log in to Railway")
            print(f"Error: {login_result.stderr}")
            return None
        
        # Link to project
        link_result = subprocess.run(
            ["railway", "link"],
            capture_output=True,
            text=True
        )
        
        if link_result.returncode != 0:
            print("❌ Failed to link Railway project")
            print(f"Error: {link_result.stderr}")
            return None
        
        # Get variables
        result = subprocess.run(
            ["railway", "variables", "list", "--json"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("❌ Failed to get Railway variables")
            print(f"Error: {result.stderr}")
            return None
        
        return json.loads(result.stdout)
        
    except Exception as e:
        print(f"❌ Error getting Railway variables: {e}")
        return None

def create_env_file(variables):
    """Create .env file with Railway variables"""
    env_path = Path(".env")
    
    try:
        with open(env_path, "w") as f:
            f.write("# Environment variables synced from Railway\n")
            f.write(f"# Synced at: {datetime.now().isoformat()}\n\n")
            
            for var in variables:
                f.write(f"{var['name']}={var['value']}\n")
        
        print(f"✅ Environment variables written to {env_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def main():
    print("\n🔄 Syncing Railway environment variables...")
    
    # Check if Railway CLI is installed
    try:
        subprocess.run(["railway", "--version"], capture_output=True)
    except FileNotFoundError:
        print("❌ Railway CLI not found")
        if not install_railway_cli():
            return False
    
    # Get variables from Railway
    variables = get_railway_env()
    if not variables:
        return False
    
    # Create .env file
    return create_env_file(variables)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)