#!/usr/bin/env python3
"""
Launcher for the Master Prompt Review Dashboard
"""

import subprocess
import sys
import os

def main():
    print("🔍 Launching Master Prompt Review Dashboard...")
    print("This will open a web interface for reviewing master prompt changes.")
    print("Press Ctrl+C to stop the dashboard.")
    print()
    
    try:
        # Change to the master_prompt_review directory
        os.chdir("master_prompt_review")
        
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "review_dashboard.py",
            "--server.port", "8502",
            "--server.address", "localhost"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped.")
    except Exception as e:
        print(f"❌ Error launching dashboard: {str(e)}")
        print("Make sure you have streamlit installed: pip install streamlit")

if __name__ == "__main__":
    main()
