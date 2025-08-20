#!/usr/bin/env python3
"""
Simple launcher for the Compass API
"""
import subprocess
import sys

def main():
    print("🚀 Starting Compass API...")
    print("📱 Telegram bot is already running on Railway")
    print("🌐 Compass API: Starting on port 5001")
    
    # Just run the API
    subprocess.run([sys.executable, "compass_api.py"])

if __name__ == "__main__":
    main()
