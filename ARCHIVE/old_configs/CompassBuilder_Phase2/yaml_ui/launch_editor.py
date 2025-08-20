# build this

import os
import subprocess
import webbrowser
from pathlib import Path

def launch_editor():
    """Launch the Prompt Editor UI"""
    
    # Get the directory containing this script
    current_dir = Path(__file__).parent.absolute()
    
    # Set up environment
    env = os.environ.copy()
    env["STREAMLIT_THEME_BASE"] = "light"
    env["STREAMLIT_SERVER_PORT"] = "8501"
    
    # Start Streamlit
    print("Starting Prompt Editor...")
    process = subprocess.Popen(
        ["streamlit", "run", "prompt_editor.py"],
        env=env,
        cwd=current_dir
    )
    
    # Open browser
    webbrowser.open("http://localhost:8501")
    
    try:
        process.wait()
    except KeyboardInterrupt:
        print("\nShutting down Prompt Editor...")
        process.terminate()
        process.wait()

if __name__ == "__main__":
    launch_editor()
