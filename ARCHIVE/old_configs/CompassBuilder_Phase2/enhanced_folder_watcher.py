import os
import sys
import time
import logging
import asyncio
import traceback
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(__file__))

# Import all enhancement components
from enhanced_fluff_detector import EnhancedFluffDetector, FluffAnalysis
from compass_classifier import CompassClassifier, CompassClassification
from strategic_scorer import StrategicScorer, StrategicScore
from curated_exporter import CuratedExporter

# Import existing components
from auto_ingest.document_categorizer import DocumentCategorizer
from auto_ingest.supabase_uploader import SupabaseUploader
from master_prompt_review.review_system import MasterPromptReviewSystem
from consider_list.consider_list_manager import ConsiderListManager
from notification_system import NotificationSystem

class EnhancedDocumentProcessor:
    def __init__(self, watch_dir: str):
        self.watch_dir = watch_dir
        
        # Ensure OpenAI API key is available
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        logging.info("Initializing Enhanced Document Processor...")
        
        # Initialize all enhancement components
        self.enhanced_fluff_detector = EnhancedFluffDetector()
        self.compass_classifier = CompassClassifier()
        self.strategic_scorer = StrategicScorer()
        self.curated_exporter = CuratedExporter()
        
        # Initialize existing components
        self.categorizer = DocumentCategorizer(os.getenv("OPENAI_API_KEY"))
        self.supabase_uploader = SupabaseUploader()
        self.review_system = MasterPromptReviewSystem()
        self.consider_manager = ConsiderListManager()
        self.notification_system = NotificationSystem()
        
        # Test Supabase connection
        if not self.supabase_uploader.test_connection():
            logging.warning("Supabase connection failed - documents will not be uploaded to database")
        else:
            logging.info("Supabase connection successful - documents will be uploaded to database")
        
        # Create processed folder structure
        self.processed_dir = os.path.join(watch_dir, 'processed')
        os.makedirs(self.processed_dir, exist_ok=True)
        
        logging.info("Enhanced Document Processor initialized successfully")

    async def process_document(self, file_path: str):
        """Process a document through the complete enhancement pipeline"""
        try:
            logging.info(f"Starting enhanced processing of: {file_path}")
            
            # Read document content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Phase 1: Enhanced Fluff Detection
            logging.info(f"Phase 1: Enhanced fluff analysis for {file_path}")
            fluff_analysis = self.enhanced_fluff_detector.analyze_content(content, file_path)
            
            logging.info(f"Fluff Score: {fluff_analysis.fluff_score}")
            logging.info(f"Signal Score: {fluff_analysis.signal_score}")
            logging.info(f"Danger Score: {fluff_analysis.danger_score}")
            logging.info(f"Recommendation: {fluff_analysis.recommendation}")
            logging.info(f"Rescue Reasons: {fluff_analysis.rescue_reasons}")
            
            # Phase 2: Compass Classification
            logging.info(f"Phase 2: Compass classification for {file_path}")
            compass_classification = self.compass_classifier.classify_content(content, file_path)
            
            logging.info(f"Primary Category: {compass_classification.primary_category}")
            logging.info(f"Secondary Categories: {compass_classification.secondary_categories}")
            logging.info(f"Confidence: {compass_classification.confidence}")
            logging.info(f"Keywords Found: {compass_classification.keywords_found}")
            logging.info(f"Compass Tags: {compass_classification.compass_tags}")
            
            # Phase 3: Strategic Scoring
            logging.info(f"Phase 3: Strategic scoring for {file_path}")
            strategic_score = self.strategic_scorer.score_content(content, file_path)
            
            logging.info(f"Total Strategic Score: {strategic_score.total_score}")
            logging.info(f"Quality Score: {strategic_score.quality_score}")
            logging.info(f"Originality Score: {strategic_score.originality_score}")
            logging.info(f"Actionability Score: {strategic_score.actionability_score}")
            logging.info(f"Processing Decision: {strategic_score.processing_decision}")
            
            # Phase 4: Curated Export
            logging.info(f"Phase 4: Curated export for {file_path}")
            
            # Convert dataclass objects to dictionaries for export
            classification_dict = {
                "primary_category": compass_classification.primary_category,
                "secondary_categories": compass_classification.secondary_categories,
                "confidence": compass_classification.confidence,
                "keywords_found": compass_classification.keywords_found,
                "compass_tags": compass_classification.compass_tags,
                "processing_priority": compass_classification.processing_priority,
                "export_path": compass_classification.export_path
            }
            
            strategic_score_dict = {
                "signal_score": strategic_score.signal_score,
                "danger_score": strategic_score.danger_score,
                "quality_score": strategic_score.quality_score,
                "originality_score": strategic_score.originality_score,
                "actionability_score": strategic_score.actionability_score,
                "total_score": strategic_score.total_score,
                "recommendations": strategic_score.recommendations,
                "risk_factors": strategic_score.risk_factors,
                "processing_decision": strategic_score.processing_decision
            }
            
            fluff_analysis_dict = {
                "fluff_score": fluff_analysis.fluff_score,
                "signal_score": fluff_analysis.signal_score,
                "danger_score": fluff_analysis.danger_score,
                "rescue_reasons": fluff_analysis.rescue_reasons,
                "domain_terms": fluff_analysis.domain_terms,
                "structure_quality": fluff_analysis.structure_quality,
                "recommendation": fluff_analysis.recommendation,
                "confidence": fluff_analysis.confidence
            }
            
            # Export to curated structure
            exported_file = self.curated_exporter.export_content(
                file_path, classification_dict, strategic_score_dict, fluff_analysis_dict
            )
            
            if exported_file:
                logging.info(f"Successfully exported to: {exported_file}")
                
                # Send notification for Compass Core updates
                if "COMPASS_CORE" in exported_file:
                    notification_sent = self.notification_system.notify_compass_core_update(
                        classification_dict, strategic_score_dict, file_path, exported_file
                    )
                    if notification_sent:
                        logging.info(f"Notification sent for Compass Core update: {os.path.basename(file_path)}")
                    else:
                        logging.warning(f"Failed to send notification for: {os.path.basename(file_path)}")
            
            # Legacy processing for backward compatibility
            
            # Master Prompt Review (all documents)
            logging.info(f"Creating master prompt review request for {file_path}")
            review_result = self.review_system.create_review_request(
                content,
                "Enhanced_Compass_System",
                f"Enhanced processing detected potential master prompt change from {os.path.basename(file_path)}"
            )
            
            if review_result and review_result.get("success"):
                logging.info(f"Review request created: {review_result.get('review_id')}")
            else:
                logging.error(f"Failed to create review request: {review_result}")
            
            # Consider List (for technical/method content)
            consider_categories = ["ai_agents", "technical", "method_core", "personality_systems"]
            if any(cat in compass_classification.compass_tags for cat in consider_categories):
                logging.info(f"Document eligible for consider list: {file_path}")
                
                # Determine priority based on strategic score
                priority = "medium"
                if strategic_score.total_score >= 8.0:
                    priority = "high"
                elif strategic_score.total_score <= 3.0:
                    priority = "low"
                
                consider_result = self.consider_manager.add_to_consider_list(
                    content,
                    "Enhanced_Compass_System",
                    compass_classification.primary_category,
                    priority,
                    f"Enhanced processing: {os.path.basename(file_path)}. Score: {strategic_score.total_score}. Decision: {strategic_score.processing_decision}"
                )
                
                if consider_result['success']:
                    logging.info(f"Added to consider list: {consider_result.get('consider_id', 'Unknown')}")
                    logging.info(f"Priority: {priority}")
                else:
                    logging.error(f"Failed to add to consider list: {consider_result['error']}")
            
            # Supabase Upload
            logging.info(f"Uploading {file_path} to Supabase...")
            
            # Create analysis dict for Supabase
            analysis = {
                "enhanced_analysis": {
                    "fluff_analysis": fluff_analysis_dict,
                    "compass_classification": classification_dict,
                    "strategic_score": strategic_score_dict
                },
                "processing_timestamp": datetime.now().isoformat(),
                "enhanced_processing": True
            }
            
            upload_result = self.supabase_uploader.upload_document(
                file_path, analysis, [compass_classification.primary_category], "Enhanced_Processing"
            )
            
            if upload_result:
                logging.info(f"Successfully uploaded {file_path} to Supabase")
            else:
                logging.warning(f"Failed to upload {file_path} to Supabase")
            
            # Move to processed folder
            processed_path = os.path.join(self.processed_dir, os.path.basename(file_path))
            os.rename(file_path, processed_path)
            
            logging.info(f"Successfully processed and moved {file_path} to processed folder")
            
            # Generate periodic reports
            if self._should_generate_reports():
                self._generate_reports()
            
        except Exception as e:
            logging.error(f"Error in enhanced processing of {file_path}: {str(e)}")
            logging.error(traceback.format_exc())

    def _should_generate_reports(self) -> bool:
        """Determine if reports should be generated (e.g., every 10 files)"""
        # Simple counter - in production, you might want a more sophisticated approach
        return True  # Generate reports for every file for now

    def _generate_reports(self):
        """Generate all reports"""
        try:
            logging.info("Generating enhanced reports...")
            
            # Generate all export reports
            summary_file = self.curated_exporter.create_compass_core_summary()
            queue_file = self.curated_exporter.create_human_review_queue()
            report_file = self.curated_exporter.create_quarantine_rescue_report()
            overview_file = self.curated_exporter.create_export_overview()
            
            logging.info(f"Generated reports:")
            logging.info(f"- Compass Core Summary: {summary_file}")
            logging.info(f"- Human Review Queue: {queue_file}")
            logging.info(f"- Quarantine Report: {report_file}")
            logging.info(f"- Export Overview: {overview_file}")
            
        except Exception as e:
            logging.error(f"Error generating reports: {str(e)}")

class EnhancedFolderWatcher(FileSystemEventHandler):
    def __init__(self, watch_dir: str):
        self.watch_dir = watch_dir
        self.processor = EnhancedDocumentProcessor(watch_dir)
        self.processing_files = set()
        
        # Process existing files on startup
        self._process_existing_files()
    
    def _process_existing_files(self):
        """Process any existing files in the watch directory"""
        logging.info("Processing existing files in watch directory...")
        
        for filename in os.listdir(self.watch_dir):
            file_path = os.path.join(self.watch_dir, filename)
            if os.path.isfile(file_path) and self._is_valid_document(file_path):
                logging.info(f"Found existing file: {file_path}")
                self._process_file(file_path)
    
    def _is_valid_document(self, file_path: str) -> bool:
        """Check if file is a valid document for processing"""
        valid_extensions = {'.md', '.txt', '.json', '.docx', '.pdf'}
        return Path(file_path).suffix.lower() in valid_extensions
    
    def on_created(self, event):
        """Handle file creation events"""
        if not event.is_directory and self._is_valid_document(event.src_path):
            logging.info(f"New file detected: {event.src_path}")
            self._process_file(event.src_path)
    
    def on_modified(self, event):
        """Handle file modification events"""
        if not event.is_directory and self._is_valid_document(event.src_path):
            logging.info(f"File modified: {event.src_path}")
            self._process_file(event.src_path)
    
    def _process_file(self, file_path: str):
        """Process a file through the enhanced pipeline"""
        if file_path in self.processing_files:
            logging.info(f"File already being processed: {file_path}")
            return
        
        self.processing_files.add(file_path)
        
        try:
            # Run the async processing
            asyncio.run(self.processor.process_document(file_path))
        except Exception as e:
            logging.error(f"Error processing {file_path}: {str(e)}")
        finally:
            self.processing_files.discard(file_path)

def main():
    """Main function to run the enhanced folder watcher"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/enhanced_processing.log'),
            logging.StreamHandler()
        ]
    )
    
    # Get watch directory
    watch_dir = "documents_to_process"
    
    if not os.path.exists(watch_dir):
        os.makedirs(watch_dir)
        logging.info(f"Created watch directory: {watch_dir}")
    
    logging.info(f"Starting Enhanced Folder Watcher for: {watch_dir}")
    
    # Create and start the watcher
    event_handler = EnhancedFolderWatcher(watch_dir)
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=False)
    observer.start()
    
    try:
        logging.info("Enhanced Folder Watcher is running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping Enhanced Folder Watcher...")
        observer.stop()
    
    observer.join()
    logging.info("Enhanced Folder Watcher stopped")

if __name__ == "__main__":
    main()
