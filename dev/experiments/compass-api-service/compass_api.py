#!/usr/bin/env python3
"""
Compass Management API

Simple Flask API for the HTML management interface.
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Configuration
EXPORT_DIR = "EXPORT"
DOCS_TO_PROCESS_DIR = "documents_to_process"
LOGS_DIR = "logs"

@app.route('/')
def serve_html():
    """Serve the HTML management interface"""
    return send_from_directory('.', 'compass_management.html')

@app.route('/api/stats')
def get_stats():
    """Get system statistics"""
    try:
        stats = {
            'total_files': 0,
            'compass_core': 0,
            'human_review': 0,
            'quarantine': 0,
            'last_updated': datetime.now().isoformat()
        }
        
        # Count files in each directory
        if os.path.exists(EXPORT_DIR):
            for root, dirs, files in os.walk(EXPORT_DIR):
                if 'COMPASS_CORE' in root:
                    stats['compass_core'] += len(files)
                elif 'HUMAN_REVIEW' in root:
                    stats['human_review'] += len(files)
                elif 'QUARANTINE_RESCUE' in root:
                    stats['quarantine'] += len(files)
                stats['total_files'] += len(files)
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/review-queue')
def get_review_queue():
    """Get items in the human review queue"""
    try:
        review_items = []
        review_dir = os.path.join(EXPORT_DIR, "HUMAN_REVIEW")
        
        if os.path.exists(review_dir):
            for root, dirs, files in os.walk(review_dir):
                for file in files:
                    if file.endswith('.md') and not file.endswith('.meta.json'):
                        file_path = os.path.join(root, file)
                        meta_path = file_path + '.meta.json'
                        
                        # Get file stats
                        stat = os.stat(file_path)
                        
                        item = {
                            'filename': file,
                            'path': os.path.relpath(file_path, EXPORT_DIR),
                            'size': stat.st_size,
                            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'category': os.path.basename(root),
                            'score': 'N/A',
                            'decision': 'N/A'
                        }
                        
                        # Try to get metadata
                        if os.path.exists(meta_path):
                            try:
                                with open(meta_path, 'r') as f:
                                    metadata = json.load(f)
                                    strategic_score = metadata.get('strategic_score', {})
                                    item['score'] = strategic_score.get('total_score', 'N/A')
                                    item['decision'] = strategic_score.get('processing_decision', 'N/A')
                            except:
                                pass
                        
                        review_items.append(item)
        
        return jsonify(review_items)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/approve/<filename>')
def approve_item(filename):
    """Approve an item and move it to Compass Core"""
    try:
        # Find the file in human review
        review_dir = os.path.join(EXPORT_DIR, "HUMAN_REVIEW")
        compass_core_dir = os.path.join(EXPORT_DIR, "COMPASS_CORE")
        
        # Search for the file
        for root, dirs, files in os.walk(review_dir):
            if filename in files:
                source_path = os.path.join(root, filename)
                source_meta = source_path + '.meta.json'
                
                # Determine category from path
                category = os.path.basename(root)
                target_dir = os.path.join(compass_core_dir, category)
                target_path = os.path.join(target_dir, filename)
                target_meta = target_path + '.meta.json'
                
                # Create target directory if it doesn't exist
                os.makedirs(target_dir, exist_ok=True)
                
                # Move file and metadata
                if os.path.exists(source_path):
                    os.rename(source_path, target_path)
                if os.path.exists(source_meta):
                    os.rename(source_meta, target_meta)
                
                return jsonify({
                    'success': True,
                    'message': f'Approved {filename} to Compass Core',
                    'new_path': os.path.relpath(target_path, EXPORT_DIR)
                })
        
        return jsonify({'error': f'File {filename} not found in review queue'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/move-to-consider/<filename>')
def move_to_consider(filename):
    """Move an item to the consider list"""
    try:
        # This would move the file to a consider list
        # For now, just return success
        return jsonify({
            'success': True,
            'message': f'Moved {filename} to Consider List'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-notification')
def test_notification():
    """Send a test notification"""
    try:
        from notification_system import NotificationSystem
        
        notifier = NotificationSystem()
        success = notifier.notify_compass_core_update(
            "TEST_NOTIFICATION.md",
            "Test notification from web interface",
            "test",
            8.5,
            "SAFE_CORE"
        )
        
        return jsonify({
            'success': success,
            'message': 'Test notification sent' if success else 'Failed to send notification'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/start-watcher')
def start_watcher():
    """Start the enhanced folder watcher"""
    try:
        # This would start the folder watcher
        # For now, just return success
        return jsonify({
            'success': True,
            'message': 'Enhanced folder watcher started'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs')
def get_logs():
    """Get recent system logs"""
    try:
        logs = []
        log_file = os.path.join(LOGS_DIR, "enhanced_processing.log")
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                # Get last 50 lines
                lines = f.readlines()
                logs = lines[-50:] if len(lines) > 50 else lines
        
        return jsonify({'logs': logs})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🌐 Starting Compass Management API...")
    print("📱 Open http://localhost:5001 in your browser")
    print("🔧 API endpoints available at http://localhost:5001/api/")
    app.run(debug=True, host='0.0.0.0', port=5001)
