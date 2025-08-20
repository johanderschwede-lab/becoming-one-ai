#!/usr/bin/env python3
"""
Enhanced Compass System Launcher

This script provides easy access to all enhanced features:
- Enhanced Folder Watcher (all 4 phases)
- Review Dashboard
- Consider List Dashboard
- Export Reports
- System Status
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_logging():
    """Setup logging for the launcher"""
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/launcher.log'),
            logging.StreamHandler()
        ]
    )

def check_dependencies():
    """Check if all required dependencies are available"""
    required_modules = [
        'watchdog',
        'openai',
        'requests',
        'streamlit'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Missing required modules: {', '.join(missing_modules)}")
        print("Please install them with: pip install " + " ".join(missing_modules))
        return False
    
    return True

def check_environment():
    """Check if environment variables are set"""
    required_vars = [
        'OPENAI_API_KEY',
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file")
        return False
    
    return True

def create_directories():
    """Create necessary directories"""
    directories = [
        "documents_to_process",
        "logs",
        "EXPORT",
        "processed"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def show_menu():
    """Show the main menu"""
    print("\n" + "="*60)
    print("🚀 ENHANCED COMPASS SYSTEM LAUNCHER")
    print("="*60)
    print("1. 🎯 Start Enhanced Folder Watcher (All 4 Phases)")
    print("2. 📊 Launch Review Dashboard")
    print("3. 📋 Launch Consider List Dashboard")
    print("4. 📈 Generate Export Reports")
    print("5. 🔍 System Status & Health Check")
    print("6. 🧪 Test Enhanced Components")
    print("7. 📚 Show Documentation")
    print("8. 🚪 Exit")
    print("="*60)

def start_enhanced_watcher():
    """Start the enhanced folder watcher"""
    print("\n🎯 Starting Enhanced Folder Watcher...")
    print("This will process documents through all 4 phases:")
    print("  • Phase 1: Smart Fluff Detection")
    print("  • Phase 2: Compass Classification")
    print("  • Phase 3: Strategic Scoring")
    print("  • Phase 4: Curated Export")
    print("\nPlace documents in the 'documents_to_process' folder to begin.")
    print("Press Ctrl+C to stop the watcher.\n")
    
    try:
        subprocess.run([sys.executable, "enhanced_folder_watcher.py"], check=True)
    except KeyboardInterrupt:
        print("\n⏹️  Enhanced Folder Watcher stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting enhanced watcher: {e}")

def launch_review_dashboard():
    """Launch the review dashboard"""
    print("\n📊 Launching Review Dashboard...")
    print("This will open a web interface for reviewing master prompt changes.")
    print("The dashboard will be available at: http://localhost:8501")
    print("Press Ctrl+C to stop the dashboard.\n")
    
    try:
        subprocess.run([sys.executable, "launch_review_dashboard.py"], check=True)
    except KeyboardInterrupt:
        print("\n⏹️  Review Dashboard stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching review dashboard: {e}")

def launch_consider_dashboard():
    """Launch the consider list dashboard"""
    print("\n📋 Launching Consider List Dashboard...")
    print("This will open a web interface for managing the consider list.")
    print("The dashboard will be available at: http://localhost:8502")
    print("Press Ctrl+C to stop the dashboard.\n")
    
    try:
        subprocess.run([sys.executable, "launch_consider_dashboard.py"], check=True)
    except KeyboardInterrupt:
        print("\n⏹️  Consider List Dashboard stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching consider dashboard: {e}")

def generate_export_reports():
    """Generate all export reports"""
    print("\n📈 Generating Export Reports...")
    
    try:
        # Import the exporter
        from curated_exporter import CuratedExporter
        
        exporter = CuratedExporter()
        
        # Generate all reports
        summary_file = exporter.create_compass_core_summary()
        queue_file = exporter.create_human_review_queue()
        report_file = exporter.create_quarantine_rescue_report()
        overview_file = exporter.create_export_overview()
        
        print("✅ Generated reports:")
        print(f"  • Compass Core Summary: {summary_file}")
        print(f"  • Human Review Queue: {queue_file}")
        print(f"  • Quarantine Report: {report_file}")
        print(f"  • Export Overview: {overview_file}")
        
        # Show stats
        stats = exporter.generate_export_stats()
        print(f"\n📊 Export Statistics:")
        print(f"  • Total Files: {stats['total_files']}")
        print(f"  • Compass Core: {stats['compass_core']}")
        print(f"  • Human Review: {stats['human_review']}")
        print(f"  • Quarantine: {stats['quarantine']}")
        
    except Exception as e:
        print(f"❌ Error generating reports: {e}")

def system_status():
    """Show system status and health check"""
    print("\n🔍 System Status & Health Check")
    print("="*40)
    
    # Check directories
    directories = [
        "documents_to_process",
        "logs",
        "EXPORT",
        "processed"
    ]
    
    print("\n📁 Directory Status:")
    for directory in directories:
        if os.path.exists(directory):
            file_count = len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
            print(f"  ✅ {directory}: {file_count} files")
        else:
            print(f"  ❌ {directory}: Missing")
    
    # Check environment
    print("\n🔧 Environment Status:")
    env_vars = ['OPENAI_API_KEY', 'SUPABASE_URL', 'SUPABASE_ANON_KEY']
    for var in env_vars:
        if os.getenv(var):
            print(f"  ✅ {var}: Set")
        else:
            print(f"  ❌ {var}: Missing")
    
    # Check Supabase connection
    print("\n🗄️  Database Status:")
    try:
        from auto_ingest.supabase_uploader import SupabaseUploader
        uploader = SupabaseUploader()
        if uploader.test_connection():
            print("  ✅ Supabase: Connected")
        else:
            print("  ❌ Supabase: Connection failed")
    except Exception as e:
        print(f"  ❌ Supabase: Error - {e}")
    
    # Check export structure
    print("\n📦 Export Structure:")
    export_dir = "EXPORT"
    if os.path.exists(export_dir):
        for folder in os.listdir(export_dir):
            folder_path = os.path.join(export_dir, folder)
            if os.path.isdir(folder_path):
                file_count = len([f for f in os.listdir(folder_path) if f.endswith(('.md', '.txt', '.json'))])
                print(f"  📁 {folder}: {file_count} files")
    else:
        print("  ❌ EXPORT directory not found")

def test_enhanced_components():
    """Test the enhanced components"""
    print("\n🧪 Testing Enhanced Components...")
    
    # Test Enhanced Fluff Detector
    print("\n1. Testing Enhanced Fluff Detector...")
    try:
        from enhanced_fluff_detector import EnhancedFluffDetector
        
        detector = EnhancedFluffDetector()
        test_content = """
        # System Prompt for Emotional Anchor Processing
        
        When working with emotional anchors, start with stance work.
        The nervous system plays a crucial role in this process.
        
        This represents a comprehensive framework for personal development.
        """
        
        analysis = detector.analyze_content(test_content, "test_file.md")
        print(f"  ✅ Fluff Score: {analysis.fluff_score}")
        print(f"  ✅ Signal Score: {analysis.signal_score}")
        print(f"  ✅ Recommendation: {analysis.recommendation}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test Compass Classifier
    print("\n2. Testing Compass Classifier...")
    try:
        from compass_classifier import CompassClassifier
        
        classifier = CompassClassifier()
        test_content = """
        # Becoming One™ Method Guide
        
        The emotional anchor digestion process involves stance work and
        nervous system awareness. This method integrates with our Telegram
        platform and Supabase database.
        """
        
        classification = classifier.classify_content(test_content, "test_file.md")
        print(f"  ✅ Primary Category: {classification.primary_category}")
        print(f"  ✅ Keywords Found: {len(classification.keywords_found)}")
        print(f"  ✅ Confidence: {classification.confidence}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    # Test Strategic Scorer
    print("\n3. Testing Strategic Scorer...")
    try:
        from strategic_scorer import StrategicScorer
        
        scorer = StrategicScorer()
        test_content = """
        # Step-by-Step Emotional Processing
        
        1. Recognize the emotional anchor
        2. Access your nervous system response
        3. Apply the anti-bypass approach
        4. Extract the pearl of wisdom
        
        I found that this method works best when you practice regularly.
        Try this approach for at least 10 minutes daily.
        """
        
        score = scorer.score_content(test_content, "test_file.md")
        print(f"  ✅ Total Score: {score.total_score}")
        print(f"  ✅ Processing Decision: {score.processing_decision}")
        print(f"  ✅ Recommendations: {len(score.recommendations)}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n✅ Enhanced component testing completed!")

def show_documentation():
    """Show documentation"""
    print("\n📚 Enhanced Compass System Documentation")
    print("="*50)
    
    docs = """
    🚀 ENHANCED COMPASS SYSTEM - COMPLETE ENHANCEMENT PLAN
    
    This system implements all 4 phases of the enhancement plan:
    
    🔥 PHASE 1: Smart Fluff Detector
    - Domain-specific term recognition (stance, digest, schaubild, etc.)
    - Protected folders that are never quarantined
    - Context-aware scoring with rescue reasons
    - Structure quality analysis
    
    🧭 PHASE 2: Compass-Based Classification
    - 9 core categories: prompt_module, method_model, offer, platform, tone, community, content, research, strategy
    - Weighted keyword matching with confidence scoring
    - Multiple tag support
    - Sidecar metadata files (.meta.json)
    
    🧠 PHASE 3: Strategic Prompt Scoring
    - 5-dimensional scoring: signal, danger, quality, originality, actionability
    - Processing decisions: SAFE_CORE, REVIEW_CORE, RESCUE_QUEUE, QUARANTINE, HUMAN_REVIEW
    - Risk factor identification
    - Priority-based recommendations
    
    📚 PHASE 4: Curated Exports
    - COMPASS_CORE: Clean, structured source of truth
    - HUMAN_REVIEW: Content needing assessment
    - QUARANTINE_RESCUE: Flagged content with recovery options
    - Automated report generation
    
    📁 FOLDER STRUCTURE:
    documents_to_process/     # Add your 200+ documents here
    ├── processed/           # Processed files
    ├── logs/               # Processing logs
    └── EXPORT/             # Curated exports
        ├── COMPASS_CORE/   # Ready-to-use content
        ├── HUMAN_REVIEW/   # Needs human assessment
        └── QUARANTINE_RESCUE/ # Flagged content
    
    🎯 USAGE:
    1. Start Enhanced Folder Watcher
    2. Add documents to documents_to_process/
    3. Monitor logs for processing status
    4. Review exports in EXPORT/ folder
    5. Use dashboards for review and management
    
    🔧 COMPONENTS:
    - enhanced_folder_watcher.py: Main processing pipeline
    - enhanced_fluff_detector.py: Smart content filtering
    - compass_classifier.py: Domain-specific classification
    - strategic_scorer.py: Multi-dimensional scoring
    - curated_exporter.py: Organized exports
    - launch_enhanced_system.py: This launcher
    
    📊 DASHBOARDS:
    - Review Dashboard: Master prompt review system
    - Consider Dashboard: Implementation idea management
    
    🎯 READY FOR YOUR 200+ DOCUMENTS!
    """
    
    print(docs)

def main():
    """Main function"""
    setup_logging()
    
    print("🚀 Enhanced Compass System Launcher")
    print("Initializing...")
    
    # Check dependencies and environment
    if not check_dependencies():
        return
    
    if not check_environment():
        return
    
    # Create directories
    create_directories()
    
    print("\n✅ System ready!")
    
    # Main menu loop
    while True:
        show_menu()
        
        try:
            choice = input("\nSelect an option (1-8): ").strip()
            
            if choice == "1":
                start_enhanced_watcher()
            elif choice == "2":
                launch_review_dashboard()
            elif choice == "3":
                launch_consider_dashboard()
            elif choice == "4":
                generate_export_reports()
            elif choice == "5":
                system_status()
            elif choice == "6":
                test_enhanced_components()
            elif choice == "7":
                show_documentation()
            elif choice == "8":
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid option. Please select 1-8.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
