# build this

import os
import time
import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
from typing import Optional, Dict, Any

class YAMLProcessor:
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        
    def process_yaml(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Process a YAML file and prepare it for upload"""
        try:
            with open(file_path, 'r') as f:
                content = yaml.safe_load(f)
                
            return {
                "file_name": os.path.basename(file_path),
                "content": content,
                "processed_at": datetime.utcnow().isoformat(),
                "status": "processed",
                "metadata": {
                    "size": os.path.getsize(file_path),
                    "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                }
            }
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
            return None

class PromptFileHandler(FileSystemEventHandler):
    def __init__(self, processor: YAMLProcessor):
        self.processor = processor
        self.processing_queue = set()
        
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith(('.yaml', '.yml')):
            return
            
        if event.src_path not in self.processing_queue:
            self.processing_queue.add(event.src_path)
            self._process_file(event.src_path)
            
    def on_modified(self, event):
        if event.is_directory or not event.src_path.endswith(('.yaml', '.yml')):
            return
            
        if event.src_path not in self.processing_queue:
            self.processing_queue.add(event.src_path)
            self._process_file(event.src_path)
    
    def _process_file(self, file_path: str):
        """Process a file and remove it from queue"""
        try:
            processed_data = self.processor.process_yaml(file_path)
            if processed_data:
                # TODO: Upload to Supabase
                print(f"Processed: {file_path}")
        finally:
            self.processing_queue.remove(file_path)

def watch_directory(path: str, processor: YAMLProcessor):
    """Set up directory watching"""
    event_handler = PromptFileHandler(processor)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def main():
    """Main pipeline routine"""
    # TODO: Add Supabase client initialization
    watch_path = os.getenv("WATCH_DIR", "../CompassBuilder_Starter_Kit/output")
    
    if not os.path.exists(watch_path):
        print(f"Error: Watch directory {watch_path} not found")
        return
        
    processor = YAMLProcessor(None)  # TODO: Add Supabase client
    print(f"Starting file watcher on {watch_path}")
    watch_directory(watch_path, processor)

if __name__ == "__main__":
    main()
