#!/usr/bin/env python3
"""
Launcher for the Consider List Dashboard
"""

import subprocess
import sys
import os

def main():
    print("📋 Launching Consider List Dashboard...")
    print("This will open a web interface for managing the consider list.")
    print("Press Ctrl+C to stop the dashboard.")
    print()
    
    try:
        # Change to the consider_list directory
        os.chdir("consider_list")
        
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "consider_dashboard.py",
            "--server.port", "8503",
            "--server.address", "localhost"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped.")
    except Exception as e:
        print(f"❌ Error launching dashboard: {str(e)}")
        print("Make sure you have streamlit installed: pip install streamlit")

if __name__ == "__main__":
    main()
