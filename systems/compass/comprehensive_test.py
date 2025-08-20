#!/usr/bin/env python3
"""
Comprehensive Test of Enhanced Compass System

This test demonstrates the complete workflow:
1. Document processing through all 4 phases
2. Notification system
3. Export and reporting
"""

import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def setup_logging():
    """Setup logging for the test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/comprehensive_test.log'),
            logging.StreamHandler()
        ]
    )

def test_enhanced_components():
    """Test all enhanced components"""
    print("\n🧪 TESTING ENHANCED COMPONENTS")
    print("="*50)
    
    # Test Enhanced Fluff Detector
    print("\n1. Testing Enhanced Fluff Detector...")
    try:
        from enhanced_fluff_detector import EnhancedFluffDetector
        
        detector = EnhancedFluffDetector()
        test_content = """
        # Becoming One™ Method: Emotional Processing
        
        When working with emotional anchors, start with stance work.
        The nervous system plays a crucial role in this process.
        
        ## Key Components:
        1. Emotional anchor recognition
        2. Schaubild integration
        3. Field-aware processing
        
        This method integrates with our Telegram platform and Supabase database.
        """
        
        analysis = detector.analyze_content(test_content, "test_file.md")
        print(f"  ✅ Fluff Score: {analysis.fluff_score}")
        print(f"  ✅ Signal Score: {analysis.signal_score}")
        print(f"  ✅ Recommendation: {analysis.recommendation}")
        print(f"  ✅ Domain Terms: {len(analysis.domain_terms)} found")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    # Test Compass Classifier
    print("\n2. Testing Compass Classifier...")
    try:
        from compass_classifier import CompassClassifier
        
        classifier = CompassClassifier()
        classification = classifier.classify_content(test_content, "test_file.md")
        print(f"  ✅ Primary Category: {classification.primary_category}")
        print(f"  ✅ Confidence: {classification.confidence}")
        print(f"  ✅ Keywords Found: {len(classification.keywords_found)}")
        print(f"  ✅ Compass Tags: {len(classification.compass_tags)}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    # Test Strategic Scorer
    print("\n3. Testing Strategic Scorer...")
    try:
        from strategic_scorer import StrategicScorer
        
        scorer = StrategicScorer()
        score = scorer.score_content(test_content, "test_file.md")
        print(f"  ✅ Total Score: {score.total_score}")
        print(f"  ✅ Processing Decision: {score.processing_decision}")
        print(f"  ✅ Add to Compass Core: {scorer.should_add_to_compass_core(score)}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    # Test Curated Exporter
    print("\n4. Testing Curated Exporter...")
    try:
        from curated_exporter import CuratedExporter
        
        exporter = CuratedExporter()
        
        # Convert to dict format
        classification_dict = {
            "primary_category": classification.primary_category,
            "secondary_categories": classification.secondary_categories,
            "confidence": classification.confidence,
            "keywords_found": classification.keywords_found,
            "compass_tags": classification.compass_tags,
            "processing_priority": classification.processing_priority,
            "export_path": classification.export_path
        }
        
        strategic_score_dict = {
            "signal_score": score.signal_score,
            "danger_score": score.danger_score,
            "quality_score": score.quality_score,
            "originality_score": score.originality_score,
            "actionability_score": score.actionability_score,
            "total_score": score.total_score,
            "recommendations": score.recommendations,
            "risk_factors": score.risk_factors,
            "processing_decision": score.processing_decision
        }
        
        fluff_analysis_dict = {
            "fluff_score": analysis.fluff_score,
            "signal_score": analysis.signal_score,
            "danger_score": analysis.danger_score,
            "rescue_reasons": analysis.rescue_reasons,
            "domain_terms": analysis.domain_terms,
            "structure_quality": analysis.structure_quality,
            "recommendation": analysis.recommendation,
            "confidence": analysis.confidence
        }
        
        # Create test file
        test_file = "test_comprehensive.md"
        with open(test_file, "w") as f:
            f.write(test_content)
        
        # Export
        exported_file = exporter.export_content(
            test_file, classification_dict, strategic_score_dict, fluff_analysis_dict
        )
        
        if exported_file:
            print(f"  ✅ Exported to: {exported_file}")
            
            # Generate reports
            summary_file = exporter.create_compass_core_summary()
            overview_file = exporter.create_export_overview()
            print(f"  ✅ Generated reports: {summary_file}, {overview_file}")
        else:
            print("  ❌ Export failed")
            return False
            
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    # Test Notification System
    print("\n5. Testing Notification System...")
    try:
        from notification_system import NotificationSystem
        
        notifier = NotificationSystem()
        results = notifier.test_notifications()
        print(f"  ✅ Telegram: {'✅' if results['telegram'] else '❌'}")
        print(f"  ✅ Email: {'✅' if results['email'] else '❌'}")
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    print("\n✅ All enhanced components tested successfully!")
    return True

def test_complete_workflow():
    """Test the complete workflow with a real document"""
    print("\n🔄 TESTING COMPLETE WORKFLOW")
    print("="*50)
    
    # Create a test document
    test_document = """
# Master Prompt: Becoming One™ Community Guidelines

## System Instructions

This system manages the WillB.one community with authentic human connection.

## Core Principles

### 1. Authentic Connection
- No spiritual authority positioning
- Practical method sharing
- Peer-to-peer learning support

### 2. Safe Space Maintenance
- Respectful communication
- No judgment or criticism
- Supportive environment

### 3. Method Integration
- Becoming One™ method guidance
- Emotional anchor processing support
- Stance work encouragement

## Technical Implementation

This integrates with:
- Telegram groups and channels
- Supabase user management
- Pinecone knowledge base
- Railway deployment platform

## User Experience

The community provides:
- Daily emotional processing support
- Method guidance and resources
- Connection with like-minded individuals
- Access to Becoming One™ materials

This represents our community framework for authentic human development.
    """
    
    # Write test document
    test_file = "documents_to_process/TEST_COMMUNITY_GUIDELINES.md"
    with open(test_file, "w") as f:
        f.write(test_document)
    
    print(f"📄 Created test document: {test_file}")
    
    # Process with enhanced system
    try:
        from enhanced_folder_watcher import EnhancedDocumentProcessor
        
        processor = EnhancedDocumentProcessor("documents_to_process")
        
        # Process the document
        import asyncio
        asyncio.run(processor.process_document(test_file))
        
        print("✅ Document processed successfully!")
        
        # Check results
        if os.path.exists("EXPORT/COMPASS_CORE/community/TEST_COMMUNITY_GUIDELINES.md"):
            print("✅ Document exported to Compass Core!")
            
            # Check metadata
            metadata_file = "EXPORT/COMPASS_CORE/community/TEST_COMMUNITY_GUIDELINES.md.meta.json"
            if os.path.exists(metadata_file):
                print("✅ Metadata file created!")
                
                # Read and display key info
                import json
                with open(metadata_file, "r") as f:
                    metadata = json.load(f)
                
                classification = metadata.get("classification", {})
                strategic_score = metadata.get("strategic_score", {})
                
                print(f"📊 Category: {classification.get('primary_category')}")
                print(f"📊 Score: {strategic_score.get('total_score')}")
                print(f"📊 Decision: {strategic_score.get('processing_decision')}")
                
        else:
            print("❌ Document not exported to Compass Core")
            return False
            
    except Exception as e:
        print(f"❌ Error processing document: {e}")
        return False
    
    return True

def show_system_status():
    """Show current system status"""
    print("\n📊 SYSTEM STATUS")
    print("="*50)
    
    # Check directories
    directories = [
        "documents_to_process",
        "EXPORT",
        "EXPORT/COMPASS_CORE",
        "EXPORT/HUMAN_REVIEW",
        "EXPORT/QUARANTINE_RESCUE",
        "logs"
    ]
    
    for directory in directories:
        if os.path.exists(directory):
            file_count = len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
            print(f"📁 {directory}: {file_count} files")
        else:
            print(f"❌ {directory}: Missing")
    
    # Check environment
    env_vars = ['OPENAI_API_KEY', 'SUPABASE_URL', 'SUPABASE_ANON_KEY', 'TELEGRAM_BOT_TOKEN']
    for var in env_vars:
        if os.getenv(var):
            print(f"✅ {var}: Configured")
        else:
            print(f"❌ {var}: Missing")

def main():
    """Main test function"""
    setup_logging()
    
    print("🧪 COMPREHENSIVE COMPASS SYSTEM TEST")
    print("="*60)
    print("This test will verify all components of the enhanced system.")
    
    # Show system status
    show_system_status()
    
    # Test enhanced components
    if not test_enhanced_components():
        print("\n❌ Enhanced components test failed!")
        return
    
    # Test complete workflow
    if not test_complete_workflow():
        print("\n❌ Complete workflow test failed!")
        return
    
    print("\n🎉 ALL TESTS PASSED!")
    print("="*60)
    print("✅ Enhanced Fluff Detector: Working")
    print("✅ Compass Classifier: Working")
    print("✅ Strategic Scorer: Working")
    print("✅ Curated Exporter: Working")
    print("✅ Notification System: Working")
    print("✅ Complete Workflow: Working")
    
    print("\n🚀 YOUR ENHANCED COMPASS SYSTEM IS READY!")
    print("You can now:")
    print("1. Add documents to documents_to_process/")
    print("2. Get Telegram notifications when content is added to Compass Core")
    print("3. Review exports in EXPORT/ folder")
    print("4. Use dashboards for management")

if __name__ == "__main__":
    main()
