# build this

import os
import subprocess
import webbrowser
from pathlib import Path

def start_processing():
    """Start the document processor and dashboard"""
    
    # Get the directory containing this script
    current_dir = Path(__file__).parent.absolute()
    
    # Set up environment
    env = os.environ.copy()
    
    # Start the document watcher
    print("Starting document processor...")
    watcher_process = subprocess.Popen(
        ["python", "auto_ingest/folder_watcher.py"],
        env=env,
        cwd=current_dir
    )
    
    # Start the dashboard
    print("Starting processing dashboard...")
    dashboard_process = subprocess.Popen(
        ["streamlit", "run", "doc_processor/tracking_dashboard.py"],
        env=env,
        cwd=current_dir
    )
    
    # Open browser to dashboard
    webbrowser.open("http://localhost:8501")
    
    print("\nDocument processor is running!")
    print("✨ Drop documents into the 'documents_to_process' folder to begin")
    print("📊 View progress at http://localhost:8501")
    print("\nPress Ctrl+C to stop...")
    
    try:
        watcher_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        watcher_process.terminate()
        dashboard_process.terminate()
        watcher_process.wait()
        dashboard_process.wait()

if __name__ == "__main__":
    start_processing()
