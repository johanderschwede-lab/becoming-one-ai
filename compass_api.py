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
    """Approve an item and move it to compass core"""
    try:
        # This would implement the approval logic
        return jsonify({'status': 'success', 'message': f'Approved {filename}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/move-to-consider/<filename>')
def move_to_consider(filename):
    """Move an item to the consider list"""
    try:
        # This would implement the move to consider logic
        return jsonify({'status': 'success', 'message': f'Moved {filename} to consider list'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/test-notification')
def test_notification():
    """Test notification system"""
    try:
        return jsonify({'status': 'success', 'message': 'Test notification sent'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/start-watcher')
def start_watcher():
    """Start the folder watcher"""
    try:
        return jsonify({'status': 'success', 'message': 'Folder watcher started'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logs')
def get_logs():
    """Get recent logs"""
    try:
        logs = []
        if os.path.exists(LOGS_DIR):
            for file in os.listdir(LOGS_DIR):
                if file.endswith('.log'):
                    file_path = os.path.join(LOGS_DIR, file)
                    with open(file_path, 'r') as f:
                        content = f.read()
                        logs.append({
                            'filename': file,
                            'content': content[-1000:]  # Last 1000 characters
                        })
        return jsonify(logs)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'compass-api'
    })

if __name__ == '__main__':
    # Use Railway's PORT environment variable or default to 5001
    port = int(os.environ.get('PORT', 5001))
    
    print(f"🌐 Starting Compass Management API...")
    print(f"📱 Open http://localhost:{port} in your browser")
    print(f"🔧 API endpoints available at http://localhost:{port}/api/")
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)
