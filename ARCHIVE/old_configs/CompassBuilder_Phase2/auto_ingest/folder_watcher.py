# build this

import os
import time
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import logging
from datetime import datetime
import traceback

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/processing.log')
    ]
)

from prompt_preservers import PromptPreserver
from rescue_system import RescueSystem
from archive_manager import ArchiveManager
from document_categorizer import DocumentCategorizer
from supabase_uploader import SupabaseUploader
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'master_prompt_review'))
from review_system import MasterPromptReviewSystem
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'consider_list'))
from consider_list_manager import ConsiderListManager

class DocumentHandler(FileSystemEventHandler):
    def __init__(self, processor):
        self.processor = processor
        self.processing_queue = set()
        self.loop = asyncio.get_event_loop()
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        if self._is_valid_document(event.src_path):
            logging.info(f"New file detected: {event.src_path}")
            self._process_document(event.src_path)
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        if self._is_valid_document(event.src_path) and event.src_path not in self.processing_queue:
            logging.info(f"File modified: {event.src_path}")
            self._process_document(event.src_path)
    
    def _is_valid_document(self, file_path: str) -> bool:
        """Check if file is a valid document type"""
        return any([
            file_path.endswith('.md'),
            file_path.endswith('.txt'),
            file_path.endswith('.doc'),
            file_path.endswith('.docx'),
            file_path.endswith('.pdf')
        ])
    
    def _process_document(self, file_path: str):
        """Process a document asynchronously"""
        if file_path in self.processing_queue:
            return
        
        self.processing_queue.add(file_path)
        logging.info(f"Starting to process: {file_path}")
        
        # Create a new event loop for this thread if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run the async process
        loop.run_until_complete(self._async_process_document(file_path))
        
        # Remove from processing queue
        self.processing_queue.discard(file_path)
    
    async def _async_process_document(self, file_path: str):
        """Async document processing"""
        try:
            # Wait a moment to ensure file is fully written
            await asyncio.sleep(1)
            
            # Check if this is a chat file with prompts
            if self.processor.preserver.is_chat_file(file_path):
                logging.info(f"Processing chat file: {file_path}")
                preserved_path, prompts = self.processor.preserver.preserve_chat_file(
                    file_path,
                    os.path.join(os.path.dirname(file_path), "processed")
                )
                
                self.processor.archive_manager.archive_file(
                    file_path,
                    {"type": "chat", "prompts": len(prompts)},
                    status="preserved"
                )
                
                logging.info(f"Preserved chat file with {len(prompts)} prompts: {file_path}")
                return
            
            # For non-chat files, proceed with normal analysis
            logging.info(f"Analyzing document: {file_path}")
            analysis = await self.processor.categorizer.analyze_document(file_path)
            
            logging.info(f"Checking for fluff: {file_path}")
            fluff_analysis = self.processor.categorizer.analyze_fluff(analysis["content"])
            fluff_score = fluff_analysis.get("score", 0)
            fluff_matches = fluff_analysis.get("matches", [])
            
            logging.info(f"Determining categories for: {file_path}")
            categories = self.processor.categorizer.suggest_categories(analysis)
            
            # Get primary category first
            primary_cat = categories[0] if categories else "uncategorized"
            
            # Determine phase folder
            if "master_prompt" in categories or "becoming_one_method" in categories:
                phase_folder = "Phase2_Clean_Logic"
            elif "ai_agents" in categories:
                phase_folder = "Phase3_AgentExpansions"
            else:
                phase_folder = "Phase1_Legacy_Imports"
            
            logging.info(f"File {file_path} categorized as: {categories}")
            logging.info(f"Primary category: {primary_cat}")
            logging.info(f"Phase folder: {phase_folder}")
            
            # Process potential fluff content
            if fluff_score >= 2.0:
                logging.info(f"High fluff score ({fluff_score}) detected for: {file_path}")
                with open(file_path, 'r') as f:
                    content = f.read()
                
                destination = self.processor.rescue_system.process_quarantined_file(
                    file_path, content, fluff_matches, fluff_score
                )
                
                self.processor.archive_manager.archive_file(
                    file_path,
                    {
                        "fluff_score": fluff_score,
                        "fluff_matches": fluff_matches,
                        "destination": destination
                    },
                    status="quarantined" if destination == "99_trash_quarantine" else "rescued"
                )
                
                dest_folder = os.path.join(
                    os.path.dirname(file_path),
                    destination
                )
                os.makedirs(dest_folder, exist_ok=True)
                new_path = os.path.join(dest_folder, Path(file_path).name)
                os.rename(file_path, new_path)
                
                logging.info(f"Moved fluff content to: {destination}")
                return
            
            # Track document
            logging.info(f"Tracking document: {file_path}")
            self.processor.categorizer.track_document(file_path, analysis, categories)
            
            # Archive the processed file
            logging.info(f"Archiving document: {file_path}")
            self.processor.archive_manager.archive_file(
                file_path,
                {
                    "categories": categories,
                    "analysis": analysis,
                    "destination": f"{phase_folder}/{primary_cat}"
                },
                status="processed"
            )
            
            # ALL documents in this folder are treated as potential master prompt changes
            logging.info(f"Processing as potential master prompt document: {file_path}")
            logging.info("Creating review request for potential master prompt change...")
            
            # Read the document content
            with open(file_path, 'r') as f:
                new_master_prompt = f.read()
            
            # Create review request
            review_result = self.processor.review_system.create_review_request(
                new_master_prompt,
                "Auto_Compass_System",
                f"Automatically detected potential master prompt change from file: {os.path.basename(file_path)}"
            )
            
            if review_result['success']:
                logging.info(f"Review request created successfully: {review_result['review_id']}")
                logging.info(f"Impact Level: {review_result['analysis'].get('impact_level', 'Unknown')}")
                logging.info(f"AI Recommendation: {review_result['analysis'].get('recommendation', 'Unknown')}")
            else:
                logging.error(f"Failed to create review request: {review_result['error']}")
            
            # Check if this document should be added to consider list
            consider_categories = ["ai_agents", "technical", "method_core", "personality_systems"]
            if any(cat in categories for cat in consider_categories):
                logging.info(f"Document eligible for consider list: {file_path}")
                
                # Read the document content
                with open(file_path, 'r') as f:
                    doc_content = f.read()
                
                # Determine priority based on content analysis
                priority = "medium"  # Default
                if any(word in doc_content.lower() for word in ["urgent", "critical", "important", "priority", "high priority"]):
                    priority = "high"
                elif any(word in doc_content.lower() for word in ["nice to have", "future", "maybe", "consider", "low priority", "medium priority"]):
                    priority = "low"
                elif "medium priority" in doc_content.lower():
                    priority = "medium"
                
                # Add to consider list
                consider_result = self.processor.consider_manager.add_to_consider_list(
                    doc_content,
                    "Auto_Compass_System",
                    categories[0] if categories else "other",
                    priority,
                    f"Automatically added from file: {os.path.basename(file_path)}. Categories: {', '.join(categories)}"
                )
                
                if consider_result['success']:
                    logging.info(f"Added to consider list: {consider_result.get('consider_id', 'Unknown')}")
                    logging.info(f"Priority: {priority}")
                else:
                    logging.error(f"Failed to add to consider list: {consider_result['error']}")
            
            # Upload to Supabase for AI use
            logging.info(f"Uploading {file_path} to Supabase...")
            upload_result = self.processor.supabase_uploader.upload_document(
                file_path, analysis, categories, phase_folder
            )
            
            if upload_result:
                logging.info(f"Successfully uploaded {file_path} to Supabase")
            else:
                logging.warning(f"Failed to upload {file_path} to Supabase")
            
            # Move to appropriate folder
            cat_folder = os.path.join(
                os.path.dirname(file_path),
                'processed',
                phase_folder,
                primary_cat
            )
            os.makedirs(cat_folder, exist_ok=True)
            new_path = os.path.join(cat_folder, Path(file_path).name)
            os.rename(file_path, new_path)
            
            logging.info(f"Successfully processed and moved {file_path} to {phase_folder}/{primary_cat}")
            
        except Exception as e:
            logging.error(f"Error processing {file_path}: {str(e)}")
            logging.error(traceback.format_exc())

class AutoProcessor:
    def __init__(self, watch_dir: str):
        self.watch_dir = watch_dir
        
        # Ensure OpenAI API key is available
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        logging.info("Initializing components...")
        self.categorizer = DocumentCategorizer(os.getenv("OPENAI_API_KEY"))
        self.rescue_system = RescueSystem()
        self.archive_manager = ArchiveManager(os.path.join(watch_dir, "archive"))
        self.preserver = PromptPreserver()
        self.supabase_uploader = SupabaseUploader()
        self.review_system = MasterPromptReviewSystem()
        self.consider_manager = ConsiderListManager()
        
        # Test Supabase connection
        if not self.supabase_uploader.test_connection():
            logging.warning("Supabase connection failed - documents will not be uploaded to database")
        else:
            logging.info("Supabase connection successful - documents will be uploaded to database")
        
        # Create processed folder structure
        self.processed_dir = os.path.join(watch_dir, 'processed')
        os.makedirs(self.processed_dir, exist_ok=True)
        
        # Create category folders
        for category in self.categorizer.categories:
            folder = os.path.join(self.processed_dir, category)
            os.makedirs(folder, exist_ok=True)
            logging.info(f"Created category folder: {folder}")
    
    def _is_valid_document(self, file_path: str) -> bool:
        """Check if file is a valid document type"""
        return any([
            file_path.endswith('.md'),
            file_path.endswith('.txt'),
            file_path.endswith('.doc'),
            file_path.endswith('.docx'),
            file_path.endswith('.pdf')
        ])

    def start(self):
        """Start watching the directory"""
        logging.info(f"Starting document processor - watching {self.watch_dir}")
        
        # Process existing files first
        logging.info("Processing existing files...")
        for file_name in os.listdir(self.watch_dir):
            file_path = os.path.join(self.watch_dir, file_name)
            if os.path.isfile(file_path) and self._is_valid_document(file_path):
                logging.info(f"Found existing file: {file_path}")
                event_handler = DocumentHandler(self)
                event_handler._process_document(file_path)
        
        # Start watching for new files
        event_handler = DocumentHandler(self)
        observer = Observer()
        observer.schedule(event_handler, self.watch_dir, recursive=False)
        observer.start()
        
        try:
            while True:
                time.sleep(1)
                
                # Generate archive report every hour
                if datetime.now().minute == 0:
                    logging.info("Generating hourly report...")
                    report = self.archive_manager.generate_archive_report()
                    report_path = os.path.join(
                        self.watch_dir,
                        "archive",
                        "reports",
                        f"archive_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
                    )
                    os.makedirs(os.path.dirname(report_path), exist_ok=True)
                    with open(report_path, 'w') as f:
                        f.write(report)
                    logging.info(f"Report generated: {report_path}")
                    
        except KeyboardInterrupt:
            observer.stop()
            logging.info("Document processor stopped")
        except Exception as e:
            logging.error(f"Error in main loop: {str(e)}")
            logging.error(traceback.format_exc())
            observer.stop()
        
        observer.join()

def main():
    """Main watcher routine"""
    try:
        watch_dir = os.getenv(
            "WATCH_DIR",
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "documents_to_process"
            )
        )
        
        # Create watch directory if it doesn't exist
        os.makedirs(watch_dir, exist_ok=True)
        logging.info(f"Using watch directory: {watch_dir}")
        
        processor = AutoProcessor(watch_dir)
        processor.start()
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        logging.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    main()